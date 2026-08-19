# MKS SERVO42D / 57D (RS485 bus mode)

[← Components index](JKSlider_Components.md)

Drive the axis **directly from the UIC** over RS485 with [`MC_MKS_Client`](../MC_MKS_client.py) — **no SliderMC**, no STEP/DIR. Protocol map: [MKS_SERVO_RS485.md](../docs/MKS_SERVO_RS485.md).

For STEP/DIR closed-loop (SERVO42C + SliderMC), see [JKSlider_Components_Integrated_Drivers.md](JKSlider_Components_Integrated_Drivers.md) instead.

| Field | Content |
|-------|---------|
| **Name** | MKS SERVO42D / SERVO57D — integrated closed-loop stepper, **RS485** |
| **Status** | `Documented` — client shipped; end-to-end bench checklist in [TODO.md](../TODO.md) |
| **Manufacturer** | [Makerbase MKS-SERVO42D-57D](https://github.com/makerbase-motor/MKS-SERVO42D-57D) |
| **Manual** | [RS485 User Manual V1.0.9](https://github.com/makerbase-motor/MKS-SERVO42D-57D/blob/master/User%20Manual/V1.0.9/MKS%20SERVO42%2657D_RS485%20User%20Manual%20V1.0.9.pdf) |

---

## When to use

| Use this path | Prefer SliderMC STEP/DIR |
|---------------|--------------------------|
| One axis, motor already has RS485 + FOC | Existing SliderMC + SERVO42C / external driver |
| UIC owns soft limits + mm math | Need MC planner / PIO STEP fidelity |
| Soft-limit jog via F5 only | Need F6 continuous RPM cruise on the wire |

---

## Wiring (MAX485)

Defaults (`MC_MKS_config` / `SliderPins.MC_MKS_config`): UART0 **GP16 TX / GP17 RX**, **DE+RE on GP18**, baud **38400**, addr **1**.

```
  Pico (UIC)              MAX485 module            MKS SERVO42D/57D
  GP16 TX ---------------> DI
  GP17 RX <--------------- RO
  GP18 -------------------> DE and RE (tie together)
  GND ------------------- GND ------------------- GND (signal ground)
  3V3 or 5V --------------> VCC (per module)

                                                 RS485 A <--> A
                                                 RS485 B <--> B

  Motor V+ / Gnd  <--- separate 12–24 V supply (not from Pico)
```

- Share **signal GND** Pico ↔ MAX485 ↔ motor logic ground.  
- Motor power is **independent**.  
- Prefer **57D** if you need two hard endstops without remapping.  
- **42D** has one dedicated limit input; set `LIMIT_REMAP=1` so En/Dir become L/R (see manual `9EH`; Com must be tied high per MKS).

---

## Motor menu (minimum)

| Setting | Value |
|---------|--------|
| Work mode | **`SR_vFOC`** (client also sends `82H` = `05` on `start()`) |
| `UartBaud` | Match `UART_BAUD` (default **38400**) |
| `UartAddr` | Match `MKS_ADDR` (default **1**) |
| Protocol | Native serial (**not** Modbus-RTU / `Mb_RTU`) |

Optional: `EndLimit`, home direction/speed/trigger — or leave to client when `HOME_USE` / `HARD_LIMIT_USE` are set.

---

## UIC software

```python
from MC_MKS_client import MC_MKS_Client
from UIC_base import UIC_Base

mc = MC_MKS_Client()
ui = UIC_Base()
mc.set_status_callback(ui.on_status)
await mc.start()
```

| File | Role |
|------|------|
| [`MC_MKS_client.py`](../MC_MKS_client.py) | `MC_MKS_Client` — F5 motion, DE, ~5 Hz status |
| [`MC_MKS_config.py`](../MC_MKS_config.py) | Pins, `MM_PER_ROT`, soft limits, home/limits, accel map |
| [`SliderPins.example.py`](../SliderPins.example.py) | `MC_MKS_config = { … }` overlay template |

Mechanics: set **`MM_PER_ROT`** (mm per motor revolution). Soft travel: **`SLIDER_MIN` / `SLIDER_MAX`**. Continuous LEFT/RIGHT in the panel maps to `moveTo` those bounds.

**Do not** load both `MC_Client` and `MC_MKS_Client` against the same UART.

---

## Homing and hard limits

| Config | Effect |
|--------|--------|
| `HOME_USE=1` | `home()` runs origin home (`91H`); then UIC zero via `92H` + `HOME_SET_POS_MM` |
| `HOME_DIR` / `HOME_SPEED_MM_S` / `HOME_TRIG_LEVEL` | Written via `90H` |
| `HARD_LIMIT_USE=1` | Enables `EndLimit` in `90H` |
| `LIMIT_REMAP=1` | `9EH` for 42D dual-limit wiring |

Wire endstops to the motor’s limit inputs (or remapped En/Dir), not to SliderMC GPIOs.
