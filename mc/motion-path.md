<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Motion Path — technical manual";
  --doc-path: ".\\SliderDoc\\mc\\motion-path.md";
}
</style>

# Motion Path — technical manual

A **Motion Path** is a host-authored motion profile: a PC application or other
UIC pre-computes a sequence of tiny position deltas (already speed/accel
limited) and streams it into SliderMC, which plays it back at a fixed,
configurable time-slice. This is a second, deliberately simple "player"
alongside the normal sine-ramp planner (`MT`/`M`/`ML`/`MR`/`MJ`/`MH`) — see
[MOTION.md](MOTION.md#path-playback-2nd-planner) for the internal architecture
and [PROTOCOL.md](../contract/protocol.md#p--path-host-authored-motion-path) for the
command reference. This document explains the feature end to end for
integrators writing the PC/UIC side.

## Why a separate path player?

The normal planner (`MT`, `SS`, `SA`, …) computes its own S-curve ramps and
checks `max_speed`/`max_accel`. That is the right model for interactive jogs
and absolute moves, but wrong for a pre-authored path: the host already knows
the exact position at every instant (e.g. a camera slider timeline exported
frame-by-frame), and re-deriving speed/accel on the device would only
reintroduce rounding and phase drift. Motion Path instead:

- trusts the host to have already limited speed and acceleration,
- takes one signed delta-distance sample **per fixed time slice**,
- converts each slice directly to a step count and a constant-rate PIO delay
  (no ramp within a slice),
- and hands off cleanly to the normal planner for stop/halt deceleration.

## Commands

| Short | Long | Args | Description |
|-------|------|------|-------------|
| `PC` | `PathClear` | — | Clear the path buffer (path count → 0). |
| `PD` | `PathData` | `um [um2]` | Append signed 16-bit µm sample(s); with axis2 on, optional 2nd sample (skip → `0`; single arg → `(a, 0)`). |
| `PG` | `PathGo` | — | Play the buffer from sample 0 until path count is reached, or `MS`/`H`. |
| `PN` | `PathNumber` | — | Reply `PN:<count>` — samples currently buffered. |
| `PS` | `PathSlice` | `us` or bare | Set the slice length in µs (≥1000); bare reloads the config default. |

All are silent on success except `PN` (`PN:<count>` reply). Errors use the
usual `!E:<code> <text>` form:

| Code | Command(s) | Meaning |
|------|------------|---------|
| `parse` | `PD`, `PS` | `PD` value outside -32768..32767, or `PS` below 1000 µs |
| `full` | `PD` | Buffer already holds `path_buffer_size` samples (checked whether or not playback is active) |
| `empty` | `PG` | No samples buffered yet |
| `disabled` | `PG` | Driver not enabled (`SE 1` first) |
| `busy` | `PC`, `PG`, `PS` | Rejected because path-mode is already active (see gating below) — `PD` is exempt, see live streaming |

## Data model

- **Sample:** one signed 16-bit integer, unit **µm** (micrometres), range
  `-32768..32767` (≈ ±32.767 mm of delta-distance per slice). With
  `axis2_use=1`, each `PD` can supply a second sample for axis 2; skip token
  `_` becomes `0` µm on that axis.
- **`0` means stand still** for that slice — no STEP pulses are issued; the
  PIO naturally holds its output level for the slice duration.
- **Buffer:** a flat array, not a ring buffer. `PD` always appends; `PG`
  always starts playback at sample 0. The buffer is **retained** after
  playback ends (naturally, or via `MS`/`H`), so `PG` can replay the same
  data without resending it.
- **Capacity:** `path_buffer_size` (config key, default 32000 samples,
  settable 1..32768 via `CS path_buffer_size <n>` / `CG path_buffer_size`).
  The static RAM buffer is `PATH_BUFFER_MAX` (32768) **per axis**; with axis2
  on, both axes share the same logical capacity.
- **Slice length:** `PS <us>` (µs, integer, ≥1000). This is a **session**
  value (like `SS`/`SA`), not persisted to `mc.ini` by `PS` itself — the
  persisted default is config key `init_path_slice_us` (default 10000 = 10
  ms), reloaded by a bare `PS`. The slice length is captured once when `PG`
  starts and stays fixed for that playback; changing `PS` mid-playback is
  rejected (`!E:busy`).

## Typical host sequence

```text
SE 1                   # enable the driver
PC                     # start from an empty buffer
PS 10000               # 10 ms per slice (optional — this is already the default)
PD 500                 # slice 0: +0.5 mm
PD 500                 # slice 1: +0.5 mm
PD 0                   # slice 2: stand still
PD -250                # slice 3: -0.25 mm
...
PN                     # -> PN:<count>, sanity-check before playing
PG                     # start playback
```

While playback is in progress, verbose/`?` status lines report state letter
`P` (see below). To stop early:

```text
MS                     # soft-decelerate from the current path speed
```

or, for an emergency stop:

```text
H                      # immediate halt, EN off, cancels waits/chain
```

### Live streaming (playing while still filling)

`PG` may be sent **before** the whole path has been transmitted — `PD` stays
allowed while playback is active (it is the one exception to the gating rule
below), so the host keeps calling `PD` after `PG`, as long as it stays ahead
of playback (poll `PN` to see how many samples have been buffered so far;
there is currently no direct "samples remaining" query, so the host should
track its own write count against `PN`/its own buffer size and leave
comfortable headroom). If playback catches up to the last buffered sample
before more `PD` data arrives, SliderMC treats that as the **end of the
path** (see below) and starts a normal soft-stop — there is no "hold and
wait for more data" mode. Hosts doing live streaming must keep enough
samples queued ahead of the current slice rate.

## Playback mechanics

For each slice, SliderMC:

1. Converts the signed µm distance to a step count using `steps_per_unit`.
2. Converts the slice time (µs) to PIO clock cycles.
3. If the step count is `0`, no STEP word is queued for that slice — the
   owed idle time is carried forward and merged into the delay ahead of the
   next real step word (see error diffusion below).
4. Otherwise, issues one or more constant-rate PIO STEP words (chunked to
   ≤64 pulses per word, matching hardware limits) covering exactly that
   slice's step count over that slice's time budget.

There is **no acceleration ramp within a slice** — slice-to-slice speed
changes are as abrupt as the sample sequence dictates. This is intentional:
the host is expected to have already shaped speed/accel across many slices
(e.g. a 10 ms slice at typical settings is far below any perceptible jerk).

### Error diffusion (why totals stay exact)

A naive per-slice "round distance to nearest step" or "round time to nearest
PIO cycle" would accumulate rounding error over a long path (thousands of
slices), causing the final position or the total elapsed time to drift.
Motion Path instead carries the fractional remainder from one slice to the
next, for both quantities independently:

- **Steps:** `steps_f = distance_mm * steps_per_unit + step_err_carry`;
  `steps_i = round(steps_f)`; `step_err_carry = steps_f - steps_i`. A `0`
  sample always yields exactly `0` steps and leaves the carry untouched, so
  a run of stand-still slices never "steals" or "donates" fractional steps.
- **Time:** `cycles_f = slice_us * (sysclk_hz / 1e6) + time_err_carry`;
  `cycles_i = round(cycles_f)`; `time_err_carry = cycles_f - cycles_i`.

Both accumulators guarantee that the sum of issued steps tracks the sum of
requested distance (and the sum of issued PIO cycles tracks the sum of
requested slice time) to within one unit over the whole path, however long.
These are pure functions (`motion_path_diffuse_steps` /
`motion_path_diffuse_cycles`) and are covered by host unit tests
(`test/host/test_motion_path.cpp`).

### End of path, `MS`, and `H`

Whichever way playback stops — the buffer is exhausted, or `MS`/`H` arrives
— SliderMC does the same thing: it takes the **current position and the
velocity implied by the last issued STEP word**, hands both to the normal
planner (`planner_takeover_from_path`), and then runs the ordinary
soft-stop (`MS`) or hard-halt (`H`) deceleration from that speed. There is no
separate "path deceleration" — the path player never invents its own ramp,
it only ever plays constant-rate slices and then lets the main planner do
what it already does for any other move.

## Gating: what else you can send during playback

While `PG` is active, SliderMC rejects most other commands with
`!E:busy path active`, to guarantee the path player is the sole owner of the
STEP FIFO until it ends. Allowed during playback:

- `MS`, `H` / `HT` / `Halt` (the only ways to end playback early)
- `PD` / `PathData` (live-move streaming — the only way to add more samples
  once `PG` is active; still rejected with `!E:full` at `path_buffer_size`)
- `PN` / `PathNumber`
- All status/query commands: `IM`, `IH`, `IL`, `IE`, `IP`, `IT`, `IR`, `IW`,
  `ID`, `IZ`, `IX` / `Pinout`, `GS`, `GA`, `GE`, `GT`, `GV`, `GD`,
  `VA`/`VF`/`VP`/`VG`
- `Help` / `HL` / `$`
- `CG` / `ConfigGet`

Everything else — including another `PG`, `PC`, `PS`, and all
move/session-set commands (`MT`, `M`, `ML`, `MR`, `MJ`, `MH`, `SS`, `SA`, `SE`,
`ST`, `SV`, `SD`, `CS`) — is rejected until playback ends.

## Status reporting

- **State letter:** `P` (new, alongside `E`/`I`/`M`/`A`/`B`/`H`/`L`/`D` — see
  [PROTOCOL.md](../contract/protocol.md#state-letters)). Verbose (`SV 1`) and realtime
  `?` both report it the same way as any other state.
- **Verbose/`?` payload:** `#P <pos> <vel> <accel>` — position and velocity
  are live (`vel` is the rate implied by the most recently issued STEP
  word); `accel` is always reported as `0`, since path-mode plays each slice
  at a constant rate and never computes an acceleration ramp. There is no
  target field (path-mode has no single target position).
- **`IM` / `IsMoving`** reports `1` while path-mode is active (it is a form
  of motion).
- **`IP` / `IsPosition`** reports the live position as the path advances.
- There is currently no query for "samples remaining to play" — use `PN`
  (total buffered) together with your own bookkeeping of how much you have
  sent if you need that during live streaming.

## Safety and limits

- **Hard-limit switches and `PIN_DRV_ERROR`** are still monitored and will
  halt the axis during path playback exactly as they do for any other move
  — path-mode is not a way to bypass the emergency stop chain.
- **Soft position limits** (`slider_min_mm`/`slider_max_mm`) are **not**
  checked per-slice during path playback, matching the project's stance
  that a Motion Path is pre-verified by the host — the same as speed/accel
  limits not being checked. Keep the path within the mechanical travel.
- **Speed and acceleration limits** (`max_speed_mm_s`/`max_accel_mm_s2`) are
  **not** enforced against path data — SliderMC assumes the host already
  produced a well-formed, speed/accel-limited path. A path that implies an
  unreasonable step rate will still be attempted (subject to the PIO's
  maximum step frequency).

## Configuration reference

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `path_buffer_size` | int | 32000 | `PD` sample capacity (1..32768); `CS`/`CG` |
| `init_path_slice_us` | int µs | 10000 | Default `PS` slice length (≥1000); reloaded by bare `PS` |

See [CONFIG.md](CONFIG.md) for the full config key list and general
CS/CG conventions.

## Implementation reference (for firmware developers)

| Piece | File |
|-------|------|
| Public API (`motion_path_clear/add/count/set_slice_us/go/is_active/fill_fifo/abort_to_planner/get_status`, plus the pure error-diffusion helpers) | [include/motion_path.h](../include/motion_path.h) |
| Implementation: buffer, error diffusion, FIFO feed, planner handoff | [src/motion/motion_path.cpp](../src/motion/motion_path.cpp) |
| Feed-task branch (`motion_path_fill_fifo()` instead of `planner_fill_fifo()` while active) | [src/motion/motion_task.cpp](../src/motion/motion_task.cpp) |
| `planner_takeover_from_path()` (seeds the main planner's position/velocity before a normal stop/halt) | [include/planner.h](../include/planner.h), [src/motion/planner.cpp](../src/motion/planner.cpp) |
| `MC_STATE_PATH` / state letter `P` | [include/motion_api.h](../include/motion_api.h), [src/protocol/verbose.cpp](../src/protocol/verbose.cpp) |
| Command dispatch, gating, `MS`/`H` handoff interception, help table | [src/protocol/commands.cpp](../src/protocol/commands.cpp) |
| Config fields + `CS`/`CG` keys | [include/config_store.h](../include/config_store.h), [include/config_defaults.h](../include/config_defaults.h), [src/config/config_store.cpp](../src/config/config_store.cpp) |
| Host unit tests (buffer, error diffusion, gating) | [test/host/test_motion_path.cpp](../test/host/test_motion_path.cpp), [test/host/test_protocol_main.cpp](../test/host/test_protocol_main.cpp) |

Run all host tests (including the Motion Path ones) with:

```powershell
powershell -File scripts/run_host_tests.ps1
```
