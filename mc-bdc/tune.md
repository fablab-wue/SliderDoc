# Tuning

The 1 kHz loop is two loops in series.

1. Position P, plus velocity feedforward from the planner: `v_cmd = Kp · error + Kff · v_planner`. Error inside ±1 count counts as zero.
2. Speed PI on encoder velocity: `pwm = Kp · e_v + Ki · ∫e_v`. The integrator freezes while the duty is saturated.

A DC motor does not detent. While the axis is enabled and idle, the position loop holds it. On `ph_en`, duty 0 coasts, so the shaft can creep inside that ±1 count band until the loop corrects it.

## Constants

Per-axis keys, `N` = 1 or 2. `CS` writes them to `mc.ini`.

| Key | Default | Meaning |
|-----|---------|---------|
| `motor_N_pos_kp` | 12 | counts/s commanded per count of position error |
| `motor_N_pos_ki` | 0 | leave at 0 unless a constant load leaves a standing error |
| `motor_N_pos_kd` | 0 | leave at 0; it amplifies encoder noise |
| `motor_N_vel_kp` | 0.0015 | duty per (count/s) of speed error |
| `motor_N_vel_ki` | 0.4 | duty per (count/s) per second; holds steady speed |
| `motor_N_vel_kd` | 0 | leave at 0 |
| `motor_N_vel_ff` | 1 | scale on planner speed into the speed loop |
| `motor_N_vel_lpf_hz` | 40 | low-pass on measured speed |
| `motor_N_i_limit` | 0 | amps; 0 = foldback off |
| `motor_N_i_per_v` | 0 | amps per ADC volt; 0 uses the preset scale when one exists |

These defaults are a soft start for a small gearmotor, not a tuned slider.

## Step by step

`TU` prints `t_ms,set,meas,pwm,i` on USB only, up to 500 samples. The axis must be enabled (`SE 1`) or the bridge stays off.

1. With `SE 0`, turn the shaft by hand and read `IP`. Counts must change. On `pwm_ab`, disconnect the motor supply first, because release is a brake.
2. Set `CS motor_1_driver` to the wired preset. If the board has a known amp-per-volt scale, set `motor_1_i_per_v`. `dbh1` can stay at 0 and uses about 6.45 A/V. Leave `motor_1_i_limit` at 0 until the loops are stable.
3. `SE 1`, then `TU 1 pwm 0.15 200`. `meas` must move. If positive duty decreases the counts you want as forward, set `CS motor_1_dir_active 0` and repeat.
4. Speed loop: `TU 1 vel 200 300`. `set` is 200 counts/s. Raise `motor_1_vel_kp` from 0.0015 until `meas` reaches that speed without buzzing, then `motor_1_vel_ki` from 0.4 until the speed holds. Leave `vel_kd` at 0 and `vel_lpf_hz` at 40 unless the speed trace is noisy.
5. Position loop: `TU 1 pos 20 250` steps 20 counts from the current encoder reading. Raise `motor_1_pos_kp` from 12 until the error settles within a few counts without overshoot. Leave `pos_ki` and `pos_kd` at 0. Leave `vel_ff` at 1 so a real move feeds planner speed into the speed loop.
6. If current sense is wired, set `motor_1_i_limit` below the stall current and repeat the position step. The `i` column should stay near that cap instead of climbing.
7. Short real move: modest `SS` and `SA`, then `MT` a small distance. `~` on USB prints setpoint, encoder, error, speeds, duty, and current for one sample.

`TU <axis> <pwm|vel|pos> <amplitude> [ms]`. `pwm` is open-loop duty (−1..1). `vel` closes only the speed loop; the amplitude is counts/s. `pos` is a count step on both loops.

## Typical faults

| What you see | Likely cause |
|--------------|----------------|
| Overshoot past the step, then a slow return | `pos_kp` too high. Lower it before adding `pos_kd`. |
| Buzz or harsh jitter while holding | `vel_kp` too high, or `vel_lpf_hz` so high that encoder grain reaches the duty. |
| Slow swing around the target | `vel_ki` too high, or `pos_kp` and `vel_ki` both large. Drop `vel_ki` first. |
| Never reaches the speed in `TU vel` | `vel_kp` too low, the duty is already saturated, or `i_limit` is folding the command back. |
| Shaft runs the wrong way | `motor_N_dir_active` is inverted. The encoder still counts; only the drive direction flips. |
| Creeps a count or two at rest, then corrects | Normal on `ph_en`: duty 0 coasts. A preset with an active brake holds tighter. |
| `TU` prints rows but the shaft does not move | `SE` is still 0, or the bridge enable pin is not the one that preset uses. |
| Current column stays 0 | `motor_N_sense` is off, or `i_per_v` is 0 on a preset that has no built-in scale. |
