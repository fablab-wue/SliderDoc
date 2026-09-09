<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Pin map";
  --doc-path: ".\\SliderDoc\\mc\\pins.md";
}
</style>

# Pin map

Pins are fixed in `include/pins.h` at compile time and cannot be changed by protocol commands.
Select a board with PlatformIO envs `pico` (default), `picow`, `rp2040zero`, `pico2`, `pico2w`, or `rp2350mini` (see [BUILD.md](BUILD.md)). Pico 2 uses the Pico header map at **150 MHz**; Pico 2 W uses the Pico W map (LED GP28); RP2350 Mini uses the Zero map. STEP PIO SM stays **50 MHz** on all boards (sysclk 133 MHz on RP2040, 150 MHz on RP2350).

Live dumps on the device:

- `VG` / `VersionGPIO` — machine-readable `PIN_*=GPIO` lines
- `IX` / `Pinout` — ASCII table of GP number, name, and brief description (≤80 columns)

Extra-axis rows (`DRV_*2` / `SW_*2`, `DRV_*3` / `SW_*3`) appear in `IX` / `VG` **only when** that motor is live (`CS motors 2` or `3`). Servo rows appear when `servos>=1`. `PIN_CAMERA_CTRL` is always listed (reserved, inited inactive — **no protocol command**).

---

## Raspberry Pi Pico (`BOARD_PICO`, env `pico`) / Pico 2 (`pico2`)

![SliderMC Pico pinout](../assets/img/pico_pinout_mc.png)

Regenerate: `python tools/render_pico_pinout_SliderMC.py` → [`pico_pinout_mc.txt`](../assets/pico_pinout_mc.txt) + PNG. Pico 2 reuses this header map.

| Symbol | GPIO | Role |
|--------|------|------|
| `PIN_DRV_STEP_1` | 0 | Motor 1 STEP |
| `PIN_DRV_DIR_1` | 1 | Motor 1 DIR |
| `PIN_SW_LIMIT_L_1` | 2 | Motor 1 hard limit left (`SW_LIMIT_L_1_use=1`) |
| `PIN_SW_LIMIT_R_1` | 3 | Motor 1 hard limit right |
| `PIN_DRV_STEP_2` | 4 | Motor 2 STEP (`motors>=2`) |
| `PIN_DRV_DIR_2` | 5 | Motor 2 DIR |
| `PIN_SW_LIMIT_L_2` | 6 | Motor 2 hard limit left |
| `PIN_SW_LIMIT_R_2` | 7 | Motor 2 hard limit right |
| `PIN_DRV_STEP_3` | 8 | Motor 3 STEP (`motors>=3`; polarity follows motor 2) |
| `PIN_DRV_DIR_3` | 9 | Motor 3 DIR |
| `PIN_SW_LIMIT_L_3` | 10 | Motor 3 hard limit left |
| `PIN_SW_LIMIT_R_3` | 11 | Motor 3 hard limit right |
| `PIN_DRV_ERROR_1` | 12 | Motor 1 fault / E-stop (always polled) |
| `PIN_DRV_ERROR_2` | 13 | Motor 2 fault / E-stop |
| `PIN_DRV_ERROR_3` | 14 | Motor 3 fault / E-stop |
| `PIN_DRV_ENABLE` | 15 | Shared driver enable |
| `PIN_UART_TX` | 16 | UART TX to UI controller |
| `PIN_UART_RX` | 17 | UART RX from UI controller |
| `PIN_EXT_4` / `PIN_SERVO_3` | 18 | Extender `EO4`; **SERVO_3 when `servos>=3`** (steals EXT_4) |
| `PIN_EXT_3` | 19 | Extender `EO3` |
| `PIN_EXT_2` | 20 | Extender `EO2` |
| `PIN_EXT_1` | 21 | Extender `EO1` |
| `PIN_CAMERA_CTRL` | 22 | Reserved camera control (inited inactive; no protocol command) |
| `PIN_LED` | `LED_BUILTIN` (GP25) | Status / heartbeat LED (onboard) |
| `PIN_SERVO_1` | 26 | RC servo 1 PWM (100 Hz, wrap 65535; ~1.25′ / 0.021° per count over ±135° at 500–2500 µs) |
| `PIN_SERVO_2` | 27 | RC servo 2 PWM |
| `PIN_BUZZER` | 28 | Optional piezo (`BE` / Beep); gated by `BUZZER_use` (default off) |

UART baud rate: **115 200**. GP16/GP17 are **UART0** (`Serial1` via `PIN_UART_SERIAL`).

---

## Raspberry Pi Pico W (`BOARD_PICO_W`, env `picow`) / Pico 2 W (`pico2w`)

Same header pin map as classic Pico, except the status LED:

| Symbol | GPIO | Role |
|--------|------|------|
| *(all other pins)* | *(same as Pico)* | Same as table above |
| `PIN_LED` | **28** | External status / heartbeat LED |

The Pico W / Pico 2 W onboard LED is on the CYW43 WiFi chip — do not drive `LED_BUILTIN` under FreeRTOS. Use env `picow` or `pico2w` and wire an external LED to **GP28**. That aliases `PIN_BUZZER`; firmware will **not** pulse the buzzer (heartbeat LED wins). Use a different compile-time GPIO if a piezo is needed.

---

## Waveshare RP2040-Zero (`BOARD_RP2040_ZERO`, env `rp2040zero`) / RP2350 Mini (`rp2350mini`)

