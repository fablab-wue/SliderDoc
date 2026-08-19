# OLED Displays

[← Components index](JKSlider_Components.md)

**UIC** wiring (panel Pico). Motion axis is on SliderMC — see [ARCHITECTURE.md](../docs/ARCHITECTURE.md).

I2C **128×64** status display. Copy matching driver file + `oledfont.py` to the Pico.

| Typical size | Controller | `DSP_DRIVER` | Driver file |
|--------------|------------|--------------|-------------|
| 0.96″ | SSD1306 | `"ssd1306"` | `ssd1306.py` |
| 1.3″ | SH1106 / SSH1106 / CH1115·16 | `"sh1106"` | `sh1106.py` |
| 1.54″ / 2.42″ | SSD1309 | `"ssd1309"` | `ssd1309.py` |

| Net | Default | Config |
|-----|---------|--------|
| SDA | GP0 | `PIN_DSP_I2C_SDA` |
| SCL | GP1 | `PIN_DSP_I2C_SCL` |
| — | — | `DSP_I2C_ID = 0`, `DSP_I2C_ADDR = 0x3C`, `DSP_I2C_FREQ = 400_000` |

![OLED I2C module wiring](../docs/img/oled_i2c_wiring.svg)

Example UI (not a product photo — mockups live under `docs/img/oled/`):

![OLED homing](../docs/img/oled/oled-homing.png)

### SSD1306 0.96″ I2C module

**Status:** Working (project default).

**Config:**

```python
# UIC_config.py
DSP_ENABLED = True
DSP_DRIVER = "ssd1306"
DSP_ROTATE_180 = False
PIN_DSP_I2C_SDA = 0
PIN_DSP_I2C_SCL = 1
DSP_I2C_ADDR = 0x3C
DSP_WIDTH = 128
DSP_HEIGHT = 64
```

Module VCC is often 3.3–5 V; Pico I2C logic is **3.3 V**. Add product photos under `docs/img/components/` when you document a specific board.

### SH1106 / SSD1309 modules

**Status:** Working with the matching driver file and `DSP_DRIVER` string (see table). Marketplace **SSH1106** and **CH1115/CH1116** → use `"sh1106"`.
