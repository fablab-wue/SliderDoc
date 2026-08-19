# JKSlider — Hardware Manual

![JKSlider](../docs/img/jkslider-hero.png)

**JKSlider V1 by JK**

Mechanics, motors, mounting, and power — choosing parts for a motorized camera slider that JKSlider / SliderCtrl can drive.  
Panel wiring and firmware config: [JKSlider_Technical_Manual.md](JKSlider_Technical_Manual.md) ([Bring-up](JKSlider_Technical_Manual_BringUp.md), [Panel](JKSlider_Technical_Manual_Panel.md), [Motion](JKSlider_Technical_Manual_Motion.md)).  
On-set operation: [JKSlider_User_Manual.md](JKSlider_User_Manual.md).  
Electronics architecture (UIC + SliderMC): [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

JKSlider expects a **STEP / DIR** (+ usually **EN**) axis on the **motion Pico** (SliderMC). Almost any linear stage that accepts that interface can become a shooting tool. Plan for **two boards**, shared signal ground, and either a stacked pair or a **4-wire remote cable** (**5 V**, **GND**, **TX**, **RX** — GP16/17 crossed) so the UIC can sit in hand while the MC stays with the driver and PSU. Link details: [Technical Manual — Link](JKSlider_Technical_Manual_Link.md#handheld-uic-remote-4-wire-cable).

---

## Choosing the linear unit

The carriage must move smoothly under camera weight without stick-slip. Three common paths:

| Approach | Character | Notes |
|----------|-----------|--------|
| **Industrial high-end** | Quiet, stiff, long life | Recirculating ball rails, profiled linear guides (HIWIN-class, Bosch Rexroth, …). Best for heavy cameras and long travel; budget and weight go up. |
| **Steel rods + ball bearings** | Classic DIY / workshop | Parallel rods (or one rod + anti-rotation), linear ball bushings (LM…UU) or pillow blocks. Rigid if well aligned; watch rod flex on long spans. |
| **Plastic slider (e.g. igus)** | Dry-running, low maintenance | DryLin / similar polymer bearings on aluminium shafts or profiles. Quiet, corrosion-tolerant, good for portable kits; check load ratings and play under tilt. |

**Practical picks**

- Short travel, light mirrorless → plastic or rod+bushing is enough.  
- Long travel or cinema heads → industrial rail or thick rods, stiff base.  
- Upcycle: many “dead” CNC / printer / lab stages already have usable rails — keep the linear unit, replace drive and electronics.

Alignment matters more than brand: parallel rails, no binding at ends, carriage square to the optical axis.

---

## Choosing the drive mechanism

| Mechanism | Pros | Cons / watch-outs |
|-----------|------|-------------------|
| **Leadscrew + nut** (trapezoidal / ACME) | Cheap, strong, simple gearing via pitch | Backlash unless preloaded; slower max speed; nut wear |
| **Ball screw** | Low friction, high precision, efficient | Cost; may need brake or low-backdrive design on steep pitches |
| **Timing belt + pulley** | Fast travel, quiet if tensioned, printer-grade parts plentiful | Stretch / tensioning; less “locked” when unpowered; pulley teeth and idlers |
| **3D-printer ecosystem** | GT2 belts, T8 screws, NEMA mounts, couplers everywhere | Designed for print heads, not always for fluid heads — derate load and stiffen mounts |

**Gearing tip for JKSlider:** set `steps_per_mm` (or motor steps × microsteps ÷ mm per rev) in **SliderMC** config so the millimetre world matches the real carriage. Soft limits and marks only make sense after that.

Belt systems love higher top speed; screws love finer positioning. Both work — match MC `max_speed` / `max_accel` (and optional `JKS_SPEED_MAX_MM_S` / `JKS_ACCEL_MAX_MM_S2` panel clamps) to what the mechanics can do without ringing.

---

## Choosing the motor

JKSlider / Slider talk **STEP + DIR** (and typically **EN**). The motor behind that interface can vary:

| Option | Feel on set | Notes |
|--------|-------------|--------|
| **Stepper + classic driver** (A4988, DRV8825, TMC2208/09 in STEP/DIR, …) | Familiar, open-loop | Cheapest path. Audible idle/whine depending on driver and mode; TMC stealth modes help. Missed steps under overload → soft limits and sensible accel matter. |
| **Stepper + encoder / closed loop** | More confidence under load | Driver or external loop corrects lost steps. Still STEP/DIR from the Pico in many products. Cost and wiring up; great for heavier payloads. |
| **BLDC / servo with STEP/DIR interface** | Smooth, quiet, efficient | Many “servo” modules accept pulse/dir like a stepper. Higher price; need correct PUL/DIR/ENA levels and often a separate enable/alarm story. |

**Driver interface (what Pico sees)**

```
  Pico GP18  ---- STEP ---->  driver PUL / STEP
  Pico GP19  ---- DIR  ---->  driver DIR
  Pico GP20  ---- EN   ---->  driver ENA (often active-low)
  Pico GND   --------------  driver GND  (common ground required)
```

Match `EN_ACTIVE_LOW`, `DIR_POSITIVE_HIGH`, and logic level (3.3 V Pico vs 5 V tolerant inputs). Motor power is **never** taken from the Pico’s 3V3 — only signal ground is shared.

**Comparison (rule of thumb)**

- **Steppers** — cost-effective, maker-friendly, can be noisy; fine for many kits if accel and current are sane.  
- **Servos / closed-loop** — smoother and quieter under load, more expensive, more setup.  
- Noise on set: prefer quiet drivers, lower current at idle, or servo; add soft pads under feet for table use.

---

## Mounting

How the slider sits in the shot is as important as how it rolls.

| Mount | Use case |
|-------|----------|
| **Flat base / tabletop** | Tabletop product, interview desk, “slider on sticks” without a bowl. Wide footprint, rubber feet, cable exits that don’t tip the rig. |
| **Tripod / bowl / 100–150 mm** | Standard film/video stands. Need a stiff interface plate; avoid flex between bowl and rail. |
| **Quick-release between stand and fluid head** | Manfrotto / Arca / similar: swap head or slider fast. Keep QR stiffness high — play here looks like soft image. |
| **Magic arm / clamp** | Odd angles, car mounts, temporary grips. Great for light cameras; check payload and vibration. |

Also plan:

- **Camera side:** Arca plate, ¼″-20 / ⅜″-16, or a small fluid head on the carriage.  
- **Level and safety:** straps or pins so a failed clamp doesn’t drop glass.  
- **Cable loop:** service loop so USB / HDMI / power don’t tug the carriage at end of travel.

---

## Power supply

| Domain | Typical | Notes |
|--------|---------|--------|
| **Motor bus** | 12 / 24 / 36 / 48 V DC | Set by motor + driver rating. Higher voltage → better high-speed torque on steppers (within driver limits). Size current for stall / peak, not only average. |
| **Logic / Pico** | 5 V → Pico VSYS/VBUS, or regulated 3V3 if designed that way | Prefer a **DC/DC buck** from the motor bus to **5 V** for the Pico (and OLED / NeoPixel if 5 V). Do **not** feed motor current through USB alone on a real axis. |
| **Ground** | Common GND | Motor supply GND, DC/DC GND, and Pico GND must meet at a star or solid plane. |

```
  Battery / PSU  ---+--- motor driver VMOT
                    |
                   DC/DC buck ---> 5 V ---> Pico VSYS (and panel logic)
                    |
                   GND ---------------- common
```

On battery: fuse or breaker near the pack; avoid reverse polarity into the driver. On mains PSU: proper enclosure and strain relief.

---

## Electronic housing

| Style | Strengths | Trade-offs |
|-------|-----------|------------|
| **Tabletop case** | Room for pots, OLED, STOP; stable when operating; easy DIY (3D print / laser / aluminium box) | Extra box on set; cable to the motor |
| **Fluid-head / handle integrated** | One-handed ride-along feel; minimal footprint | Tight packaging, heat, EMC, and ergonomics harder; service access |

Place STOP and OPTION where a gloved hand finds them. Keep STEP wires short and twisted with GND where possible. Vent or heatsink the driver; leave USB accessible for updates.

---

## Homing, limits, and safety hardware

Firmware supports what you wire:

| Hardware | Role |
|----------|------|
| **SW_HOME** | Homing reference + hard limit into `HOME_DIRECTION` |
| **Soft limits** | Software travel (set after measuring real stroke) |
| **DRV_ERROR / e-stop** | Hardware interlock (`PIN_DRV_ERROR`) → halt + disable; also driver alarm/stall |
| **Panel STOP** | Operator stop / halt / disable |

Prefer a real switch or sensor at the home end (mechanical, optical, or Hall). Debounce is in firmware; still use a clean GND return.

---

## Further hardware points worth deciding early

Suggestions beyond the sections above — useful checklist when you design a kit:

1. **Payload & CG** — camera + lens + matte box + follow focus; CG height above the rail drives tipping and motor load on tilt.  
2. **Travel length vs stiffness** — longer rails need thicker profiles or mid support.  
3. **Orientation** — horizontal only vs vertical / Dutch; vertical needs brake, low-backdrive screw, or closed-loop holding.  
4. **Weather & dust** — outdoor: covers, sealed bearings, conformal coat on electronics.  
5. **Cable chain / drag chain** — keeps power and video moving with the carriage.  
6. **Vibration isolation** — rubber feet, separate stand for noisy PSUs, soft pads under driver case.  
7. **EMI** — keep STEP/DIR away from mic and wireless video; ferrite on motor leads if needed.  
8. **Connector strategy** — XT60 / GX16 / aviation plugs for motor power; JST / Dupont only inside the case.  
9. **Serviceability** — replace belt, re-flash Pico, swap driver without tearing down the rail.  
10. **Redundant stop** — panel STOP + wired `DRV_ERROR` / E-stop for rented or crew use.  
11. **Thermal** — driver and motor temperature at your chosen current; derate in sun.  
12. **Spare travel** — leave a few mm beyond soft max/min so hard limit and crash pads are not the same point.  
13. **Counterweight / balance** — long lenses on short carriages.  
14. **Transport** — rail splits, soft case, lock carriage for travel.  
15. **Standards** — Arca, ⅜″ thread, NATO rail if you live in that ecosystem.

---

## How this maps to firmware

| Hardware choice | Main config knobs |
|-----------------|-------------------|
| Pitch / belt / microsteps | `steps_per_mm` (and related keys) in **SliderMC** config |
| Travel | MC `slider_min` / `slider_max` (UIC reads via `CG`) |
| Home end | `HOME_DIRECTION`, `PIN_SW_HOME`, switch polarity (MC) |
| Speed / torque feel | driver current, MC `max_speed` / `max_accel`, ACCEL pot range |
| Quiet vs aggressive stop | driver mode, MC halt / DRV_ERROR decel |
| Panel layout | button vs keypad — Technical Manual |

Bring-up order that saves pain: **stiff mechanics → correct steps/mm → home switch → soft limits → panel**.

---

## One-line hardware philosophy

Upcycled or industrial rails, market STEP/DIR drivers, honest power design, and a housing that matches how you shoot — then JKSlider turns that axis into a set tool.

*JKSlider V1 by JK*
