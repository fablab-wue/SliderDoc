# Generate docs/img/sine_ramp_300mm_s.svg — raised-cosine ramp + FIFO delay/repeat.
# Usage: python docs/render_sine_ramp_fifo.py

import math
from pathlib import Path

V = 300.0
A = 200.0
T = math.pi * V / (2.0 * A)
STEPS_PER_MM = 320.0
PIO = 125_000_000
PULSE = 10
PACK_MIN = 8000
BUDGET_MS = 3.0
PACK_MAX = 64
MAX_HZ = 100_000
N = 128

W, H = 860, 640
ML, MR = 78, 78
MT1, MB1 = 48, 300
MT2, MB2 = 360, 560
XL, XR = ML, W - MR
TW = XR - XL
TH1 = MB1 - MT1
TH2 = MB2 - MT2
LOG_LO, LOG_HI = 3.0, 7.0

OUT = Path(__file__).resolve().parent / "img" / "sine_ramp_300mm_s.svg"


def x_of(t):
    return XL + TW * (t / T)


def y_v(v):
    return MB1 - TH1 * (v / V)


def y_a(a):
    return MB1 - TH1 * (a / A)


def y_d(d):
    ld = math.log10(max(d, 10 ** LOG_LO))
    ld = min(max(ld, LOG_LO), LOG_HI)
    return MB2 - TH2 * ((ld - LOG_LO) / (LOG_HI - LOG_LO))


def y_r(r):
    return MB2 - TH2 * (r / 63.0)


