# SliderMC firmware docs

C++ / FreeRTOS motor controller for RP2040 (STEP/DIR axis; optional 2nd STEP/DIR via `axis2_use`).

**Start here:** [build.md](build.md)

| Document | Topic |
|----------|-------|
| [build.md](build.md) | VS Code, PlatformIO, flash, host tests |
| [config.md](config.md) | Config keys, `CS`/`CG`, persistence |
| [dual-movement.md](dual-movement.md) | Optional 2nd axis: timing, units, soft limits |
| [pins.md](pins.md) | Fixed GPIO map |
| [motion.md](motion.md) | Planner, PIO STEP, tasks |
| [motion-path.md](motion-path.md) | Host-authored path playback (`PD`/`PG`) |
| [motion-technique.md](motion-technique.md) | Motion technique notes |

**Code repo:** [SliderMC](https://github.com/fablab-wue/SliderMC)

**Related:** [contract/protocol.md](../contract/protocol.md) · [UIC](../uic/README.md)