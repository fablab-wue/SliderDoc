#!/usr/bin/env python3
"""Render SliderMC Command Cheat Sheet (DIN A4 HTML + Markdown + optional PDF).

Command rows mirror firmware k_help_rows in src/protocol/commands.cpp.
Canonical command prose: contract/protocol.md — keep GROUPS descriptions in sync.
Regenerate after editing protocol tables: python tools/render_command_cheatsheet.py

Each row: (short, phrase, call, reply, desc)
  call/reply appear in the Markdown reference; HTML print sheet uses short/phrase/desc.
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

# (group_title, [(short, phrase, call, reply, desc), ...])
GROUPS = [
    (
        "S — Set (session)",
        [
            (
                "SS",
                "Set Speed",
                "SS [<v>]",
                SILENT,
                "Cruise speed mm/s (≤ max_speed_1); bare reloads init_speed; live on next fill (incl. MJ). Dual MT: axis1=session, axis2×ratio.",
            ),
            (
                "SA",
                "Set Accel",
                "SA [<a>]",
                SILENT,
                "Peak accel mm/s² (≤ max_accel_1); bare reloads init_accel; live on next fill (incl. MJ). Dual MT: same ratio scaling as SS.",
            ),
            (
                "SE",
                "Set Enable",
                "SE [0|1]",
                SILENT,
                "Driver enable 0|1; bare toggles; required before motion; off = hard stop.",
            ),
            (
                "ST",
                "Set Terminal",
                "ST [0|1]",
                SILENT,
                "Terminal Mode 0|1; bare toggles; local echo + UART sniff to USB (expert).",
            ),
            (
                "SV",
                "Set Verbose",
                "SV [0|1]",
                SILENT,
                "Verbose #… push 0|1; bare toggles; ~3 Hz (rate via verbose_rate_hz).",
            ),
            (
                "SD",
                "Set Debug",
                "SD [0..5]",
                SILENT,
                "USB-only debug level 0..5; bare restores default; never on UIC UART.",
            ),
            (
                "SL",
                "Set Left",
                "SL [<pos> [<pos2> [<pos3>]]] | SL X.. Y.. Z..",
                SILENT,
                "Session soft min (working window); bare→slider_min_N; none clears (→envelope if set); skip _; !E:limit past envelope.",
            ),
            (
                "SR",
                "Set Right",
                "SR [<pos> [<pos2> [<pos3>]]] | SR X.. Y.. Z..",
                SILENT,
                "Session soft max; bare→slider_max_N; none clears; skip _; !E:limit if left>right.",
            ),
            (
                "SP",
                "Set Position",
                "SP [<pos> [<pos2> [<pos3>]]] | SP X.. Y.. Z..",
                SILENT,
                "Set reported pose (no motion); idle only; bare/0 = here is zero; skip _.",
            ),
        ],
    ),
    (
        "G — Get (session)",
        [
            ("GS", "Get Speed", "GS", "GS:<mm/s>", "Current session cruise speed."),
            ("GA", "Get Accel", "GA", "GA:<mm/s2>", "Current session acceleration."),
            ("GE", "Get Enable", "GE", "GE:0|1", "Driver enable state."),
            ("GT", "Get Terminal", "GT", "GT:0|1", "Terminal Mode state."),
            ("GV", "Get Verbose", "GV", "GV:0|1", "Verbose push state."),
            ("GD", "Get Debug", "GD", "GD:<0..5>", "USB debug level."),
            (
                "GL",
                "Get Left",
                "GL",
                "GL:<pos> [<pos2> [<pos3>]]",
                "Session soft min; effective (session else envelope); - if both None; extra fields when axis≥2.",
            ),
            (
                "GR",
                "Get Right",
                "GR",
                "GR:<pos> [<pos2> [<pos3>]]",
                "Session soft max; same effective / - rules as GL.",
            ),
        ],
    ),
    (
        "I — Is / status",
        [
            ("IM", "Is Moving", "IM", "IM:0|1", "Moving or settling on any active axis."),
            ("IH", "Is Homing", "IH", "IH:0|1", "Homing cycle active."),
            ("IL", "Is Limit", "IL", "IL:0|1", "At soft-limit position (axis1)."),
            ("IE", "Is Error", "IE", "IE:0|1", "PIN_DRV_ERROR / EMO latched."),
            (
                "IP",
                "Is Position",
                "IP",
                "IP:<pos> [<pos2> [<pos3>]]",
                "One field per live axis (CG axis).",
            ),
            ("IA", "Is Axis", "IA", "IA:1|2|3", "Live axis count (CS axis / CG axis)."),
            (
                "IT",
                "Is Target",
                "IT",
                "IT:<pos>|-",
                "Axis-1 seek target, or - if none / soft-stop.",
            ),
            (
                "IR",
                "Is Ready",
                "IR",
                "IR:0|1",
                "1 only if idle, not homing, enabled, and not waiting.",
            ),
            ("IW", "Is Waiting", "IW", "IW:0|1", "1 if any WT / WM / WH / WP / WC / WN wait is active."),
            (
                "ID",
                "Is Diag",
                "ID",
                "ID:underrun=N peak_hz=… overshoot=… fifo_min=…",
                "Motion diag counters (FIFO underrun, peak STEP Hz, …).",
            ),
            (
                "IC",
                "Is Cause",
                "IC",
                "IC:<reason>",
                "Last chip reset: power|wdt|run|soft|debug|brownout|…",
            ),
            (
                "IG",
                "Is GPIO",
                "IG",
                "(multi-line table)",
                "ASCII GP / name / desc (≤80 cols). Extra-axis rows only if that axis is live.",
            ),
        ],
    ),
    (
        "M — Movement",
        [
            (
                "MT",
                "Move To",
                "MT <pos> [<pos2> [<pos3>]] | MT X.. Y.. Z..",
                SILENT,
                "Absolute user units; extra live axes; skip _; needs SE; live-retarget. Dual: time-sync ratio. Out-of-window = !E:soft (no clip).",
            ),
            (
                "MB",
                "Move By",
                "MB <delta> [<delta2> [<delta3>]] | MB X.. Y.. Z..",
                SILENT,
                "Relative move; same extra-axis/skip/named rules as MT.",
            ),
            (
                "MJ",
                "Move Joy",
                "MJ <pct> [<pct2> [<pct3>]] | MJ X.. Y.. Z..",
                SILENT,
                "Joy speed % of SS, signed (− left / + right); omit named extra=0; 0=soft-stop; SS/SA live; clamp max_speed_N. Hold-to-jog: MJ ±100, MS on release.",
            ),
            (
                "MH",
                "Move Home",
                "MH [1|2|3]",
                SILENT,
                "Homing; axis 1 (default), 2, or 3; no-op if home_mode_N=0; cancel MS/HT.",
            ),
            (
                "MS",
                "Move Stop",
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
                "Path Clear",
                "PC",
                SILENT,
                "Clear path buffer (count→0); !E:busy while PG active.",
            ),
            (
                "PD",
                "Path Data",
                "PD <um> [<um2> [<um3>]] | PD X.. Y.. Z..",
                SILENT,
                "Append signed µm sample(s); extra live axes; skip _ →0; OK while PG (live stream).",
            ),
            (
                "PG",
                "Path Go",
                "PG",
                SILENT,
                "Play buffer from sample 0; needs SE; !E:empty|busy|disabled. MS/HT ends path.",
            ),
            (
                "PN",
                "Path Number",
                "PN",
                "PN:<count>",
                "Samples in buffer; allowed during PG.",
            ),
            (
                "PS",
                "Path Slice",
                "PS [<us>]",
                SILENT,
                "Slice length µs (≥1000); bare→init_path_slice_us; !E:busy while PG.",
            ),
        ],
    ),
    (
        "E — Extender / beep",
        [
            (
                "EO",
                "Ext Out",
                "EO0..3 [0|1]",
                SILENT,
                "Ext out n logical 0|1; bare EO0 toggles; glued EO01≡EO0 1; OK during EMO. EO4+ rejected.",
            ),
            (
                "BE",
                "Beep",
                "BE",
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
                "Config Set",
                "CS <key> <value>",
                SILENT,
                "Persist key to mc.ini; silent ok. axis / WDT_use need RB to take HW effect.",
            ),
            (
                "CR",
                "Config Reset",
                "CR",
                SILENT,
                "Reset all config to compiled defaults and save mc.ini.",
            ),
            (
                "CG",
                "Config Get",
                "CG [<key>]",
                "CG:<key>=<value>",
                "One key, or bare dumps all keys (multi-line).",
            ),
            (
                "RB",
                "Reboot",
                "RB",
                SILENT,
                "Soft MCU reset (no power cycle); EN off first. After CS axis.",
            ),
        ],
    ),
    (
        "W — Wait",
        [
            (
                "WT",
                "Wait Time",
                "WT [<sec>]",
                SILENT,
                "Delay then continue ; chain; bare→1 s; never !E:timeout.",
            ),
            (
                "WM",
                "Wait Moving",
                "WM [<timeout_s>]",
                SILENT,
                "Pause chain until move ends; optional timeout → !E:timeout, cancel rest of chain.",
            ),
            (
                "WH",
                "Wait Homing",
                "WH [<timeout_s>]",
                SILENT,
                "Pause until homing ends; timeout same as WM.",
            ),
            (
                "WP",
                "Wait Pos",
                "WP <pos> [<timeout_s>]",
                SILENT,
                "Wait until axis-1 pos reached/overstepped; idle→immediate; 2nd arg=timeout.",
            ),
            (
                "WC",
                "Wait Cruise",
                "WC [<timeout_s>]",
                SILENT,
                "Wait until cruise (status M) or idle; optional timeout → !E:timeout.",
            ),
            (
                "WN",
                "Wait Not cruise",
                "WN [<timeout_s>]",
                SILENT,
                "Wait until not cruise M; idle/A/B→immediate; timeout same as WM.",
            ),
        ],
    ),
    (
        "V — Version",
        [
            ("VA", "Version About", "VA", "VA:…", "About string (name, version, author)."),
            ("VF", "Version FW", "VF", "VF:<version>", "Firmware version."),
            ("VP", "Version Protocol", "VP", "VP:<n>", "Protocol version (2)."),
        ],
    ),
    (
        "Special",
        [
            (
                "HT",
                "Halt",
                "HT",
                SILENT,
                "Immediate STEP abort; enable off; cancel waits and remaining ; chain.",
            ),
            (
                "VG",
                "Version GPIO",
                "VG",
                "VG:PIN_*=n (multi-line)",
                "Machine-readable pin map. Extra-axis pins if that axis is live.",
            ),
            (
                "HL/$",
                "Help",
                "HL | $",
                "(multi-line table)",
                "Two-column table of all commands (short + phrase).",
            ),
            (
                "?/#",
                "Status now",
                "? | #",
                "#<state> …",
                "Realtime compact status line (no newline).",
            ),
            (
                "!/ESC",
                "Soft stop now",
                "! | ESC",
                SILENT,
                "Realtime soft stop (same urgency as MS).",
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

# Left: S, G, I, M, Path   Right: E, C, W, V, Special
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
            "<thead><tr><th>Short</th><th>Phrase</th><th>Description</th></tr></thead>"
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
        "axis args positional or named <code>X</code>/<code>Y</code>/<code>Z</code> "
        "(glued <code>MTX20Y50Z100</code> ok); "
        "<code>#</code> is realtime status, not a comment; "
        "bare bool setters toggle; "
        "motion/settings silent on success; errors <code>!E:code message</code>.</div>"
    )
    parts.append(
        '<div class="row"><strong>Realtime</strong> (no newline): '
        "<code>?</code>/<code>#</code> status · "
        "<code>!</code>/<code>ESC</code> soft stop · "
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
        "<code>MS</code>/<code>!</code>/<code>ESC</code> soft decel (enable kept, ends joy-mode); "
        "<code>HT</code> immediate abort, enable off, cancel waits. "
        "<code>MJ</code>: skip if value unchanged. Hold-to-jog: <code>MJ ±100</code>, "
        "<code>MS</code> on release.</div>"
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
        lines.append("| Short | Phrase | Call | Reply | Description |")
        lines.append("|-------|--------|------|-------|-------------|")
        for sh, lng, call, reply, desc in rows:
            lines.append(
                f"| `{_md_cell(sh)}` | `{_md_cell(lng)}` | `{_md_cell(call)}` | "
                f"`{_md_cell(reply)}` | {_md_cell(desc)} |"
            )
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- Chain with `;`. Realtime (no newline): `?`/`#` status, `!`/`ESC` soft stop, `Ctrl-X` soft reset. `#` is not a comment."
    )
    lines.append(
        "- Path mode (`PG`): most move/session cmds → `!E:busy`; allowed: `MS`/`HT`/`RB`/`PD`/`PN`/`I*`/`G*`/`V*`/`IG`/`HL`/`$`/`CG`/`BE`."
    )
    lines.append(
        "- `MJ` / Move Joy: signed % of `SS`; skip unchanged values; `SS`/`SA` live in joy-mode. Hold-to-jog: `SS` then `MJ ±100`, `MS` on release. See [motion-joy.md](../mc/motion-joy.md)."
    )
    lines.append(
        "- Skip token `_` only (`MT`/`MB`/`PD`/`SL`/`SR`). Named `X`/`Y`/`Z` is an alternative (not mixed with positional). `SL`/`SR` `none` clears a side (effective = envelope when set). See [working-window.md](../mc/working-window.md)."
    )
    lines.append(
        "- Soft limits / units: see config keys `slider_min_N`/`slider_max_N`, `steps_per_unit_N`, `unit_name`."
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
