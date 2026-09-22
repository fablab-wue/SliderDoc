<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "About dual movement - 2 axis slider";
  --doc-path: ".\\SliderDoc\\mc\\dual-movement.md";
}
</style>

# About dual movement - 2 axis slider

How SliderMC coordinates **two STEP/DIR motors** when `motors=2`. Typical rig: **motor 1 = linear travel** (slider), **motor 2 = pan** (tilt or turn also work). Dual `MT` / `MB` is a **time-synced** dual move (both finish together), **not** a CNC-style diagonal feedrate. `motors=3` exists (third STEP/DIR, same protocol tokens); optional RC servos pack after motors. This page keeps the 2-motor timing story.

UIC apps use [`MC_Client`](https://github.com/fablab-wue/SliderCtrl/blob/main/MC_client.py): `getMotorCount()`, packed `axis_count`, optional `moveTo(pos, pos2)` / `home(axis)`, `set_axis_status_callback` — see [UIC API](../uic/api/overview.md). Shipping JKSlider stays 1-motor; B4Slider selects packed axes **1–5** (`getAxisCount()`). Verbose `#…` joins packed groups with ` | ` (`#I p1 | p2` — see [protocol — Verbose push](../contract/protocol.md#verbose-push-3-hz-when-session-verbose1)).

**Related:** [config.md](config.md) · [motion.md](motion.md) · [motion-joy.md](motion-joy.md) · [protocol — Live axis count](../contract/protocol.md#live-axis-count-axis) · [pins.md](pins.md)

---

## Enabling motor 2

1. `CS motors 2` (persist with normal config save / `mc.ini`). Use `CS motors 3` for a third STEP/DIR motor.
2. GPIO / PIO re-init **immediately** — no `RB` required.

**`CS axis` is rejected.** Dual `MT` is valid as soon as `IA` shows the new sum.

Supported boards: Pico / Pico W / RP2040-Zero. Pin map: [pins.md](pins.md).

---

## Dual `MT` / `MB` timing (not CNC)

Session **`SS` / `SA`** (and `init_speed` / `init_accel`) set **axis-1** cruise and peak accel/decel. `SA a` sets both ramps; `SA a d` splits them. Dual scaling applies to **both**.

When **both** axes move (`MT a b` with both deltas ≠ 0), firmware scales axis-2 so both finish together:

\[
v_2 = v_1 \cdot \frac{|d_2|}{|d_1|},\quad a_2 = a_1 \cdot \frac{|d_2|}{|d_1|},\quad d_{\mathrm{dec},2} = d_{\mathrm{dec},1} \cdot \frac{|d_2|}{|d_1|}
\]

(clamped to `max_speed_1` / `max_accel_1` on axis 1 and `max_speed_2` / `max_accel_2` on axis 2; see `motion_move_to2` in SliderMC `planner.cpp`).

- Axis-2-only (`MT _ b`) uses full `SS`/`SA` on axis 2.
- Axis-1-only (`MT 200`) leaves axis 2 idle.

**Not CNC:** there is **no** path-length / feedrate along a diagonal. Each axis is an independent STEP/DIR profile; they are **time-synced** from the axis-1 distance ratio. Tool-path “G1 F…” diagonal speed does not apply.

Example: `SS 50`, `MT 100 20` → axis1 ≈ 50 u/s, axis2 ≈ 10 u/s (ratio 20/100).

### Mid-move `SS` / `SA`

On a coordinated dual seek, firmware keeps the start ratio \(r = |d_2|/|d_1|\).

- `SS` / `SA` set **axis-1** cruise / accel / decel (session values).
- Axis-2 is updated as \(v_2 = v_1 \cdot r\), \(a_2 = a_1 \cdot r\), \(d_{\mathrm{dec},2} = d_{\mathrm{dec},1} \cdot r\) (same clamps as at `MT` start).

So a speed or accel change mid-move keeps both axes finishing **at about the same time**. A new dual `MT a b` replaces \(r\) from the new deltas. Coordination ends on single-axis `MT`/`MB`, joy, halt, soft reset, or when both axes go idle. Soft stop (`MS`) does not clear \(r\) immediately — scaled accel stays on axis-2 for a matched decelerate; mid-stop `SA` still rescales until both idle.

---

## Soft stop (`MS`) on both axes

`MS` / soft stop applies to **every active axis** independently: each decelerates to 0 with its own `decel_mm_s2`.

On a coordinated dual `MT` (both deltas ≠ 0), axis 2 still carries the scaled cruise/accel/decel (\(v_2/a_2 \approx v_1/a_1\)), including after mid-move `SS`/`SA`. Soft-stop duration scales like \(v/d_{\mathrm{dec}}\), so both axes usually finish decelerating **at about the same time**.

This is **not** a dedicated sync-stop controller — only matching per-axis physics. Sync can break if `max_speed_1` / `max_speed_2` / `max_accel_1` / `max_accel_2` clamped an axis, one axis was already braking for its target, or the move was jog / joy / single-axis (no dual scaling).

---

## Unit-less args (mm or degrees)

Protocol text often says mm / mm/s / mm/s², but values are **user units** converted with `steps_per_unit_1` / `steps_per_unit_2`.

| Setup | Treat args as | Set |
|-------|---------------|-----|
| Linear slider | mm, mm/s, mm/s² | `steps_per_unit_1` = steps per mm; `motor_1_unit=mm` |
| Rotary / pan | °, °/s, °/s² | `steps_per_unit_1` (or `_2`) = steps per degree; `motor_N_unit=deg` |

`CG axis_N_unit` is the packed label a UIC shows. It is generated from `motor_N_unit` (default `mm`) or `servo_N_unit` (default `deg`). **`CS axis_N_unit` is rejected.** Soft limits, `IP`, and verbose positions use the same user unit.

Same-release synonyms: `steps_per_mm_1` / `steps_per_mm_2` still set the same fields; `CG`/`foreach` emit the canonical names. There are **no aliases** for unnumbered `steps_per_unit` / `steps_per_mm`.

---

## Endless rotation: soft limits `none`

```text
CS MOTOR_1_min none
CS MOTOR_1_max none
CS MOTOR_2_min none
CS MOTOR_2_max none
```

(`-` is also accepted.) Soft travel bounds are disabled for that axis — typical for a continuous pan.

**Omitting** keys is not the same as `none`: factory defaults apply (`0` / `600`). Hard limits and homing stay independent if enabled. With soft min/max `none`, homing falls back to position **0** as the home target.

---

## Split config (axis 1 vs 2)

| Axis 1 | Axis 2 |
|--------|--------|
| `steps_per_unit_1` | `steps_per_unit_2` |
| `MOTOR_1_min` / `MOTOR_1_max` | `MOTOR_2_min` / `MOTOR_2_max` |
| `DRV_*_1_active`, `SW_*_1_*`, `home_*_1` | same keys with `_2` (digit before `_active` / `_use`) |
| `max_speed_1` / `max_accel_1` | `max_speed_2` / `max_accel_2` |

**Shared** (not per-motor): session `SS`/`SA` (master units), `motors`/`servos`, `name`, ramp/path globals, debug/verbose init. Each motor has `motor_N_unit`; each servo has `servo_N_unit`. Packed `axis_N_unit` is generated from those and is read-only. `MJ` uses session `SS` as 100 % and clamps each motor to its own `max_speed_N`. Packed servos use `SERVO_N_*`. Motor 3 uses the matching `_3` keys when `motors=3`.

Full tables: [config.md](config.md).

---

## Practical suggestions

1. **Skip token:** `MT _ 45` for pan-only; `MT 200` stays axis1-only. Extra live axes take a 3rd token (`MT a b c`); skip `_` idles that axis.
2. **Hold-to-jog:** `SS` then `MJ ±100` (per-axis `0` on extras), `MS` on release. There is no `ML`/`MR`.
3. **Joystick:** `MJ pct [pct2 [pct3]]` — independent signed % of `SS` per axis (omit extra → that axis = 0). Not dual-`MT` time-sync. See [motion-joy.md](motion-joy.md).
4. **Prefer pan on motor 2** — keeps linear “mm” on motor 1 (`IP` first field / UIC habit). `WP` / Wait Pos is the **time-sync master** (optional 2nd arg is timeout). In-move `;` chains: [command-chains.md](../architecture/command-chains.md). Homing: `MH 1|2|3` (motors only).
5. **`max_speed_1` / `max_speed_2` clamp:** if `|d2| ≫ |d1|`, scaled `v2` may hit `max_speed_2` and **lose** perfect time sync — shorten the axis2 move, raise the cap, or move axes sequentially. Mid-move `SS`/`SA` stay time-synced while coordination is active (same clamp still applies).
6. **Path mode (`PG`):** extra `PD` args are **slice-timed**, not the same as dual-`MT` distance scaling. See [motion-path.md](motion-path.md).
7. **UIC:** both JKSlider and B4Slider select packed axes 1–6 (`getAxisCount()`). JKSlider MOVE/FAST send packed `MJ` with **0** on unselected live channels; B4Slider MOVE uses skipped `MT`. JKSlider A/B/C marks, loops, DELAY, and MSM stay **axis 1**. Hosts/scripts can still send dual `MT` directly. Use `CG axis_N_unit` for the display unit (`CS` rejects it; set `motor_N_unit` or `servo_N_unit`).

---

## Quick checklist

- [ ] `CS motors 2` (no `RB`)
- [ ] `steps_per_unit_1` / `_2` match mechanics (mm or °)
- [ ] `motor_N_unit` / `servo_N_unit` set for UIC (`mm` or `deg`; read back as `axis_N_unit`)
- [ ] Soft limits `none` on any endless rotate motor
- [ ] Watch `|d2|/|d1|` vs `max_speed_1` / `max_speed_2` on dual seeks
