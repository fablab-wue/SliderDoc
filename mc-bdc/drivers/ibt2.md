# ibt2 — BTS7960 module

`CS motor_n_driver ibt2`

Pulse RPWM or LPWM. Tie both R_EN and L_EN to `DRV_C` (high = on). Do not PWM the enable pins; they take about a millisecond to wake, and dropping them coasts the motor. `auto` sense is current. Wire one IS pin to `DRV_CUR_ERR`. The other IS pin may float.

| | |
|---|---|
| Supply | about 6–27 V (module-dependent) |
| Current | module boards are often sold as 43 A; treat that as a peak and keep the heatsink |
| Active brake | yes — both PWM inputs low, enables high |
| Hand release | yes — `SE 0` drops `DRV_C` |
| Current limit | yes, after `motor_n_i_per_v` matches the IS resistor |
| Error input | no |

Both inputs high with the enables high turns on both high sides and shorts the supply. Brake is both PWM inputs low.

```text
DRV_A_n ---- RPWM
DRV_B_n ---- LPWM
DRV_C_n ---- R_EN and L_EN
CUR_ERR_n -- R_IS or L_IS
```
