# SliderMC_BDC firmware docs

C++ / FreeRTOS motion controller for two brushed DC motors with AB encoders, plus up to four RC servos. Same `# MC V1` command set as SliderMC. `CS motors` is 1–2. `CS servos` is 0–4.

**Start here:** [pins.md](pins.md)

| Document | Topic |
|----------|-------|
| [pins.md](pins.md) | Pico and RP2040-Zero GPIO map |
| [drivers.md](drivers.md) | H-bridge modules and presets |
| [tune.md](tune.md) | Position and speed loops, step-by-step tune |
| [motion.md](motion.md) | 1 kHz cascade, encoder, hand teach, homing |
| [config.md](config.md) | Driver, sense, and PID keys |
| [../mc/build.md](../mc/build.md) | Flash a UF2, PlatformIO, host tests |
| [../mc/config.md](../mc/config.md) | Shared `CS` / `CG` keys |
| [../mc/motion.md](../mc/motion.md) | Sine planner (same law as SliderMC) |
| [../contract/protocol.md](../contract/protocol.md) | ASCII protocol |

**Code repo:** [SliderMC_BDC](https://github.com/fablab-wue/SliderMC_BDC)

Servo 1 uses the `EXT_4` pin, servo 2 uses `EXT_3`, and so on. With no servo configured, all four extender pins are free.
