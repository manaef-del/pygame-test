"""Lädt den pygbag-Build in Headless-Chromium und gibt die Konsole aus.

Aufruf (nach ``python -m pygbag --build .``)::

    python tools/browser_smoke.py build/web

Dient der Diagnose in CI: Python-Fehler im Browser landen in der
Browser-Konsole, die hier auf stdout gespiegelt wird.
"""

from __future__ import annotations

import functools
import http.server
import sys
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

WAIT_SECONDS = 60
PORT = 8765


def serve(directory: Path) -> http.server.ThreadingHTTPServer:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    handler_cls = type("Quiet", (handler.func,), {"log_message": lambda *a, **k: None})
    handler = functools.partial(handler_cls, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main(web_dir: str) -> int:
    server = serve(Path(web_dir))
    url = f"http://127.0.0.1:{PORT}/index.html"
    lines: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 480, "height": 800})
        page.on("console", lambda m: lines.append(f"[console.{m.type}] {m.text}"))
        page.on("pageerror", lambda e: lines.append(f"[pageerror] {e}"))
        page.on("requestfailed", lambda r: lines.append(f"[requestfailed] {r.url} {r.failure}"))
        page.goto(url, wait_until="load")
        deadline = time.time() + WAIT_SECONDS
        while time.time() < deadline:
            page.wait_for_timeout(1000)
            # Sobald das Spiel zeichnet, taucht "Punkte:" nicht in der Konsole
            # auf, deshalb einfach die volle Wartezeit abwarten.
        page.screenshot(path=str(Path(web_dir).parent / "smoke.png"))
        try:
            canvas_info = page.evaluate(
                "() => { const c = document.querySelector('canvas');"
                " if (!c) return 'no canvas';"
                " return `canvas ${c.width}x${c.height} css ${c.clientWidth}x${c.clientHeight}`; }"
            )
        except Exception as exc:  # noqa: BLE001
            canvas_info = f"evaluate failed: {exc}"
        browser.close()

    server.shutdown()
    print("=== BROWSER CONSOLE ===")
    for line in lines:
        print(line)
    print("=== CANVAS ===")
    print(canvas_info)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "build/web"))
