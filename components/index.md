<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "JKSlider — Components";
  --doc-path: ".\\SliderDoc\\components\\index.md";
}
</style>

# JKSlider — Components

![JKSlider](../assets/img/jkslider-hero.png)

**JKSlider V1 by JK**

This is a **living catalog of hardware that DIY users have run with JKSlider** — either **tested and working** or documented **problems**. When you validate a new part, update the matching chapter with pins, pinouts, schematics, photos, manufacturer links, and the exact config changes needed.

JKSlider is a **UIC + SliderMC** split: panel I/O on the UIC Pico, motion axis on the motion Pico. Overview: [architecture/overview.md](../architecture/overview.md) · [architecture SVG](../assets/img/architecture_overview.svg).

**Which board?**

| Board | Typical components |
|-------|-------------------|
| **UIC** | Buttons, keypad, OLED, RGB/NeoPixel, pots, joystick, camera shutter |
| **SliderMC** | Motor / STEP·DIR driver, home switch, hard limits, Ext, DRV_ERROR |

SliderMC pins: [PINS.md](../mc/pins.md) · [pico_pinout_mc.png](../assets/img/pico_pinout_mc.png) · [CONFIG.md](../mc/config.md)

Installer wiring and firmware: [../uic/projects/jkslider/technical/README.md](../uic/projects/jkslider/technical/README.md) ([Panel](../uic/projects/jkslider/technical/panel.md), [Motion](../uic/projects/jkslider/technical/motion-installer.md)).  
MC protocol (sibling clone): [PROTOCOL.md](../contract/protocol.md).  
Mechanics / power / housings: [../build/hardware-manual.md](../build/hardware-manual.md).  
Operator panel behaviour: [../uic/projects/jkslider/user-manual.md](../uic/projects/jkslider/user-manual.md).

**Photos:** put all component product photos under [`../assets/img/components/`](../assets/img/components/). Shared diagrams (Pico pinouts, silk map, OLED mockups) may stay under `../assets/img/` and be linked from entries.

---

## How to add a component

Copy this block into the matching chapter file:

| Field | Content |
|-------|---------|
| **Name** | Short product / module name |
| **Status** | `Working` / `Issues` / `Untested` + one-line note |
| **Photos** | `../assets/img/components/...` |
| **Pins** | Board (**UIC** or **SliderMC**) + net names + GP# (and connector pin order if any) |
| **Schematic / pinout** | ASCII and/or image embeds |
| **Manufacturer** | Shop / datasheet links |
| **Config** | Exact symbols in `UIC_config.py` / `JKSliderConfig.py` and/or SliderMC `mc.ini` / `CS` |

Do not invent “Working” claims without a real build. Prefer linking the Technical Manual for long schematics instead of duplicating them.

---

## Chapters

| Topic | Document |
|-------|----------|
| Servos and stepper motors with integrated drivers | [../components/integrated-drivers.md](../components/integrated-drivers.md) |
| MKS SERVO42D/57D over RS485 (no SliderMC) | [../components/mks-servoxx.md](../components/mks-servoxx.md) |
| Stepper motors with external drivers | [../components/external-drivers.md](../components/external-drivers.md) |
| Switches for homing | [../components/homing-switches.md](../components/homing-switches.md) |
| Distinct buttons | [../components/buttons.md](../components/buttons.md) |
| Keypads | [../components/keypads.md](../components/keypads.md) |
| OLED displays | [../components/oled.md](../components/oled.md) |
| RGB LEDs | [../components/rgb-leds.md](../components/rgb-leds.md) |
| Potentiometers | [../components/potentiometers.md](../components/potentiometers.md) |
| Analog joysticks | [../components/joysticks.md](../components/joysticks.md) |
| Camera connections (`CTRL_CAMERA`) | [../components/camera.md](../components/camera.md) |
