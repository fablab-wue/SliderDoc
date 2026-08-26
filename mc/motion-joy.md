<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Joystick control — technical manual";
  --doc-path: ".\\SliderDoc\\mc\\motion-joy.md";
}
</style>

# Joystick control — technical manual

**MoveJoy** (`MJ`) is a single command for driving SliderMC from an analogue
joystick (or any host that streams a signed speed). It covers 1-axis and
2-axis sliders: one packet is a full velocity snapshot, the planner holds
that speed until the next `MJ`, a rail, or another move command.

This sits beside the normal sine-ramp planner (`MT`/`M`/`ML`/`MR`/`MH`) and
the host-authored [Motion Path](motion-path.md) player. Command reference:
[protocol.md — M — Movement](../contract/protocol.md#m--movement-silent).
Hardware notes for a panel stick: [joysticks.md](../components/joysticks.md).

## Why not `ML` / `MR` + `SS` + `MS`?

Those four commands can approximate a stick, but they fight the protocol:

- `SS` is the **100 % reference** for later `MT`/`ML` — a stick must not
  overwrite it on every deflection.
- Dual-axis sticks need **independent** signed speeds (`MJ 40 -20`). Dual
  `MT` time-sync and a single session cruise cannot do that.
- Typical update rate is **5–20 Hz** (also acyclic). Re-issuing a long
  position jog on every packet would restart ramps and eventually expire.

`MJ` is a **velocity hold**: cruise is `% of SS` (clamped per axis), the
target is the soft-limit in that direction, and identical repeats are a
no-op.

It is recommended for the sender (UIC) not to send an `MJ` command if the
value has not changed, to reduce the payload on the serial link.

## Commands

| Short | Long | Args | Description |
|-------|------|------|-------------|
| `MJ` | `MoveJoy` | `pct [pct2]` | Signed joy speed as **percent of session `SS`**. Negative = left (`ML`), positive = right (`MR`), `0` = soft-stop (normal `SA` deceleration). Optional 2nd arg on a 2-axis slider. |
| `SS` | `SetSpeed` | `v` or bare | 100 % reference (mm/s). Legal **during** joy-mode; rescales live cruise. |
| `SA` | `SetAccel` | `a` or bare | Ramp used for accel/decel (including stick changes and `MJ 0`). Legal during joy-mode. |
| `MS` | `MoveStop` | — | Ends joy-mode and soft-stops (same as other moves). |

Success is silent (like `ML`/`MR`). Needs `SE 1`. Rejected while path-mode
is active (`!E:busy path active`) and while disabled (`!E:disabled`).

## Speed law

```text
v = (pct / 100) * session SS
v = clamp(|v|, 0, max_speed[axis])   # plus PIO max step Hz
sign(v) = sign(pct)
```

- Values above 100 % are allowed; they **clamp**, they do not error.
- Axis 1 clamps to `max_speed`; axis 2 to `max_speed_2`.
- `|pct| < 1e-3` counts as 0 (float noise). Deadband belongs on the UIC.
- `MJ` does **not** change session `SS`. After joy ends, `MT`/`ML` still use
  the previous cruise.

## 1-axis vs 2-axis snapshot

Each `MJ` is a **complete** velocity snapshot:

| Call | 1-axis | 2-axis (`axis2_use=1`) |
|------|--------|------------------------|
| `MJ 40` | axis 1 = 40 % | axis 1 = 40 %, **axis 2 = 0 %** (soft-stop) |
| `MJ 40 -20` | `pct2` ignored | independent cruises (not dual-`MT` time-sync) |
| `MJ 0` / `MJ 0 0` | soft-stop | soft-stop both |
| `MJ` (no args) | `!E:parse` | `!E:parse` |

## Joy-mode

The first `MJ` enters **joy-mode** and ramps toward the commanded velocity
(`SA`). Joy-mode **stays on** even at 0 % so a later `MJ 50` is just another
setpoint.

These **exit** joy-mode and take over motion: `MT`, `M`, `ML`, `MR`, `MH`,
`MS`, realtime `!`, `HT`/`H`, path `PG`.

`SS` / `SA` (including bare reset to `init_*`) do **not** exit joy-mode.
`SS` updates the 100 % reference; live cruise becomes
`(stored_pct / 100) * new_SS`, then clamped per axis, then ramps with
current `SA`.

No comms-loss timeout — last `MJ` holds (needed for acyclic sends). Send
`MJ 0` to stop from the stick; `MS` is an explicit stop that also leaves
joy-mode.

## Limits

- **Soft rail:** remaining distance clips to the session working window
  (`SL`/`SR`, boot-copied from `slider_min` / `slider_max`). The axis sits
  there with **no `!E`**. Reverse `MJ` moves away. See [working-window.md](working-window.md).
- **Hard-limit trip while moving:** same `planner_halt_all()` as other moves
  (EN off).
- Already blocked by a latched hard switch in that direction: that axis
  sits; the other axis may still move.

## Typical command flow

UIC SPEED pot maps to `SS`; the stick maps to `MJ` percentages:

```text
...
SS 30     # user change speed with potentiometer
...
MJ 5      # user begins playing with joystick
MJ 10
MJ 20
MJ 60
MJ 100
...
SS 50     # user change speed with potentiometer

MJ 100
MJ 50
MJ 0      # movement stops
...
MS      # explicit stop command
```

Two-axis example (linear + pan):

```text
SE 1
SS 40
SA 120
MJ 80 -25     # axis1 80 % of SS right; axis2 25 % of SS left
MJ 80 -25     # identical — UIC should skip this packet
MJ 0 0        # both axes soft-stop; still in joy-mode
MT 100        # ends joy-mode; seek uses current SS (40)
```

## Configuration

| Key | Role |
|-----|------|
| `max_speed` | Ceiling for `SS` and axis-1 cruise (including `MJ`) |
| `max_speed_2` | Axis-2 cruise ceiling (independent of `SS`) |
| `max_accel` / `max_accel_2` | Per-axis cap on session `SA` when applied to that axis |
| `init_speed` / `init_accel` | Reloaded by bare `SS` / `SA` (still legal in joy-mode) |

See [config.md](config.md). Dual-axis timing for `MT` (not `MJ`):
[dual-movement.md](dual-movement.md).

## Implementation reference (for firmware developers)

| Piece | File |
|-------|------|
| `motion_joy()` / `motion_end_joy()` | [include/motion_api.h](https://github.com/fablab-wue/SliderMC/blob/main/include/motion_api.h) |
| Velocity-hold, joy-mode flag, `SS`/`SA` rescale | [src/motion/planner.cpp](https://github.com/fablab-wue/SliderMC/blob/main/src/motion/planner.cpp) |
| Host-test stub | [src/motion/motion_stub.cpp](https://github.com/fablab-wue/SliderMC/blob/main/src/motion/motion_stub.cpp) |
| Command dispatch + help | [src/protocol/commands.cpp](https://github.com/fablab-wue/SliderMC/blob/main/src/protocol/commands.cpp) |
| `max_speed_2` / `max_accel_2` | [config.md](config.md), SliderMC `config_store` |
| Host tests | SliderMC `test/host/test_protocol_main.cpp` |
