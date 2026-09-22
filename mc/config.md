<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Configuration";
  --doc-path: ".\\SliderDoc\\mc\\config.md";
}
</style>

# Configuration

Runtime **config** is held in RAM and persisted on LittleFS as `/mc.ini`.  
Factory defaults are compiled in `include/config_defaults.h` and mirrored in `data/mc.ini` (flashed via `uploadfs`).

**Session** values (cruise speed, accel, terminal, verbose) are used by S/G commands and motion.  
They are loaded from `init_*` config keys at boot. `SS`/`SA`/`ST`/`SV` change session only (not the file).  
Bare `SS`/`SA` reload that field from config init (`SA` loads `init_accel` into **both** live accel and decel). `CS` updates config and the matching session field (`CS init_accel` also writes both session ramps).

**No firmware aliases** for old unnumbered axis-1 keys (`max_speed`, `slider_min`, `home_mode`, `DRV_STEP_active`, …) or `axis2_use`. Those names return `!E:cfg`. **`CS axis` and `CS slider_*` are rejected.** Same-release synonyms only: `steps_per_mm_N`→`steps_per_unit_N`, `soft_min_N`/`soft_max_N`→packed `axis_min_N`/`axis_max_N`, plus session-init aliases `speed`→`init_speed`, `accel`→`init_accel`, `verbose`→`init_verbose`, `terminal`→`init_terminal`, `debug_level`→`init_debug_level`. Saves write only the canonical names (`MOTOR_*` / `SERVO_*`, not `slider_*`).

## Protocol

| Command | Effect |
|---------|--------|
| `CS key value` | Set key (silent on success; `!E:cfg …` on error); updates session when applicable |
| `CG key` | Reply `CG:key=value` |
| `CG` | Dump all keys, one `CG:…` line each |
| `SS` / `SA` / `ST` / `SV` | Session set (see [PROTOCOL.md](../contract/protocol.md)) |
| `GS` / `GA` / `GT` / `GV` | Session get |

Key names are matched case-insensitively.

### `init_debug_level` (USB-only traces)

Traces go to USB CDC only (never UIC UART), prefixed `D:…`. Session/`SD` and persistent `CS init_debug_level` both apply.

| Level | Emitted when ≥ level |
|-------|----------------------|
| 0 | Off |
| 2 | FIFO underrun (real starvation only, not the direction-change pause); target crossed (`D:overshoot`); move abandoned at a soft limit (`D:move_blocked`); restored diag after a watchdog reboot |
| 3 | Emergency `halt` |
| 4 | Reverse decelerate enter; direction-change pause |

Default is **3**.

