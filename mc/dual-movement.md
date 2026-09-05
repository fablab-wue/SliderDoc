<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "About dual movement - 2 axis slider";
  --doc-path: ".\\SliderDoc\\mc\\dual-movement.md";
}
</style>

# About dual movement - 2 axis slider

How SliderMC coordinates **two STEP/DIR axes** when `axis2_use=1`. Typical rig: **axis 1 = linear travel** (slider), **axis 2 = pan** (tilt or turn also work). Dual `MT` / `M` is a **time-synced** dual move (both finish together), **not** a CNC-style diagonal feedrate.

UIC apps use [`MC_Client`](https://github.com/fablab-wue/SliderCtrl/blob/main/MC_client.py): `axis_count`, optional `moveTo(pos, pos2)` / `home(axis)`, `set_axis_status_callback` — see [UIC API](../uic/api/overview.md). Shipping JKSlider / B4Slider remain 1-axis faces (`UIC_Base` uses axis 1). Verbose `#…` joins per-axis groups with ` | ` (see [protocol — Verbose push](../contract/protocol.md#verbose-push-3-hz-when-session-verbose1)).

**Related:** [config.md](config.md) · [motion.md](motion.md) · [motion-joy.md](motion-joy.md) · [protocol — Optional 2nd axis](../contract/protocol.md#optional-2nd-axis-axis2_use) · [pins.md](pins.md)

---

## Enabling axis2

1. `CS axis2_use 1` (persist with normal config save / `mc.ini`).
2. **Reboot** with `RB` / `Reboot`, or power-cycle.

`CS` updates config, `IA`, and the welcome banner immediately, but the second PIO state machine and axis-2 GPIOs are set up only at boot. Dual `MT` before reboot can leave `pos2` stuck at 0.

Supported boards: Pico / Pico W / RP2040-Zero. Pin map: [pins.md](pins.md).

---

## Dual `MT` / `M` timing (not CNC)

Session **`SS` / `SA`** (and `init_speed` / `init_accel`) set **axis-1** cruise and peak accel.

When **both** axes move (`MT a b` with both deltas ≠ 0), firmware scales axis-2 so both finish together:

\[
v_2 = v_1 \cdot \frac{|d_2|}{|d_1|},\quad a_2 = a_1 \cdot \frac{|d_2|}{|d_1|}
\]

(clamped to `max_speed` / `max_accel` on axis 1 and `max_speed_2` / `max_accel_2` on axis 2; see `motion_move_to2` in SliderMC `planner.cpp`).

- Axis-2-only (`MT _ b`) uses full `SS`/`SA` on axis 2.
- Axis-1-only (`MT 200`) leaves axis 2 idle.

**Not CNC:** there is **no** path-length / feedrate along a diagonal. Each axis is an independent STEP/DIR profile; they are **time-synced** from the axis-1 distance ratio. Tool-path “G1 F…” diagonal speed does not apply.

Example: `SS 50`, `MT 100 20` → axis1 ≈ 50 u/s, axis2 ≈ 10 u/s (ratio 20/100).

### Mid-move `SS` / `SA`

On a coordinated dual seek, firmware keeps the start ratio \(r = |d_2|/|d_1|\).

- `SS` / `SA` set **axis-1** cruise / accel (session values).
- Axis-2 is updated as \(v_2 = v_1 \cdot r\), \(a_2 = a_1 \cdot r\) (same clamps as at `MT` start).

So a speed or accel change mid-move keeps both axes finishing **at about the same time**. A new dual `MT a b` replaces \(r\) from the new deltas. Coordination ends on single-axis `MT`/`M`, jog, halt, soft reset, or when both axes go idle. Soft stop (`MS`) does not clear \(r\) immediately — scaled accel stays on axis-2 for a matched decelerate; mid-stop `SA` still rescales until both idle.

---

## Soft stop (`MS`) on both axes

`MS` / soft stop applies to **every active axis** independently: each decelerates to 0 with its own `accel_mm_s2`.

On a coordinated dual `MT` (both deltas ≠ 0), axis 2 still carries the scaled cruise/accel (\(v_2/a_2 \approx v_1/a_1\)), including after mid-move `SS`/`SA`. Soft-stop duration scales like \(v/a\), so both axes usually finish decelerating **at about the same time**.

This is **not** a dedicated sync-stop controller — only matching per-axis physics. Sync can break if `max_speed` / `max_speed_2` / `max_accel` / `max_accel_2` clamped an axis, one axis was already braking for its target, or the move was jog / joy / single-axis (no dual scaling).

---

## Unit-less args (mm or degrees)

Protocol text often says mm / mm/s / mm/s², but values are **user units** converted with `steps_per_unit` / `steps_per_unit_2`.

| Setup | Treat args as | Set |
|-------|---------------|-----|
| Linear slider | mm, mm/s, mm/s² | `steps_per_unit` = steps per mm; `unit_name=mm` |
| Rotary / pan | °, °/s, °/s² | `steps_per_unit` (or `_2`) = steps per degree; `unit_name=deg` |

`CG unit_name` lets a UIC show the unit label (default `mm`). Soft limits, `IP`, and verbose positions use the same user unit.

Legacy CS aliases: `steps_per_mm` / `steps_per_mm_2` still set the same fields; `CG`/`foreach` emit the new names.

---

## Endless rotation: soft limits `none`

```text
CS slider_min none
CS slider_max none
CS slider_min_2 none
CS slider_max_2 none
```

(`-` is also accepted.) Soft travel bounds are disabled for that axis — typical for a continuous pan.

**Omitting** keys is not the same as `none`: factory defaults apply (`0` / `600`). Hard limits and homing stay independent if enabled. With soft min/max `none`, homing falls back to position **0** as the home target.

---

## Split config (axis 1 vs 2)

| Axis 1 | Axis 2 |
|--------|--------|
| `steps_per_unit` | `steps_per_unit_2` |
| `slider_min` / `slider_max` | `slider_min_2` / `slider_max_2` |
| `DRV_*_active`, `SW_*`, `home_*` | same keys with `_2` |
| `max_speed` / `max_accel` | `max_speed_2` / `max_accel_2` |

**Shared** (not per-axis): session `SS`/`SA`, `unit_name`, `axis2_use`, `name`, ramp/path globals, debug/verbose init. `MJ` uses session `SS` as 100 % and clamps each axis to its own `max_speed` / `max_speed_2`.

Full tables: [config.md](config.md).

---

## Practical suggestions

1. **Skip token:** `MT _ 45` for pan-only; `MT 200` stays axis1-only.
2. **Jog masks:** `ML` / `MR` with `0|1|2` — which axes jog (`0` = both when axis2 is on).
3. **Joystick:** `MJ pct [pct2]` — independent signed % of `SS` per axis (omit `pct2` → axis 2 = 0). Not dual-`MT` time-sync. See [motion-joy.md](motion-joy.md).
4. **Prefer pan on axis 2** — keeps linear “mm” on axis 1 (`IP` first field / UIC habit). `WP` / `WaitPos` is axis 1 only (optional 2nd arg is timeout). In-move `;` chains: [command-chains.md](../architecture/command-chains.md).
5. **`max_speed` / `max_speed_2` clamp:** if `|d2| ≫ |d1|`, scaled `v2` may hit `max_speed_2` and **lose** perfect time sync — shorten the axis2 move, raise the cap, or move axes sequentially. Mid-move `SS`/`SA` stay time-synced while coordination is active (same clamp still applies).
6. **Path mode (`PG`):** dual `PD` is **slice-timed**, not the same as dual-`MT` distance scaling. See [motion-path.md](motion-path.md).
7. **UIC:** JKSlider / B4Slider UIs are still mostly 1-axis; dual `MT` is driven by hosts/scripts. Use `CG unit_name` for the display unit.

---

## Quick checklist

- [ ] `CS axis2_use 1` → save → **`RB`**
- [ ] `steps_per_unit` / `_2` match mechanics (mm or °)
- [ ] `unit_name` set for UIC (`mm` or `deg`)
- [ ] Soft limits `none` on any endless rotate axis
- [ ] Watch `|d2|/|d1|` vs `max_speed` / `max_speed_2` on dual seeks
