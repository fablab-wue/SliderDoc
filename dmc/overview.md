<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "DF_DMC_2_MC overview";
  --doc-path: ".\\SliderDoc\\dmc\\overview.md";
}
</style>

# DF_DMC_2_MC overview

[← Index](README.md)

**DF_DMC_2_MC** is a USB **DMC v2** client for [Dragonframe](https://www.dragonframe.com/) Arc. It sits on a **Waveshare RP2040-Zero** between the PC and [SliderMC](https://github.com/fablab-wue/SliderMC):

```text
Dragonframe (PC)
        USB CDC  — binary DMC v2
DF_DMC_2_MC  (RP2040-Zero)
        UART 115200  GP12 TX / GP13 RX  — SliderMC ASCII (VH, CG, MT, PG, …)
SliderMC
```

It is **not** a UIC panel. The panel ([SliderCtrl](https://github.com/fablab-wue/SliderCtrl)) and Dragonframe are alternate hosts of the same motion board. Do not put both on the MC UART at once.

Code: [DF_DMC_2_MC](https://github.com/fablab-wue/DF_DMC_2_MC). Pins: [pins.md](pins.md). Opcode map: [mapping.md](mapping.md). Build: [build.md](build.md).

## Official protocol (Dragonframe)

DF_DMC_2_MC implements a **dmc-lite** subset. Wire format and message IDs are defined by Dragonframe — we do **not** redistribute their sketches or PDFs.

- [DMC v2 COMM Protocol (2024-08-13 PDF)](https://www.dragonframe.com/download/dmcproto/DMC-Protocol-2024-08-13.pdf)
- [How do I integrate a motion control system?](https://www.dragonframe.com/ufaqs/how-do-i-integrate-a-motion-control-system-with-dragonframe/) (same PDF; `dmc_msg.h` / `dmc_msg.c`)
- [Where do I find the dmc-lite Arduino sketch?](https://www.dragonframe.com/ufaqs/where-do-i-find-the-dmc-lite-arduino-sketch/) — installed with Dragonframe 2024+ under `Resources/Arc Motion Control/dmc`

Our behaviour (hello name, units, which opcodes we honour) is in this folder and in firmware `src/`.

## Dragonframe Connect

Dragonframe always starts with binary `MSG_HI` (`0x0001`). DF_DMC_2_MC replies with identity named **`SliderCtrl MC V1 (dmc-lite)`**. Device type in Scene → Connections stays **dmc-lite**. An unsolicited hello is also sent when the USB serial port opens.

Hello fields:

- motor count from SliderMC `CG` `axis` (1–6; simulator stays at 1)
- DMX count **512**
- GIO out **4** / GIO in **4**
- upload frame count **2048**
- capabilities `REAL_TIME` + `REAL_TIME_CAMERA`
- protocol version **2**, firmware `1.2.3`

In Dragonframe:

1. Scene → Connections → Add connection
2. Device type **dmc-lite**
3. Serial port of the Zero
4. Connect
5. In Arc, set **steps per unit = 1000**

USB is **CDC only** (no mass-storage log drive). CDC is binary DMC — the PlatformIO serial monitor is not a text console.

## Units (DMC wire)

DMC positions, speeds, and limits are signed integers with no unit field. DF_DMC_2_MC uses a **fixed scale**:

| DMC value | SliderMC |
|-----------|----------|
| 1000 steps | 1 mm (linear) or 1 deg (servo) |
| 1000 steps/s | 1 mm/s or 1 deg/s |
| 1000 steps/s² | 1 mm/s² or 1 deg/s² |

Conversion is only `÷ 1000` into SliderMC millimetres/degrees (`MT`, `SS`, `SA`, `SL`/`SR`). Do **not** scale by MC `steps_per_unit_N`; MC already turns mm into motor steps. Reset pose uses `SP` (no motion), not `MH`.

Scene FPS is **not** in hello. Dragonframe sends FPS×1000 only on `MSG_RT_RUN_MOVE` (`0x0111`) and `MSG_RT_JOG_ALL` (`0x0120`). That becomes MC `PS` (µs per frame), e.g. 24 fps → `24000` → `PS 41667`. Shoot-move-shoot has no FPS.

## Simulator

Build flag `-DSIMULATE` is on by default. If no SliderMC answers `CG` / a `# MC V1` banner on UART within 2 seconds, the firmware simulates one axis using the same `CG:` / `IP:` line shapes as live SliderMC.

On a live MC: `SE 1`, `SV 1`, and `CS verbose_rate_hz 10` so `#` status can feed ~10 Hz DMC position reports.

## LED meanings (GP16 WS2812)

| Color | Meaning |
|-------|---------|
| Magenta pulse | Boot |
| Blue pulse | Waiting for Dragonframe `MSG_HI` |
| Cyan/green | HI received, MC not ready yet |
| Green pulse | Simulator or MC ready |
| Bright cyan flash | DMC traffic |
| Red pulse | No MC and simulator disabled |

Classic onboard LED: `SLIDERDMC_STATUS_LED_MODE=0`.

## Firmware `src/` map

| File | Role |
|------|------|
| `config.h` | Limits, pin map, 1000 steps = 1 mm/deg, hello name |
| `dmc_protocol` | Framing, opcodes, Fletcher checksum |
| `gio` | Local DMC GIO GP1–8, shutter GP9, buzzer GP10, MOVE GP11 |
| `dmx` | 512-ch live DMX on GP0 (PIO UART); channels 1–6 also PWM on GP29/28/27/26/15/14 |
| `path_store` | DF upload table → MC `PD` samples |
| `mc_client` | SliderMC UART + simulator |
| `status_led` | WS2812 / classic LED |
| `bridge` | USB DMC dispatch |
| `main.cpp` | `setup()` / `loop()` |

GIO on this Zero is **not** SliderMC extender `EO`/`EI`. See [pins.md](pins.md).
