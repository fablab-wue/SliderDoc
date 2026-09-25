# SliderMC Command Cheat Sheet

Firmware V1.0. Same groups as the [printable sheet](command-cheatsheet.html).
Canonical prose: [protocol.md](protocol.md). Dual-axis timing: [dual-movement.md](../mc/dual-movement.md). Joystick: [motion-joy.md](../mc/motion-joy.md). Working window: [working-window.md](../mc/working-window.md).

Regenerate: `python tools/render_command_cheatsheet.py`

- **Call** — send this (brackets = optional; bare = omit args).
- **Reply** — typical success line; `—` = silent (errors still `!E:…`).

## Arguments

`<s>`
: Speed in mm/s or deg/s

`<a>`
: Acceleration / deceleration in mm/s² or deg/s²

`<axv>`
: Axis values for the packed live channels (STEP/DIR motors first, then RC servos; up to six). A line is **either** positional **or** named — never mixed (`MT 20 C100` → `!E:parse`).
: **Positional:** one number per channel in order, spaces between them. `_` skips a slot and leaves that channel unchanged (`MT _ _ 100` moves only channel 3). Omitted trailing slots are unchanged (`MT 50` is channel 1 only).
: **Named:** letters `X` `Y` `Z` = motors 1–3, `A` `B` `C` = servos 1–3, then the value (spaces optional: `C100`, `C 100`, `MT C100 B50`). Duplicate letter, unknown letter, or a channel that is not fitted → `!E:parse`.
: `PD` uses the same forms in **µm** (`<axv_um>`); skip `_` or omit named → `0`.
: `MJ` uses signed **percent** (not mm); omitted named extra = `0`; `_` is invalid.

## S — Set (session)

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Set Speed | **`SS`**`[<v>]` | `—` | Cruise speed mm/s (≤ max_speed_1); bare reloads init_speed; live on next fill (incl. MJ). Dual MT: axis1=session, axis2×ratio. |
| Set Accel | **`SA`**`[<a> [d]]` | `—` | Peak accel [, decel] mm/s² (≤ max_accel_1). One value sets both ramps; two split start/stop. No skip _. Bare reloads init_accel into both; live on next fill (incl. MJ). Dual MT: same ratio scaling as SS. |
| Set Enable | **`SE`**`[0\|1]` | `—` | Driver enable 0\|1; bare toggles; required before motion; off = hard stop. SE 0 also stops servo PWM (limp). |
| Set Terminal | **`ST`**`[0\|1]` | `—` | Terminal Mode 0\|1; bare toggles; local echo + UART sniff to USB (expert). |
| Set Verbose | **`SV`**`[0\|1]` | `—` | Verbose #… push 0\|1; bare toggles; ~3 Hz (rate via verbose_rate_hz). |
| Set Debug | **`SD`**`[0..5]` | `—` | USB-only debug level 0..5; bare restores default; never on UIC UART. |
| Set Left | **`SL`**`[<axv>]` | `—` | Session soft min (working window); bare→MOTOR_N_min/SERVO envelope; none clears (→envelope if set); skip _; !E:limit past envelope. |
| Set Right | **`SR`**`[<axv>]` | `—` | Session soft max; bare→MOTOR_N_max/SERVO envelope; none clears; skip _; !E:limit if left>right. |
| Set Position | **`SP`**`[<axv>]` | `—` | Set reported pose (no motion); idle only; bare/0 = here is zero; skip _. |

## G — Get (session)

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Get Speed | **`GS`** | `GS:<mm/s>` | Current session cruise speed. |
| Get Accel | **`GA`** | `GA:<a> <d>` | Current session accel and decel (mm/s²). |
| Get Enable | **`GE`** | `GE:0\|1` | Driver enable state. |
| Get Terminal | **`GT`** | `GT:0\|1` | Terminal Mode state. |
| Get Verbose | **`GV`** | `GV:0\|1` | Verbose push state. |
| Get Debug | **`GD`** | `GD:<0..5>` | USB debug level. |
| Get Left | **`GL`** | `GL:<pos> [\| …]` | Session soft min; effective (session else envelope); - if both None; extra pipe fields when packed≥2. |
| Get Right | **`GR`** | `GR:<pos> [\| …]` | Session soft max; same effective / - rules as GL. |

