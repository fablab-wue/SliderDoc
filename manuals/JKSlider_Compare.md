# JKSlider vs motorized camera sliders

![JKSlider](../docs/img/jkslider-hero.png)

Competitive scan of commercial and DIY motorized sliders vs **JKSlider V1** (UIC panel + SliderMC motion stack).

**Sources:** product pages and reviews for Accsoon TopRig, Edelkrone, Rhino Arc, Syrp Genie / Magic Carpet, Kessler CineDrive, eMotimo Spectrum, and open projects (DollyDuino, DIY-Machines, QuadMeUp, ardu_slidercontrol). Qualitative — not a lab benchmark.

**Research date:** July 2026. Product lines change quickly; verify current firmware/app features before purchasing decisions.

| | |
|--|--|
| Strong | On-set tactile UX |
| Strong | Safety / limits / EMO |
| Strong | MSM timelapse + shutter (default) |
| Strong | Dedicated motion MCU (UI load isolated) |
| Strong | MicroPython UIC (maker / DIY panel) |
| Gap | Remote + multi-axis |

**Positioning in one line:** JKSlider is a set-first, laptop-free 1-axis controller for upcycled rails — closer in spirit to Accsoon’s onboard panel and eMotimo’s “program on the box” than to Edelkrone’s app ecosystem. It wins on analogue feel, STOP/EMO, open STEP/DIR hardware, and default stop–shoot–move TL; it loses where products sell pan/tilt packages, phone remotes, and turnkey batteries/short ready-made travel.

---

## Feature matrix

Yes / Partial / No relative to typical shipping capability. DIY column = common open projects, not every fork.

| Capability | JKSlider | Accsoon | Edelkrone | Rhino | Syrp | Kessler+ | DIY OSS |
|------------|----------|---------|-----------|-------|------|----------|---------|
| Physical panel (no phone required) | Yes | Yes | Partial | Yes | Partial | Partial | Partial |
| Analogue SPEED + ACCEL knobs | Yes | Partial | No | Partial | No | No | Rare |
| Live retarget while moving | Yes | Partial | Yes | Yes | Partial | Yes | Varies |
| Smooth ramps (S / sine) | Yes | Yes | Yes | Yes | Yes | Yes | Often |
| A/B marks + loop | Yes | Yes | Yes | Yes | Yes | Yes | Often |
| 3+ saved positions (A/B/C) | Yes | No | Yes | Yes | Partial | Yes | Varies |
| Live move ETA / duration dial-in | Yes | Partial | Yes | Yes | Partial | Yes | Varies |
| Walk-in DELAY before move | Yes | No | Partial | Partial | Partial | Yes | Rare |
| Pause / resume mid-move | Yes | Partial | Yes | Yes | Partial | Yes | Varies |
| Soft + hard limits / homing | Yes | Partial | Yes | Yes | Partial | Yes | Often |
| Hardware STOP / EMO interlock | Yes | Partial | Partial | Partial | Partial | Partial | Rare |
| Closed-loop / stall via driver+EMO | Yes | Partial | Yes | Partial | Partial | Yes | Rare |
| True stop–shoot–move timelapse | Yes | Yes | Yes | Yes | Yes | Yes | Often |
| Camera shutter trigger cable | Yes | Yes | Yes | Yes | Yes | Yes | Often |
| Continuous ÷N hyper-slow TL | Yes | Partial | Partial | Partial | Partial | Partial | Varies |
| Phone / app remote | No | Yes | Yes | Yes | Yes | Yes | Often |
| Multi-axis (pan / tilt / focus) | No | Partial | Yes | Yes | Yes | Yes | Often |
| Subject / face tracking | No | Partial | Partial | Yes | Partial | No | Rare |
| Turnkey mechanics + battery pack | No | Yes | Yes | Yes | Yes | Yes | DIY |
| Open firmware / DIY STEP·DIR | Yes | No | No | No | No | No | Yes |
| Dedicated motion MCU (UI isolated) | Yes | No | No | No | No | Partial | Rare |
| Upcycle any rail length | Yes | No | Partial | Partial | Yes | Yes | Yes |

---

## Usability by peer

### Accsoon TopRig S40/S60 — consumer / creator (~mid)

Closest usability rival for “buttons + knob on the rail.” Fast setup, AB loop, app TL with shutter cable, short travel (≈22–42 cm), optional object-tracking pan (~55°).

### Edelkrone SliderONE / PLUS — prosumer ecosystem (high)

Macro-repeatable, app-centric, pairs with HeadONE/PLUS for multi-axis. Reviewers praise precision; criticize setup/battery sprawl vs simple one-box sliders.

### Rhino Motion + Arc II — production B-cam (high)

On-device joysticks + iOS, keyframes, loop interviews, face tracking, real intervalometer. Powerful but multi-box / multi-battery.

### Syrp Magic Carpet + Genie — modular track + motor (mid–high)

Best-in-class manual feel (inertia); Genie adds video/TL presets, bulb ramp, shutter control. Less “panel muscle memory,” more module + app.

