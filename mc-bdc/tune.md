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
| `motor_N_vel_kp` | 0.0015 | duty per (count/s), stored as for 320 counts/mm; the loop scales by `steps_per_unit/320` |
| `motor_N_vel_ki` | 0.4 | duty per (count/s) per second, same scale |
| `motor_N_vel_kd` | 0 | leave at 0; same scale |
| `motor_N_vel_ff` | 1 | scale on planner speed into the speed loop |
| `motor_N_vel_lpf_hz` | 40 | low-pass on measured speed |
| `motor_N_i_limit` | 0 | amps; 0 = foldback off |
| `motor_N_i_per_v` | 0 | amps per ADC volt; 0 uses the preset scale when one exists |
| `motor_N_deadzone` | 0 | mm; 0 = off. After the move stops, duty is forced off once the error has stayed inside this band |
| `motor_N_deadzone_s` | 0.1 | seconds the error must stay inside the band |

`pos_kp` is counts/s per count. It does not contain `steps_per_unit`. The stored `vel_kp`, `vel_ki`, and `vel_kd` are duty per count/s as tuned for 320 counts/mm. The loop multiplies them by `steps_per_unit / 320` before use, so do not scale them again by hand. At 20 counts/mm the values in `CG` are applied at 1/16. At 320 they are used as stored. The speed estimate waits 20 ms before it turns counts into a speed, so one edge is 50 counts/s rather than 1000.

If `TU vel` sits at `pwm` ±1, `pos_kp` and a dead-zone of a fraction of a millimetre cannot change the motion. Lower `vel_ki` before touching `pos_kp`. With an overshoot of about 20 counts at 20 counts/mm, `motor_1_deadzone` needs to be about 1.5 mm before the hold can arm. 0.1 mm is only 2 counts and is left on every reversal.

`motor_N_deadzone` 0 leaves the loop holding. While a move is going to a target, the shaft keeps driving until it is within 0.25 mm. Entering the dead-zone does not stop that move. Duty is forced off only after the error has stayed inside 0.25 mm for `deadzone_s`. After that, the dead-zone still holds a small drift so the shaft does not kick. The next tick outside the dead-zone regulates again. Duty 0 is that preset's brake or coast.

These defaults are a soft start for a small gearmotor, not a tuned slider.

## Step by step

`TU` prints `t_ms,set,meas,pwm,i` on USB only, up to 500 samples. The axis must be enabled (`SE 1`) or the bridge stays off.

1. With `SE 0`, turn the shaft by hand and read `IP`. Counts must change. On `pwm_ab`, disconnect the motor supply first, because release is a brake.
2. Set `CS motor_1_driver` to the wired preset. If the board has a known amp-per-volt scale, set `motor_1_i_per_v`. `dbh1` can stay at 0 and uses about 6.45 A/V. Leave `motor_1_i_limit` at 0 until the loops are stable.
3. `SE 1`, then `TU 1 pwm 0.15 200`. `meas` must change. If it stays on one count, the duty is below the motor's starting friction. Raise the amplitude (`TU 1 pwm 0.4 200`, then `0.7`) until the count moves. A later `TU vel` that only starts after `pwm` has climbed past about 0.6 is the same threshold. If positive duty decreases the counts you want as forward, set `CS motor_1_dir_active 0` and repeat.
4. Speed loop: `TU 1 vel 200 300`. `set` is 200 counts/s. Raise `motor_1_vel_kp` from 0.0015 until `meas` reaches that speed without buzzing, then `motor_1_vel_ki` from 0.4 until the speed holds. Leave `vel_kd` at 0 and `vel_lpf_hz` at 40 unless the speed trace is noisy.
5. Position loop: `TU 1 pos 20 250` steps 20 counts from the current encoder reading. Raise `motor_1_pos_kp` from 12 until the error settles within a few counts without overshoot. Leave `pos_ki` and `pos_kd` at 0. Leave `vel_ff` at 1 so a real move feeds planner speed into the speed loop.
6. If current sense is wired, set `motor_1_i_limit` below the stall current and repeat the position step. The `i` column should stay near that cap instead of climbing.
7. Short real move: modest `SS` and `SA`, then `MT` a small distance. `~` on USB prints setpoint, encoder, error, speeds, duty, and current for one sample.

`motor_N_dir_active` swaps which way the bridge drives. `motor_N_enc_swap` swaps which way the encoder counts. Positive duty should increase the count. `TU N ab` checks that and flips `enc_swap` when the count runs backward.

## Hold during a move

