# B4Slider

AXIS-select camera slider panel (`B4Slider.py`) — packed axes **1–5**.

**Always:** MOVE_L/R, SET, OPTION, AXIS_1..5, SPEED (pot or rotary).  
**Typical silk:** AXIS `1` `2` `3` on [`B4S_button_layout_3axis.svg`](../../../assets/img/B4S_button_layout_3axis.svg) (slider + pan + tilt). AXIS_4/5 are optional extras, not drawn. Legal chords use packed `getAxisCount()`. MOVE on the selection is one skipped `MT` ([time-synced](../../../mc/dual-movement.md)).

A/B in the [user manual](user-manual.md) is the **working window** (travel clip + MOVE target), not JKSlider marks. Philosophy: [Architecture — Marks vs working window](../../../architecture/marks-vs-working-window.md).

Shutter is SliderMC `CT` / `PIN_CAMERA_CTRL`, not a UIC GPIO.

| Document | Audience |
|----------|----------|
| [user-manual.md](user-manual.md) | Operator |
| [cheat-sheet/](cheat-sheet/README.md) | One-page set card (HTML/PDF) |
| [panel-layouts/](panel-layouts/README.md) | Pico / Zero pinouts and recommended plate |
| [technical/README.md](technical/README.md) | Installer notes (stub — shared bring-up with JKSlider) |

**Code:** [B4Slider.py](https://github.com/fablab-wue/SliderCtrl/blob/main/B4Slider.py) · [B4SliderConfig.py](https://github.com/fablab-wue/SliderCtrl/blob/main/B4SliderConfig.py)
