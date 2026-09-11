<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Camera Connections (CTRL_CAMERA)";
  --doc-path: ".\\SliderDoc\\components\\camera.md";
}
</style>

# Camera Connections (CTRL_CAMERA)

[← Components index](index.md)

Shutter / intervalometer for timelapse and video. On the **split stack**, camera is **SliderMC** `PIN_CAMERA_CTRL` / `CT` (Pico **GP22** / Zero **GP25**). UIC Pico GP22 and Zero GP29 are free on JKS and B4S pinouts. Overview: [ARCHITECTURE.md](../architecture/overview.md) · MC wiring: [pins.md — PIN_CAMERA_CTRL](../mc/pins.md#pin_camera_ctrl-low-active-open-collector).

## SliderMC (`PIN_CAMERA_CTRL`)

Low-active open-collector sink. Two ways to reach the camera:

| Path | Use when |
|------|----------|
| **Optocoupler (PC817)** | Isolated dry contact (typical shutter cable tip/sleeve); no shared ground required |
| **FET level-shifter (BSS138 / 2N7000)** | Camera or box wants **5 V TTL/CMOS**; shared GND OK |

![CTRL_CAMERA optocoupler wiring](../assets/img/camera_optocoupler_wiring.svg)

![PIN_CAMERA_CTRL FET level-shifter](../assets/img/camera_fet_level_shifter.svg)

Intended out-side pull-up is **5 V**. FET `V_DS`: BSS138 **50 V**, 2N7000 **60 V**. Pico pad is **3.3 V only** — never put 5 V on `PIN_CAMERA_CTRL`. Full ASCII, pinouts, and voltage notes: [mc/pins.md](../mc/pins.md#pin_camera_ctrl-low-active-open-collector).

## UIC (`PIN_CTRL_CAMERA`) — JKSlider

**UIC** wiring — `PIN_CTRL_CAMERA` is on the panel Pico (default GP22) if you still pulse the shutter from JKSlider firmware. B4Slider does not.

Shutter / intervalometer output for timelapse and video move modes.

| Symbol | Default | Role |
|--------|---------|------|
| `PIN_CTRL_CAMERA` | 22 | Active-high GPIO |
| `CTRL_CAMERA_PULSE_MS` | 100 | Pulse width (ms) |
| `CTRL_CAMERA_ACTIVE_HIGH` | True | Output polarity |

### Optocoupler remote (e.g. PC817)

**Status:** Working (interface pattern documented).

![CTRL_CAMERA optocoupler wiring](../assets/img/camera_optocoupler_wiring.svg)

Tip/ring/sleeve depends on the camera body — check that remote pinout.

| Mode | CTRL_CAMERA behaviour |
|------|------------------------|
| TL×1 (video) | High while moving; stays high during DELAY soft-pause; low when idle |
| TL×N + MSM | Pulse while stopped, then hop; RGB LED off during pulse |
| TL×N + Cont | Hold-high like video (÷N crawl); not pulses |
| Idle | Low |

Panel / TL settings in `JKSliderConfig.py`: `JKS_CAMERA_FPS`, `JKS_CAMERA_FPS_STEPS`, `JKS_TL_MODE`, `JKS_MSM_EXPOSURE_MS`, `JKS_MSM_SETTLE_MS`. Toggle MSM ↔ Cont with `T`+`D`+`OPTION` (saved).

Full write-up: [Technical Manual — CTRL_CAMERA](../uic/projects/jkslider/technical/panel.md#wiring-schematics--ctrl_camera-shutter--intervalometer).

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

**Photos:** add camera-remote adapters under `../assets/img/components/` when documented.
