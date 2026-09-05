#!/usr/bin/env python3
"""Render SliderMC Command Cheat Sheet (DIN A4 HTML + Markdown + optional PDF).

Command rows mirror firmware k_help_rows in src/protocol/commands.cpp.
Canonical command prose: contract/protocol.md — keep GROUPS descriptions in sync.
Regenerate after editing protocol tables: python tools/render_command_cheatsheet.py

Each row: (short, long, call, reply, desc)
  call/reply appear in the Markdown reference; HTML print sheet uses short/long/desc.
"""

from __future__ import annotations

import html
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_OUT = ROOT / "contract" / "command-cheatsheet.html"
MD_OUT = ROOT / "contract" / "command-cheatsheet.md"
MD2_OUT = ROOT / "contract" / "command-cheatsheet2.md"
PDF_OUT = ROOT / "contract" / "command-cheatsheet.pdf"
MD2_CSS = r"""<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "SliderMC Command Cheat Sheet";
  --doc-path: ".\\SliderDoc\\contract\\command-cheatsheet.md";
}
</style>

"""
FW_VERSION = "1.0"

SILENT = "—"

# (group_title, [(short, long, call, reply, desc), ...])
GROUPS = [
    (
        "S — Set (session)",
        [
            (
                "SS",
                "SetSpeed",
                "SS [<v>]",
                SILENT,
                "Cruise speed mm/s (≤ max_speed); bare reloads init_speed; live on next fill (incl. MJ). Dual MT: axis1=session, axis2×ratio.",
            ),
            (
                "SA",
                "SetAccel",
                "SA [<a>]",
                SILENT,
                "Peak accel mm/s² (≤ max_accel); bare reloads init_accel; live on next fill (incl. MJ). Dual MT: same ratio scaling as SS.",
            ),
            (
                "SE",
                "SetEnable",
                "SE [0|1]",
                SILENT,
                "Driver enable 0|1; bare toggles; required before motion; off = hard stop.",
            ),
            (
                "ST",
                "SetTerminal",
                "ST [0|1]",
                SILENT,
                "Terminal Mode 0|1; bare toggles; local echo + UART sniff to USB (expert).",
            ),
            (
                "SV",
                "SetVerbose",
                "SV [0|1]",
                SILENT,
                "Verbose #… push 0|1; bare toggles; ~3 Hz (rate via verbose_rate_hz).",
            ),
            (
                "SD",
                "SetDebug",
                "SD [0..5]",
                SILENT,
                "USB-only debug level 0..5; bare restores default; never on UIC UART.",
            ),
            (
                "SL",
                "SetLeft",
                "SL [<pos> [<pos2>]]",
                SILENT,
                "Session soft min (working window); bare→slider_min; none clears (→envelope if set); skip _; !E:limit past envelope.",
            ),
            (
                "SR",
                "SetRight",
                "SR [<pos> [<pos2>]]",
                SILENT,
                "Session soft max; bare→slider_max; none clears; skip _; !E:limit if left>right.",
            ),
            (
                "SP",
                "SetPosition",
                "SP [<pos> [<pos2>]]",
                SILENT,
                "Set reported pose (no motion); idle only; bare/0 = here is zero; skip _.",
            ),
        ],
    ),
    (
        "G — Get (session)",
        [
            ("GS", "GetSpeed", "GS", "GS:<mm/s>", "Current session cruise speed."),
            ("GA", "GetAccel", "GA", "GA:<mm/s2>", "Current session acceleration."),
            ("GE", "GetEnable", "GE", "GE:0|1", "Driver enable state."),
            ("GT", "GetTerminal", "GT", "GT:0|1", "Terminal Mode state."),
            ("GV", "GetVerbose", "GV", "GV:0|1", "Verbose push state."),
            ("GD", "GetDebug", "GD", "GD:<0..5>", "USB debug level."),
            (
                "GL",
                "GetLeft",
                "GL",
                "GL:<pos> [<pos2>]",
                "Session soft min; effective (session else envelope); - if both None; dual when axis2 on.",
            ),
            (
                "GR",
                "GetRight",
                "GR",
                "GR:<pos> [<pos2>]",
                "Session soft max; same effective / - rules as GL.",
            ),
        ],
    ),
    (
        "I — Is / status",
        [
            ("IM", "IsMoving", "IM", "IM:0|1", "Moving or settling on any active axis."),
            ("IH", "IsHoming", "IH", "IH:0|1", "Homing cycle active."),
            ("IL", "IsLimit", "IL", "IL:0|1", "At soft-limit position (axis1)."),
            ("IE", "IsError", "IE", "IE:0|1", "PIN_DRV_ERROR / EMO latched."),
            (
                "IP",
                "IsPosition",
                "IP",
                "IP:<pos> [<pos2>]",
                "Axis-1 position; second field when axis2_use=1.",
            ),
            ("IA", "IsAxis", "IA", "IA:1|2", "Active axis count (config_axis2_enabled)."),
            (
                "IT",
                "IsTarget",
                "IT",
                "IT:<pos>|-",
                "Axis-1 seek target, or - if none / soft-stop.",
            ),
            (
                "IR",
                "IsReady",
                "IR",
                "IR:0|1",
                "1 only if idle, not homing, enabled, and not waiting.",
            ),
            ("IW", "IsWaiting", "IW", "IW:0|1", "1 if any W / WM / WH / WP / WC / WnC wait is active."),
            (
                "ID",
                "IsDiag",
                "ID",
                "ID:underrun=N peak_hz=… overshoot=… fifo_min=…",
                "Motion diag counters (FIFO underrun, peak STEP Hz, …).",
            ),
            (
                "IZ",
                "IsReset",
                "IZ",
                "IZ:<reason>",
                "Last chip reset: power|wdt|run|soft|debug|brownout|…",
            ),
            (
                "IX",
                "Pinout",
                "IX",
                "(multi-line table)",
                "ASCII GP / name / desc (≤80 cols). Axis-2 rows only if axis2 on.",
            ),
        ],
    ),
    (
        "M — Movement",
        [
            (
                "MT",
                "MoveTo",
                "MT <pos> [<pos2>]",
                SILENT,
                "Absolute user units; optional 2nd axis; skip _; needs SE; live-retarget. Dual: time-sync ratio.",
            ),
            (
                "M",
                "Move",
                "M <delta> [<delta2>]",
                SILENT,
                "Relative move (alias MoveBy); same dual/skip rules as MT.",
            ),
            (
                "ML",
                "MoveLeft",
                "ML [0|1|2]",
                SILENT,
                "Jog −; mask 0=both, 1=axis1, 2=axis2 when axis2 on; soft-stop MS/!.",
            ),
            (
                "MR",
                "MoveRight",
                "MR [0|1|2]",
                SILENT,
                "Jog +; mask same as ML; soft-stop MS/!.",
            ),
            (
                "MJ",
                "MoveJoy",
                "MJ <pct> [<pct2>]",
                SILENT,
                "Joy speed % of SS, signed (− left / + right); 2-axis optional pct2 (omit=0); 0=soft-stop; SS/SA live; clamp max_speed[_2].",
            ),
            (
                "MH",
                "MoveHome",
                "MH [1|2]",
                SILENT,
                "Homing; axis 1 (default) or 2; no-op if home_mode=0; cancel MS/H.",
            ),
            (
                "MS",
                "MoveStop",
                "MS",
                SILENT,
                "Soft decelerate both axes; keeps enable; ends joy-mode; does not cancel waits. Dual: scaled accel kept.",
            ),
        ],
    ),
    (
        "P — Path",
        [
            (
                "PC",
                "PathClear",
                "PC",
                SILENT,
                "Clear path buffer (count→0); !E:busy while PG active.",
            ),
            (
                "PD",
                "PathData",
                "PD <um> [<um2>]",
                SILENT,
                "Append signed µm sample(s); optional axis2; skip _ →0; OK while PG (live stream).",
            ),
            (
                "PG",
                "PathGo",
                "PG",
                SILENT,
                "Play buffer from sample 0; needs SE; !E:empty|busy|disabled. MS/H ends path.",
            ),
            (
                "PN",
                "PathNumber",
                "PN",
                "PN:<count>",
                "Samples in buffer; allowed during PG.",
            ),
            (
                "PS",
                "PathSlice",
                "PS [<us>]",
                SILENT,
                "Slice length µs (≥1000); bare→init_path_slice_us; !E:busy while PG.",
            ),
        ],
    ),
    (
        "X — Extender",
        [
            (
                "X0–3",
                "Ext0–3",
                "Xn [0|1]",
                SILENT,
                "Ext out n logical 0|1; bare toggles; glued X00≡X0 0; OK during EMO. X4+ rejected.",
            ),
            (
                "Z",
                "Buzzer",
                "Z",
                SILENT,
                "Pulse PIN_BUZZER ~0.1 s; not a wait. No-op if BUZZER_use=0. OK during EMO/path.",
            ),
        ],
    ),
    (
        "C — Config",
        [
            (
                "CS",
                "ConfigSet",
                "CS <key> <value>",
                SILENT,
                "Persist key to mc.ini; silent ok. axis2_use / WDT_use need RB to take HW effect.",
            ),
            (
                "CR",
                "ConfigReset",
                "CR",
                SILENT,
                "Reset all config to compiled defaults and save mc.ini.",
            ),
            (
                "CG",
                "ConfigGet",
                "CG [<key>]",
                "CG:<key>=<value>",
                "One key, or bare dumps all keys (multi-line).",
            ),
            (
                "RB",
                "Reboot",
                "RB",
                SILENT,
                "Soft MCU reset (no power cycle); EN off first. After CS axis2_use.",
            ),
        ],
    ),
    (
        "W — Wait",
        [
            (
                "W",
                "Wait",
                "W [<sec>]",
                SILENT,
                "Delay then continue ; chain; bare→1 s; never !E:timeout.",
            ),
            (
                "WM",
                "WaitMoving",
                "WM [<timeout_s>]",
                SILENT,
                "Pause chain until move ends; optional timeout → !E:timeout, cancel rest of chain.",
            ),
            (
                "WH",
                "WaitHoming",
                "WH [<timeout_s>]",
                SILENT,
                "Pause until homing ends; timeout same as WM.",
            ),
            (
                "WP",
                "WaitPos",
                "WP <pos> [<timeout_s>]",
                SILENT,
                "Wait until axis-1 pos reached/overstepped; idle→immediate; 2nd arg=timeout.",
            ),
            (
                "WC",
                "WaitCruise",
                "WC [<timeout_s>]",
                SILENT,
                "Wait until cruise (status M) or idle; optional timeout → !E:timeout.",
            ),
            (
                "WnC",
                "WaitNotCruise",
                "WnC [<timeout_s>]",
                SILENT,
                "Wait until not cruise M; idle/A/B→immediate; timeout same as WM.",
            ),
        ],
    ),
    (
        "V — Version",
        [
            ("VA", "VersionAbout", "VA", "VA:…", "About string (name, version, author)."),
            ("VF", "VersionFW", "VF", "VF:<version>", "Firmware version."),
            ("VP", "VersionProtocol", "VP", "VP:<n>", "Protocol version."),
        ],
    ),
    (
        "Special",
        [
            (
                "H/HT",
                "Halt",
                "H | HT",
                SILENT,
                "Immediate STEP abort; enable off; cancel waits and remaining ; chain.",
            ),
            (
                "P",
                "Pins",
                "VG | P",
                "VG:PIN_*=n (multi-line)",
                "Machine-readable pin map (alias VersionGPIO). Axis-2 pins if axis2 on.",
            ),
            (
                "$/HL",
                "Help",
                "$ | HL | Help",
                "(multi-line table)",
                "ASCII table of all commands (≤80 columns).",
            ),
        ],
    ),
]


