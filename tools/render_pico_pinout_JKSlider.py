# Generate Pico board pinout ASCII + PNG for JKSlider UIC (stdlib only).
# docs/img/keypad_map.png is a hand-authored Fritzing-style asset — not overwritten here.
#   python docs/render_pico_pinout.py
#
# Top view, USB at top. UIC panel pins from JKSliderConfig / SliderConfig;
# motion runs on SliderMC (UART GP16/17 @ 1 Mbaud).

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT
OUT_TXT = ROOT / "assets"
OUT_PNG = ROOT / "uic" / "projects" / "jkslider" / "panel-layouts"

# Left / right edge, top→bottom (USB at top). Official 40-pin header map.
# (pad_name, JKSlider UIC label)
LEFT = [
    ("GP0", "DSP_I2C_SDA"),
    ("GP1", "DSP_I2C_SCL"),
    ("GND", "GND"),
    ("GP2", "LED_R"),
    ("GP3", "LED_G"),
    ("GP4", "LED_B"),
    ("GP5", "BTN_STOP"),
    ("GND", "GND"),
    ("GP6", "BTN_MOVE_L"),
    ("GP7", "BTN_MOVE_R"),
    ("GP8", "BTN_FAST_L"),
    ("GP9", "BTN_FAST_R"),
    ("GND", "GND"),
    ("GP10", "BTN_A"),
    ("GP11", "BTN_B"),
    ("GP12", "BTN_C"),
    ("GP13", "BTN_OPTION"),
    ("GND", "GND"),
    ("GP14", "BTN_DELAY"),
    ("GP15", "BTN_TIMELAPSE"),
]

RIGHT = [
    ("VBUS", "VBUS"),
    ("VSYS", "VSYS"),
    ("GND", "GND"),
    ("3V3_EN", "3V3_EN"),
    ("3V3", "3V3 OUT"),
    ("ADC_VREF", "ADC_VREF"),
    ("GP28", "POT_JOYSTICK"),
    ("AGND", "ADC GND"),
    ("GP27", "POT_ACCEL"),
    ("GP26", "POT_SPEED"),
    ("RUN", "RUN"),
    ("GP22", "CTRL_CAMERA"),
    ("GND", "GND"),
    ("GP21", "free"),
    ("GP20", "free"),
    ("GP19", "free"),
    ("GP18", "free"),
    ("GND", "GND"),
    ("GP17", "UART_RX"),
    ("GP16", "UART_TX"),
]

# Keypad mode: matrix nets. KP_ROW1 = upper keys on GP6; KP_ROW4 on GP9.
KEYPAD_LEFT_OVERRIDE = {
    "GP5": "BTN_STOP",
    "GP6": "KP_ROW1",
    "GP7": "KP_ROW2",
    "GP8": "KP_ROW3",
    "GP9": "KP_ROW4",
    "GP10": "KP_COL1",
    "GP11": "KP_COL2",
    "GP12": "KP_COL3",
    "GP13": "BTN_OPTION",
    "GP14": "free",
    "GP15": "free",
}

# Group palette
C_GND = (20, 20, 20)
C_PWR_5V = (200, 40, 40)  # power 5V — pins 39/40
C_PWR_3V3 = (230, 120, 30)  # power 3V3 — pins 35/36
C_BTN = (40, 180, 175)  # turquoise
C_KP = (40, 180, 175)  # same as BTN_*
C_DSP = (230, 200, 50)  # yellow
C_LED = (245, 225, 120)  # light yellow (LED_*)
C_CTRL = (190, 150, 220)  # light purple
C_UART = (60, 130, 220)  # blue — UIC ↔ SliderMC UART
C_POT = (140, 200, 110)  # light green
C_FREE = (190, 190, 195)  # light gray (free / unused)
C_CTRL_PIN = (240, 140, 140)  # light red — 3V3_EN / RUN (no legend entry)
C_GP = (90, 170, 100)
C_PINNUM = (90, 90, 95)

# Official pinout artwork (board + side labels). Crop PCB at 1:1 — do not scale.
PICO_GPIO_PNG = ROOT / "assets" / "img" / "raspberry-pi-pico-gpio.png"
# Inclusive crop of green PCB (measured from raspberry-pi-pico-gpio.png).
_BOARD_CROP = (411, 24, 658, 625)  # x0, y0, x1, y1
_PIN_Y0_ABS = 39  # absolute Y of pin 1 / pin 40 centers in source PNG
_PIN_PITCH = 30


