# JKSlider panel layouts

Generated and reference pinout assets for the UIC Pico.

Filename schema: `{Project}_{Board}_{kind}_{spec}` (underscore only). Project `JKS`; Board `Pico` or `RP2040zero` when the drawing is board-specific.

| Asset | Source |
|-------|--------|
| `JKS_Pico_pinout_button.png` / `.txt` | `python tools/render_pico_pinout_JKSlider.py` |
| `JKS_Pico_pinout_keypad.png` / `.txt` | same |
| Wiring SVGs | [assets/img/](../../../../assets/img/) (shared); plate: `JKS_button_layout.svg` |
| `JKS_RP2040zero_pinout_button.png` / `.txt` | `python tools/render_rp2040zero_pinout_SliderMC.py button` |
| `keypad_map.png` | Hand-authored (not overwritten by script) |

See [technical/panel.md](../technical/panel.md) for variant wiring. UIC GP22 / Zero GP29 are unlabeled (camera is SliderMC `PIN_CAMERA_CTRL`).
