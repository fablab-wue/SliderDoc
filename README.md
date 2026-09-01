# SliderDoc

![JKSlider](assets/img/jkslider-hero.png)

Documentation and manuals for an **open DIY motorized camera slider** ecosystem: **UIC** ([SliderCtrl](https://github.com/fablab-wue/SliderCtrl)) + **MC** ([SliderMC](https://github.com/fablab-wue/SliderMC)) + shared UART contract.

Whether you operate on set, install a panel, build the rail, or extend the firmware — this repo is the single source for architecture, protocol, user manuals, and build guides. **Mechanics and enclosure are yours**; the docs cover control feel, motion firmware, and wiring so your build can behave like a commercial motorized slider on the things that matter for shooting — or as a **construction kit** for custom motorized rigs.

## Linked code repositories

| Repo | Role |
|------|------|
| [SliderCtrl](https://github.com/fablab-wue/SliderCtrl) | UI controller — MicroPython panel firmware (JKSlider, B4Slider, libraries) |
| [SliderMC](https://github.com/fablab-wue/SliderMC) | Motion controller — C++ / FreeRTOS STEP/DIR (optional 2nd axis: typical **linear + pan**, time-synced) |

---

## Features (system summary)

One consolidated view of the whole stack — details live in each repo README and in [architecture/marketing.md](architecture/marketing.md).

- **Motorized camera slider control** — laptop-free set operation; analogue speed and accel; STOP / EMO / limits  
- **JKSlider** full panel + **B4Slider** minimal remote — and room for more UIC faces on the same protocol  
- **Construction kit** — JKSlider / B4Slider panel apps, **`MC_Client`** / **`UIC_Base`**, SliderMC motion; build sliders, mini-dollies, rotating heads, turntables, **slider + pan**, or other STEP/DIR rigs  
- **Optional 2-axis** — typical **linear travel + pan** (or tilt/turn), **time-synced** dual moves (not CNC); SliderMC `axis2_use`; `MC_Client` dual `moveTo` / `home`. Shipping panels stay 1-axis. [dual-movement.md](mc/dual-movement.md) · [UIC API](uic/api/overview.md)  
- **Production moves** — marks A/B/C, pair loops, DELAY, timelapse dividers, pause/resume, live retarget, camera trigger  
- **Dedicated motion MCU** — PIO step timing isolated from MicroPython UIC; crossed UART contract at 115200 baud  
- **Open firmware, open docs** — MIT licensed; Thonny / REPL and USB CLI; edit pins, fork panels, script moves  
- **DIY mechanics** — rail, motor, driver, and housing up to the builder; upcycle linear units and off-the-shelf STEP/DIR drivers  

How this compares to commercial motorized sliders: [architecture/compare.md](architecture/compare.md).

---

## Start here (by role)

| I am… | Start here |
|-------|------------|
| Operator | [jkslider/user-manual.md](uic/projects/jkslider/user-manual.md) or [b4slider/user-manual.md](uic/projects/b4slider/user-manual.md) |
| Installer | [jkslider/technical/](uic/projects/jkslider/technical/README.md) + [build/checklists/](build/checklists/README.md) |
| Builder (mechanics) | [build/hardware-manual.md](build/hardware-manual.md) |
| UIC developer | [uic/api/overview.md](uic/api/overview.md) |
| MC developer | [mc/README.md](mc/README.md) |
| Protocol author | [contract/protocol.md](contract/protocol.md) |

## Documentation tree

| Section | Contents |
|---------|----------|
| [architecture/](architecture/README.md) | System split, command chains, compare, marketing |
| [contract/](contract/README.md) | UART protocol, link/handshake, MC command cheat sheet |
| [uic/](uic/README.md) | API, libraries, JKSlider / B4Slider / template projects |
| [mc/](mc/README.md) | Build, config, pins, motion firmware |
| [components/](components/README.md) | Tested hardware module catalog |
| [build/](build/README.md) | Hardware manual + installer checklists |
| [reference/](reference/README.md) | Glossary |
| [assets/](assets/README.md) | Images, SVG, pinout text, OLED mockups |
| [tools/](tools/README.md) | Render/sim scripts (maintainers) |

## Maintaining docs

See [CONTRIBUTING.md](CONTRIBUTING.md). Regenerate cheat sheets and pinouts with scripts in [tools/](tools/README.md).

---

## License

Copyright (c) 2026 Jochen Krapf \<jk@nerd2nerd.org\>

Licensed under the [MIT License](LICENSE).

Company names and product names mentioned in this project are trademarks or registered trademarks of their respective owners. Use here is for identification only.
