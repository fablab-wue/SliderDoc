<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "SliderMC Command Cheat Sheet";
  --doc-path: ".\\SliderDoc\\contract\\command-cheatsheet.md";
}
</style>

# SliderMC Command Cheat Sheet

Firmware V1.0. Same groups as the [printable sheet](command-cheatsheet.html).
Canonical prose: [protocol.md](protocol.md). Dual-axis timing: [dual-movement.md](../mc/dual-movement.md). Joystick: [motion-joy.md](../mc/motion-joy.md). Working window: [working-window.md](../mc/working-window.md).

Regenerate: `python tools/render_command_cheatsheet.py`

- **Call** — send this (brackets = optional; bare = omit args).
- **Reply** — typical success line; `—` = silent (errors still `!E:…`).

## S — Set (session)

| Short | Phrase | Call | Reply | Description |
|-------|--------|------|-------|-------------|
| `SS` | `Set Speed` | `SS [<v>]` | `—` | Cruise speed mm/s (≤ max_speed_1); bare reloads init_speed; live on next fill (incl. MJ). Dual MT: axis1=session, axis2×ratio. |
| `SA` | `Set Accel` | `SA [<a>]` | `—` | Peak accel mm/s² (≤ max_accel_1); bare reloads init_accel; live on next fill (incl. MJ). Dual MT: same ratio scaling as SS. |
| `SE` | `Set Enable` | `SE [0\|1]` | `—` | Driver enable 0\|1; bare toggles; required before motion; off = hard stop. |
| `ST` | `Set Terminal` | `ST [0\|1]` | `—` | Terminal Mode 0\|1; bare toggles; local echo + UART sniff to USB (expert). |
| `SV` | `Set Verbose` | `SV [0\|1]` | `—` | Verbose #… push 0\|1; bare toggles; ~3 Hz (rate via verbose_rate_hz). |
| `SD` | `Set Debug` | `SD [0..5]` | `—` | USB-only debug level 0..5; bare restores default; never on UIC UART. |
| `SL` | `Set Left` | `SL [<pos> [<pos2> [<pos3>]]] \| SL X.. Y.. Z..` | `—` | Session soft min (working window); bare→slider_min_N; none clears (→envelope if set); skip _; !E:limit past envelope. |
| `SR` | `Set Right` | `SR [<pos> [<pos2> [<pos3>]]] \| SR X.. Y.. Z..` | `—` | Session soft max; bare→slider_max_N; none clears; skip _; !E:limit if left>right. |
| `SP` | `Set Position` | `SP [<pos> [<pos2> [<pos3>]]] \| SP X.. Y.. Z..` | `—` | Set reported pose (no motion); idle only; bare/0 = here is zero; skip _. |

## G — Get (session)

| Short | Phrase | Call | Reply | Description |
|-------|--------|------|-------|-------------|
| `GS` | `Get Speed` | `GS` | `GS:<mm/s>` | Current session cruise speed. |
| `GA` | `Get Accel` | `GA` | `GA:<mm/s2>` | Current session acceleration. |
| `GE` | `Get Enable` | `GE` | `GE:0\|1` | Driver enable state. |
| `GT` | `Get Terminal` | `GT` | `GT:0\|1` | Terminal Mode state. |
| `GV` | `Get Verbose` | `GV` | `GV:0\|1` | Verbose push state. |
| `GD` | `Get Debug` | `GD` | `GD:<0..5>` | USB debug level. |
| `GL` | `Get Left` | `GL` | `GL:<pos> [<pos2> [<pos3>]]` | Session soft min; effective (session else envelope); - if both None; extra fields when axis≥2. |
| `GR` | `Get Right` | `GR` | `GR:<pos> [<pos2> [<pos3>]]` | Session soft max; same effective / - rules as GL. |

## I — Is / status

