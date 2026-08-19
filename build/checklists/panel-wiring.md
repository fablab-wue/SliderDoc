# Checklist — panel wiring

UIC GPIO checklist. Full pinouts: [jkslider/technical/panel.md](../../uic/projects/jkslider/technical/panel.md).

- [ ] Choose variant: **button** or **keypad** (`JKS_INPUT_MODE` in `SliderPins.py`)
- [ ] SPEED / ACCEL pots on GP26 / GP27 (ADC)
- [ ] Optional joystick on GP28 or disabled in config
- [ ] RGB LED on GP2–4 (or NeoPixel on free GPIO)
- [ ] OLED I2C on GP0/1 if fitted
- [ ] Camera shutter on GP22 if fitted
- [ ] UART to MC: **GP16 TX → MC RX**, **GP17 RX → MC TX**, common GND
- [ ] Regenerate pinout PNG if you changed labels: `python tools/render_pico_pinout_JKSlider.py`