#!/usr/bin/env python3
"""Render SliderMC Command Cheat Sheet (DIN A4 HTML + optional PDF).

Command rows mirror firmware k_help_rows in src/protocol/commands.cpp.
Descriptions here are the shared source for the cheat sheet and docs/PROTOCOL.md
command tables (keep both in sync when editing).
"""

from __future__ import annotations

import html
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML_OUT = ROOT / "MC_Command_Cheat_Sheet.html"
PDF_OUT = ROOT / "MC_Command_Cheat_Sheet.pdf"
FW_VERSION = "1.0"

# (group_title, [(short, long, desc), ...])
# Descriptions are shared with PROTOCOL.md command tables.
GROUPS = [
    (
        "S — Set (session)",
        [
            ("SS", "SetSpeed",
             "Set cruise speed mm/s (≤ max_speed); bare reloads init_speed; applies live to the next fill."),
            ("SA", "SetAccel",
             "Set accel mm/s² (≤ max_accel); bare reloads init_accel; applies live to the next fill."),
            ("SE", "SetEnable",
             "Driver enable 0|1; bare toggles; required before motion; off stops hard."),
            ("ST", "SetTerminal",
             "Terminal Mode 0|1; bare toggles; local echo + UART command sniff to USB."),
            ("SV", "SetVerbose",
             "Verbose status push 0|1; bare toggles; ~3 Hz #M/#I lines when on."),
            ("SD", "SetDebug",
             "USB-only debug level 0..5; bare restores default; never sent on UIC UART."),
        ],
    ),
    (
        "G — Get (session)",
        [
            ("GS", "GetSpeed", "Reply GS:<mm/s> — current session cruise speed."),
            ("GA", "GetAccel", "Reply GA:<mm/s2> — current session acceleration."),
            ("GE", "GetEnable", "Reply GE:0|1 — driver enable state."),
            ("GT", "GetTerminal", "Reply GT:0|1 — Terminal Mode state."),
            ("GV", "GetVerbose", "Reply GV:0|1 — verbose push state."),
            ("GD", "GetDebug", "Reply GD:<0..5> — USB debug level."),
        ],
    ),
    (
        "I — Is / status",
        [
            ("IM", "IsMoving", "Reply IM:0|1 — axis currently moving (or settling)."),
            ("IH", "IsHoming", "Reply IH:0|1 — homing cycle active."),
            ("IL", "IsLimit", "Reply IL:0|1 — at soft-limit position."),
            ("IE", "IsError", "Reply IE:0|1 — PIN_DRV_ERROR / EMO latched."),
            ("IP", "IsPosition", "Reply IP:<mm> — current planner position."),
            ("IT", "IsTarget", "Reply IT:<mm>|- — seek target, or - if none."),
            ("IR", "IsReady",
             "Reply IR:1 only if idle, not homing, enabled, and not waiting."),
            ("IW", "IsWaiting", "Reply IW:1 if any W / WM / WH wait is active."),
            ("ID", "IsDiag",
             "Reply underrun count, peak STEP Hz, overshoot steps, min FIFO level."),
            ("IZ", "IsReset",
             "Reply last chip reset cause (power|wdt|run|soft|debug|brownout|…)."),
            ("IX", "Pinout",
             "ASCII table: GP number, pin name, brief description (≤80 cols)."),
        ],
    ),
    (
        "M — Movement",
        [
            ("MT", "MoveTo",
             "Move to absolute mm; needs enable; live-retargets an active move."),
            ("M", "Move",
             "Relative move by mm (alias MoveBy); needs enable; live-retargets."),
            ("ML", "MoveLeft", "Continuous jog negative; soft-stop with MS or !."),
            ("MR", "MoveRight", "Continuous jog positive; soft-stop with MS or !."),
            ("MH", "MoveHome",
             "Homing cycle (home_mode); no-op if 0; needs SE 1; cancel with MS/H."),
            ("MS", "MoveStop",
             "Soft decelerate to stop; keeps enable; does not cancel waits."),
        ],
    ),
    (
        "X — Extender",
        [
            ("X0–9", "Ext0–9",
             "Ext out n logical 0|1; bare toggles; glued X00≡X0 0; ok during EMO."),
        ],
    ),
    (
        "C — Config",
        [
            ("CS", "ConfigSet",
             "Set persistent key value (mc.ini); silent ok; updates session init_speed/init_accel/…"),
            ("CG", "ConfigGet",
             "Get key → CG:key=value; bare dumps all keys."),
        ],
    ),
    (
        "W — Wait",
        [
            ("W", "Wait",
             "Delay sec then continue ; chain; bare → 1 s; never !E:timeout."),
            ("WM", "WaitMoving",
             "Pause chain until move ends; optional timeout cancels remaining chain."),
            ("WH", "WaitHoming",
             "Pause chain until homing ends; optional timeout cancels remaining chain."),
        ],
    ),
    (
        "V — Version",
        [
            ("VA", "VersionAbout", "Reply VA: about string (name, version, author)."),
            ("VF", "VersionFW", "Reply VF:<version> — firmware version."),
            ("VP", "VersionProtocol", "Reply VP:<n> — protocol version."),
        ],
    ),
    (
        "Special",
        [
            ("H/HT", "Halt",
             "Immediate STEP abort; enable off; cancel waits and remaining ; chain."),
            ("P", "Pins", "List PIN_*=GPIO lines (machine-readable, read-only)."),
            ("$/HL", "Help", "ASCII table of all commands (≤80 columns)."),
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

# Split groups across two fixed columns so footer stays on page 1.
# Left: S, G, I, M   Right: X, C, W, V, Special
COL_SPLIT = 4


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
        for sh, lng, desc in rows:
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
        "<code>B</code> decel · <code>H</code> homing · "
        "<code>L</code> hard-limit · <code>D</code> disabled · <code>E</code> error. "
        "Moving: <code>#M/#A/#B pos speed accel [target]</code>.</div>"
    )
    parts.append(
        '<div class="row"><strong>Halt vs Stop:</strong> '
        "<code>MS</code>/<code>!</code> soft decel (enable kept); "
        "<code>H</code>/<code>HT</code> immediate abort, enable off, cancel waits.</div>"
    )
    parts.append("</footer>")
    parts.append("</div></body></html>")
    return "\n".join(parts)


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
