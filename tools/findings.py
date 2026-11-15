"""The findings page of the team site. The tab Proof (/proof) is the same page for the experiments that test the team's
method itself; PROOF at the end holds its differences.

view.py serves PAGE at /findings, after writing into it the icons (__ICONS__) and the rows (__ROWS__): entry(slug,
module) of every tools/finding_<slug>.py, with each mark that names a board score read from that score row by
resolve(). The page reads nothing after it loads, so its picture is drawn at once. view.py also adds tools/sitekit.py
(terms defined on click).

The first view is the research question and one picture of it: a glass rail from 40 % to 100 % on MATH-500, on which
the base model's scores without reward are drawn in one after another (Base, Base + cue, restart, vote over 4 samples,
vote after restart) against RL's (one sample, then the same vote and restarts). Each mark opens the finding it comes
from. Under the rail, the points by which RL still leads with the same vote and restarts, counted once to that value,
and one sentence on what remains. The whole entrance takes about 2 s. The marks come from the `steps` of the entries
below: numbers read from each finding module's own values, or a score row of the board (the rows tools/climb.py reads)
named by its result id and configuration. No number is typed here.

Under the picture, the findings in groups that follow the story (GROUPS), each group headed by its question. A row
holds the finding's effect size as one figure with its unit ("66 % of the gap", "+6.1 points") and a short tag for the
set it was measured on, its TITLE, its LINE and its icon, and opens /finding/<slug>. A finding that TABLE does not name
goes into the last group, "New", so a new page appears here without an edit. The looks are those of
tools/architecture.py (.claude/skills/site-ui/SKILL.md): its tokens, one light from the upper left, a slow sway, and
one still frame with reduced motion.

One finding, one file: a module tools/finding_<slug>.py draws its own icon. It defines ICON, the source of a
JavaScript arrow function `(kit, t, tilt) => "<svg markup>"`. view.py replaces __ICONS__ below with the object literal
`{"<slug>": <ICON source>, ...}` when it builds the page, so the functions are plain page code. The page calls an icon
about 30 times a second while its row is on screen. `kit` is the object of that name below (the projection, a glass
slab, a lit face, a line, the theme tokens), `t` is the time in seconds, and `tilt` is the lean toward the mouse as
[x, y] from -1 to 1. The kit's view already sways and leans, so most icons use only `t`, for their own slow motion.
The icon's space is 112 by 80 units around the centre (56, 36). A module without ICON gets a plain glass slab.
"""


NO_REWARD, ANSWERS, WEIGHTS = "What needs no reward?", "How does RL change the answers?", "Where does RL's change sit in the weights?"
GROUPS = [NO_REWARD, ANSWERS, WEIGHTS, "New"]


def signed(x, digits=1):
    """A signed number with a true minus sign: "+37.2", "−1.2"."""
    return f"{x:+.{digits}f}".replace("-", "−")


def points(before, after, n):
    """The difference of two counts of n as signed points with one decimal: "+37.2"."""
    return signed(100 * (after - before) / n)


def step(name, model, right, n, source):
    """One mark on the rail: right answers of n on MATH-500, by the base or the RL model, and where the count is."""
    return {"name": name, "model": model, "right": right, "n": n, "source": source}


def board_step(name, model, result, config):
    """One mark whose count view.py reads from the board's score row of this result, model and configuration on MATH-500."""
    return {"name": name, "model": model, "find": {"result": result, "benchmark": "MATH-500", "model": model, "config": config},
            "source": f"board {result}"}


