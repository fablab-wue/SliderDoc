<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "SliderDMC build";
  --doc-path: ".\\SliderDoc\\dmc\\build.md";
}
</style>

# SliderDMC build

[← Index](README.md)

Firmware: [SliderDMC](https://github.com/fablab-wue/SliderDMC). Board: **Waveshare RP2040-Zero**. Core: earlephilhower Arduino Pico via PlatformIO (`env:rpipico`, `board = pico` — GPIO numbers match the Zero map in [pins.md](pins.md)).

## Prerequisites (Windows)

1. Install [VS Code](https://code.visualstudio.com/).
2. Install the **PlatformIO IDE** extension.
3. **File → Open Folder** → the `SliderDMC` repository root (not SliderMC / SliderCtrl).
4. Connect the Zero over USB.

SliderMC build notes (WinUSB / picotool) also apply: [mc/build.md](../mc/build.md#windows-upload-picotool--upload_port-error).

## Flags (`platformio.ini`)

| Flag | Default | Meaning |
|------|---------|---------|
| `-DSIMULATE` | on | After ~2 s with no MC banner/`CG`, run a 1-axis simulator |
| `-DSLIDERDMC_STATUS_LED_MODE=1` | on | GP16 WS2812. `=0` is classic `LED_BUILTIN` blink |

```bash
python -m platformio run
python -m platformio run --target upload
```

USB CDC is **binary DMC**. `pio device monitor` will not show a useful text console. Close Dragonframe (and any other COM session) before Upload — DTR/1200-baud reset needs the port free.

## PC test (no Dragonframe)

Keep Dragonframe disconnected, one COM session:

```bash
python pc_dmc_test.py COM21 --sequence hi
```

Expect `type=0x0001`, `name="SliderCtrl MC V1 (dmc-lite)"`, `motors=1` (or live `axis`). Further sequences: `hi,status,position,config` and `hi,gio,dmx`. Script lives in the SliderDMC repo.

## Dragonframe Connect

Scene → Connections → **dmc-lite** → this COM port. Arc: **steps per unit = 1000**. See [overview.md](overview.md).

Official wire format: [DMC-Protocol-2024-08-13.pdf](https://www.dragonframe.com/download/dmcproto/DMC-Protocol-2024-08-13.pdf).
