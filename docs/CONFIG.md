# Configuration

Runtime **config** is held in RAM and persisted on LittleFS as `/mc.ini`.  
Factory defaults are compiled in `include/config_defaults.h` and mirrored in `data/mc.ini` (flashed via `uploadfs`).

**Session** values (cruise speed, accel, terminal, verbose) are used by S/G commands and motion.  
They are loaded from `init_*` config keys at boot. `SS`/`SA`/`ST`/`SV` change session only (not the file).  
Bare `SS`/`SA` reload that field from config init. `CS` updates config and the matching session field.

Legacy aliases on parse/`CS`/`CG`: `speed`→`init_speed`, `accel`→`init_accel`, `verbose`→`init_verbose`, `terminal`→`init_terminal`, `soft_min`→`slider_min`, `soft_max`→`slider_max`, `debug_level`→`init_debug_level`. Saves write only the new names.

## Protocol

| Command | Effect |
|---------|--------|
| `CS key value` | Set key (silent on success; `!E:cfg …` on error); updates session when applicable |
| `CG key` | Reply `CG:key=value` |
| `CG` | Dump all keys, one `CG:…` line each |
| `SS` / `SA` / `ST` / `SV` | Session set (see [PROTOCOL.md](PROTOCOL.md)) |
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
| `init_speed` | float mm/s | 50 | Cruise speed init (session via `SS`/`GS`); must be ≤ `max_speed` |
| `init_accel` | float mm/s² | 200 | Peak sine-ramp acceleration init; must be ≤ `max_accel` |
| `max_speed` | float mm/s | 100 | Speed ceiling (`SS` rejects above; planner also caps cruise) |
| `max_accel` | float mm/s² | 300 | Accel ceiling (`SA` rejects above) |
| `steps_per_mm` | float | 320 | Mechanics scaling |
| `slider_min` | float mm or `none` | 0 | Soft limit min (`none` / `-` disables) |
| `slider_max` | float mm or `none` | 600 | Soft limit max |
| `init_verbose` | 0/1 | 0 | Init for verbose `#…` push (~3 Hz); session via `SV`/`GV` |
| `init_terminal` | 0/1 | 0 | Init for Terminal Mode (expert USB sniffer + local echo); session via `ST`/`GT` — see [PROTOCOL.md](PROTOCOL.md#terminal-mode) |
| `init_debug_level` | 0..5 | 3 | USB-only debug verbosity (see above) |
| `WDT_use` | 0/1 | 1 | `1` = arm RP2040 WDT (2 s) from heartbeat init (before unlock `\n`); change takes effect after reboot |
| `DRV_STEP_active` | 0/1 | 1 | STEP active level (PIO program) |
| `DRV_DIR_active` | 0/1 | 1 | `1` = DIR high means +mm |
| `DRV_EN_active` | 0/1 | 0 | EN active level (`0` = low-active) |
| `SW_HOME_active` | 0/1 | 0 | Home switch active level |
| `SW_HOME_use` | 0/1 | 0 | `1` = enable `PIN_SW_HOME` for homing only (no halt) |
| `DRV_ERROR_active` | 0/1 | 0 | Driver error input active level |
| `SW_LIMIT_L_active` | 0/1 | 0 | Left hard-limit active level |
| `SW_LIMIT_R_active` | 0/1 | 0 | Right hard-limit active level |
| `SW_LIMIT_L_use` | 0/1 | 0 | `1` = enable left hard limit on `PIN_SW_LIMIT_L` |
| `SW_LIMIT_R_use` | 0/1 | 0 | `1` = enable right hard limit on `PIN_SW_LIMIT_R` |
| `EXT_0_active` … `EXT_9_active` | 0/1 | 1 | Active level for `PIN_EXT_n` (high-active default) |
| `home_mode` | 0..4 | 0 | Homing reference mode (see below) |
| `home_move_out` | float mm | 3 | Extra travel after leaving reference switch |
| `home_speed` | float mm/s | 25 | Cruise speed during homing |
| `home_accel` | float mm/s² | 20 | Acceleration during homing |
| `ramp_start_hz` | int | 1000 | First step rate leaving standstill |
| `stop_approach_hz` | int | 400 | Minimum step rate on the last few steps near target (floor; 0 disables) |
| `dir_change_pause_s` | float | 0.1 | Pause at 0 on reverse |
| `path_buffer_size` | int | 64000 | `PD` sample capacity (1..65536); see [PROTOCOL.md](PROTOCOL.md#p--path-host-authored-motion-path) |
| `init_path_slice_us` | int µs | 10000 | Default `PS` slice length (≥1000); session field set via `PS`; bare `PS` reloads this |

### Pin active levels

For every motor/switch/extender pin except UART: `0` = low-active (asserted when GPIO is 0), `1` = high-active (asserted when GPIO is 1).  
Helper: `config_pin_asserted(gpio_level, active)`. Extender outputs boot **inactive** (opposite of `EXT_n_active`); logical level is not persisted — only polarity is in `mc.ini`.

Removed legacy keys: `step_active_high`, `dir_invert`, `en_active_low`.

### Hard limits (`SW_LIMIT_*_use`)

GPIO numbers stay fixed in `pins.h`. Each side is independent:

- `SW_LIMIT_L_use=0` / `SW_LIMIT_R_use=0` (default): that switch is not fitted — pin not initialized for limits, no poll, no trip.
- `=1`: poll that pin with ~**20 ms** software debounce (bounce / Prellen).

On a stable assert: **immediate** stop (PIO FIFO cleared, no decelerate), driver disabled (`SE 0`), state `HARD_LIMIT`, wait/command chain canceled. Toward-limit moves are rejected (`!E:hard`). After `SE 1`, motion **away** from the switch is allowed; the latch clears when the switch is stably released. See [MOTION.md](MOTION.md).

### Watchdog (`WDT_use`) and status LED

`board_heartbeat_init()` runs **before** the unlock `\n` wait: it sets up `PIN_LED` and, if `WDT_use=1` (default), arms the RP2040 watchdog (**2 s** timeout). Every protocol/`unlock` poll (~5 ms) calls `board_heartbeat_tick()`, which always feeds the WDT and advances the LED state machine every **3rd** poll (~**67 Hz**, close to 64). A freeze of that path longer than 2 s (including a hung wait-for-`\n`) triggers a reboot.

`PIN_LED` is board-specific (see [PINS.md](PINS.md)): classic Pico onboard (`LED_BUILTIN` / GP25), Pico W external GP28 (`picow` env — CYW43 LED is unsafe under FreeRTOS), RP2040-Zero external GP14.

Until the first `\n` (UIC UART or USB CDC) and banner, the LED uses the **WAIT** pattern. After `board_heartbeat_ready()`, patterns follow `McState` (same source as verbose/`?`), priority: ERROR → HARD_LIMIT → HOMING → MOVING → DISABLED → IDLE → HOLD/other.

`CS WDT_use=0` updates RAM/`mc.ini`, but **disabling takes effect only after reboot** (the hardware WDT cannot be cleanly turned off once armed; while armed, the heartbeat keeps feeding it). Enabling via `CS` also applies after the next boot.

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


### Homing (`SW_HOME_use` / `home_mode`)

`SW_HOME_use=1` enables debounced polling of `PIN_SW_HOME` for the homing cycle only. Outside `MH`, the home switch is ignored (no halt, no motion block).

| Value | Behavior |
|-------|----------|
| `0` | No homing. `MH` returns silently (no motion) |
| `1` | `PIN_SW_HOME` as left reference (needs `SW_HOME_use=1`) |
| `2` | `PIN_SW_HOME` as right reference (needs `SW_HOME_use=1`) |
| `3` | `PIN_SW_LIMIT_L` as reference (needs `SW_LIMIT_L_use=1`) |
| `4` | `PIN_SW_LIMIT_R` as reference (needs `SW_LIMIT_R_use=1`) |

`MH` / `MoveHome` requires `SE 1`. Cycle: optional drive-out of an existing hard limit → seek toward reference at `home_speed` / `home_accel` → reverse off the switch plus `home_move_out` → set position to `slider_min` (modes 1/3) or `slider_max` (2/4). Seek is capped at 110% of `(slider_max − slider_min)`. Abort: `MS`/`Halt` (silent), `!E:home travel`, or `!E:home hard` (modes 1/2). See [MOTION.md](MOTION.md).

## Persistence

Config is held in RAM and persisted on **LittleFS** as `/mc.ini` (64 KiB FS partition).

1. **Boot:** `config_init_defaults()` → `board_config_load_from_fs()` (if `/mc.ini` exists) → `session_sync_from_config()`, then GPIO/motion init.
2. **`CS`:** update RAM (+ session for applicable keys), then flush all keys to `/mc.ini`. On flash failure the reply is `!E:cfg save failed` (RAM already updated).
3. **Factory image:** flash the FS once with `pio run -t uploadfs` so `data/mc.ini` is present (see [BUILD.md](BUILD.md)). If the file is missing, compiled defaults remain until the first successful `CS` write.
4. **`SD` / SetDebug** does **not** flush the file; persist `init_debug_level` with `CS init_debug_level …`.
5. **USB mass-storage editing** of `mc.ini` is a later milestone (`SingleFileDrive` on LittleFS — not FatFS).
