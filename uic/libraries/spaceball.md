# SpaceBall API

MicroPython UART reader for classic serial **6DOF** devices: Magellan / SpaceMouse, Spaceball 2003/3003/4000, and SpaceOrb 360. Implementation lives in [`SpaceBall.py`](../SpaceBall.py).

Not for USB HID devices and not for the modern 3Dconnexion SpaceMouse Module binary UART framing (`0x96`…`0x8D`).

Defaults: **UART1**, **GP8** TX / **GP9** RX, **9600** baud, 8N1.

---

## Class `SpaceBall`

### Protocol constants

| Constant | Value | Device family |
|----------|------:|---------------|
| `PROTO_AUTO` | 0 | Autodetect (listen + probe; late lock on first unambiguous packet) |
| `PROTO_MAGELLAN` | 1 | Magellan / classic SpaceMouse (ASCII `'d'` / `'k'`) |
| `PROTO_SPACEBALL` | 2 | Spaceball 2003 / 3003 / 4000 FLX |
| `PROTO_SPACEORB` | 3 | SpaceOrb 360 / Avenger |

### Constructor

```python
SpaceBall(pin_TX=8, pin_RX=9, protocol=0, auto=True, callback=None)
```

| Arg | Default | Meaning |
|-----|---------|---------|
| `pin_TX` | `8` | Pico TX → device RX (via MAX232) |
| `pin_RX` | `9` | Pico RX ← device TX (via MAX232) |
| `protocol` | `0` | See constants above |
| `auto` | `True` | Prefer asyncio background RX (`await start()`); `False` = call `poll()` yourself |
| `callback` | `None` | Optional callable `fn(sb)` after each complete axis/button packet |

On Magellan / Spaceball (forced or after auto lock), the constructor sends the usual init / probe strings. SpaceOrb needs no host init.

### Public members

