# JKSlider — Technical Manual: Config

![JKSlider](../docs/img/jkslider-hero.png)

**JKSlider V1 by JK**

`JKSliderConfig.py` / UIC display-link pins and installer OLED/LED notes.  
Hub: [JKSlider_Technical_Manual.md](JKSlider_Technical_Manual.md).

Session vs persistent MC keys: [PROTOCOL — Session vs config](../../SliderMC/docs/PROTOCOL.md#session-vs-config) · [CONFIG.md keys](../../SliderMC/docs/CONFIG.md#keys).

## UIC display / link pins (`MC_config` / `UIC_config`)

Typical UIC defaults for the **SliderMC split** (edit via `SliderPins.py`):

| GPIO | Signal |
|------|--------|
| GP16 / 17 | UART_TX / UART_RX to SliderMC @ 1 Mbaud |
| GP22 | CTRL_CAMERA shutter / intervalometer |
| GP18–21 | free (optional NeoPixel / future IO) |
| GP2 / 3 / 4 | LED_R / LED_G / LED_B |
| GP0 / 1 | DSP_I2C_SDA / DSP_I2C_SCL |

STEP/DIR/EN, SW_HOME, DRV_ERROR, and hard limits are on the **SliderMC** Pico — see [PINS.md](../../SliderMC/docs/PINS.md) and [pico_pinout_mc.png](../../SliderMC/docs/img/pico_pinout_mc.png).

Also set `DSP_ENABLED`, LED polarity, etc. Motion ceilings (`max_speed`, `max_accel`) and soft travel (`slider_min` / `slider_max`) live on **SliderMC** and are read by UIC via `CG` after the welcome banner. Full list: [docs/API.md](../docs/API.md). Architecture: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## One file per slider HW (`SliderPins.py`)

For your hardware, copy [`SliderPins.example.py`](../SliderPins.example.py) → `SliderPins.py` and edit **that file only** (pins **and** behaviour). Keep one profile per physical slider build.

Shipped defaults stay in `MC_config.py` / `UIC_config.py` / `JKSliderConfig.py` — users normally do not edit those.

1. Copy the example → `SliderPins.py` on the UIC (gitignored locally).
2. Edit only the values you need. The file is **data only** — named dicts `MC_config`, `UIC_config`, and `JKSlider`.
3. Each defaults module imports `SliderPins` at the end and cherry-picks its dict into `globals()`. Missing keys / missing file = keep built-in defaults.

Later panel apps can add another dict (e.g. `OtherApp = { ... }`) in the same `SliderPins.py` and cherry-pick it from their own `*Config.py`.

## `JKSliderConfig.py` options

### Pins / input

| Option | Meaning |
|--------|---------|
| `JKS_INPUT_MODE` | `"button"` or `"keypad"` |
| `PIN_POT_SPEED` / `PIN_POT_ACCEL` / `PIN_POT_JOYSTICK` | ADC pots; joystick `None` = off |
| `PIN_BTN_*` | Discrete buttons (button mode) |
| `PIN_KEYPAD_ROWS` / `PIN_KEYPAD_COLS` | Keypad matrix |
| `PIN_BTN_STOP` | Always; ORed with matrix BTN_STOP in keypad mode |
| `PIN_BTN_OPTION` | Always; ORed with matrix OPTION (`*`) in keypad mode |

### Behaviour

| Option | Meaning |
|--------|---------|
| `JKS_MOVE_TAP_MS` | MOVE release ≤ this (ms) → locked cruise; longer hold → stop on release (default 333) |
| `JKS_SWAP_LR` | Initial L/R swap (also toggled at runtime) |
| `JKS_CAMERA_FPS` | Default shutter FPS for CTRL_CAMERA (30) |
| `JKS_CAMERA_FPS_STEPS` | FPS cycle list `(24, 25, 30, 48, 50, 60)` |
| `JKS_TL_MODE` | Default TL≠1 style if file has no `tl_mode`: `"msm"` or `"continuous"` (Cont = ÷N crawl + hold-high). Runtime: `T`+`D`+`*` |
| `JKS_MSM_EXPOSURE_MS` | MSM wait after pulse before hop (default 200) |
| `JKS_MSM_SETTLE_MS` | MSM wait after hop before next shoot (default 50) |
| `JKS_MSM_MIN_STEP_MM` | MSM minimum planned hop (default 0.1) |
| `JKS_AT_MARK_MM` | Distance (mm) to treat carriage as at PosA/B/C (default 0.5) |
| `JKS_LEFT_IS_NEGATIVE` | Left = decreasing position |
| `JKS_SPEED_MIN_MM_S` | SPEED pot floor (mm/s) |
| `JKS_SPEED_MAX_MM_S` | Panel ceiling: clamps `slider.max_speed = min(MC max_speed, this)` after CG |
| `JKS_ACCEL_MIN_MM_S2` / `JKS_ACCEL_MAX_MM_S2` | ACCEL pot floor; max clamps `slider.max_accel = min(MC max_accel, JKS_ACCEL_MAX_MM_S2)` |
| `JKS_SPEED_CURVE_GAMMA` | SPEED pot feel |
| `JKS_JOYSTICK_CURVE_GAMMA` / `JOYSTICK_DEADZONE` | Stick feel |
| `JKS_POT_*` / `JKS_ACCEL_*` / `JKS_JOY_*` | ADC denoise |
| `JKS_LONG_PRESS_MS` | Save mark / long actions (default 1000) |
| `JKS_STOP_HALT_MS` / `JKS_STOP_DISABLE_MS` | STOP hold thresholds |
| `JKS_BTN_DEBOUNCE_MS` | Debounce |
| `JKS_LOOP_DWELL_MS` | Pause at loop ends |
| `JKS_DELAY_CLEAR_MS` / `JKS_DELAY_MAX_S` | Delay arming |
| `JKS_OPTION_DELAY_SCALE` / `JKS_OPTION_DELAY_PRESET_S` | OPTION+DELAY |
| `JKS_OPTION_TL_MAX` / `JKS_OPTION_TL_FAVORITE` | OPTION+TIMELAPSE |
| `JKS_DISPLAY_DIM` | Dim scale for BTN_OPTION+FAST_L+FAST_R |
| `JKS_STORE_MARGIN_MM` | Keep marks inside soft limits |
| `JKS_POSITIONS_FILE` | Persist filename |
| `JKS_DSP_EXTRA_ROTATE_MS` | Extra-line rotate |
| `JKS_DSP_UNIT` | OLED Pos/Spd/Acc: `"mm"` (default) or `"inch"` (`in` / `in/s` / `in/s2`) or `"degree"` (`°` / `°/s` / `°/s2`). API stays mm |
| `JKS_BOOT_TEXT` / `JKS_BOOT_SPLASH_MS` | Boot splash |
| `JKS_BOOT_UNLOCK` | `True` (default): wait for OPTION or STOP before enable/homing; rainbow while locked |

## OLED / LED notes (installer)

- RGB LED wiring: see [Wiring schematics — RGB LED](JKSlider_Technical_Manual_Panel.md#wiring-schematics--rgb-led)
- Pico **onboard LED** blinks at 1 Hz as the hardware watchdog heartbeat (`WDT_*` / `PIN_LED_ONBOARD` in `UIC_config.py`)
- OLED: `DSP_ENABLED`, `DSP_DRIVER` (`ssd1306` / `sh1106` / `ssd1309`), `DSP_ROTATE_180` in `UIC_config.py`. Copy the matching driver file + `oledfont.py`. Marketplace **SSH1106** and **CH1115/CH1116** → use `"sh1106"`.
- OLED while moving: labels **Spd*** / **Acc*** with live verbose values (Acc approximate); idle shows **Spd** / **Acc** from commanded pots. `DSP_LIVE_POS` (`True` default) also refreshes Pos during motion; set `False` to freeze Pos and cut I2C load. Transfers are page-wise during motion.
- OLED mockups for docs: `python docs/oled/render_examples.py` → `docs/img/oled/*.png`
- LED colours and OLED layout for operators: **User Manual**
- Soft-limit approach distance: `SOFT_LIMIT_WARN_MM` in `UIC_config.py`

