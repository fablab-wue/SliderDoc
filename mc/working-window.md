<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Working Window — technical manual";
  --doc-path: ".\\SliderDoc\\mc\\working-window.md";
}
</style>

# Working Window — technical manual

A **working window** is the session travel clip on SliderMC: left and right soft
ends that bind `MT` / `ML` / `MR` / `MJ` (and friends) until reboot. It is the
protocol surface behind B4Slider’s **A/B** shot framing. Command reference:
[protocol.md — S / G](../contract/protocol.md#s--set-session-silent). Operator
model vs JKSlider marks: [marks-vs-working-window.md](../architecture/marks-vs-working-window.md).

## Envelope vs window

| Layer | Keys / commands | Persists |
|-------|-----------------|----------|
| **Envelope** | `slider_min` / `slider_max` (and `_2`) via `CS` / `mc.ini` | Yes — installer rail, homing pose/span |
| **Working window** | `SL` / `SR` (session); read with `GL` / `GR` | No — reboot / bare `SL`/`SR` reload from envelope |

Boot copies the envelope into the session window (same idea as `SS` from
`init_speed`). `none` on an envelope side means that side has no mechanical
clip (e.g. rotary); the session side starts disabled (`GL:-`).

**Do not** shrink the rail with `CS slider_min` for a shot. That overwrote the
envelope and survived power-off. Use `SL` / `SR` instead.

## Commands

| Short | Long | Args | Description |
|-------|------|------|-------------|
| `SL` | `SetLeft` | `[pos [pos2]]` | Session **min** (ML / −). Bare = reset to `slider_min` / `_2`. `none` = clear that side. |
| `SR` | `SetRight` | `[pos [pos2]]` | Session **max** (MR / +). Bare = reset to `slider_max` / `_2`. `none` = clear that side. |
| `GL` | `GetLeft` | — | Effective left: session, else envelope if set, else `-`. Dual: `GL:<a> <b>`. |
| `GR` | `GetRight` | — | Same shape as `GL`. |

Skip on one axis with `_` (leave unchanged). `none` stores session None for that
side — not a skip. Missing 2nd arg does **not** zero axis 2.

**Envelope fallback:** if the session side is None and `slider_min`/`max` is set,
`GL`/`GR` and motion clipping use the envelope value. Only when **both** session
and envelope are None is that side open (`GL:-`).

Silent on success. No `SE` required. Legal in joy-mode (does not exit `MJ`).
Rejected while path-mode is active (`!E:busy`). Not in the EMO allowlist.

| Code | Meaning |
|------|---------|
| `parse` | Bad args |
| `limit` | Past envelope, or effective left > right |

## Clip law

All moves (including `MJ`) use the **effective** working window (session, else
envelope) for remaining-distance clipping. Homing and path playback still use the
**envelope** (or ignore soft rails as documented elsewhere).

- Pose **inside** the window: travel stops softly at left/right.
- Pose **outside** (e.g. after `SL`/`SR`): motion **into** the window is
  allowed; further **out** sits with no `!E` spam (same as joy-at-rail).
- `CS slider_min/max` updates the envelope only and **clamps** the session
  window inward if needed; it does not reopen a narrowed shot by itself.

## Typical command flow

B4-style SET+MOVE mapped to the wire:

```text
...
GL              # GL:0     (boot = slider_min)
GR              # GR:600
...
SL 120          # SET+MOVE_L tap at 120 mm
SR 480          # SET+MOVE_R tap at 480 mm
ML              # cruise to left wall (120)
...
SL              # SET+MOVE_L hold — open left to slider_min
...
```

Two-axis skip / clear:

```text
SL _ 45         # axis2 left only (skip axis1)
GL              # GL:0.00 45.00
SL none 50      # clear axis1 (→ envelope if set); set axis2 to 50
SL _ none       # clear axis2 only
```

## UIC

[`MC_Client`](https://github.com/fablab-wue/SliderCtrl/blob/main/MC_client.py):

- `setLeft` / `setRight` / `getLeft` / `getRight` → `SL` / `SR` / cache
- `setSoftLimits(min, max)` → session `SL`+`SR` (**not** `CS`); `None` → `SL none` /
  `SR none` (effective limit = envelope when set)
- `slider_min` / `slider_max` stay the CG envelope after `fetchConfig`

**B4Slider** owns the operator chords; the window lives on the MC until reboot.
**JKSlider** keeps the session at full rail and stores A/B/C marks in the app.

## Configuration

| Key | Role |
|-----|------|
| `slider_min` / `slider_max` | Envelope (and homing); `none` disables that side |
| `slider_min_2` / `slider_max_2` | Axis-2 envelope |

See [config.md](config.md). Dual-axis units: [dual-movement.md](dual-movement.md).

## Implementation reference (for firmware developers)

| Piece | File |
|-------|------|
| Session fields / `session_set_window_*` | SliderMC `config_store` |
| Planner clip | `axis_hw_window_min/max` in [axis_hw.h](https://github.com/fablab-wue/SliderMC/blob/main/include/axis_hw.h); `soft_*_steps` in `planner.cpp` |
| Homing span / pose | still `axis_hw_slider_min/max` (envelope) |
| Command dispatch | [commands.cpp](https://github.com/fablab-wue/SliderMC/blob/main/src/protocol/commands.cpp) |
| Host tests | SliderMC `test/host/test_protocol_main.cpp` |
