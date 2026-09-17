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
                "SA [<a> [d]]",
                SILENT,
                "Peak accel [, decel] mm/s² (≤ max_accel_1). One value sets both ramps; two split start/stop. No skip _. Bare reloads init_accel into both; live on next fill (incl. MJ). Dual MT: same ratio scaling as SS.",
            ),
            (
                "SE",
                "Set Enable",
                "SE [0|1]",
                SILENT,
                "Driver enable 0|1; bare toggles; required before motion; off = hard stop. SE 0 also stops servo PWM (limp).",
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
                "SL [<axv>]",
                SILENT,
                "Session soft min (working window); bare→MOTOR_N_min/SERVO envelope; none clears (→envelope if set); skip _; !E:limit past envelope.",
            ),
            (
                "SR",
                "Set Right",
                "SR [<axv>]",
                SILENT,
                "Session soft max; bare→MOTOR_N_max/SERVO envelope; none clears; skip _; !E:limit if left>right.",
            ),
            (
                "SP",
                "Set Position",
                "SP [<axv>]",
                SILENT,
                "Set reported pose (no motion); idle only; bare/0 = here is zero; skip _.",
            ),
        ],
    ),
    (
        "G — Get (session)",
        [
            ("GS", "Get Speed", "GS", "GS:<mm/s>", "Current session cruise speed."),
            ("GA", "Get Accel", "GA", "GA:<a> <d>", "Current session accel and decel (mm/s²)."),
            ("GE", "Get Enable", "GE", "GE:0|1", "Driver enable state."),
            ("GT", "Get Terminal", "GT", "GT:0|1", "Terminal Mode state."),
            ("GV", "Get Verbose", "GV", "GV:0|1", "Verbose push state."),
            ("GD", "Get Debug", "GD", "GD:<0..5>", "USB debug level."),
            (
                "GL",
                "Get Left",
                "GL",
                "GL:<pos> [| …]",
                "Session soft min; effective (session else envelope); - if both None; extra pipe fields when packed≥2.",
            ),
            (
                "GR",
                "Get Right",
                "GR",
                "GR:<pos> [| …]",
                "Session soft max; same effective / - rules as GL.",
            ),
        ],
    ),
    (
        "I — Is / Info",
        [
            ("IM", "Is Moving", "IM", "IM:0|1", "Moving or settling on any active axis."),
            ("IH", "Is Homing", "IH", "IH:0|1", "Homing cycle active."),
            ("IL", "Is Limit", "IL", "IL:0|1", "At soft-limit position (axis1)."),
            ("IE", "Is Error", "IE", "IE:0|1", "PIN_DRV_ERROR / EMO latched."),
            (
                "IP",
                "Is Position",
                "IP",
                "IP:<pos> [| …]",
                "One pipe field per packed live channel (motors then servos; CG axis = sum).",
            ),
            ("IA", "Is Axis", "IA", "IA:<n>", "Packed live channels motors+servos (1..6). Same as CG axis. CS axis rejected."),
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
                "MT <axv> (absolute)",
                SILENT,
                "Absolute user units; up to 6 packed channels (XYZ motors, ABC servos); skip _; needs SE; live-retarget. Dual MT: time-sync. Out-of-window = !E:soft (no clip).",
            ),
            (
                "MB",
                "Move By",
                "MB <axv> (delta) …",
                SILENT,
                "Relative move; same skip/named XYZABC rules as MT.",
            ),
            (
                "MJ",
                "Move Joy",
                "MJ <pct> …",
                SILENT,
                "Joy speed % of SS, signed (− left / + right); omit named extra=0; 0=soft-stop; SS/SA live; clamp max_speed_N. Hold-to-jog: MJ ±100, MS on release.",
            ),
            (
                "MH",
                "Move Home",
                "MH [1|2|3]",
                SILENT,
                "Homing; axis 1 (default), 2, or 3; no-op if home_mode_N=0; cancel MS/ME.",
            ),
            (
                "MS",
                "Move Soft Stop",
                "MS",
                SILENT,
                "Soft decelerate both axes; keeps enable; ends joy-mode; does not cancel waits. Dual: scaled accel kept.",
            ),
            (
                "ME",
                "Move E-Stop, Halt",
                "ME",
                SILENT,
                "Immediate STEP abort; enable off; cancel waits and remaining ; chain.",
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
                "PD <axv_um>",
                SILENT,
                "Append signed µm sample(s); up to 6 packed channels; skip _ →0; OK while PG (live stream).",
            ),
            (
                "PG",
                "Path Go",
                "PG",
                SILENT,
                "Play buffer from sample 0; needs SE; !E:empty|busy|disabled. MS/ME ends path.",
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
                "Wait until time-sync master pos reached/overstepped; idle→immediate; 2nd arg=timeout.",
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
        "E — Extender",
        [
            (
                "EO",
                "Ext Out",
                "EO0..3 [0|1]",
                SILENT,
                "Ext out n logical 0|1; bare EO0 toggles; glued EO01≡EO0 1; OK during EMO. EO4+ rejected.",
            ),
        ],
    ),
    (
        "Special",
        [
            (
                "RB",
                "Reboot",
                "RB",
                SILENT,
                "Soft MCU reset (no power cycle); EN off first. CS motors/servos do not need RB.",
            ),
            (
                "BE",
                "Beep",
                "BE [<ms>]",
                SILENT,
                "Pulse PIN_BUZZER; bare 100 ms; clamp 1..1000; not a wait. No-op if BUZZER_use=0. OK during EMO/path.",
            ),
            (
                "CT",
                "Camera Trigger",
                "CT [<ms>]",
                SILENT,
                "Pulse PIN_CAMERA_CTRL low (OC sink); bare 100 ms; clamp 1..60000; not a wait; motion continues. OK during EMO/path. Verbose on: status letter T while pulsing (at least once).",
            ),
            (
                "HL/?",
                "Help",
                "HL | ?",
                "(multi-line table)",
                "Two-column table of all commands (short + phrase). ? needs newline; not realtime status.",
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
                "Persist key to mc.ini; silent ok. CS motors/servos re-init GPIO immediately (no RB). CS axis rejected.",
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
        ],
    ),
    (
        "V — Version",
        [
            ("VA", "Version About", "VA", "VA:…", "About string (name, version, author)."),
            ("VF", "Version FW", "VF", "VF:<version>", "Firmware version."),
            ("VP", "Version Protocol", "VP", "VP:1", "Protocol version (1). Wire may change without bumping VP."),
            (
                "VG",
                "Version GPIO",
                "VG",
                "VG:PIN_*=n (multi-line)",
                "Machine-readable pin map. Extra-axis pins if that axis is live.",
            ),
        ],
    ),
]

NOW_COMMANDS = [
    (
        "#",
        "Status now",
        "#",
        "#<state> …",
        "Realtime compact status line (no newline).",
    ),
    (
        "!",
        "Soft Stop now",
        "!",
        SILENT,
        "Realtime soft stop (same urgency as MS).",
    ),
    (
        "ESC",
        "E-Stop now",
        "ESC",
        SILENT,
        "Realtime halt (same urgency as ME): STEP abort, EN off, cancel waits/chain.",
    ),
]


CSS = """
@page { size: 210mm 297mm; margin: 6mm; }
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  font-size: 6.6pt;
  color: #111;
  background: #fff;
}
.sheet {
  width: 198mm;
  margin: 0 auto;
  padding: 0;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-bottom: 1.1pt solid #222;
  padding-bottom: 0.8mm;
  margin-bottom: 1.2mm;
}
header h1 {
  margin: 0;
  font-size: 10pt;
  font-weight: 700;
  letter-spacing: 0.02em;
}
header .meta {
  font-size: 6.4pt;
  color: #444;
  text-align: right;
  line-height: 1.2;
}
.columns {
  column-count: 2;
  column-gap: 3.5mm;
  column-fill: balance;
}
.group {
  break-inside: avoid;
  page-break-inside: avoid;
  -webkit-column-break-inside: avoid;
  display: inline-block;
  width: 100%;
  margin: 0 0 1mm 0;
}
.group h2 {
  margin: 0 0 0.3mm 0;
  font-size: 6.5pt;
  font-weight: 700;
  color: #fff;
  background: #333;
  padding: 0.3mm 1mm;
  letter-spacing: 0.02em;
}
table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}
td {
  padding: 0.18mm 0.5mm;
  vertical-align: top;
  border-bottom: 0.25pt solid #ddd;
  line-height: 1.16;
}
col.sh { width: 8mm; }
col.ln { width: 26mm; }
col.ds { width: auto; }
td.sh {
  font-family: Consolas, "Courier New", monospace;
  font-weight: 700;
  font-size: 6.6pt;
  white-space: nowrap;
}
td.ln {
  font-family: Consolas, "Courier New", monospace;
  font-size: 6.3pt;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
td.ds { font-size: 6.5pt; }
footer {
  margin-top: 1.2mm;
  padding-top: 1mm;
  border-top: 1pt solid #222;
  font-size: 6.1pt;
  line-height: 1.22;
  color: #222;
  break-inside: avoid;
  page-break-inside: avoid;
}
footer strong { font-weight: 700; }
footer .row { margin: 0.15mm 0; }
code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 6pt;
  background: #f0f0f0;
  padding: 0 1pt;
}
@media screen {
  body { background: #e8e8e8; padding: 8mm; }
  .sheet {
    width: 210mm;
    min-height: 297mm;
    background: #fff;
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    padding: 6mm;
  }
}
@media print {
  body { background: #fff; }
  .sheet { width: auto; box-shadow: none; padding: 0; min-height: 0; }
}
"""

# Print sheet: all groups flow in two balanced CSS columns (one A4 page).


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
    ]

    def emit_group(title: str, rows: list) -> None:
        parts.append('<section class="group">')
        parts.append(f"<h2>{html.escape(title)}</h2>")
        parts.append("<table>")
        parts.append(
            '<colgroup><col class="sh"><col class="ln"><col class="ds"></colgroup>'
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

    for title, rows in GROUPS:
        emit_group(title, rows)
    emit_group("Now Commands", NOW_COMMANDS)
    parts.append("</div>")  # columns

    parts.append("<footer>")
    parts.append(
        '<div class="row"><strong>Wire:</strong> '
        "one command per line (<code>\\n</code>); "
        "chain with <code>;</code>; "
        "axis args positional or named <code>X</code>/<code>Y</code>/<code>Z</code> "
        "(glued <code>MTX20Y50Z100</code> ok); "
        "<code>#</code> is realtime status, not a comment; "
        "<code>/</code> comments to end of line; "
        "bare bool setters toggle; "
        "motion/settings silent on success; errors <code>!E:code message</code>.</div>"
    )
    parts.append(
        '<div class="row"><strong>Realtime</strong> (no newline): '
        "<code>#</code> status · "
        "<code>!</code> soft stop · "
        "<code>ESC</code> halt (same as ME) · "
        "<code>Ctrl-X</code> (0x18) soft reset. "
        "<code>?</code> is help (needs newline), not status.</div>"
    )
    parts.append(
        '<div class="row"><strong>Status</strong> (<code>#X …</code>): '
        "<code>I</code> idle · <code>A</code> accel · <code>M</code> cruise · "
        "<code>B</code> decel · <code>H</code> homing · <code>P</code> path · "
        "<code>L</code> hard-limit · <code>D</code> disabled · <code>E</code> error · "
        "<code>T</code> camera trigger (CT pulse, or one-shot listen). "
        "Moving: <code>#M/#A/#B pos speed accel [target]</code>.</div>"
    )
    parts.append(
        '<div class="row"><strong>Halt vs Stop:</strong> '
        "<code>MS</code>/<code>!</code> soft decel (enable kept, ends joy-mode); "
        "<code>ME</code>/<code>ESC</code> immediate abort, enable off, cancel waits. "
        "<code>MJ</code>: skip if value unchanged. Hold-to-jog: <code>MJ ±100</code>, "
        "<code>MS</code> on release. <code>VP</code> stays 1 (wire may still change).</div>"
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
        "## Arguments",
        "",
        "`<s>`",
        ": Speed in mm/s or deg/s",
        "",
        "`<a>`",
        ": Acceleration / deceleration in mm/s² or deg/s²",
        "",
        "`<axv>`",
        ": Axis values for the packed live channels (STEP/DIR motors first, then RC servos; up to six). A line is **either** positional **or** named — never mixed (`MT 20 C100` → `!E:parse`).",
        ": **Positional:** one number per channel in order, spaces between them. `_` skips a slot and leaves that channel unchanged (`MT _ _ 100` moves only channel 3). Omitted trailing slots are unchanged (`MT 50` is channel 1 only).",
        ": **Named:** letters `X` `Y` `Z` = motors 1–3, `A` `B` `C` = servos 1–3, then the value (spaces optional: `C100`, `C 100`, `MT C100 B50`). Duplicate letter, unknown letter, or a channel that is not fitted → `!E:parse`.",
        ": `PD` uses the same forms in **µm** (`<axv_um>`); skip `_` or omit named → `0`.",
        ": `MJ` uses signed **percent** (not mm); omitted named extra = `0`; `_` is invalid.",
        "",
    ]

    def emit_md_table(rows: list) -> None:
        lines.append("| Command | Call | Reply | Description |")
        lines.append("|--------|------|-------|-------------|")
        for sh, lng, call, reply, desc in rows:
            call_cell = f"**`{_md_cell(sh)}`**"
            extra = call.strip()
            prefix = sh.upper()
            if extra.upper().startswith(prefix):
                extra = extra[len(sh) :].lstrip()
            if extra:
                call_cell += f"`{_md_cell(extra)}`"
            lines.append(
                f"| {_md_cell(lng)} | {call_cell} | `{_md_cell(reply)}` | {_md_cell(desc)} |"
            )
        lines.append("")

    for title, rows in GROUPS:
        lines.append(f"## {title}")
        lines.append("")
        emit_md_table(rows)
    lines.append("## Now Commands")
    lines.append("")
    lines.append("Executed immediately without \\n")
    lines.append("")
    emit_md_table(NOW_COMMANDS)
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- Chain with `;`. `/` comments from that character to end of line. Realtime (no newline): `#` status, `!` soft stop, `ESC` halt, `Ctrl-X` soft reset. `#` is not a comment. `?` is help (needs `\\n`), not status."
    )
    lines.append(
        "- Path mode (`PG`): most move/session cmds → `!E:busy`; allowed: `MS`/`ME`/`RB`/`PD`/`PN`/`I*`/`G*`/`V*`/`IG`/`HL`/`?`/`CG`/`BE`/`CT`."
    )
    lines.append(
        "- `MJ` / Move Joy: signed % of `SS`; skip unchanged values; `SS`/`SA` live in joy-mode. Hold-to-jog: `SS` then `MJ ±100`, `MS` on release. See [motion-joy.md](../mc/motion-joy.md)."
    )
    lines.append(
        "- Skip token `_` only (`MT`/`MB`/`PD`/`SL`/`SR`). Named `X`/`Y`/`Z`/`A`/`B`/`C` is an alternative (not mixed with positional). `SL`/`SR` `none` clears a side (effective = envelope when set). See [working-window.md](../mc/working-window.md)."
    )
    lines.append(
        "- Envelopes / units: `MOTOR_N_min`/`MOTOR_N_max`, `SERVO_N_min`/`SERVO_N_max`, synthesized `axis_min_N`, `steps_per_unit_N`, `unit_name`. Servo pulse `SERVO_N_min_pulse`/`max_pulse` (default 500–2500 µs; analog 1000–2000); `SERVO_N_swap` reverses sense. `CS axis` and `CS slider_*` are rejected."
    )
    lines.append(
        "- Breaking wire (`ME`, `?` help, `#` status only, `/` comments, `CT`) does **not** bump `VP` — still `VP:1`."
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
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--no-first-run",
        "--disable-extensions",
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
