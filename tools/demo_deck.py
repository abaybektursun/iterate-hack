"""The talk as a slide deck: nine 16:9 slides, one figure each, very few words.

view.py serves page(...) at /demo (the stepped story of demo.py is at /demo/story) and FIGS at /demo/fig/<name>.
Each slide is a 1600 x 900 box scaled to fit the window. Keys: right arrow, Space or PageDown next; left arrow or
PageUp back; Home and End; t theme; f fullscreen; p print. A click on the right or left third of the window also
steps. The slide is in the address (/demo#finding), so Back works. Printing (p) gives one slide per page at 13.333 x
7.5 in, in the theme on screen.

Every number is read at build time from the module that holds it: the finish dial from finding_the_finish_dial.DATA,
the comparison with autoresearch from demo_facts.FACTS['auto_research_comparison'], the review rounds from
proof_review_cuts_waste.DATA, the idea tree's links from demo_ali_data.DATA (counted as demo_ali.py counts them), the
number of people from demo_facts.FACTS['people']; view.py passes the number of finding pages and the list of papers.
The photos are data URIs in demo_photos.py. Slides 4 and 7 show the pictures of architecture.py and of /demo/ali/slide2
in an iframe of FIGS: those pages with their header, words column and key hidden.
"""
import html
import re

import architecture
import demo
import demo_ali
import demo_ali_data
import demo_facts
import demo_photos
import finding_the_finish_dial
import proof_review_cuts_waste

HOOK = "36 hours to solve RSI"  # the opening line of the talk

# The title of each paper by its file name in view.PAPERS.
PAPER_TITLES = {"the-finish-dial.pdf": "The Finish Dial", "theories-on-trial.pdf": "Theories on Trial",
                "the-first-hundred-steps.pdf": "The First Hundred Steps", "no-early-warning.pdf": "No Early Warning"}
PAPER_AUTHOR = "The Invariant Swarm"

# What the deck shares with demo.py: the Archivo link and the theme script (?theme=, then the stored choice).
FONT = re.search(r'<link rel="preconnect".*?display=swap">', demo.TEMPLATE, re.S).group(0)
THEME_JS = re.search(r"<script>\n/\* The theme before the first paint.*?</script>", demo.TEMPLATE, re.S).group(0)
TOKENS = (':root {\n  color-scheme: light;\n  ' + demo.LIGHT + '\n}\n@media (prefers-color-scheme: dark) {\n'
          '  :root:not([data-theme="light"]) {\n    color-scheme: dark;\n    ' + demo.DARK + '\n  }\n}\n'
          ':root[data-theme="dark"] {\n  color-scheme: dark;\n  ' + demo.DARK + '\n}\n')

# The two logos of architecture.py (past.dev and Exa), read from its page.
LOGOS = {m.group(1): {"box": m.group(2), "body": m.group(3)} for m in
         re.finditer(r'  (\w+): \{ box: "([^"]+)", w: [\d.]+, h: [\d.]+, base: [\d.]+, tall: [\d.]+, body: `(.*?)` \}', architecture.PAGE)}
assert set(LOGOS) == {"past", "exa"}, f"architecture.py logos changed: {sorted(LOGOS)}"


def esc(s):
    return html.escape(str(s), quote=True)


def num(x):
    return f"{x:,}" if isinstance(x, int) else f"{x:g}"


def size_label(s):
    return ("−" + f"{-s:g}") if s < 0 else f"{s:g}"


# ---------- the embedded pictures ----------
FIG_THEME = (r"""<script>
(() => { const t = new URLSearchParams(location.search).get("theme"); if (t === "light" || t === "dark") document.documentElement.dataset.theme = t; })();
</script>""")


def embed(page, css):
    assert page.count("</head>") == 1
    return page.replace("</head>", f"<style>\n{css}\n</style>\n{FIG_THEME}\n</head>", 1)


