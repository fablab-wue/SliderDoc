# Stepper Motors with external Drivers

[← Components index](index.md)

Standard NEMA17 (or similar) + separate STEP/DIR board. Wire STEP/DIR/EN to the **SliderMC** board — not the UIC. For a second motor when `axis2_use=1`, wire the second driver to the axis-2 pins for your board — see [pins.md](../mc/pins.md).

SliderMC pinout: [PINS.md](../mc/pins.md) · [pico_pinout_mc.png](../assets/img/pico_pinout_mc.png) · [CONFIG.md](../mc/config.md) · [ARCHITECTURE.md](../../architecture/overview.md)

### A4988 / DRV8825-class (carrier boards)

**Status:** Working (common STEP/DIR pattern; match `steps_per_unit` / microsteps to MS straps).

| SliderMC | Driver |
|----------|--------|
| GP18 | STEP |
| GP19 | DIR |
| GP20 | EN (usually active-low → `DRV_EN_active=0`) |
| GND | GND (share with motor PSU −) |
| — | VM from motor PSU only |

**Config (SliderMC `mc.ini` / `CS`):** e.g. `steps_per_unit=320` for 200 full steps × 8 microsteps / 5 mm/rev; `DRV_EN_active=0`.

### TMC2208 / TMC2209 (SilentStepStick / BTT-style, standalone)

**Status:** Working (wiring documented).

Typical: SliderMC 3V3 → VIO; GP18/19/20 → STEP/DIR/EN; shared GND; VM from motor PSU. Set StealthChop/SpreadCycle per board straps. MS1/MS2 → GND for **8** microsteps.

![TMC STEP/DIR wiring](../../assets/img/tmc_stepdir_wiring.svg)

*(Diagram labels “Pico” = **SliderMC** Pico.)*

Details: [Technical Manual — TMC2208/09](../uic/projects/jkslider/technical/motion-installer.md#tmc2208--tmc2209-silentstepstick--btt-style-standalone).

### TMC5160 / TMC5160T Pro (SPI module)

**Status:** Working for STEP/DIR after microsteps are programmed offline.

JKSlider / SliderMC do **not** bit-bang SPI. Program `MRES` / current with another host so **microsteps** match `steps_per_unit`, then run STEP/DIR from the **SliderMC** Pico.

Details: [Technical Manual — TMC5160](../uic/projects/jkslider/technical/motion-installer.md#tmc5160t--tmc5160t-pro-btt-spi-module).

**Manufacturer:** board vendors vary (BigTreeTech and SilentStepStick clones). Add exact shop links when you qualify a SKU.
