# Build and VS Code setup

## Prerequisites (Windows)

1. Install [VS Code](https://code.visualstudio.com/).
2. Install the **PlatformIO IDE** extension (`platformio.platformio-ide`).
3. Optionally install **Microsoft C/C++** (`ms-vscode.cpptools`).
4. Open **PlatformIO: Home** once so PlatformIO Core installs.
5. Connect a Pico over USB (Windows usually loads CDC drivers automatically).
6. For host protocol tests, install GCC (`g++`), e.g. MSYS2 mingw-w64.

## Open the project

**File → Open Folder** → the `SliderMC` repository root (not `SliderCtrl`).

## Build and upload

- Envs (PlatformIO):
  - `pico` — Raspberry Pi Pico (`board = rpipico`); `BOARD_PICO` default in `pins.h`
  - `picow` — Raspberry Pi Pico W (`board = rpipicow`); `-DBOARD_PICO_W`, external `PIN_LED` on **GP28** (CYW43 onboard LED is not used under FreeRTOS)
  - `rp2040zero` — Waveshare RP2040-Zero (`board = waveshare_rp2040_zero`); `-DBOARD_RP2040_ZERO`
- earlephilhower core, FreeRTOS enabled via `PIO_FRAMEWORK_ARDUINO_ENABLE_FREERTOS`.
- PlatformIO toolbar: **Build** / **Upload** / **Monitor** (select the env matching your hardware).
- USB CDC carries the ASCII CLI (same protocol as UART).
- UIC UART is **1 000 000** baud on `PIN_UART_TX` / `PIN_UART_RX` (see PINS.md).
- Close the serial monitor (or SliderCLI) before **Upload** — the 1200 baud reset needs the CDC COM port free.

### Windows upload: picotool / `upload_port` error

Default `upload_protocol` is **picotool**. On Windows that tool needs a **WinUSB** driver on the Pico’s BOOTSEL vendor interface. Without it, PlatformIO Upload fails even though dragging a `.uf2` onto the `RPI-RP2` drive works.

Typical symptoms:

```text
Looking for upload port...
Error: Please specify `upload_port` for environment or use global `--upload-port` option.
```

or (running picotool by hand while the board is in BOOTSEL):

```text
Device ... appears to be a RP2040 device in BOOTSEL mode, but picotool
was unable to connect. You may need to install a driver via Zadig.
```

**Cause:** BOOTSEL exposes a composite USB device (`VID_2E8A` / `PID_0003`):

| Interface | Role | Needed for |
|-----------|------|------------|
| MI_00 | Mass storage (`RPI-RP2`) | Manual `.uf2` copy |
| MI_01 | `RP2 Boot` vendor | picotool / PlatformIO Upload |

If MI_01 has no WinUSB driver (Device Manager shows Error / no driver), picotool is blind. The upload script then tries to find a CDC COM port for a 1200 baud reset; a board already in BOOTSEL has no COM port → `upload_port` error. With firmware running, COM autodetection may succeed and reset into BOOTSEL, then the same picotool failure still appears.

**Fix (recommended):** install WinUSB with [Zadig](https://zadig.akeo.ie/):

1. Put the Pico in BOOTSEL (hold BOOTSEL, plug USB, release). `RPI-RP2` should appear.
2. Run Zadig as Administrator → **Options → List All Devices**.
3. Select **`RP2 Boot (Interface 1)`** only (`2E8A` / `0003`, Interface **1**).
4. Target driver: **WinUSB** → **Install Driver** / **Replace Driver**.
5. Do **not** replace the driver on the composite parent or on Interface 0 — that breaks the `RPI-RP2` drag-and-drop path.
6. Verify: `picotool info -d` should print RP2040 device info and exit 0. In Device Manager, `RP2 Boot` should be OK under USB devices.

After that, **Upload** from a running MC firmware (CDC COM present) resets via 1200 baud, flashes with picotool, and reboots. Manual `.uf2` copy remains available as a fallback.

**Alternative:** set `upload_protocol = mbed` in `platformio.ini` so PlatformIO copies `firmware.uf2` to the `RPI-RP2` drive (no WinUSB). Less reliable timing after reset, and **Upload Filesystem** (`uploadfs`) still needs picotool.

## FreeRTOS

Tasks are started from `motion_tasks_start()` in `src/motion/motion_task.cpp`:

- `feed` — FIFO fill
- `plan` — planner tick
- `proto` — USB + UART protocol, status LED heartbeat via `PIN_LED` (~67 Hz state patterns), optional WDT feed

`loop()` stays idle so it cannot starve motion. The protocol task arms the LED/WDT in `board_heartbeat_init()` **before** waiting for unlock `\n` (UIC UART or USB CDC); after the banner, LED patterns follow McState via `PIN_LED`. See [CONFIG.md](CONFIG.md#watchdog-wdt_use-and-onboard-led) and [PINS.md](PINS.md) for board-specific LED pins (Pico onboard / Pico W GP28 external / Zero GP14 external).

## Host protocol tests

No Pico required:

```powershell
powershell -File scripts/run_host_tests.ps1
```

Uses `src/motion/motion_stub.cpp` instead of the on-device planner/PIO path.

## Config file / filesystem

- Defaults: `data/mc.ini` and `include/config_defaults.h`
- On-device FS: **LittleFS**, 64 KiB (`board_build.filesystem_size = 0x10000` in `platformio.ini`)
- Load/save: `src/board/littlefs_port.cpp` — boot loads `/mc.ini`; each successful `CS` rewrites it
- Flash the factory FS image (includes `data/mc.ini`) after changing defaults or on a fresh Pico:

```powershell
pio run -t uploadfs -e pico
```

Typical first-time sequence: **Build** → **Upload** (firmware) → **Upload Filesystem** (`uploadfs`) → **Monitor**.  
Flash the factory FS image for the matching env, e.g. `pio run -t uploadfs -e pico` (or `-e picow` / `-e rp2040zero`).  
Manual check: `CS init_speed 25`, reset, `CG init_speed` → `CG:init_speed=25`.

## Publish to GitHub

If this clone has no `origin` yet and [GitHub CLI](https://cli.github.com/) is installed:

```powershell
gh auth login
powershell -File scripts/create_github_repo.ps1
```
