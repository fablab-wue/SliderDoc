# Generate Pico board pinout ASCII + PNG for SliderMC_BDC (stdlib only).
#   python tools/render_pico_pinout_SliderMC_BDC.py
#
# Top view, USB at top. Pins from SliderMC_BDC include/pins.h.

from __future__ import annotations

from pathlib import Path

from pinout_common import (
    C_BUZZER,
    C_CAMERA,
    C_CTRL_PIN,
    C_DRV,
    C_DRV_ERR,
    C_GND,
    C_GP,
    C_PINNUM,
    C_POT,
    C_PWR_3V3,
    C_PWR_5V,
    C_SERVO,
    C_SW,
    C_UART,
    OUT_PNG,
    Canvas,
    color_for,
    crop_rgb,
    load_png_rgb,
    text_width,
)

DOCS = Path(__file__).resolve().parents[1]
OUT_TXT = DOCS / "assets"

LEFT = [
    ("GP0", "ENC_A_1"),
    ("GP1", "ENC_B_1"),
    ("GND", "GND"),
    ("GP2", "DRV_A_1"),
    ("GP3", "DRV_B_1"),
    ("GP4", "DRV_C_1"),
    ("GP5", "DRV_D_1"),
    ("GND", "GND"),
    ("GP6", "LIMIT_L_1"),
    ("GP7", "LIMIT_R_1"),
    ("GP8", "ENC_A_2"),
    ("GP9", "ENC_B_2"),
    ("GND", "GND"),
    ("GP10", "DRV_A_2"),
    ("GP11", "DRV_B_2"),
    ("GP12", "DRV_C_2"),
    ("GP13", "DRV_D_2"),
    ("GND", "GND"),
    ("GP14", "LIMIT_L_2"),
    ("GP15", "LIMIT_R_2"),
]

RIGHT = [
    ("VBUS", "VBUS"),
    ("VSYS", "VSYS"),
    ("GND", "GND"),
    ("3V3_EN", "3V3_EN"),
    ("3V3", "3V3 OUT"),
    ("ADC_VREF", "ADC_VREF"),
    ("GP28", "BUZZER"),
    ("AGND", "ADC GND"),
    ("GP27", "CUR_ERR_1"),
    ("GP26", "CUR_ERR_2"),
    ("RUN", "RUN"),
    ("GP22", "CAMERA_CTRL"),
    ("GND", "GND"),
    ("GP21", "SERVO_1"),
    ("GP20", "SERVO_2"),
    ("GP19", "SERVO_3"),
    ("GP18", "SERVO_4"),
    ("GND", "GND"),
    ("GP17", "UART_RX"),
    ("GP16", "UART_TX"),
]

PICO_GPIO_PNG = OUT_PNG / "raspberry-pi-pico-gpio.png"
_BOARD_CROP = (411, 24, 658, 625)
_PIN_Y0_ABS = 39
_PIN_PITCH = 30


def render_ascii() -> str:
    lines = [
        "Raspberry Pi Pico — SliderMC_BDC pinout (top view, USB at top)",
        "Defaults in SliderMC_BDC include/pins.h",
        "",
        "        function         pin              pin        function",
        "                         +--- USB ---+",
    ]
    for i, ((lg, ll), (rg, rl)) in enumerate(zip(LEFT, RIGHT)):
        pn_l = i + 1
        pn_r = 40 - i
        lines.append(
            "  %-16s %-7s %2d |o         o| %-2d %-8s %s"
            % (ll, lg, pn_l, pn_r, rg, rl)
        )
    lines.extend(
        [
            "                         +-----------+",
            "",
            "Legend: motor1 ENC GP0/1, DRV_A..D GP2–5, LIMIT GP6/7.",
            "Motor2 ENC GP8/9, DRV_A..D GP10–13, LIMIT GP14/15.",
            "CUR_ERR_1 GP27, CUR_ERR_2 GP26. UART 115200 baud GP16/17.",
            "SERVO_1..4 share EXT_4..EXT_1 on GP21..GP18. Servo 1 takes EXT_4 first.",
            "GP22 CAMERA_CTRL. GP28 buzzer. GP25 onboard LED (not on the header).",
            "Pico motor-1 PWM shares a slice with a servo: DRV_A_1/SERVO_4, DRV_B_1/SERVO_3,",
            "DRV_C_1/SERVO_2, DRV_D_1/SERVO_1. Pico 2 reuses this header map.",
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
    board_w, board_h, board_rows, pin_ys = load_pico_board()

    margin = 24
    title_h = 56
    gap = 4
    fun_w = 128
    gp_w = 52
    pin_w = 28
    box_h = min(22, _PIN_PITCH - 6)
    side_w = fun_w + gap + gp_w + gap + pin_w
    width = margin + side_w + board_w + side_w + margin
    legend = [
        ("DRV_*", C_DRV),
        ("CUR_ERR", C_DRV_ERR),
        ("ENC_*", C_POT),
        ("LIMIT_*", C_SW),
        ("SERVO_*", C_SERVO),
        ("UART_*", C_UART),
        ("CAMERA_CTRL", C_CAMERA),
        ("BUZZER", C_BUZZER),
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

    c.text("Pico SliderMC_BDC pinout", margin, margin, text_c, 2)
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
        lg, ll = LEFT[i]
        rg, rl = RIGHT[i]
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
    ascii_path = OUT_TXT / "MCBDC_Pico_pinout.txt"
    png_path = OUT_PNG / "MCBDC_Pico_pinout.png"
    ascii_path.write_text(render_ascii(), encoding="utf-8")
    render_png(png_path)
    print("wrote", ascii_path)
    print("wrote", png_path)


if __name__ == "__main__":
    main()
