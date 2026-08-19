# Simulate JKSlider sine-ramp accel as PIO FIFO words, write CSV, plot SVG.
# Usage:
#   python docs/sim_sine_ramp_fifo.py
#   python docs/sim_sine_ramp_fifo.py --accel 100
#
# Models the velocity-task fill loop: raised-cosine ramp on wall time,
# delay/repeat packing with STEP_FIFO_TIME_BUDGET_MS and STEP_PACK_MIN_HZ.

from __future__ import annotations

import argparse
import csv
import math
from collections import deque
from pathlib import Path

# --- motion target -------------------------------------------------------------
V_CMD = 300.0  # mm/s
A_PEAK = 50.0  # mm/s^2 (overridden by --accel)

# --- firmware defaults (SliderConfig / Slider.py) ------------------------------
STEPS_PER_MM = 320.0
PIO_FREQ_HZ = 125_000_000
STEP_PULSE_CYCLES = 629
STEP_PACK_MIN_HZ = 200
STEP_FIFO_TIME_BUDGET_MS = 8.0
STEP_PACK_MAX = 64
MAX_STEP_RATE_HZ = 100_000
MIN_SPEED_MM_S = 0.006
# Leaving standstill: snap first ramp speed (0 = disable). Matches SliderConfig.
RAMP_START_HZ = 1000
STEP_DELAY_MASK = (1 << 26) - 1
# Slider._put_word waits while tx_fifo() >= 7 (Pico PIO TX depth 8).
HW_TX_FIFO_MAX = 7

# Planner fill iteration when room exists / when waiting on a full FIFO.
# MicroPython manages roughly one put per 100-250 us (see Technical Manual).
FILL_DT_S = 200e-6
WAIT_DT_S = 100e-6

DOCS = Path(__file__).resolve().parent
CSV_PATH = DOCS / "data" / "sine_ramp_fifo_words.csv"
SVG_PATH = DOCS / "img" / "sine_ramp_300mm_s.svg"

EPS_V = 0.05
RESTART_EPS = 0.5


def set_output_paths(accel_mm_s2: float) -> None:
    """Name CSV/SVG from cruise speed and peak accel (e.g. v300_a50)."""
    global A_PEAK, CSV_PATH, SVG_PATH
    A_PEAK = float(accel_mm_s2)
    tag = f"v{int(round(V_CMD))}_a{int(round(A_PEAK))}"
    CSV_PATH = DOCS / "data" / f"sine_ramp_fifo_{tag}.csv"
    SVG_PATH = DOCS / "img" / f"sine_ramp_fifo_{tag}.svg"


class Ramp:
    """Matches Slider._ramp_velocity (raised cosine, phi: 0 -> pi)."""

    def __init__(self):
        self.act = 0.0
        self.active = False
        self.v0 = 0.0
        self.v1 = 0.0
        self.phi = 0.0
        self.a = 0.0

    def step(self, cmd: float, a_peak: float, dt: float) -> float:
        """Advance act toward cmd; return instantaneous acceleration (mm/s^2)."""
        act = self.act
        if abs(cmd - act) <= EPS_V and not self.active:
            self.act = cmd
            return 0.0

        if self.active:
            dv_seg = self.v1 - self.v0
            toward = cmd - act
            flip = dv_seg * toward < 0.0
            big_jump = abs(cmd - self.v1) > RESTART_EPS
            a_changed = abs(a_peak - self.a) > max(1.0, 0.05 * a_peak)
            need_restart = flip or big_jump or a_changed
        else:
            need_restart = True

        if need_restart:
            # Mirror Slider._ramp_velocity RAMP_START_HZ snap from standstill.
            if RAMP_START_HZ > 0:
                start = max(MIN_SPEED_MM_S, float(RAMP_START_HZ) / STEPS_PER_MM)
                if abs(act) < start and abs(cmd) >= start:
                    act = math.copysign(start, cmd)
                    self.act = act
            self.v0 = act
            self.v1 = cmd
            self.phi = 0.0
            self.a = a_peak
            if abs(self.v1 - self.v0) <= EPS_V:
                self.act = cmd
                self.active = False
                return 0.0
            self.active = True

        dv = self.v1 - self.v0
        omega = 2.0 * self.a / abs(dv)
        self.phi += omega * dt
        if self.phi >= math.pi:
            self.act = self.v1
            self.active = False
            self.phi = math.pi
            return 0.0

        blend = 0.5 * (1.0 - math.cos(self.phi))
        self.act = self.v0 + dv * blend
        return self.instant_accel()

    def instant_accel(self) -> float:
        if not self.active:
            return 0.0
        dv = self.v1 - self.v0
        if abs(dv) <= EPS_V:
            return 0.0
        return self.a * math.sin(self.phi) * (1.0 if dv >= 0.0 else -1.0)


