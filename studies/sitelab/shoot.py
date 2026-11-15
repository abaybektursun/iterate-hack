"""Watch a lab page run in real time on the GPU: frames at real intervals, the frame rate, console errors, pointer input.

  uv run --with playwright studies/sitelab/shoot.py <url> <out dir> [--frames 6] [--every 1000] [--size 1600x1000]
      [--scheme dark|light] [--do "wait 2000; move 800 500; click 800 500; drag 600 500 900 520; wheel -400; key Space"]

Runs the installed Chrome headless with hardware WebGL (no virtual time, so animation runs as in a visible tab).
First it runs the --do steps in order, then it saves <out dir>/f00.png ... at --every ms. It prints the frames per
second counted by requestAnimationFrame over the whole run, and every console error and failed request.
"""
import argparse
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

a = argparse.ArgumentParser()
a.add_argument("url")
a.add_argument("out")
a.add_argument("--frames", type=int, default=6)
a.add_argument("--every", type=int, default=1000)
a.add_argument("--size", default="1600x1000")
a.add_argument("--scheme", default="dark")
a.add_argument("--do", default="")
a = a.parse_args()
w, h = map(int, a.size.split("x"))
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True, args=[
        "--ignore-gpu-blocklist", "--enable-gpu", "--use-angle=gl", "--enable-webgl", "--disable-frame-rate-limit"])
    page = browser.new_page(viewport={"width": w, "height": h}, color_scheme=a.scheme)
    problems = []
    page.on("console", lambda m: problems.append(f"console {m.type}: {m.text[:300]}") if m.type == "error" else None)
    page.on("pageerror", lambda e: problems.append(f"page error: {str(e)[:300]}"))
    page.on("requestfailed", lambda r: problems.append(f"request failed: {r.url[:200]}"))
    page.on("response", lambda r: problems.append(f"http {r.status}: {r.url[:200]}") if r.status >= 400 else None)
    page.add_init_script("window.__n = 0; (function f() { window.__n++; requestAnimationFrame(f); })();")
    start = time.time()
    page.goto(a.url, wait_until="load")
    for step in filter(None, (s.strip() for s in a.do.split(";"))):
        op, *v = step.split()
        if op == "wait":
            page.wait_for_timeout(int(v[0]))
        elif op == "move":
            page.mouse.move(float(v[0]), float(v[1]), steps=12)
        elif op == "click":
            page.mouse.click(float(v[0]), float(v[1]))
        elif op == "drag":
            page.mouse.move(float(v[0]), float(v[1]))
            page.mouse.down()
            page.mouse.move(float(v[2]), float(v[3]), steps=20)
            page.mouse.up()
        elif op == "wheel":
            page.mouse.wheel(0, float(v[0]))
        elif op == "key":
            page.keyboard.press(v[0])
        else:
            sys.exit(f"unknown step: {step}")
    for i in range(a.frames):
        page.screenshot(path=str(out / f"f{i:02d}.png"))
        page.wait_for_timeout(a.every)
    frames = page.evaluate("window.__n")
    gl = page.evaluate("""() => { const g = document.createElement('canvas').getContext('webgl2');
        const e = g && g.getExtension('WEBGL_debug_renderer_info'); return g ? (e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'webgl2') : 'no webgl2'; }""")
    browser.close()
print(f"{frames / (time.time() - start):.0f} frames per second over {time.time() - start:.0f} s (screenshots slow it); renderer: {gl}")
print(f"{a.frames} frames in {out}")
print("\n".join(problems) if problems else "no console errors, no failed requests")
