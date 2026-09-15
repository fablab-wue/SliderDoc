# Tools

Render and simulation scripts (maintainer-facing). Run from repository root unless noted.

| Script | Output |
|--------|--------|
| [render_cheat_sheet.py](render_cheat_sheet.py) | `uic/projects/{jkslider,b4slider}/cheat-sheet/cheat-sheet.pdf` (`jkslider` / `b4slider` args; default both) |
| [render_command_cheatsheet.py](render_command_cheatsheet.py) | `contract/command-cheatsheet.html` (+ `.md`, optional PDF) |
| [render_pico_pinout_JKSlider.py](render_pico_pinout_JKSlider.py) | JKSlider `panel-layouts/JKS_Pico_pinout_{button,keypad}.png`, `assets/JKS_Pico_pinout_{button,keypad}.txt`; `b4` → `uic/projects/b4slider/panel-layouts/B4S_Pico_pinout.png`, `assets/B4S_Pico_pinout.txt` |
| [render_pico_pinout_SliderMC.py](render_pico_pinout_SliderMC.py) | `assets/img/MC_Pico_pinout.png`, `assets/MC_Pico_pinout.txt` |
| [render_rp2040zero_pinout_SliderMC.py](render_rp2040zero_pinout_SliderMC.py) | `assets/img/MC_RP2040zero_pinout.png`, `assets/MC_RP2040zero_pinout.txt`; `button` → `JKS_RP2040zero_pinout_button.*`; `b4` → `B4S_RP2040zero_pinout.*` |
| [render_rp2040zero_pinout_SliderDMC.py](render_rp2040zero_pinout_SliderDMC.py) | `assets/img/DMC_RP2040zero_pinout.png`, `assets/DMC_RP2040zero_pinout.txt` |
| [render_dir_change_pause.py](render_dir_change_pause.py) | `assets/img/dir_change_pause.png` |
| [render_sine_ramp_fifo.py](render_sine_ramp_fifo.py) | `assets/img/sine_ramp_300mm_s.svg` |
| [sim_sine_ramp_fifo.py](sim_sine_ramp_fifo.py) | FIFO ramp SVGs under `assets/img/` |
| [oled/render_examples.py](oled/render_examples.py) | `assets/img/oled/*.png` |

**Prerequisites:** Python 3; Playwright or Chrome/Edge for PDFs; matplotlib for some plots.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for when to regenerate and commit outputs.