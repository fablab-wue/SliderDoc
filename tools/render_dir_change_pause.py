# Generate docs/img/dir_change_pause.png — velocity profile with DIR_CHANGE_PAUSE_S.
# Usage: python docs/render_dir_change_pause.py

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

A = 200.0
V = 50.0
PAUSE = 0.1
DT = 0.01
PI = math.pi
EPS = 0.05
RESTART_EPS = 0.5
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "dir_change_pause.png"


def ramp_step(act, cmd, st):
    if abs(cmd - act) <= EPS and not st["active"]:
        return cmd
    need = not st["active"]
    if st["active"]:
        dv_seg = st["v1"] - st["v0"]
        toward = cmd - act
        need = (dv_seg * toward < 0) or (abs(cmd - st["v1"]) > RESTART_EPS)
    if need:
        st["v0"], st["v1"], st["phi"] = act, cmd, 0.0
        if abs(st["v1"] - st["v0"]) <= EPS:
            st["active"] = False
            return cmd
        st["active"] = True
    if not st["active"]:
        return act
    dv = st["v1"] - st["v0"]
    st["phi"] += (2 * A / abs(dv)) * DT
    if st["phi"] >= PI:
        st["active"] = False
        st["phi"] = PI
        return st["v1"]
    blend = 0.5 * (1.0 - math.cos(st["phi"]))
    return st["v0"] + dv * blend


def main():
    ts, cmds, acts = [], [], []
    act = 0.0
    pending = False
    pause_rem = 0.0
    st = dict(active=False, v0=0.0, v1=0.0, phi=0.0)
    t = 0.0
    while t <= 3.05:
        if t < 1.0:
            cmd_req = V
        elif t < 2.6:
            cmd_req = -V
        else:
            cmd_req = 0.0
        cmd = cmd_req
        if pause_rem > 0:
            pause_rem -= DT
            if pause_rem < 0:
                pause_rem = 0.0
            act = 0.0
            st = dict(active=False, v0=0.0, v1=0.0, phi=0.0)
            cmd = 0.0
        elif abs(cmd_req) >= EPS and abs(act) >= EPS and cmd_req * act < 0:
            pending = True
            cmd = 0.0
            act = ramp_step(act, cmd, st)
        elif pending:
            if abs(act) < EPS:
                if abs(cmd_req) >= EPS:
                    pending = False
                    pause_rem = PAUSE
                    act = 0.0
                    st = dict(active=False, v0=0.0, v1=0.0, phi=0.0)
                    cmd = 0.0
                else:
                    pending = False
                    act = ramp_step(act, cmd, st)
            else:
                if abs(cmd_req) < EPS:
                    pending = False
                cmd = 0.0
                act = ramp_step(act, cmd, st)
        else:
            act = ramp_step(act, cmd, st)
        ts.append(t)
        cmds.append(cmd_req)
        acts.append(act)
        t += DT

    t_ramp = PI * V / (2 * A)
    pause0 = 1.0 + t_ramp
    pause1 = pause0 + PAUSE

    fig, ax = plt.subplots(figsize=(9.5, 4.2), dpi=140)
    ax.plot(ts, cmds, color="#888888", linewidth=1.2, linestyle="--", label="Commanded")
    ax.plot(ts, acts, color="#1a6fb5", linewidth=2.0, label="Actual")
    ax.axhline(0, color="#bbbbbb", linewidth=0.8)
    ax.axvspan(
        pause0,
        pause1,
        color="#e8a317",
        alpha=0.35,
        label="DIR_CHANGE_PAUSE_S = {:g} s".format(PAUSE),
    )
    ax.set_xlabel("t (s)")
    ax.set_ylabel("v (mm/s)")
    ax.set_title("SliderCtrl velocity profile (sine ramp + direction-change pause)")
    ax.set_xlim(0, 3.05)
    ax.set_ylim(-65, 65)
    ax.legend(loc="upper right", frameon=False)
    ax.grid(True, alpha=0.3)
    ax.annotate(
        "DIR_CHANGE_PAUSE_S",
        xy=((pause0 + pause1) / 2, 8),
        xytext=((pause0 + pause1) / 2, 38),
        ha="center",
        fontsize=9,
        color="#8a5a00",
        arrowprops=dict(arrowstyle="->", color="#8a5a00", lw=1),
    )
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