### Kessler CineDrive / eMotimo — pro motion control (very high)

Multi-axis keyframes, stop-motion, serious payloads. On-device (eMotimo) or kOS. JKSlider is not competing here on axis count — only on tactile 1-axis set UX.

### Open DIY (DollyDuino, DIY-Machines, QuadMeUp, …) — maker (low)

Often Wi‑Fi/touch/gamepad, 2–3 axes, camera trigger. Weaker than JKSlider on analogue SPEED/ACCEL + STOP/EMO discipline; JKSlider now matches them on shutter MSM, while DIY still leads on remote/Wi‑Fi.

---

## Where JKSlider already leads

### Set muscle memory

Dual pots for SPEED/ACCEL, timed MOVE tap/hold, FAST jog, OPTION chords, A/B/C with power-off memory, DELAY walk-ins and mid-move pause — few consumer sliders match this without opening an app. Accsoon is the nearest with a speed knob + panel; JKSlider goes deeper on modifiers and marks.

**Duration without an app:** at PosA, live ETAs to B/C update as you turn SPEED/ACCEL — dial until the ETA matches the planned shot time, then tap B (see User Manual — *Time a move with SPEED + ETA*).

### Safety & status

Soft limits, hard-limit home, hardware EMO, boot unlock, WDT + LED heartbeat, OLED + RGB status language. Commercial kits often soft-stop or rely on app abort; dedicated EMO + driver disable is uncommon at this price class.

**Closed-loop / stall:** use a market STEP/DIR closed-loop driver and wire its alarm/OC output to `DRV_ERROR` — stall/fault uses the same halt path (Technical Manual). No Pico encoder firmware required.

### Motion manners

Sine (cosine-velocity) ramps, live retarget, DIR settle, TMC-friendly STEP/DIR — cinema-smooth behavior on maker hardware. Accsoon advertises S-curve; Edelkrone/Rhino compete on feel with closed mechanics.

### Maker economics

Open MicroPython, any rail length, any STEP/DIR driver (TMC2208/09, 5160, closed-loop STEP/DIR modules…). Competitors lock you into proprietary motors/apps. Closest OSS peers add Wi‑Fi but rarely match the panel UX.

---

## Missing features (prioritized)

Gaps vs what buyers expect from “motorized camera slider” products and from capable DIY controllers.

| Priority | Missing capability | Why it matters | Who has it |
|----------|--------------------|----------------|------------|
| **P1** | Wireless / app remote | Tight spaces, solo interview B-cam, phone as joystick. Pico W could host BLE/Wi‑Fi later. | Edelkrone app, Accsoon TopRig, Rhino Arc II, Syrp, QuadMeUp ESP32 web UI |
| **P1** | 2nd axis: pan (orbit / tracking) | Interview loop + keep subject framed is a top rental / B-cam ask. | Accsoon 55° pan, Rhino Arc, Edelkrone HeadONE/PLUS, DollyDuino orbit |
| **P2** | More keyframes / path edit | A/B/C is strong for set work; VFX/macro wants 5+ keyframes and ease per segment. | Rhino Arc II (5 KF), Edelkrone, Kessler CineDrive, ESP32 3-axis DIY |
| **P2** | Incline / vertical mode + holding torque UX | Safety when hand-control or power loss could back-drive. | Edelkrone SliderONE v3, Kessler worm drives, Accsoon vertical rating |
| **P3** | Turnkey battery + mechanics SKU | Product gap vs controller-only positioning — not a firmware gap. | Accsoon NP-F kits, Rhino/Syrp/Edelkrone complete systems |

### TIMELAPSE modes (shipped)

- **MSM** (default; `JKS_TL_MODE` / saved `tl_mode`): stop → shutter → exposure → hop → settle; interval = N/FPS; hop sized with `estimateMoveTime`. Toggle with `T`+`D`+`*`.
- **Cont** (`continuous`): SPEED/ACCEL ÷ N; `CTRL_CAMERA` hold-high like video (match camera TL to slider TL).
- **×1**: video hold-high while moving / soft-paused; low when idle.

---

## Suggested roadmap

### P1 — Reach

Pico W BLE or simple web remote · optional 2nd STEP/DIR for pan.

### P2+ — Pro polish

More keyframes · incline hold UX · packaged NP-F power notes in Hardware Manual.

---

## Bottom line

**Against Accsoon TopRig:** JKSlider is more flexible mechanically and richer as a set panel, with onboard MSM + shutter; Accsoon wins as a finished short slider with app remote + pan assist.

**Against Edelkrone / Rhino / Syrp / Kessler:** those are multi-axis motion products; JKSlider should not chase full MoCo — keep owning tactile 1-axis control, open hardware, and MSM, then add a light remote / pan option.

**Against DIY OSS:** JKSlider already looks more “rental desk” as a set panel and ships shutter MSM; the UIC↔MC split isolates UI load from STEP timing (many single-MCU DIY projects do not). Wi‑Fi/remote remains the main DIY advantage to close next.

---

Company names and product names mentioned in this project are trademarks or registered trademarks of their respective owners. Use here is for identification only.
