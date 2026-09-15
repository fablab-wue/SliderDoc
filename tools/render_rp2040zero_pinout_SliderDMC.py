# Generate RP2040-Zero pinout ASCII + PNG for SliderDMC (stdlib only).
#   python tools/render_rp2040zero_pinout_SliderDMC.py
#
# Top view + bottom view (USB at top). Same geometry as SliderMC Zero renderer.

from __future__ import annotations

from pathlib import Path

from pinout_common import (
    C_BUZZER,
    C_CAMERA,
    C_DRV,
    C_EXT,
    C_FREE,
    C_GND,
    C_GP,
    C_LED,
    C_PINNUM,
    C_PWR_3V3,
    C_PWR_5V,
    C_SW,
    C_UART,
    OUT_PNG,
    Canvas,
    color_for,
    crop_rgb,
    load_png_rgb,
    scale_nn,
    text_width,
)

DOCS = Path(__file__).resolve().parents[1]
OUT_TXT = DOCS / "assets"
ZERO_GPIO_PNG = OUT_PNG / "waveshare-rp2040-zero-gpio.png"

_TOP_CROP = (321, 176, 509, 441)
_BOT_CROP = (321, 593, 509, 841)
_SCALE = 2
_LBL_SCALE = 2
_PITCH = 52
_BOX_H = 44
_FUN_W = 172
_GP_W = 64
_GAP = 6

_PAD_LEFT_Y0, _PAD_LEFT_PITCH = 32.5, 27.27
_PAD_RIGHT_Y0, _PAD_RIGHT_PITCH = 34.15, 26.86
_PAD_BOTTOM_X0, _PAD_BOTTOM_PITCH = 43.6, 26.1

# Left edge, top→bottom.
LEFT = [
    ("5V", "5V"),
    ("GND", "GND"),
    ("3V3", "3V3"),
    ("GP29", "free"),
    ("GP28", "free"),
    ("GP27", "free"),
    ("GP26", "free"),
    ("GP15", "BUZZER"),
    ("GP14", "CAMERA"),
]

# Right edge, top→bottom.
RIGHT = [
    ("GP0", "DMX_TX"),
    ("GP1", "free"),
    ("GP2", "GIO_OUT0"),
    ("GP3", "GIO_OUT1"),
    ("GP4", "GIO_OUT2"),
    ("GP5", "GIO_OUT3"),
    ("GP6", "GIO_IN0"),
    ("GP7", "GIO_IN1"),
    ("GP8", "GIO_IN2"),
]

# Bottom edge, left→right.
BOTTOM = [
    ("GP13", "UART_RX"),
    ("GP12", "UART_TX"),
    ("GP11", "free"),
    ("GP10", "free"),
    ("GP9", "GIO_IN3"),
]

# Bottom view SMD pads, top→bottom.
BOT_PADS = [
    ("GND", "GND"),
    ("GP25", "free"),
    ("GP24", "free"),
    ("GP23", "free"),
    ("GP22", "free"),
    ("GP21", "free"),
    ("GP20", "free"),
    ("GP19", "free"),
    ("GP18", "free"),
    ("GP17", "free"),
]

LEGEND = [
    ("DMX_TX", C_DRV),
    ("GIO_OUT*", C_EXT),
    ("GIO_IN*", C_SW),
    ("UART_*", C_UART),
    ("CAMERA", C_CAMERA),
    ("BUZZER", C_BUZZER),
    ("NEOPIXEL", C_LED),
    ("free", C_FREE),
    ("GND", C_GND),
    ("power 3V3", C_PWR_3V3),
    ("power 5V", C_PWR_5V),
]

ASCII_HEAD = (
    "Waveshare RP2040-Zero — SliderDMC pinout (USB at top)",
    "Defaults in src/config.h",
)