# slug -> its group, its figure [number, unit, tag of the set] and its marks on the rail, each read from the module m.
# The order is the order on the page. The rail shows MATH-500 at T 1.0 / top-p 1.0. Board result-e78dfe recounted the
# climb from the per-problem rows: the honest best base score is the vote after restart (result-5d032f), not the tie rule
# chosen on the same problems.
AFTER_RESTART = "T 1.0 / top-p 1.0, vote over 4 samples after restart"
TABLE = {
    "opening-cue": {
        "group": NO_REWARD,
        "figure": lambda m: [points(m.PLAIN, m.CUE, m.N), "points", "MATH-500, over Base"],
        "steps": lambda m: [step("Base", "base", m.PLAIN, m.N, m.DATA["artifact"]),
                            step("Base + cue", "base", m.CUE, m.N, m.DATA["artifact"]),
                            step("RL, one sample", "rl", m.RL, m.N, m.DATA["artifact"])]},
    "base-opens-itself": {
        "group": NO_REWARD,
        "figure": lambda m: [signed(m.DATA["diff_cue"][0]), "points", "MATH-500, the base's own opening with Okay against the prefilled cue"]},
    "restart-on-cap": {
        "group": NO_REWARD,
        "figure": lambda m: [signed(m.GAIN), "points", "MATH-500, T 0.6"],
        "steps": lambda m: [step("Base + cue, restart", "base", m.T10["restart"], m.D["n"], m.T10["artifact"])]},
    "vote-over-four": {
        "group": NO_REWARD,
        "figure": lambda m: [signed(m.BASE["gain"]), "points", "MATH-500, Base + cue"],
        "steps": lambda m: [step("Vote over 4 samples", "base", m.BASE["vote"], m.N, m.DATA["artifact"]),
                            board_step("Vote over 4 samples, restart", "base", "result-5d032f", "cue, " + AFTER_RESTART),
                            board_step("RL, vote over 4 samples, restart", "rl", "result-5d032f", "plain, " + AFTER_RESTART)]},
    "equal-token-frontier": {
        "group": NO_REWARD,
        "figure": lambda m: [signed(m._best["gap"][0]), "points", f"MATH-500, against one RL sample, at {m._best['multiple']:.1f} times the tokens"]},
    "cue-on-code": {
        "group": NO_REWARD,
        "figure": lambda m: [points(m.ST[0]["passed"], m.ST[2]["passed"], m.N), "points", f"{m.N} code problems"]},
    "imitation-beats-rl": {
        "group": NO_REWARD,
        "figure": lambda m: [signed(m.DATA["diff"]["hard328"]["vote"][0]), "points", "328 harder problems, Think-SFT over RL"]},
    "where-the-gap-goes": {
        "group": ANSWERS,
        "figure": lambda m: [f"{m.pc(m._RL['parts']['reliability'][1])} %", "of the gap",
                             f"MATH-500; a random weight change gives {m.pc(m._NULL['parts']['reliability'][1])} %"]},
    "rl-reliability": {
        "group": ANSWERS,
        "figure": lambda m: [f"{m.SOME} %", "of the gain", "MATH-500, 4 samples each of Base + cue and RL"]},
    "rl-edge-comes-early": {
        "group": ANSWERS,
        "figure": lambda m: [f"{m.CLOSED_U} to {m.CLOSED} %", "of the gap", "MATH-500, base finishes RL's answers"]},
    "rl-learns-the-opening-first": {
        "group": ANSWERS,
        "figure": lambda m: [f"{m.DATA['okay'][2]} of {m.DATA['n']}", "answers",
                             f"MATH-500, open with 'Okay' after 100 RL steps; Base {m.DATA['okay'][0]}"]},
    "rl-wait-habit": {
        "group": ANSWERS,
        "figure": lambda m: [m.PUSH_POINTS, "points", "MATH-500, at RL's rate of Wait"]},
    "one-difficulty-axis": {
        "group": ANSWERS,
        "figure": lambda m: [signed(m.DATA["diff"]["excess_mean"], 2), "problems", "MATH-500, mean of 618 pairs of methods"]},
    "a-quarter-of-rl": {
        "group": WEIGHTS,
        "figure": lambda m: [f"{m.Q_M} %", "of the gain", "MATH-500, a = 0.25"]},
    "eight-directions": {
        "group": WEIGHTS,
        "figure": lambda m: [signed(m.DATA["vs_cue_hard"]["points"]), "points",
                             f"328 harder problems, over Base + cue; 8 random directions {signed(m.DATA['random_vs_cue_hard']['points'])}"]},
    "rl-every-neuron": {
        "group": WEIGHTS,
        "figure": lambda m: [m.pct(m.mean(m.ONE["best"])), "of RL's effect", f"next-word predictions, RL's best {m.ONE['share']:g} % of neurons copied"]},
    "neurons-you-can-describe": {
        "group": WEIGHTS,
        "figure": lambda m: [f"{100 * m.DATA['sets']['selected']['mean_accuracy']:.1f} %", "of snippets sorted right",
                             f"30 neurons, blind reader; chance is {round(100 * m.DATA['chance'])} %"]},
    "loop-neurons": {
        "group": WEIGHTS,
        "figure": lambda m: [f"{m.DATA['states'][0]['loops']} → {m.DATA['states'][1]['loops']}", "loops", f"of {m.DATA['n']} answers, MATH-500, T 0.6"]},
}


def entry(slug, m):
    """What the page says of one finding: slug, title, line, group, rank (the order on the page), figure and steps."""
    row = TABLE.get(slug, {})
    return {"slug": slug, "title": m.TITLE, "line": m.LINE, "group": row.get("group", "New"),
            "rank": list(TABLE).index(slug) if slug in TABLE else len(TABLE),
            "figure": row["figure"](m) if "figure" in row else None,
            "steps": row["steps"](m) if "steps" in row else []}


def resolve(rows, scores):
    """The rows with the count of each board mark read from its one score row (scores: the board's rows of pk "scores")."""
    def one(s):
        if "find" not in s:
            return s
        found = [r for r in scores if all(r.get(k) == v for k, v in s["find"].items())]
        assert len(found) == 1, f"{len(found)} score rows for {s['find']}"
        return {"name": s["name"], "model": s["model"], "right": int(found[0]["right"]), "n": int(found[0]["n"]), "source": s["source"]}
    return [{**r, "steps": [one(s) for s in r["steps"]]} for r in rows]


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Findings</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens and the light of architecture.py. Dark is the hero: lit glass in a dark room. Light is the same object as
   white porcelain on a cool grey table, with a cast shadow in place of the glow. The light comes from the upper left. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --core: var(--blue);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --core: #f6f9ff;
  }
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
a { color: inherit; }
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.page { max-width: 1840px; margin: 0 auto; padding: 20px 40px 72px; }
.top { display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }
.say { margin: clamp(28px, 7vh, 76px) 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; }

