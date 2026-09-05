<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Motion architecture";
  --doc-path: ".\\SliderDoc\\mc\\motion.md";
}
</style>

# Motion architecture

Highest priority: smooth, jerk-limited STEP generation. Protocol and UI traffic must never starve the FIFO.

## FreeRTOS tasks

| Task | Priority | Role |
|------|----------|------|
| `feed` (MotionFeed) | Highest | Sole owner of `planner_fill_fifo()` (or `motion_path_fill_fifo()` while path-mode is active). Waits on the TX-not-full IRQ **only while the FIFO is full**; otherwise sleeps 1 ms, so it can never spin and starve `plan`/`proto` |
| `plan` (Planner) | High | Switches, DIR pause, settle, underrun check, status (~200 Hz) — does **not** fill FIFO |
| `proto` (Protocol) | Medium | USB CDC + UART 115200 baud RX/TX, verbose push, LED heartbeat (~67 Hz state patterns) / WDT |
| `loop` | Idle | Idle delay only |

## PIO STEP

- Packed FIFO words: `delay[25:0]` + `repeat[31:26]` (1…64 pulses/word).
- **High phase:** 188 cycles (~1.5 µs @ 125 MHz).
- **Period formula:** `period ≈ PIO_STEP_PERIOD_FIXED(192) + delay` (includes SET/MOV/JMP overhead).
- **Polarity:** `DRV_STEP_active` selects active-high vs active-low PIO program (`pio_step_reconfigure()` only when idle).
- **DIR:** `DRV_DIR_active` — `1` means DIR high = +mm.
- Soft stop drains TX; hard abort disables SM and clears FIFOs (and disarms TX IRQ).

Files: `src/motion/pio_step.cpp`, `include/pio_step.h`.

## Planner (sine seek)

Raised-cosine velocity blend. The ramp **target** is the cruise speed, or 0 when
stopping / reversing / braking. Two rules keep the profile symmetric:

- The target is **not** `min(cruise, vmax(rem))`. Such a target moves with every
  FIFO word as `rem` shrinks, restarts the sine phase each time, and leaves the
  axis crawling at `ramp_start_hz` — the higher the cruise, the worse.
- Once `|v| > vmax(rem)` the planner **commits** to a single brake ramp down to
  0 (`g_braking`). Re-deriving the brake per word collapses the S-curve into
  constant deceleration of `2a/π` (≈64 % of `SA`), which is why braking used to
  report one fixed acceleration value. While braking, the distance clamp acts
  only as an outer cap (`1.25 × vmax`) and no longer tears down the ramp.

Distance limiting otherwise applies as a clamp on the issued velocity:

\[
d = \pi v^2 / (4 a)
\quad\Rightarrow\quad
v_{\max}(d) = \sqrt{4 a d / \pi}
\]

### Rules (from MicroPython lessons)

1. **One source of truth for STEP rate** — `planner_fill_fifo()` computes Hz from remaining distance + cruise/accel at issue time.
2. **`pack_n`:** if `remaining_steps <= 0` return **0 before** any min-Hz shortcut (prevents Zielpunkt-Pendeln).
3. **Position** advances when pulses are **committed to TX**; soft-stop waits for empty FIFO.
4. **Live retarget** — `MT` / `MJ` / `SS` / `SA` update target/cruise/accel; next fill uses new remaining distance.
5. **Reverse** — decelerate to 0 → `dir_change_pause_s` → accelerate the other way.
6. **Soft limits** clamp remaining steps to the **session working window** (`SL`/`SR`); illegal `MT` outside the window is rejected.
7. **Homing** — FSM via `MH` (`home_mode`, `home_speed`, `home_accel`, `home_move_out`); mode `0` = silent no-op (`SP` declares origin).

API units are user units (typically mm / mm/s / mm/s², or ° / °/s / °/s²); internals use steps via `steps_per_unit` (and `steps_per_unit_2` when axis2 is enabled). See [dual-movement.md](dual-movement.md) for dual-axis timing and units.