def _labels(mode: str):
    left = []
    for gpio, lab in LEFT:
        if mode == "keypad" and gpio in KEYPAD_LEFT_OVERRIDE:
            left.append((gpio, KEYPAD_LEFT_OVERRIDE[gpio]))
        else:
            left.append((gpio, lab))
    return left, list(RIGHT)


def _color_for(label: str, gpio: str, pin_num: int | None = None):
    """RGB category colours (official Pico pinout style groups)."""
    lab = label.upper().replace(" ", "_")
    if pin_num in (39, 40) or gpio in ("VBUS", "VSYS"):
        return C_PWR_5V
    if pin_num in (35, 36) or gpio in ("3V3", "ADC_VREF") or lab in ("3V3_OUT", "ADC_VREF"):
        return C_PWR_3V3
    if gpio in ("GND", "AGND") or lab in ("GND", "ADC_GND") or "ADC_GND" in lab:
        return C_GND
    if gpio == "3V3_EN" or lab == "3V3_EN" or gpio == "RUN":
        return C_CTRL_PIN
    if lab.startswith("DSP_") or "DSP_I2C" in lab:
        return C_DSP
    if lab.startswith("LED_") or "NEOPIXEL" in lab:
        return C_LED
    if lab.startswith("POT_"):
        return C_POT
    if lab.startswith("UART_"):
        return C_UART
    if lab.startswith("KP_") or "KP_ROW" in lab or "KP_COL" in lab:
        return C_KP
    if lab.startswith("BTN_"):
        return C_BTN
    if lab.startswith("CTRL_") or "CTRL_CAMERA" in lab:
        return C_CTRL
    if lab in ("FREE", "(FREE)") or "(FREE)" in lab:
        return C_FREE
    return C_FREE


def render_ascii(mode: str) -> str:
    left, right = _labels(mode)
    title = "BUTTON mode" if mode == "button" else "KEYPAD mode"
    lines = [
        "Raspberry Pi Pico — JKSlider UIC pinout (top view, USB at top)",
        title + "  |  defaults in UIC_config.py + JKSliderConfig.py",
        "",
        "        function         pin              pin        function",
        "                         +--- USB ---+",
    ]
    for i, ((lg, ll), (rg, rl)) in enumerate(zip(left, right)):
        pn_l = i + 1
        pn_r = 40 - i
        left_fun = "%-16s" % ll
        left_gp = "%-7s" % lg
        right_gp = "%-8s" % rg
        right_fun = rl
        lines.append(
            "  %s %s %2d |o         o| %-2d %s %s"
            % (left_fun, left_gp, pn_l, pn_r, right_gp, right_fun)
        )
    lines.extend(
        [
            "                         +-----------+",
            "",
            "Legend: pots on ADC pins GP26–28; UART to SliderMC on GP16 (TX) / GP17 (RX) @ 1 Mbaud.",
            "Motion STEP/DIR/EN, SW_HOME, DRV_ERROR live on the SliderMC Pico — not on this UIC.",
        ]
    )
    if mode == "keypad":
        lines.extend(
            [
                "Keypad nets: GP6–9 = KP_ROW1..KP_ROW4 (High-Z idle / drive LOW to scan);",
                "  GP10–12 = KP_COL1..KP_COL3;",
                "  BTN_STOP on GP5 (+ matrix key on KP_ROW4/KP_COL2);",
                "  BTN_OPTION on GP13 (+ matrix * keys on KP_ROW4/KP_COL1 & KP_COL3).",
                "  KP_ROW1 (GP6, upper): MOVE_L, DELAY, MOVE_R",
                "  KP_ROW2 (GP7): FAST_L, TIMELAPSE, FAST_R",
                "  KP_ROW3 (GP8): A, B, C",
                "  KP_ROW4 (GP9, lower): OPTION, STOP, OPTION",
            ]
        )
    else:
        lines.append(
            "Button mode: one GPIO per BTN_* (active-low). "
            'JKS_INPUT_MODE = "button".'
        )
    lines.append(
        "GP22 CTRL_CAMERA = shutter / intervalometer (PIN_CTRL_CAMERA). "
        "Optional NeoPixel: use a free GPIO (GP18–21) and set PIN_NEOPIXEL."
    )
    lines.append(
        "Naming: BTN_* = electronics/pinout; User Manual uses plain names "
        "(STOP, MOVE_L, …). Key silk: short labels (` > `, ` * `, …)."
    )
    return "\n".join(lines) + "\n"