FIGS = {
    # architecture.py follows only the system theme, so the deck's tokens are added for data-theme here.
    "harness": embed(architecture.PAGE, f""":root[data-theme="light"] {{ color-scheme: light; {demo.LIGHT} }}
:root[data-theme="dark"] {{ color-scheme: dark; {demo.DARK} }}
html, body {{ overflow: hidden; }}
.top, .foot, .side, .part.key, .part.tool {{ display: none !important; }}
.page {{ display: block !important; height: 100vh !important; min-height: 0 !important; max-width: none !important; padding: 0 !important; }}
.stage {{ height: 100vh; padding: 0 !important; }}"""),
    "tree": embed(demo_ali.PAGES["slide2"], """html, body { overflow: hidden; }
.top, .side, .foot { display: none !important; }
.page { padding: 0 !important; max-width: none !important; height: 100vh; }
#viewMap { display: none !important; }
#viewTree { display: block !important; }
.stage { height: 100vh; padding: 0 !important; justify-content: center; }
.stage svg { height: 100vh !important; max-height: 100vh !important; }
.grow .lk, .grow .nd { animation: none !important; }  /* the whole tree at once: the slide may be hidden while it loads, and it prints"""),
}


# ---------- the numbers ----------
DIAL = finding_the_finish_dial.DATA
CELLS = DIAL["cells"]
DIAL_N = DIAL["n"]
DIAL_ROWS = sorted((c for c in CELLS.values() if c["kind"] in ("top", "base")), key=lambda c: c["size"])
PEAK = max((c for c in DIAL_ROWS if c["kind"] == "top"), key=lambda c: c["right"])
assert PEAK is CELLS["1.5"], "the peak of the finish dial moved: the slide text names size 1.5"
RL = CELLS["rl"]

AUTO = demo_facts.FACTS["auto_research_comparison"]
assert AUTO["v"] and AUTO["n"], "demo_facts has no autoresearch comparison"
PEOPLE = demo_facts.FACTS["people"]["v"]

SKILL, PLAIN = proof_review_cuts_waste.SKILL, proof_review_cuts_waste.PLAIN
ROUNDS = proof_review_cuts_waste.DATA["rounds"]

# The idea tree's links, counted as demo_ali.py counts them: one per (item, parent), across when the clusters differ.
_NODES = {n["id"]: n for n in demo_ali_data.DATA["nodes"]}
LINKS = [(p, n["id"], _NODES[p]["b"] != n["b"]) for n in demo_ali_data.DATA["nodes"] for p in n["parents"]]
N_LINKS, N_CROSS = len(LINKS), sum(x for _, _, x in LINKS)


