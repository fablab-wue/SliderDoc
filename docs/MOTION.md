# Motion architecture

Highest priority: smooth, jerk-limited STEP generation. Protocol and UI traffic must never starve the FIFO.

## FreeRTOS tasks

| Task | Priority | Role |
|------|----------|------|
| `feed` (MotionFeed) | Highest | Sole owner of `planner_fill_fifo()` (or `motion_path_fill_fifo()` while path-mode is active). Waits on the TX-not-full IRQ **only while the FIFO is full**; otherwise sleeps 1 ms, so it can never spin and starve `plan`/`proto` |
| `plan` (Planner) | High | Switches, DIR pause, settle, underrun check, status (~200 Hz) — does **not** fill FIFO |
| `proto` (Protocol) | Medium | USB CDC + UART 1 Mbaud RX/TX, verbose push, LED heartbeat (~67 Hz state patterns) / WDT |
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
4. **Live retarget** — `MT` / `SS` / `SA` update target/cruise/accel; next fill uses new remaining distance.
5. **Reverse** — decelerate to 0 → `dir_change_pause_s` → accelerate the other way.
6. **Soft limits** clamp remaining steps; illegal `MT` outside limits is rejected.
7. **Homing** — FSM via `MH` (`home_mode`, `home_speed`, `home_accel`, `home_move_out`); mode `0` = silent no-op.

API units mm / mm/s / mm/s²; internals use steps via `steps_per_mm`.

Shared math (host-testable): `include/planner_math.h`, `src/motion/planner_math.cpp`.

## Path playback (2nd planner)

`PC`/`PD`/`PG`/`PN`/`PS` (see [PROTOCOL.md](PROTOCOL.md#p--path-host-authored-motion-path)) implement a host-authored motion
path via a second, deliberately simpler planner in `src/motion/motion_path.cpp`,
kept separate from the sine-ramp planner above.

- **Buffer:** a flat `int16_t` array (`PATH_BUFFER_MAX` = 65536 samples, 128 KB,
  static — no malloc), holding one signed µm delta-distance per fixed time
  slice (`PS`, µs). `PD` appends; `PG` always plays from sample 0.
- **Playback:** the `feed` task calls `motion_path_fill_fifo()` instead of
  `planner_fill_fifo()` while path-mode is active. Each slice converts to a
  step count (`steps_per_mm`) and a PIO delay (constant rate for that slice —
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
  status queries, `Help`, and `CG` are allowed. Speed/accel limits are **not**
  checked — the host is
  trusted to deliver an already-limited path, same stance as elsewhere.

Files: `include/motion_path.h`, `src/motion/motion_path.cpp`.

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
- Soft limits (`slider_min` / `slider_max`) are separate and unchanged.

## Stop vs Halt

- **`MS` / realtime `!`:** soft decelerate via stop-distance law; enable unchanged; normal jog/move workflow.
- **`H` / `HT` / hard limit / `PIN_DRV_ERROR`:** `planner_halt()` — immediate FIFO abort, EN off, cancel waits/chain.

## `PIN_DRV_ERROR`

Always sampled (polarity `DRV_ERROR_active`), ~20 ms debounce. Works if already asserted at power-up (no rising edge required). While stable-asserted: `drv_error=1`, halt, protocol gate (`!E:emo active` except diagnostics/`CS`/`CG`/halt). On release: clear `drv_error` only.

## Homing

Requires `enable=1` and a valid `home_mode` plus matching `*_use` flag. `IH` / `IsHoming` is 1 for the whole cycle.

1. If sitting on a hard limit that is not already the reference: drive out until released (`ClearHard`).
2. If already on the reference: skip seek and start backoff.
3. **Seek** toward the reference (modes 1/3 −, 2/4 +) at `home_speed` / `home_accel`. Soft limits do not clamp. Max travel `1.1 × (slider_max − slider_min)` → `!E:home travel`.
4. On reference assert: reverse (**Backoff**), leave the switch, then continue `home_move_out` mm.
5. Set machine position to `slider_min` (1/3) or `slider_max` (2/4); clear `homing`.

Mode 3/4: the reference limit does not raise a hard-limit fault during seek (it ends seek). Modes 1/2: hitting L/R hard limit aborts with `!E:home hard` (and `planner_halt`). `MS` soft-cancels; `H`/`HT` emergency-halts. Outside the cycle, `PIN_SW_HOME` never halts motion.

## Current milestone

- Real PIO + FIFO feed + sine seek planner with live retarget: **implemented**.
- Hard limits L/R (debounced, immediate halt): **implemented**.
- Homing cycle (`MH`): **implemented**.
- Stop vs Halt + `PIN_DRV_ERROR` poll/gate: **implemented**.