/* The first view: the question, the rail, what remains */
.ask { margin: clamp(26px, 6vh, 64px) 0 0; font-size: clamp(24px, 2.1vw, 38px); line-height: 1.16; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 31ch; min-height: 2.32em; }
.ask b { font-weight: 600; white-space: nowrap; }
.fig { position: relative; margin-top: clamp(24px, 5vh, 52px); }
#rail { display: block; width: 100%; overflow: visible; }
#rail .hit { fill: transparent; cursor: pointer; pointer-events: all; }
#rail * { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#rbody) var(--sheet); stroke: url(#rrim) var(--ink); stroke-width: 1.4; }
.tick { stroke: var(--faint); stroke-width: 1; opacity: .55; }
.tlab { fill: var(--faint); font-size: 12px; font-family: inherit; font-stretch: 104%; }
.fill { fill: none; stroke: var(--core); stroke-linecap: round; }
.glow { fill: none; stroke: var(--blue); stroke-linecap: round; opacity: calc(var(--bloom) * .22); }
.rshade { fill: var(--ink); opacity: calc(var(--shadow) * .12); }
.left { stroke: var(--ink); stroke-width: 1.2; stroke-dasharray: 2 5; stroke-linecap: round; opacity: .5; fill: none; }
.bead { fill: var(--core); }
.halo { fill: var(--blue); opacity: calc(var(--bloom) * .26); }
.ring { fill: var(--paper); stroke: var(--ink); stroke-width: 1.8; }
.lead { fill: none; stroke: var(--faint); stroke-width: 1; opacity: .7; transition: stroke .15s ease, opacity .15s ease; }
.lead.on { stroke: var(--blue); opacity: 1; }
.labels a { position: absolute; display: flex; flex-direction: column; text-align: center; padding: 0 3px; text-decoration: none; opacity: 0; transition: opacity .6s ease; border-radius: 4px; }
.labels a.base { justify-content: flex-end; }
.labels a.in { opacity: 1; }
.lname { color: var(--mute); font-size: 13px; line-height: 1.2; font-weight: 520; font-stretch: 104%; transition: color .15s ease; }
.lval { font-size: 22px; line-height: 1.2; font-weight: 420; letter-spacing: -.01em; transition: color .15s ease; }
.labels a:hover .lval, .labels a:hover .lname, .labels a.on .lval, .labels a.on .lname { color: var(--blue); }
.key { display: flex; flex-wrap: wrap; gap: 6px 28px; margin-top: 14px; color: var(--faint); font-size: 13px; }
.key span { white-space: nowrap; }
.key #setting { margin-left: auto; white-space: normal; }
.key i { display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 8px; vertical-align: -1px; }
.key .kb { background: var(--core); box-shadow: 0 0 0 3px color-mix(in srgb, var(--blue) calc(var(--bloom) * 26%), transparent); }
.key .kr { border: 2px solid var(--ink); background: var(--paper); }
.remain { display: grid; grid-template-columns: auto minmax(0, 1fr); align-items: start; gap: 0 32px; margin-top: clamp(26px, 5vh, 48px); }
.gap { margin: 0; white-space: nowrap; line-height: 1; transition: opacity .25s ease; }
.gap.wait { opacity: 0; }
.gap b { font-size: clamp(52px, 5.4vw, 88px); font-weight: 300; letter-spacing: -.035em; font-stretch: 100%; }
.gap > span { display: block; margin-top: 8px; color: var(--mute); font-size: 14px; font-weight: 520; }
.rest { grid-column: 2; grid-row: 1 / span 2; margin: 6px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 46ch; transition: opacity .6s ease; }
.rest.wait { opacity: 0; }
.acts { grid-column: 1; display: flex; gap: 22px; margin-top: 16px; font-size: 13px; color: var(--mute); white-space: nowrap; }
.acts summary { cursor: pointer; list-style: none; }
.acts summary::-webkit-details-marker { display: none; }
.acts button:hover, .acts summary:hover { color: var(--ink); }
.acts button:focus-visible, .acts summary:focus-visible { outline-offset: 4px; }
ul.src { list-style: none; margin: 10px 0 0; padding: 0; color: var(--mute); font-size: 13px; columns: 2 380px; column-gap: 48px; }
ul.src li { padding: 5px 0; border-top: 1px solid var(--rule); break-inside: avoid; overflow-wrap: anywhere; }

/* The findings, in groups that follow the question */
.groups { margin-top: clamp(64px, 12vh, 132px); }
.groups.flat { margin-top: clamp(26px, 5vh, 52px); }
.group { display: grid; grid-template-columns: minmax(190px, 17%) minmax(0, 1fr); gap: 0 40px; border-top: 1px solid var(--rule); padding-top: 6px; margin-top: 44px; }
.group:first-child { margin-top: 0; }
.group h2 { margin: 18px 0 0; max-width: 15ch; font-size: 19px; line-height: 1.22; font-weight: 400; font-stretch: 102%; letter-spacing: -.004em; }
.rows { list-style: none; margin: 0; padding: 0; }
.row { display: grid; grid-template-columns: 250px minmax(0, 58ch) 92px; justify-content: start; gap: 0 36px; align-items: baseline; padding: 16px 0 18px; text-decoration: none; }
.row.nofig { grid-template-columns: minmax(0, 58ch) 92px; }
.row.nofig .fig2 { display: none; }
.row:focus-visible { outline-offset: 2px; border-radius: 4px; }
.num { display: block; line-height: 1.05; }
.num b { font-size: 31px; font-weight: 300; letter-spacing: -.02em; white-space: nowrap; font-stretch: 100%; }
.num .u { margin-left: 5px; color: var(--mute); font-size: 15px; font-weight: 460; white-space: nowrap; }
.unit { display: block; margin-top: 7px; color: var(--faint); font-size: 12.5px; line-height: 1.32; }
.title { margin: 0; font-size: 17.5px; line-height: 1.22; font-weight: 600; font-stretch: 106%; letter-spacing: .004em; transition: color .15s ease; }
.row:hover .title { color: var(--blue); }
.line { margin: 6px 0 0; color: var(--mute); font-size: 14.5px; line-height: 1.42; }
.icon { display: block; width: 92px; height: 66px; overflow: visible; align-self: center; }
.flat .group { display: block; border-top: 0; }
.flat .group h2 { display: none; }

