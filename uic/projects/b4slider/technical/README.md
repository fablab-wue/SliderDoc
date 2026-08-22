# B4Slider — technical (planned)

Operator use of a finished unit: [user-manual.md](../user-manual.md).  
One-page set card: [cheat-sheet/cheat-sheet.pdf](../cheat-sheet/cheat-sheet.pdf).

B4Slider shares most install steps with JKSlider. Use these **today**:

| Topic | Document |
|-------|----------|
| UART link + handshake | [contract/link-and-handshake.md](../../../../contract/link-and-handshake.md) |
| Shared bring-up | [jkslider/technical/bring-up.md](../../jkslider/technical/bring-up.md) (skip keypad/OLED steps) |
| Shared config model | [jkslider/technical/config.md](../../jkslider/technical/config.md) (`B4SliderConfig.py` / `SliderPins.py`) |
| Protocol | [contract/protocol.md](../../../../contract/protocol.md) |

## Planned pages

| Page | Status |
|------|--------|
| `bring-up.md` | Planned — B4-specific file list and Thonny steps |
| `panel-layouts.md` | Planned — extra silk notes; assets in [panel-layouts/](../panel-layouts/README.md) |
| `config.md` | Planned — `B4S_*` reference |
| [cheat-sheet/](../cheat-sheet/README.md) | Done — operator one-pager |

**Code entry points:** [B4Slider.py](https://github.com/fablab-wue/SliderCtrl/blob/main/B4Slider.py) · [B4SliderConfig.py](https://github.com/fablab-wue/SliderCtrl/blob/main/B4SliderConfig.py)