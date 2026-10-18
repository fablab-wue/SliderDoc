# Generate RP2040-Zero pinout ASCII + PNG for SliderMC_BDC.
#   python tools/render_rp2040zero_pinout_SliderMC_BDC.py

from __future__ import annotations

from pathlib import Path

import render_rp2040zero_pinout_SliderMC as z
from pinout_common import (
    C_BUZZER,
    C_CAMERA,
    C_DRV,
    C_DRV_ERR,
    C_FREE,
    C_GND,
    C_LED,
    C_POT,
    C_PWR_3V3,
    C_PWR_5V,
    C_SERVO,
    C_SW,
    C_UART,
)

DOCS = Path(__file__).resolve().parents[1]

LEFT = [
    ("5V", "5V"),
    ("GND", "GND"),
    ("3V3", "3V3"),
    ("GP29", "CUR_ERR_1"),
    ("GP28", "CUR_ERR_2"),
    ("GP27", "SERVO_1"),
    ("GP26", "SERVO_2"),
    ("GP15", "SERVO_3"),
    ("GP14", "SERVO_4"),
]
RIGHT = [
    ("GP0", "ENC_A_1"),
    ("GP1", "ENC_B_1"),
    ("GP2", "DRV_A_1"),
    ("GP3", "DRV_B_1"),
    ("GP4", "DRV_C_1"),
    ("GP5", "DRV_D_1"),
    ("GP6", "LIMIT_L_1"),
    ("GP7", "LIMIT_R_1"),
    ("GP8", "free"),
]
BOTTOM = [
    ("GP13", "UART_RX"),
    ("GP12", "UART_TX"),
    ("GP11", "LED"),
    ("GP10", "BUZZER"),
    ("GP9", "CAMERA_CTRL"),
]
BOT_PADS = [
    ("GND", "GND"),
    ("GP25", "free"),
    ("GP24", "LIMIT_R_2"),
    ("GP23", "LIMIT_L_2"),
    ("GP22", "DRV_D_2"),
    ("GP21", "DRV_C_2"),
    ("GP20", "DRV_B_2"),
    ("GP19", "DRV_A_2"),
    ("GP18", "ENC_B_2"),
    ("GP17", "ENC_A_2"),
]


def main():
    original = z._layout

    def layout(_mode: str = "mc"):
        lay = original("mc")
        lay["left"] = LEFT
        lay["right"] = RIGHT
        lay["bottom"] = BOTTOM
        lay["bot_pads"] = BOT_PADS
        lay["fun_w"] = 200
        lay["legend"] = [
            ("DRV_*", C_DRV),
            ("CUR_ERR", C_DRV_ERR),
            ("ENC_*", C_POT),
            ("LIMIT_*", C_SW),
            ("SERVO_*", C_SERVO),
            ("UART_*", C_UART),
            ("CAMERA_CTRL", C_CAMERA),
            ("BUZZER", C_BUZZER),
            ("LED", C_LED),
            ("free", C_FREE),
            ("GND", C_GND),
            ("power 3V3", C_PWR_3V3),
            ("power 5V", C_PWR_5V),
        ]
        lay["ascii_head"] = (
            "Waveshare RP2040-Zero — SliderMC_BDC pinout (USB at top)",
            "Defaults in SliderMC_BDC include/pins.h (BOARD_RP2040_ZERO)",
        )
        lay["ascii_notes"] = [
            "Motor 1: ENC GP0/1, DRV_A..D GP2–5, LIMIT GP6/7. GP8 free.",
            "CUR_ERR_1 GP29, CUR_ERR_2 GP28. UART 115200 baud GP12/13.",
            "SERVO_1..4 share EXT_4..EXT_1 on GP27, GP26, GP15, GP14.",
            "Motor 2 underside: ENC GP17/18, DRV_A..D GP19–22, LIMIT GP23/24.",
            "GP11 LED, GP10 buzzer, GP9 camera. GP16 onboard WS2812. GP25 free.",
            "A stock header brings out GP0–15 and GP26–29 only. RP2350-Zero reuses this map.",
        ]
        lay["png_title"] = "RP2040-Zero SliderMC_BDC pinout"
        lay["png_sub"] = "Top + bottom view  USB at top  two DC motors  pins.h defaults"
        lay["txt_name"] = "MCBDC_RP2040zero_pinout.txt"
        lay["png_name"] = "MCBDC_RP2040zero_pinout.png"
        return lay

    z._layout = layout
    text = z.render_ascii("mc")
    ascii_path = DOCS / "assets" / "MCBDC_RP2040zero_pinout.txt"
    png_path = DOCS / "assets" / "img" / "MCBDC_RP2040zero_pinout.png"
    ascii_path.write_text(text, encoding="utf-8")
    z.render_png(png_path, "mc")
    print("wrote", ascii_path)
    print("wrote", png_path)


if __name__ == "__main__":
    main()
