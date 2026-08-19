# MKS SERVO42D/57D RS485 ↔ `MC_API`

**`MC_MKS_Client`** ([`MC_MKS_client.py`](../MC_MKS_client.py)) is a drop-in `MC_API` replacement for [`MC_Client`](../MC_client.py) when the axis is an MKS SERVO42D/57D in **RS485 bus mode** (no SliderMC).

Manual: [MKS SERVO42&57D_RS485 User Manual V1.0.9](https://github.com/makerbase-motor/MKS-SERVO42D-57D/blob/master/User%20Manual/V1.0.9/MKS%20SERVO42%2657D_RS485%20User%20Manual%20V1.0.9.pdf).

Component page / wiring: [JKSlider_Components_MKS_SERVOxx.md](../manuals/JKSlider_Components_MKS_SERVOxx.md).

**Verdict:** covers retarget, mid-move speed/accel (re-issue), soft/hard stop, soft-limit jog, optional hard limits & homing, live pos/speed. Not command-compatible with SliderMC ASCII. Soft limits and mm/s² accel live in the UIC client.

---

## Modes and wiring (defaults)

| Item | Requirement |
|------|-------------|
| Work mode | `SR_vFOC` (menu or `82H` = `05`) — `start()` sets this |
| Link | UART0 **GP16 TX / GP17 RX**, baud **38400** (`MC_MKS_config.UART_BAUD`) |
| MAX485 | **DE+RE** tied → **GP18** (`PIN_RS485_DE`); A/B to motor; shared GND |
| Slave addr | `MKS_ADDR` (default `1`) |
| Frame | Downlink `FA addr code … CRC8`; uplink `FB …` (sum & 0xFF) |
| Protocol | **Native FA/FB only** — Modbus-RTU (`Mb_RTU` / `8EH`) is out of scope |
| Dual hard limits | Prefer **57D**. **42D**: enable `LIMIT_REMAP` (`9EH`) so En/Dir act as L/R |

Do **not** run `MC_Client` and `MC_MKS_Client` on the same UART pins at once.

### MAX485 (ASCII)

```
  Pico (UIC)              MAX485                 MKS SERVO42D/57D
  GP16 TX ----------------> DI
  GP17 RX <----[1kOhm]----- RO
  GP18 -------------------> DE + RE (tied)
  GND  -------------------- GND ---------------- GND (signal)
       3V3/5V VCC as module requires
                            A ------------------ A
                            B ------------------ B
                           Motor supply 12–24 V separate (not from Pico)
```

---

## Unit conversion (UIC owns mm)

| Quantity | MKS unit | Client mapping |
|----------|----------|----------------|
| Position | Encoder axis (`31H`), `0x4000` = 1 rev | `MM_PER_ROT`, `AXIS_PER_ROT` |
| Speed | RPM `0…3000` | `rpm = mm_s * 60 / \|MM_PER_ROT\|` |
| Accel | Opaque `acc` `1…255` | Linear clamp via `ACCEL_MM_S2_FOR_ACC_MAX` → `MKS_ACC_*` |
| Soft limits | — | `SLIDER_MIN` / `SLIDER_MAX` in config / `setSoftLimits` |

Negative `MM_PER_ROT` inverts travel sense.

---

## Motion strategy (**F5 only**)

| Role | How |
|------|-----|
| Absolute / retarget | **`F5`** speed, acc, absAxis — re-issue for live speed/accel/target |
| Continuous jog | `move(+v)` → `moveTo(SLIDER_MAX)`; `move(-v)` → `moveTo(SLIDER_MIN)` |
| Soft stop | `F5` with **speed=0, acc≠0** |
| Hard / E-stop | **`F7`** then **`F3` disable** |
| Homing | Optional `HOME_USE`: `90H`/`94H` setup, **`91H`** origin, then `92H` + `HOME_SET_POS_MM` |
| Hard limits | Optional `HARD_LIMIT_USE` → `EndLimit` in `90H`; `LIMIT_REMAP` for 42D |
| Enable | **`F3H`** |
| Status | Poll **`F1`**, **`31`**, **`32`** (+ stall `3E`) at **`STATUS_HZ`** (default **5**) |

**No F6** speed mode.

---

## `MC_API` → MKS map

| Method | Behaviour |
|--------|-----------|
| `await start()` | UART+DE, `82H` SR_vFOC, optional remap/home params, status task |
| `enable(on)` | `F3H` |
| `setSpeed` / `setAcceleration` | Cache; mid-move re-issues `F5` |
| `setMaxSpeed` / `setSoftLimits` | Local clamp only |
| `moveTo` / `moveBy` | Soft-clamp → `F5` |
| `move(±v)` / `move(0)` / `stop()` | Soft-limit seek / soft stop |
| `halt()` | `F7` + disable |
| `home()` | If `HOME_USE` |
| `setPosition(mm)` | **`92H`** + UIC bias (supported; unlike `MC_Client`) |
| `estimateMoveTime` | Simple mm trapezoid/triangle (constant `a`) |
| `estimateMoveTimeTo` | Same from current position (extra vs classic `MC_Client`) |

Status callback: `cb(state, pos, speed, accel, target)` with letters `D/I/A/M/B/H/L/E` from `F1` + flags.

### Accel / time model (simple)

- UI keeps **mm/s²**.
- `acc = clamp(round(a * MKS_ACC_MAX / ACCEL_MM_S2_FOR_ACC_MAX), MKS_ACC_MIN…)`
- Time estimates are **display-grade** trapezoids — **not** &lt;1% MKS discrete-RPM fidelity.

### Drop-in usage

```python
from MC_MKS_client import MC_MKS_Client
from UIC_base import UIC_Base

mc = MC_MKS_Client()
ui = UIC_Base()
mc.set_status_callback(ui.on_status)
await mc.start()
await ui.start()
ui.set_soft_limits(mc.slider_min, mc.slider_max)
mc.setSpeed(40)
mc.enable(True)
mc.moveTo(100)
await mc.wait()
```

Config: [`MC_MKS_config.py`](../MC_MKS_config.py) + optional `SliderPins.MC_MKS_config` overlay.

---

## Out of scope / keep SliderMC when…

- You need sine-ramp telemetrized accel or SliderMC soft limits without UIC math  
- You already have STEP/DIR + `DRV_ERROR` (use SERVO42C path in [JKSlider_Components_Integrated_Drivers.md](../manuals/JKSlider_Components_Integrated_Drivers.md))  
- You need Modbus-RTU or F6 cruise mode
