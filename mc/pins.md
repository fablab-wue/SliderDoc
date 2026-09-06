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

Extra-axis rows (`DRV_*2` / `SW_*2`, `DRV_*3` / `SW_*3`) appear in `IX` / `VG` **only when** that axis is live (`CS axis 2` or `3`). `PIN_CAMERA_CTRL` is always listed (reserved, inited inactive — **no protocol command**).

---

## Raspberry Pi Pico (`BOARD_PICO`, env `pico`) / Pico 2 (`pico2`)

![SliderMC Pico pinout](../assets/img/pico_pinout_mc.png)

Regenerate: `python tools/render_pico_pinout_SliderMC.py` → [`pico_pinout_mc.txt`](../assets/pico_pinout_mc.txt) + PNG. Pico 2 reuses this header map.

| Symbol | GPIO | Role |
|--------|------|------|
| `PIN_SW_LIMIT_R3` | 0 | Axis-3 hard limit right (`axis≥3`) |
| `PIN_SW_LIMIT_L3` | 1 | Axis-3 hard limit left |
| `PIN_DRV_ERROR3` | 2 | Axis-3 fault / E-stop |
| `PIN_DRV_EN3` | 3 | Axis-3 enable |
| `PIN_DRV_DIR3` | 4 | Axis-3 DIR |
| `PIN_DRV_STEP3` | 5 | Axis-3 STEP (polarity follows axis 2) |
| `PIN_SW_LIMIT_R2` | 6 | Axis-2 hard limit right (`axis≥2`) |
| `PIN_SW_LIMIT_L2` | 7 | Axis-2 hard limit left |
| `PIN_EXT_0` | 8 | General-purpose output (`EO0`; inactive at boot) |
| `PIN_EXT_1` | 9 | Extender `EO1` |
| `PIN_DRV_ERROR2` | 10 | Axis-2 fault / E-stop |
| `PIN_DRV_EN2` | 11 | Axis-2 enable |
| `PIN_DRV_DIR2` | 12 | Axis-2 DIR |
| `PIN_DRV_STEP2` | 13 | Axis-2 STEP |
| `PIN_EXT_2` | 14 | Extender `EO2` |
| `PIN_EXT_3` | 15 | Extender `EO3` |
| `PIN_UART_TX` | 16 | UART TX to UI controller |
| `PIN_UART_RX` | 17 | UART RX from UI controller |
| `PIN_DRV_STEP` | 18 | STEP to driver (axis 1) |
| `PIN_DRV_DIR` | 19 | DIR (axis 1) |
| `PIN_DRV_EN` | 20 | Enable (axis 1) |
| `PIN_DRV_ERROR` | 21 | Driver fault / E-stop (always polled) |
| `PIN_CAMERA_CTRL` | 22 | Reserved camera control (inited inactive; no protocol command) |
| `PIN_LED` | `LED_BUILTIN` (GP25) | Status / heartbeat LED (onboard) |
| `PIN_SW_LIMIT_L` | 26 | Hard limit left (if `SW_LIMIT_L_1_use=1`) |
| `PIN_SW_LIMIT_R` | 27 | Hard limit right (if `SW_LIMIT_R_1_use=1`) |
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
| `PIN_DRV_STEP` | 0 | STEP (axis 1) |
| `PIN_DRV_DIR` | 1 | DIR (axis 1) |
| `PIN_DRV_EN` | 2 | Enable (axis 1) |
| `PIN_DRV_ERROR` | 3 | Driver fault / E-stop |
| `PIN_SW_LIMIT_L` | 4 | Hard limit left (axis 1) |
| `PIN_SW_LIMIT_R` | 5 | Hard limit right (axis 1) |
| `PIN_DRV_STEP2` | 6 | STEP axis2 |
| `PIN_DRV_DIR2` | 7 | DIR axis2 |
| `PIN_DRV_ERROR2` | 8 | Fault / E-stop axis2 |
| `PIN_SW_LIMIT_L2` | 9 | Hard limit left axis2 |
| `PIN_SW_LIMIT_R2` | 10 | Hard limit right axis2 |
| `PIN_DRV_EN2` | 11 | Enable axis2 |
| `PIN_UART_TX` | 12 | UART TX to UIC |
| `PIN_UART_RX` | 13 | UART RX from UIC |
| `PIN_DRV_ERROR3` | 14 | Fault / E-stop axis3 |
| `PIN_DRV_EN3` | 15 | Enable axis3 |
| *(unused)* | 16 | Onboard WS2812 data — unused by firmware |
| `PIN_SW_LIMIT_R3` | 17 | Hard limit right axis3 |
| `PIN_SW_LIMIT_L3` | 18 | Hard limit left axis3 |
| `PIN_EXT_3` | 21 | Extender output 3 (`EO3`) |
| `PIN_EXT_2` | 22 | Extender output 2 (`EO2`) |
| `PIN_EXT_1` | 23 | Extender output 1 (`EO1`) |
| `PIN_EXT_0` | 24 | Extender output 0 (`EO0`) |
| `PIN_CAMERA_CTRL` | 25 | Reserved camera control (inited inactive; no protocol command) |
| `PIN_DRV_DIR3` | 26 | DIR axis3 |
| `PIN_DRV_STEP3` | 27 | STEP axis3 (polarity follows axis 2) |
| `PIN_BUZZER` | 28 | Optional piezo (`BE`; `BUZZER_use`) |
| `PIN_LED` | 29 | External status / heartbeat LED |

`axis` 1\|2\|3 is supported on Zero / Mini.

---

## Shared notes

GPIO numbers are fixed in `pins.h` (not changeable via protocol).  
Active levels for all pins except UART are config keys (`DRV_STEP_1_active`, `SW_LIMIT_L_1_active`, …): `0` = low-active, `1` = high-active. Digit is **before** the suffix (`SW_LIMIT_R_3_use`).  
Hard-limit **usage** is gated by `SW_LIMIT_L_N_use` / `SW_LIMIT_R_N_use` (default off). Homing modes 1/2 use those same limit pins.  
Optional **buzzer** is gated by `BUZZER_use` (default off); `BE` pulses `PIN_BUZZER` (GP28) ~0.1 s. On Pico W / Pico 2 W GP28 is `PIN_LED`, so the buzzer is not claimed.  
`PIN_DRV_ERROR` is always polled (`DRV_ERROR_1_active`); assert → emergency halt + command gate, except during stall-home (`home_mode_N` 3/4). See [CONFIG.md](CONFIG.md) / [MOTION.md](MOTION.md).  
`PIN_CAMERA_CTRL` is reserved and driven inactive at boot — no `CS` / motion command this pass.

`PIN_EXT_0`…`3` are always outputs. Polarity via `EXT_n_active`; boot level is **inactive**. Logical on/off: `EO0`…`EO3`. **`EO4`… is rejected.**

STEP polarity (`DRV_STEP_1_active` / `DRV_STEP_2_active`) selects one of two PIO programs. Axis 3 STEP follows axis 2 (no `DRV_STEP_3_active`). See [MOTION.md](MOTION.md).

Oscilloscope `DEBUG_HW` pins are **off by default** (commented out in `pins.h`) and are not shown on the pinout images. Define `DEBUG_HW` at compile time if you need them; they then appear in `IX`/`VG` only.