| Member | Type | Meaning |
|--------|------|---------|
| `trans_x`, `trans_y`, `trans_z` | `int` | Last translation sample (0 at rest) |
| `rot_x`, `rot_y`, `rot_z` | `int` | Last rotation sample (0 at rest) |
| `buttons` | `int` | Bitmask of pressed buttons (see [Buttons](#buttons)) |
| `protocol` | `int` | Locked / forced protocol (`PROTO_*`) |
| `callback` | callable or `None` | Optional update hook (see below) |

### Methods

| Method | Role |
|--------|------|
| `poll()` | Drain UART RX into the parsers; update public axes / buttons |
| `async start()` | Start asyncio RX task (`poll()` every 1 ms) |
| `async stop()` | Cancel the RX task |
| `deinit()` | Release the UART |
| `on_data()` | Hook after publics update — override in a subclass (default no-op) |

With `auto=True`, call `await sb.start()` so the FIFO is drained in the background. With `auto=False`, call `poll()` often enough (about 1 kHz is comfortable at 9600 baud) and print or consume axes less often.

### Update hooks (`on_data` / `callback`)

After a complete decoded **axis or button** packet updates the public fields, the library calls `on_data()`, then `callback(self)` if set. Version / reset / probe-only traffic does not notify.

Keep the handler short: with `auto=True` it runs inside the asyncio RX task.

```python
class MyBall(SpaceBall):
    def on_data(self):
        print(self.trans_x, self.buttons)

sb = MyBall(auto=True)
# or without subclassing:
sb = SpaceBall(callback=lambda s: print(s.trans_z), auto=False)
```

---

## Examples

### Sync poll (`SpaceBall.py` `__main__`)

Poll often; print every 250 ms.

```python
sb = SpaceBall(pin_TX=8, pin_RX=9, protocol=0, auto=False)
print("protocol:", sb.protocol)
next_print = time.ticks_add(time.ticks_ms(), 250)
try:
    while True:
        sb.poll()
        now = time.ticks_ms()
        if time.ticks_diff(now, next_print) >= 0:
            print(
                "T", sb.trans_x, sb.trans_y, sb.trans_z,
                "R", sb.rot_x, sb.rot_y, sb.rot_z,
                "B", sb.buttons, "P", sb.protocol,
            )
            next_print = time.ticks_add(now, 250)
        time.sleep_ms(5)
finally:
    sb.deinit()
```

### Asyncio (`SpaceBallAsyncExample.py`)

Background RX at 1 ms; foreground print every 250 ms.

```python
import uasyncio as asyncio
from SpaceBall import SpaceBall

async def demo():
    sb = SpaceBall(pin_TX=8, pin_RX=9, protocol=0, auto=True)
    await sb.start()
    try:
        while True:
            print(
                "T", sb.trans_x, sb.trans_y, sb.trans_z,
                "R", sb.rot_x, sb.rot_y, sb.rot_z,
                "B", sb.buttons, "P", sb.protocol,
            )
            await asyncio.sleep_ms(250)
    finally:
        await sb.stop()
        sb.deinit()

asyncio.run(demo())
```

Copy [`SpaceBall.py`](../SpaceBall.py) and [`SpaceBallAsyncExample.py`](../SpaceBallAsyncExample.py) to the Pico, then:

```text
import SpaceBallAsyncExample
SpaceBallAsyncExample.run()
```

---

## Wiring — MAX232 / MAX3232

Classic serial SpaceMouse / SpaceBall / SpaceOrb need **RS-232 levels**, not raw Pico TTL. Use a **MAX232** (5 V) or **MAX3232** (3V3-friendly) with the charge-pump capacitors from the chip datasheet.

**Power:** the device takes power from the RS-232 connector — typically **DTR** and/or **RTS** (DE-9 pins **4** and/or **7**), about **9–12 V**, roughly **5 mA**. The MAX232 / MAX3232 `V+` charge-pump rail often supplies that; an external 9–12 V supply on pins 4/7 also works. See the [OpenMoCo Serial-Connection wiki](https://os.mbed.com/teams/OpenMoCo/code/SpaceBall/wiki/Serial-Connection).

When the MAX232 is powered from **5 V**, put a **1 kΩ series resistor** between `R1OUT` and the Pico RX pin so a 5 V logic high does not overdrive the 3V3 GPIO. With a **3V3 MAX3232**, omit the resistor (wire `R1OUT` straight to GP9).

### ASCII graph

```
 Pico (3V3 TTL)                    MAX232 (5V) / MAX3232 (3V3)     DE-9 male (to SpaceMouse)
 ----------------                  ----------------------------     -------------------------
 GP8  UART1 TX  -----------------> T1IN ---- T1OUT --------------> pin 2 RD  (device RX)
 GP9  UART1 RX  <----[1kOhm]------ R1OUT ---- R1IN <-------------- pin 3 TD  (device TX)
                    ^ only when MAX232 VCC = 5 V
                    (omit / short when using 3V3 MAX3232)
 5V or 3V3 / GND ---- VCC/GND + C1..C4 per datasheet
                                   V+ (~+9V) --------------------> pin 4 DTR and/or pin 7 RTS (device power)
                                   GND --------------------------> pin 5 SG
```

### Connection table

| Pico | Level shifter | DE-9 pin | Function |
|------|---------------|----------|----------|
| GP8 (UART1 TX) | T1IN → T1OUT | 2 RD | Host → device data |
| GP9 (UART1 RX) | R1OUT → [1 kΩ if 5 V] → GP9; R1IN ← | 3 TD | Device → host data |
| 5 V or 3V3 | VCC | — | Chip supply (MAX232 = 5 V, MAX3232 = 3V3) |
| GND | GND | 5 SG | Signal ground |
| — | V+ (~+9 V) | 4 DTR and/or 7 RTS | **Device power** |
| — | C1…C4 | — | Charge-pump caps per datasheet |

---

## DE-9 (RS-232) connector — SpaceMouse / SpaceBall

Male DE-9 toward the device (standard DTE-style labelling from the PC/host side):

| Pin | Signal | Role for this setup |
|----:|--------|---------------------|
| 1 | DCD | unused |
| 2 | RD | host → device (Pico TX via MAX232) |
| 3 | TD | device → host (Pico RX via MAX232) |
| 4 | DTR | **device power** (~9–12 V) |
| 5 | SG | signal ground |
| 6 | DSR | unused |
| 7 | RTS | **device power** (alt / alongside DTR) |
| 8 | CTS | unused |
| 9 | RI | unused |

---

## Buttons

`buttons` is a single `int` bitmask. Bit *n* set means that logical button is pressed. Packet fields are combined with `|` (bitwise OR). Spaceball classic also ORs **two raw packet bits** into logical button 1.

### Magellan / SpaceMouse (`'k'` packet)

After nibble-crunch of the three data bytes `n1`, `n2`, `n3`:

```text
buttons = (n1 << 1) | (n2 << 5) | n3
```

(Same packing as Linux [`magellan.c`](https://raw.githubusercontent.com/torvalds/linux/master/drivers/input/joystick/magellan.c).) Overlapping shifts mean adjacent nibble fields OR into shared bit positions. Result bits 0–8 map to Magellan keys:

| `buttons` bit | Magellan / SpaceMouse |
|--------------:|------------------------|
| 0 | Button 1 |
| 1 | Button 2 |
| 2 | Button 3 |
| 3 | Button 4 |
| 4 | Button 5 |
| 5 | Button 6 |
| 6 | Button 7 |
| 7 | Button 8 |
| 8 | Button A / `*` |

### Spaceball classic (`'K'` packet, 2003 / 3003)

Linux ORs two hardware flags into BTN_1: `(d2 & 0x01) || (d2 & 0x20)` → our bit 0. Remaining buttons are single flags:

| `buttons` bit | Spaceball classic | Raw packet |
|--------------:|-------------------|------------|
| 0 | Button 1 | `d2` bit0 **OR** `d2` bit5 |
| 1 | Button 2 | `d2` bit1 |
| 2 | Button 3 | `d2` bit2 |
| 3 | Button 4 | `d2` bit3 |
| 4 | Button 5 | `d1` bit0 |
| 5 | Button 6 | `d1` bit1 |
| 6 | Button 7 | `d1` bit2 |
| 7 | Button 8 | `d1` bit4 |

### Spaceball 4000 FLX (`'.'` advanced packet)

No dual-bit OR; wider map:

| `buttons` bit | Spaceball 4000 FLX |
|--------------:|--------------------|
| 0–5 | Buttons 1–6 (`d2` bits 0–5) |
| 6 | Button 7 (`d2` bit7) |
| 7–11 | Buttons 8, 9, A, B, C (`d1` bits 0–4) |
| 12 | MODE (`d1` bit5) |

### SpaceOrb 360 (`'D'` / `'K'`)

`buttons = data[1] & 0x3F` (six bits; Linux order TL, TR, Y, X, B, A):

| `buttons` bit | SpaceOrb |
|--------------:|----------|
| 0 | TL |
| 1 | TR |
| 2 | Y |
| 3 | X |
| 4 | B |
| 5 | A |

---

## Protocol / source links

### Origin (mbed)

- [OpenMoCo SpaceBall](https://os.mbed.com/teams/OpenMoCo/code/SpaceBall/) — original C++ lib (sources currently hard to download from mbed)
- [Serial-Connection wiki](https://os.mbed.com/teams/OpenMoCo/code/SpaceBall/wiki/Serial-Connection) — MAX3232 adapter, power on pins 4/7

### Magellan / SpaceMouse

- [Paul Bourke — Decoding Magellan Space Mouse](https://paulbourke.net/dataformats/spacemouse/)
- [Magellan Programmers Manual (PDF)](https://www.spacemice.org/pdf/Magellan_Programmers_Manual_2000.pdf)
- Linux [`magellan.c`](https://raw.githubusercontent.com/torvalds/linux/master/drivers/input/joystick/magellan.c)

### Spaceball

- [SpaceBall 2003–3003 Protocol (PDF)](https://spacemice.org/pdf/SpaceBall_2003-3003_Protocol.pdf)
- Linux [`spaceball.c`](https://raw.githubusercontent.com/torvalds/linux/master/drivers/input/joystick/spaceball.c)

### SpaceOrb

- Linux [`spaceorb.c`](https://raw.githubusercontent.com/torvalds/linux/master/drivers/input/joystick/spaceorb.c)