| Short | Phrase | Call | Reply | Description |
|-------|--------|------|-------|-------------|
| `IM` | `Is Moving` | `IM` | `IM:0\|1` | Moving or settling on any active axis. |
| `IH` | `Is Homing` | `IH` | `IH:0\|1` | Homing cycle active. |
| `IL` | `Is Limit` | `IL` | `IL:0\|1` | At soft-limit position (axis1). |
| `IE` | `Is Error` | `IE` | `IE:0\|1` | PIN_DRV_ERROR / EMO latched. |
| `IP` | `Is Position` | `IP` | `IP:<pos> [<pos2> [<pos3>]]` | One field per live axis (CG axis). |
| `IA` | `Is Axis` | `IA` | `IA:1\|2\|3` | Live axis count (CS axis / CG axis). |
| `IT` | `Is Target` | `IT` | `IT:<pos>\|-` | Axis-1 seek target, or - if none / soft-stop. |
| `IR` | `Is Ready` | `IR` | `IR:0\|1` | 1 only if idle, not homing, enabled, and not waiting. |
| `IW` | `Is Waiting` | `IW` | `IW:0\|1` | 1 if any WT / WM / WH / WP / WC / WN wait is active. |
| `ID` | `Is Diag` | `ID` | `ID:underrun=N peak_hz=… overshoot=… fifo_min=…` | Motion diag counters (FIFO underrun, peak STEP Hz, …). |
| `IC` | `Is Cause` | `IC` | `IC:<reason>` | Last chip reset: power\|wdt\|run\|soft\|debug\|brownout\|… |
| `IG` | `Is GPIO` | `IG` | `(multi-line table)` | ASCII GP / name / desc (≤80 cols). Extra-axis rows only if that axis is live. |

## M — Movement

| Short | Phrase | Call | Reply | Description |
|-------|--------|------|-------|-------------|
| `MT` | `Move To` | `MT <pos> [<pos2> [<pos3>]] \| MT X.. Y.. Z..` | `—` | Absolute user units; extra live axes; skip _; needs SE; live-retarget. Dual: time-sync ratio. Out-of-window = !E:soft (no clip). |
| `MB` | `Move By` | `MB <delta> [<delta2> [<delta3>]] \| MB X.. Y.. Z..` | `—` | Relative move; same extra-axis/skip/named rules as MT. |
| `MJ` | `Move Joy` | `MJ <pct> [<pct2> [<pct3>]] \| MJ X.. Y.. Z..` | `—` | Joy speed % of SS, signed (− left / + right); omit named extra=0; 0=soft-stop; SS/SA live; clamp max_speed_N. Hold-to-jog: MJ ±100, MS on release. |
| `MH` | `Move Home` | `MH [1\|2\|3]` | `—` | Homing; axis 1 (default), 2, or 3; no-op if home_mode_N=0; cancel MS/HT. |
| `MS` | `Move Stop` | `MS` | `—` | Soft decelerate both axes; keeps enable; ends joy-mode; does not cancel waits. Dual: scaled accel kept. |

## P — Path

| Short | Phrase | Call | Reply | Description |
|-------|--------|------|-------|-------------|
| `PC` | `Path Clear` | `PC` | `—` | Clear path buffer (count→0); !E:busy while PG active. |
| `PD` | `Path Data` | `PD <um> [<um2> [<um3>]] \| PD X.. Y.. Z..` | `—` | Append signed µm sample(s); extra live axes; skip _ →0; OK while PG (live stream). |
| `PG` | `Path Go` | `PG` | `—` | Play buffer from sample 0; needs SE; !E:empty\|busy\|disabled. MS/HT ends path. |
| `PN` | `Path Number` | `PN` | `PN:<count>` | Samples in buffer; allowed during PG. |
| `PS` | `Path Slice` | `PS [<us>]` | `—` | Slice length µs (≥1000); bare→init_path_slice_us; !E:busy while PG. |

## E — Extender / beep

| Short | Phrase | Call | Reply | Description |
|-------|--------|------|-------|-------------|
| `EO` | `Ext Out` | `EO0..3 [0\|1]` | `—` | Ext out n logical 0\|1; bare EO0 toggles; glued EO01≡EO0 1; OK during EMO. EO4+ rejected. |
| `BE` | `Beep` | `BE` | `—` | Pulse PIN_BUZZER ~0.1 s; not a wait. No-op if BUZZER_use=0. OK during EMO/path. |

