# JKSlider

![JKSlider](../docs/img/jkslider-hero.png)

**JKSlider V1 by JK** — pro-feel motorized camera slider control for the set.  
Plug-and-play panel experience. Open MicroPython stack. Built to shoot, not to demo.

**Easy on set. Ready for every take.** Analogue knobs, muscle-memory buttons, soft limits, hard-limit home, STOP / EMO — the checklist a real production needs, without a laptop in the shot.

---

## Set-ready. Maker-built.

**Feel the move** — SPEED & ACCEL under your fingertips. Live retarget. Sine-smooth ramps. Cinema manners, Pico price.

**Mark · Recall · Loop** — Pos A / B / C that stick after power-off. Pair loops for interviews, product, and B-roll that have to match.

**Time your story** — DELAY walk-ins. TIMELAPSE dividers for hyper-smooth long takes.

**Stay in command** — Latched cruise, FAST jog, optional joystick, OPTION modifiers, boot unlock. RGB status plus a choosable **I2C 128×64 OLED** (0.96″ SSD1306, 1.3″ SH1106 / SSH1106 / CH1115–16 clones, or 1.5–2.42″ SSD1309) with the **same UI layout** and optional 180° mount.

---

## DIY. Cost-effective. Maker-friendly.

Upcycle linear units and leftover slider mechanics. Drive **off-the-shelf STEP/DIR steppers** or market servo drivers (A4988, DRV8825, TMC, …). Two open Picos (or compact **RP2040-Zero** boards for smaller designs) — no proprietary black box, no rental-house markup.

**Split architecture for smooth takes:** a dedicated **SliderMC** motion Pico owns STEP/DIR; the **UIC** panel Pico runs MicroPython + AsyncIO for knobs, buttons, OLED, and camera. Display redraws and keypad scans never steal motion timing. Prefer Pico + MicroPython for the panel (or a compact **RP2040-Zero** for smaller handheld remotes); fork the UART client onto another host if you want. The UIC can be a **handheld wired remote** while the MC sits by the driver and PSU — only a **4-wire** cable (**5 V**, **GND**, **TX**, **RX**).

Build the panel you want. Own the toolchain. Ship the shot.

Architecture: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

---

## Create beyond the panel

**MC_Client** + **UIC_Base** — the UIC libraries under JKSlider — are yours for custom control projects: millimetre API over UART to SliderMC, soft/hard limits, EMO, OLED/LED hooks. Prototype a new UI, script a rig, invent the next slider workflow.

JKSlider is the turnkey face. **MC_Client** + **UIC_Base** + **SliderMC** are the engine for makers who build their own.

---

**JKSlider** — set-ready control. Maker-friendly hardware. Creative freedom under the hood.

*JKSlider V1 by JK*

---

Company names and product names mentioned in this project are trademarks or registered trademarks of their respective owners. Use here is for identification only.