def clamp_delay(delay_cycles: int) -> int:
    d = int(delay_cycles)
    if d < 1:
        return 1
    if d > STEP_DELAY_MASK:
        return STEP_DELAY_MASK
    return d


def pack_n(step_hz: float, pending_steps: int) -> int:
    if step_hz < float(STEP_PACK_MIN_HZ):
        return 1
    budget_ms = max(0.5, float(STEP_FIFO_TIME_BUDGET_MS))
    budget_steps = max(1, int(step_hz * budget_ms / 1000.0))
    room = budget_steps - pending_steps
    if room < 1:
        return 0
    return min(STEP_PACK_MAX, room)


def word_duration_s(delay: int, n_pulses: int) -> float:
    period = (delay + STEP_PULSE_CYCLES) / PIO_FREQ_HZ
    return n_pulses * period


def ramp_start_mm_s() -> float:
    if RAMP_START_HZ <= 0:
        return MIN_SPEED_MM_S
    return max(MIN_SPEED_MM_S, float(RAMP_START_HZ) / STEPS_PER_MM)


def ramp_distance_mm() -> float:
    """Sine-ramp distance from RAMP_START (or 0) to V_CMD: d = pi*(v1^2-v0^2)/(4a)."""
    v1 = V_CMD
    v0 = ramp_start_mm_s() if v1 >= ramp_start_mm_s() else 0.0
    return math.pi * (v1 * v1 - v0 * v0) / (4.0 * A_PEAK)


def ramp_distance_steps() -> int:
    """Steps in one sine ramp start -> V_CMD."""
    return int(round(ramp_distance_mm() * STEPS_PER_MM))


def ideal_ramp_time_s() -> float:
    """Raised-cosine duration from start floor to V_CMD."""
    v0 = ramp_start_mm_s() if V_CMD >= ramp_start_mm_s() else 0.0
    return math.pi * abs(V_CMD - v0) / (2.0 * A_PEAK)