With `axis2_use=1`, the planner maintains **two** independent axes, each with its own PIO state machine, position, soft limits, and homing FSM. Session `SS`/`SA` apply to both; dual-arg `MT`/`M` and mask args on `ML`/`MR`/`MH` select which axes move. `MJ` / `MoveJoy` holds a signed per-axis velocity as a percent of `SS` (independent, not dual-`MT` time-sync) — [motion-joy.md](motion-joy.md). See [dual-movement.md](dual-movement.md) and [protocol.md — Optional 2nd axis](../contract/protocol.md#optional-2nd-axis-axis2_use).

Shared math (host-testable): `include/planner_math.h`, `src/motion/planner_math.cpp`.

## Path playback (2nd planner)

`PC`/`PD`/`PG`/`PN`/`PS` (see [PROTOCOL.md](../contract/protocol.md#p--path-host-authored-motion-path)) implement a host-authored motion
path via a second, deliberately simpler planner in `src/motion/motion_path.cpp`,
kept separate from the sine-ramp planner above. This is a **second planner**, not the optional physical axis2 — though when `axis2_use=1`, path mode plays **two** sample streams (dual `PD` args).

- **Buffer:** a flat `int16_t` array (`PATH_BUFFER_MAX` = 32768 samples per axis,
  static — no malloc), holding one signed µm delta-distance per fixed time
  slice (`PS`, µs). With axis2 enabled there are two parallel buffers. `PD` appends; `PG` always plays from sample 0.
- **Playback:** the `feed` task calls `motion_path_fill_fifo()` instead of
  `planner_fill_fifo()` while path-mode is active. Each slice converts to a
  step count (`steps_per_unit`) and a PIO delay (constant rate for that slice —
  no ramp), chunked into ≤64-pulse words like the normal planner. A `0` sample
  emits no word; the PIO naturally holds/stalls, giving an exact stand-still.
- **Error diffusion:** both the distance→steps and slice-time→PIO-cycles
  conversions keep a fractional carry (`motion_path_diffuse_steps` /
  `motion_path_diffuse_cycles`, host-testable) so rounding per slice never
  biases the total distance or total playback time. A stand-still slice's
  owed time is carried forward and added ahead of the next real step word.
- **Ending path-mode:** on buffer exhaustion, or on `MS`/`H` while active,
  `motion_path_abort_to_planner()` hands the current position/velocity to
  `planner_takeover_from_path()`, then the normal `planner_request_stop()` /
  `planner_request_halt()` decelerates from that speed exactly like a live
  move — path-mode never invents its own stop/halt ramp.
- **Gating:** while `PG` is active, all other move/session commands are
  rejected (`!E:busy`); only `MS`, `H`/`HT`, `PD` (live-move streaming), `PN`,
  status queries, `Help`, and `CG` are allowed (`MJ` included in the busy
  set). Speed/accel limits are **not**
  checked — the host is
  trusted to deliver an already-limited path, same stance as elsewhere.

Files: `include/motion_path.h`, `src/motion/motion_path.cpp`.

## Joystick hold (`MJ`)

`MJ` / `MoveJoy` is a **velocity hold** for analogue sticks (typical 5–20 Hz, also acyclic): signed percent of session `SS`, clamped per axis to `max_speed` / `max_speed_2`. It is **not** a wrap of `ML`/`SS`/`MS`. First `MJ` enters joy-mode; `SS`/`SA` stay legal and rescale/re-ramp from the stored percentages. Other moves (`MT`, `ML`, `MS`, `PG`, …) end joy-mode.

Integrator guide (command flow, snapshot rules, UIC skip-if-unchanged): [motion-joy.md](motion-joy.md). Hardware: [joysticks.md](../components/joysticks.md).

## Debug counters (`motion_diag`)

| Counter | Meaning |
|---------|---------|
| `underrun_count` | SM TXSTALL while moving *and* the planner still had steps to issue. Intentional idle gaps (direction-change pause, final settle) do not count |
| `peak_step_hz` | Highest issued step rate |
| `overshoot_steps` | Steps by which an issued word *crossed* the target (should stay 0). Being past the target while a reverse move bleeds off speed is not counted |
| `fifo_min_level` | Lowest observed TX level while filling |

Read over the protocol with **`ID` / `IsDiag`** (also allowed during EMO). Counters always describe the running session: they are mirrored into a `.noinit` RAM snapshot, but that snapshot is only restored when the chip came up from a **watchdog** reset, so a post-mortem `ID` is never confused with fresh data. After such a reboot USB prints `D:diag_restored …` / `D:reset=wdt` when `init_debug_level≥2`.

**`IZ` / `IsReset`** reports the last chip reset cause (`power`, `wdt`, `run`, `soft`, `debug`, `brownout`, …).

## Host tests

```powershell
powershell -File scripts/run_host_tests.ps1
```

- **Planner scenario sim** (`test/sim`): Python twin of `planner_fill_fifo` + PIO drain. Matrix of speeds/accels covering normal moves, reverse/forward retarget, and mid-move speed changes. Also: `python -m unittest test.sim.test_planner_scenarios -v`
- Protocol tests: `motion_stub` (no PIO); needs `g++`/`clang++`.
- Planner math: stop-distance, `pack_n` pendeln guard, max Hz ≥ 300 kHz, sine endpoints; needs `g++`/`clang++`.

## Hard limits

Enabled per side with `SW_LIMIT_L_use` / `SW_LIMIT_R_use` (GPIOs fixed in `pins.h`). Polarity via `SW_LIMIT_*_active`.

- Polled from `planner_tick` with **~20 ms** debounce (assert and release) to survive switch bounce.
- On stable trip: shared **`planner_halt()`** — `pio_step_stop_hard()`, `enable=0`, cancel waits/chain, state letter `L`.
- Toward-limit commands rejected until cleared; after `SE 1`, drive-out (opposite direction) is allowed; latch clears on stable release.
- Soft limits / working window (`slider_min`/`max` envelope; `SL`/`SR` session): **separate**; see [working-window.md](working-window.md).

## Stop vs Halt

- **`MS` / realtime `!`:** soft decelerate via stop-distance law; enable unchanged; normal jog/move workflow. Also **ends joy-mode** (`MJ`).
- **`H` / `HT` / hard limit / `PIN_DRV_ERROR`:** `planner_halt()` — immediate FIFO abort, EN off, cancel waits/chain.

## `PIN_DRV_ERROR`

Always sampled (polarity `DRV_ERROR_active`), ~20 ms debounce. Works if already asserted at power-up (no rising edge required). While stable-asserted: `drv_error=1`, halt, protocol gate (`!E:emo active` except diagnostics/`CS`/`CG`/halt). On release: clear `drv_error` only.

## Homing

Requires `enable=1` and a valid `home_mode` (limit modes also need that side’s `SW_LIMIT_*_use`). `IH` / `IsHoming` is 1 for the whole cycle. `home_mode=0`: `MH` is a silent no-op — use `SP` to declare origin.

**Limit-home (1/2)**

1. If sitting on the opposite hard limit: drive out until released (`ClearHard`).
2. If already on the reference limit: skip seek and start backoff.
3. **Seek** toward the reference (1 −, 2 +) at `home_speed` / `home_accel`. Soft limits do not clamp. Max travel `1.1 × (slider_max − slider_min)` → `!E:home travel`.
4. On reference assert: reverse (**Backoff**), leave the switch, then continue `home_move_out` mm.
5. Set machine position to `slider_min` (1) or `slider_max` (2); clear `homing`.

The reference limit does not raise a hard-limit fault during seek (it ends seek). Hitting the **other** limit aborts with `!E:home hard`.

**Stall-home (3/4)**

1. Seek left (3) or right (4) until debounced `DRV_ERROR`. This is **not** the normal EMO path — motion is not protocol-gated.
2. Stop stepping. Pulse `DRV_EN` off then on (~200 ms) so latched DIAG / Protect can clear.
3. Wait until `DRV_ERROR` is stably deasserted (~20 ms debounce). Timeout → `!E:home stall`.
4. Drive out `home_move_out` (DIAG ignored for a short window after re-enable).
5. Set pose to `slider_min` (3) or `slider_max` (4).

A real EMO still applies if `DRV_ERROR` asserts while **not** in this stall seek/reset, or if the line stays asserted after the EN pulse times out. Hitting a hard limit during stall-home aborts (`!E:home hard`). `MS` soft-cancels; `H`/`HT` emergency-halts.

Use stall-home only on drivers that expose a stall line on `DRV_ERROR` (TMC2209 DIAG; MKS SERVO57D `OUT_1`). TMC2208, SERVO42C, and SERVO42D STEP/DIR have no usable stall pin — use modes 1/2 or `SP`. See [homing-switches.md](../components/homing-switches.md) and [integrated-drivers.md](../components/integrated-drivers.md).

## Current milestone

- Real PIO + FIFO feed + sine seek planner with live retarget: **implemented**.
- Hard limits L/R (debounced, immediate halt): **implemented**.
- Homing cycle (`MH`): **implemented**.
- Joystick hold (`MJ` / `MoveJoy`): **implemented**.
- Stop vs Halt + `PIN_DRV_ERROR` poll/gate: **implemented**.
