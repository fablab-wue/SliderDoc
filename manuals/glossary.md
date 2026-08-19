# Glossary

Terms used in JKSlider manuals, config, and the MC_Client API.

## Acronyms

| Acronym | Expansion | Meaning |
|---------|-----------|---------|
| **ADC** | Analogue-to-digital converter | Reads a continuous voltage as a number. On JKSlider, ADC channels sample the SPEED, ACCEL, and optional JOYSTICK pots so the firmware can map knob position to mm/s and mm/s². |
| **API** | Application programming interface | The documented methods and config for writing your own code on top of `MC_Client` / `UIC_Base` (see [`docs/API.md`](../docs/API.md)). JKSlider is one application that uses this API. |
| **DIR** | Direction | Digital STEP/DIR line that selects motor travel sense (forward vs reverse). SliderMC `PIN_DRV_DIR` (GP19); polarity via `DRV_DIR_active` / `CS`. |
| **DIP** | Dual in-line package | Small switch banks on many stepper driver boards. Often used to set microstepping; those straps must match `MICROSTEPS` on SliderMC. |
| **DRV_ERROR** | Driver error / E-stop interlock | Hardware stop input (`PIN_DRV_ERROR`, SliderMC GP21). When active, motion halts immediately, the driver is disabled, and further moves are blocked until the input clears. Use for a closed-loop driver’s alarm/OC output and/or a panel emergency-stop button. Not the same as the panel **STOP** key. |
| **DSP** | Display | Optional 128×64 OLED over I2C (`PIN_DSP_I2C_SDA` / `PIN_DSP_I2C_SCL`). Enable with `DSP_ENABLED`; chip via `DSP_DRIVER`. |
| **EN** | Enable | Driver enable pin on SliderMC (`PIN_DRV_EN`, GP20). Most boards are active-low (`DRV_EN_active=0`): the motor is powered when the pin is low. |
| **ETA** | Estimated time of arrival | Predicted travel time from current SPEED and ACCEL (sine-ramp model). Shown on the OLED at a mark (times to the other Pos) or during goto (elapsed + remaining). Operators dial SPEED until the ETA matches a planned shot length. |
| **FPS** | Frames per second | Playback frame rate for MSM timelapse math (`period ≈ TL ÷ FPS`). Set by `JKS_CAMERA_FPS` or cycled with OPTION+STOP in **MSM** when TL ≠ 1. |
| **GPIO** | General-purpose input/output | Pico pins used as digital I/O or ADC (buttons, DRV_STEP/DIR, DRV_ERROR, LED, etc.). Numbered as GPn in the Technical Manual pinouts. |
| **I2C** | Inter-Integrated Circuit | Two-wire serial bus (SDA/SCL). Used for the optional 128×64 OLED when `DSP_ENABLED` is true (`DSP_I2C_*`). |
| **LED** | Light-emitting diode | Status lighting: discrete RGB on GP2–GP4 and/or an optional NeoPixel. Colours mirror motion, delay, TL, limits, and DRV_ERROR (see User Manual). |
| **MC** / **SliderMC** | Motion controller | Dedicated Pico (or compact RP2040 board, e.g. RP2040-Zero) running SliderMC (C++/PlatformIO): STEP/DIR planner, home/limits, `DRV_ERROR`, EXT. See [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md). |
| **MC_API** | Motion client contract | Duck-typed method surface on `MC_Client` (and a future RS485 client): `start`, motion/config, getters, `set_status_callback`. |
| **MC_Client** | Motion client class | UIC UART client to SliderMC (`MC_client.py`). |
| **MSM** | Stop–shoot–move | Stills timelapse: stand still → pulse `CTRL_CAMERA` → wait exposure → hop → settle → repeat. Default when `tl_mode`/`JKS_TL_MODE` is `"msm"` and TL ≠ 1. Toggle vs Cont with `T`+`D`+`*`. |
| **Cont** | Continuous crawl | TL≠1 ÷N crawl with `CTRL_CAMERA` hold-high like video (not pulses). OLED `Cont xN @Ffps`; video time = wall-time÷TL. Match the camera’s own TL to the slider TL. |
| **NP-F** | NP-F battery mount | Common camcorder / LED light battery form factor. Mentioned in compare and hardware notes for turnkey or field power packs—not required by the Pico firmware itself. |
| **OC** | Open-collector | Transistor output that pulls a line to ground when active and otherwise floats. Typical for driver alarm/error pins; wire to `DRV_ERROR` (often with pull-up) so a stall or fault triggers the same interlock as e-stop. |
| **OLED** | Organic light-emitting diode | Optional 128×64 panel display: yellow badges (D / TL / marks), blue Pos/Spd/Acc (idle) or Spd*/Acc* (moving), and status / ETA / MSM·Cont lines. Chip selected with `DSP_DRIVER` in `UIC_config.py`. |
| **SH1106** | Sinowealth OLED controller | Common on **1.3″** 128×64 I2C modules (132-column RAM). Marketplace listings sometimes say **SSH1106**. **CH1115 / CH1116** are clones — use `DSP_DRIVER = "sh1106"`. |
| **SSD1306** | Solomon Systech OLED controller | Most common on **0.96″** 128×64 I2C modules. Default `DSP_DRIVER`. |
| **SSD1309** | Solomon Systech OLED controller | Often used on larger **1.54″ / 2.42″** 128×64 I2C (or SPI) modules. `DSP_DRIVER = "ssd1309"`. |
| **PIO** | Programmable I/O | RP2040 hardware state machines that generate precise STEP pulses (and optional NeoPixel timing) without loading the CPU the way bit-banged loops would. |
| **PSU** | Power supply unit | The motor (and system) power source. Motor VM must share ground with the Pico; size current for the driver and mechanics (see Hardware Manual). |
| **PWM** | Pulse-width modulation | Rapid on/off driving of the RGB LED channels to set brightness and colour mix. |
| **RGB** | Red–green–blue | Three-colour status LED (or the equivalent NeoPixel colours) used for idle, motion, delay, TL, limits, and DRV_ERROR. |
| **SPI** | Serial Peripheral Interface | Multi-wire bus used to configure some TMC drivers (current, microsteps). JKSlider motion still uses STEP/DIR after the driver is set up. |
| **SliderPins** | HW profile overlay | One gitignored file per slider build (`SliderPins.py` from the example). Overrides any key in `MC_config` / `UIC_config` / `JKSliderConfig`. Edit **that file only**. |
| **STEP** / **DRV_STEP** | Step pulse | One pulse advances the motor by one microstep. SliderMC `PIN_DRV_STEP` (GP18); rate and ramps come from the SliderMC planner. |
| **SW_HOME** | Home switch | SliderMC homing reference input (`PIN_SW_HOME`, GP22); enabled by `SW_HOME_use`. |
| **TL** | Timelapse | Panel **TIMELAPSE** divider and yellow **TL** badge. ×1 is video (hold-high while moving / soft-paused); ≠1 selects MSM or Cont (`tl_mode`), toggled with `T`+`D`+`*`. |
| **TMC** | Trinamic Motor Control | Family of silent / feature-rich stepper drivers (e.g. TMC2208/09, TMC5160) commonly wired as STEP/DIR (+ EN) to the Pico. |
| **USB** | Universal Serial Bus | Used to flash MicroPython, run Thonny/`mpremote`, and optionally power the Pico during bring-up. Prefer a data-capable cable. |
| **UIC** | UI controller | Panel Pico (or compact RP2040 board, e.g. RP2040-Zero) running MicroPython (`JKSlider` / `MC_Client` / `UIC_Base`): pots, buttons/keypad, OLED, RGB, camera, UART host to SliderMC. Preferred stack for this project; forks may use other hosts. See [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md). |
| **UIC_Base** | UIC peripherals class | OLED / RGB / camera / WDT on the UIC (`UIC_base.py`); refreshed via `MC_Client` status callback. |
| **WDT** | Watchdog timer | Hardware timer that resets the Pico if firmware stops feeding it. Fed from the I/O monitor; the onboard LED blinks at 1 Hz as a heartbeat when enabled. |