def simulate_words():
    """Return list of dict rows: one per FIFO word for a full ramp.

    Models Slider._put_word TX depth (block while tx_fifo >= 7) and SM pull:
    a TX slot frees when the in-flight word finishes and the SM pulls the next.
    Runs until the ramp's step count has actually been queued, so the word
    stream carries the real distance (planner may reach cruise much earlier).
    """
    ramp = Ramp()
    t = 0.0
    rows = []
    word_i = 0
    target_steps = ramp_distance_steps()
    issued_steps = 0
    t_limit = 20.0 * math.pi * V_CMD / (2.0 * A_PEAK) + 60.0

    # in_flight: [pulses_left, delay, period_s] or None
    in_flight = None
    tx: deque[list] = deque()  # words waiting in PIO TX FIFO
    shaft_t = 0.0

    def tx_steps() -> int:
        return sum(int(e[0]) for e in tx)

    def pipeline_steps() -> int:
        n = tx_steps()
        if in_flight is not None:
            n += int(in_flight[0])
        return n

    def drain_to(wall_t: float) -> None:
        """Play in-flight pulses up to wall_t; pull from TX when a word ends."""
        nonlocal in_flight, shaft_t
        while shaft_t < wall_t:
            if in_flight is None:
                if not tx:
                    shaft_t = wall_t
                    return
                # SM pulls next TX word at the start of play.
                in_flight = tx.popleft()
            pulses_left, _delay, period = in_flight
            can_play = wall_t - shaft_t
            if can_play <= 0:
                return
            pulses_fit = int(can_play / period)
            if pulses_fit <= 0:
                if shaft_t + period <= wall_t:
                    pulses_fit = 1
                else:
                    return
            take = min(pulses_left, pulses_fit)
            in_flight[0] -= take
            shaft_t += take * period
            if in_flight[0] <= 0:
                in_flight = None

    def inflight_remaining_s() -> float:
        if in_flight is None:
            return 0.0
        return in_flight[0] * in_flight[2]

    while t < t_limit:
        drain_to(t)

        if issued_steps >= target_steps:
            # Whole ramp queued: let the pipeline play out, then stop.
            rem = inflight_remaining_s() + sum(e[0] * e[2] for e in tx)
            if rem > 0:
                t += rem
                drain_to(t)
            break

        step_hz = min(max(abs(ramp.act) * STEPS_PER_MM, 0.0), MAX_STEP_RATE_HZ)
        if abs(ramp.act) < MIN_SPEED_MM_S:
            dt = FILL_DT_S
            ramp.step(V_CMD, A_PEAK, dt)
            t += dt
            continue

        # _put_word blocks while tx_fifo_count() >= 7.
        if len(tx) >= HW_TX_FIFO_MAX:
            dt = max(inflight_remaining_s(), WAIT_DT_S)
            t += dt
            ramp.step(V_CMD, A_PEAK, dt)
            continue

        n = pack_n(step_hz, tx_steps())
        remaining = target_steps - issued_steps
        if 0 < remaining < n:
            n = remaining
        if n < 1:
            # 3 ms step-time budget full — wait until TX pipeline shrinks.
            budget_steps = max(
                1, int(step_hz * max(0.5, STEP_FIFO_TIME_BUDGET_MS) / 1000.0)
            )
            need_free = tx_steps() - budget_steps + 1
            if need_free < 1:
                need_free = 1
            # Freeing TX steps requires finishing in-flight (pull) then TX words.
            wait = inflight_remaining_s()
            left = need_free
            for pulses_left, _d, per in tx:
                if left <= 0:
                    break
                take = min(pulses_left, left)
                wait += take * per
                left -= take
            dt = max(wait, WAIT_DT_S)
            t += dt
            ramp.step(V_CMD, A_PEAK, dt)
            continue

        delay = clamp_delay(int(PIO_FREQ_HZ / step_hz) - STEP_PULSE_CYCLES)
        period = (delay + STEP_PULSE_CYCLES) / PIO_FREQ_HZ
        repeat = n - 1
        dur = word_duration_s(delay, n)

        rows.append(
            {
                "word": word_i,
                "time_s": f"{t:.9f}",
                "delay_cycles": delay,
                "repeat": repeat,
                "n_pulses": n,
                "speed_mm_s": f"{ramp.act:.6f}",
                "accel_mm_s2": f"{ramp.instant_accel():.6f}",
                "step_hz": f"{step_hz:.3f}",
                "word_duration_s": f"{dur:.9f}",
                "pending_steps_before": pipeline_steps(),
            }
        )
        word_i += 1
        issued_steps += n

        word = [n, delay, period]
        if in_flight is None and not tx:
            # SM idle: pull immediately (word never sits in TX).
            in_flight = word
            shaft_t = t
        else:
            tx.append(word)

        ramp.step(V_CMD, A_PEAK, FILL_DT_S)
        t += FILL_DT_S

    return rows


