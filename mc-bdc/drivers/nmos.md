# nmos — 170 W 5–30 V module

`CS motor_n_driver nmos`

The [170 W module](https://www.amazon.de/gp/product/B0GVD6CPTL) uses two half-bridge drivers and four NMOS transistors. Three logic wires: IN1, IN2, and an active-low EN. Forward is IN1 = PWM and IN2 low. Reverse swaps them. Both inputs low, with EN active, is the brake. `auto` sense is off. 3.3 V is a valid high.

| | |
|---|---|
| Supply | 5–30 V |
| Current | listing power is 170 W. At 12 V that is about 14 A if the heatsink and wiring allow it |
| Active brake | yes — both inputs low while EN is low |
| Hand release | yes — EN high |
| Current limit | no |
| Error input | no |

Duty stops at 99%. The control pins must not sit at a DC high, or the bootstrap capacitor does not recharge. On `SE 1` the firmware drives EN high and then low so the board sees the falling edge it requires before the inputs are used.

```text
DRV_A_n ---- IN1
DRV_B_n ---- IN2
DRV_C_n ---- EN      (active low)
            motor supply 5–30 V
```
