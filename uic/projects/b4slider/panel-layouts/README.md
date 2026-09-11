# B4Slider panel layouts

Generated and reference pinout assets for the UIC Pico / RP2040-Zero.

Filename schema: `{Project}_{Board}_{kind}_{spec}` (underscore only). Project `B4S`; Board `Pico` or `RP2040zero` when the drawing is board-specific.

| Asset | Source |
|-------|--------|
| [`B4S_Pico_pinout.png`](B4S_Pico_pinout.png) / [`assets/B4S_Pico_pinout.txt`](../../../../assets/B4S_Pico_pinout.txt) | `python tools/render_pico_pinout_JKSlider.py b4` |
| [B4S_button_layout.svg](../../../../assets/img/B4S_button_layout.svg) / `.png` | Hand-authored 6U × 6U panel (1-axis) |
| [B4S_button_layout_3axis.svg](../../../../assets/img/B4S_button_layout_3axis.svg) | Hand-authored 6U × 6.5U — AXIS `1` `2` `3` glued under OPTION (AXIS_4/5 not drawn) |
| [`B4S_RP2040zero_pinout.txt`](../../../../assets/B4S_RP2040zero_pinout.txt) / `.png` | `python tools/render_rp2040zero_pinout_SliderMC.py b4` |

See [user-manual.md](../user-manual.md) for silk and gestures. UIC GP22 / Zero GP29 are free (camera is SliderMC `PIN_CAMERA_CTRL`).