ASCII_NOTES = [
    "Legend: DMX_TX GP0 (PIO UART 250k 8N2); GIO OUT GP2–5; GIO IN GP6–9.",
    "UART to SliderMC 115200 baud GP12 (TX) / GP13 (RX). CAMERA GP14 (OC). BUZZER GP15.",
    "GP16 = onboard WS2812 status LED. GP17–20 are not DMC GIO (those are MC extender pins).",
    "Cross UART to SliderMC: DMC TX GP12 → MC RX; DMC RX GP13 ← MC TX. See dmc/pins.md.",
]


def render_ascii() -> str:
    lines = [
        ASCII_HEAD[0],
        ASCII_HEAD[1],
        "",
        "    function     pad                  pad    function",
        "                        +---- USB ----+",
    ]
    for (lg, lf), (rg, rf) in zip(LEFT, RIGHT):
        lines.append("  %-14s %-6s |o           o| %-6s %s" % (lf, lg, rg, rf))
    lines.extend(
        [
            "                        +-------------+",
            "                         " + " ".join(g[2:] for g, _ in BOTTOM),
            "",
            "Bottom edge (left→right):",
        ]
    )
    for gp, fun in BOTTOM:
        lines.append("  %-6s %s" % (gp, fun))
    lines.extend(["", "Bottom-side SMD pads (top→bottom):"])
    for gp, fun in BOT_PADS:
        lines.append("  %-6s %s" % (gp, fun))
    lines.append("")
    lines.extend(ASCII_NOTES)
    return "\n".join(lines) + "\n"


def _gp_box_color(pad: str):
    if pad in ("GND", "AGND"):
        return C_GND
    if pad in ("5V", "VBUS", "VSYS"):
        return C_PWR_5V
    if pad == "3V3":
        return C_PWR_3V3
    if pad.startswith("GP"):
        return C_GP
    return C_PINNUM


def _block_h(n: int) -> int:
    return (n - 1) * _PITCH + _BOX_H


def _row_ys(n: int, top: int) -> list[int]:
    return [top + i * _PITCH for i in range(n)]


def _pad_centers(n: int, first: float, pitch: float, origin: int) -> list[int]:
    return [origin + int(round((first + i * pitch) * _SCALE)) for i in range(n)]


def _draw_column(c: Canvas, items, ys, x_inner: int, side: str, fun_w: int = _FUN_W):
    for (gp, fun), by in zip(items, ys):
        fc = color_for(fun, gp)
        gc = _gp_box_color(gp)
        if side == "left":
            gx = x_inner - _GP_W
            fx = gx - _GAP - fun_w
            c.label_box(fun, fx, by, fun_w, _BOX_H, fc, "left", _LBL_SCALE)
            c.label_box(gp, gx, by, _GP_W, _BOX_H, gc, "center", _LBL_SCALE)
        else:
            c.label_box(gp, x_inner, by, _GP_W, _BOX_H, gc, "center", _LBL_SCALE)
            c.label_box(
                fun, x_inner + _GP_W + _GAP, by, fun_w, _BOX_H, fc, "left", _LBL_SCALE
            )


def _draw_bottom_column(c: Canvas, items, xs, y_inner: int, fun_w: int = _FUN_W):
    for (gp, fun), cx in zip(items, xs):
        bx = cx - _BOX_H // 2
        c.label_box_rot90cw(gp, bx, y_inner, _GP_W, _BOX_H, _gp_box_color(gp),
                            "center", _LBL_SCALE)
        c.label_box_rot90cw(fun, bx, y_inner + _GP_W + _GAP, fun_w, _BOX_H,
                            color_for(fun, gp), "left", _LBL_SCALE)


