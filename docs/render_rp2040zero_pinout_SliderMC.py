# Generate RP2040-Zero SliderMC pinout ASCII + PNG (stdlib only).
#   python docs/render_rp2040zero_pinout.py
#
# Top view + bottom view (USB at top). Pins from include/pins.h BOARD_RP2040_ZERO.
# Label columns follow the Waveshare diagram: left edge on the left, GP0..GP13 on
# the right, and the underside SMD pads on the bottom view.

from __future__ import annotations

from pathlib import Path

from pinout_common import (
    C_DBG,
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

DOCS = Path(__file__).resolve().parent
OUT_TXT = DOCS
ZERO_GPIO_PNG = OUT_PNG / "waveshare-rp2040-zero-gpio.png"

# Board photos cropped from the Waveshare diagram (board + castellated pads only,
# external labels excluded). Derived by scanning for PCB navy + gold pad pixels.
_TOP_CROP = (321, 176, 509, 441)
_BOT_CROP = (321, 593, 509, 841)
_SCALE = 2

# Label geometry: 2x the Pico renderer so proportions against the 2x board photo
# match img/pico_pinout_mc.png (box height 44 at pad pitch ~54 -> comparable gap).
_LBL_SCALE = 2
_PITCH = 52
_BOX_H = 44
_FUN_W = 172
_GP_W = 64
_GAP = 6

# Castellated pad positions inside _TOP_CROP, in source pixels (linear fit over
# the gold pad centroids detected in the board photo). 9 pads per side edge,
# 5 along the bottom edge.
_PAD_LEFT_Y0, _PAD_LEFT_PITCH = 32.5, 27.27
_PAD_RIGHT_Y0, _PAD_RIGHT_PITCH = 34.15, 26.86
_PAD_BOTTOM_X0, _PAD_BOTTOM_PITCH = 43.6, 26.1

# Left edge, top→bottom.
LEFT = [
    ("5V", "5V"),
    ("GND", "GND"),
    ("3V3", "3V3"),
    ("GP29", "DRV_ERROR"),
    ("GP28", "DRV_EN"),
    ("GP27", "DRV_DIR"),
    ("GP26", "DRV_STEP"),
    ("GP15", "free"),
    ("GP14", "LED"),
]

# Right edge, top→bottom.
RIGHT = [
    ("GP0", "EXT_0"),
    ("GP1", "EXT_1"),
    ("GP2", "EXT_2"),
    ("GP3", "EXT_3"),
    ("GP4", "EXT_4"),
    ("GP5", "EXT_5"),
    ("GP6", "EXT_6"),
    ("GP7", "EXT_7"),
    ("GP8", "EXT_8"),
]

# Bottom edge, left→right (drawn rotated 90 deg CW under the matching pad).
BOTTOM = [
    ("GP13", "UART_RX"),
    ("GP12", "UART_TX"),
    ("GP11", "SW_LIMIT_R*"),
    ("GP10", "SW_LIMIT_L*"),
    ("GP9", "SW_HOME*"),
]

# Bottom view SMD pads, top→bottom.
BOT_PADS = [
    ("GND", "GND"),
    ("GP25", "DBG_UNDERRUN"),
    ("GP24", "DBG_IRQ"),
    ("GP23", "DBG_CMD"),
    ("GP22", "DBG_MOV_CONST"),
    ("GP21", "DBG_MOV"),
    ("GP20", "DBG_FIFO"),
    ("GP19", "free"),
    ("GP18", "free"),
    ("GP17", "EXT_9"),
]

LEGEND = [
    ("EXT_*", C_EXT),
    ("DRV_*", C_DRV),
    ("UART_*", C_UART),
    ("SW_*", C_SW),
    ("DBG_*", C_DBG),
    ("LED", C_LED),
    ("free", C_FREE),
    ("GND", C_GND),
    ("power 3V3", C_PWR_3V3),
    ("power 5V", C_PWR_5V),
]


def render_ascii() -> str:
    lines = [
        "Waveshare RP2040-Zero — SliderMC pinout (USB at top)",
        "Defaults in include/pins.h (BOARD_RP2040_ZERO)",
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
    lines.extend(
        [
            "",
            "Legend: EXT_0…8 on GP0–8, EXT_9 on GP17 (X0…X9); UART 1 Mbaud GP12/13;",
            "motor DRV on GP26–29 (GP29 DRV_ERROR always polled).",
            "SW_HOME* / SW_LIMIT_* off until CS …_use=1.",
            "GP20–25 DBG_* (DEBUG_HW only, brown); GP14 status LED; GP15/18/19 free.",
            "GP16 = onboard RGB LED, unused by firmware.",
            "Pin names match P / IX (Pinout) commands.",
        ]
    )
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
    """Top-y of each label box for an n-row column starting at `top`."""
    return [top + i * _PITCH for i in range(n)]


def _pad_centers(n: int, first: float, pitch: float, origin: int) -> list[int]:
    """Screen coords of n evenly pitched pads, scaled from the source photo."""
    return [origin + int(round((first + i * pitch) * _SCALE)) for i in range(n)]


def _draw_column(c: Canvas, items, ys, x_inner: int, side: str):
    for (gp, fun), by in zip(items, ys):
        fc = color_for(fun, gp)
        gc = _gp_box_color(gp)
        if side == "left":
            gx = x_inner - _GP_W
            fx = gx - _GAP - _FUN_W
            c.label_box(fun, fx, by, _FUN_W, _BOX_H, fc, "left", _LBL_SCALE)
            c.label_box(gp, gx, by, _GP_W, _BOX_H, gc, "center", _LBL_SCALE)
        else:
            c.label_box(gp, x_inner, by, _GP_W, _BOX_H, gc, "center", _LBL_SCALE)
            c.label_box(
                fun, x_inner + _GP_W + _GAP, by, _FUN_W, _BOX_H, fc, "left", _LBL_SCALE
            )


def _draw_bottom_column(c: Canvas, items, xs, y_inner: int):
    """GP + function labels rotated 90 deg CW, hanging under each bottom pad."""
    for (gp, fun), cx in zip(items, xs):
        bx = cx - _BOX_H // 2
        c.label_box_rot90cw(gp, bx, y_inner, _GP_W, _BOX_H, _gp_box_color(gp),
                            "center", _LBL_SCALE)
        c.label_box_rot90cw(fun, bx, y_inner + _GP_W + _GAP, _FUN_W, _BOX_H,
                            color_for(fun, gp), "left", _LBL_SCALE)


def render_png(path: Path):
    _w, _h, rows = load_png_rgb(ZERO_GPIO_PNG)
    tw0, th0, top0 = crop_rgb(rows, *_TOP_CROP)
    bw0, bh0, bot0 = crop_rgb(rows, *_BOT_CROP)
    top_w, top_h, top_rows = scale_nn(tw0, th0, top0, _SCALE)
    bot_w, bot_h, bot_rows = scale_nn(bw0, bh0, bot0, _SCALE)

    margin = 24
    title_h = 64
    view_gap = 46
    note_h = 26
    side_w = _FUN_W + _GAP + _GP_W

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

    bottom_stack_h = _GP_W + _GAP + _FUN_W
    top_sec_h = top_h + _GAP + bottom_stack_h
    bot_sec_h = max(_block_h(len(BOT_PADS)), bot_h)
    height = (
        margin + title_h + top_sec_h + view_gap + 18 + bot_sec_h + note_h + legend_h + margin
    )

    text_c = (25, 25, 30)
    sub_c = (90, 90, 100)
    c = Canvas(width, height)

    c.text("RP2040-Zero SliderMC pinout", margin, margin, text_c, 3)
    c.text(
        "Top + bottom view  USB at top  BOARD_RP2040_ZERO  pins.h defaults",
        margin,
        margin + 34,
        sub_c,
        1,
    )

    sec_y = margin + title_h
    board_left = margin + side_w + _GAP
    top_x = board_left + (board_col_w - top_w) // 2
    top_y = sec_y
    c.blit_rgb(top_x, top_y, top_w, top_h, top_rows)

    # Each label box is centred on the castellated pad it belongs to.
    left_ys = [
        y - _BOX_H // 2
        for y in _pad_centers(len(LEFT), _PAD_LEFT_Y0, _PAD_LEFT_PITCH, top_y)
    ]
    right_ys = [
        y - _BOX_H // 2
        for y in _pad_centers(len(RIGHT), _PAD_RIGHT_Y0, _PAD_RIGHT_PITCH, top_y)
    ]
    _draw_column(c, LEFT, left_ys, top_x, "left")
    _draw_column(c, RIGHT, right_ys, top_x + top_w + _GAP, "right")
    _draw_bottom_column(
        c,
        BOTTOM,
        _pad_centers(len(BOTTOM), _PAD_BOTTOM_X0, _PAD_BOTTOM_PITCH, top_x),
        top_y + top_h + _GAP,
    )

    bot_sec_y = sec_y + top_sec_h + view_gap + 18
    bot_x = board_left + (board_col_w - bot_w) // 2
    bot_y = bot_sec_y + (bot_sec_h - bot_h) // 2
    c.blit_rgb(bot_x, bot_y, bot_w, bot_h, bot_rows)
    c.text("Bottom view  underside SMD pads", board_left, bot_sec_y - 20, sub_c, 1)

    pad_ys = _row_ys(len(BOT_PADS), bot_sec_y + (bot_sec_h - _block_h(len(BOT_PADS))) // 2)
    _draw_column(c, BOT_PADS, pad_ys, board_left + board_col_w + _GAP, "right")
    c.text(
        "GP16 = onboard RGB LED (unused by firmware)",
        board_left,
        bot_sec_y + bot_sec_h + 6,
        sub_c,
        1,
    )

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
    ascii_path = OUT_TXT / "rp2040zero_pinout_mc.txt"
    png_path = OUT_PNG / "rp2040zero_pinout_mc.png"
    ascii_path.write_text(render_ascii(), encoding="utf-8")
    render_png(png_path)
    print("wrote", ascii_path)
    print("wrote", png_path)


if __name__ == "__main__":
    main()
