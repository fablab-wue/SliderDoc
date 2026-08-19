# Render flat OLED example PNGs (active area only, no photorealistic frame).
# Stdlib only (no Pillow). Run from repo:
#   python docs/oled/render_examples.py
# Writes to docs/img/oled/.

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import oledfont  # noqa: E402

# Public-domain style 8x8 ASCII font (row-major, MSB = left), chars 32..127.
_FONT8_BASIC = (
    b"\x00\x00\x00\x00\x00\x00\x00\x00"  # 32
    b"\x18\x3c\x3c\x18\x18\x00\x18\x00"
    b"\x6c\x6c\x00\x00\x00\x00\x00\x00"
    b"\x6c\x6c\xfe\x6c\xfe\x6c\x6c\x00"
    b"\x30\x7c\xc0\x78\x0c\xf8\x30\x00"
    b"\x00\xc6\xcc\x18\x30\x66\xc6\x00"
    b"\x38\x6c\x38\x76\xdc\xcc\x76\x00"
    b"\x60\x60\xc0\x00\x00\x00\x00\x00"
    b"\x18\x30\x60\x60\x60\x30\x18\x00"
    b"\x60\x30\x18\x18\x18\x30\x60\x00"
    b"\x00\x66\x3c\xff\x3c\x66\x00\x00"
    b"\x00\x30\x30\xfc\x30\x30\x00\x00"
    b"\x00\x00\x00\x00\x00\x30\x30\x60"
    b"\x00\x00\x00\xfc\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x30\x30\x00"
    b"\x06\x0c\x18\x30\x60\xc0\x80\x00"
    b"\x7c\xc6\xce\xde\xf6\xe6\x7c\x00"  # 0
    b"\x30\x70\x30\x30\x30\x30\xfc\x00"
    b"\x78\xcc\x0c\x38\x60\xcc\xfc\x00"
    b"\x78\xcc\x0c\x38\x0c\xcc\x78\x00"
    b"\x1c\x3c\x6c\xcc\xfe\x0c\x1e\x00"
    b"\xfc\xc0\xf8\x0c\x0c\xcc\x78\x00"
    b"\x38\x60\xc0\xf8\xcc\xcc\x78\x00"
    b"\xfc\xcc\x0c\x18\x30\x30\x30\x00"
    b"\x78\xcc\xcc\x78\xcc\xcc\x78\x00"
    b"\x78\xcc\xcc\x7c\x0c\x18\x70\x00"
    b"\x00\x30\x30\x00\x00\x30\x30\x00"
    b"\x00\x30\x30\x00\x00\x30\x30\x60"
    b"\x18\x30\x60\xc0\x60\x30\x18\x00"
    b"\x00\x00\xfc\x00\x00\xfc\x00\x00"
    b"\x60\x30\x18\x0c\x18\x30\x60\x00"
    b"\x78\xcc\x0c\x18\x30\x00\x30\x00"
    b"\x7c\xc6\xde\xde\xde\xc0\x78\x00"
    b"\x30\x78\xcc\xcc\xfc\xcc\xcc\x00"  # A
    b"\xfc\x66\x66\x7c\x66\x66\xfc\x00"
    b"\x3c\x66\xc0\xc0\xc0\x66\x3c\x00"
    b"\xf8\x6c\x66\x66\x66\x6c\xf8\x00"
    b"\xfe\x62\x68\x78\x68\x62\xfe\x00"
    b"\xfe\x62\x68\x78\x68\x60\xf0\x00"
    b"\x3c\x66\xc0\xc0\xce\x66\x3e\x00"
    b"\xcc\xcc\xcc\xfc\xcc\xcc\xcc\x00"
    b"\x78\x30\x30\x30\x30\x30\x78\x00"
    b"\x1e\x0c\x0c\x0c\xcc\xcc\x78\x00"
    b"\xe6\x66\x6c\x78\x6c\x66\xe6\x00"
    b"\xf0\x60\x60\x60\x62\x66\xfe\x00"
    b"\xc6\xee\xfe\xfe\xd6\xc6\xc6\x00"
    b"\xc6\xe6\xf6\xde\xce\xc6\xc6\x00"
    b"\x38\x6c\xc6\xc6\xc6\x6c\x38\x00"
    b"\xfc\x66\x66\x7c\x60\x60\xf0\x00"
    b"\x78\xcc\xcc\xcc\xdc\x78\x1c\x00"
    b"\xfc\x66\x66\x7c\x6c\x66\xe6\x00"
    b"\x78\xcc\xe0\x70\x1c\xcc\x78\x00"
    b"\xfc\xb4\x30\x30\x30\x30\x78\x00"
    b"\xcc\xcc\xcc\xcc\xcc\xcc\xfc\x00"
    b"\xcc\xcc\xcc\xcc\xcc\x78\x30\x00"
    b"\xc6\xc6\xc6\xd6\xfe\xee\xc6\x00"
    b"\xc6\xc6\x6c\x38\x38\x6c\xc6\x00"
    b"\xcc\xcc\xcc\x78\x30\x30\x78\x00"
    b"\xfe\xc6\x8c\x18\x32\x66\xfe\x00"
    b"\x78\x60\x60\x60\x60\x60\x78\x00"
    b"\xc0\x60\x30\x18\x0c\x06\x02\x00"
    b"\x78\x18\x18\x18\x18\x18\x78\x00"
    b"\x10\x38\x6c\xc6\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\xff"
    b"\x30\x30\x18\x00\x00\x00\x00\x00"
    b"\x00\x00\x78\x0c\x7c\xcc\x76\x00"  # a
    b"\xe0\x60\x60\x7c\x66\x66\xdc\x00"
    b"\x00\x00\x78\xcc\xc0\xcc\x78\x00"
    b"\x1c\x0c\x0c\x7c\xcc\xcc\x76\x00"
    b"\x00\x00\x78\xcc\xfc\xc0\x78\x00"
    b"\x38\x6c\x60\xf0\x60\x60\xf0\x00"
    b"\x00\x00\x76\xcc\xcc\x7c\x0c\xf8"
    b"\xe0\x60\x6c\x76\x66\x66\xe6\x00"
    b"\x30\x00\x70\x30\x30\x30\x78\x00"
    b"\x0c\x00\x0c\x0c\x0c\xcc\xcc\x78"
    b"\xe0\x60\x66\x6c\x78\x6c\xe6\x00"
    b"\x70\x30\x30\x30\x30\x30\x78\x00"
    b"\x00\x00\xcc\xfe\xfe\xd6\xc6\x00"
    b"\x00\x00\xf8\xcc\xcc\xcc\xcc\x00"
    b"\x00\x00\x78\xcc\xcc\xcc\x78\x00"
    b"\x00\x00\xdc\x66\x66\x7c\x60\xf0"
    b"\x00\x00\x76\xcc\xcc\x7c\x0c\x1e"
    b"\x00\x00\xdc\x76\x66\x60\xf0\x00"
    b"\x00\x00\x7c\xc0\x78\x0c\xf8\x00"
    b"\x10\x30\x7c\x30\x30\x34\x18\x00"
    b"\x00\x00\xcc\xcc\xcc\xcc\x76\x00"
    b"\x00\x00\xcc\xcc\xcc\xcc\x76\x00"
    b"\x00\x00\xc6\xd6\xfe\xfe\x6c\x00"
    b"\x00\x00\xc6\x6c\x38\x6c\xc6\x00"
    b"\x00\x00\xcc\xcc\xcc\x7c\x0c\xf8"
    b"\x00\x00\xfc\x98\x30\x64\xfc\x00"
    b"\x1c\x30\x30\xe0\x30\x30\x1c\x00"
    b"\x18\x18\x18\x00\x18\x18\x18\x00"
    b"\xe0\x30\x30\x1c\x30\x30\xe0\x00"
    b"\x76\xdc\x00\x00\x00\x00\x00\x00"
    b"\x00\x10\x38\x6c\xc6\xc6\xfe\x00"
)

