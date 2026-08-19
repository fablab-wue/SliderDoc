# JKSlider — Components

![JKSlider](../docs/img/jkslider-hero.png)

**JKSlider V1 by JK**

This is a **living catalog of hardware that DIY users have run with JKSlider** — either **tested and working** or documented **problems**. When you validate a new part, update the matching chapter with pins, pinouts, schematics, photos, manufacturer links, and the exact config changes needed.

JKSlider is a **UIC + SliderMC** split: panel I/O on the UIC Pico, motion axis on the motion Pico. Overview: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) · [architecture SVG](../docs/img/architecture_overview.svg).

**Which board?**

| Board | Typical components |
|-------|-------------------|
| **UIC** | Buttons, keypad, OLED, RGB/NeoPixel, pots, joystick, camera shutter |
| **SliderMC** | Motor / STEP·DIR driver, home switch, hard limits, Ext, DRV_ERROR |

SliderMC pins: [PINS.md](../../SliderMC/docs/PINS.md) · [pico_pinout_mc.png](../../SliderMC/docs/img/pico_pinout_mc.png) · [CONFIG.md](../../SliderMC/docs/CONFIG.md)

Installer wiring and firmware: [JKSlider_Technical_Manual.md](JKSlider_Technical_Manual.md) ([Panel](JKSlider_Technical_Manual_Panel.md), [Motion](JKSlider_Technical_Manual_Motion.md)).  
MC protocol (sibling clone): [PROTOCOL.md](../../SliderMC/docs/PROTOCOL.md).  
Mechanics / power / housings: [JKSlider_Hardware_Manual.md](JKSlider_Hardware_Manual.md).  
Operator panel behaviour: [JKSlider_User_Manual.md](JKSlider_User_Manual.md).

**Photos:** put all component product photos under [`docs/img/components/`](../docs/img/components/). Shared diagrams (Pico pinouts, silk map, OLED mockups) may stay under `docs/img/` and be linked from entries.

---

## How to add a component

Copy this block into the matching chapter file:

| Field | Content |
|-------|---------|
| **Name** | Short product / module name |
| **Status** | `Working` / `Issues` / `Untested` + one-line note |
| **Photos** | `../docs/img/components/...` |
| **Pins** | Board (**UIC** or **SliderMC**) + net names + GP# (and connector pin order if any) |
| **Schematic / pinout** | ASCII and/or image embeds |
| **Manufacturer** | Shop / datasheet links |
| **Config** | Exact symbols in `UIC_config.py` / `JKSliderConfig.py` and/or SliderMC `mc.ini` / `CS` |

Do not invent “Working” claims without a real build. Prefer linking the Technical Manual for long schematics instead of duplicating them.

---

## Chapters

| Topic | Document |
|-------|----------|
| Servos and stepper motors with integrated drivers | [JKSlider_Components_Integrated_Drivers.md](JKSlider_Components_Integrated_Drivers.md) |
| MKS SERVO42D/57D over RS485 (no SliderMC) | [JKSlider_Components_MKS_SERVOxx.md](JKSlider_Components_MKS_SERVOxx.md) |
| Stepper motors with external drivers | [JKSlider_Components_External_Drivers.md](JKSlider_Components_External_Drivers.md) |
| Switches for homing | [JKSlider_Components_Homing_Switches.md](JKSlider_Components_Homing_Switches.md) |
| Distinct buttons | [JKSlider_Components_Buttons.md](JKSlider_Components_Buttons.md) |
| Keypads | [JKSlider_Components_KeyPads.md](JKSlider_Components_KeyPads.md) |
| OLED displays | [JKSlider_Components_OLED.md](JKSlider_Components_OLED.md) |
| RGB LEDs | [JKSlider_Components_RGB_LEDs.md](JKSlider_Components_RGB_LEDs.md) |
| Potentiometers | [JKSlider_Components_Potentiometers.md](JKSlider_Components_Potentiometers.md) |
| Analog joysticks | [JKSlider_Components_JoySticks.md](JKSlider_Components_JoySticks.md) |
| Camera connections (`CTRL_CAMERA`) | [JKSlider_Components_Camera.md](JKSlider_Components_Camera.md) |