![SliderMC RP2040-Zero pinout](../assets/img/rp2040zero_pinout_mc.png)

Regenerate: `python tools/render_rp2040zero_pinout_SliderMC.py` → [`rp2040zero_pinout_mc.txt`](../assets/rp2040zero_pinout_mc.txt) + PNG. RP2350 Mini reuses this map.

| Symbol | GPIO | Role |
|--------|------|------|
| `PIN_DRV_ENABLE` | 0 | Shared driver enable |
| `PIN_DRV_STEP_1` | 1 | Motor 1 STEP |
| `PIN_DRV_DIR_1` | 2 | Motor 1 DIR |
| `PIN_SW_LIMIT_L_1` | 3 | Motor 1 hard limit left |
| `PIN_SW_LIMIT_R_1` | 4 | Motor 1 hard limit right |
| `PIN_DRV_STEP_2` | 5 | Motor 2 STEP |
| `PIN_DRV_DIR_2` | 6 | Motor 2 DIR |
| `PIN_SW_LIMIT_L_2` | 7 | Motor 2 hard limit left |
| `PIN_SW_LIMIT_R_2` | 8 | Motor 2 hard limit right |
| `PIN_DRV_ERROR_1` | 9 | Motor 1 fault / E-stop |
| `PIN_DRV_ERROR_2` | 10 | Motor 2 fault / E-stop |
| `PIN_DRV_ERROR_3` | 11 | Motor 3 fault / E-stop |
| `PIN_UART_TX` | 12 | UART TX to UIC |
| `PIN_UART_RX` | 13 | UART RX from UIC |
| `PIN_SW_LIMIT_R_3` | 14 | Motor 3 hard limit right |
| `PIN_SW_LIMIT_L_3` | 15 | Motor 3 hard limit left |
| *(unused)* | 16 | Onboard WS2812 data — unused by firmware |
| `PIN_EXT_1` | 17 | Extender `EO1` |
| `PIN_EXT_2` | 18 | Extender `EO2` |
| `PIN_EXT_3` | 19 | Extender `EO3` |
| `PIN_EXT_4` | 20 | Extender `EO4` |
| `PIN_SERVO_1` | 21 | RC servo 1 PWM (100 Hz, wrap 65535; ~1.25′ / 0.021° per count over ±135° at 500–2500 µs) |
| `PIN_SERVO_2` | 22 | RC servo 2 PWM |
| `PIN_SERVO_3` | 23 | RC servo 3 PWM |
| `PIN_CAMERA_CTRL` | 25 | Reserved camera control (inited inactive; no protocol command) |
| `PIN_DRV_DIR_3` | 26 | Motor 3 DIR |
| `PIN_DRV_STEP_3` | 27 | Motor 3 STEP (polarity follows motor 2) |
| `PIN_BUZZER` | 28 | Optional piezo (`BE`; `BUZZER_use`) |
| `PIN_LED` | 29 | External status / heartbeat LED |

`motors` 1\|2\|3 and `servos` 0..3 are supported on Zero / Mini.

---

## Shared notes

GPIO numbers are fixed in `pins.h` (not changeable via protocol).  
Pad drive: STEP / DIR / EXT / SERVO **8 mA**; `PIN_DRV_ENABLE` and `PIN_CAMERA_CTRL` **12 mA**.  
Active levels for all pins except UART are config keys (`DRV_STEP_1_active`, `SW_LIMIT_L_1_active`, …): `0` = low-active, `1` = high-active. Digit is **before** the suffix (`SW_LIMIT_R_3_use`).  
Hard-limit **usage** is gated by `SW_LIMIT_L_N_use` / `SW_LIMIT_R_N_use` (default off). Homing modes 1/2 use those same limit pins.  
Optional **buzzer** is gated by `BUZZER_use` (default off); `BE` pulses `PIN_BUZZER` (GP28) ~0.1 s. On Pico W / Pico 2 W GP28 is `PIN_LED`, so the buzzer is not claimed.  
`PIN_DRV_ERROR` is always polled (`DRV_ERROR_1_active`); assert → emergency halt + command gate, except during stall-home (`home_mode_N` 3/4). See [CONFIG.md](CONFIG.md) / [MOTION.md](MOTION.md).  
`PIN_CAMERA_CTRL` is reserved and driven inactive at boot — no `CS` / motion command this pass.

`PIN_EXT_1`…`4` are always outputs (logical `EO1`…`EO4` / protocol `EO0`…`EO3`). Polarity via `EXT_n_active`; boot level is **inactive**. On Pico, **GP18 is SERVO_3 when `servos>=3`** (EXT_4 stolen). **`EO4`… is rejected.**

STEP polarity (`DRV_STEP_1_active` / `DRV_STEP_2_active`) selects one of two PIO programs. Motor 3 STEP follows motor 2 (no `DRV_STEP_3_active`). See [MOTION.md](MOTION.md).

RC servos use hardware PWM at **100 Hz**, wrap **65535**. Envelope ±135° maps linearly onto `SERVO_N_min_pulse`…`max_pulse` (default **500–2500 µs**; analog often 1000–2000). Default span resolution ≈ **1.25 arc minutes (′)** / 0.021° per count. `SERVO_N_swap` reverses sense; `SERVO_N_active` inverts the pulse. `SE 0` stops PWM (limp).

Oscilloscope `DEBUG_HW` pins are **off by default** (commented out in `pins.h`) and are not shown on the pinout images. Define `DEBUG_HW` at compile time if you need them; they then appear in `IX`/`VG` only.