W, H = 128, 64
YELLOW = (255, 200, 0)
BLUE = (80, 180, 255)
BLACK = (0, 0, 0)
SCALE = 4  # docs: 512x256


class FB:
    def __init__(self):
        self.pix = [[0] * W for _ in range(H)]

    def pixel(self, x, y, colour=1):
        if 0 <= x < W and 0 <= y < H:
            self.pix[y][x] = 1 if colour else 0

    def text8(self, s, x, y):
        for ch in s:
            o = ord(ch)
            if o < 32 or o > 127:
                o = 63
            base = (o - 32) * 8
            for row in range(8):
                bits = _FONT8_BASIC[base + row]
                for col in range(8):
                    if bits & (0x80 >> col):
                        self.pixel(x + col, y + row, 1)
            x += 8


def fmt_num(value):
    v = float(value)
    if v > 999.9:
        v = 999.9
    elif v < -999.9:
        v = -999.9
    return "{:6.1f}".format(v)


def draw_screen(status, pos, spd, acc, app):
    fb = FB()
    if status:
        fb.text8(status, 0, 4)
    num_x, unit_x = 26, 76
    for y, label, num, unit in (
        (17, "Pos", fmt_num(pos), "mm"),
        (27, "Spd", fmt_num(spd), "mm/s"),
        (37, "Acc", fmt_num(acc), "mm/s2"),
    ):
        oledfont.text(fb, label, 0, y + 1)
        fb.text8(num, num_x, y)
        oledfont.text(fb, unit, unit_x, y + 1)
    if app:
        line_w = 21
        lines = app.replace("\r", "").split("\n")
        drawn = 0
        for line in lines:
            while line and drawn < 2:
                oledfont.text(fb, line[:line_w], 0, 48 + drawn * 8)
                line = line[line_w:]
                drawn += 1
            if drawn >= 2:
                break
    return fb


