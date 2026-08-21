# SliderMC Command Cheat Sheet

Firmware V1.0. Same groups as the [printable sheet](command-cheatsheet.html).
Canonical prose: [protocol.md](protocol.md). Dual-axis timing: [dual-movement.md](../mc/dual-movement.md).

Regenerate: `python tools/render_command_cheatsheet.py`

- **Call** — send this (brackets = optional; bare = omit args).
- **Reply** — typical success line; `—` = silent (errors still `!E:…`).

## S — Set (session)

| Short | Long | Call | Reply | Description |
|-------|------|------|-------|-------------|
| `SS` | `SetSpeed` | `SS [<v>]` | `—` | Cruise speed mm/s (≤ max_speed); bare reloads init_speed; live on next fill. Dual MT: axis1=session, axis2×ratio. |
| `SA` | `SetAccel` | `SA [<a>]` | `—` | Peak accel mm/s² (≤ max_accel); bare reloads init_accel; live on next fill. Dual MT: same ratio scaling as SS. |
| `SE` | `SetEnable` | `SE [0\|1]` | `—` | Driver enable 0\|1; bare toggles; required before motion; off = hard stop. |
| `ST` | `SetTerminal` | `ST [0\|1]` | `—` | Terminal Mode 0\|1; bare toggles; local echo + UART sniff to USB (expert). |
| `SV` | `SetVerbose` | `SV [0\|1]` | `—` | Verbose #… push 0\|1; bare toggles; ~3 Hz (rate via verbose_rate_hz). |
| `SD` | `SetDebug` | `SD [0..5]` | `—` | USB-only debug level 0..5; bare restores default; never on UIC UART. |

## G — Get (session)

| Short | Long | Call | Reply | Description |
|-------|------|------|-------|-------------|
| `GS` | `GetSpeed` | `GS` | `GS:<mm/s>` | Current session cruise speed. |
| `GA` | `GetAccel` | `GA` | `GA:<mm/s2>` | Current session acceleration. |
| `GE` | `GetEnable` | `GE` | `GE:0\|1` | Driver enable state. |
| `GT` | `GetTerminal` | `GT` | `GT:0\|1` | Terminal Mode state. |
| `GV` | `GetVerbose` | `GV` | `GV:0\|1` | Verbose push state. |
| `GD` | `GetDebug` | `GD` | `GD:<0..5>` | USB debug level. |

## I — Is / status

| Short | Long | Call | Reply | Description |
|-------|------|------|-------|-------------|
| `IM` | `IsMoving` | `IM` | `IM:0\|1` | Moving or settling on any active axis. |
| `IH` | `IsHoming` | `IH` | `IH:0\|1` | Homing cycle active. |
| `IL` | `IsLimit` | `IL` | `IL:0\|1` | At soft-limit position (axis1). |
| `IE` | `IsError` | `IE` | `IE:0\|1` | PIN_DRV_ERROR / EMO latched. |
| `IP` | `IsPosition` | `IP` | `IP:<pos> [<pos2>]` | Axis-1 position; second field when axis2_use=1. |
| `IA` | `IsAxis` | `IA` | `IA:1\|2` | Active axis count (config_axis2_enabled). |
| `IT` | `IsTarget` | `IT` | `IT:<pos>\|-` | Axis-1 seek target, or - if none / soft-stop. |
| `IR` | `IsReady` | `IR` | `IR:0\|1` | 1 only if idle, not homing, enabled, and not waiting. |
| `IW` | `IsWaiting` | `IW` | `IW:0\|1` | 1 if any W / WM / WH wait is active. |
| `ID` | `IsDiag` | `ID` | `ID:underrun=N peak_hz=… overshoot=… fifo_min=…` | Motion diag counters (FIFO underrun, peak STEP Hz, …). |
| `IZ` | `IsReset` | `IZ` | `IZ:<reason>` | Last chip reset: power\|wdt\|run\|soft\|debug\|brownout\|… |
| `IX` | `Pinout` | `IX` | `(multi-line table)` | ASCII GP / name / desc (≤80 cols). Axis-2 rows only if axis2 on. |

## M — Movement

