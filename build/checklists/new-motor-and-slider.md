# Checklist — new motor / slider

Use when changing mechanics, driver, or travel. Full detail: [bring-up.md](../../uic/projects/jkslider/technical/bring-up.md#checklist--new-motor--slider-slidermc).

## A. Mechanics (SliderMC)

- [ ] Motor steps/rev (usually 200)
- [ ] Microstepping matches driver DIP/SPI
- [ ] mm per motor revolution measured
- [ ] `steps_per_unit` verified
- [ ] `slider_min` / `slider_max` set via `CS` or `mc.ini` — [mc/config.md](../../mc/config.md)

## B. Speed / feel

- [ ] `max_speed` / `max_accel` conservative first
- [ ] Homing direction and switch polarity — [mc/config.md](../../mc/config.md)

## C. Driver pins (SliderMC)

- [ ] STEP/DIR/EN, home, DRV_ERROR on MC Pico — [mc/pins.md](../../mc/pins.md)
- [ ] `EN_ACTIVE_LOW`, `DIR_POSITIVE_HIGH`, switch polarity correct

## D. UIC panel (after axis works)

- [ ] `SliderPins.py` for your variant — [jkslider/technical/config.md](../../uic/projects/jkslider/technical/config.md)
- [ ] Ruler check: known move matches measured distance