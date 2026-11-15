"""The Team page of the site: who the team is. view.py serves PAGE at /team; the home dial leads to it.

PLACEHOLDER: the three names below are invented and every line under them is still to be written (Abay, 2026-11-15:
"for now just add 3 random names with placeholders for the info"). The page says so in its first sentence. Replace
PEOPLE with the real people. A person shows the rows of the fields that are filled; with none filled, one muted line
"Details to be added".
"""
import html

PEOPLE = [
    {"name": "Mira Okafor", "role": None, "work": None, "before": None, "contact": None},
    {"name": "Jonas Velde", "role": None, "work": None, "before": None, "contact": None},
    {"name": "Tessa Lindqvist", "role": None, "work": None, "before": None, "contact": None},
]
FIELDS = (("role", "Role"), ("work", "Work here"), ("before", "Before"), ("contact", "Contact"))


def page():
    esc = html.escape
    def rows(p):
        filled = "".join(f"<div><dt>{label}</dt><dd>{esc(p[key])}</dd></div>" for key, label in FIELDS if p[key])
        return f"<dl>{filled}</dl>" if filled else '<p class="todo">Details to be added</p>'
    return PAGE.replace("__PEOPLE__", "".join(f'<section><h2>{esc(p["name"])}</h2>{rows(p)}</section>' for p in PEOPLE))


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Team</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens and the type of the Design page (architecture.py). A page of type only: no picture yet. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --ink: #101820; --mute: #56636d; --rule: #cbd2d8; --blue: #1f43d6;
}
@media (prefers-color-scheme: dark) {
  :root { --paper: #080c11; --ink: #e9eff3; --mute: #93a1ad; --rule: #1c2630; --blue: #8fb1ff; }
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif; -webkit-font-smoothing: antialiased;
}
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.page { max-width: 1840px; margin: 0 auto; padding: 20px 40px 60px; }
.top { display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.cap { margin: clamp(28px, 7vh, 76px) 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 30ch; text-wrap: balance; }
.people { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 48px; margin-top: clamp(26px, 7vh, 72px); }
h2 { margin: 0; padding-bottom: 14px; border-bottom: 1px solid var(--rule); font-size: clamp(24px, 2.3vw, 40px); line-height: 1.08; font-weight: 300; letter-spacing: -.016em; }
dl { margin: 0; }
dl div { display: grid; grid-template-columns: 6.4em minmax(0, 1fr); column-gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--rule); }
dt { font-weight: 600; font-stretch: 108%; }
dd { margin: 0; }
.todo { margin: 0; padding: 10px 0; color: var(--mute); }
@media (max-width: 900px) {
  .page { padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .people { grid-template-columns: 1fr; row-gap: 34px; }
}
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings">Findings</a>
  </header>
  <p class="cap">Three people run this project with their coding agents. The names here are placeholders until each person adds their own.</p>
  <div class="people">__PEOPLE__</div>
</div>
</body>
</html>
"""
