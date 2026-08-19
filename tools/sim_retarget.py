"""CLI shim for the planner scenario twin.

The model and unit-test matrix live under ``test/sim/``:

  python -m unittest test.sim.test_planner_scenarios -v

Or via the host-test runner:

  powershell -File scripts/run_host_tests.ps1
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from test.sim.planner_model import halfway_time, run_scenario  # noqa: E402


def main() -> int:
    show = "-v" in sys.argv
    results = []
    t3 = halfway_time(20.0, 10.0)

    results.append(run_scenario(
        "Retarget halfway - Reverse",
        20.0, 10.0,
        [(0.0, lambda s: s.move_to(100.0)),
         (t3, lambda s: s.move_to(0.0))],
        verbose=show))
    results.append(run_scenario(
        "Retarget halfway - Forward near (mt50)",
        20.0, 10.0,
        [(0.0, lambda s: s.move_to(100.0)),
         (t3, lambda s: s.move_to(50.0))],
        verbose=show))
    results.append(run_scenario(
        "Retarget halfway - Forward far (mt150)",
        20.0, 10.0,
        [(0.0, lambda s: s.move_to(100.0)),
         (t3, lambda s: s.move_to(150.0))],
        verbose=show))
    results.append(run_scenario(
        "Speed change halfway - faster (ss20->ss50)",
        20.0, 10.0,
        [(0.0, lambda s: s.move_to(100.0)),
         (t3, lambda s: s.set_speed(50.0))],
        verbose=show))
    results.append(run_scenario(
        "Speed change halfway - slower (ss50->ss20)",
        50.0, 10.0,
        [(0.0, lambda s: s.move_to(100.0)),
         (1.0, lambda s: s.set_speed(20.0))],
        verbose=show))

    print("\n========== SUMMARY ==========")
    fails = 0
    for r in results:
        print("  %-40s %s" % (r.name, "PASS" if r.ok else "FAIL"))
        if not r.ok:
            fails += 1
    if fails:
        print("%d scenario(s) failed" % fails)
        return 1
    print("All %d scenarios passed." % len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
