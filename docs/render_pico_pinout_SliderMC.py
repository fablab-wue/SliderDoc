# Generate Pico board pinout ASCII + PNG for SliderMC (stdlib only).
#   python docs/render_pico_pinout.py
#
# Top view, USB at top. Pins from include/pins.h + data/mc.ini.

from __future__ import annotations

from pathlib import Path

from pinout_common import (
    C_CTRL_PIN,
    C_DBG,
    C_DRV,
    C_EXT,
    C_FREE,
    C_GND,
    C_GP,
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
    text_width,
)

DOCS = Path(__file__).resolve().parent
OUT_TXT = DOCS

# Left / right edge, top→bottom (USB at top). Official 40-pin header map.
LEFT = [
    ("GP0", "EXT_0"),
    ("GP1", "EXT_1"),
    ("GND", "GND"),
    ("GP2", "EXT_2"),
    ("GP3", "EXT_3"),
    ("GP4", "EXT_4"),
    ("GP5", "EXT_5"),
    ("GND", "GND"),
    ("GP6", "EXT_6"),
    ("GP7", "EXT_7"),
    ("GP8", "EXT_8"),
    ("GP9", "EXT_9"),
    ("GND", "GND"),
    ("GP10", "DBG_FIFO"),
    ("GP11", "DBG_MOV"),
    ("GP12", "DBG_MOV_CONST"),
    ("GP13", "DBG_CMD"),
    ("GND", "GND"),
    ("GP14", "DBG_IRQ"),
    ("GP15", "DBG_UNDERRUN"),
]

RIGHT = [
    ("VBUS", "VBUS"),
    ("VSYS", "VSYS"),
    ("GND", "GND"),
    ("3V3_EN", "3V3_EN"),
    ("3V3", "3V3 OUT"),
    ("ADC_VREF", "ADC_VREF"),
    ("GP28", "free"),
    ("AGND", "ADC GND"),
    ("GP27", "SW_LIMIT_R*"),
    ("GP26", "SW_LIMIT_L*"),
    ("RUN", "RUN"),
    ("GP22", "SW_HOME*"),
    ("GND", "GND"),
    ("GP21", "DRV_ERROR"),
    ("GP20", "DRV_EN"),
    ("GP19", "DRV_DIR"),
    ("GP18", "DRV_STEP"),
    ("GND", "GND"),
    ("GP17", "UART_RX"),
    ("GP16", "UART_TX"),
]

PICO_GPIO_PNG = OUT_PNG / "raspberry-pi-pico-gpio.png"
_BOARD_CROP = (411, 24, 658, 625)
_PIN_Y0_ABS = 39
_PIN_PITCH = 30


def _labels():
    return list(LEFT), list(RIGHT)


def render_ascii() -> str:
    left, right = _labels()
    lines = [
        "Raspberry Pi Pico — SliderMC pinout (top view, USB at top)",
        "Defaults in include/pins.h + data/mc.ini",
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
            "Legend: EXT_0…9 on GP0–9 (X0…X9); UART 1 Mbaud GP16/17; motor DRV on GP18–20.",
            "SW_HOME* / SW_LIMIT_* off until CS …_use=1. GP21 DRV_ERROR always polled.",
            "GP10–15 DBG_* (DEBUG_HW only, brown); GP23–25, GP28 free.",
            "Pin names match P / IX (Pinout) commands.",
        ]
    )
    return "\n".join(lines) + "\n"


def load_pico_board():
    _w, _h, rows = load_png_rgb(PICO_GPIO_PNG)
    x0, y0, x1, y1 = _BOARD_CROP
    board_w, board_h, board = crop_rgb(rows, x0, y0, x1, y1)
    pin_ys = [_PIN_Y0_ABS - y0 + i * _PIN_PITCH for i in range(20)]
    return board_w, board_h, board, pin_ys


def render_png(path: Path):
    left, right = _labels()
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
        ("EXT_*", C_EXT),
        ("DRV_*", C_DRV),
        ("UART_*", C_UART),
        ("SW_*", C_SW),
        ("DBG_*", C_DBG),
        ("free", C_FREE),
        ("GND", C_GND),
        ("power 3V3", C_PWR_3V3),
        ("power 5V", C_PWR_5V),
    ]
    legend_rows = 1
    x = margin
    max_x = width - margin
    for name, _col in legend:
        item_w = 14 + text_width(name, 1) + 16
        if x + item_w > max_x and x > margin:
            legend_rows += 1
            x = margin
        x += item_w
    legend_h = legend_rows * 16 + 8
    height = margin + title_h + board_h + 12 + legend_h + margin
    text_c = (25, 25, 30)

    c = Canvas(width, height)

    def gp_box_color(pad, pin_num):
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

    c.text("Pico SliderMC pinout", margin, margin, text_c, 2)
    c.text(
        "Top view  USB at top  GP + function  pins.h defaults",
        margin,
        margin + 28,
        (90, 90, 100),
        1,
    )

    board_x = margin + side_w
    board_y = margin + title_h
    c.blit_rgb(board_x, board_y, board_w, board_h, board_rows)

    for i in range(20):
        cy = board_y + pin_ys[i]
        by = cy - box_h // 2
        lg, ll = left[i]
        rg, rl = right[i]
        pn_l = i + 1
        pn_r = 40 - i
        lc = color_for(ll, lg, pn_l)
        rc = color_for(rl, rg, pn_r)

        lx = margin
        c.label_box(ll, lx, by, fun_w, box_h, lc, "left")
        lx += fun_w + gap
        c.label_box(lg, lx, by, gp_w, box_h, gp_box_color(lg, pn_l), "center")
        lx += gp_w + gap
        c.label_box(str(pn_l), lx, by, pin_w, box_h, C_PINNUM, "center")

        rx = board_x + board_w
        c.label_box(str(pn_r), rx, by, pin_w, box_h, C_PINNUM, "center")
        rx += pin_w + gap
        c.label_box(rg, rx, by, gp_w, box_h, gp_box_color(rg, pn_r), "center")
        rx += gp_w + gap
        c.label_box(rl, rx, by, fun_w, box_h, rc, "left")

    ly = board_y + board_h + 10
    x = margin
    row_h_leg = 16
    for name, col in legend:
        item_w = 14 + text_width(name, 1) + 16
        if x + item_w > max_x and x > margin:
            x = margin
            ly += row_h_leg
        c.fill_rect(x, ly, 10, 10, col)
        c.text(name, x + 14, ly + 1, text_c, 1)
        x += item_w

    c.save(path)


def main():
    OUT_PNG.mkdir(parents=True, exist_ok=True)
    ascii_path = OUT_TXT / "pico_pinout_mc.txt"
    png_path = OUT_PNG / "pico_pinout_mc.png"
    ascii_path.write_text(render_ascii(), encoding="utf-8")
    render_png(png_path)
    print("wrote", ascii_path)
    print("wrote", png_path)


if __name__ == "__main__":
    main()