def render_png(path: Path):
    fun_w = _FUN_W
    _w, _h, rows = load_png_rgb(ZERO_GPIO_PNG)
    tw0, th0, top0 = crop_rgb(rows, *_TOP_CROP)
    bw0, bh0, bot0 = crop_rgb(rows, *_BOT_CROP)
    top_w, top_h, top_rows = scale_nn(tw0, th0, top0, _SCALE)
    bot_w, bot_h, bot_rows = scale_nn(bw0, bh0, bot0, _SCALE)

    margin = 24
    title_h = 64
    view_gap = 46
    note_h = 26
    side_w = fun_w + _GAP + _GP_W

    board_col_w = max(top_w, bot_w)
    width = margin + side_w + _GAP + board_col_w + _GAP + side_w + margin
    max_x = width - margin

    legend_rows = 1
    x = margin
    for name, _col in LEGEND:
        item_w = 18 + text_width(name, _LBL_SCALE) + 22
        if x + item_w > max_x and x > margin:
            legend_rows += 1
            x = margin
        x += item_w
    legend_h = legend_rows * (10 * _LBL_SCALE + 10) + 8

    bottom_stack_h = _GP_W + _GAP + fun_w
    top_sec_h = top_h + _GAP + bottom_stack_h
    bot_sec_h = max(_block_h(len(BOT_PADS)), bot_h)
    height = (
        margin + title_h + top_sec_h + view_gap + 18 + bot_sec_h + note_h + legend_h + margin
    )

    text_c = (25, 25, 30)
    sub_c = (90, 90, 100)
    c = Canvas(width, height)

    c.text("RP2040-Zero SliderDMC pinout", margin, margin, text_c, 3)
    c.text("Top + bottom view  USB at top  src/config.h  DragonFrame DMC bridge", margin, margin + 34, sub_c, 1)

    sec_y = margin + title_h
    board_left = margin + side_w + _GAP
    top_x = board_left + (board_col_w - top_w) // 2
    top_y = sec_y
    c.blit_rgb(top_x, top_y, top_w, top_h, top_rows)

    left_ys = [
        y - _BOX_H // 2
        for y in _pad_centers(len(LEFT), _PAD_LEFT_Y0, _PAD_LEFT_PITCH, top_y)
    ]
    right_ys = [
        y - _BOX_H // 2
        for y in _pad_centers(len(RIGHT), _PAD_RIGHT_Y0, _PAD_RIGHT_PITCH, top_y)
    ]
    _draw_column(c, LEFT, left_ys, top_x, "left", fun_w)
    _draw_column(c, RIGHT, right_ys, top_x + top_w + _GAP, "right", fun_w)
    _draw_bottom_column(
        c,
        BOTTOM,
        _pad_centers(len(BOTTOM), _PAD_BOTTOM_X0, _PAD_BOTTOM_PITCH, top_x),
        top_y + top_h + _GAP,
        fun_w,
    )

    bot_sec_y = sec_y + top_sec_h + view_gap + 18
    bot_x = board_left + (board_col_w - bot_w) // 2
    bot_y = bot_sec_y + (bot_sec_h - bot_h) // 2
    c.blit_rgb(bot_x, bot_y, bot_w, bot_h, bot_rows)
    c.text("Bottom view  underside SMD pads", board_left, bot_sec_y - 20, sub_c, 1)

    pad_ys = _row_ys(len(BOT_PADS), bot_sec_y + (bot_sec_h - _block_h(len(BOT_PADS))) // 2)
    _draw_column(c, BOT_PADS, pad_ys, board_left + board_col_w + _GAP, "right", fun_w)
    c.text("GP16 = onboard WS2812 status LED", board_left, bot_sec_y + bot_sec_h + 6, sub_c, 1)

    ly = bot_sec_y + bot_sec_h + note_h
    sw = 10 * _LBL_SCALE
    x = margin
    for name, col in LEGEND:
        item_w = 18 + text_width(name, _LBL_SCALE) + 22
        if x + item_w > max_x and x > margin:
            x = margin
            ly += sw + 10
        c.fill_rect(x, ly, sw, sw, col)
        c.text(name, x + sw + 8, ly + 1, text_c, _LBL_SCALE)
        x += item_w

    c.save(path)


def main():
    OUT_PNG.mkdir(parents=True, exist_ok=True)
    ascii_path = OUT_TXT / "DMC_RP2040zero_pinout.txt"
    png_path = OUT_PNG / "DMC_RP2040zero_pinout.png"
    ascii_path.write_text(render_ascii(), encoding="utf-8")
    render_png(png_path)
    print("wrote", ascii_path)
    print("wrote", png_path)


if __name__ == "__main__":
    main()
