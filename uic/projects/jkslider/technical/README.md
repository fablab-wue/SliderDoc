# JKSlider — Technical Manual

![JKSlider](../../../../assets/img/jkslider-hero.png)

**JKSlider V1 by JK**

Configure, wire, and bring up a new JKSlider panel.  
Written for makers who build hardware; you do **not** need to be a programmer.  
Operator use of a finished unit: [../user-manual.md](../user-manual.md).  
Mechanics / motors / power: [../../../../build/hardware-manual.md](../../../../build/hardware-manual.md).  
One-page set card: [../cheat-sheet/cheat-sheet.pdf](../cheat-sheet/cheat-sheet.pdf).  
Axis library details (optional): [../../../api/overview.md](../../../api/overview.md).  
Architecture: [../../../../architecture/overview.md](../../../../architecture/overview.md).

## Why two Picos

JKSlider uses a **UIC** (panel) Pico and a **SliderMC** (motion) Pico linked by UART (a compact **RP2040-Zero** works on either side for smaller designs). The motion board owns STEP/DIR so OLED redraws, keypad scanning, pots, and optional WLAN never steal STEP timing. This project prefers **MicroPython + AsyncIO** on the UIC (Thonny / REPL — DIY-friendly). Full philosophy, pros/cons, and what connects where: [../../../../architecture/overview.md](../../../../architecture/overview.md).

The UIC can be a **handheld wired remote** while the MC stays by the motor driver and PSU — only a **4-wire** cable (**5 V**, **GND**, **TX**, **RX**) between them. Details: [Link — Handheld UIC remote](../../../../contract/link-and-handshake.md#handheld-uic-remote-4-wire-cable).

You will flash **two** boards: MicroPython + project files on the UIC, SliderMC firmware on the motion Pico.

## Sibling repos (UIC + MC)

Clone **SliderCtrl** and **SliderMC** next to each other so relative doc links resolve, for example:

```text
C:\GitHub\SliderCtrl\
C:\GitHub\SliderMC\
```

Documentation for SliderMC firmware lives in [`mc/`](../../../../mc/README.md) — protocol in [`contract/protocol.md`](../../../../contract/protocol.md). See also [BUILD.md](../../../../mc/build.md), [PINS.md](../../../../mc/pins.md), [CONFIG.md](../../../../mc/config.md), [MOTION.md](../../../../mc/motion.md).

## Overview — what you will do

| Step | What | Where |
|------|------|--------|
| 1 | Flash **SliderMC** onto the motion Pico; flash **MicroPython** onto the UIC Pico | [Bring-up](bring-up.md) · MC [BUILD.md](../../../../mc/build.md) |
| 2 | Wire UIC↔MC UART; edit config for **your motor / slider** and **your panel** | [Link](../../../../contract/link-and-handshake.md) · [Bring-up checklist](bring-up.md#checklist--new-motor--slider-sliderconfigpy) · [Config](config.md) |
| 3 | Choose a panel variant; copy UIC project files with **Thonny** | [Panel](panel.md) · [Bring-up](bring-up.md) |
| 4 | Start JKSlider and test motion / STOP / homing | [Bring-up — First test](bring-up.md#7-first-test-run) |

The UIC only runs the files that sit **on that board**. Editing a file on your PC does nothing until you save it **to the UIC** again.

## Getting started with new hardware (short list)

1. Flash MicroPython; install Thonny — [Bring-up](bring-up.md).
2. Fill the **motor / slider checklist** in `UIC_config.py` — [Bring-up checklist](bring-up.md#checklist--new-motor--slider-sliderconfigpy); MC keys: [CONFIG.md](../../../../mc/config.md).
3. Choose a [panel variant](panel.md#configuration-variants); wire pots/buttons or keypad.
4. Copy `SliderPins.example.py` → `SliderPins.py` and edit **that file only** (pins, `JKS_INPUT_MODE`, …) — [Config](config.md).
5. Upload files to the Pico; add `main.py` if you want auto-start — [Bring-up](bring-up.md).
6. First power: unlock (OPTION or STOP if `JKS_BOOT_UNLOCK`) → release stuck keys → homing → test MOVE / STOP / OLED.
7. Hand over [User Manual](../user-manual.md) + [cheat sheet](../cheat-sheet/cheat-sheet.pdf) to the operator.

## Manual map

| Document | Contents |
|----------|----------|
| [link-and-handshake.md](../../../../contract/link-and-handshake.md) | Crossed UART, power/VSYS, session handshake |
| [bring-up.md](bring-up.md) | Thonny, file copy, first test |
| [panel.md](panel.md) | Variants, UIC pinouts, wiring |
| [motion-installer.md](motion-installer.md) | Step rates, sine ramps, TMC STEP/DIR |
| [config.md](config.md) | `SliderPins.py`, defaults modules |
| [user-manual.md](../user-manual.md) | Operator guide |
| [hardware-manual.md](../../../../build/hardware-manual.md) | Rails, motors, power |
| [components/index.md](../../../../components/index.md) | DIY parts catalog |

**Checklists:** [build/checklists/](../../../../build/checklists/README.md)
