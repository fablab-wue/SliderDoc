#!/usr/bin/env python3
"""Render JKSlider cheat sheet HTML to PDF (A4).

Input:  uic/projects/jkslider/cheat-sheet/cheat-sheet.html
Output: uic/projects/jkslider/cheat-sheet/cheat-sheet.pdf
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "uic" / "projects" / "jkslider" / "cheat-sheet" / "cheat-sheet.html"
PDF = ROOT / "uic" / "projects" / "jkslider" / "cheat-sheet" / "cheat-sheet.pdf"
GITHUB = "https://github.com/fablab-wue/SliderCtrl"


def _render_playwright() -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    html_uri = HTML.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_uri, wait_until="networkidle")
        page.pdf(
            path=str(PDF),
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


def _render_chrome(chrome: str) -> None:
    # Chrome needs absolute file paths; output must not exist or be writable.
    if PDF.exists():
        PDF.unlink()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--no-margins",
        f"--print-to-pdf={PDF}",
        HTML.resolve().as_uri(),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main() -> int:
    if not HTML.is_file():
        print("Missing HTML:", HTML, file=sys.stderr)
        return 1

    text = HTML.read_text(encoding="utf-8")
    if GITHUB not in text:
        print("Warning: expected GitHub URL missing from HTML:", GITHUB)

    if _render_playwright():
        print("Wrote", PDF, "(playwright)")
        return 0

    chrome = _find_chrome()
    if chrome:
        try:
            _render_chrome(chrome)
            if PDF.is_file():
                print("Wrote", PDF, "(%s)" % Path(chrome).name)
                return 0
        except (subprocess.CalledProcessError, OSError) as exc:
            print("Chrome/Edge print failed:", exc, file=sys.stderr)

    print(
        "Install Playwright (pip install playwright && playwright install chromium)\n"
        "or install Chrome/Edge for headless --print-to-pdf.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
