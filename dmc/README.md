<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "SliderDMC";
  --doc-path: ".\\SliderDoc\\dmc\\README.md";
}
</style>

# SliderDMC firmware docs

DragonFrame **DMC v2** USB bridge to **SliderMC** ASCII UART. Shipping board: **Waveshare RP2040-Zero**.

**Start here:** [overview.md](overview.md)

| Document | Topic |
|----------|-------|
| [overview.md](overview.md) | What it is, Connect, units, simulator, LED |
| [build.md](build.md) | PlatformIO, flags, `pc_dmc_test.py` |
| [pins.md](pins.md) | GPIO map, UART to MC, wiring ASCII |
| [mapping.md](mapping.md) | DMC opcodes → MC / local GPIO |

**Code repo:** [SliderDMC](https://github.com/fablab-wue/SliderDMC)

**Official DMC protocol (Dragonframe, not this project):** [DMC-Protocol-2024-08-13.pdf](https://www.dragonframe.com/download/dmcproto/DMC-Protocol-2024-08-13.pdf)

**Related:** [mc/README.md](../mc/README.md) · [contract/protocol.md](../contract/protocol.md) · [architecture/overview.md](../architecture/overview.md)
