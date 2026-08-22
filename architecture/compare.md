<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "JKSlider vs motorized camera sliders";
  --doc-path: ".\\SliderDoc\\architecture\\compare.md";
}
</style>

# JKSlider vs motorized camera sliders

![JKSlider](../assets/img/jkslider-hero.png)

Competitive scan of commercial and DIY motorized sliders vs **JKSlider V1** (UIC panel + SliderMC motion stack).

**Sources:** product pages and reviews for Accsoon TopRig, Edelkrone, Rhino Arc, Syrp Genie / Magic Carpet, Kessler CineDrive, eMotimo Spectrum, iFootage Shark Slider Nano 2 / Pico Pro, Neewer ER1, GVM Slider-80 / GP-120QD, Zeapon AXIS, and open projects (DollyDuino, DIY-Machines, QuadMeUp, ardu_slidercontrol). Qualitative — not a lab benchmark. Typical USD bands are street/MSRP snapshots, not a quote.

**Research date:** August 2026. Product lines change quickly; verify current firmware/app features before purchasing decisions.

| | |
|--|--|
| Strong | On-set tactile UX |
| Strong | Safety / limits / EMO |
| Strong | MSM timelapse + shutter (default) |
| Strong | Dedicated motion MCU (UI load isolated) |
| Strong | MicroPython UIC (maker / DIY panel) |
| Gap | Remote; panel still primarily 1-axis |

**Positioning in one line:** JKSlider is a set-first, laptop-free controller for upcycled rails — closer in spirit to Accsoon’s onboard panel and eMotimo’s “program on the box” than to Edelkrone’s app ecosystem. It wins on analogue feel, STOP/EMO, open STEP/DIR hardware, and default stop–shoot–move TL. SliderMC can optionally drive a **2nd STEP/DIR axis** (`axis2_use` on Pico or Zero); shipping JKSlider/B4Slider panels remain primarily **1-axis** UX. It loses where products sell full pan/tilt packages, phone remotes, and turnkey batteries/short ready-made travel.

---

## Feature matrix

**✔** = typical shipping capability; (**✓**) = limited / accessory / app-only; **-** = not typical. DIY column = common open projects, not every fork.

| Capability | JKSlider | Accsoon / TopRig | Edelkrone | Rhino | Syrp | Kessler+ | DIY OSS | Nano 2 | Pico Pro | Neewer | GVM | Zeapon |
|:-----------|:--------:|:----------------:|:---------:|:-----:|:----:|:--------:|:-------:|:------:|:--------:|:------:|:---:|:------:|
| Physical panel (no phone required) | **✔** | **✔** | (**✓**) | **✔** | (**✓**) | (**✓**) | (**✓**) | **✔** | **✔** | (**✓**) | (**✓**) | **✔** |
| Analogue SPEED + ACCEL knobs | **✔** | (**✓**) | - | (**✓**) | - | - | - | (**✓**) | (**✓**) | - | - | (**✓**) |
| Live retarget while moving | **✔** | (**✓**) | **✔** | **✔** | (**✓**) | **✔** | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) | **✔** |
| Smooth ramps (S / sine) | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** |
| A/B marks + loop | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** |
| 3+ saved positions (A/B/C) | **✔** | - | **✔** | **✔** | (**✓**) | **✔** | (**✓**) | **✔** | **✔** | - | - | (**✓**) |
| Live move ETA / duration dial-in | **✔** | (**✓**) | **✔** | **✔** | (**✓**) | **✔** | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) |
| Walk-in DELAY before move | **✔** | - | (**✓**) | (**✓**) | (**✓**) | **✔** | - | - | - | (**✓**) | (**✓**) | (**✓**) |
| Pause / resume mid-move | **✔** | (**✓**) | **✔** | **✔** | (**✓**) | **✔** | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) | **✔** |
| Soft + hard limits / homing | **✔** | (**✓**) | **✔** | **✔** | (**✓**) | **✔** | **✔** | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) |
| Hardware STOP / EMO interlock | **✔** | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) | - | - | - | - | - | (**✓**) |
| Closed-loop / stall via driver+EMO | **✔** | (**✓**) | **✔** | (**✓**) | (**✓**) | **✔** | - | (**✓**) | - | - | - | - |
| True stop–shoot–move timelapse | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** |
| Camera shutter trigger cable | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | (**✓**) | **✔** | **✔** | (**✓**) |
| Continuous ÷N hyper-slow TL | **✔** | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) | (**✓**) |
| Phone / app remote | - | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** |
| Multi-axis (pan / tilt / focus) | (**✓**) | (**✓**) | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | **✔** | (**✓**) | (**✓**) | **✔** |
| Subject / face tracking | - | (**✓**) | (**✓**) | **✔** | (**✓**) | - | - | **✔** | (**✓**) | (**✓**) | (**✓**) | (**✓**) |
| Turnkey mechanics | - | **✔** | **✔** | **✔** | **✔** | **✔** | (**✓**) | **✔** | **✔** | **✔** | **✔** | **✔** |
| Battery pack | - | **✔** | (**✓**) | **✔** | **✔** | (**✓**) | - | (**✓**) | **✔** | **✔** | **✔** | (**✓**) |
| Open firmware / DIY STEP·DIR | **✔** | - | - | - | - | - | **✔** | - | - | - | - | - |
| Dedicated motion MCU (UI isolated) | **✔** | - | - | - | - | (**✓**) | - | - | - | - | - | - |
| Upcycle any rail length | **✔** | - | (**✓**) | (**✓**) | **✔** | **✔** | **✔** | - | - | - | - | - |