Electronics and pinouts use the `BTN_*` prefix (e.g. `BTN_STOP`); the User Manual uses the short names below.

## Panel controls

| Name | Config / pin hint | Meaning |
|------|-------------------|---------|
| **SPEED** / **POT_SPEED** | Pot (`PIN_POT_SPEED`) | Sets cruise / goto / loop / joystick full-scale speed (mm/s). Left = near zero. |
| **ACCEL** / **POT_ACCEL** | Pot (`PIN_POT_ACCEL`) | How quickly the axis ramps up and down (mm/s²). Also affects OLED ETAs. |
| **JOYSTICK** / **POT_JOYSTICK** | Optional pot (`PIN_POT_JOYSTICK`) | Analogue velocity: centre = stop, full deflection ≈ SPEED (or max with OPTION). Recalibrate centre with OPTION+A+B+C when idle. |
| **STOP** | `BTN_STOP` | Soft stop (tap), fast halt while already decelerating or hold ≥1 s, disable driver ≥2 s, re-enable when disabled. Chords: STOP+A/B/C = soft min / mid / max; OPTION+STOP+A = home; OPTION+STOP = peek marks or cycle FPS in TL; keypad both ` * ` + ` 0 ` = emergency halt. |
| **MOVE_L** / **MOVE_R** | `BTN_MOVE_L` / `BTN_MOVE_R` | Cruise left/right at SPEED. Tap ≤`JKS_MOVE_TAP_MS` locks cruise; longer hold = hold-to-run. Same MOVE tip while locked stops. Opposite MOVE reverses. With OPTION: max speed + max accel boost while held. |
| **FAST_L** / **FAST_R** | `BTN_FAST_L` / `BTN_FAST_R` | Hold for max speed/accel jog (no lock). Matching side with MOVE boosts cruise. Both FAST ≥1 s (or OPTION+MOVE both): swap L/R. OPTION+both FAST: dim LED/OLED. |
| **A** / **B** / **C** | `BTN_A` / `BTN_B` / `BTN_C` | Tap = goto Pos; hold ≥1 s = store. Pairs start/stop loops (first leg = 2nd letter). OPTION+pair = same loop. OPTION+tap = goto at max speed/accel. |
| **OPTION** | `BTN_OPTION` | Modifier only (alone does nothing). Combines with MOVE, FAST, A/B/C, DELAY, TIMELAPSE, STOP for boosts, presets, FPS cycle, swap, dim, joy calibrate, etc. Keypad: two ` * ` keys OR as OPTION; both down → `DOUBLE_OPTION` (with STOP = halt). Discrete GP13 ORed with matrix `*` in keypad mode. |
| **DELAY** | `BTN_DELAY` | Two roles, one key: **DELAY arming** (idle — hold to arm walk-in delay, short tap clears; OPTION+DELAY preset or ×5 scale) and **mid-move pause** (hold = soft-stop, release = resume). |
| **TIMELAPSE** | `BTN_TIMELAPSE` | Tap cycles TL divider (1, 5, 10, …); hold returns to ×1. OPTION+tap = +1; OPTION+hold = favourite (often ×25). With DELAY+OPTION toggles MSM ↔ Cont. |