## C — Config

| Short | Phrase | Call | Reply | Description |
|-------|--------|------|-------|-------------|
| `CS` | `Config Set` | `CS <key> <value>` | `—` | Persist key to mc.ini; silent ok. axis / WDT_use need RB to take HW effect. |
| `CR` | `Config Reset` | `CR` | `—` | Reset all config to compiled defaults and save mc.ini. |
| `CG` | `Config Get` | `CG [<key>]` | `CG:<key>=<value>` | One key, or bare dumps all keys (multi-line). |
| `RB` | `Reboot` | `RB` | `—` | Soft MCU reset (no power cycle); EN off first. After CS axis. |

## W — Wait

| Short | Phrase | Call | Reply | Description |
|-------|--------|------|-------|-------------|
| `WT` | `Wait Time` | `WT [<sec>]` | `—` | Delay then continue ; chain; bare→1 s; never !E:timeout. |
| `WM` | `Wait Moving` | `WM [<timeout_s>]` | `—` | Pause chain until move ends; optional timeout → !E:timeout, cancel rest of chain. |
| `WH` | `Wait Homing` | `WH [<timeout_s>]` | `—` | Pause until homing ends; timeout same as WM. |
| `WP` | `Wait Pos` | `WP <pos> [<timeout_s>]` | `—` | Wait until axis-1 pos reached/overstepped; idle→immediate; 2nd arg=timeout. |
| `WC` | `Wait Cruise` | `WC [<timeout_s>]` | `—` | Wait until cruise (status M) or idle; optional timeout → !E:timeout. |
| `WN` | `Wait Not cruise` | `WN [<timeout_s>]` | `—` | Wait until not cruise M; idle/A/B→immediate; timeout same as WM. |

## V — Version

| Short | Phrase | Call | Reply | Description |
|-------|--------|------|-------|-------------|
| `VA` | `Version About` | `VA` | `VA:…` | About string (name, version, author). |
| `VF` | `Version FW` | `VF` | `VF:<version>` | Firmware version. |
| `VP` | `Version Protocol` | `VP` | `VP:<n>` | Protocol version (2). |

## Special

| Short | Phrase | Call | Reply | Description |
|-------|--------|------|-------|-------------|
| `HT` | `Halt` | `HT` | `—` | Immediate STEP abort; enable off; cancel waits and remaining ; chain. |
| `VG` | `Version GPIO` | `VG` | `VG:PIN_*=n (multi-line)` | Machine-readable pin map. Extra-axis pins if that axis is live. |
| `HL/$` | `Help` | `HL \| $` | `(multi-line table)` | Two-column table of all commands (short + phrase). |
| `?/#` | `Status now` | `? \| #` | `#<state> …` | Realtime compact status line (no newline). |
| `!/ESC` | `Soft stop now` | `! \| ESC` | `—` | Realtime soft stop (same urgency as MS). |

## Notes

- Chain with `;`. Realtime (no newline): `?`/`#` status, `!`/`ESC` soft stop, `Ctrl-X` soft reset. `#` is not a comment.
- Path mode (`PG`): most move/session cmds → `!E:busy`; allowed: `MS`/`HT`/`RB`/`PD`/`PN`/`I*`/`G*`/`V*`/`IG`/`HL`/`$`/`CG`/`BE`.
- `MJ` / Move Joy: signed % of `SS`; skip unchanged values; `SS`/`SA` live in joy-mode. Hold-to-jog: `SS` then `MJ ±100`, `MS` on release. See [motion-joy.md](../mc/motion-joy.md).
- Skip token `_` only (`MT`/`MB`/`PD`/`SL`/`SR`). Named `X`/`Y`/`Z` is an alternative (not mixed with positional). `SL`/`SR` `none` clears a side (effective = envelope when set). See [working-window.md](../mc/working-window.md).
- Soft limits / units: see config keys `slider_min_N`/`slider_max_N`, `steps_per_unit_N`, `unit_name`.
