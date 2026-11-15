"""The Papers page of the team site: how the paper loop works, and the papers it has produced.

view.py serves page(PAPERS) at /papers; the home dial leads to it. The words column states what the loop is and its
six steps in order. The picture is the papers themselves: one lit sheet per paper of view.PAPERS, in the order they
were written, each with its title, its claim, its length, why the loop picked it and how it was checked. A click on a
sheet opens its PDF. The status at the top right says whether the loop's work item (LOOP_ITEM) is open on the board
and when it last moved, from /data, read every 10 s. Nothing here writes to the board.

Where the words come from. The steps: the comments of board item work-184476, meta/tierlist/ (TIERLIST.md, ROUND3.md,
ROUND4.md) and the NOTES.md of each paper folder. A paper's claim is the subtitle on the first page of its PDF. Its
pages are counted by pdfinfo. "picked" and "checked" quote the tier lists, result-8c92fc and its comments, the
comments of work-184476 and facts.json (`checks_against_readouts`). A paper that view.PAPERS holds and ROWS does not
still gets a sheet, with its title only, so a new paper cannot stop view.py at import; add its row here.
"""
import html
import json

import demo_deck

LOOP_ITEM = "work-184476"
ROWS = {
    "the-finish-dial.pdf": {
        "claim": "The top singular directions of an RL weight update set how often a language model finishes its answer.",
        "pages": 6,
        "picked": "The one finding in tier S of the first tier list: 5 judges gave it 4.8 of 5.",
        "checked": "25 of 25 numbers in the published PDF match their sources.",
    },
    "theories-on-trial.pdf": {
        "claim": "Forecasts that language-model agents file with a mechanism are more confident, not more accurate, than forecasts filed without one.",
        "pages": 6,
        "picked": "Tier round 3: 8 scouts, 9 candidates, 5 judges. It scored 4.3 of 5.",
    },
    "the-first-hundred-steps.pdf": {
        "claim": "On the released checkpoints of an RL run, a three-token opening takes the base model to within 1.4 points of step 100.",
        "pages": 4,
        "picked": "Tier round 3, 4.4 of 5. It waited for three more samples of each model.",
        "checked": "4 review passes.",
    },
    "no-early-warning.pdf": {
        "claim": "In the first 2,000 tokens nothing we tried orders two attempts at one problem better than 0.59; the signal arrives when attempts end.",
        "pages": 4,
        "picked": "Tier round 4: first of 6 candidates, and it needed no GPU run.",
        "checked": "64 checks of its numbers against stored readouts pass.",
    },
}
STEPS = [
    ("Tier", "Scout agents collect the project's findings, re-read the best at their files, search the literature and score novelty and evidence. Judges rank them."),
    ("Pick", "The best finding with no paper yet is next. If it lacks samples, the runs are started and the paper waits for them."),
    ("Facts", "The paper's numbers are recomputed from files in git into one file, facts.json. The figures are drawn from that file."),
    ("Threats", "Notes list what could refute the claim, strongest first. The claim is cut down to what survives."),
    ("Draft", "One agent writes four to six pages in LaTeX, with every number taken from facts.json."),
    ("Review", "Other agents review the PDF, the fixes are applied, and the PDF goes on this site. Then the loop starts again."),
]


def page(papers):
    """The page for these papers (view.PAPERS: file names in the order written)."""
    esc = html.escape
    sheets = []
    for i, name in enumerate(papers):
        row = ROWS.get(name, {})
        foot = "".join(f"<p>{esc(row[k])}</p>" for k in ("picked", "checked") if k in row)
        pages = f'{row["pages"]} pages' if "pages" in row else "PDF"
        sheets.append(
            f'<a class="sheet" style="--i:{i}" href="/paper/{esc(name)}"><span class="no">Paper {i + 1}</span>'
            f'<h2>{esc(demo_deck.paper_title(name))}</h2><p class="claim">{esc(row.get("claim", ""))}</p>'
            f'<div class="how">{foot}</div><span class="open"><b>{pages}</b><i>Open the PDF</i></span></a>')
    steps = "".join(f'<li><b>{esc(n)}</b><span>{esc(t)}</span></li>' for n, t in STEPS)
    return (PAGE.replace("__SHEETS__", "".join(sheets)).replace("__STEPS__", steps)
            .replace("__N__", str(len(papers))).replace("__ITEM__", json.dumps(LOOP_ITEM)))


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Papers</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens, the light and the type of the Design page (architecture.py). */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-c: rgba(16, 24, 32, .5);
  --lit: 0 30px 50px -28px rgba(16, 24, 32, .5);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .5); --rim-c: rgba(143, 177, 255, .22);
    --lit: 0 0 90px -20px rgba(143, 177, 255, .22);
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
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }

.page {
  display: grid; grid-template-columns: minmax(320px, 27vw) minmax(0, 1fr); grid-template-rows: auto minmax(0, 1fr);
  column-gap: 48px; height: 100vh; min-height: 660px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 22px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top .name a, .top .name a:hover { color: var(--ink); }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.status { margin-left: auto; color: var(--mute); white-space: nowrap; display: flex; align-items: center; gap: 10px; }
.status::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--blue); box-shadow: 0 0 0 4px color-mix(in srgb, var(--blue) 20%, transparent); }
.status.bad { color: var(--red); }
.status.bad::before { background: var(--red); box-shadow: 0 0 0 4px color-mix(in srgb, var(--red) 20%, transparent); }