# --- minimal bitmap font (5x7) ---
_CHARS = {}


def _init_font():
    raw = {
        " ": b"\x00\x00\x00\x00\x00",
        "-": b"\x08\x08\x08\x08\x08",
        "|": b"\x00\x00\x7f\x00\x00",
        "<": b"\x08\x14\x22\x41\x00",
        ">": b"\x41\x22\x14\x08\x00",
        "*": b"\x14\x08\x3e\x08\x14",
        "(": b"\x00\x41\x22\x1c\x00",
        ")": b"\x00\x1c\x22\x41\x00",
        "/": b"\x20\x10\x08\x04\x02",
        "0": b"\x3e\x51\x49\x45\x3e",
        "1": b"\x00\x42\x7f\x40\x00",
        "2": b"\x42\x61\x51\x49\x46",
        "3": b"\x21\x41\x45\x4b\x31",
        "4": b"\x18\x14\x12\x7f\x10",
        "5": b"\x27\x45\x45\x45\x39",
        "6": b"\x3c\x4a\x49\x49\x30",
        "7": b"\x01\x71\x09\x05\x03",
        "8": b"\x36\x49\x49\x49\x36",
        "9": b"\x06\x49\x49\x29\x1e",
        "A": b"\x7e\x11\x11\x11\x7e",
        "B": b"\x7f\x49\x49\x49\x36",
        "C": b"\x3e\x41\x41\x41\x22",
        "D": b"\x7f\x41\x41\x22\x1c",
        "E": b"\x7f\x49\x49\x49\x41",
        "F": b"\x7f\x09\x09\x09\x01",
        "G": b"\x3e\x41\x49\x49\x7a",
        "H": b"\x7f\x08\x08\x08\x7f",
        "I": b"\x00\x41\x7f\x41\x00",
        "J": b"\x20\x40\x41\x3f\x01",
        "K": b"\x7f\x08\x14\x22\x41",
        "L": b"\x7f\x40\x40\x40\x40",
        "M": b"\x7f\x02\x0c\x02\x7f",
        "N": b"\x7f\x04\x08\x10\x7f",
        "O": b"\x3e\x41\x41\x41\x3e",
        "P": b"\x7f\x09\x09\x09\x06",
        "Q": b"\x3e\x41\x51\x21\x5e",
        "R": b"\x7f\x09\x19\x29\x46",
        "S": b"\x46\x49\x49\x49\x31",
        "T": b"\x01\x01\x7f\x01\x01",
        "U": b"\x3f\x40\x40\x40\x3f",
        "V": b"\x1f\x20\x40\x20\x1f",
        "W": b"\x3f\x40\x38\x40\x3f",
        "X": b"\x63\x14\x08\x14\x63",
        "Y": b"\x07\x08\x70\x08\x07",
        "Z": b"\x61\x51\x49\x45\x43",
        "_": b"\x40\x40\x40\x40\x40",
        ".": b"\x00\x60\x60\x00\x00",
        "+": b"\x08\x08\x3e\x08\x08",
        ":": b"\x00\x36\x36\x00\x00",
        ",": b"\x00\x80\x60\x00\x00",
        "'": b"\x00\x07\x00\x00\x00",
        "=": b"\x14\x14\x14\x14\x14",
    }
    for k, v in list(raw.items()):
        _CHARS[k] = v
        _CHARS[k.lower()] = v


def _png_chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def save_png(path, width, height, rows):
    raw = bytearray()
    for row in rows:
        raw.append(0)
        raw.extend(row)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _png_chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def _text_width(s, scale=1):
    return len(str(s)) * 6 * scale


