# B4Slider — User Manual

**B4Slider** — four-button camera slider panel

How to operate a **ready-configured** B4Slider on set.  
App: [`B4Slider.py`](../B4Slider.py) · config: [`B4SliderConfig.py`](../B4SliderConfig.py) (`B4S_*`).  
Shared motion / LED stack: [`docs/API.md`](../docs/API.md). Installer hub: [JKSlider_Technical_Manual.md](JKSlider_Technical_Manual.md).

B4Slider is a **minimal** UIC: **MOVE_L**, **MOVE_R**, **OPTION**, **SET**, one **SPEED** pot, and an RGB status LED. There is no keypad A/B/C, STOP key, DELAY, or TIMELAPSE. Soft travel limits **are** the A/B working window (see [Workflow: A / B](#workflow-a--b-soft-limits)).

Optional second pot (**ACCEL**) when `B4S_USE_ACCEL_POT=1`. OLED is not required.

The panel Pico talks to a **motion board** (SliderMC) over UART, or to an MKS SERVO via [`MC_MKS_Client`](../docs/MKS_SERVO_RS485.md). If that link is unplugged, the UI may still start, but moves will not work — see [Technical Manual — Link](JKSlider_Technical_Manual_Link.md#communication-mc--uic).

## Getting started

1. Power on — status LED does a rainbow while locked (if unlock is enabled).
2. **Unlock** — press **OPTION** (` * `). (Disable with `B4S_BOOT_UNLOCK = False`.)
3. Soft limits start at **full slider travel** (MC `slider_min` / `slider_max`). Nothing is remembered after power-off (no position file).
4. Dial **SPEED**, then use MOVE / SET as below.

**OPTION** is a modifier: hold it with another control. Alone it does nothing (except unlock at boot).

The **Key** column uses silk labels: ` < ` MOVE_L, ` > ` MOVE_R, ` * ` OPTION, ` S ` SET.

## Panel layout

```text
          [S]
  [← L]         [R →]
          [*]
        (SPEED pot)
```

Optional ACCEL pot sits beside SPEED when enabled in config.

## Knobs

### SPEED

- Left → slower floor; right → faster (finer at the low end; `B4S_SPEED_CURVE_GAMMA`).
- Can be changed while moving (unless OPTION is held for max-speed boost).
- Full-scale ceiling is the panel/MC max (`B4S_SPEED_MAX_MM_S` / MC `max_speed`).

### ACCEL (optional)

Only if `B4S_USE_ACCEL_POT = 1`:

- Left → gentler; right → snappier (same idea as JKSlider ACCEL).
- When the ACCEL pot is enabled, **SET hold** gestures for accel presets / learn are **off**.

Without an ACCEL pot, use **SET** holds for presets **L** (low) / **H** (high) — not related to A/B soft ends.

## Move

Cruise, jog, boost, stop, halt.

| Action | Key | Result |
|--------|-----|--------|
| **(MOVE_L / MOVE_R)** tap ≤⅓ s | ` < ` / ` > ` tap | **Locked cruise** toward that soft end at SPEED until stop, reverse, SET, halt, or arrival |
| **(MOVE_L / MOVE_R)** hold >⅓ s | ` < ` / ` > ` hold | Hold-to-run: moves while pressed; soft-stops on release |
| Same **MOVE** tip while locked | ` < ` or ` > ` tip | Soft-stop |
| Opposite **MOVE** while cruising | ` < ` or ` > ` | Reverse / retarget to the other soft end |
| **OPTION + (MOVE_L / MOVE_R)** tap / hold | ` * ` + ` < ` / ` > ` | Same as MOVE, but at panel **max speed** |
| **OPTION** hold while moving | ` * ` hold | Boost to max speed; release → back to SPEED pot |
| **SET** while moving | ` S ` | Soft-stop |
| **MOVE_L + MOVE_R** | ` < ` ` > ` | **Halt** (emergency stop); driver disabled until any key |
| **MOVE_L + MOVE_R** hold ≥ 1 s | ` < ` ` > ` hold ≥ 1 s | Swap left/right |
| **All four** (L+R+OPTION+SET) | ` < ` ` > ` ` * ` ` S ` | Halt + **reset like power-up** (full soft limits, loop off, accel preset L) |

Tap vs hold uses `B4S_MOVE_TAP_MS` (default **333 ms**). Left is toward decreasing position when `B4S_LEFT_IS_NEGATIVE` is True (default).

## Soft limits (A / B window)

There are no separate PosA / PosB buttons. The two soft ends **are** the shot window:

| Action | Key | Result |
|--------|-----|--------|
| **SET + MOVE_L** tap | ` S ` ` < ` tap | Set **soft_limit_L** = current position (white blip) |
| **SET + MOVE_R** tap | ` S ` ` > ` tap | Set **soft_limit_R** = current position (white blip) |
| **SET + MOVE_L** hold ≥ 1 s | ` S ` ` < ` hold ≥ 1 s | Reset soft_limit_L → full slider min |
| **SET + MOVE_R** hold ≥ 1 s | ` S ` ` > ` hold ≥ 1 s | Reset soft_limit_R → full slider max |
| **SET + L + R** hold ≥ 1 s | ` S ` ` < ` ` > ` hold ≥ 1 s | Reset **both** ends to full slider |

Travel is allowed **only** between soft_limit_L and soft_limit_R. MOVE cruise targets those ends (the old “goto A / B”).

## SET and OPTION

| Action | Key | Result |
|--------|-----|--------|
| **SET** tap (idle) | ` S ` tap | Nothing (avoids accidental presses) |
| **SET** hold ≥ 1 s (idle) | ` S ` hold ≥ 1 s | Accel **preset L** (low) — only if no ACCEL pot |
| **SET** hold ≥ 3 s (idle) | ` S ` hold ≥ 3 s | Accel **preset H** (high) — only if no ACCEL pot |
| **SET** hold ≥ 5 s (idle) | ` S ` hold ≥ 5 s | **Accel learn**: SPEED pot maps to accel while held; release latches into the active preset — only if no ACCEL pot |
| **OPTION + SET** tap | ` * ` ` S ` tap | Disable motor driver (dim orange LED) |
| **OPTION + SET** hold ≥ 1 s (idle) | ` * ` ` S ` hold ≥ 1 s | Toggle **loop** armed (single ↔ ping-pong between soft ends) |
| Any button while disabled | — | Re-enable driver |

While holding SET for accel, the LED flashes **white once per second** so you can count 1 / 3 / 5 without a display. Preset L / H / learn confirm with violet flashes (1 / 2 / 3).

**Loop:** arming does **not** start motion. Next MOVE cruise starts; on arrival at a soft end the carriage auto-retargets to the other end until you stop (SET / same MOVE tip / halt / all-four).

## Color codes

RGB status LED (shared [`UIC_Base`](../UIC_base.py)). Docs use **percent**; API uses 0…255 — see [API — RGB status LED](../docs/API.md#rgb-status-led-led_r--led_g--led_b--optional-neopixel).

| Color / pattern | Meaning |
|------------------|---------|
| Rainbow | Boot unlock (until OPTION) |
| Dim white | Idle, enabled, single-run |
| Dim white ↔ dim blue | **Loop armed** (idle) |
| Yellow | Accelerating or decelerating |
| Green | Moving at cruise speed |
| Green / yellow + ~30% blue | Near a soft end (`B4S_NEAR_SOFT_MM`, default 3 mm) |
| Green / yellow + 100% blue | At a soft end |
| + ~10% blue while looping | Ping-pong running |
| Dim orange | Driver **disabled** |
| Red fast blink | Hard limit |
| Red blink | Homing (if used on the motion board) |
| Solid red | DRV_ERROR / EMO |
| White blip | Soft limit set or reset confirm |
| White flash /s | SET hold second counter |
| Violet ×1 / ×2 / ×3 | Accel preset L / H / learn latched |
| Red flash (+ white ×3) | Halt / all-four power-up reset |

## Cheat card

```text
B4Slider
L/R tap      cruise to soft end
L/R hold     jog while held
L+R          HALT
L+R 1s       swap L/R
* + L/R      max-speed cruise
* hold       max speed while moving
* + S tap    disable; any key enables
* + S hold   loop on/off (next MOVE starts)
S tap        (idle: nothing)
S            stop (while moving)
S + L/R      set soft end here
S + L/R 1s   reset that soft end
S + L+R 1s   reset both soft ends
S hold 1s    accel preset L   [no ACCEL pot]
S hold 3s    accel preset H   [no ACCEL pot]
S hold 5s    accel learn pot  [no ACCEL pot]
*+S+L+R      HALT + reset like power-up
```

## Workflow: normal moving

1. **Unlock** with OPTION.
2. Dial **SPEED** (and ACCEL pot or SET presets L/H if no ACCEL pot).
3. **Tap** **MOVE_L** / **MOVE_R** for a short burst move: release within ~⅓ s and the slider continues cruising toward that soft end until you stop it, reverse it, or reach the limit.
4. **Hold** **MOVE_L** / **MOVE_R** longer than ~⅓ s for hold-to-run. The carriage moves while the button is down; release stops it.
5. **Same-side tap while cruising** stops the cruise; **opposite-side tap** reverses direction. This makes the move buttons behave like a left/right lock-and-stop control rather than a raw jog.
6. **OPTION before MOVE_L / MOVE_R** changes the start condition: when OPTION is already down before the move starts, the slider launches with **max speed + max accel**.
7. **OPTION during movement** is a speed boost only: **speed goes to max_speed**, while **accel stays at the current pot/preset value** until OPTION is released.
8. If you want to keep the current pot accel but make the move faster, hold OPTION after the move is already running. If you want the full startup acceleration burst, press OPTION before the move.
9. **SET** while moving soft-stops the carriage. **MOVE_L + MOVE_R** is the emergency halt; any button re-enables the driver after a disabled state.
10. **All four** (MOVE_L + MOVE_R + OPTION + SET) resets the session like power-up and clears the soft-limit / loop state.

## Workflow: A / B (soft limits)

Use the soft ends as your two shot marks.

1. **Unlock** — press OPTION if the LED is still rainbow.
2. **Open the window** (optional) — if limits were shrunk earlier: **SET + L + R** hold ≥ 1 s to restore full travel.
3. **Frame end A** — MOVE or hold-jog to the first pose. Press **SET + MOVE_L** tap → soft_limit_L saved (white blip).
4. **Frame end B** — move to the second pose. **SET + MOVE_R** tap → soft_limit_R saved.
5. **Rehearse** — dial SPEED; **MOVE_L** or **MOVE_R** tap to cruise to that end. Same tip stops; opposite tip reverses.
6. **Loop (optional)** — idle: **OPTION + SET** hold ≥ 1 s (LED white↔blue). Then MOVE tap; carriage ping-pongs until SET / same tip / L+R.
7. **Boost** — hold OPTION while moving, or start with OPTION+MOVE, for max speed.
8. **Reset ends** — SET+MOVE hold ≥ 1 s resets that side to full slider; or all-four for a full session reset.

## Config entries

Edit [`B4SliderConfig.py`](../B4SliderConfig.py) defaults, or overlay via `SliderPins.py`:

```python
B4Slider = { ... }      # consumed by B4SliderConfig.py
UIC_config = { ... }    # shared LED / OLED / camera (UIC_Base)
MC_config = { ... }     # UART / floors (MC_Client)
```

### Panel (`B4S_*` / pins)

| Key | Default | Meaning |
|-----|---------|---------|
| `PIN_BTN_MOVE_L` / `MOVE_R` | 6 / 7 | `<` / `>` |
| `PIN_BTN_OPTION` | 13 | `*` |
| `PIN_BTN_SET` | 5 | `S` (was STOP on JKSlider discrete map) |
| `PIN_POT_SPEED` | 26 | SPEED ADC |
| `PIN_POT_ACCEL` | 27 | ACCEL ADC if used |
| `B4S_USE_ACCEL_POT` | `0` | `1` = ACCEL pot on; disables SET accel holds |
| `B4S_ACCEL_PRESET_L` / `_H` | 100 / 400 | mm/s² presets (no ACCEL pot) |
| `B4S_SPEED_MIN_MM_S` | 1.0 | SPEED pot floor |
| `B4S_SPEED_MAX_MM_S` | 100.0 | Panel ceiling (also clamped by MC) |
| `B4S_ACCEL_MIN_MM_S2` / `_MAX_` | 50 / 500 | ACCEL pot range / learn range |
| `B4S_MOVE_TAP_MS` | 333 | Tap vs hold threshold (~⅓ s) |
| `B4S_LONG_PRESS_MS` | 1000 | ≥ 1 s |
| `B4S_EXTRA_LONG_MS` | 3000 | ≥ 3 s |
| `B4S_LEARN_HOLD_MS` | 5000 | ≥ 5 s accel learn |
| `B4S_LEFT_IS_NEGATIVE` | `True` | Left toward decreasing mm |
| `B4S_NEAR_SOFT_MM` | 3.0 | Near-soft LED distance (also sets UIC warn) |
| `B4S_LOOP_BLUE_ADD` | 26 | ~10% blue while looping (0…255) |
| `B4S_BOOT_UNLOCK` | `True` | Require OPTION before enable |
| `B4S_LED_FLASH_ON_MS` / `_OFF_` | 80 | Flash timing |
| `B4S_LED_BLIP_MS` | 120 | Soft-limit confirm blip |
| `B4S_LED_PINGPONG_MS` | 600 | Loop-armed white↔blue period |

### Shared LED (`UIC_config`)

| Key | Default | Meaning |
|-----|---------|---------|
| `SOFT_LIMIT_WARN_MM` | 10.0 | Near-soft distance (B4Slider overwrites from `B4S_NEAR_SOFT_MM` at run) |
| `LED_SOFT_NEAR_BLUE_ADD` | 76 | ~30% blue add (0…255) |
| `LED_SOFT_AT_BLUE_ADD` | 255 | 100% blue add at soft end |
| `LED_DIM_WHITE` / `LED_DIM_ORANGE` | 0.12 | Idle / disabled duty (0…1) |
| `LED_BLINK_HARD_LIMIT_MS` | 80 | Hard-limit red blink half-period |

Deep wiring, SliderMC, and library details: [Technical Manual](JKSlider_Technical_Manual.md), [API](../docs/API.md), [ARCHITECTURE](../docs/ARCHITECTURE.md).
