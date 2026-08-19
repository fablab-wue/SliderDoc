# Camera Connections (CTRL_CAMERA)

[← Components index](JKSlider_Components.md)

**UIC** wiring — `PIN_CTRL_CAMERA` is on the panel Pico (default GP22). SliderMC uses GP22 for `SW_HOME`. Overview: [ARCHITECTURE.md](../docs/ARCHITECTURE.md).

Shutter / intervalometer output for timelapse and video move modes.

| Symbol | Default | Role |
|--------|---------|------|
| `PIN_CTRL_CAMERA` | 22 | Active-high GPIO |
| `CTRL_CAMERA_PULSE_MS` | 100 | Pulse width (ms) |
| `CTRL_CAMERA_ACTIVE_HIGH` | True | Output polarity |

### Optocoupler remote (e.g. PC817)

**Status:** Working (interface pattern documented).

![CTRL_CAMERA optocoupler wiring](../docs/img/camera_optocoupler_wiring.svg)

Tip/ring/sleeve depends on the camera body — check that remote pinout.

| Mode | CTRL_CAMERA behaviour |
|------|------------------------|
| TL×1 (video) | High while moving; stays high during DELAY soft-pause; low when idle |
| TL×N + MSM | Pulse while stopped, then hop; RGB LED off during pulse |
| TL×N + Cont | Hold-high like video (÷N crawl); not pulses |
| Idle | Low |

Panel / TL settings in `JKSliderConfig.py`: `JKS_CAMERA_FPS`, `JKS_CAMERA_FPS_STEPS`, `JKS_TL_MODE`, `JKS_MSM_EXPOSURE_MS`, `JKS_MSM_SETTLE_MS`. Toggle MSM ↔ Cont with `T`+`D`+`OPTION` (saved).

Full write-up: [Technical Manual — CTRL_CAMERA](JKSlider_Technical_Manual_Panel.md#wiring-schematics--ctrl_camera-shutter--intervalometer).

**Config example:**

```python
# UIC_config.py
PIN_CTRL_CAMERA = 22
CTRL_CAMERA_PULSE_MS = 100
CTRL_CAMERA_ACTIVE_HIGH = True

# JKSliderConfig.py
JKS_CAMERA_FPS = 24
JKS_TL_MODE = "msm"
```

**Photos:** add camera-remote adapters under `docs/img/components/` when documented.