def load_png_rgb(path: Path):
    """Load 8-bit RGB/RGBA PNG → (width, height, list of RGB row bytearrays)."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG: %s" % path)
    pos = 8
    width = height = ctype = None
    idat = b""
    while pos < len(data):
        ln = struct.unpack(">I", data[pos : pos + 4])[0]
        tag = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + ln]
        pos += 12 + ln
        if tag == b"IHDR":
            width, height, bit, ctype = struct.unpack(">IIBB", chunk[:10])
            if bit != 8 or ctype not in (2, 6):
                raise ValueError("unsupported PNG format")
        elif tag == b"IDAT":
            idat += chunk
        elif tag == b"IEND":
            break
    raw = zlib.decompress(idat)
    bpp = 3 if ctype == 2 else 4
    stride = width * bpp
    rows = []
    prev = bytearray(stride)
    i = 0
    for _y in range(height):
        f = raw[i]
        i += 1
        row = bytearray(raw[i : i + stride])
        i += stride
        if f == 1:
            for x in range(bpp, stride):
                row[x] = (row[x] + row[x - bpp]) & 255
        elif f == 2:
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                a = row[x - bpp] if x >= bpp else 0
                row[x] = (row[x] + ((a + prev[x]) // 2)) & 255
        elif f == 4:
            for x in range(stride):
                a = row[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                row[x] = (row[x] + pr) & 255
        if bpp == 4:
            rgb = bytearray(width * 3)
            for x in range(width):
                rgb[x * 3] = row[x * 4]
                rgb[x * 3 + 1] = row[x * 4 + 1]
                rgb[x * 3 + 2] = row[x * 4 + 2]
            rows.append(rgb)
        else:
            rows.append(row)
        prev = row
    return width, height, rows


def load_pico_board():
    """Crop green PCB from official pinout PNG at native 1:1 size. Return board rows + pin Y in crop."""
    _w, _h, rows = load_png_rgb(PICO_GPIO_PNG)
    x0, y0, x1, y1 = _BOARD_CROP
    board_w = x1 - x0 + 1
    board_h = y1 - y0 + 1
    board = []
    for y in range(y0, y1 + 1):
        board.append(bytearray(rows[y][x0 * 3 : (x1 + 1) * 3]))
    pin_ys = [_PIN_Y0_ABS - y0 + i * _PIN_PITCH for i in range(20)]
    return board_w, board_h, board, pin_ys


def render_png(mode: str, path: Path):
    _init_font()
    left, right = _labels(mode)
    board_w, board_h, board_rows, pin_ys = load_pico_board()

    margin = 24
    title_h = 56
    gap = 4
    fun_w = 118
    gp_w = 52
    pin_w = 28
    box_h = min(22, _PIN_PITCH - 6)
    side_w = fun_w + gap + gp_w + gap + pin_w
    width = margin + side_w + board_w + side_w + margin
    legend = [
        ("BTN_*/KP_*", C_BTN),
        ("UART_*", C_UART),
        ("DSP_*", C_DSP),
        ("LED_*", C_LED),
        ("CTRL_*", C_CTRL),
        ("POT_*", C_POT),
        ("free", C_FREE),
        ("GND", C_GND),
        ("power 3V3", C_PWR_3V3),
        ("power 5V", C_PWR_5V),
    ]
    # Pre-measure wrapped legend height
    legend_rows = 1
    x = margin
    max_x = width - margin
    for name, _col in legend:
        item_w = 14 + _text_width(name, 1) + 16
        if x + item_w > max_x and x > margin:
            legend_rows += 1
            x = margin
        x += item_w
    legend_h = legend_rows * 16 + 8
    height = margin + title_h + board_h + 12 + legend_h + margin
    bg = (250, 250, 252)
    text_c = (25, 25, 30)
    white = (255, 255, 255)

    px = [[bg[0], bg[1], bg[2]] for _ in range(width * height)]

    def put(x, y, rgb):
        if 0 <= x < width and 0 <= y < height:
            px[y * width + x] = [rgb[0], rgb[1], rgb[2]]

    def fill_rect(x, y, w, h, rgb):
        for yy in range(max(0, y), min(height, y + h)):
            for xx in range(max(0, x), min(width, x + w)):
                put(xx, yy, rgb)

    def text(s, x, y, rgb, scale=1):
        s = str(s)
        cx = x
        for ch in s:
            glyph = _CHARS.get(ch) or _CHARS.get(ch.upper()) or _CHARS[" "]
            for col in range(5):
                bits = glyph[col]
                for row in range(7):
                    if bits & (1 << row):
                        for dy in range(scale):
                            for dx in range(scale):
                                put(cx + col * scale + dx, y + row * scale + dy, rgb)
            cx += 6 * scale

    def label_box(s, x, y, w, h, rgb, align="left"):
        fill_rect(x, y, w, h, rgb)
        lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        tc = white if lum < 140 else (20, 20, 20)
        tw = _text_width(s, 1)
        tx = x + 4 if align == "left" else x + max(2, (w - tw) // 2)
        text(s[:18], tx, y + (h - 7) // 2, tc, 1)

    def gp_box_color(pad: str, pin_num: int):
        if pad in ("GND", "AGND"):
            return C_GND
        if pad in ("VBUS", "VSYS") or pin_num in (39, 40):
            return C_PWR_5V
        if pad in ("3V3", "ADC_VREF") or pin_num in (35, 36):
            return C_PWR_3V3
        if pad in ("RUN", "3V3_EN"):
            return C_CTRL_PIN
        if pad.startswith("GP"):
            return C_GP
        return C_PINNUM

    title = "Pico JKSlider UIC — %s mode" % ("BUTTON" if mode == "button" else "KEYPAD")
    text(title, margin, margin, text_c, 2)
    text(
        "Top view  USB at top  GP + function  Default wiring",
        margin,
        margin + 28,
        (90, 90, 100),
        1,
    )

    board_x = margin + side_w
    board_y = margin + title_h
    # Blit PCB crop 1:1 (no scale)
    for by in range(board_h):
        src = board_rows[by]
        for bx in range(board_w):
            o = bx * 3
            put(board_x + bx, board_y + by, (src[o], src[o + 1], src[o + 2]))

    for i in range(20):
        cy = board_y + pin_ys[i]
        by = cy - box_h // 2
        lg, ll = left[i]
        rg, rl = right[i]
        pn_l = i + 1
        pn_r = 40 - i
        lc = _color_for(ll, lg, pn_l)
        rc = _color_for(rl, rg, pn_r)

        lx = margin
        label_box(ll, lx, by, fun_w, box_h, lc, "left")
        lx += fun_w + gap
        label_box(lg, lx, by, gp_w, box_h, gp_box_color(lg, pn_l), "center")
        lx += gp_w + gap
        label_box(str(pn_l), lx, by, pin_w, box_h, C_PINNUM, "center")

        rx = board_x + board_w
        label_box(str(pn_r), rx, by, pin_w, box_h, C_PINNUM, "center")
        rx += pin_w + gap
        label_box(rg, rx, by, gp_w, box_h, gp_box_color(rg, pn_r), "center")
        rx += gp_w + gap
        label_box(rl, rx, by, fun_w, box_h, rc, "left")

    # Legend — wrap to multiple rows so every entry fits
    ly = board_y + board_h + 10
    x = margin
    row_h_leg = 16
    for name, col in legend:
        item_w = 14 + _text_width(name, 1) + 16
        if x + item_w > max_x and x > margin:
            x = margin
            ly += row_h_leg
        fill_rect(x, ly, 10, 10, col)
        text(name, x + 14, ly + 1, text_c, 1)
        x += item_w

    out_rows = []
    for y in range(height):
        row = bytearray(width * 3)
        for x in range(width):
            r, g, b = px[y * width + x]
            row[x * 3] = r
            row[x * 3 + 1] = g
            row[x * 3 + 2] = b
        out_rows.append(row)
    save_png(path, width, height, out_rows)


def main():
    OUT_PNG.mkdir(parents=True, exist_ok=True)
    for mode in ("button", "keypad"):
        ascii_path = OUT_TXT / ("pico_pinout_%s.txt" % mode)
        png_path = OUT_PNG / ("pico_pinout_%s.png" % mode)
        ascii_path.write_text(render_ascii(mode), encoding="utf-8")
        render_png(mode, png_path)
        print("wrote", ascii_path)
        print("wrote", png_path)


if __name__ == "__main__":
    main()
