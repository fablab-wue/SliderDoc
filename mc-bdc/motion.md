# Motion

The sine-ramp planner is the same law as [SliderMC](../mc/motion.md). It advances a **commanded** position in time: cruise, accel, decel, reverse, soft limits, and path playback. It does not emit STEP pulses.

A 1 kHz task closes the loops on the encoder. One quadrature edge (4× decode) is one planner step, so `steps_per_unit` is encoder counts per user unit. See [tune.md](tune.md) for the two loops and the gain keys.

`IP` and the verbose line report the **measured** encoder position. The planner setpoint does not follow a free shaft. `~` on USB prints one regulator line (setpoint, encoder, error, speeds, duty, current). The same character on the UIC UART is ignored.

## Encoder

Counting uses the SliderCtrl quadrature program. It fills one PIO instruction block. Up to four state machines share it, so two encoders fit. `pin_b` must be `pin_a + 1`. Internal pull-ups are on.

The program pushes one FIFO word per accepted edge, and the RX FIFO is only 8 deep. A PIO interrupt drains it. The 1 kHz loop is not the counter.

On a direction change the reported position is 1 count behind. Repeated reversals do not accumulate a loss. The regulator latches a ±1 bias from the last travel sign and holds it while stopped.

## Hand teach

`SE 0` releases bridges that have a coast state. The counters keep running, so `IP` is the pose to store. The setpoint does not follow. While still released, `SP` the position you just read. That sets the hold point without moving the mechanics. Then `SE 1` holds there.

`pwm_ab` brakes when both direction pins are low, and `SE 0` drives them low. Disconnect the motor supply before turning that axis by hand.

## Limits and homing

`LIMIT_L_n` and `LIMIT_R_n` are the hard-limit inputs. They stay off until `motor_N_limit_l_use` / `motor_N_limit_r_use` is 1. Homing modes 1 and 2 seek those switches. Modes 3 and 4 are encoder stall: commanded speed is nonzero while measured speed stays near zero and the duty is high.

`motor_N_sense error` makes `IE` report `DRV_CUR_ERR_n` and halt motion. Otherwise `IE` stays 0. The pin is never both an ADC input and a fault input.