# ---------- the figures, drawn here as SVG ----------
def dial_svg():
    W, H, x0, x1, yt, yb = 1100, 470, 110, 1010, 50, 380
    lo_s, hi_s = DIAL_ROWS[0]["size"], DIAL_ROWS[-1]["size"]
    rights = [c["right"] for c in DIAL_ROWS] + [RL["right"]]
    lo, hi = (min(rights) - 20) // 20 * 20, -(-(max(rights) + 14) // 20) * 20
    X = lambda s: x0 + (s - lo_s) / (hi_s - lo_s) * (x1 - x0)
    Y = lambda r: yb - (r - lo) / (hi - lo) * (yb - yt)
    out = [f'<svg viewBox="0 0 {W} {H}" width="{W * 1.1:.0f}" height="{H * 1.1:.0f}" class="fig" role="img" aria-label="Right answers of {DIAL_N} by the size of the 8 directions">']
    for t in range(-(-lo // 40) * 40, hi + 1, 40):
        out.append(f'<line class="grid" x1="{x0 - 20}" x2="{x1 + 20}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/><text class="tick" x="{x0 - 30}" y="{Y(t) + 5:.1f}" text-anchor="end">{t}</text>')
    out.append(f'<text class="axis" x="{x0 - 30}" y="{yt - 22}" text-anchor="start">Right of {DIAL_N}</text>')
    yr = Y(RL["right"])
    out.append(f'<line class="rl" x1="{x0 - 20}" x2="{x1 + 20}" y1="{yr:.1f}" y2="{yr:.1f}"/>'
               f'<text class="lab" x="{x1 + 28}" y="{yr + 6:.1f}" text-anchor="start">RL <tspan class="v">{RL["right"]}</tspan></text>')
    out.append('<polyline class="curve" points="' + " ".join(f'{X(c["size"]):.1f},{Y(c["right"]):.1f}' for c in DIAL_ROWS) + '"/>')
    for c in DIAL_ROWS:
        x, y = X(c["size"]), Y(c["right"])
        peak = c is PEAK
        out.append(f'<circle class="{"pk" if peak else "pt"}" cx="{x:.1f}" cy="{y:.1f}" r="{8 if peak else 5.5}"/>')
        out.append(f'<text class="tick" x="{x:.1f}" y="{yb + 36}" text-anchor="middle">{size_label(c["size"])}</text>')
        if peak:
            out.append(f'<text class="pkv" x="{x:.1f}" y="{y + 46:.1f}" text-anchor="middle">{c["right"]}</text>')
        if c["kind"] == "base":
            out.append(f'<text class="lab" x="{x + 14:.1f}" y="{y + 38:.1f}" text-anchor="start">Base <tspan class="v">{c["right"]}</tspan></text>')
    out.append(f'<text class="axis" x="{(x0 + x1) / 2:.0f}" y="{yb + 76}" text-anchor="middle">Size of the 8 directions added to the base model</text>')
    return "".join(out) + "</svg>"


def bar(x, y0, w, h, cls, value, label=None):
    s = f'<rect class="{cls}" x="{x:.1f}" y="{y0 - h:.1f}" width="{w}" height="{h:.1f}"/>'
    if value is not None:
        s += f'<text class="bv{" on" if cls == "b1" else ""}" x="{x + w / 2:.1f}" y="{y0 - h - 14:.1f}" text-anchor="middle">{value}</text>'
    if label:
        s += f'<text class="bl" x="{x + w / 2:.1f}" y="{y0 + 28}" text-anchor="middle">{label}</text>'
    return s


def auto_svg():
    v, W, H, y0, top = AUTO["v"], 620, 470, 360, 270
    a, b = v["autoresearch"], v["nanolab"]
    out = [f'<svg viewBox="0 0 {W} {H}" width="{W * 1.12:.0f}" height="{H * 1.12:.0f}" class="fig" role="img" aria-label="Autoresearch and Nanolab on {AUTO["n"]} harder problems">']
    for gx, key, name in ((40, "right", f"Right of {AUTO['n']}"), (340, "tokens_per_problem", "Tokens per problem")):
        m = max(a[key], b[key])
        out.append(bar(gx, y0, 110, a[key] / m * top, "b0", num(a[key]), "Autoresearch"))
        out.append(bar(gx + 130, y0, 110, b[key] / m * top, "b1", num(b[key]), "Nanolab"))
        out.append(f'<text class="gl" x="{gx + 120}" y="{y0 + 72}" text-anchor="middle">{name}</text>')
    out.append(f'<line class="base" x1="20" x2="{W - 20}" y1="{y0}" y2="{y0}"/>')
    return "".join(out) + "</svg>"


def review_svg():
    W, H, y0, top = 620, 470, 360, 270
    m = SKILL["minutes"]
    out = [f'<svg viewBox="0 0 {W} {H}" width="{W * 1.12:.0f}" height="{H * 1.12:.0f}" class="fig" role="img" aria-label="Container minutes per batch over review rounds">']
    for i, (v, r) in enumerate(zip(m, ROUNDS)):
        out.append(bar(60 + i * 130, y0, 100, v / m[0] * top, "b1" if i == len(m) - 1 else "b0",
                       num(v) if i in (0, len(m) - 1) else None, r))
    yp = y0 - PLAIN["minutes"][-1] / m[0] * top
    out.append(f'<line class="rl" x1="40" x2="{W - 20}" y1="{yp:.1f}" y2="{yp:.1f}"/>'
               f'<text class="lab sm" x="{W - 20}" y="{yp - 12:.1f}" text-anchor="end">Plain instruction <tspan class="v">{num(PLAIN["minutes"][-1])}</tspan></text>')
    out.append(f'<line class="base" x1="40" x2="{W - 20}" y1="{y0}" y2="{y0}"/>')
    out.append(f'<text class="gl" x="{W / 2 + 10:.0f}" y="{y0 + 72}" text-anchor="middle">Container minutes per batch</text>')
    return "".join(out) + "</svg>"


def photo(uri, cls):
    if uri:
        return f'<div class="photo {cls}"><img src="{uri}" alt=""></div>'
    return f'<div class="photo {cls} empty"><span>Photo</span></div>'


def logo(name):
    L = LOGOS[name]
    return f'<svg class="logo logo-{name}" viewBox="{L["box"]}" aria-hidden="true">{L["body"]}</svg>'


def paper(name):
    lines = "".join(f'<i style="width:{w}%"></i>' for w in (92, 86, 90, 70, 88, 94, 62))
    return (f'<a class="sheet" href="/paper/{esc(name)}"><b>{esc(PAPER_TITLES[name])}</b>'
            f'<span>{esc(PAPER_AUTHOR)}</span><div class="lines">{lines}</div></a>')


def slides(n_findings, papers):
    missing = [p for p in papers if p not in PAPER_TITLES]
    assert not missing, f"demo_deck.PAPER_TITLES has no title for {missing}"
    return [
        ("hook", f'<div class="mid"><h1 class="big">{esc(HOOK)}</h1><p class="sub faint">Team Invariant</p></div>'),
        ("question", f'<div class="mid"><p class="sub top">{PEOPLE} independent researchers, limited tokens, compute and people</p>'
                     f'<h1 class="big">Hill climbing is not useful if we don\'t understand it</h1></div>'),
        ("tea", f'<div class="mid"><p class="sub">Our solution</p>{photo(demo_photos.TEA, "tea")}<p class="sub">Gong fu tea and meditation</p></div>'),
        ("harness", '<div class="head"><h2>Nanolab</h2><p class="sub">A hill climbing engine and an interpretability engine in one harness</p></div>'
                    '<iframe class="fig-frame harness" data-fig="harness" title="The harness" tabindex="-1"></iframe>'
                    f'<div class="tools"><span>Search {logo("exa")}</span><span>Memory {logo("past")}</span><span>GPUs <b class="word">Modal</b></span></div>'),
        ("finding", '<div class="mid"><h2 class="title">8 directions in the weights hold most of RL\'s gain</h2>'
                    f'{dial_svg()}<p class="sub">Why: they make the model finish its answer, cut-off answers '
                    f'{CELLS["0"]["cut"]} → {CELLS["1.5"]["cut"]}</p></div><p class="corner">{n_findings} findings</p>'),
        ("proof", '<div class="head"><h2>Proof</h2></div><div class="pair">'
                  f'<figure><figcaption>Against autoresearch</figcaption>{auto_svg()}</figure>'
                  f'<figure><figcaption>Its own review cuts waste</figcaption>{review_svg()}</figure></div>'),
        ("ideas", f'<div class="head"><h2>Ideas converge</h2><p class="sub">{N_CROSS} of {N_LINKS} links join two different clusters of ideas</p></div>'
                  '<iframe class="fig-frame tree" data-fig="tree" title="The idea tree" tabindex="-1"></iframe>'),
        ("papers", f'<div class="mid"><h2 class="title">{len(papers)} papers, written by the swarm</h2>'
                   f'<div class="sheets">{"".join(paper(p) for p in papers)}</div></div>'),
        ("close", f'<div class="mid">{photo(demo_photos.MEDITATE, "meditate")}<p class="end">Also our solution to AI psychosis</p>'
                  '<p class="sub faint">monitor.invariant.team</p></div>'),
    ]


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Talk</title>
__FONT__
__THEME_JS__
<style>
__TOKENS__
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { margin: 0; height: 100%; overflow: hidden; background: var(--paper); }
body {
  color: var(--ink); font: 400 15px/1.4 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased; user-select: none;
}
a { color: inherit; text-decoration: none; }
p, h1, h2, figure { margin: 0; }

/* One slide is a 1600 x 900 box, scaled to the window (--s, set from the script). */
.slide { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; background: var(--paper);
  opacity: 0; visibility: hidden; transition: opacity .35s ease, visibility 0s linear .35s; }
.slide.on { opacity: 1; visibility: visible; transition: opacity .35s ease; }
.box { position: relative; flex: none; width: 1600px; height: 900px; transform: scale(var(--s, 1)); }
@media (prefers-reduced-motion: reduce) { .slide, .slide.on { transition: none; } }

.mid { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 30px; text-align: center; padding: 0 140px; }
.big { font-weight: 300; font-size: 76px; line-height: 1.12; letter-spacing: -.012em; max-width: 1240px; }
.sub { font-size: 24px; font-weight: 500; color: var(--mute); }
.faint { color: var(--faint); font-weight: 500; }
.top { margin-bottom: 8px; }
.title { font-weight: 300; font-size: 54px; line-height: 1.15; letter-spacing: -.008em; }
.end { font-weight: 300; font-size: 48px; margin-top: 6px; }
.head { position: absolute; left: 96px; top: 72px; z-index: 1; }
.head h2 { font-weight: 300; font-size: 54px; line-height: 1.1; }
.head .sub { margin-top: 12px; }
.corner { position: absolute; right: 96px; bottom: 64px; font-size: 22px; font-weight: 500; color: var(--faint); }

.photo { border-radius: 2px; overflow: hidden; }
.photo img { display: block; width: 100%; height: 100%; object-fit: cover; }
.photo.tea { width: 720px; height: 540px; }
.photo.meditate { width: 640px; height: 480px; }
.photo.empty { border: 1px dashed var(--faint); opacity: .7; display: flex; align-items: center; justify-content: center; }
.photo.empty span { font-size: 22px; font-weight: 500; color: var(--faint); }

.fig-frame { position: absolute; border: 0; background: var(--paper); pointer-events: none; color-scheme: normal; }
.fig-frame.harness { left: 250px; top: 215px; width: 1100px; height: 600px; }
.fig-frame.tree { left: 220px; top: 190px; width: 1160px; height: 680px; }
.tools { position: absolute; left: 0; right: 0; bottom: 56px; display: flex; justify-content: center; gap: 72px; font-size: 22px; font-weight: 560; color: var(--mute); }
.tools span { display: inline-flex; align-items: center; gap: 14px; }
.logo { height: 24px; width: auto; fill: var(--ink); }
.logo-exa { height: 22px; }
.tools .word { font-size: 25px; font-weight: 640; color: var(--ink); }  /* a sponsor with no logo in architecture.py */

/* the figures drawn here */
.fig { display: block; overflow: visible; font-family: inherit; }
.fig text { fill: var(--ink); font-variant-numeric: tabular-nums; }
.fig .grid { stroke: var(--rule); stroke-width: 1; }
.fig .tick { font-size: 18px; fill: var(--faint); }
.fig .axis { font-size: 18px; font-weight: 500; fill: var(--mute); }
.fig .rl { stroke: var(--mute); stroke-width: 1.5; stroke-dasharray: 2 6; stroke-linecap: round; }
.fig .lab { font-size: 22px; font-weight: 560; fill: var(--mute); }
.fig .lab.sm { font-size: 18px; }
.fig .v { font-weight: 400; fill: var(--ink); }
.fig .curve { fill: none; stroke: var(--ink); stroke-width: 1.6; stroke-linejoin: round; opacity: .75; }
.fig .pt { fill: var(--ink); }
.fig .pk { fill: var(--blue); stroke: var(--paper); stroke-width: 3; }
.fig .pkv { font-size: 30px; font-weight: 500; fill: var(--blue); }
.fig .b0 { fill: var(--fbar1); }
.fig .b1 { fill: var(--blue); }
.fig .bv { font-size: 26px; font-weight: 400; }
.fig .bv.on { fill: var(--blue); font-weight: 500; }
.fig .bl { font-size: 17px; font-weight: 500; fill: var(--mute); }
.fig .gl { font-size: 20px; font-weight: 600; fill: var(--ink); }
.fig .base { stroke: var(--faint); stroke-width: 1; }

.pair { position: absolute; left: 0; right: 0; top: 205px; display: flex; justify-content: center; gap: 90px; }
.pair figcaption { font-size: 26px; font-weight: 560; margin: 0 0 18px 20px; }

.sheets { display: flex; gap: 80px; margin-top: 30px; }
/* a paper is white in both themes: the sheet carries the light values of these four tokens */
.sheet { --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --rule: #d3d9de; color: var(--ink);
  width: 330px; height: 427px; background: var(--sheet); border: 1px solid var(--rule); padding: 118px 34px 0; text-align: left; display: flex; flex-direction: column; gap: 10px; }
.sheet b { font-size: 26px; font-weight: 560; line-height: 1.2; }
.sheet span { font-size: 16px; font-weight: 500; color: var(--mute); }
.sheet .lines { margin-top: 26px; display: flex; flex-direction: column; gap: 13px; }
.sheet .lines i { display: block; height: 2px; background: var(--rule); }

.count { position: fixed; left: 18px; bottom: 12px; font-size: 13px; color: var(--faint); opacity: .7; z-index: 2; }

@page { size: 13.333in 7.5in; margin: 0; }
@media print {
  html, body { height: auto; overflow: visible; }
  .count { display: none; }
  .slide { position: relative; inset: auto; display: block; width: 13.333in; height: 7.5in; overflow: hidden;
    opacity: 1; visibility: visible; transition: none; break-after: page; page-break-after: always; }
  .slide:last-child { break-after: auto; page-break-after: auto; }
  .box { transform: scale(.8) !important; transform-origin: 0 0; }
}
</style>
</head>
<body>
<main class="deck" id="deck">
__SLIDES__
</main>
<div class="count" id="count" aria-live="polite"></div>
<script>
const SLIDES = [...document.querySelectorAll(".slide")], IDS = SLIDES.map(s => s.id);
let cur = -1;
const themeNow = () => document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

/* the box fills the window at 16:9 */
function fit() { document.documentElement.style.setProperty("--s", Math.min(innerWidth / 1600, innerHeight / 900)); }
addEventListener("resize", fit); fit();

/* the embedded pictures get the deck's theme, at load and on every change */
const frames = [...document.querySelectorAll("iframe[data-fig]")];
const syncFrame = f => { const d = f.contentDocument; if (d && d.documentElement) d.documentElement.dataset.theme = themeNow(); };
frames.forEach(f => { f.addEventListener("load", () => syncFrame(f)); f.src = `/demo/fig/${f.dataset.fig}?theme=${themeNow()}`; });
function toggleTheme() {
  const t = themeNow() === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = t;
  try { localStorage.setItem("demo-theme", t); } catch (e) { /* storage blocked: the choice lasts until the page closes */ }
  frames.forEach(syncFrame);
}

function show(i, push) {
  i = Math.max(0, Math.min(SLIDES.length - 1, i));
  if (i === cur) return;
  if (cur >= 0) SLIDES[cur].classList.remove("on");
  SLIDES[i].classList.add("on"); cur = i;
  SLIDES.forEach((s, k) => s.setAttribute("aria-hidden", k === i ? "false" : "true"));
  document.getElementById("count").textContent = `${i + 1} / ${SLIDES.length}`;
  const h = "#" + IDS[i];
  if (push && h !== location.hash) history.pushState(null, "", h);
}
const fromHash = () => { const k = IDS.indexOf(decodeURIComponent(location.hash.slice(1))); show(k < 0 ? 0 : k, false); };
addEventListener("popstate", fromHash);
addEventListener("hashchange", fromHash);

document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key;
  if (k === "ArrowRight" || k === " " || k === "PageDown") { e.preventDefault(); show(cur + 1, true); }
  else if (k === "ArrowLeft" || k === "PageUp") { e.preventDefault(); show(cur - 1, true); }
  else if (k === "Home") { e.preventDefault(); show(0, true); }
  else if (k === "End") { e.preventDefault(); show(SLIDES.length - 1, true); }
  else if ((k === "t" || k === "T") && !e.repeat) { e.preventDefault(); toggleTheme(); }
  else if ((k === "f" || k === "F") && !e.repeat) { e.preventDefault(); if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen(); }
  else if ((k === "p" || k === "P") && !e.repeat) { e.preventDefault(); window.print(); }
});
document.addEventListener("click", e => {
  if (e.target.closest("a")) return;  // the paper sheets open their PDF
  const x = e.clientX / innerWidth;
  if (x > 2 / 3) show(cur + 1, true); else if (x < 1 / 3) show(cur - 1, true);
});
fromHash();
</script>
</body>
</html>
"""


def page(n_findings, papers):
    """The deck, with the number of finding pages and the paper file names (view.FINDINGS, view.PAPERS) written in."""
    body = "\n".join(f'<section class="slide" id="{sid}" aria-label="Slide {i + 1}"><div class="box">{inner}</div></section>'
                     for i, (sid, inner) in enumerate(slides(n_findings, list(papers))))
    return (TEMPLATE.replace("__FONT__", FONT).replace("__THEME_JS__", THEME_JS).replace("__TOKENS__", TOKENS)
            .replace("__SLIDES__", body))