CSS = """
@page { size: A4; margin: 7mm; }
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  font-size: 7.2pt;
  color: #111;
  background: #fff;
}
.sheet {
  width: 196mm;
  margin: 0 auto;
  padding: 0;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-bottom: 1.2pt solid #222;
  padding-bottom: 1.2mm;
  margin-bottom: 2mm;
}
header h1 {
  margin: 0;
  font-size: 11pt;
  font-weight: 700;
  letter-spacing: 0.02em;
}
header .meta {
  font-size: 7pt;
  color: #444;
  text-align: right;
  line-height: 1.25;
}
.columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 4mm;
  align-content: start;
}
.group {
  break-inside: avoid;
  page-break-inside: avoid;
  margin-bottom: 1.4mm;
}
.group h2 {
  margin: 0 0 0.4mm 0;
  font-size: 7pt;
  font-weight: 700;
  color: #fff;
  background: #333;
  padding: 0.4mm 1.2mm;
  letter-spacing: 0.02em;
}
table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}
th, td {
  padding: 0.35mm 0.6mm;
  vertical-align: top;
  border-bottom: 0.25pt solid #ddd;
  line-height: 1.22;
}
th {
  text-align: left;
  font-size: 6.2pt;
  color: #555;
  font-weight: 600;
  border-bottom: 0.5pt solid #999;
}
col.sh { width: 8mm; }
col.ln { width: 22mm; }
col.ds { width: auto; }
td.sh {
  font-family: Consolas, "Courier New", monospace;
  font-weight: 700;
  font-size: 7pt;
  white-space: nowrap;
}
td.ln {
  font-family: Consolas, "Courier New", monospace;
  font-size: 6.8pt;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
td.ds { font-size: 7pt; }
footer {
  margin-top: 1.8mm;
  padding-top: 1.4mm;
  border-top: 1pt solid #222;
  font-size: 6.6pt;
  line-height: 1.28;
  color: #222;
  break-inside: avoid;
  page-break-inside: avoid;
}
footer strong { font-weight: 700; }
footer .row { margin: 0.25mm 0; }
code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 6.5pt;
  background: #f0f0f0;
  padding: 0 1pt;
}
@media screen {
  body { background: #e8e8e8; padding: 8mm; }
  .sheet {
    background: #fff;
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    padding: 7mm;
  }
}
@media print {
  body { background: #fff; }
  .sheet { box-shadow: none; padding: 0; }
}
"""

