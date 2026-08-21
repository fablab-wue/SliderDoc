# Tools

Render and simulation scripts (maintainer-facing). Run from repository root unless noted.

| Script | Output |
|--------|--------|
| [render_cheat_sheet.py](render_cheat_sheet.py) | `uic/projects/jkslider/cheat-sheet/cheat-sheet.pdf` |
| [render_command_cheatsheet.py](render_command_cheatsheet.py) | `contract/command-cheatsheet.html` (+ `.md`, optional PDF) |
| [render_pico_pinout_JKSlider.py](render_pico_pinout_JKSlider.py) | `panel-layouts/*.png`, `assets/pico_pinout_*.txt` |
| [render_pico_pinout_SliderMC.py](render_pico_pinout_SliderMC.py) | `assets/img/pico_pinout_mc.png`, `assets/pico_pinout_mc.txt` |
| [render_rp2040zero_pinout_SliderMC.py](render_rp2040zero_pinout_SliderMC.py) | `assets/img/rp2040zero_pinout_mc.png`, `assets/rp2040zero_pinout_mc.txt` |
| [render_dir_change_pause.py](render_dir_change_pause.py) | `assets/img/dir_change_pause.png` |
| [render_sine_ramp_fifo.py](render_sine_ramp_fifo.py) | `assets/img/sine_ramp_300mm_s.svg` |
| [sim_sine_ramp_fifo.py](sim_sine_ramp_fifo.py) | FIFO ramp SVGs under `assets/img/` |
| [oled/render_examples.py](oled/render_examples.py) | `assets/img/oled/*.png` |

**Prerequisites:** Python 3; Playwright or Chrome/Edge for PDFs; matplotlib for some plots.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for when to regenerate and commit outputs.