/* The words: the sentence and the six steps, which are a sequence */
.words { grid-column: 1; grid-row: 2; min-height: 0; overflow: hidden auto; scrollbar-width: none; padding: clamp(18px, 4.5vh, 52px) 0 0; }
.cap { margin: 0; font-size: clamp(20px, 1.56vw, 27px); line-height: 1.22; font-weight: 300; font-stretch: 102%; letter-spacing: -.012em; max-width: 24ch; text-wrap: balance; }
.steps { list-style: none; counter-reset: step; margin: clamp(18px, 3.4vh, 34px) 0 0; padding: 0; border-bottom: 1px solid var(--rule); }
.steps li { counter-increment: step; display: grid; grid-template-columns: 1.5em 5.2em minmax(0, 1fr); column-gap: 8px; padding: 9px 0; border-top: 1px solid var(--rule); align-items: baseline; }
.steps li::before { content: counter(step); color: var(--mute); font-size: 13px; }
.steps b { font-weight: 600; font-stretch: 108%; }
.steps span { color: var(--mute); font-size: 13.5px; line-height: 1.42; text-wrap: pretty; }

/* The picture: the papers, as lit sheets standing in a shallow arc */
.stage { grid-column: 2; grid-row: 2; min-height: 0; min-width: 0; display: flex; align-items: center; perspective: 1900px; perspective-origin: 30% 20%; }
.row { display: flex; gap: clamp(14px, 1.7vw, 30px); width: 100%; transform-style: preserve-3d; animation: sway 16s ease-in-out infinite alternate; }
@keyframes sway { from { transform: rotateX(3deg) rotateY(-5deg); } to { transform: rotateX(1.5deg) rotateY(3.5deg); } }
.sheet {
  flex: 1 1 0; min-width: 0; aspect-ratio: 1 / 1.52; max-height: 74vh; display: flex; flex-direction: column;
  padding: clamp(14px, 1.5vw, 26px); text-decoration: none; border-radius: 3px;
  background: linear-gradient(150deg, var(--glass-hi), var(--glass) 46%, var(--glass-lo));
  border: 1px solid var(--rim-c); border-top-color: var(--rim-a); border-left-color: var(--rim-a); box-shadow: var(--lit);
  transform: translateZ(calc(var(--i) * -34px)) translateY(calc(var(--i) * 10px)); transition: transform .25s cubic-bezier(.3, 0, .2, 1), border-color .2s ease;
  animation: rise .7s cubic-bezier(.2, .7, .2, 1) both; animation-delay: calc(.1s + var(--i) * 90ms);
}
@keyframes rise { from { opacity: 0; transform: translateZ(calc(var(--i) * -34px)) translateY(calc(var(--i) * 10px + 26px)); } }
.sheet:hover, .sheet:focus-visible { transform: translateZ(calc(var(--i) * -34px + 30px)) translateY(calc(var(--i) * 10px - 4px)); border-color: var(--blue); }
.no { font-size: 12.5px; font-weight: 600; color: var(--mute); }
.sheet h2 { margin: .5em 0 0; font-size: clamp(19px, 1.75vw, 31px); line-height: 1.08; font-weight: 300; font-stretch: 100%; letter-spacing: -.014em; text-wrap: balance; }
.claim { margin: .9em 0 0; font-size: clamp(12.5px, .95vw, 15px); line-height: 1.4; text-wrap: pretty; }
.how { margin-top: auto; padding-top: 12px; font-size: clamp(11.5px, .82vw, 13px); line-height: 1.38; color: var(--mute); }
.how p { margin: 0; padding: 6px 0; border-top: 1px solid var(--rule); }
.open { display: flex; justify-content: space-between; align-items: baseline; padding-top: 8px; border-top: 1px solid var(--ink); font-size: 13px; }
.open b { font-weight: 600; }
.open i { font-style: normal; color: var(--blue); font-weight: 600; }

@media (max-width: 1100px) {
  .page { display: block; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .words { overflow: visible; padding-top: 20px; }
  .cap { font-size: 22px; max-width: none; }
  .stage { display: block; perspective: none; margin-top: 26px; }
  .row { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 14px; animation: none; }
  .sheet, .sheet:hover, .sheet:focus-visible { transform: none; aspect-ratio: auto; max-height: none; min-height: 300px; animation-name: fade; }
  .sheet h2 { font-size: 25px; } .claim { font-size: 14.5px; } .how { font-size: 13px; }
}
@keyframes fade { from { opacity: 0; } }
@media (prefers-reduced-motion: reduce) {
  .row, .sheet { animation: none; }
  .sheet { transition: none; }
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
    <span class="status" id="status">Reading the board</span>
  </header>
  <div class="words">
    <p class="cap">A loop of agents takes the project's strongest finding that has no paper yet, recomputes its numbers and writes it up. It has written __N__ papers.</p>
    <ol class="steps">__STEPS__</ol>
  </div>
  <div class="stage"><div class="row">__SHEETS__</div></div>
</div>
<script>
/* The status: whether the loop's work item is open on the board, and when it last moved. */
const ITEM = __ITEM__, st = document.getElementById("status");
let readAt = 0;
const ago = ns => { const m = Math.max(0, Math.floor((Date.now() * 1e6 - Number(ns)) / 60e9)); return m < 1 ? "now" : m < 60 ? m + " min ago" : Math.floor(m / 60) + " h ago"; };
async function read() {
  try {
    const r = await fetch("/data"); if (!r.ok) throw new Error(r.status);
    const it = (await r.json()).items.find(i => i.id === ITEM);
    readAt = Date.now(); st.classList.remove("bad");
    st.textContent = !it ? "The loop's work item is not among the newest on the board"
      : it.listed === "work" ? "The loop is running, last step " + ago(it.active_ns || it.at_ns) : "The loop has stopped";
  } catch (e) {
    st.classList.add("bad");
    st.textContent = readAt ? "Offline, last read " + new Date(readAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false }) : "Offline";
  }
}
read(); setInterval(read, 10000);
</script>
</body>
</html>
"""