| Short | Long | Call | Reply | Description |
|-------|------|------|-------|-------------|
| `MT` | `MoveTo` | `MT <pos> [<pos2>]` | `—` | Absolute user units; optional 2nd axis; skip none/N/_/*; needs SE; live-retarget. Dual: time-sync ratio. |
| `M` | `Move` | `M <delta> [<delta2>]` | `—` | Relative move (alias MoveBy); same dual/skip rules as MT. |
| `ML` | `MoveLeft` | `ML [0\|1\|2]` | `—` | Jog −; mask 0=both, 1=axis1, 2=axis2 when axis2 on; soft-stop MS/!. |
| `MR` | `MoveRight` | `MR [0\|1\|2]` | `—` | Jog +; mask same as ML; soft-stop MS/!. |
| `MH` | `MoveHome` | `MH [1\|2]` | `—` | Homing; axis 1 (default) or 2; no-op if home_mode=0; cancel MS/H. |
| `MS` | `MoveStop` | `MS` | `—` | Soft decelerate both axes; keeps enable; does not cancel waits. Dual: scaled accel kept. |

## P — Path

| Short | Long | Call | Reply | Description |
|-------|------|------|-------|-------------|
| `PC` | `PathClear` | `PC` | `—` | Clear path buffer (count→0); !E:busy while PG active. |
| `PD` | `PathData` | `PD <um> [<um2>]` | `—` | Append signed µm sample(s); optional axis2; skip→0; OK while PG (live stream). |
| `PG` | `PathGo` | `PG` | `—` | Play buffer from sample 0; needs SE; !E:empty\|busy\|disabled. MS/H ends path. |
| `PN` | `PathNumber` | `PN` | `PN:<count>` | Samples in buffer; allowed during PG. |
| `PS` | `PathSlice` | `PS [<us>]` | `—` | Slice length µs (≥1000); bare→init_path_slice_us; !E:busy while PG. |

## X — Extender

| Short | Long | Call | Reply | Description |
|-------|------|------|-------|-------------|
| `X0–3` | `Ext0–3` | `Xn [0\|1]` | `—` | Ext out n logical 0\|1; bare toggles; glued X00≡X0 0; OK during EMO. X4+ rejected. |

## C — Config

| Short | Long | Call | Reply | Description |
|-------|------|------|-------|-------------|
| `CS` | `ConfigSet` | `CS <key> <value>` | `—` | Persist key to mc.ini; silent ok. axis2_use / WDT_use need RB to take HW effect. |
| `CR` | `ConfigReset` | `CR` | `—` | Reset all config to compiled defaults and save mc.ini. |
| `CG` | `ConfigGet` | `CG [<key>]` | `CG:<key>=<value>` | One key, or bare dumps all keys (multi-line). |
| `RB` | `Reboot` | `RB` | `—` | Soft MCU reset (no power cycle); EN off first. After CS axis2_use. |

## W — Wait

| Short | Long | Call | Reply | Description |
|-------|------|------|-------|-------------|
| `W` | `Wait` | `W [<sec>]` | `—` | Delay then continue ; chain; bare→1 s; never !E:timeout. |
| `WM` | `WaitMoving` | `WM [<timeout_s>]` | `—` | Pause chain until move ends; optional timeout → !E:timeout, cancel rest of chain. |
| `WH` | `WaitHoming` | `WH [<timeout_s>]` | `—` | Pause until homing ends; timeout same as WM. |

## V — Version

| Short | Long | Call | Reply | Description |
|-------|------|------|-------|-------------|
| `VA` | `VersionAbout` | `VA` | `VA:…` | About string (name, version, author). |
| `VF` | `VersionFW` | `VF` | `VF:<version>` | Firmware version. |
| `VP` | `VersionProtocol` | `VP` | `VP:<n>` | Protocol version. |

## Special

| Short | Long | Call | Reply | Description |
|-------|------|------|-------|-------------|
| `H/HT` | `Halt` | `H \| HT` | `—` | Immediate STEP abort; enable off; cancel waits and remaining ; chain. |
| `P` | `Pins` | `VG \| P` | `VG:PIN_*=n (multi-line)` | Machine-readable pin map (alias VersionGPIO). Axis-2 pins if axis2 on. |
| `$/HL` | `Help` | `$ \| HL \| Help` | `(multi-line table)` | ASCII table of all commands (≤80 columns). |

## Notes

- Chain with `;`. Realtime (no newline): `?` status, `!` soft stop, `Ctrl-X` soft reset.
- Path mode (`PG`): most move/session cmds → `!E:busy`; allowed: `MS`/`H`/`RB`/`PD`/`PN`/`I*`/`G*`/`V*`/`IX`/`Help`/`CG`.
- Soft limits / units: see config keys `slider_min`/`max`, `steps_per_unit`, `unit_name`.
