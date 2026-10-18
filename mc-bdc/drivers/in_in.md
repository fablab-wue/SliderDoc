# in_in — MX1508, L9110S, DRV8833, 50 A board

`CS motor_n_driver in_in`

Two inputs only. Pulse one, hold the other low. Swap to reverse. Both high is the short brake used by MX1508 and DRV8833. Both low coasts. If the board has nSLEEP or STBY, wire it to `DRV_C` (high = run). `auto` sense is off.

| | |
|---|---|
| Supply | MX1508 / L9110S about 2.5–12 V; DRV8833 VM 10.8 V max |
| Current | about 1–1.5 A on the small modules; the 50 A board is a separate part |
| Active brake | yes — both inputs high |
| Hand release | yes — both inputs low, and nSLEEP low when that pin is wired |
| Current limit | no |
| Error input | no |

The [50 A isolated module](https://www.amazon.de/gp/product/B07RQKS377) uses this preset: two PWM inputs, 5–15 V, no separate enable. Confirm that board's 00/11 table on the bench before relying on its brake. A review of that module measured a large voltage spike when the motor terminals were shorted; a bidirectional TVS across the motor is worth fitting.

```text
DRV_A_n ---- IN1
DRV_B_n ---- IN2
DRV_C_n ---- nSLEEP / STBY if the board has it
```

DRV887x in PWM mode (PMODE high) uses this same preset. Both inputs high is then the chip's slow-decay brake, and `DRV_C` is nSLEEP.