# Left: S, G, I, M, Path   Right: X, C, W, V, Special
COL_SPLIT = 5


def build_html() -> str:
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>SliderMC Command Cheat Sheet</title>",
        f"<style>{CSS}</style>",
        "</head>",
        "<body>",
        '<div class="sheet">',
        "<header>",
        "<h1>SliderMC Command Cheat Sheet</h1>",
        f'<div class="meta">Firmware V{html.escape(FW_VERSION)}<br>DIN A4 · ASCII protocol</div>',
        "</header>",
        '<div class="columns">',
        '<div class="col">',
    ]

    def emit_group(title: str, rows: list) -> None:
        parts.append('<section class="group">')
        parts.append(f"<h2>{html.escape(title)}</h2>")
        parts.append("<table>")
        parts.append(
            '<colgroup><col class="sh"><col class="ln"><col class="ds"></colgroup>'
        )
        parts.append(
            "<thead><tr><th>Short</th><th>Long</th><th>Description</th></tr></thead>"
        )
        parts.append("<tbody>")
        for sh, lng, _call, _reply, desc in rows:
            parts.append(
                "<tr>"
                f'<td class="sh">{html.escape(sh)}</td>'
                f'<td class="ln">{html.escape(lng)}</td>'
                f'<td class="ds">{html.escape(desc)}</td>'
                "</tr>"
            )
        parts.append("</tbody></table></section>")

    for title, rows in GROUPS[:COL_SPLIT]:
        emit_group(title, rows)
    parts.append("</div>")
    parts.append('<div class="col">')
    for title, rows in GROUPS[COL_SPLIT:]:
        emit_group(title, rows)
    parts.append("</div></div>")  # col + columns

    parts.append("<footer>")
    parts.append(
        '<div class="row"><strong>Wire:</strong> '
        "one command per line (<code>\\n</code>); "
        "chain with <code>;</code>; "
        "<code>#</code> comment to EOL (comment-only lines ignored); "
        "bare bool setters toggle; "
        "motion/settings silent on success; errors <code>!E:code message</code>.</div>"
    )
    parts.append(
        '<div class="row"><strong>Realtime</strong> (no newline): '
        "<code>?</code> status · "
        "<code>!</code> soft stop · "
        "<code>Ctrl-X</code> (0x18) soft reset.</div>"
    )
    parts.append(
        '<div class="row"><strong>Status</strong> (<code>#X …</code>): '
        "<code>I</code> idle · <code>A</code> accel · <code>M</code> cruise · "
        "<code>B</code> decel · <code>H</code> homing · <code>P</code> path · "
        "<code>L</code> hard-limit · <code>D</code> disabled · <code>E</code> error. "
        "Moving: <code>#M/#A/#B pos speed accel [target]</code>.</div>"
    )
    parts.append(
        '<div class="row"><strong>Halt vs Stop:</strong> '
        "<code>MS</code>/<code>!</code> soft decel (enable kept, ends joy-mode); "
        "<code>H</code>/<code>HT</code> immediate abort, enable off, cancel waits. "
        "<code>MJ</code>: skip if value unchanged.</div>"
    )
    parts.append("</footer>")
    parts.append("</div></body></html>")
    return "\n".join(parts)