---

## Kit snapshot (Aug 2026)

Street/MSRP bands. JKSlider has no SKU (controller + upcycled rail).

| Product | Maker | Travel / sizes | Payload | Control | Power | Weight | Notes | Typical USD |
|:--------|:-----:|:--------------:|:-------:|:-------:|:-----:|:------:|:-----:|:-----------:|
| [TopRig S40 / S60](https://accsoon.com/toprig-s40-s60/) | [Accsoon](https://accsoon.com/) | 225 / 425 mm (body 410 / 610 mm) | 4 kg horiz / 2.5 kg vert | Onboard buttons + speed knob + BT app | NP-F or DC 9–16.8 V (~60 h claimed on NP-F550) | 1.4 / 1.5 kg | Brushless S-curve; 0.1–5 cm/s; 55° tracking pan | USD 320–500 (MSRP often 349 / 399) |
| [SliderONE v3](https://edelkrone.com/products/sliderone) | [Edelkrone](https://edelkrone.com/) | 20 cm (270×95×50 mm) | ~9 kg horiz / 1.8 kg vert | App / watch / hand-pose; pairs HeadONE / HeadPLUS | LP-E6 (not included) | 1.1 kg | Macro-repeatable; TapMove coming | USD 380–550 (MSRP 549); + HeadONE from ~449 |
| [SliderPLUS v5](https://edelkrone.com/products/sliderplus) (EOL) / v6 | [Edelkrone](https://edelkrone.com/) | Compact / Long dual-length rails | Prosumer / cinema (varies by PRO) | App + Motor Module | Battery modules extra | Rail-only | v5 rail+motor ~USD 800–1100; v6 rail from ~890; HeadPLUS v3 from ~1890 | Motorized PLUS ~USD 800–1500 |
| [Arc II](https://rhinocameragear.eu/rhino-arc-v2/) + Slider | [Rhino](https://rhinocameragear.eu/) (US store closed) | 24″ / 42″ rails typical | Head ~15 lb pan/tilt | Joysticks + iOS; face tracking | Internal 4400 mAh + extra packs | Multi-box | Leftover dealer stock; Ultimate 4-axis bundle | Head ~USD 1400; bundle 1400–3600 (MSRP ~3650) |
| [Genie II Linear](https://www.manfrotto.com/global-en/genie-ii-linear-sy0038-0003/) + Magic Carpet | [Syrp](https://www.manfrotto.com/) (Manfrotto) | Carpet ~2.6–5.2 ft | Linear ~7.5 kg horiz / ~5 kg vert (kit-dep.) | Joystick + Genie 2 app | Removable pack | Motor + track | Rope drive; Mini II pan ~USD 280; 3-axis kits historically ~1.7k–2.2k | Motor USD 500–1100 (MSRP ~1110) + track 330–470 |
| [CineDrive](https://kesslercrane.com/collections/cinedrive) | [Kessler](https://kesslercrane.com/) | CineSlider rail often ~3–5 ft | Motor series 7.5–50+ lb vert | kOS / Brain | Modular 12 V | Modular | Brain USD 1524 + slider motor 528 + rail ~1400; pan/tilt head 4840 | 1-axis ~USD 2k–4k; 3-axis 6k+ |
| [Spectrum ST4](https://emotimo.com/products/st4) | [eMotimo](https://emotimo.com/) | Head (add slider) | 15 lb | Onboard + gamepad | V-mount / Gold Mount | ~4.5 lb head | 4-axis; ST4.3 up to 7-axis with Nucleus | USD 2100–3300; Run and Gun ~4450 |
| DollyDuino, DIY-Machines, QuadMeUp, … | various | Any rail | Build-dep. | Wi-Fi / touch / gamepad | DIY pack | DIY | Open firmware; usually one MCU | Electronics USD 50–400 + rail |
| [Shark Slider Nano 2](https://www.ifootagegear.com/products/shark-slider-nano2) 660 / 860 | [iFootage](https://www.ifootagegear.com/) | 433 / 633 mm | 7 / 5 kg horiz; 3.5 / 2.5 kg vert | IPS/OLED + Moco app; 8 keyframes | PD 60 W or NP-F 60 W+ | 2.96 / 3.47 kg | Al+CF; 5 modes; DJI RS2–RS5 5-axis when paired; slide ~1 µm/s–140 mm/s | USD 500–700 (MSRP 699) |
| [Shark Slider Pico Pro](https://www.ifootagegear.com/products/shark-slider-pico) | [iFootage](https://www.ifootagegear.com/) | 255 mm (400×91×52 mm) | 1.5 kg horiz / 0.8 kg vert | LCD; NFC/BT/Apple Watch | Built-in 5000 mAh (~7 h horiz); PD 3.0 | 0.82 kg | Phone / Pocket 3/4 / Action 5/6; 360° pan; Pico non-Pro ~USD 199 | USD 240–300 (often 299) |
| [ER1](https://neewer.com/products/neewer-er1-motorized-carbon-fiber-camera-slider-with-f750-battery-66607157) 80 / 100 / 120 | [Neewer](https://neewer.com/) | 80 / 100 / 120 cm rail | 5 kg horiz / 2.5 kg at 45° | App + 2.4G remote (~8–10 m) | NP-F750 4400 mAh or USB-C 5 V 2 A | ~2.4–2.8 kg | A/B loop; TL; 120° mechanical pan knobs; CF+Al | USD 250–400 |
| [Slider-80](https://gvmled.com/gvm-slider80/) (also GP-120QD ~48″) | [GVM](https://gvmled.com/) | 80 cm class (~116 cm travel on GP-120QD) | ~5 kg horiz / 2.5 kg at 45° | Bluetooth app and/or remote | NP-F | Kit ~2–3 kg slider | Same kit class as ER1; ball head; shutter cables; 120° pan | USD 240–350 (B&H Slider-80 ~259) |
| [AXIS](https://www.zeapon.com/product/axis-multi-axis-motorized-slider/) 80 / 100 / 120 | [Zeapon](https://www.zeapon.com/) | Travel ~600 / 800 / 1000 mm | ~12 kg horiz / 3.5 kg vert | LCD + speed knobs + app | NP-F + USB-C PD | 4.2–4.7 kg (Pro 5.4–5.9 kg) | 11-layer CF; integrated pan; Pro + PONS tilt | USD 600–1000 (2-axis); ~850–1200 (Pro) |

---

## Usability by peer

### Accsoon TopRig S40/S60 — consumer / creator (~USD 320–500)

Closest usability rival for “buttons + knob on the rail.” Fast setup, AB loop, app TL with shutter cable, short travel (≈22–42 cm; S40 is very short), optional object-tracking pan (~55°). Typical street **USD 320–500** (MSRP often USD 349 / USD 399).

### Edelkrone SliderONE / PLUS — prosumer ecosystem (~USD 380–1500 slide; heads extra)

Macro-repeatable, app-centric, pairs with HeadONE/PLUS for multi-axis. SliderONE v3 is about **USD 380–550** (MSRP USD 549); HeadONE v2 from ~USD 449. PLUS is the longer/pricier stack (v5 rail+motor EOL ~USD 800–1100; v6 rail from ~USD 890). Reviewers praise precision; criticize setup/battery sprawl vs simple one-box sliders.

### Rhino Motion + Arc II — production B-cam (leftover ~USD 1400–3600)

On-device joysticks + iOS, keyframes, loop interviews, face tracking, real intervalometer. Powerful but multi-box / multi-battery. The **US maker store is closed**; leftover dealers still list the Arc II head (~USD 1400) and Ultimate bundles (MSRP ~USD 3650, sales seen ~USD 2000). Typical leftover **USD 1400–3600**.

### Syrp Magic Carpet + Genie — modular track + motor (~USD 500–1100 motor + track)

Best-in-class manual feel (inertia); Genie adds video/TL presets, bulb ramp, shutter control. Less “panel muscle memory,” more module + app. Genie II Linear **~USD 500–1100** (MSRP ~USD 1110, clearance lower) plus Carpet track **USD 330–470**; 3-axis kits historically **~USD 1.7k–2.2k**.

### Kessler CineDrive / eMotimo — pro motion control (very high)

Multi-axis keyframes, stop-motion, serious payloads. On-device (eMotimo) or kOS. CineDrive 1-axis slide **~USD 2k–4k**, pan/tilt **USD 6k+**. Spectrum ST4 head **~USD 2.1k–3.3k**. JKSlider is not competing here on axis count — only on tactile 1-axis set UX.

### iFootage Shark Slider Nano 2 — creator / DJI RS (~USD 500–700)

OLED/touch + Moco app, up to 8 keyframes, AI face/object tracking, five shoot modes. Strongest when locked to DJI RS (5-axis); alone it is slide + pan on a short carbon rail. Not a tactile SPEED/ACCEL/EMO panel. Typical **USD 500–700** (MSRP USD 699).

### iFootage Shark Slider Pico Pro — bag / phone (~USD 240–300)

255 mm travel for phone, DJI Pocket / Action, and light mirrorless. Dual-axis slide + 360° pan, built-in pack, NFC/Bluetooth. Not a DSLR rail replacement. Typical **USD 240–300** (often USD 299; Pico non-Pro ~USD 199).

### Neewer ER1 — budget CF kit (~USD 250–400)

Cheap complete kit (NP-F, TL, shutter cables, A/B loop). App / 2.4G remote first; analogue knobs, EMO, 3 marks, and live ETA are weak vs JKSlider. 80 / 100 / 120 cm rails. Typical **USD 250–400**.

### GVM Slider-80 — budget CF kit (~USD 240–350)

Same OEM-class kit as ER1 (do not treat them as different architectures): CF tubes, NP-F, A/B, Bluetooth app and/or remote, 120° mechanical pan, ball head. Typical **USD 240–350** (B&H Slider-80 ~USD 259). GP-120QD is the longer 48″ sibling.

### Zeapon AXIS — 2-axis bag slider (~USD 600–1200)

Fastest “bag to 2-axis” of this list: LCD + speed knobs on the box, integrated pan, 80 / 100 / 120 cm carbon. Pro adds PONS tilt toward Edelkrone/Rhino capability without Kessler money. Typical **USD 600–1000** (2-axis) / **~USD 850–1200** (Pro).

### Open DIY (DollyDuino, DIY-Machines, QuadMeUp, …) — maker (~USD 50–400 electronics)

Often Wi‑Fi/touch/gamepad, 2–3 axes, camera trigger. Weaker than JKSlider on analogue SPEED/ACCEL + STOP/EMO discipline; JKSlider now matches them on shutter MSM, while DIY still leads on remote/Wi‑Fi. Electronics typically **USD 50–400** plus a rail.

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
| **P1** | Wireless / app remote | Tight spaces, solo interview B-cam, phone as joystick. Pico W could host BLE/Wi‑Fi later. | Edelkrone app, Accsoon TopRig, iFootage Moco (Nano 2 / Pico Pro), Neewer / GVM apps, Zeapon app, Rhino Arc II, Syrp, QuadMeUp ESP32 web UI |
| **P1** | Dual-axis **panel** UX (pan orbit / tracking) | SliderMC optional 2nd STEP/DIR (`axis2_use`) is available; JKSlider/B4Slider still drive primarily one axis. | Accsoon 55° pan, Zeapon AXIS (pan / Pro tilt), Nano 2 + DJI RS, Pico Pro 360° pan, Rhino Arc, Edelkrone HeadONE/PLUS, DollyDuino orbit |
| **P2** | More keyframes / path edit | A/B/C is strong for set work; VFX/macro wants 5+ keyframes and ease per segment. | Nano 2 (8 points), Rhino Arc II (5 KF), Edelkrone, Kessler CineDrive, ESP32 3-axis DIY |
| **P2** | Incline / vertical mode + holding torque UX | Safety when hand-control or power loss could back-drive. | Edelkrone SliderONE v3, Kessler worm drives, Accsoon vertical rating, Zeapon / Nano 2 vertical payload ratings |
| **P3** | Turnkey battery + mechanics SKU | Product gap vs controller-only positioning — not a firmware gap. | Accsoon NP-F kits, Pico Pro built-in pack, Neewer / GVM NP-F kits, Nano 2 PD/NP-F, Rhino/Syrp/Edelkrone/Zeapon complete systems |

### TIMELAPSE modes (shipped)

- **MSM** (default; `JKS_TL_MODE` / saved `tl_mode`): stop → shutter → exposure → hop → settle; interval = N/FPS; hop sized with `estimateMoveTime`. Toggle with `T`+`D`+`*`.
- **Cont** (`continuous`): SPEED/ACCEL ÷ N; `CTRL_CAMERA` hold-high like video (match camera TL to slider TL).
- **×1**: video hold-high while moving / soft-paused; low when idle.

---

## Suggested roadmap

### P1 — Reach

Pico W BLE or simple web remote · dual-axis panel UX on top of SliderMC `axis2_use`.

### P2+ — Pro polish

More keyframes · incline hold UX · packaged NP-F power notes in Hardware Manual.

---

## Bottom line

**Against Accsoon TopRig:** JKSlider is more flexible mechanically and richer as a set panel, with onboard MSM + shutter; Accsoon wins as a finished short slider with app remote + pan assist (~USD 320–500).

**Against iFootage Nano 2 / Pico Pro:** Nano 2 wins as a DJI-RS tracking box with 8 keyframes (~USD 500–700); Pico Pro wins as a bag slider for phone/Pocket (~USD 240–300). JKSlider wins on analogue SPEED/ACCEL, STOP/EMO, and any-length rails.

**Against Neewer ER1 / GVM Slider-80:** those are the cheap complete CF kits (~USD 240–400) with app A/B and TL. JKSlider is the set panel and open STEP/DIR stack, not a USD 300 Amazon rail.

**Against Zeapon AXIS:** AXIS is the fastest bag-to-2-axis carbon slider (~USD 600–1200). JKSlider should not chase a motorized pan head — keep owning tactile 1-axis control; SliderMC `axis2_use` is the path if a light pan face is needed.

**Against Edelkrone / Rhino / Syrp / Kessler:** those are multi-axis motion products; JKSlider should not chase full MoCo — keep owning tactile control, open hardware, and MSM. SliderMC already supports an optional 2nd STEP/DIR; next reach is a light remote / dual-axis panel UX.

**Against DIY OSS:** JKSlider already looks more “rental desk” as a set panel and ships shutter MSM; the UIC↔MC split isolates UI load from STEP timing (many single-MCU DIY projects do not). Wi‑Fi/remote remains the main DIY advantage to close next.

---

Company names and product names mentioned in this project are trademarks or registered trademarks of their respective owners. Use here is for identification only.
