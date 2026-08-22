<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Switches for Homing";
  --doc-path: ".\\SliderDoc\\components\\homing-switches.md";
}
</style>

# Switches for Homing

[← Components index](index.md)

Hard-limit / home input on **SliderMC** **`PIN_SW_HOME`** (GP22). With `axis2_use=1`, axis 2 uses **`PIN_SW_HOME2`** (GP9) and matching `SW_HOME_*_2` / `home_*_2` config keys.

SliderMC pinout: [PINS.md](../mc/pins.md) · [pico_pinout_mc.png](../assets/img/pico_pinout_mc.png) · [CONFIG.md](../mc/config.md) · [ARCHITECTURE.md](../architecture/overview.md)

Optional hard limits (separate from home): `PIN_SW_LIMIT_L` / `PIN_SW_LIMIT_R` (GP26 / GP27) when `SW_LIMIT_L_use` / `SW_LIMIT_R_use` are enabled — see PINS.md.

| Symbol | Default | Role |
|--------|---------|------|
| `PIN_SW_HOME` | 22 | SliderMC home/reference GPIO |
| `SW_HOME_use` | 0 | Set `1` to enable this homing input |
| `SW_HOME_active` | 0 | Typical switch to GND with pull-up |
| `home_mode` | 0 | `1`/`2` select SW_HOME direction |
| `home_speed` | 20.0 | Seek speed |
| `home_move_out` | 3.0 | Back off after trip |
| `home_accel` | 20.0 | Homing accel |

### Mechanical NC/NO to GND

**Status:** Working (default firmware polarity).

```
  GP22 ----+----[ switch ]---- GND
           |
        (internal pull-up)
```

Use NO or NC so the **active** level matches `SW_HOME_active`. Optical / hall sensors: set polarity to the sensor’s open-collector behaviour.

**Photos:** add under `../assets/img/components/` when you document a specific switch.

**Config example:**

```ini
# SliderMC mc.ini
SW_HOME_use=1
SW_HOME_active=0
home_mode=1
home_speed=20
home_move_out=3
home_accel=20
```
