# Generate RP2040-Zero pinout ASCII + PNG (stdlib only).
#   python tools/render_rp2040zero_pinout_SliderMC.py          # SliderMC
#   python tools/render_rp2040zero_pinout_SliderMC.py button   # JKSlider UIC
#
# Top view + bottom view (USB at top).
# Label columns follow the Waveshare diagram: left edge on the left, GP0..GP13 on
# the right, and the underside SMD pads on the bottom view.

from __future__ import annotations

import sys
from pathlib import Path

from pinout_common import (
    C_BTN,
    C_CTRL,
    C_DBG,
    C_DRV,
    C_DSP,
    C_EXT,
    C_FREE,
    C_GND,
    C_GP,
    C_LED,
    C_PINNUM,
    C_POT,
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
    ("GP29", "LED"),
    ("GP28", "BUZZER*"),
    ("GP27", "EXT_0"),
    ("GP26", "EXT_1"),
    ("GP15", "EXT_2"),
    ("GP14", "EXT_3"),
]

# Right edge, top→bottom.
RIGHT = [
    ("GP0", "DRV_STEP"),
    ("GP1", "DRV_DIR"),
    ("GP2", "DRV_EN"),
    ("GP3", "DRV_ERROR"),
    ("GP4", "SW_HOME*"),
    ("GP5", "DRV_STEP2"),
    ("GP6", "DRV_DIR2"),
    ("GP7", "DRV_ERROR2"),
    ("GP8", "SW_HOME2*"),
]

# Bottom edge, left→right (drawn rotated 90 deg CW under the matching pad).
BOTTOM = [
    ("GP13", "UART_RX"),
    ("GP12", "UART_TX"),
    ("GP11", "free"),
    ("GP10", "SW_LIMIT_L*"),
    ("GP9", "SW_LIMIT_R*"),
]

# Bottom view SMD pads, top→bottom.
BOT_PADS = [
    ("GND", "GND"),
    ("GP25", "SW_LIMIT_L2*"),
    ("GP24", "SW_LIMIT_R2*"),
    ("GP23", "DBG_FIFO"),
    ("GP22", "DBG_MOV"),
    ("GP21", "DBG_MOV_CONST"),
    ("GP20", "DBG_CMD"),
    ("GP19", "DBG_IRQ"),
    ("GP18", "DBG_UNDERRUN"),
    ("GP17", "DRV_EN2"),
]