def annotate_shaft_times(rows):
    """Add shaft_time_s = cumulative PIO play time (integral of delay words).

    time_s is planner issue time (when the word was queued). shaft_time_s is when
    that word starts on the motor: sum of prior n*(delay+STEP_PULSE_CYCLES)/PIO.
    """
    shaft = 0.0
    for r in rows:
        r["shaft_time_s"] = f"{shaft:.9f}"
        shaft += float(r["word_duration_s"])
    return shaft


def write_csv(rows) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "word",
        "time_s",
        "shaft_time_s",
        "delay_cycles",
        "repeat",
        "n_pulses",
        "speed_mm_s",
        "accel_mm_s2",
        "step_hz",
        "word_duration_s",
        "pending_steps_before",
    ]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def read_csv():
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def plot_svg(rows) -> None:
    """Two-panel SVG from FIFO-word CSV (staircase delay/repeat)."""
    if not rows:
        raise SystemExit("no CSV rows to plot")

    issue_ts = [float(r["time_s"]) for r in rows]
    vs = [float(r["speed_mm_s"]) for r in rows]
    acs = [float(r["accel_mm_s2"]) for r in rows]
    delays = [int(r["delay_cycles"]) for r in rows]
    repeats = [int(r["repeat"]) for r in rows]
    durs = [float(r["word_duration_s"]) for r in rows]

    # Shaft total kept for the footer comparison only.
    shaft_sum = sum(durs)
    T_ideal = math.pi * V_CMD / (2.0 * A_PEAK)

    t_min = 0.0
    t_max = max(issue_ts[-1] + durs[-1], T_ideal)

    V = V_CMD
    A = A_PEAK
    W, H = 900, 640
    ML, MR = 88, 78
    MT1, MB1 = 48, 300
    MT2, MB2 = 360, 560
    XL, XR = ML, W - MR
    TW = XR - XL
    TH1 = MB1 - MT1
    TH2 = MB2 - MT2
    LOG_LO, LOG_HI = 3.0, 7.0

    def x_of(t):
        return XL + TW * ((t - t_min) / (t_max - t_min if t_max > t_min else 1.0))

    def y_v(v):
        return MB1 - TH1 * (max(0.0, min(v, V)) / V)

    def y_a(a):
        return MB1 - TH1 * (max(0.0, min(a, A)) / A)

    def y_d(d):
        ld = math.log10(max(d, 10 ** LOG_LO))
        ld = min(max(ld, LOG_LO), LOG_HI)
        return MB2 - TH2 * ((ld - LOG_LO) / (LOG_HI - LOG_LO))

    def y_r(r):
        return MB2 - TH2 * (r / 63.0)

    def stair(values, yfun):
        pts = []
        for i, val in enumerate(values):
            t_a = issue_ts[i]
            t_b = t_a + durs[i]
            y = yfun(val)
            pts.append(f"{x_of(t_a):.2f},{y:.2f}")
            pts.append(f"{x_of(t_b):.2f},{y:.2f}")
        return pts

    pts_v = stair(vs, y_v)
    pts_a = stair(acs, y_a)
    pts_d = stair(delays, y_d)
    # One unconnected marker per issued FIFO word. A tiny horizontal segment
    # with round caps renders as a compact dot without connecting samples.
    repeat_marks = " ".join(
        f"M{x_of(issue_ts[i]):.2f},{y_r(val):.2f}h0.01"
        for i, val in enumerate(repeats)
    )

    x_pack = None
    for i, r in enumerate(rows):
        if int(r["repeat"]) > 0:
            x_pack = x_of(issue_ts[i])
            break

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
        '  <title id="title">JKSlider FIFO-word sine ramp simulation '
        "0 to 300 mm/s</title>"
    )
    a(
        '  <desc id="desc">Per-FIFO-word simulation of raised-cosine velocity '
        f"ramp with delay and repeat fields. Peak accel {A_PEAK:g} mm/s2, "
        "320 steps/mm. X axis is planner/real issue time (time_s).</desc>"
    )
    a('  <rect width="100%" height="100%" fill="white"/>')
    a(
        '  <text x="450" y="26" text-anchor="middle" font-family="sans-serif" '
        'font-size="16" font-weight="bold">FIFO-word sim: 0 &#8594; 300 mm/s '
        f"at {A_PEAK:g} mm/s&#178; ({len(rows)} words)</text>"
    )

    a('  <g stroke="#eee" stroke-width="1">')
    v_tick = 0
    while v_tick <= V + 1e-9:
        y = y_v(v_tick)
        a(f'    <line x1="{XL}" y1="{y:.1f}" x2="{XR}" y2="{y:.1f}"/>')
        v_tick += 50
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

    if x_pack is not None:
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
        '  <polyline fill="none" stroke="#1677c8" stroke-width="2" '
        f'stroke-linejoin="round" points="{" ".join(pts_v)}"/>'
    )
    a(
        '  <polyline fill="none" stroke="#d66a00" stroke-width="2" '
        f'stroke-linejoin="round" points="{" ".join(pts_a)}"/>'
    )
    a(
        '  <polyline fill="none" stroke="#1a7a3c" stroke-width="2" '
        f'stroke-linejoin="round" points="{" ".join(pts_d)}"/>'
    )
    a(
        '  <path fill="none" stroke="#7a2ca0" stroke-width="2.5" '
        f'stroke-linecap="round" d="{repeat_marks}"/>'
    )

    a('  <g font-family="sans-serif" font-size="9">')
    v_tick = 0
    while v_tick <= V + 1e-9:
        a(
            f'    <text x="{XL - 6}" y="{y_v(v_tick) + 3:.1f}" text-anchor="end" '
            f'fill="#1677c8">{int(v_tick)}</text>'
        )
        v_tick += 50
    # Ten equal acceleration intervals (11 labels including 0 and peak).
    for tick_i in range(11):
        a_tick = A * tick_i / 10.0
        label = f"{a_tick:g}"
        a(
            f'    <text x="{XR + 6}" y="{y_a(a_tick) + 3:.1f}" '
            f'fill="#d66a00">{label}</text>'
        )
    a(
        f'    <text x="{XL - 52}" y="{mid1:.0f}" fill="#1677c8" font-size="11" '
        f'transform="rotate(-90 {XL - 52} {mid1:.0f})" text-anchor="middle">'
        "Velocity (mm/s)</text>"
    )
    a(
        f'    <text x="{XR + 48}" y="{mid1:.0f}" fill="#d66a00" font-size="11" '
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
        f'    <text x="{XL - 52}" y="{mid2:.0f}" fill="#1a7a3c" '
        f'transform="rotate(-90 {XL - 52} {mid2:.0f})" text-anchor="middle">'
        "FIFO delay (cycles)</text>"
    )
    a(
        f'    <text x="{XR + 48}" y="{mid2:.0f}" fill="#7a2ca0" '
        f'transform="rotate(90 {XR + 48} {mid2:.0f})" text-anchor="middle">'
        "FIFO repeat (0..63)</text>"
    )
    a("  </g>")

    a('  <g font-family="sans-serif" font-size="11" fill="#222" text-anchor="middle">')
    tlab = 0.0
    while tlab < t_max - 1e-6:
        x = x_of(tlab)
        a(f'    <text x="{x:.1f}" y="{MB1 + 16}">{tlab:.0f}</text>')
        a(f'    <text x="{x:.1f}" y="{MB2 + 16}">{tlab:.0f}</text>')
        tlab += 1.0
    x_end = x_of(t_max)
    a(f'    <text x="{x_end:.1f}" y="{MB1 + 16}">{t_max:.2f}</text>')
    a(f'    <text x="{x_end:.1f}" y="{MB2 + 16}">{t_max:.2f}</text>')
    a(
        f'    <text x="{(XL + XR) / 2:.0f}" y="{MB2 + 36}">Real / planner time (s) '
        f"&#8212; time_s when each word is issued "
        f"(shaft &#8721;delays={shaft_sum:.3f}s, ideal T={T_ideal:.3f}s)</text>"
    )
    a("  </g>")

    a('  <g font-family="sans-serif" font-size="12">')
    line_items = (
        (140, "#1677c8", "velocity"),
        (250, "#d66a00", "acceleration"),
        (390, "#1a7a3c", "FIFO delay"),
    )
    for x0, col, lab in line_items:
        a(
            f'    <line x1="{x0}" y1="610" x2="{x0 + 28}" y2="610" '
            f'stroke="{col}" stroke-width="3"/>'
        )
        a(f'    <text x="{x0 + 34}" y="614">{lab}</text>')
    a('    <circle cx="534" cy="610" r="2" fill="#7a2ca0"/>')
    a('    <text x="554" y="614">FIFO repeat</text>')
    a("  </g>")

    a(
        '  <text x="450" y="634" text-anchor="middle" font-family="sans-serif" '
        'font-size="10" fill="#666">X = real planner time_s (word issue) '
        "&#183; speed ticks 50 mm/s &#183; accel scale 10 intervals &#183; "
        "source: docs/data/sine_ramp_fifo_words.csv</text>"
    )
    a("</svg>")

    SVG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    global FILL_DT_S
    parser = argparse.ArgumentParser(description="Simulate FIFO-word sine ramp")
    parser.add_argument(
        "--accel",
        type=float,
        default=A_PEAK,
        help=f"peak acceleration mm/s^2 (default {A_PEAK:g})",
    )
    parser.add_argument(
        "--fill-dt-us",
        type=float,
        default=FILL_DT_S * 1e6,
        help="planner loop period per queued word in us (default 200)",
    )
    args = parser.parse_args()
    FILL_DT_S = args.fill_dt_us * 1e-6
    set_output_paths(args.accel)

    rows = simulate_words()
    total_shaft = annotate_shaft_times(rows)
    write_csv(rows)
    plot_svg(rows)
    t_issue_last = float(rows[-1]["time_s"]) if rows else 0.0
    print(f"words={len(rows)}")
    print(f"accel={A_PEAK:g} mm/s^2")
    print(f"csv={CSV_PATH}")
    print(f"svg={SVG_PATH}")
    steps = sum(int(r["n_pulses"]) for r in rows)
    dist_mm = steps / STEPS_PER_MM
    ideal_mm = ramp_distance_mm()
    ideal_from_zero = math.pi * V_CMD * V_CMD / (4.0 * A_PEAK)
    T_ideal = ideal_ramp_time_s()
    print(f"shaft_time_sum (integrated delays) = {total_shaft:.6f} s")
    print(f"last planner issue time_s          = {t_issue_last:.6f} s")
    print(f"ideal raised-cosine T (from start) = {T_ideal:.6f} s")
    print(
        f"steps issued = {steps} ({dist_mm:.1f} mm) vs ideal from start "
        f"{ideal_mm:.1f} mm  ratio={dist_mm / ideal_mm:.4f}"
    )
    print(
        f"ideal from true zero would be {ideal_from_zero:.1f} mm "
        f"(RAMP_START_HZ={RAMP_START_HZ})"
    )
    if rows:
        print(
            f"t0_issue={rows[0]['time_s']}s  "
            f"v_last={rows[-1]['speed_mm_s']}  "
            f"delay_last={rows[-1]['delay_cycles']}  "
            f"repeat_last={rows[-1]['repeat']}"
        )
        for r in rows:
            if int(r["repeat"]) > 0:
                print(
                    f"first packed word={r['word']} "
                    f"issue_t={r['time_s']} shaft_t={r['shaft_time_s']} "
                    f"v={r['speed_mm_s']} delay={r['delay_cycles']} "
                    f"repeat={r['repeat']}"
                )
                break


if __name__ == "__main__":
    main()
