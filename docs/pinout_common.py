# Shared helpers for SliderMC pinout PNG renderers (stdlib only).

from __future__ import annotations

import struct
import zlib
from pathlib import Path

DOCS = Path(__file__).resolve().parent
OUT_PNG = DOCS / "img"

# Group palette (shared by Pico + RP2040-Zero pinout images)
C_GND = (20, 20, 20)
C_PWR_5V = (200, 40, 40)
C_PWR_3V3 = (230, 120, 30)
C_EXT = (190, 150, 220)  # light purple — EXT_0…EXT_9
C_DRV = (130, 70, 180)  # purple — all DRV_* pins
C_UART = (60, 130, 220)  # blue — UART to UIC
C_SW = (120, 210, 205)  # light turquoise — SW_*
C_DBG = (150, 95, 45)  # brown — DBG_* (DEBUG_HW)
C_LED = (220, 170, 40)  # amber — status LED
C_FREE = (190, 190, 195)
C_CTRL_PIN = (240, 140, 140)
C_GP = (90, 170, 100)
C_PINNUM = (90, 90, 95)

_CHARS: dict[str, bytes] = {}


def init_font():
    if _CHARS:
        return
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


def text_width(s, scale=1):
    return len(str(s)) * 6 * scale


def load_png_rgb(path: Path):
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


def crop_rgb(rows, x0, y0, x1, y1):
    board = []
    for y in range(y0, y1 + 1):
        board.append(bytearray(rows[y][x0 * 3 : (x1 + 1) * 3]))
    return (x1 - x0 + 1), (y1 - y0 + 1), board


def scale_nn(board_w, board_h, board_rows, scale: int):
    if scale == 1:
        return board_w, board_h, board_rows
    out_w = board_w * scale
    out_h = board_h * scale
    out = []
    for y in range(board_h):
        src = board_rows[y]
        row = bytearray(out_w * 3)
        for x in range(board_w):
            o = x * 3
            r, g, b = src[o], src[o + 1], src[o + 2]
            for dx in range(scale):
                d = (x * scale + dx) * 3
                row[d] = r
                row[d + 1] = g
                row[d + 2] = b
        for _ in range(scale):
            out.append(bytearray(row))
    return out_w, out_h, out


def color_for(label: str, gpio: str, pin_num: int | None = None):
    lab = label.upper().replace(" ", "_").rstrip("*")
    if pin_num in (39, 40) or gpio in ("VBUS", "VSYS", "5V"):
        return C_PWR_5V
    if pin_num in (35, 36) or gpio in ("3V3", "ADC_VREF") or lab in ("3V3_OUT", "ADC_VREF"):
        return C_PWR_3V3
    if gpio in ("GND", "AGND") or lab in ("GND", "ADC_GND") or "ADC_GND" in lab:
        return C_GND
    if gpio == "3V3_EN" or lab == "3V3_EN" or gpio == "RUN":
        return C_CTRL_PIN
    if lab.startswith("EXT_"):
        return C_EXT
    if lab.startswith("DRV_"):
        return C_DRV
    if lab.startswith("UART_"):
        return C_UART
    if lab.startswith("SW_"):
        return C_SW
    if lab.startswith("DBG_"):
        return C_DBG
    if lab in ("LED", "PIN_LED"):
        return C_LED
    if lab in ("FREE", "(FREE)") or "(FREE)" in lab or lab == "RGB_UNUSED":
        return C_FREE
    return C_FREE


class Canvas:
    def __init__(self, width: int, height: int, bg=(250, 250, 252)):
        init_font()
        self.width = width
        self.height = height
        self.bg = bg
        self.px = [[bg[0], bg[1], bg[2]] for _ in range(width * height)]

    def put(self, x, y, rgb):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.px[y * self.width + x] = [rgb[0], rgb[1], rgb[2]]

    def fill_rect(self, x, y, w, h, rgb):
        for yy in range(max(0, y), min(self.height, y + h)):
            for xx in range(max(0, x), min(self.width, x + w)):
                self.put(xx, yy, rgb)

    def text(self, s, x, y, rgb, scale=1):
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
                                self.put(cx + col * scale + dx, y + row * scale + dy, rgb)
            cx += 6 * scale

    def label_box(self, s, x, y, w, h, rgb, align="left", scale=1):
        self.fill_rect(x, y, w, h, rgb)
        lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        fg = (255, 255, 255) if lum < 140 else (20, 20, 25)
        tw = text_width(s, scale)
        pad = 3 * scale
        tx = x + pad if align == "left" else x + max(2, (w - tw) // 2)
        self.text(s, tx, y + max(1, (h - 7 * scale) // 2), fg, scale)

    def label_box_rot90cw(self, s, x, y, w, h, rgb, align="left", scale=1):
        """Label of logical size w (along text) x h (thickness), rotated 90 deg
        clockwise: occupies h x w pixels at (x, y) and reads top to bottom."""
        self.fill_rect(x, y, h, w, rgb)
        lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        fg = (255, 255, 255) if lum < 140 else (20, 20, 25)
        tw = text_width(s, scale)
        pad = 3 * scale
        tx = pad if align == "left" else max(2, (w - tw) // 2)
        ty = max(1, (h - 7 * scale) // 2)
        cx = tx
        for ch in str(s):
            glyph = _CHARS.get(ch) or _CHARS.get(ch.upper()) or _CHARS[" "]
            for col in range(5):
                bits = glyph[col]
                for row in range(7):
                    if bits & (1 << row):
                        for dy in range(scale):
                            for dx in range(scale):
                                lx = cx + col * scale + dx
                                ly = ty + row * scale + dy
                                self.put(x + (h - 1 - ly), y + lx, fg)
            cx += 6 * scale

    def blit_rgb(self, board_x, board_y, board_w, board_h, board_rows):
        for by in range(board_h):
            src = board_rows[by]
            for bx in range(board_w):
                o = bx * 3
                self.put(board_x + bx, board_y + by, (src[o], src[o + 1], src[o + 2]))

    def save(self, path: Path):
        out_rows = []
        for y in range(self.height):
            row = bytearray(self.width * 3)
            for x in range(self.width):
                r, g, b = self.px[y * self.width + x]
                row[x * 3] = r
                row[x * 3 + 1] = g
                row[x * 3 + 2] = b
            out_rows.append(row)
        save_png(path, self.width, self.height, out_rows)