## Keys

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `init_speed` | float mm/s | 50 | Cruise speed init (session via `SS`/`GS`); must be ≤ `max_speed_1` |
| `init_accel` | float mm/s² | 200 | Peak sine-ramp init for **both** session accel and decel (`SA` / `GA`); must be ≤ `max_accel_1` |
| `max_speed_1` | float mm/s | 100 | Axis-1 speed ceiling (`SS` rejects above; planner also caps axis-1 cruise, including `MJ`) |
| `max_accel_1` | float mm/s² | 300 | Axis-1 accel/decel ceiling (`SA` rejects either arg above; planner caps axis-1 ramps) |
| `max_speed_2` / `max_speed_3` | float mm/s | 100 | Axis-2 / axis-3 speed ceiling (planner / `MJ`; session `SS` still vs `max_speed_1`) |
| `max_accel_2` / `max_accel_3` | float mm/s² | 300 | Axis-2 / axis-3 accel ceiling |
| `steps_per_unit_1` | float | 320 | Axis-1 steps per user unit (mm, deg, …); synonym `steps_per_mm_1` |
| `motor_1_unit` … `motor_3_unit` | string | `mm` | Stored UIC label for that motor (max 7 printable ASCII chars; no `#`) |
| `servo_1_unit` … `servo_3_unit` | string | `deg` | Stored UIC label for that servo (same character rules) |
| `MOTOR_1_min` | float units or `none` | 0 | Motor-1 envelope min (`none` / `-` disables); boot → session `SL`; homing; packed `axis_min_1` / `soft_min_1` |
| `MOTOR_1_max` | float units or `none` | 600 | Motor-1 envelope max; boot → session `SR`; packed `axis_max_1` / `soft_max_1` |
| `init_verbose` | 0/1 | 0 | Init for verbose `#…` push (~3 Hz); session via `SV`/`GV` |
| `verbose_rate_hz` | int | 3 | Verbose push rate when session verbose is on |
| `init_terminal` | 0/1 | 0 | Init for Terminal Mode (expert USB sniffer + local echo); session via `ST`/`GT` — see [PROTOCOL.md](../contract/protocol.md#terminal-mode) |
| `init_debug_level` | 0..5 | 3 | USB-only debug verbosity (see above) |
| `WDT_use` | 0/1 | 1 | `1` = arm WDT (2 s) from heartbeat init (before unlock `\n`); change takes effect after reboot |
| `motors` | 1\|2\|3 | 1 | Live STEP/DIR count. `IA` / `CG axis` / banner use `motors+servos`. **Re-inits GPIO/PIO without `RB`.** |
| `servos` | 0..3 | 0 | RC servo PWM channels. Pico GP26/27/18 (18 steals EXT_4 when `servos>=3`); Zero GP21–23. PWM 100 Hz, wrap 65535; default 500–2500 µs → ~**1.25′** / 0.021° per count over ±135°. |
| `axis` | int (read) | 1 | Synthesized packed sum (`motors+servos`). `CG axis` and bare `CG` dump emit it. **`CS axis` is rejected.** |
| `axis_N_unit` | string (read) | *(from source)* | Packed label copied from `motor_N_unit` or the matching `servo_*_unit` (motors, then servos). Bare `CG` emits it for live channels only. **`CS axis_N_unit` is rejected.** |
| `name` | string | *(empty)* | Optional device name in welcome banner (max 31 printable ASCII chars; no `#`) |
| `DRV_STEP_1_active` | 0/1 | 1 | Axis-1 STEP active level (PIO program) |
| `DRV_STEP_2_active` | 0/1 | 1 | Axis-2 STEP polarity. **No `DRV_STEP_3_active`** — axis 3 STEP follows axis 2 (PIO has two polarity programs). |
| `DRV_DIR_1_active` … `DRV_DIR_3_active` | 0/1 | 1 | `1` = DIR high means +units |
| `DRV_EN_1_active` … `DRV_EN_3_active` | 0/1 | 0 | EN active level (`0` = low-active) |
| `DRV_ERROR_1_active` … `DRV_ERROR_3_active` | 0/1 | 0 | Driver error input active level |
| `SW_LIMIT_L_1_active` / `SW_LIMIT_R_1_active` | 0/1 | 0 | Axis-1 hard-limit active levels |
| `SW_LIMIT_L_1_use` / `SW_LIMIT_R_1_use` | 0/1 | 0 | `1` = enable that axis-1 hard limit |
| `SW_LIMIT_L_N_active` / `SW_LIMIT_R_N_use` | 0/1 | 0 | Same for axes 2 and 3 (`SW_LIMIT_R_3_use`, …). Digit is **before** `_active` / `_use`. |
| `BUZZER_use` | 0/1 | 0 | `1` = enable `PIN_BUZZER` (GP28) for `BE`; skipped if that GPIO is `PIN_LED` (Pico W) |
| `EXT_0_active` … `EXT_3_active` | 0/1 | 1 | Active level for `PIN_EXT_n` (high-active default); four extenders (`EO0`…`EO3`) |
| `home_mode_1` | 0..4 | 0 | Axis-1 homing reference mode (see below) |
| `home_move_out_1` | float mm | 3 | Extra travel after leaving reference switch |
| `home_speed_1` | float mm/s | 25 | Cruise speed during homing |
| `home_accel_1` | float mm/s² | 20 | Acceleration during homing |
| `steps_per_unit_2` / `_3` | float | 320 | Axis-2 / 3 steps per user unit (synonym `steps_per_mm_N`) |
| `MOTOR_2_min` / `MOTOR_3_min` | float or `none` | 0 | Motor-2 / 3 envelope min (packed `axis_min_N`) |
| `MOTOR_2_max` / `MOTOR_3_max` | float or `none` | 600 | Motor-2 / 3 envelope max |
| `SERVO_1_min` / `_2` / `_3` | float or `none` | -135 | Servo envelope min (degrees). Packed after motors. Maps onto `SERVO_N_min_pulse` unless `swap=1`. |
| `SERVO_1_max` / `_2` / `_3` | float or `none` | 135 | Servo envelope max (maps onto `SERVO_N_max_pulse` unless swap) |
| `SERVO_N_max_speed` / `SERVO_N_max_accel` | float | *(servo defaults)* | Servo planner ceilings |
| `SERVO_N_active` | 0/1 | 1 | Electrical PWM polarity: `1` = high pulse, `0` = invert |
| `SERVO_N_min_pulse` | int µs | 500 | Pulse at envelope min (400–2600; must stay `< max_pulse`). Digital default; analog typically 1000. |
| `SERVO_N_max_pulse` | int µs | 2500 | Pulse at envelope max. Analog typically 2000. |
| `SERVO_N_swap` | 0/1 | 0 | `1` = reverse mechanical sense (min angle ↔ long pulse). Not the same as `active`. |
| `home_mode_2` / `home_mode_3` | 0..4 | 0 | Motor-2 / 3 homing mode (servos are not homed) |
| `home_move_out_N` / `home_speed_N` / `home_accel_N` | float | *(same as axis 1)* | Homing parameters for axes 2 and 3 |
| `ramp_start_hz` | int | 1000 | First step rate leaving standstill |
| `stop_approach_hz` | int | 400 | Minimum step rate on the last few steps near target (floor; 0 disables) |
| `dir_change_pause_s` | float | 0.1 | Pause at 0 on reverse |
| `path_buffer_size` | int | 32000 | Logical `PD` sample cap **per axis** (≤ pool/`n`); pool is 65536 samples split by live `axis`. See [PROTOCOL.md](../contract/protocol.md#p--path-host-authored-motion-path) |
| `init_path_slice_us` | int µs | 10000 | Default `PS` slice length (≥1000); session field set via `PS`; bare `PS` reloads this |

RC servo pulse defaults are **500–2500 µs** (modern digital, ~1.25′ over ±135°). Classic analog: `CS SERVO_1_min_pulse 1000` / `CS SERVO_1_max_pulse 2000` (~2.5′). `SERVO_N_swap 1` reverses horn sense; `SERVO_N_active` only inverts the PWM level.

### Pin active levels

For every motor/switch/extender pin except UART: `0` = low-active (asserted when GPIO is 0), `1` = high-active (asserted when GPIO is 1).  
Helper: `config_pin_asserted(gpio_level, active)`. Extender outputs boot **inactive** (opposite of `EXT_n_active`); logical level is not persisted — only polarity is in `mc.ini`.

Removed legacy keys: `step_active_high`, `dir_invert`, `en_active_low`.

### Hard limits (`SW_LIMIT_*_N_use`)

GPIO numbers stay fixed in `pins.h`. Each side and axis is independent:

- `SW_LIMIT_L_1_use=0` / `SW_LIMIT_R_1_use=0` (default): that switch is not fitted — pin not initialized for limits, no poll, no trip.
- `=1`: poll that pin with ~**20 ms** software debounce (bounce / Prellen). Same pattern for `_2` / `_3`.

On a stable assert: **immediate** stop (PIO FIFO cleared, no decelerate), driver disabled (`SE 0`), state `HARD_LIMIT`, wait/command chain canceled. Toward-limit moves are rejected (`!E:hard`). After `SE 1`, motion **away** from the switch is allowed; the latch clears when the switch is stably released. See [MOTION.md](MOTION.md).

### Watchdog (`WDT_use`) and status LED

`board_heartbeat_init()` runs **before** the unlock `\n` wait: it sets up `PIN_LED` and, if `WDT_use=1` (default), arms the RP2040 watchdog (**2 s** timeout). Every protocol/`unlock` poll (~5 ms) calls `board_heartbeat_tick()`, which always feeds the WDT and advances the LED state machine every **3rd** poll (~**67 Hz**, close to 64). A freeze of that path longer than 2 s (including a hung wait-for-`\n`) triggers a reboot.

`PIN_LED` is board-specific (see [PINS.md](PINS.md)): classic Pico onboard (`LED_BUILTIN` / GP25), Pico W / Pico 2 W external GP28 (`picow` / `pico2w` — CYW43 LED is unsafe under FreeRTOS), RP2040-Zero / RP2350 Mini external GP29 plus onboard WS2812 on `PIN_NEOPIXEL` GP16.

Until the first `\n` (UIC UART or USB CDC) and banner, the GPIO LED uses the **WAIT** pattern. After `board_heartbeat_ready()`, GPIO patterns follow `McState` (same source as verbose/`?`), priority: ERROR → HARD_LIMIT → HOMING → MOVING → DISABLED → IDLE → HOLD/other.

When `PIN_NEOPIXEL` ≠ `PIN_LED`, the WS2812 shows JKSlider-style colours (brightness 32, protocol task only; STEP PIO stays on pio0). Priority (top wins):

| Priority | Status | Colour |
|----------|--------|--------|
| 1 | `ERROR` / `DRV_ERROR` | Solid red `255,0,0` |
| 2 | FIFO underrun (latched ~1.5 s) | Fast red blink `255,0,0` / off, 80 ms |
| 3 | `HARD_LIMIT` | Fast red blink `255,0,0` / off, 80 ms |
| 4 | `HOMING` | Red blink `255,0,0` / off, 250 ms |
| 5 | Path play (`PATH`) | Cyan `0,200,200` |
| 6 | Accel / decel | Yellow `255,255,0` |
| 7 | Moving cruise | Green `0,255,0` |
| 8 | Disabled | Dim orange `31,11,0` |
| 9 | Idle, UIC UART linked | Dim white `31,31,31` |
| 10 | Idle, USB-only / no UIC | Dim purple `31,0,31` |
| 11 | Startup (before unlock `\n` on UIC UART or USB) | Rainbow until unlock |

UIC-linked means the unlock `\n` arrived on UART, or any UART RX since then (no idle timeout). USB-only bench stays dim purple at idle.

`CS WDT_use=0` updates RAM/`mc.ini`, but **disabling takes effect only after reboot** (the hardware WDT cannot be cleanly turned off once armed; while armed, the heartbeat keeps feeding it). Enabling via `CS` also applies after the next boot (`RB` / power-cycle).

#### LED timing (counter beats, `#`=ON `.`=OFF)

Graphs are in **counter** units (one step every 3rd 5 ms poll). Wall-clock rates scale with ~67 Hz (e.g. “4 Hz” ≈ 4.2 Hz).

```
tick:  0-------1-------2-------3-------4-------5-------6-------7-------8
       01234567890123456789012345678901234567890123456789012345678901234

WAIT      !(c&0x20)       duty 32/64   ~1 Hz 50% (before unlock \n)
  ################################................................#

ERROR     (c&0x0C)!=0     duty 48/64   ~4 Hz bright
  ....############....############....############....############.

HARD_LIM  (c&0x0C)==0     duty 16/64   ~4 Hz dark
  ####............####............####............####............#

HOMING    (c&0x03)==0     duty 16/64   ~16 Hz dark
  #...#...#...#...#...#...#...#...#...#...#...#...#...#...#...#...#

MOVING    (c&0x03)!=0     duty 48/64   ~16 Hz bright
  .###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.###.

DISABLED  (c&0x3F)==0     duty 1/64    ~1 Hz short flash
  #...............................................................#

IDLE      (c&0x3C)==0     duty 4/64    ~1 Hz longer flash
  ####............................................................#

HOLD/else (c&0x30)==0     duty 16/64   ~1 Hz longer still
  ################................................................#
```


### Homing (`home_mode_N`)

There is no dedicated home-switch pin. Homing uses a hard limit (modes 1/2) or driver stall / `DRV_ERROR` (modes 3/4). `home_mode_N=0` plus `SP` declares origin without a switch. Use `home_mode_1` / `home_mode_2` / `home_mode_3`.

| Value | Behavior |
|-------|----------|
| `0` | No homing. `MH` returns silently. Use `SP` to declare “here is zero.” |
| `1` | Seek `SW_LIMIT_L` (needs `SW_LIMIT_L_N_use=1`); finish at `MOTOR_N_min` |
| `2` | Seek `SW_LIMIT_R` (needs `SW_LIMIT_R_N_use=1`); finish at `MOTOR_N_max` |
| `3` | Seek left until `DRV_ERROR`; EN pulse; wait clear; drive out; finish at `MOTOR_N_min` |
| `4` | Seek right until `DRV_ERROR`; same stall cycle; finish at `MOTOR_N_max` |

`SW_HOME_*` keys are gone (not remapped). `CS home_mode_N 3` / `4` means stall-home.

`MH` / Move Home requires `SE 1`. Optional motor arg `1` (default), `2`, or `3` when that motor is live. Servos cannot be homed. Limit-home cycle: optional drive-out of the opposite hard limit → seek toward the reference → reverse off the switch plus `home_move_out_N` → set pose. Stall-home: seek until `DRV_ERROR` → **do not** take the EMO halt path → pulse `DRV_EN` (~200 ms) → wait until the error line is stably clear → drive out `home_move_out_N`. Seek is capped at 110% of `(MOTOR_N_max − MOTOR_N_min)`. Abort: `MS`/`ME` (silent), `!E:home travel`, `!E:home hard` (wrong limit), `!E:home stall` (error never clears). Chip notes: [homing-switches.md](../components/homing-switches.md). See [MOTION.md](MOTION.md).

### Live counts (`motors` / `servos`)

`motors` is `1`, `2`, or `3` (default `1`). `servos` is `0`..`3` (default `0`). Packed `IA` / `CG axis` = sum (1..6). Extra motors are independent STEP/DIR planner axes; servos are PWM channels on the same packed protocol. Session cruise/accel (`SS`/`SA`) follow the **time-sync master**. Mechanics and envelopes use `MOTOR_N_*` / `SERVO_N_*`. Welcome banner is `{motors}+{servos} axis`. `IP` / `GL` / `GR` return pipe groups. Pin map: [pins.md](pins.md). Narrative: [dual-movement.md](dual-movement.md). Joystick: [motion-joy.md](motion-joy.md).

`CS motors` / `CS servos` update RAM/`mc.ini` and **re-init GPIO / PIO / PWM immediately** (no `RB`). **`CS axis` is rejected.**

## Persistence

Config is held in RAM and persisted on **LittleFS** as `/mc.ini` (64 KiB FS partition).

1. **Boot:** `config_init_defaults()` → `board_config_load_from_fs()` (if `/mc.ini` exists) → `session_sync_from_config()`, then GPIO/motion init.
2. **`CS`:** update RAM (+ session for applicable keys), then flush all keys to `/mc.ini`. On flash failure the reply is `!E:cfg save failed` (RAM already updated).
3. **Factory image:** flash the FS once with `pio run -t uploadfs` so `data/mc.ini` is present (see [BUILD.md](BUILD.md)). If the file is missing, compiled defaults remain until the first successful `CS` write.
4. **`SD` / SetDebug** does **not** flush the file; persist `init_debug_level` with `CS init_debug_level …`.
5. **USB mass-storage editing** of `mc.ini` is a later milestone (`SingleFileDrive` on LittleFS — not FatFS).
