# Motor drivers

`n` is the motor number, 1 or 2. Set the preset with `CS motor_n_driver <name>`. `motor_n_sense` defaults to `auto` and follows the preset (`current`, `error`, or `off`). The four logic pins are `DRV_A_n`..`DRV_D_n`. There is no shared enable pin. `DRV_CUR_ERR_n` is the ADC or the fault input, never both.

Yes/no below is what this firmware does with that preset. Most bridges are driven at 20 kHz. `lmd18200` is 10 kHz. Bootstrap modules stop short of 100% duty so the high-side supply can recharge.

| Module | Chip | Config | Connection | Brake | Hand | Current | Error |
|--------|------|--------|------------|-------|------|---------|-------|
| [DRV887x PH/EN](drivers/ph_en.md) | DRV8874 / 76 / 73 | `ph_en` | `A` PWM/EN, `B` PH, `C` nSLEEP, `CUR_ERR` IPROPI | no | yes | yes | if `sense error` |
| [IBT-2](drivers/ibt2.md) | BTS7960 | `ibt2` | `A` RPWM, `B` LPWM, `C` R_EN+L_EN, `CUR_ERR` IS | yes | yes | yes | no |
| [IN/IN and 50 A board](drivers/in_in.md) | MX1508, DRV8833, … | `in_in` | `A` IN1, `B` IN2, `C` nSLEEP if present | yes | yes | no | no |
| [TB6612](drivers/tb6612.md) | TB6612FNG | `tb6612` | `A` AIN1, `B` AIN2, `C` PWMA, `D` STBY | yes | yes | no | no |
| [L298N](drivers/l298n.md) | L298N | `l298n` | `A` IN1, `B` IN2, `C` ENA | yes | yes | no | no |
| [9–30 V 60 A](drivers/pwm_ab.md) | discrete NMOS | `pwm_ab` | `A` PA, `B` A, `C` B | yes | no | no | no |
| [DBH-1A](drivers/dbh1.md) | DBH-1A | `dbh1` | `A` IN1, `B` IN2, `C` ENA, `CUR_ERR` CT | yes | yes | yes | no |
| [170 W NMOS](drivers/nmos.md) | half-bridge + NMOS | `nmos` | `A` IN1, `B` IN2, `C` EN (active low) | yes | yes | no | no |
| [LMD18200](drivers/lmd18200.md) | LMD18200 | `lmd18200` | `A` PWM, `B` DIR, `C` BRAKE | yes | yes | after `i_per_v` | thermal flag instead of current |

STEP/DIR stepper drivers (TMC2209, DRV8825, A4988) stay on SliderMC. They have no PWM magnitude input.

`CG motor_1_sense` prints `auto(current)` or `auto(off)`. Set `current`, `error`, or `off` only to override. `error` makes `IE` report the pin and halt motion. `current` uses the ADC while the commanded duty is away from zero (`motor_n_i_per_v`, `motor_n_i_limit`). The read is not aligned to a PWM edge.
