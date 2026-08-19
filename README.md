# SliderDoc

![JKSlider](docs/img/jkslider-hero.png)

This is a collection of **Documentation** and **Manuals** to all Slider Projects

## Linked Projects / Repositorys

### SliderCtrl / JKSlider

User Interface Controller (**UIC**) - https://github.com/fablab-wue/SliderCtrl

### SliderMC

Motor Controller (**MC**) - https://github.com/fablab-wue/SliderMC

---

## Documentation

| Document | Contents |
|----------|----------|
| [manuals/JKSlider_Manual.md](manuals/JKSlider_Manual.md) | Index of all manuals |
| [manuals/JKSlider_User_Manual.md](manuals/JKSlider_User_Manual.md) | Operator — knobs, buttons, OLED / LED on a ready panel |
| [manuals/JKSlider_Technical_Manual.md](manuals/JKSlider_Technical_Manual.md) | Installer hub — links to Link / Bring-up / Panel / Motion / Config |
| [manuals/JKSlider_Hardware_Manual.md](manuals/JKSlider_Hardware_Manual.md) | Builder — rails, drive, motors, mounting, power, housings |
| [manuals/JKSlider_Components.md](manuals/JKSlider_Components.md) | DIY — tested modules, pinouts, schematics, config deltas |
| [manuals/JKSlider_Compare.md](manuals/JKSlider_Compare.md) | Competitive scan |
| [manuals/JKSlider_Mrk.md](manuals/JKSlider_Mrk.md) | Short marketing overview |
| [manuals/glossary.md](manuals/glossary.md) | Acronyms and panel control names |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | UIC ↔ SliderMC architecture |
| [docs/API.md](docs/API.md) | `MC_Client` / `UIC_Base` library API |
| [docs/img/jkslider-hero.png](docs/img/jkslider-hero.png) | Marketing hero image |
| [docs/img/pico_pinout_button.png](docs/img/pico_pinout_button.png) · [keypad](docs/img/pico_pinout_keypad.png) | Pico pinout diagrams |
| [docs/img/keypad_map.png](docs/img/keypad_map.png) | Recommended keypad silk labels |
| [docs/img/discrete_button_layout.png](docs/img/discrete_button_layout.png) | Recommended discrete button / pot layout |
| [docs/img/rocker_switch_layout.png](docs/img/rocker_switch_layout.png) | Recommended rocker-switch panel layout |
| [docs/img/oled/](docs/img/oled/) | OLED screen mockups |

GPIO maps, keypad wiring, LED / NeoPixel schematics, and `JKS_*` options are all in the **Technical Manual** — not duplicated here.

Marketing one-pager: [manuals/JKSlider_Mrk.md](manuals/JKSlider_Mrk.md) · Set cheat sheet (A4): [manuals/JKSlider_Cheat_Sheet.pdf](manuals/JKSlider_Cheat_Sheet.pdf)

---

## License

Copyright (c) 2026 Jochen Krapf \<jk@nerd2nerd.org\>

Licensed under the [MIT License](LICENSE).

Company names and product names mentioned in this project are trademarks or registered trademarks of their respective owners. Use here is for identification only.

`ssd1306.py` / `sh1106.py` / `ssd1309.py` are based on common MicroPython OLED patterns (SSD1306 lineage typically MIT). `oledfont.py` uses Adafruit GFX 5×7 font data (BSD-style upstream). Keep their notices if you redistribute those files alone.
