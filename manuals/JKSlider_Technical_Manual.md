# JKSlider — Technical Manual

![JKSlider](../docs/img/jkslider-hero.png)

**JKSlider V1 by JK**

Configure, wire, and bring up a new JKSlider panel.  
Written for makers who build hardware; you do **not** need to be a programmer.  
Operator use of a finished unit: [JKSlider_User_Manual.md](JKSlider_User_Manual.md).  
Mechanics / motors / power: [JKSlider_Hardware_Manual.md](JKSlider_Hardware_Manual.md).  
One-page set card: [JKSlider_Cheat_Sheet.pdf](JKSlider_Cheat_Sheet.pdf).  
Axis library details (optional): [docs/API.md](../docs/API.md).  
Architecture: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## Why two Picos

JKSlider uses a **UIC** (panel) Pico and a **SliderMC** (motion) Pico linked by UART (a compact **RP2040-Zero** works on either side for smaller designs). The motion board owns STEP/DIR so OLED redraws, keypad scanning, pots, and optional WLAN never steal STEP timing. This project prefers **MicroPython + AsyncIO** on the UIC (Thonny / REPL — DIY-friendly). Full philosophy, pros/cons, and what connects where: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

The UIC can be a **handheld wired remote** while the MC stays by the motor driver and PSU — only a **4-wire** cable (**5 V**, **GND**, **TX**, **RX**) between them. Details: [Link — Handheld UIC remote](JKSlider_Technical_Manual_Link.md#handheld-uic-remote-4-wire-cable).

You will flash **two** boards: MicroPython + project files on the UIC, SliderMC firmware on the motion Pico.

## Sibling repos (UIC + MC)

Clone **SliderCtrl** and **SliderMC** next to each other so relative doc links resolve, for example:

```text
C:\GitHub\SliderCtrl\
C:\GitHub\SliderMC\
```

From this `manuals/` folder, MC docs are `../../SliderMC/docs/…` — start at [SliderMC docs README](../../SliderMC/docs/README.md), [PROTOCOL.md](../../SliderMC/docs/PROTOCOL.md) (incl. [Commands](../../SliderMC/docs/PROTOCOL.md#commands)), [BUILD.md](../../SliderMC/docs/BUILD.md), [PINS.md](../../SliderMC/docs/PINS.md), [CONFIG.md](../../SliderMC/docs/CONFIG.md), [MOTION.md](../../SliderMC/docs/MOTION.md).

## Overview — what you will do

| Step | What | Where |
|------|------|--------|
| 1 | Flash **SliderMC** onto the motion Pico; flash **MicroPython** onto the UIC Pico | [Bring-up](JKSlider_Technical_Manual_BringUp.md) · MC [BUILD.md](../../SliderMC/docs/BUILD.md) |
| 2 | Wire UIC↔MC UART; edit config for **your motor / slider** and **your panel** | [Link](JKSlider_Technical_Manual_Link.md) · [Bring-up checklist](JKSlider_Technical_Manual_BringUp.md#checklist--new-motor--slider-sliderconfigpy) · [Config](JKSlider_Technical_Manual_Config.md) |
| 3 | Choose a panel variant; copy UIC project files with **Thonny** | [Panel](JKSlider_Technical_Manual_Panel.md) · [Bring-up](JKSlider_Technical_Manual_BringUp.md) |
| 4 | Start JKSlider and test motion / STOP / homing | [Bring-up — First test](JKSlider_Technical_Manual_BringUp.md#7-first-test-run) |

The UIC only runs the files that sit **on that board**. Editing a file on your PC does nothing until you save it **to the UIC** again.

## Getting started with new hardware (short list)

1. Flash MicroPython; install Thonny — [Bring-up](JKSlider_Technical_Manual_BringUp.md).
2. Fill the **motor / slider checklist** in `UIC_config.py` — [Bring-up checklist](JKSlider_Technical_Manual_BringUp.md#checklist--new-motor--slider-sliderconfigpy); MC keys: [CONFIG.md](../../SliderMC/docs/CONFIG.md).
3. Choose a [panel variant](JKSlider_Technical_Manual_Panel.md#configuration-variants); wire pots/buttons or keypad.
4. Copy `SliderPins.example.py` → `SliderPins.py` and edit **that file only** (pins, `JKS_INPUT_MODE`, …) — [Config](JKSlider_Technical_Manual_Config.md).
5. Upload files to the Pico; add `main.py` if you want auto-start — [Bring-up](JKSlider_Technical_Manual_BringUp.md).
6. First power: unlock (OPTION or STOP if `JKS_BOOT_UNLOCK`) → release stuck keys → homing → test MOVE / STOP / OLED.
7. Hand over [User Manual](JKSlider_User_Manual.md) + [cheat sheet](JKSlider_Cheat_Sheet.pdf) to the operator.

## Manual map

| Document | Contents |
|----------|----------|
| [JKSlider_Technical_Manual_Link.md](JKSlider_Technical_Manual_Link.md) | Crossed UART, power/VSYS, session handshake (`\n` → banner) |
| [JKSlider_Technical_Manual_BringUp.md](JKSlider_Technical_Manual_BringUp.md) | Thonny, file copy, first test, `UIC_config` motor checklist |
| [JKSlider_Technical_Manual_Panel.md](JKSlider_Technical_Manual_Panel.md) | Variants, UIC pinouts, button/keypad/pots/RGB/camera wiring |
| [JKSlider_Technical_Manual_Motion.md](JKSlider_Technical_Manual_Motion.md) | Step rates, sine ramps, TMC STEP/DIR, DRV_ERROR |
| [JKSlider_Technical_Manual_Config.md](JKSlider_Technical_Manual_Config.md) | `SliderPins.py` (one file per HW), defaults modules, OLED/LED notes |
| [JKSlider_User_Manual.md](JKSlider_User_Manual.md) | Operator — knobs, chords, OLED/LED meanings |
| [JKSlider_Hardware_Manual.md](JKSlider_Hardware_Manual.md) | Rails, motors, mounting, power, housings |
| [JKSlider_Components.md](JKSlider_Components.md) | DIY parts catalog (tested modules) |