/* The icon: glass, its light and its lines */
.icon * { pointer-events: none; }
.body { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: .6; stroke-linejoin: round; }
.face { fill: url(#body) var(--sheet); }
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1; stroke-linejoin: round; }
.plain { fill: var(--ink); }
.lit { fill: var(--core); }
.icon .halo { fill: var(--blue); opacity: calc(var(--bloom) * .28); }

@keyframes fade { from { opacity: 0; } }
.rows li { animation: fade .7s calc(var(--i, 0) * 60ms) both; }
@media (max-width: 900px) {
  .page { padding: 16px 16px 48px; }
  .top { gap: 13px; padding-bottom: 12px; }
  .name { font-stretch: 112%; margin-right: 0; }
  .ask { margin-top: 22px; font-size: 23px; min-height: 0; }
  .fig { margin-top: 22px; }
  .lname { font-size: 12px; line-height: 1.15; }
  .lval { font-size: 15px; font-weight: 520; }
  .key { font-size: 12px; justify-content: flex-start; }
  .remain { grid-template-columns: minmax(0, 1fr); gap: 12px; }
  .rest { font-size: 17px; grid-column: 1; grid-row: auto; }
  .acts { grid-column: 1; }
  .groups { margin-top: 56px; }
  .group { display: block; margin-top: 40px; }
  .group h2 { margin: 16px 0 2px; }
  .row { grid-template-columns: minmax(0, 1fr) 72px; gap: 0 14px; padding: 16px 0 18px; }
  .row .fig2 { grid-column: 1; grid-row: 1; }
  .row .icon { grid-column: 2; grid-row: 1; width: 72px; height: 52px; }
  .row.nofig { grid-template-columns: minmax(0, 1fr) 72px; }
  .row.nofig .text { grid-column: 1; grid-row: 1; margin-top: 0; }
  .row .text { grid-column: 1 / -1; margin-top: 10px; }
  .num b { font-size: 27px; }
  .group h2 { max-width: none; font-size: 18px; }
}
@media (prefers-reduced-motion: reduce) {
  .rows li { animation: none; }
  .labels a, .rest, .lead, .top a, .title, .lname, .lval { transition: none; }
}
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
  <radialGradient id="body" cx=".3" cy=".16" r="1.05"><stop offset="0" style="stop-color:var(--glass-hi)"/><stop offset=".5" style="stop-color:var(--glass)"/><stop offset="1" style="stop-color:var(--glass-lo)"/></radialGradient>
  <linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1"><stop offset="0" style="stop-color:var(--rim-a)"/><stop offset=".56" style="stop-color:var(--rim-b)"/><stop offset="1" style="stop-color:var(--rim-c)"/></linearGradient>
  <radialGradient id="atmo"><stop offset=".3" style="stop-color:var(--blue);stop-opacity:.2"/><stop offset=".66" style="stop-color:var(--blue);stop-opacity:.06"/><stop offset="1" style="stop-color:var(--blue);stop-opacity:0"/></radialGradient>
  <radialGradient id="shade"><stop offset=".5" style="stop-color:var(--ink);stop-opacity:.2"/><stop offset="1" style="stop-color:var(--ink);stop-opacity:0"/></radialGradient>
  <radialGradient id="spec"><stop offset="0" style="stop-color:#fff;stop-opacity:.2"/><stop offset="1" style="stop-color:#fff;stop-opacity:0"/></radialGradient>
  <radialGradient id="rbody" cx=".26" cy="0" r="1.2"><stop offset="0" style="stop-color:var(--glass-hi)"/><stop offset=".5" style="stop-color:var(--glass)"/><stop offset="1" style="stop-color:var(--glass-lo)"/></radialGradient>
  <linearGradient id="rrim" x1="0" y1="0" x2="1" y2=".04"><stop offset="0" style="stop-color:var(--rim-a)"/><stop offset=".5" style="stop-color:var(--rim-b)"/><stop offset="1" style="stop-color:var(--rim-c)"/></linearGradient>
  <filter id="soft" x="-10%" y="-200%" width="120%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>
</defs></svg>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings" aria-current="page">Findings</a>
  </header>
  <p class="say" id="say" hidden></p>
  <section class="story" id="story" data-terms hidden>
    <p class="ask" id="ask"></p>
    <div class="fig" id="fig">
      <svg id="rail" aria-hidden="true"></svg>
      <div class="labels" id="labels"></div>
    </div>
    <div class="key"><span><i class="kb"></i>Base or Base + cue, no reward</span><span><i class="kr"></i>RL</span><span id="setting"></span></div>
    <div class="remain">
      <p class="gap wait" id="gapbox"><b id="gap"></b><span id="gapunit"></span></p>
      <div class="acts"><button id="replay" type="button">Replay</button><details class="src" id="srcbox"><summary>Where each number comes from</summary></details></div>
      <p class="rest wait" id="rest"></p>
    </div>
    <ul class="src" id="src" hidden></ul>
  </section>
  <div class="groups" id="groups"></div>
</div>
<script>
const KIND = "findings";
const $ = id => document.getElementById(id);
const S = { key: "", tiles: [], last: 0 };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1), h = n => n.toFixed(2);
const pc = s => (100 * s.right / s.n).toFixed(1) + "\u00a0%";
const nb = s => esc(s).replace(/(\d) (%|points)/g, "$1\u00a0$2");  // a number never breaks from its unit

/* Geometry of an icon: it lives in a small 3D space around one centre (x right, y down, z toward the viewer), as in
   architecture.py. Its ground plane lies back by TILT degrees, so it is seen from slightly above: u runs to the right,
   v toward the viewer and w up out of the plane. The view sways by a few degrees and leans toward the mouse. */