def main():
    pts_v, pts_a, pts_d, pts_r = [], [], [], []
    for i in range(N + 1):
        t = T * i / N
        phi = math.pi * i / N
        v = V * 0.5 * (1.0 - math.cos(phi))
        a = A * math.sin(phi)
        step_hz = min(max(v * STEPS_PER_MM, 1e-12), MAX_HZ)
        delay = max(int(PIO / step_hz) - PULSE, 1)
        if step_hz < PACK_MIN:
            n = 1
        else:
            budget = max(1, int(step_hz * BUDGET_MS / 1000.0))
            n = min(PACK_MAX, budget)
        repeat = n - 1
        x = x_of(t)
        pts_v.append(f"{x:.2f},{y_v(v):.2f}")
        pts_a.append(f"{x:.2f},{y_a(a):.2f}")
        if i > 0:
            pts_d.append(f"{x:.2f},{y_d(delay):.2f}")
        pts_r.append(f"{x:.2f},{y_r(repeat):.2f}")

    v_pack = PACK_MIN / STEPS_PER_MM
    c = 1.0 - 2.0 * v_pack / V
    phi_pack = math.acos(max(-1.0, min(1.0, c)))
    t_pack = T * phi_pack / math.pi
    x_pack = x_of(t_pack)

    mid1 = (MT1 + MB1) / 2.0
    mid2 = (MT2 + MB2) / 2.0
    lines = []
    a = lines.append

    a('<?xml version="1.0" encoding="UTF-8"?>')
    a(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">'
    )
    a(
        '  <title id="title">JKSlider acceleration 0 to 300 mm/s '
        "with FIFO delay and repeat</title>"
    )
    a(
        '  <desc id="desc">Raised-cosine velocity and half-sine acceleration, '
        "plus PIO FIFO delay cycles and packed repeat field, for peak accel "
        "200 mm/s2 over 2.356 s. Assumes 320 steps/mm, PIO 125 MHz, "
        "STEP_PACK_MIN_HZ 8000, time budget 3 ms.</desc>"
    )
    a('  <rect width="100%" height="100%" fill="white"/>')
    a(
        '  <text x="430" y="26" text-anchor="middle" font-family="sans-serif" '
        'font-size="16" font-weight="bold">JKSlider acceleration: 0 &#8594; '
        "300 mm/s at 200 mm/s&#178;</text>"
    )

    a('  <g stroke="#e5e5e5" stroke-width="1">')
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        y = MB1 - TH1 * frac
        a(f'    <line x1="{XL}" y1="{y:.1f}" x2="{XR}" y2="{y:.1f}"/>')
    a("  </g>")
    a('  <g stroke="#222" stroke-width="1.5" fill="none">')
    a(f'    <line x1="{XL}" y1="{MT1}" x2="{XL}" y2="{MB1}"/>')
    a(f'    <line x1="{XR}" y1="{MT1}" x2="{XR}" y2="{MB1}"/>')
    a(f'    <line x1="{XL}" y1="{MB1}" x2="{XR}" y2="{MB1}"/>')
    a("  </g>")

    a('  <g stroke="#e5e5e5" stroke-width="1">')
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        y = MB2 - TH2 * frac
        a(f'    <line x1="{XL}" y1="{y:.1f}" x2="{XR}" y2="{y:.1f}"/>')
    a("  </g>")
    a('  <g stroke="#222" stroke-width="1.5" fill="none">')
    a(f'    <line x1="{XL}" y1="{MT2}" x2="{XL}" y2="{MB2}"/>')
    a(f'    <line x1="{XR}" y1="{MT2}" x2="{XR}" y2="{MB2}"/>')
    a(f'    <line x1="{XL}" y1="{MB2}" x2="{XR}" y2="{MB2}"/>')
    a("  </g>")

    a(
        f'  <line x1="{x_pack:.2f}" y1="{MT1}" x2="{x_pack:.2f}" y2="{MB1}" '
        'stroke="#999" stroke-width="1" stroke-dasharray="4 3"/>'
    )
    a(
        f'  <line x1="{x_pack:.2f}" y1="{MT2}" x2="{x_pack:.2f}" y2="{MB2}" '
        'stroke="#999" stroke-width="1" stroke-dasharray="4 3"/>'
    )
    a(
        f'  <text x="{x_pack:.2f}" y="{MT2 - 8}" text-anchor="middle" '
        'font-family="sans-serif" font-size="11" fill="#666">'
        "pack &#8805; 8 kHz</text>"
    )

    a(
        '  <polyline fill="none" stroke="#1677c8" stroke-width="2.5" '
        f'stroke-linejoin="round" points="{" ".join(pts_v)}"/>'
    )
    a(
        '  <polyline fill="none" stroke="#d66a00" stroke-width="2.5" '
        f'stroke-linejoin="round" points="{" ".join(pts_a)}"/>'
    )
    a(
        '  <polyline fill="none" stroke="#1a7a3c" stroke-width="2.5" '
        f'stroke-linejoin="round" points="{" ".join(pts_d)}"/>'
    )
    a(
        '  <polyline fill="none" stroke="#7a2ca0" stroke-width="2.5" '
        f'stroke-linejoin="round" points="{" ".join(pts_r)}"/>'
    )

    a('  <g font-family="sans-serif" font-size="11">')
    for vv, lab in ((0, "0"), (75, "75"), (150, "150"), (225, "225"), (300, "300")):
        a(
            f'    <text x="{XL - 8}" y="{y_v(vv) + 4:.1f}" text-anchor="end" '
            f'fill="#1677c8">{lab}</text>'
        )
    for aa, lab in ((0, "0"), (50, "50"), (100, "100"), (150, "150"), (200, "200")):
        a(f'    <text x="{XR + 8}" y="{y_a(aa) + 4:.1f}" fill="#d66a00">{lab}</text>')
    a(
        f'    <text x="{XL - 42}" y="{mid1:.0f}" fill="#1677c8" '
        f'transform="rotate(-90 {XL - 42} {mid1:.0f})" text-anchor="middle">'
        "Velocity (mm/s)</text>"
    )
    a(
        f'    <text x="{XR + 48}" y="{mid1:.0f}" fill="#d66a00" '
        f'transform="rotate(90 {XR + 48} {mid1:.0f})" text-anchor="middle">'
        "Acceleration (mm/s&#178;)</text>"
    )
    a("  </g>")

    a('  <g font-family="sans-serif" font-size="11">')
    for exp, lab in ((3, "1e3"), (4, "1e4"), (5, "1e5"), (6, "1e6"), (7, "1e7")):
        y = MB2 - TH2 * ((exp - LOG_LO) / (LOG_HI - LOG_LO))
        a(
            f'    <text x="{XL - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'fill="#1a7a3c">{lab}</text>'
        )
    for rr, lab in ((0, "0"), (16, "16"), (32, "32"), (48, "48"), (63, "63")):
        a(f'    <text x="{XR + 8}" y="{y_r(rr) + 4:.1f}" fill="#7a2ca0">{lab}</text>')
    a(
        f'    <text x="{XL - 42}" y="{mid2:.0f}" fill="#1a7a3c" '
        f'transform="rotate(-90 {XL - 42} {mid2:.0f})" text-anchor="middle">'
        "FIFO delay (cycles)</text>"
    )
    a(
        f'    <text x="{XR + 48}" y="{mid2:.0f}" fill="#7a2ca0" '
        f'transform="rotate(90 {XR + 48} {mid2:.0f})" text-anchor="middle">'
        "FIFO repeat (0..63)</text>"
    )
    a("  </g>")

    a('  <g font-family="sans-serif" font-size="11" fill="#222" text-anchor="middle">')
    for tlab in (0.0, 0.5, 1.0, 1.5, 2.0, T):
        x = x_of(tlab)
        txt = f"{tlab:.3f}" if abs(tlab - T) < 1e-9 else f"{tlab:.1f}"
        a(f'    <text x="{x:.1f}" y="{MB1 + 16}">{txt}</text>')
        a(f'    <text x="{x:.1f}" y="{MB2 + 16}">{txt}</text>')
    a(
        f'    <text x="{(XL + XR) / 2:.0f}" y="{MB2 + 36}">Time (s) &#8212; '
        f"ramp T = &#960;&#183;v/(2a) = {T:.3f} s</text>"
    )
    a("  </g>")

    a('  <g font-family="sans-serif" font-size="12">')
    items = (
        (120, "#1677c8", "velocity"),
        (230, "#d66a00", "acceleration"),
        (370, "#1a7a3c", "FIFO delay"),
        (500, "#7a2ca0", "FIFO repeat"),
    )
    for x0, col, lab in items:
        a(
            f'    <line x1="{x0}" y1="610" x2="{x0 + 28}" y2="610" '
            f'stroke="{col}" stroke-width="3"/>'
        )
        a(f'    <text x="{x0 + 34}" y="614">{lab}</text>')
    a("  </g>")

    a(
        '  <text x="430" y="634" text-anchor="middle" font-family="sans-serif" '
        'font-size="10" fill="#666">320 steps/mm &#183; delay = PIO_FREQ/step_hz '
        "&#8722; 10 &#183; pack when step_hz &#8805; 8000 "
        "(repeat = n&#8722;1, n &#8804; 64, 3 ms budget)</text>"
    )
    a("</svg>")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"samples={N + 1} pack_at_s={t_pack:.4f} v_pack={v_pack:.3f} mm/s")


if __name__ == "__main__":
    main()
