# Config keys

Shared keys (`SS`, `SA`, soft limits, homing, units, path buffer) are in [SliderMC config](../mc/config.md). This page is only what the DC-servo firmware adds. `N` is 1 or 2. `CS` stores the value in `/mc.ini`. `CG` reads it back.

## Driver

| Key | Values | Default |
|-----|--------|---------|
| `motor_N_driver` | `ph_en`, `ibt2`, `in_in`, `tb6612`, `l298n`, `pwm_ab`, `dbh1`, `nmos`, `lmd18200` | `ph_en` |
| `motor_N_sense` | `auto`, `current`, `error`, `off` | `auto` |
| `motor_N_dir_active` | `1` positive duty is forward, `0` swaps it | `1` |

`auto` follows the preset. `CG motor_1_sense` prints `auto(current)` or `auto(off)`. An explicit value sticks until you set `auto` again. Changing `motor_N_driver` reconfigures the bridge and the servo PWM slices.

Presets and wiring: [drivers.md](drivers.md).

## Current

| Key | Default | Meaning |
|-----|---------|---------|
| `motor_N_i_per_v` | 0 | amps per volt at `DRV_CUR_ERR_n`. 0 uses the preset scale when one exists (`dbh1` is about 6.45 A/V). |
| `motor_N_i_limit` | 0 | amps. 0 disables foldback. Above the limit the speed command is scaled down. |

The ADC is read while the commanded duty is away from zero. It is not aligned to a PWM edge. Keep the pin at or below 3.3 V.

## PID

See [tune.md](tune.md) for the meaning of each gain and the bench sequence. Defaults: `pos_kp` 12, `vel_kp` 0.0015, `vel_ki` 0.4, `vel_ff` 1, `vel_lpf_hz` 40. The other PID terms default to 0.
