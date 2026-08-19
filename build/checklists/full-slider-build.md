# Checklist — full slider build

End-to-end order for a new JKSlider + SliderMC pair. Details: [jkslider/technical/README.md](../../uic/projects/jkslider/technical/README.md).

- [ ] **1. Flash SliderMC** on the motion Pico — [mc/build.md](../../mc/build.md)
- [ ] **2. Flash MicroPython** on the UIC Pico
- [ ] **3. Wire crossed UART** (GP16/17, shared GND) — [contract/link-and-handshake.md](../../contract/link-and-handshake.md)
- [ ] **4. Motor / slider config** on MC — [new-motor-and-slider.md](new-motor-and-slider.md)
- [ ] **5. Panel wiring** — [panel-wiring.md](panel-wiring.md)
- [ ] **6. Copy `SliderPins.example.py` → `SliderPins.py`** and edit — [jkslider/technical/config.md](../../uic/projects/jkslider/technical/config.md)
- [ ] **7. Upload UIC Python files** (Thonny / mpremote) — [jkslider/technical/bring-up.md](../../uic/projects/jkslider/technical/bring-up.md)
- [ ] **8. First test run** — [first-test-run.md](first-test-run.md)
- [ ] **9. Hand off** [user-manual.md](../../uic/projects/jkslider/user-manual.md) + [cheat-sheet](../../uic/projects/jkslider/cheat-sheet/cheat-sheet.html) to operator