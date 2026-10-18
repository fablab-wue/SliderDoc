# pwm_ab — 9–30 V 60 A dual module

`CS motor_n_driver pwm_ab`

The dual-channel board sold as a 9–30 V, 60 A PWM H-bridge (about 60 kHz switch, a few milliohms, bootstrap high side). Each channel has three logic inputs. `PA` is the speed PWM. `A` and `B` are direction. `A,B = 1,0` is forward, `0,1` is reverse, `0,0` is brake. The firmware never drives `1,1`. `auto` sense is off. There is no current pin and no enable pin. 3.3 V is a valid high.

| | |
|---|---|
| Supply | 9–30 V |
| Current | the listing's 60 A is a peak; one owner reported failure a little over 30 A. Keep the heatsink |
| Active brake | yes — `A` and `B` both low |
| Hand release | no — `SE 0` is that same brake |
| Current limit | no |
| Error input | no |

Duty stops at 98%. A 100% PWM leaves no time to recharge the bootstrap capacitor, and the high side drops out. Hand-teach needs the motor supply disconnected.

```text
DRV_A_n ---- PA
DRV_B_n ---- A
DRV_C_n ---- B
GND ------- G
            motor supply 9–30 V
```

The second channel of a dual board is motor 2: that channel's PWM and two direction pins go to `DRV_A_2`..`DRV_C_2`.
