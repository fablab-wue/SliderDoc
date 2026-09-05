<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Pin map";
  --doc-path: ".\\SliderDoc\\mc\\pins.md";
}
</style>

# Pin map

Pins are fixed in `include/pins.h` at compile time and cannot be changed by protocol commands.
Select a board with PlatformIO envs `pico` (default), `picow`, or `rp2040zero` (see [BUILD.md](BUILD.md)).

Live dumps on the device:

- `VG` / `VersionGPIO` — machine-readable `PIN_*=GPIO` lines
- `IX` / `Pinout` — ASCII table of GP number, name, and brief description (≤80 columns)

Axis-2 rows (`DRV_*2` / `SW_*2`) appear in `IX` / `VG` **only when** `axis2_use=1` (and the board supports it).

---

## Raspberry Pi Pico (`BOARD_PICO`, env `pico`)

![SliderMC Pico pinout](../assets/img/pico_pinout_mc.png)

Regenerate: `python tools/render_pico_pinout_SliderMC.py` → [`pico_pinout_mc.txt`](../assets/pico_pinout_mc.txt) + PNG.

| Symbol | GPIO | Role |
|--------|------|------|
| *(free)* | 0, 1 | Unused |
| `PIN_EXT_0` … `PIN_EXT_3` | 2…5 | General-purpose outputs (`X0`…`X3`; inactive at boot) |
| `PIN_SW_LIMIT_R2` | 6 | Axis-2 hard limit right (`axis2_use=1`) |
| `PIN_SW_LIMIT_L2` | 7 | Axis-2 hard limit left |
| *(free)* | 8, 9 | Unused |
| `PIN_DRV_ERROR2` | 10 | Axis-2 fault / E-stop |
| `PIN_DRV_EN2` | 11 | Axis-2 enable |
| `PIN_DRV_DIR2` | 12 | Axis-2 DIR |
| `PIN_DRV_STEP2` | 13 | Axis-2 STEP |
| *(free)* | 14, 15 | Unused |
| `PIN_UART_TX` | 16 | UART TX to UI controller |
| `PIN_UART_RX` | 17 | UART RX from UI controller |
| `PIN_DRV_STEP` | 18 | STEP to driver (axis 1) |
| `PIN_DRV_DIR` | 19 | DIR (axis 1) |
| `PIN_DRV_EN` | 20 | Enable (axis 1) |
| `PIN_DRV_ERROR` | 21 | Driver fault / E-stop (always polled) |
| *(free)* | 22 | Unused |
| `PIN_LED` | `LED_BUILTIN` (GP25) | Status / heartbeat LED (onboard) |
| `PIN_SW_LIMIT_L` | 26 | Hard limit left (if `SW_LIMIT_L_use=1`) |
| `PIN_SW_LIMIT_R` | 27 | Hard limit right (if `SW_LIMIT_R_use=1`) |
| `PIN_BUZZER` | 28 | Optional piezo (`Z` / `Buzzer`); gated by `BUZZER_use` (default off) |

UART baud rate: **115 200**. GP16/GP17 are **UART0** (`Serial1` via `PIN_UART_SERIAL`).

---

## Raspberry Pi Pico W (`BOARD_PICO_W`, env `picow`)

Same header pin map as classic Pico, except the status LED:

| Symbol | GPIO | Role |
|--------|------|------|
| *(all other pins)* | *(same as Pico)* | Same as table above |
| `PIN_LED` | **28** | External status / heartbeat LED |

The Pico W onboard LED is on the CYW43 WiFi chip — do not drive `LED_BUILTIN` under FreeRTOS. Use env `picow` and wire an external LED to **GP28**. That aliases `PIN_BUZZER`; firmware will **not** pulse the buzzer on Pico W (heartbeat LED wins). Use a different compile-time GPIO if a piezo is needed.

---

## Waveshare RP2040-Zero (`BOARD_RP2040_ZERO`, env `rp2040zero`)

![SliderMC RP2040-Zero pinout](../assets/img/rp2040zero_pinout_mc.png)

Regenerate: `python tools/render_rp2040zero_pinout_SliderMC.py` → [`rp2040zero_pinout_mc.txt`](../assets/rp2040zero_pinout_mc.txt) + PNG.

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
| `PIN_EXT_3` | 14 | Extender output 3 (`X3`) |
| `PIN_EXT_2` | 15 | Extender output 2 (`X2`) |
| *(unused)* | 16 | Onboard WS2812 data — unused by firmware |
| *(free)* | 17…25 | Unused |
| `PIN_EXT_1` | 26 | Extender output 1 (`X1`) |
| `PIN_EXT_0` | 27 | Extender output 0 (`X0`) |
| `PIN_BUZZER` | 28 | Optional piezo (`Z`; `BUZZER_use`) |
| `PIN_LED` | 29 | External status / heartbeat LED |

**`axis2_use` is supported on Zero.**

---

## Shared notes

GPIO numbers are fixed in `pins.h` (not changeable via protocol).  
Active levels for all pins except UART are config keys (`DRV_STEP_active`, `SW_LIMIT_L_active`, …): `0` = low-active, `1` = high-active.  
Hard-limit **usage** is gated by `SW_LIMIT_L_use` / `SW_LIMIT_R_use` (default off). Homing modes 1/2 use those same limit pins.  
Optional **buzzer** is gated by `BUZZER_use` (default off); `Z` pulses `PIN_BUZZER` (GP28) ~0.1 s. On Pico W GP28 is `PIN_LED`, so the buzzer is not claimed.  
`PIN_DRV_ERROR` is always polled (`DRV_ERROR_active`); assert → emergency halt + command gate, except during stall-home (`home_mode` 3/4). See [CONFIG.md](CONFIG.md) / [MOTION.md](MOTION.md).

`PIN_EXT_0`…`3` are always outputs. Polarity via `EXT_n_active`; boot level is **inactive**. Logical on/off: `X0`…`X3` / `Ext0`…`Ext3`. **`X4`…`X9` are rejected.**

STEP polarity (`DRV_STEP_active`) selects one of two PIO programs. See [MOTION.md](MOTION.md).

Oscilloscope `DEBUG_HW` pins are **off by default** (commented out in `pins.h`) and are not shown on the pinout images. Define `DEBUG_HW` at compile time if you need them; they then appear in `IX`/`VG` only.