## I — Is / Info

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Is Moving | **`IM`** | `IM:0\|1` | Moving or settling on any active axis. |
| Is Homing | **`IH`** | `IH:0\|1` | Homing cycle active. |
| Is Limit | **`IL`** | `IL:0\|1` | At soft-limit position (axis1). |
| Is Error | **`IE`** | `IE:0\|1` | PIN_DRV_ERROR / EMO latched. |
| Is Position | **`IP`** | `IP:<pos> [\| …]` | One pipe field per packed live channel (motors then servos; CG axis = sum). |
| Is Axis | **`IA`** | `IA:<n>` | Packed live channels motors+servos (1..6). Same as CG axis. CS axis rejected. |
| Is Target | **`IT`** | `IT:<pos>\|-` | Axis-1 seek target, or - if none / soft-stop. |
| Is Ready | **`IR`** | `IR:0\|1` | 1 only if idle, not homing, enabled, and not waiting. |
| Is Waiting | **`IW`** | `IW:0\|1` | 1 if any WT / WM / WH / WP / WC / WN wait is active. |
| Is Diag | **`ID`** | `ID:underrun=N peak_hz=… overshoot=… fifo_min=…` | Motion diag counters (FIFO underrun, peak STEP Hz, …). |
| Is Cause | **`IC`** | `IC:<reason>` | Last chip reset: power\|wdt\|run\|soft\|debug\|brownout\|… |
| Is GPIO | **`IG`** | `(multi-line table)` | ASCII GP / name / desc (≤80 cols). Extra-axis rows only if that axis is live. |

## M — Movement

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Move To | **`MT`**`<axv> (absolute)` | `—` | Absolute user units; up to 6 packed channels (XYZ motors, ABC servos); skip _; needs SE; live-retarget. Dual MT: time-sync. Out-of-window = !E:soft (no clip). |
| Move Duration | **`MD`**`<ms> <axv>` | `—` | Same targets as MT. Arrive in ms (1..60000). Cruise is distance/time. Does not change SS. Too fast = !E:speed. |
| Move For | **`MF`**`<ms> <ramp_ms> <axv>` | `—` | Same targets as MD. Each ramp lasts ramp_ms. 2*ramp_ms is less than ms. Too fast = !E:speed. |
| Move By | **`MB`**`<axv> (delta) …` | `—` | Relative move; same skip/named XYZABC rules as MT. |
| Move Joy | **`MJ`**`<pct> …` | `—` | Joy speed % of SS, signed (− left / + right); omit named extra=0; 0=soft-stop; SS/SA live; clamp max_speed_N. Hold-to-jog: MJ ±100, MS on release. |
| Move Home | **`MH`**`[1\|2\|3]` | `—` | Homing; axis 1 (default), 2, or 3; no-op if home_mode_N=0; cancel MS/ME. |
| Move Soft Stop | **`MS`** | `—` | Soft decelerate both axes; keeps enable; ends joy-mode; does not cancel waits. Dual: scaled accel kept. |
| Move E-Stop, Halt | **`ME`** | `—` | Immediate STEP abort; enable off; cancel waits and remaining ; chain. |

## P — Path

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Path Clear | **`PC`** | `—` | Clear path buffer (count→0); !E:busy while PG active. |
| Path Data | **`PD`**`<axv_um>` | `—` | Append signed µm sample(s); up to 6 packed channels; skip _ →0; OK while PG (live stream). |
| Path Go | **`PG`** | `—` | Play buffer from sample 0; needs SE; !E:empty\|busy\|disabled. MS/ME ends path. |
| Path Number | **`PN`** | `PN:<count>` | Samples in buffer; allowed during PG. |
| Path Slice | **`PS`**`[<us>]` | `—` | Slice length µs (≥1000); bare→init_path_slice_us; !E:busy while PG. |

## W — Wait

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Wait Time | **`WT`**`[<sec>]` | `—` | Delay then continue ; chain; bare→1 s; never !E:timeout. |
| Wait Moving | **`WM`**`[<timeout_s>]` | `—` | Pause chain until move ends; optional timeout → !E:timeout, cancel rest of chain. |
| Wait Homing | **`WH`**`[<timeout_s>]` | `—` | Pause until homing ends; timeout same as WM. |
| Wait Pos | **`WP`**`<pos> [<timeout_s>]` | `—` | Wait until time-sync master pos reached/overstepped; idle→immediate; 2nd arg=timeout. |
| Wait Cruise | **`WC`**`[<timeout_s>]` | `—` | Wait until cruise (status M) or idle; optional timeout → !E:timeout. |
| Wait Not cruise | **`WN`**`[<timeout_s>]` | `—` | Wait until not cruise M; idle/A/B→immediate; timeout same as WM. |