def _png_chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def save_png_rgb(path, width, height, rgb_rows):
    """rgb_rows: iterable of width*(R,G,B) flat bytes, one row each."""
    raw = bytearray()
    for row in rgb_rows:
        raw.append(0)  # filter None
        raw.extend(row)
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", compressed)
        + _png_chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def fb_to_scaled_rows(fb):
    sw, sh = W * SCALE, H * SCALE
    rows = []
    for y in range(sh):
        src_y = y // SCALE
        colour = YELLOW if src_y < 16 else BLUE
        row = bytearray(sw * 3)
        for x in range(sw):
            src_x = x // SCALE
            on = fb.pix[src_y][src_x]
            r, g, b = colour if on else BLACK
            i = x * 3
            row[i] = r
            row[i + 1] = g
            row[i + 2] = b
        rows.append(row)
    return sw, sh, rows


def main():
    if len(_FONT8_BASIC) != 96 * 8:
        raise SystemExit("bad 8x8 font length: %d" % len(_FONT8_BASIC))

    out = Path(__file__).resolve().parents[1] / "img" / "oled"
    out.mkdir(parents=True, exist_ok=True)
    # (status yellow, pos, spd, acc, app text) — mirrors Slider + JKSlider OLED.
    screens = {
        # Idle, no extras
        "oled-idle.png": ("", 142.5, 0.0, 200.0, "Ready"),
        # Delay armed + TL divider on extra line (packed)
        "oled-delay.png": ("", 142.5, 0.0, 200.0, "Ready\nDelay 5.0s TL x25"),
        # Delay countdown before cruise starts
        "oled-wait.png": ("", 142.5, 0.0, 200.0, "Cruising R\nWait 3.2s"),
        # Cruise with near-soft-limit warning
        "oled-moving.png": ("", 87.4, -42.0, 150.0, "Cruising L\nNear limit"),
        # Goto with remaining distance
        "oled-goto.png": ("", 100.0, 25.0, 200.0, "Move to PosA\n->A 42mm"),
        # Loop endpoint dwell
        "oled-loop.png": ("", 150.0, 0.0, 120.0, "Loop A-B\nDwell 1.0s"),
        "oled-homing.png": ("HOMING", 12.3, -5.0, 200.0, "Homing..."),
        "oled-disabled.png": ("DISABLED", 200.0, 0.0, 200.0, "Disabled"),
        "oled-limit.png": ("LIMIT", 300.0, 0.0, 200.0, "Soft limit"),
        "oled-hard-limit.png": ("HARD LIMIT", 0.0, 0.0, 200.0, "Hard limit"),
    }
    for name, args in screens.items():
        fb = draw_screen(*args)
        sw, sh, rows = fb_to_scaled_rows(fb)
        path = out / name
        save_png_rgb(path, sw, sh, rows)
        print("wrote", path)


if __name__ == "__main__":
    main()
