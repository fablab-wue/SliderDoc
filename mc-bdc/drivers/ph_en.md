# ph_en — DRV887x, Cytron, Pololu G2

`CS motor_n_driver ph_en`

PWM plus direction. On a DRV8874/76/73, tie PMODE low so EN is the PWM pin and PH is direction. `DRV_C` is nSLEEP (high = awake). `auto` sense is current: `DRV_CUR_ERR` is IPROPI or the board CS pin. IPROPI is a current output. A resistor to GND makes the ADC voltage, and the reading is valid while the bridge is driving. Size the resistor so the pin stays at or below 3.3 V.

| | |
|---|---|
| Supply | chip-dependent; DRV8874 is about 4.5–37 V |
| Current | chip-dependent; a DRV8874 is about 6 A peak, less continuous |
| Active brake | no |
| Hand release | yes (`SE 0` drops nSLEEP; duty 0 also coasts) |
| Current limit | yes, after `motor_n_i_per_v` matches the sense resistor |
| Error input | yes if `motor_n_sense error` and nFAULT is wired instead of IPROPI |

Duty 0 drives the EN/PWM pin low and leaves nSLEEP high. On a DRV8874 in PH/EN mode, EN low is Hi-Z, not a winding short. The position loop still corrects once the shaft leaves the ±1 count deadband. That is not a locked hold.

For a real brake, tie PMODE high and select [`in_in`](in_in.md): `DRV_A` / `DRV_B` are IN1/IN2 (both high brakes) and `DRV_C` is nSLEEP.

```text
DRV_A_n ---- EN / PWM
DRV_B_n ---- PH / DIR
DRV_C_n ---- nSLEEP   (high = awake)
CUR_ERR_n -- IPROPI or CS
```

Cytron and Pololu G2 boards that use the same PWM+DIR header share this preset. Confirm on that board whether PWM low coasts or brakes. This firmware treats PWM low as coast.