def _md_cell(s: str) -> str:
    """Escape pipes for markdown tables."""
    return s.replace("|", "\\|")


def build_markdown() -> str:
    lines = [
        "# SliderMC Command Cheat Sheet",
        "",
        f"Firmware V{FW_VERSION}. Same groups as the [printable sheet](command-cheatsheet.html).",
        "Canonical prose: [protocol.md](protocol.md). Dual-axis timing: [dual-movement.md](../mc/dual-movement.md). Joystick: [motion-joy.md](../mc/motion-joy.md). Working window: [working-window.md](../mc/working-window.md).",
        "",
        "Regenerate: `python tools/render_command_cheatsheet.py`",
        "",
        "- **Call** — send this (brackets = optional; bare = omit args).",
        "- **Reply** — typical success line; `—` = silent (errors still `!E:…`).",
        "",
    ]
    for title, rows in GROUPS:
        lines.append(f"## {title}")
        lines.append("")
        lines.append("| Short | Long | Call | Reply | Description |")
        lines.append("|-------|------|------|-------|-------------|")
        for sh, lng, call, reply, desc in rows:
            lines.append(
                f"| `{_md_cell(sh)}` | `{_md_cell(lng)}` | `{_md_cell(call)}` | "
                f"`{_md_cell(reply)}` | {_md_cell(desc)} |"
            )
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- Chain with `;`. Realtime (no newline): `?` status, `!` soft stop, `Ctrl-X` soft reset."
    )
    lines.append(
        "- Path mode (`PG`): most move/session cmds → `!E:busy`; allowed: `MS`/`H`/`RB`/`PD`/`PN`/`I*`/`G*`/`V*`/`IX`/`Help`/`CG`/`Z`/`X0-3`."
    )
    lines.append(
        "- `MJ` / `MoveJoy`: signed % of `SS`; skip unchanged values; `SS`/`SA` live in joy-mode. See [motion-joy.md](../mc/motion-joy.md)."
    )
    lines.append(
        "- Skip token `_` only (`MT`/`M`/`PD`/`SL`/`SR`). `SL`/`SR` `none` clears a side (effective = envelope when set). See [working-window.md](../mc/working-window.md)."
    )
    lines.append(
        "- Soft limits / units: see config keys `slider_min`/`max`, `steps_per_unit`, `unit_name`."
    )
    lines.append("")
    return "\n".join(lines)


