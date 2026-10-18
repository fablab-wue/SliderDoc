# dbh1 — DBH-1A, 5–12 V 30 A

`CS motor_n_driver dbh1`

Dual-channel board sold as a 5–12 V, 0–30 A H-bridge with a heatsink and a current pin (switch up to about 200 kHz). Pulse one input and hold the other low. Both inputs high is the brake. `DRV_C` is the channel enable (high = run). Tie ENB of the second channel to motor 2's `DRV_C`. `CT` goes to `DRV_CUR_ERR`. `auto` sense is current.

| | |
|---|---|
| Supply | 5–12 V (about 15 V absolute). A 24 V rail will destroy the board |
| Current | listed 0–30 A per channel. `CT` reaches 3.3 V at about 21 A |
| Active brake | yes — both inputs high |
| Hand release | yes — enable low |
| Current limit | yes |
| Error input | no |

`CT` is about 0.155 V per amp, so `motor_n_i_per_v` left at 0 uses about 6.45 A/V. Set `motor_n_i_limit` for foldback. Above about 21 A the Pico pin exceeds 3.3 V; divide `CT` and set your own `i_per_v` if the motor can pull more. Logic high is valid from 2.5 V. Duty stops at 98% because of the bootstrap. Firmware PWM is 20 kHz.

```text
DRV_A_n ---- IN1
DRV_B_n ---- IN2
DRV_C_n ---- ENA
CUR_ERR_n -- CT
            motor supply 5–12 V
```
