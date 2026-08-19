# Checklist — first test run

After firmware flash and wiring. See [bring-up.md § First test](../../uic/projects/jkslider/technical/bring-up.md#7-first-test-run).

- [ ] Power motor supply + both Picos
- [ ] Run `import JKSlider; JKSlider.run()` or auto-start via `main.py`
- [ ] Unlock (OPTION or STOP if boot unlock enabled)
- [ ] Release stuck keys if OLED prompts
- [ ] Homing completes cleanly
- [ ] MOVE L/R and STOP behave correctly
- [ ] Wrong direction? Flip `DIR_POSITIVE_HIGH` or swap motor wires (one change at a time)
- [ ] Banner timeout? Check [link checklist](../../contract/link-and-handshake.md#communication-mc--uic)