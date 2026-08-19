# Analog JoySticks

[← Components index](JKSlider_Components.md)

**UIC** wiring (panel Pico). Motion axis is on SliderMC — see [ARCHITECTURE.md](../docs/ARCHITECTURE.md).

Optional centre-return analogue axis on ADC2.

| Control | Default | Config |
|---------|---------|--------|
| JOYSTICK | GP28 or disabled | `PIN_POT_JOYSTICK = 28` or `None` |
| Deadzone | 0.08 | `JOYSTICK_DEADZONE` |
| Curve | 2.0 | `JKS_JOYSTICK_CURVE_GAMMA` |

Wire one axis like a pot (3V3 — wiper — AGND). Centre = mid ADC; recalibrate when idle with **OPTION + A + B + C** (see User Manual).

**Status:** Working when enabled; leave `None` if unused.

```python
# JKSliderConfig.py
PIN_POT_JOYSTICK = 28      # or None to disable
JOYSTICK_DEADZONE = 0.08
JKS_JOYSTICK_CURVE_GAMMA = 2.0
```

Schematic context: [Technical Manual — pots / joystick](JKSlider_Technical_Manual_Panel.md#wiring-schematics--potentiometers).
