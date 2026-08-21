# JKSlider — set-ready motorized camera slider control

![JKSlider](../assets/img/jkslider-hero.png)

**JKSlider V1 by JK** — pro-feel **motorized camera slider** control for the set.  
Open MicroPython panel + dedicated motion firmware. Built to shoot, not to demo.

This page is the **in-docs marketing one-pager** for the JKSlider story. System-wide summaries live in the [SliderDoc README](../README.md); competitive detail in [compare.md](compare.md); code in [SliderCtrl](https://github.com/fablab-wue/SliderCtrl) and [SliderMC](https://github.com/fablab-wue/SliderMC).

---

## DIY project, pro-set manners

You build the rail, motor, and housing. **Slider** gives you open firmware and an on-set workflow designed to compete with expensive commercial motorized sliders on **control feel, safety interlocks, and motion depth** — not on rental-house markup or closed apps.

Feature set and usability target production sets: analogue SPEED / ACCEL, marks and loops, timelapse, DELAY, STOP / EMO, hard-limit homing. **Mechanics quality depends on your build**; the split UIC + MC stack is built so panel I/O never steals STEP timing.

For a side-by-side with commercial units: [compare.md](compare.md).

---

## Set-ready. Maker-built.

**Feel the move** — SPEED & ACCEL under your fingertips. Live retarget. Sine-smooth ramps. Cinema manners, Pico price.

**Mark · Recall · Loop** — Pos A / B / C that stick after power-off. Pair loops for interviews, product, and B-roll that have to match.

**Time your story** — DELAY walk-ins. TIMELAPSE dividers for hyper-smooth long takes.

**Stay in command** — Latched cruise, FAST jog, optional joystick, OPTION modifiers, boot unlock. RGB status plus a choosable **I2C 128×64 OLED** (0.96″ SSD1306, 1.3″ SH1106 / SSH1106 / CH1115–16 clones, or 1.5–2.42″ SSD1309) with the **same UI layout** and optional 180° mount.

---

## Panel projects

Different **faces** on the same motion stack — pick the UIC that fits your shoot and enclosure.

| Project | What you get | Manual |
|---------|--------------|--------|
| **JKSlider** | Full panel — keypad or buttons, SPEED/ACCEL pots, OLED, marks, timelapse, DELAY | [user manual](../uic/projects/jkslider/user-manual.md) |
| **B4Slider** | Minimal 4-button remote — MOVE L/R, SET, OPTION, one SPEED pot; no OLED or timelapse | [user manual](../uic/projects/b4slider/user-manual.md) |
| *More coming* | Custom rigs on `MC_Client` / UART | [project template](../uic/projects/_template/README.md) |

**JKSlider** when you need the full shoot feature set. **B4Slider** when you want the smallest wired remote for slim or budget builds.

Source: [SliderCtrl](https://github.com/fablab-wue/SliderCtrl) (`JKSlider.py`, `B4Slider.py`).

---

## Construction kit

The stack is a **software and electronics construction kit**. Start from a turnkey panel face or compose **`MC_Client`** + **`UIC_Base`** on the UIC Pico; pair with [SliderMC](https://github.com/fablab-wue/SliderMC) for deterministic motion over UART.

**Software:** panel variants, libraries, and open protocol. **Electronics:** two Picos, STEP/DIR driver(s), limits, and a crossed UART link. Your mechanics decide whether the axis becomes a motorized camera slider, mini-dolly, rotating head, turntable, or a **two-axis** rig.

API and composition: [uic/api/overview.md](../uic/api/overview.md) · new panel scaffold: [project template](../uic/projects/_template/README.md).

---

## Optional 2-axis — slider + pan

SliderMC can run a **second** STEP/DIR axis (`axis2_use=1`, reboot). The usual pairing is **axis 1 = linear travel** and **axis 2 = pan** (tilt or turn also work). Dual `MT` / `M` finishes both axes together — **time-synced**, not a CNC diagonal feedrate. Timing: [dual-movement.md](../mc/dual-movement.md).

**JKSlider** and **B4Slider** stay **1-axis operator faces** (they drive and display axis 1). A custom UIC uses [`MC_Client`](https://github.com/fablab-wue/SliderCtrl/blob/main/MC_client.py): `axis_count`, optional `moveTo(pos, pos2)` / `home(2)`, and `set_status2_callback` — see [uic/api/overview.md](../uic/api/overview.md).

---

## DIY. Cost-effective. Maker-friendly.

Upcycle linear units and leftover slider mechanics. Drive **off-the-shelf STEP/DIR steppers** or market servo drivers (A4988, DRV8825, TMC, …). Two open Picos (or compact **RP2040-Zero** boards for smaller designs) — no proprietary black box.

**Split architecture for smooth takes:** [SliderMC](https://github.com/fablab-wue/SliderMC) owns STEP/DIR, homing, and limits; the UIC Pico runs MicroPython + AsyncIO for knobs, buttons, OLED, and camera. The UIC can be a **handheld wired remote** while the MC sits by the driver and PSU — only a **4-wire** cable (**5 V**, **GND**, **TX**, **RX**).

Build the panel you want. Own the toolchain. Ship the shot.

Technical architecture: [overview.md](overview.md).

---

## Create beyond the panel

JKSlider is the turnkey face — the construction kit is for **special-purpose, feature-rich** builds that do not fit a stock panel.

**MC_Client** + **UIC_Base** give you the modular software half: millimetre API over UART to SliderMC, soft/hard limits, EMO, OLED/LED hooks, optional **2-axis** (linear + pan). Strip JKSlider down, fork B4Slider, or script a one-off rig — mini-dolly track, pan head, product turntable, slider + pan, or the next motorized workflow you have in mind.

**MC_Client** + **UIC_Base** + **SliderMC** are the engine; your enclosure and mechanics define the shot.

API entry: [uic/api/overview.md](../uic/api/overview.md).

---

**JKSlider** — set-ready control. Maker-friendly hardware. Creative freedom under the hood.

*JKSlider V1 by JK*

---

Company names and product names mentioned in this project are trademarks or registered trademarks of their respective owners. Use here is for identification only.