## E — Extender

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Ext Out | **`EO`**`0..3 [0\|1]` | `—` | Ext out n logical 0\|1; bare EO0 toggles; glued EO01≡EO0 1; OK during EMO. EO4+ rejected. |

## Special

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Reboot | **`RB`** | `—` | Soft MCU reset (no power cycle); EN off first. CS motors/servos do not need RB. |
| Beep | **`BE`**`[<ms>]` | `—` | Pulse PIN_BUZZER; bare 100 ms; clamp 1..1000; not a wait. No-op if BUZZER_use=0. OK during EMO/path. |
| Camera Trigger | **`CT`**`[<ms>]` | `—` | Pulse PIN_CAMERA_CTRL low (OC sink); bare 100 ms; clamp 1..60000; not a wait; motion continues. OK during EMO/path. Verbose on: status letter T while pulsing (at least once). |
| Help | **`HL/?`**`HL \| ?` | `(multi-line table)` | Two-column table of all commands (short + phrase). ? needs newline; not realtime status. |

## C — Config

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Config Set | **`CS`**`<key> <value>` | `—` | Persist key to mc.ini; silent ok. CS motors/servos re-init GPIO immediately (no RB). CS axis rejected. |
| Config Reset | **`CR`** | `—` | Reset all config to compiled defaults and save mc.ini. |
| Config Get | **`CG`**`[<key>]` | `CG:<key>=<value>` | One key, or bare dumps all keys (multi-line). |

## V — Version

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Version About | **`VA`** | `VA:…` | About string (name, version, author). |
| Version FW | **`VF`** | `VF:<version>` | Firmware version. |
| Version Protocol | **`VP`** | `VP:1` | Protocol version (1). Wire may change without bumping VP. |
| Version GPIO | **`VG`** | `VG:PIN_*=n (multi-line)` | Machine-readable pin map. Extra-axis pins if that axis is live. |

## Now Commands

Executed immediately without \n

| Command | Call | Reply | Description |
|--------|------|-------|-------------|
| Status now | **`#`** | `#<state> …` | Realtime compact status line (no newline). |
| Soft Stop now | **`!`** | `—` | Realtime soft stop (same urgency as MS). |
| E-Stop now | **`ESC`** | `—` | Realtime halt (same urgency as ME): STEP abort, EN off, cancel waits/chain. |

## Notes

- Chain with `;`. `/` comments from that character to end of line. Realtime (no newline): `#` status, `!` soft stop, `ESC` halt, `Ctrl-X` soft reset. `#` is not a comment. `?` is help (needs `\n`), not status.
- Path mode (`PG`): most move/session cmds → `!E:busy`; allowed: `MS`/`ME`/`RB`/`PD`/`PN`/`I*`/`G*`/`V*`/`IG`/`HL`/`?`/`CG`/`BE`/`CT`.
- `MJ` / Move Joy: signed % of `SS`; skip unchanged values; `SS`/`SA` live in joy-mode. Hold-to-jog: `SS` then `MJ ±100`, `MS` on release. See [motion-joy.md](../mc/motion-joy.md).
- Skip token `_` only (`MT`/`MB`/`PD`/`SL`/`SR`). Named `X`/`Y`/`Z`/`A`/`B`/`C` is an alternative (not mixed with positional). `SL`/`SR` `none` clears a side (effective = envelope when set). See [working-window.md](../mc/working-window.md).
- Envelopes / units: `MOTOR_N_min`/`MOTOR_N_max`, `SERVO_N_min`/`SERVO_N_max`, synthesized `axis_min_N`, `steps_per_unit_N`, stored `motor_N_unit` / `servo_N_unit`, synthesized read-only `axis_N_unit`. Servo pulse `SERVO_N_min_pulse`/`max_pulse` (default 500–2500 µs; analog 1000–2000); `SERVO_N_swap` reverses sense. `CS axis`, `CS axis_N_unit`, and `CS slider_*` are rejected.
- Breaking wire (`ME`, `?` help, `#` status only, `/` comments, `CT`) does **not** bump `VP` — still `VP:1`.
