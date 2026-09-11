<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Switches for Homing";
  --doc-path: ".\\SliderDoc\\components\\homing-switches.md";
}
</style>

# Switches for Homing

[← Components index](index.md)

There is **no dedicated home-switch pin**. Homing uses a hard limit (`home_mode_N` 1/2) or driver stall on `DRV_ERROR` (`home_mode_N` 3/4). With no switch, set `home_mode_1=0` (or `_2` / `_3`) and declare origin with `SP`.

SliderMC pinout: [PINS.md](../mc/pins.md) · [MC_Pico_pinout.png](../assets/img/MC_Pico_pinout.png) · [CONFIG.md](../mc/config.md) · [MOTION.md](../mc/motion.md)

| `home_mode_N` | Reference | Finish pose | Needs |
|-------------|-----------|-------------|-------|
| `0` | none | — (`MH` no-op; use `SP`) | — |
| `1` | `SW_LIMIT_L` | `MOTOR_N_min` | `SW_LIMIT_L_N_use=1` |
| `2` | `SW_LIMIT_R` | `MOTOR_N_max` | `SW_LIMIT_R_N_use=1` |
| `3` | stall / `DRV_ERROR` seek left | `MOTOR_N_min` | stall line on `DRV_ERROR` |
| `4` | stall / `DRV_ERROR` seek right | `MOTOR_N_max` | stall line on `DRV_ERROR` |

Pico motor 1: `PIN_SW_LIMIT_L_1` GP2, `PIN_SW_LIMIT_R_1` GP3, `PIN_DRV_ERROR_1` GP12. Motor 2 (`CS motors 2`): LIMIT GP6/7, `DRV_ERROR_2` GP13. Motor 3 (`CS motors 3`): LIMIT GP10/11, `DRV_ERROR_3` GP14. Zero remap: see [pins.md](../mc/pins.md).

### Mechanical NC/NO to GND (limit-home)

**Status:** Working (default firmware polarity).

```
  GP26 ----+----[ switch ]---- GND     (LIMIT_L, home_mode_1=1)
           |
        (internal pull-up)
```

Use NO or NC so the **active** level matches `SW_LIMIT_L_1_active` / `SW_LIMIT_R_1_active` (default 0 = to GND with pull-up). Optical / hall sensors: set polarity to the sensor’s open-collector behaviour.

**Config example:**

```ini
# SliderMC mc.ini — home on left hard limit
SW_LIMIT_L_1_use=1
SW_LIMIT_L_1_active=0
home_mode_1=1
home_speed_1=25
home_move_out_1=3
home_accel_1=20
```

### Sensorless / stall-home (`home_mode_N` 3/4)

Seek until `DRV_ERROR` asserts, **pulse EN** so a latched DIAG/Protect can clear, wait until the line is stably idle, then drive out `home_move_out_N`. This is **not** the normal EMO halt path.

| Driver | Stall on `DRV_ERROR`? | Notes |
|--------|----------------------|--------|
| **TMC2208** | No. DIAG is OT / short only. | Use mode 1/2 or `SP`. |
| **TMC2209** | Yes, if StallGuard is enabled (UART `SGTHRS` / `TCOOLTHRS`; SliderMC does not configure TMC UART). Wire **DIAG → `DRV_ERROR`**, typically `DRV_ERROR_1_active=1`. | DIAG **latches** until ENN is pulsed. Firmware pulses EN, waits for clear, then drives out. |
| **MKS SERVO42C** (STEP/DIR) | No ALM on the main header. “Wrong Protect” latches and needs screen or UART unblock. | Do **not** use 3/4. |
| **MKS SERVO42D** (STEP/DIR) | Pulse interface works; **no `OUT_1`** stall pin. | Do **not** use 3/4. Prefer LIMIT 1/2 or `SP`. RS485 is a separate stack (`MC_MKS_Client`). |
| **MKS SERVO57D** (STEP/DIR) | **`OUT_1`** = stall (0 = protected). Wire to `DRV_ERROR`, `DRV_ERROR_1_active=0`. Enable **Protect**. | Matches 3/4: MKS clears Protect when EN is invalid — same EN pulse. Do not use 3/4 on the RS485 client. |

Closed-loop wiring: [integrated-drivers.md](integrated-drivers.md). RS485 42D/57D (no SliderMC): [mks-servoxx.md](mks-servoxx.md).
