<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Dragonframe on a slider";
  --doc-path: ".\\SliderDoc\\dmc\\README.md";
}
</style>

# Dragonframe on a slider

Use **DF_DMC_2_MC** when Dragonframe Arc should drive the slider you already have. It takes the place of the panel ([SliderCtrl](https://github.com/fablab-wue/SliderCtrl)) on the SliderMC UART. The rail, motors, and housing stay as they are.

```text
Dragonframe (PC)
        USB
DF_DMC_2_MC
        UART 115200  (instead of the panel)
SliderMC
```

Do **not** put the panel and DF_DMC_2_MC on the same MC UART at the same time.

## Flash a release

No compiler and no PlatformIO. The bridge is a Waveshare RP2040-Zero.

1. Download `DF_DMC_2_MC-<tag>-rp2040zero.uf2` from the [DF_DMC_2_MC Releases](https://github.com/fablab-wue/DF_DMC_2_MC/releases) page.
2. Hold **BOOTSEL**, plug in USB, then release BOOTSEL.
3. Copy the UF2 onto the `RPI-RP2` drive. The board reboots into the new firmware.

The other Dragonframe bridges are separate downloads: [DF_DMC_2_PWM](https://github.com/fablab-wue/DF_DMC_2_PWM/releases) (`DF_DMC_2_PWM-<tag>-pico.uf2`, Raspberry Pi Pico) and [DF_DMC_2_MKS](https://github.com/fablab-wue/DF_DMC_2_MKS/releases) (`DF_DMC_2_MKS-<tag>-rp2040zero.uf2`, Waveshare RP2040-Zero). Both use the same BOOTSEL copy onto `RPI-RP2`.

A new file is built when a `v*` tag is pushed on that firmware repo. Rebuild an existing tag from that repo's Actions page with **Run workflow**.

## In Dragonframe

1. Scene → Connections → Add connection
2. Device type **dmc-lite**
3. Serial port of the DF_DMC_2_MC board
4. Connect
5. In Arc, set **steps per unit = 1000** (1000 steps = 1 mm or 1 deg)

USB on that board is binary DMC. It is not a text console.

## Where the rest of the manual lives

Pinout, wiring, build, LED colors, and the opcode map are in the firmware repository:

[DF_DMC_2_MC docs](https://github.com/fablab-wue/DF_DMC_2_MC/blob/main/docs/README.md)

SliderMC itself is unchanged. Its UART contract is still [contract/protocol.md](../contract/protocol.md).
