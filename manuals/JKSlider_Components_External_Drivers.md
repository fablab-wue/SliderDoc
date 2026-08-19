# Stepper Motors with external Drivers

[← Components index](JKSlider_Components.md)

Standard NEMA17 (or similar) + separate STEP/DIR board. Wire STEP/DIR/EN to the **SliderMC** Pico — not the UIC.

SliderMC pinout: [PINS.md](../../SliderMC/docs/PINS.md) · [pico_pinout_mc.png](../../SliderMC/docs/img/pico_pinout_mc.png) · [CONFIG.md](../../SliderMC/docs/CONFIG.md) · [ARCHITECTURE.md](../docs/ARCHITECTURE.md)

### A4988 / DRV8825-class (carrier boards)

**Status:** Working (common STEP/DIR pattern; match `steps_per_mm` / microsteps to MS straps).

| SliderMC | Driver |
|----------|--------|
| GP18 | STEP |
| GP19 | DIR |
| GP20 | EN (usually active-low → `DRV_EN_active=0`) |
| GND | GND (share with motor PSU −) |
| — | VM from motor PSU only |

**Config (SliderMC `mc.ini` / `CS`):** e.g. `steps_per_mm=320` for 200 full steps × 8 microsteps / 5 mm/rev; `DRV_EN_active=0`.

### TMC2208 / TMC2209 (SilentStepStick / BTT-style, standalone)

**Status:** Working (wiring documented).

Typical: SliderMC 3V3 → VIO; GP18/19/20 → STEP/DIR/EN; shared GND; VM from motor PSU. Set StealthChop/SpreadCycle per board straps. MS1/MS2 → GND for **8** microsteps.

![TMC STEP/DIR wiring](../docs/img/tmc_stepdir_wiring.svg)

*(Diagram labels “Pico” = **SliderMC** Pico.)*

Details: [Technical Manual — TMC2208/09](JKSlider_Technical_Manual_Motion.md#tmc2208--tmc2209-silentstepstick--btt-style-standalone).

### TMC5160 / TMC5160T Pro (SPI module)

**Status:** Working for STEP/DIR after microsteps are programmed offline.

JKSlider / SliderMC do **not** bit-bang SPI. Program `MRES` / current with another host so **microsteps** match `steps_per_mm`, then run STEP/DIR from the **SliderMC** Pico.

Details: [Technical Manual — TMC5160](JKSlider_Technical_Manual_Motion.md#tmc5160t--tmc5160t-pro-btt-spi-module).

**Manufacturer:** board vendors vary (BigTreeTech and SilentStepStick clones). Add exact shop links when you qualify a SKU.