const RAD = Math.PI / 180, TILT = 58, PC = Math.cos(TILT * RAD), PS = Math.sin(TILT * RAD);
const G = { w: 112, h: 80, cx: 56, cy: 36, D: 360, yaw: -8, deep: 34 };  // the icon's box and centre, the distance of the eye, the rest angle, half its depth
const V = { c1: 1, s1: 0, c2: 1, s2: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
const world = (u, v, w) => [u, v * PC - w * PS, v * PS + w * PC];
function proj(p) {  // to the screen: [x, y, scale, depth]
  const x = p[0] * V.c1 + p[2] * V.s1, z1 = p[2] * V.c1 - p[0] * V.s1;
  const y = p[1] * V.c2 - z1 * V.s2, z = z1 * V.c2 + p[1] * V.s2, k = G.D / (G.D - z);
  return [G.cx + x * k, G.cy + y * k, k, z];
}
function outline(a, b, r) {  // a rounded rectangle in the ground plane, clockwise from the far right corner
  const pts = [], n = 4;
  [[1, -1, -90], [1, 1, 0], [-1, 1, 90], [-1, -1, 180]].forEach(([su, sv, a0]) => {
    for (let i = 0; i <= n; i++) {
      const q = (a0 + 90 * i / n) * RAD;
      pts.push([su * (a - r) + r * Math.cos(q), sv * (b - r) + r * Math.sin(q)]);
    }
  });
  return pts;
}
function hull(p) {  // the silhouette of a convex body is the convex hull of its projected points
  p = [...p].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const turn = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const half = list => {
    const out = [];
    for (const q of list) { while (out.length > 1 && turn(out[out.length - 2], out[out.length - 1], q) <= 0) out.pop(); out.push(q); }
    out.pop();
    return out;
  };
  return [...half(p), ...half(p.reverse())];
}
const path = p => "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
function seg(p, q, w) {  // a straight line from p to q whose width follows the depth of its ends: w is its width at scale 1
  const dx = q[0] - p[0], dy = q[1] - p[1], d = Math.hypot(dx, dy) || 1, nx = -dy / d, ny = dx / d, a = w * p[2] / 2, b = w * q[2] / 2;
  return `M${h(p[0] + nx * a)} ${h(p[1] + ny * a)}L${h(q[0] + nx * b)} ${h(q[1] + ny * b)}L${h(q[0] - nx * b)} ${h(q[1] - ny * b)}L${h(p[0] - nx * a)} ${h(p[1] - ny * a)}Z`;
}

/* The kit an icon draws with. Every function returns SVG markup, lit by the one light of the page.
   at(u, v, w): a point of the icon's space on the screen, as [x, y, scale, depth].
   slab(a, b, th): a glass slab of half width a, half depth b and thickness th around the centre; its top is at w = th / 2.
   face(points): a lit glass face through points from at().
   line(p, q, w, tone, alpha): a line between two points from at(). "plain" is ink, fainter at the back; "lit" is bright,
   with a soft light around it.
   token: the theme colours, for an icon that draws a shape of its own. */
const kit = {
  at: (u, v, w = 0) => proj(world(u, v, w)),
  face(points) { const d = path(points); return `<path class="face" d="${d}"/><path class="rim" d="${d}"/>`; },
  slab(a, b, th, r = 6) {
    const edge = outline(a, b, r), up = edge.map(([u, v]) => kit.at(u, v, th / 2)), down = edge.map(([u, v]) => kit.at(u, v, -th / 2));
    const s = kit.at(-a * .36, -b * .34, th / 2);
    return `<path class="body" d="${path(hull([...up, ...down]))}"/>` + kit.face(up) +
      `<ellipse class="spec" cx="${f(s[0])}" cy="${f(s[1])}" rx="${f(a * .5)}" ry="${f(b * PC * .4)}" fill="url(#spec)"/>`;
  },
  line(p, q, w, tone = "plain", alpha = 1) {
    if (tone === "lit") return `<path class="halo" d="${seg(p, q, w + 4.5)}"/><path class="lit" d="${seg(p, q, w)}" opacity="${h(alpha)}"/>`;
    const near = Math.min(1, Math.max(0, .5 + (p[3] + q[3]) / (4 * G.deep)));
    return `<path class="plain" d="${seg(p, q, w)}" opacity="${h(alpha * (.35 + .5 * near))}"/>`;
  },
  token: { ink: "var(--ink)", mute: "var(--mute)", blue: "var(--blue)", core: "var(--core)", paper: "var(--paper)" },
};
const ICONS = __ICONS__;  // slug: the ICON of tools/finding_<slug>.py, written in by view.py
const SLAB = kit => kit.slab(44, 38, 5);  // a finding without an icon of its own

/* The rail: MATH-500 from 40 % to 100 %, a glass plate that faces the viewer and sways by a few degrees. Above it the
   base model's marks, below it the RL model's, each with its name and score; a mark and its name open the finding it
   comes from. On load the marks are drawn in one after another (plan): the lit line runs from one score of the base
   model to the next, and the points to RL count down with it. Then RL gets the same vote and restarts, and its mark
   moves on. With reduced motion the last frame is shown at once. */
const R = { base: [], rl: [], g: null, plan: null, t0: 0, el: {}, yaw: 0, pitch: 0 };
const LO = 40, HI = 100;
const ease = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
function spread(xs, w, lo, hi) {  // centres for labels of width w near xs (sorted), at least w apart, inside lo..hi
  const c = xs.map(x => Math.min(hi - w / 2, Math.max(lo + w / 2, x)));
  for (let i = 1; i < c.length; i++) c[i] = Math.max(c[i], c[i - 1] + w);
  for (let i = c.length - 1; i >= 0; i--) c[i] = Math.min(c[i], i === c.length - 1 ? hi - w / 2 : c[i + 1] - w);
  return c;
}
function rgeo() {
  const W = $("fig").clientWidth, ph = W < 640, pad = ph ? 14 : 26;
  const x0 = pad, x1 = W - pad, x = s => x0 + (s - LO) / (HI - LO) * (x1 - x0);
  const w = n => Math.min(ph ? 96 : 180, (W - 4) / Math.max(1, n));
  const bw = w(R.base.length), rw = w(R.rl.length), lh = ph ? 64 : 58;
  const g = { W, ph, x, x0, x1, bw, rw, lh, rh: ph ? 20 : 34, rr: ph ? 10 : 17, deep: ph ? 7 : 10 };
  g.rail = lh + (ph ? 44 : 60) + g.rh / 2;      // the centre line of the rail
  g.tick = g.rail + g.rh / 2 + (ph ? 17 : 20);  // the baseline of the scale under it
  g.rlTop = g.tick + (ph ? 16 : 22);
  g.H = g.rlTop + lh + 2;
  g.bc = spread(R.base.map(s => x(s.pct)), bw, 0, W);
  g.rc = spread(R.rl.map(s => x(s.pct)), rw, 0, W);
  g.D = W * 1.8;
  return g;
}
function rproj(g, x, y, z) {  // the rail's view: a slow sway of a few degrees about its centre
  const cx = g.W / 2, cy = g.rail, X = x - cx, Y = y - cy;
  const c1 = Math.cos(R.yaw * RAD), s1 = Math.sin(R.yaw * RAD), c2 = Math.cos(R.pitch * RAD), s2 = Math.sin(R.pitch * RAD);
  const x1 = X * c1 + z * s1, z1 = z * c1 - X * s1, y1 = Y * c2 - z1 * s2, k = g.D / (g.D - (z1 * c2 + Y * s2));
  return [cx + x1 * k, cy + y1 * k];
}
function plate(g, z) {  // the rail's outline at depth z
  const r = g.rr, y0 = g.rail - g.rh / 2, y1 = g.rail + g.rh / 2, a = g.x0 - 10, b = g.x1 + 10, p = [];
  const corner = (cx, cy, a0) => { for (let i = 0; i <= 6; i++) p.push(rproj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cy + r * Math.sin((a0 + 15 * i) * RAD), z)); };
  corner(b - r, y0 + r, -90); corner(b - r, y1 - r, 0); corner(a + r, y1 - r, 90); corner(a + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}
function plan() {  // the entrance, about 2 s: when each part appears and where the lit line and the RL mark are, in ms from the start
  const steps = [], b = R.base, r = R.rl, show = { r0: 0 };
  let t = 150;
  for (let i = 0; i < b.length; i++) {
    const from = i ? b[i - 1].pct : LO, d = 160 + 6 * Math.abs(b[i].pct - from);
    steps.push({ from, to: b[i].pct, t0: t, d }); t += d;
    show["b" + i] = t; t += 70;
  }
  let move = null;
  if (r.length > 1) { move = { t0: t, d: 520 }; t += 520; show.r1 = t; }
  return { steps, show, move, count: { t0: Math.max(0, t - 650), d: 650 }, end: t };  // the number counts once, to its final value
}
function moment(ms) {  // the state of the entrance at ms
  const P = R.plan;
  let head = LO;
  for (const s of P.steps) if (ms >= s.t0) head = s.from + (s.to - s.from) * ease(Math.min(1, (ms - s.t0) / s.d));
  const r = R.rl, m = P.move;
  const target = !r.length ? null : !m || ms < m.t0 ? r[0].pct : r[0].pct + (r[1].pct - r[0].pct) * ease(Math.min(1, (ms - m.t0) / m.d));
  return { head, target, moving: m && ms >= m.t0, done: ms >= P.end };
}
function rbuild() {
  const g = R.g = rgeo(), svg = $("rail");
  svg.setAttribute("viewBox", `0 0 ${g.W} ${g.H}`);
  svg.setAttribute("height", g.H);
  const ticks = [];
  for (let s = LO; s <= HI; s += 10) {
    const x = g.x(s), near = R.rl.some(r => Math.abs(g.x(r.pct) - x) < (g.ph ? 13 : 16));
    if (!near) ticks.push(`<text class="tlab" x="${f(x)}" y="${f(g.tick)}" text-anchor="middle">${s === LO || s === HI ? s + " %" : s}</text>`);
  }
  const w0 = g.x1 - g.x0;
  svg.innerHTML =
    `<ellipse class="atmo" cx="${f(g.W * .55)}" cy="${f(g.rail)}" rx="${f(w0 * .62)}" ry="${f(g.rh * 3.2)}" fill="url(#atmo)"/>` +
    `<rect class="rshade" x="${f(g.x0)}" y="${f(g.rail + g.rh * .25)}" width="${f(w0)}" height="${f(g.rh * .8)}" rx="${g.rr}" filter="url(#soft)"/>` +
    `<path class="back" id="r-back"/><path class="plate" id="r-plate"/>` +
    ticks.join("") +
    `<path class="tick" id="r-ticks"/><path class="left" id="r-left"/>` +
    `<path class="glow" id="r-glow"/><path class="fill" id="r-fill"/>` +
    R.base.map((_, i) => `<path class="lead" id="lb${i}"/>`).join("") + R.rl.map((_, i) => `<path class="lead" id="lr${i}"/>`).join("") +
    R.base.map((_, i) => `<circle class="halo" id="hb${i}" r="0"/><circle class="bead" id="bb${i}" r="0"/>`).join("") +
    `<circle class="halo" id="r-hh" r="0"/><circle class="bead" id="r-head" r="0"/>` +
    R.rl.map((_, i) => `<circle class="ring" id="br${i}" r="0"/>`).join("") +
    R.base.map((s, i) => `<circle class="hit" data-i="b${i}" r="16"/>`).join("") + R.rl.map((s, i) => `<circle class="hit" data-i="r${i}" r="16"/>`).join("");
  R.el = {};
  svg.querySelectorAll("[id]").forEach(e => { R.el[e.id] = e; });
  const lab = (s, i, kind, c, w) =>
    `<a class="${kind}${R.shown && R.shown.has(kind[0] + i) ? " in" : ""}" data-i="${kind[0]}${i}" href="/finding/${esc(s.slug)}" ` +
    `style="left:${f(c - w / 2)}px;width:${f(w)}px;top:${kind === "base" ? 0 : f(g.rlTop)}px;height:${g.lh}px" ` +
    `aria-label="${esc(s.name)}, ${pc(s)}. Opens ${esc(s.title)}."><span class="lname">${esc(s.name)}</span><span class="lval">${pc(s)}</span></a>`;
  $("labels").innerHTML = R.base.map((s, i) => lab(s, i, "base", g.bc[i], g.bw)).join("") + R.rl.map((s, i) => lab(s, i, "rl", g.rc[i], g.rw)).join("");
  $("labels").querySelectorAll("a").forEach(a => {
    const on = v => () => { a.classList.toggle("on", v); R.el["l" + a.dataset.i].classList.toggle("on", v); };
    a.addEventListener("pointerenter", on(true)); a.addEventListener("pointerleave", on(false));
    a.addEventListener("focus", on(true)); a.addEventListener("blur", on(false));
  });
  svg.querySelectorAll(".hit").forEach(c => c.addEventListener("click", () => { location.href = $("labels").querySelector(`[data-i="${c.dataset.i}"]`).href; }));
  rdraw(performance.now());
}
function rdraw(now) {
  const g = R.g, E = R.el, ms = still.matches ? Infinity : now - R.t0, M = R.plan ? moment(ms) : null;
  if (!M) return;
  const P = R.plan, t = now / 1000;
  R.yaw = still.matches ? 0 : 2.2 * Math.sin(t * .11);
  R.pitch = still.matches ? 0 : 1.4 * Math.sin(t * .08);
  E["r-back"].setAttribute("d", plate(g, -g.deep));
  E["r-plate"].setAttribute("d", plate(g, 0));
  const at = s => rproj(g, g.x(s), g.rail, 2), top = g.rail - g.rh / 2, bot = g.rail + g.rh / 2;
  let tk = "";
  for (let s = LO; s <= HI; s += 10) { const a = rproj(g, g.x(s), bot - 5, 1), b = rproj(g, g.x(s), bot - 1, 1); tk += `M${f(a[0])} ${f(a[1])}L${f(b[0])} ${f(b[1])}`; }
  E["r-ticks"].setAttribute("d", tk);
  const a = at(LO), hd = at(M.head), th = g.ph ? 3 : 4;
  const line = `M${f(a[0])} ${f(a[1])}L${f(hd[0])} ${f(hd[1])}`;
  E["r-fill"].setAttribute("d", line); E["r-fill"].setAttribute("stroke-width", th);
  E["r-glow"].setAttribute("d", line); E["r-glow"].setAttribute("stroke-width", th * 3.5);
  const shown = R.shown = new Set(Object.keys(P.show).filter(k => ms >= P.show[k]));
  const breathe = 1 + .12 * Math.sin(t * .7);
  E["r-head"].setAttribute("cx", f(hd[0])); E["r-head"].setAttribute("cy", f(hd[1])); E["r-head"].setAttribute("r", ms >= P.steps[0].t0 ? (g.ph ? 5 : 6.5) : 0);
  E["r-hh"].setAttribute("cx", f(hd[0])); E["r-hh"].setAttribute("cy", f(hd[1])); E["r-hh"].setAttribute("r", ms >= P.steps[0].t0 ? f((g.ph ? 11 : 15) * breathe) : 0);
  R.base.forEach((s, i) => {
    const q = at(s.pct), on = shown.has("b" + i);
    E["bb" + i].setAttribute("cx", f(q[0])); E["bb" + i].setAttribute("cy", f(q[1])); E["bb" + i].setAttribute("r", on ? (g.ph ? 3 : 3.8) : 0);
    E["hb" + i].setAttribute("cx", f(q[0])); E["hb" + i].setAttribute("cy", f(q[1])); E["hb" + i].setAttribute("r", on ? (g.ph ? 6 : 8) : 0);
    const c = g.bc[i], y = g.lh + 6, q2 = rproj(g, g.x(s.pct), top - 3, 2);
    E["lb" + i].setAttribute("d", on ? `M${f(c)} ${f(y)}V${f(y + 8)}L${f(q2[0])} ${f(q2[1] - 12)}L${f(q2[0])} ${f(q2[1])}` : "");
  });
  R.rl.forEach((s, i) => {
    const on = shown.has("r" + i), q = i === 0 ? at(s.pct) : at(M.target);
    E["br" + i].setAttribute("cx", f(q[0])); E["br" + i].setAttribute("cy", f(q[1]));
    E["br" + i].setAttribute("r", i === 0 ? (on ? (g.ph ? 5.5 : 7) : 0) : (M.moving ? (g.ph ? 5.5 : 7) : 0));
    const c = g.rc[i], y = g.rlTop - 4, q2 = rproj(g, g.x(s.pct), bot + 3, 2);
    E["lr" + i].setAttribute("d", on ? `M${f(q2[0])} ${f(q2[1])}V${f(g.tick + 6)}L${f(c)} ${f(y - 6)}V${f(y)}` : "");
  });
  if (M.target != null && M.target > M.head) {
    const p = at(M.head + (g.ph ? 2 : 1.2)), q = at(M.target - (g.ph ? 2 : 1.2));
    E["r-left"].setAttribute("d", q[0] > p[0] ? `M${f(p[0])} ${f(p[1])}L${f(q[0])} ${f(q[1])}` : "");
  } else E["r-left"].setAttribute("d", "");
  $("labels").querySelectorAll("a").forEach(el => el.classList.toggle("in", shown.has(el.dataset.i)));
  for (const c of $("rail").querySelectorAll(".hit")) {
    const k = c.dataset.i, s = k[0] === "b" ? R.base[+k.slice(1)] : R.rl[+k.slice(1)], q = at(s.pct);
    c.setAttribute("cx", f(q[0])); c.setAttribute("cy", f(q[1])); c.style.display = shown.has(k) ? "" : "none";
  }
  if (R.rl.length) {
    const c = P.count, v = (R.final * ease(Math.min(1, Math.max(0, (ms - c.t0) / c.d)))).toFixed(1);
    if ($("gap").textContent !== v) $("gap").textContent = v;
    $("gapbox").classList.toggle("wait", ms < c.t0);
  }
  $("rest").classList.toggle("wait", !M.done);
}
function story(list) {
  const marks = [];
  for (const x of list) for (const s of x.steps || []) marks.push({ ...s, slug: x.slug, title: x.title, pct: 100 * s.right / s.n });
  R.base = marks.filter(m => m.model === "base");
  R.rl = marks.filter(m => m.model === "rl");
  if (!R.base.length) return;
  $("story").hidden = false;
  const plain = R.base[0], rl = R.rl[0], last = R.base[R.base.length - 1], rlLast = R.rl[R.rl.length - 1];
  $("ask").innerHTML = rl ? `Olmo 3 7B scores <b>${pc(plain)}</b> on MATH-500 before RL training and <b>${pc(rl)}</b> after. ` +
    "What does RL add, and how much of it needs no reward?" : "";
  $("setting").textContent = `MATH-500, ${plain.n} problems, T 1.0. A mark opens its finding.`;
  $("gapbox").hidden = !rl;
  R.final = rl ? Math.max(0, rlLast.pct - last.pct) : 0;
  $("gapunit").textContent = R.rl.length > 1 ? "points to RL with the same vote and restarts" : "points to RL, one sample";
  $("rest").textContent = R.rl.length > 1
    ? `RL still leads when both models get the same vote over 4 samples and restarts: ${rlLast.right} of ${rlLast.n} against ${last.right} of ${last.n}. ` +
      "What RL adds in these points is not yet explained."
    : "";
  $("src").innerHTML = [...R.base, ...R.rl].map(s => `<li>${esc(s.name)}: ${s.right} of ${s.n}, ${pc(s)}. ${esc(s.source)}</li>`).join("");
  R.plan = plan();
  R.t0 = performance.now();
  rbuild();
}
$("replay").addEventListener("click", () => { R.t0 = performance.now(); });
$("srcbox").addEventListener("toggle", () => { $("src").hidden = !$("srcbox").open; });
addEventListener("resize", () => { if (R.plan) rbuild(); });

/* The findings, in their groups. Each frame redraws only the icons that are on screen: the view sways, each icon at
   its own phase, and leans toward the mouse. With reduced motion there is one still frame. */
function paint(o, t) {
  aim(G.yaw + (still.matches ? 0 : 6 * Math.sin(t * .13 + o.i * 1.3) + 9 * o.px), still.matches ? 0 : 2.5 * Math.sin(t * .09 + o.i * .8) - 5 * o.py);
  o.g.innerHTML = o.icon(kit, t, [o.px, o.py]);
}
function rows(list) {
  const key = JSON.stringify(list);
  if (key === S.key) return;
  S.key = key;
  const sorted = [...list].sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0));
  const groups = [...new Set(sorted.map(x => x.group || "New"))];
  let n = 0;
  $("groups").classList.toggle("flat", KIND !== "findings");
  $("groups").innerHTML = groups.map(name => `<section class="group"><h2>${esc(name)}</h2><ul class="rows">` +
    sorted.filter(x => (x.group || "New") === name).map(x =>
      `<li style="--i:${n++}"><a class="row${x.figure ? "" : " nofig"}" href="/${KIND === "findings" ? "finding" : "proof"}/${esc(x.slug)}" data-slug="${esc(x.slug)}">` +
      `<span class="fig2">${x.figure ? `<span class="num"><b>${esc(x.figure[0])}</b><span class="u">${esc(x.figure[1])}</span></span><span class="unit">${nb(x.figure[2])}</span>` : ""}</span>` +
      `<span class="text"><h3 class="title">${esc(x.title)}</h3><p class="line">${nb(x.line)}</p></span>` +
      `<svg class="icon" viewBox="0 0 ${G.w} ${G.h}" aria-hidden="true">` +
      `<ellipse class="atmo" cx="${G.cx}" cy="${G.cy + 3}" rx="70" ry="42" fill="url(#atmo)"/>` +
      `<ellipse class="shade" cx="${G.cx + 3}" cy="${G.cy + 11}" rx="60" ry="29" fill="url(#shade)"/><g></g></svg></a></li>`).join("") +
    "</ul></section>").join("");
  S.tiles = [...$("groups").querySelectorAll(".row")].map((el, i) =>
    ({ i, el, svg: el.querySelector("svg"), g: el.querySelector("svg g"), icon: ICONS[el.dataset.slug] || SLAB, seen: true, px: 0, py: 0, tx: 0, ty: 0 }));
  S.tiles.forEach(o => { paint(o, 0); watch.observe(o.el); });
}
const watch = new IntersectionObserver(found => found.forEach(e => {
  const o = S.tiles.find(o => o.el === e.target);
  if (o) o.seen = e.isIntersecting;
}));
function frame(now) {
  requestAnimationFrame(frame);
  if (still.matches || now - S.last < 32) return;  // a slow sway needs no more than about 30 frames a second
  S.last = now;
  if (R.plan) rdraw(now);
  for (const o of S.tiles) {
    if (!o.seen) continue;
    o.px += (o.tx - o.px) * .1;
    o.py += (o.ty - o.py) * .1;
    paint(o, now / 1000);
  }
}
document.addEventListener("pointermove", e => {  // each icon leans toward a mouse, by how far the mouse is from it
  if (e.pointerType !== "mouse" || still.matches) return;
  for (const o of S.tiles) {
    if (!o.seen) continue;
    const b = o.svg.getBoundingClientRect(), lean = d => Math.max(-1, Math.min(1, d / 320));
    o.tx = lean(e.clientX - b.left - b.width / 2);
    o.ty = lean(e.clientY - b.top - b.height / 2);
  }
});
document.documentElement.addEventListener("pointerleave", () => { S.tiles.forEach(o => { o.tx = o.ty = 0; }); });
still.addEventListener("change", () => { S.tiles.forEach(o => paint(o, 0)); if (R.plan) rdraw(performance.now()); });

/* The rows are written into the page by view.py, so the picture is drawn at once and nothing is read later. */
const LIST = __ROWS__;
if (KIND === "findings") story(LIST);
rows(LIST);
requestAnimationFrame(frame);
</script>
</body>
</html>
"""

# The tab Proof (/proof) is the same page with these differences: its rows are the experiments that test the team's
# method itself (tools/proof_<slug>.py, /proof/<slug>), written in by view.py as __ROWS__, in one list with no picture
# and no group names. view.py applies them.
PROOF = [
    ('<title>Invariant: Findings</title>', '<title>Invariant: Proof</title>'),
    ('<a href="/proof">Proof</a>\n    <a href="/findings" aria-current="page">Findings</a>',
     '<a href="/proof" aria-current="page">Proof</a>\n    <a href="/findings">Findings</a>'),
    ('<p class="say" id="say" hidden></p>', '<p class="say" id="say">Experiments on the harness itself.</p>'),
    ('const KIND = "findings";', 'const KIND = "proof";'),
]