def find_browser() -> list[str] | None:
    candidates = [
        "msedge",
        "chrome",
        "google-chrome",
        "chromium",
        "chromium-browser",
    ]
    for name in candidates:
        path = shutil.which(name)
        if path:
            return [path]

    win_paths = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]
    for p in win_paths:
        if p.is_file():
            return [str(p)]
    return None


def export_pdf(html_path: Path, pdf_path: Path) -> bool:
    browser = find_browser()
    if not browser:
        return False
    url = html_path.resolve().as_uri()
    cmd = browser + [
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        url,
    ]
    print("PDF via:", cmd[0])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not pdf_path.is_file():
        if r.stderr:
            print(r.stderr, file=sys.stderr)
        return False
    return True


def main() -> int:
    html_text = build_html()
    HTML_OUT.write_text(html_text, encoding="utf-8")
    print(f"Wrote {HTML_OUT}")

    md_text = build_markdown()
    MD_OUT.write_text(md_text, encoding="utf-8")
    print(f"Wrote {MD_OUT}")
    MD2_OUT.write_text(MD2_CSS + md_text, encoding="utf-8")
    print(f"Wrote {MD2_OUT}")

    if export_pdf(HTML_OUT, PDF_OUT):
        print(f"Wrote {PDF_OUT}")
        return 0

    print(
        "WARNING: No Edge/Chrome found for PDF export. "
        "Open the HTML and print to PDF (A4). HTML is ready.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