The duty for a commanded speed is a straight line, `sign(v) * u_bias + u_visc * v`, plus a speed-loop trim of at most ±0.30. `u_bias` is the duty at zero speed. `u_visc` is the extra duty per count/s, stored for 320 counts/mm and scaled by `steps_per_unit/320` like `vel_ki`. Both default to 0, which leaves the plain speed PI. `TU N` and `TU N max` measure the line from an open-loop duty sweep and write the keys. The result includes the measured speed and accel even when a stored limit does not change.

A position hold does not add the bias. The integrator is cleared on the first counts after a stop, so a correction does not keep driving. While the shaft is still outside 0.25 mm of the target, the speed line stays on, including when the planner speed has already reached zero. The commanded position stays within 0.25 mm of the encoder through the brake, so the profile does not finish early and leave the rest of the move to the hold.

## Commands

`TU N` with no mode runs `ab`, `max`, `pwm`, `vel`, then `pos`. Each phase gets at most 10 trials. A FAIL stops the sequence. The shaft needs room: `max` drives near full duty for half a second.

| Command | What it does |
|---------|----------------|
| `TU N ab` | Open-loop `+0.75` for 200 ms. Counts must rise. If they fall, `motor_N_enc_swap` is flipped. |
| `TU N max` | Sweeps open-loop duties 0.30, 0.45, 0.60, 0.75, 0.90. Fits `u_bias` and `u_visc`, writes 80% of the top speed and accel, widens the dead-zone to the first moving pulse, and sets `vel_ki` to 0.05 when it is still 0.4. Prints `TU max PASS v=… a=…`. |
| `TU N pwm amp [ms]` | Open-loop duty. PASS when the count moves by at least 3. |
| `TU N vel counts_per_s [ms]` | Speed loop. PASS when measured speed reaches 30% of the command and the duty is not ±1 the whole time. |
| `TU N pos counts [ms]` | Position step. PASS when the count moves toward the step and does not end past the start by more than the step. |

Every capture ends with `TU result PASS` or `TU result FAIL` and a reason. A key this run changed is printed as `TU cfg key old new`. `TU N` prints one line per trial and then `TU summary ab PASS` (or FAIL) for each phase that ran. The axis must be enabled (`SE 1`). A disabled axis prints `TU result FAIL axis disabled` and does not drive the bridge.

`TU <axis> <pwm|vel|pos> <amplitude> [ms]`. `pwm` is open-loop duty (−1..1). `vel` closes only the speed loop; the amplitude is counts/s. `pos` is a count step on both loops. The CSV is `t_ms,set,meas,pwm,i`, up to 500 samples. `TU N` does not print the CSV.

## Typical faults

| What you see | Likely cause |
|--------------|----------------|
| `TU pwm` holds one `meas` value | The duty never breaks static friction. Raise the amplitude until `meas` changes. A `TU vel` that stays at `meas` 0 until `pwm` passes about 0.6 is the same limit. |
| `TU vel` sits at `pwm` ±1 the whole time | `vel_ki` (and `vel_kp`) are saturating the duty. `pos_kp` and a dead-zone smaller than the overshoot cannot change that. Lower `vel_ki` first. The firmware already scales these by `steps_per_unit/320`. |
| Shaft hops about 3 times a second during `MT` | The duty that starts the motor is more than the duty that holds cruise, so the shaft starts, the loop drops the duty, and it sticks. The loop now holds the starting duty while the planner is still commanding speed, and pauses the profile if it leads the encoder by more than 3 mm. |
| Buzz or harsh jitter while holding | `vel_kp` too high, or `vel_lpf_hz` so high that encoder grain reaches the duty. |
| Slow swing around the target | `vel_ki` too high, or `pos_kp` and `vel_ki` both large. Drop `vel_ki` first. |
| Never reaches the speed in `TU vel` | `vel_kp` too low, the duty is already saturated, or `i_limit` is folding the command back. |
| Shaft runs the wrong way | `motor_N_dir_active` is inverted. The encoder still counts; only the drive direction flips. |
| Creeps a count or two at rest, then corrects | Normal on `ph_en`: duty 0 coasts. A preset with an active brake holds tighter. |
| `TU` prints rows but the shaft does not move | `SE` is still 0, or the bridge enable pin is not the one that preset uses. |
| Shaft runs back and hunts when `TU` ends | The hold target was still the count from the start of the test. The firmware brakes, then holds the count where the shaft stopped. |
| Current column stays 0 | `motor_N_sense` is off, or `i_per_v` is 0 on a preset that has no built-in scale. |