# JKSlider UIC on RP2040-Zero, button mode (assets/rp2040zero_pinout_button.txt).
BUTTON_LEFT = [
    ("5V", "5V"),
    ("GND", "GND"),
    ("3V3", "3V3"),
    ("GP29", "CTRL_CAMERA"),
    ("GP28", "POT_JOYSTICK"),
    ("GP27", "POT_ACCEL"),
    ("GP26", "POT_SPEED"),
    ("GP15", "DSP_I2C_SCL"),
    ("GP14", "DSP_I2C_SDA"),
]
BUTTON_RIGHT = [
    ("GP0", "BTN_STOP"),
    ("GP1", "BTN_MOVE_L"),
    ("GP2", "BTN_MOVE_R"),
    ("GP3", "BTN_FAST_L"),
    ("GP4", "BTN_FAST_R"),
    ("GP5", "BTN_A"),
    ("GP6", "BTN_B"),
    ("GP7", "BTN_C"),
    ("GP8", "BTN_OPTION"),
]
BUTTON_BOTTOM = [
    ("GP13", "UART_RX"),
    ("GP12", "UART_TX"),
    ("GP11", "LED_R"),
    ("GP10", "LED_G"),
    ("GP9", "LED_B"),
]
BUTTON_BOT_PADS = [
    ("GND", "GND"),
    ("GP25", "BTN_DELAY"),
    ("GP24", "BTN_TIMELAPSE"),
    ("GP23", "free"),
    ("GP22", "free"),
    ("GP21", "free"),
    ("GP20", "free"),
    ("GP19", "free"),
    ("GP18", "free"),
    ("GP17", "free"),
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
BUTTON_LEGEND = [
    ("BTN_*", C_BTN),
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


def _layout(mode: str):
    if mode == "button":
        return {
            "left": BUTTON_LEFT,
            "right": BUTTON_RIGHT,
            "bottom": BUTTON_BOTTOM,
            "bot_pads": BUTTON_BOT_PADS,
            "legend": BUTTON_LEGEND,
            "fun_w": 186,
            "ascii_head": (
                "Waveshare RP2040-Zero — JKSlider UIC pinout (USB at top)",
                'BUTTON mode  |  overlay in SliderPins.py (RP2040-Zero keys)',
            ),
            "ascii_notes": [
                "Legend: pots on ADC GP26–28; UART0 to SliderMC on GP12 (TX) / GP13 (RX) @ 115200 baud.",
                "OLED I2C1 SDA/SCL on GP14/15 (set DSP_I2C_ID = 1). RGB LED on GP11/10/9.",
                "CTRL_CAMERA on GP29. DELAY / TIMELAPSE on underside GP25 / GP24.",
                "Button mode: one GPIO per BTN_* (active-low). JKS_INPUT_MODE = \"button\".",
                "GP16 = onboard WS2812 (optional PIN_NEOPIXEL). GP17–23 free SMD pads.",
                "Naming: BTN_* = electronics/pinout; User Manual uses plain names (STOP, MOVE_L, …).",
            ],
            "png_title": "RP2040-Zero JKSlider UIC pinout",
            "png_sub": "Top + bottom view  USB at top  BUTTON mode  SliderPins overlay",
            "txt_name": "rp2040zero_pinout_button.txt",
            "png_name": "rp2040zero_pinout_button.png",
        }
    return {
        "left": LEFT,
        "right": RIGHT,
        "bottom": BOTTOM,
        "bot_pads": BOT_PADS,
        "legend": LEGEND,
        "fun_w": _FUN_W,
        "ascii_head": (
            "Waveshare RP2040-Zero — SliderMC pinout (USB at top)",
            "Defaults in include/pins.h (BOARD_RP2040_ZERO)",
        ),
        "ascii_notes": [
            "Legend: motor DRV on GP0–3; axis2 STEP/DIR/ERR/HOME on GP5–8; EN2 on GP17.",
            "EXT_0…3 on GP27/26/15/14 (X0…X3); UART 115200 baud GP12/13; axis2_use supported.",
            "SW_* / LIMIT_* off until CS …_use=1. LIMIT2 on GP24/25; DBG GP18–23 (OK with axis2).",
            "GP29 status LED; GP11/16/28 free; GP16 = onboard RGB unused.",
            "Pin names match IX / VG (axis2 rows only when axis2_use=1).",
        ],
        "png_title": "RP2040-Zero SliderMC pinout",
        "png_sub": "Top + bottom view  USB at top  BOARD_RP2040_ZERO  pins.h defaults",
        "txt_name": "rp2040zero_pinout_mc.txt",
        "png_name": "rp2040zero_pinout_mc.png",
    }


def render_ascii(mode: str = "mc") -> str:
    lay = _layout(mode)
    left, right = lay["left"], lay["right"]
    bottom, bot_pads = lay["bottom"], lay["bot_pads"]
    head0, head1 = lay["ascii_head"]
    lines = [
        head0,
        head1,
        "",
        "    function     pad                  pad    function",
        "                        +---- USB ----+",
    ]
    for (lg, lf), (rg, rf) in zip(left, right):
        lines.append("  %-14s %-6s |o           o| %-6s %s" % (lf, lg, rg, rf))
    lines.extend(
        [
            "                        +-------------+",
            "                         " + " ".join(g[2:] for g, _ in bottom),
            "",
            "Bottom edge (left→right):",
        ]
    )
    for gp, fun in bottom:
        lines.append("  %-6s %s" % (gp, fun))
    lines.extend(["", "Bottom-side SMD pads (top→bottom):"])
    for gp, fun in bot_pads:
        lines.append("  %-6s %s" % (gp, fun))
    lines.append("")
    lines.extend(lay["ascii_notes"])
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
    """GP + function labels rotated 90 deg CW, hanging under each bottom pad."""
    for (gp, fun), cx in zip(items, xs):
        bx = cx - _BOX_H // 2
        c.label_box_rot90cw(gp, bx, y_inner, _GP_W, _BOX_H, _gp_box_color(gp),
                            "center", _LBL_SCALE)
        c.label_box_rot90cw(fun, bx, y_inner + _GP_W + _GAP, fun_w, _BOX_H,
                            color_for(fun, gp), "left", _LBL_SCALE)


def render_png(path: Path, mode: str = "mc"):
    lay = _layout(mode)
    left, right = lay["left"], lay["right"]
    bottom, bot_pads = lay["bottom"], lay["bot_pads"]
    legend = lay["legend"]
    fun_w = lay["fun_w"]

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
    for name, _col in legend:
        item_w = 18 + text_width(name, _LBL_SCALE) + 22
        if x + item_w > max_x and x > margin:
            legend_rows += 1
            x = margin
        x += item_w
    legend_h = legend_rows * (10 * _LBL_SCALE + 10) + 8

    bottom_stack_h = _GP_W + _GAP + fun_w
    top_sec_h = top_h + _GAP + bottom_stack_h
    bot_sec_h = max(_block_h(len(bot_pads)), bot_h)
    height = (
        margin + title_h + top_sec_h + view_gap + 18 + bot_sec_h + note_h + legend_h + margin
    )

    text_c = (25, 25, 30)
    sub_c = (90, 90, 100)
    c = Canvas(width, height)

    c.text(lay["png_title"], margin, margin, text_c, 3)
    c.text(lay["png_sub"], margin, margin + 34, sub_c, 1)

    sec_y = margin + title_h
    board_left = margin + side_w + _GAP
    top_x = board_left + (board_col_w - top_w) // 2
    top_y = sec_y
    c.blit_rgb(top_x, top_y, top_w, top_h, top_rows)

    left_ys = [
        y - _BOX_H // 2
        for y in _pad_centers(len(left), _PAD_LEFT_Y0, _PAD_LEFT_PITCH, top_y)
    ]
    right_ys = [
        y - _BOX_H // 2
        for y in _pad_centers(len(right), _PAD_RIGHT_Y0, _PAD_RIGHT_PITCH, top_y)
    ]
    _draw_column(c, left, left_ys, top_x, "left", fun_w)
    _draw_column(c, right, right_ys, top_x + top_w + _GAP, "right", fun_w)
    _draw_bottom_column(
        c,
        bottom,
        _pad_centers(len(bottom), _PAD_BOTTOM_X0, _PAD_BOTTOM_PITCH, top_x),
        top_y + top_h + _GAP,
        fun_w,
    )

    bot_sec_y = sec_y + top_sec_h + view_gap + 18
    bot_x = board_left + (board_col_w - bot_w) // 2
    bot_y = bot_sec_y + (bot_sec_h - bot_h) // 2
    c.blit_rgb(bot_x, bot_y, bot_w, bot_h, bot_rows)
    c.text("Bottom view  underside SMD pads", board_left, bot_sec_y - 20, sub_c, 1)

    pad_ys = _row_ys(len(bot_pads), bot_sec_y + (bot_sec_h - _block_h(len(bot_pads))) // 2)
    _draw_column(c, bot_pads, pad_ys, board_left + board_col_w + _GAP, "right", fun_w)
    gp16_note = (
        "GP16 = onboard WS2812 (optional PIN_NEOPIXEL)"
        if mode == "button"
        else "GP16 = onboard RGB LED (unused by firmware)"
    )
    c.text(gp16_note, board_left, bot_sec_y + bot_sec_h + 6, sub_c, 1)

    ly = bot_sec_y + bot_sec_h + note_h
    sw = 10 * _LBL_SCALE
    x = margin
    for name, col in legend:
        item_w = 18 + text_width(name, _LBL_SCALE) + 22
        if x + item_w > max_x and x > margin:
            x = margin
            ly += sw + 10
        c.fill_rect(x, ly, sw, sw, col)
        c.text(name, x + sw + 8, ly + 1, text_c, _LBL_SCALE)
        x += item_w

    c.save(path)


def main():
    modes = sys.argv[1:] or ["mc"]
    unknown = [m for m in modes if m not in ("mc", "button")]
    if unknown:
        print("unknown mode(s):", ", ".join(unknown), file=sys.stderr)
        print("usage: python tools/render_rp2040zero_pinout_SliderMC.py [mc] [button]", file=sys.stderr)
        sys.exit(2)

    OUT_PNG.mkdir(parents=True, exist_ok=True)
    for mode in modes:
        lay = _layout(mode)
        ascii_path = OUT_TXT / lay["txt_name"]
        png_path = OUT_PNG / lay["png_name"]
        ascii_path.write_text(render_ascii(mode), encoding="utf-8")
        render_png(png_path, mode)
        print("wrote", ascii_path)
        print("wrote", png_path)


if __name__ == "__main__":
    main()
