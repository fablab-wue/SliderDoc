#!/usr/bin/env python3
"""Render UIC cheat sheet HTML to PDF (A4).

  python tools/render_cheat_sheet.py              # jkslider + b4slider
  python tools/render_cheat_sheet.py jkslider
  python tools/render_cheat_sheet.py b4slider
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GITHUB = "https://github.com/fablab-wue/SliderCtrl"

SHEETS = {
    "jkslider": {
        "html": ROOT / "uic" / "projects" / "jkslider" / "cheat-sheet" / "cheat-sheet.html",
        "pdf": ROOT / "uic" / "projects" / "jkslider" / "cheat-sheet" / "cheat-sheet.pdf",
    },
    "b4slider": {
        "html": ROOT / "uic" / "projects" / "b4slider" / "cheat-sheet" / "cheat-sheet.html",
        "pdf": ROOT / "uic" / "projects" / "b4slider" / "cheat-sheet" / "cheat-sheet.pdf",
    },
}


def _render_playwright(html: Path, pdf: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    html_uri = html.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_uri, wait_until="networkidle")
        page.pdf(
            path=str(pdf),
            format="A4",
            print_background=True,
            margin={
                "top": "8mm",
                "bottom": "8mm",
                "left": "8mm",
                "right": "8mm",
            },
            prefer_css_page_size=True,
        )
        browser.close()
    return True


def _find_chrome() -> str | None:
    candidates = [
        os.environ.get("CHROME_PATH"),
        os.environ.get("EDGE_PATH"),
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        if c and Path(c).is_file():
            return c
    return None


def _render_chrome(chrome: str, html: Path, pdf: Path) -> None:
    if pdf.exists():
        pdf.unlink()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--no-margins",
        f"--print-to-pdf={pdf}",
        html.resolve().as_uri(),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def _render_one(name: str) -> int:
    sheet = SHEETS[name]
    html = sheet["html"]
    pdf = sheet["pdf"]
    if not html.is_file():
        print("Missing HTML:", html, file=sys.stderr)
        return 1

    text = html.read_text(encoding="utf-8")
    if GITHUB not in text:
        print("Warning: expected GitHub URL missing from HTML:", GITHUB)

    if _render_playwright(html, pdf):
        print("Wrote", pdf, "(playwright)")
        return 0

    chrome = _find_chrome()
    if chrome:
        try:
            _render_chrome(chrome, html, pdf)
            if pdf.is_file():
                print("Wrote", pdf, "(%s)" % Path(chrome).name)
                return 0
        except (subprocess.CalledProcessError, OSError) as exc:
            print("Chrome/Edge print failed:", exc, file=sys.stderr)

    print(
        "Install Playwright (pip install playwright && playwright install chromium)\n"
        "or install Chrome/Edge for headless --print-to-pdf.",
        file=sys.stderr,
    )
    return 2


def main() -> int:
    args = sys.argv[1:] or list(SHEETS)
    unknown = [a for a in args if a not in SHEETS]
    if unknown:
        print("unknown sheet(s):", ", ".join(unknown), file=sys.stderr)
        print("usage: python tools/render_cheat_sheet.py [jkslider] [b4slider]", file=sys.stderr)
        return 2
    rc = 0
    for name in args:
        rc = max(rc, _render_one(name))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
