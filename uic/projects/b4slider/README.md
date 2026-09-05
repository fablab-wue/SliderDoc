# B4Slider

Minimal four- or six-button camera slider panel (`B4Slider.py`).

**1-axis:** MOVE_L/R, SET, OPTION, SPEED pot.  
**2-axis** (optional): add *MOVE_L2/R2* on GP8/GP9 when SliderMC `axis2_use=1` — linear travel + *pan*, time-synced dual chords after pan soft limits are marked.

A/B in the [user manual](user-manual.md) is the **working window** (travel clip + MOVE target), not JKSlider marks. *Pan A/B* is the same idea on axis 2. Philosophy: [Architecture — Marks vs working window](../../../architecture/marks-vs-working-window.md).

| Document | Audience |
|----------|----------|
| [user-manual.md](user-manual.md) | Operator |
| [cheat-sheet/](cheat-sheet/README.md) | One-page set card (HTML/PDF) |
| [panel-layouts/](panel-layouts/README.md) | Pico pinout and recommended plate |
| [technical/README.md](technical/README.md) | Installer notes (stub — shared bring-up with JKSlider) |

**Code:** [B4Slider.py](https://github.com/fablab-wue/SliderCtrl/blob/main/B4Slider.py) · [B4SliderConfig.py](https://github.com/fablab-wue/SliderCtrl/blob/main/B4SliderConfig.py)