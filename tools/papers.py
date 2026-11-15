"""The Papers page of the team site: how the paper loop works, and the papers it has produced.

view.py serves page(PAPERS) at /papers; the home dial leads to it. The words column states what the loop is and its
six steps in order. The picture is the papers themselves, as one stack of sheets in the order they were written. The
sheet in front is large and lit and can be read: its title, its claim, why the loop picked it, how it was checked, its
length and the one button, which opens the PDF in a new tab. The other sheets stand behind it, each farther and fainter,
and each shows its number and title on the strip that stays visible. A click on a strip, or the left and right arrow
keys, brings that paper to the front; the paper in front is in the address (/papers#no-early-warning), so Back works.
The strips share the width the front sheet leaves, so about eight papers fit beside the words at 1260 px. Where the page is one column (below
1240 px) there is no stack and every sheet is shown in full, one after the other. The status at the top right says
whether the loop's work item (LOOP_ITEM) is open on the board and when it last moved, from /data, read every 10 s.
Nothing here writes to the board.

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
    "two-token-limits.pdf": {
        "claim": "Three gains between fine-tunes of one 7B model, scored at 16,384 and at 32,768 tokens: one holds, one grows by 6 points and one shrinks.",
        "pages": 4,
        "picked": "Tier round 5: the cap test of a scout on stored rows; it waited for one run at the larger limit.",
        "checked": "153 checks of its numbers against stored readouts pass; 4 review passes.",
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
        row, title = ROWS.get(name, {}), esc(demo_deck.paper_title(name))
        how = "".join(f"<div><dt>{k.title()}</dt><dd>{esc(row[k])}</dd></div>" for k in ("picked", "checked") if k in row)
        pages = f'{row["pages"]} pages' if "pages" in row else "PDF"
        sheets.append(
            f'<article class="sheet{"" if i else " front"}" id="{esc(name.rsplit(".", 1)[0])}" style="--i:{i}">'
            f'<button class="spine" aria-label="Paper {i + 1}: {title}"><span><i>{i + 1}</i><b>{title}</b></span></button>'
            f'<div class="face"><p class="no">Paper {i + 1} of {len(papers)}</p><h2>{title}</h2>'
            f'<p class="claim">{esc(row.get("claim", ""))}</p><dl class="how">{how}</dl>'
            f'<p class="foot"><a class="open" href="/paper/{esc(name)}" target="_blank" rel="noopener">Open the PDF</a><span>{pages}</span></p></div></article>')
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
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #cbd2d8;
  --blue: #1f43d6; --red: #c41e34; --on-blue: #fff;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18);
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28);
  --lit: 0 30px 50px -28px rgba(16, 24, 32, .5);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c; --on-blue: #080c11;
    --btn: linear-gradient(#f7fafc, #cbd5de); --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7);
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .5);
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
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
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
.words { grid-column: 1; grid-row: 2; min-height: 0; overflow: hidden auto; scrollbar-width: none; padding: clamp(20px, 4vh, 30px) 0 0; }
.cap { margin: 0; font-size: clamp(20px, 1.56vw, 27px); line-height: 1.22; font-weight: 300; font-stretch: 102%; letter-spacing: -.012em; max-width: 24ch; text-wrap: pretty; }
.steps { list-style: none; counter-reset: step; margin: clamp(14px, 3.4vh - 6px, 34px) 0 0; padding: 0; border-bottom: 1px solid var(--rule); }
.steps li { counter-increment: step; display: grid; grid-template-columns: 1.5em 5.2em minmax(0, 1fr); column-gap: 8px; padding: clamp(7px, 1.2vh, 9px) 0; border-top: 1px solid var(--rule); align-items: baseline; }
.steps li::before { content: counter(step); color: var(--mute); font-size: 13px; }
.steps b { font-weight: 600; font-stretch: 108%; }
.steps span { color: var(--mute); font-size: 13.5px; line-height: 1.42; text-wrap: pretty; }

/* The picture: the papers as one stack. --k is a sheet's place in it, 0 in front (set by the script; before it runs,
   the order written). --fw is the width of a sheet: as tall as the stage allows, and narrow enough to leave every
   sheet behind it a strip of 92 px (with many papers the strips get narrower, the sheet no narrower than 380 px). --u, a hundredth of it, sets the type on a sheet, so the text fits at every size. */
.stage { grid-column: 2; grid-row: 2; min-height: 0; min-width: 0; container-type: size; display: grid; place-items: center; perspective: 1800px; }
/* .lean and .stack take no clicks: their own flat boxes lie in front of the sheets behind and would catch them */
.lean { pointer-events: none; transform-style: preserve-3d; transform: rotateX(calc(var(--ly, 0) * -2.5deg)) rotateY(calc(var(--lx, 0) * 3.5deg)); transition: transform .9s cubic-bezier(.2, .7, .2, 1); }
.stack {
  --fw: min(90cqh / 1.3, 540px, max(380px, 100cqw - (var(--n) - 1) * 92px)); --strip: min(138px, (100cqw - var(--fw)) / max(var(--n) - 1, 1)); --u: calc(var(--fw) / 100);
  position: relative; width: calc(var(--fw) + (var(--n) - 1) * var(--strip)); height: calc(var(--fw) * 1.3);
  transform-style: preserve-3d; animation: sway 18s ease-in-out infinite alternate;
}
@keyframes sway { from { transform: rotateX(2deg) rotateY(-3deg); } to { transform: rotateX(.5deg) rotateY(3deg); } }
.sheet {
  --k: var(--i); pointer-events: auto; position: absolute; left: 0; top: 0; width: var(--fw); height: 100%; border-radius: 4px;
  /* far is fainter: a sheet takes on the room's color with its distance */
  background: linear-gradient(color-mix(in srgb, var(--paper) calc(var(--k) * 13%), transparent) 0 0), linear-gradient(150deg, var(--glass-hi), var(--glass) 46%, var(--glass-lo));
  border: 0 solid var(--rim-a); border-width: 1px 0 0 1px;  /* the light catches the top and left edges */
  transform: translate3d(calc(var(--k) * var(--strip)), 0, calc(var(--k) * -70px));
  transition: transform .8s cubic-bezier(.3, 0, .1, 1), box-shadow .8s ease;
  animation: rise .8s cubic-bezier(.2, .7, .2, 1) both; animation-delay: calc(.1s + var(--k) * 80ms);
}
@keyframes rise { from { opacity: 0; translate: 0 28px; } }
.sheet.front { box-shadow: var(--lit); }  /* one lit object: only the sheet in front has the glow or the cast shadow */

/* A sheet behind: all of it is the button, and its number and title sit on the strip that shows */
.spine { position: absolute; inset: 0; border-radius: 4px; transition: opacity .4s ease, visibility .4s; }
.spine span { position: absolute; top: 0; right: 0; width: var(--strip); padding: calc(var(--u) * 8) calc(var(--strip) * .1) 0 calc(var(--strip) * .12); display: grid; gap: 8px; overflow-wrap: break-word; }
.spine i { font-style: normal; font-size: 12.5px; font-weight: 600; color: var(--mute); }
.spine b { font-size: clamp(12.5px, var(--strip) * .13, 16px); line-height: 1.16; font-weight: 400; letter-spacing: -.008em; color: var(--mute); transition: color .15s ease; }
.spine:hover b, .spine:focus-visible b { color: var(--ink); }
.front .spine { opacity: 0; visibility: hidden; }

/* The sheet in front: the paper, set to be read */
.face { position: absolute; inset: 0; display: flex; flex-direction: column; padding: calc(var(--u) * 8); opacity: 0; visibility: hidden; transition: opacity .3s ease, visibility .3s; }
.front .face { opacity: 1; visibility: visible; transition: opacity .3s ease .35s, visibility 0s; }
.no { margin: 0; font-size: max(12.5px, var(--u) * 2.9); font-weight: 600; color: var(--mute); }
.sheet h2 { margin: calc(var(--u) * 4.5) 0 0; font-size: calc(var(--u) * 10.4); line-height: 1.03; font-weight: 300; font-stretch: 100%; letter-spacing: -.022em; text-wrap: balance; }
.claim { margin: calc(var(--u) * 5) 0 0; font-size: max(14.5px, var(--u) * 4.1); line-height: 1.42; text-wrap: pretty; }
.how { margin: auto 0 0; padding-top: 14px; font-size: max(12.5px, var(--u) * 3.05); line-height: 1.4; }
.how div { display: grid; grid-template-columns: 5.4em minmax(0, 1fr); padding: calc(var(--u) * 1.9) 0; border-top: 1px solid var(--rule); }
.how dt { font-weight: 600; }
.how dd { margin: 0; color: var(--mute); text-wrap: pretty; }
.foot { margin: 0; padding-top: calc(var(--u) * 4); border-top: 1px solid var(--rule); display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: max(13px, var(--u) * 3.05); color: var(--mute); }
.open {
  padding: .62em 1.35em; border-radius: 999px; background: var(--btn); color: var(--btn-ink); font-weight: 600; text-decoration: none; white-space: nowrap;
  box-shadow: inset 0 1px 0 var(--btn-edge); transition: background .15s ease, color .15s ease;
}
.open:hover { background: var(--blue); color: var(--on-blue); box-shadow: none; }

@media (max-height: 760px) { .words { padding-top: 16px; } .cap { max-width: none; font-size: 20px; } .steps li { padding: 6px 0; } .steps span { font-size: 13px; line-height: 1.36; } }  /* a short window: the six steps still fit under the sentence */
@media (max-width: 1240px) {  /* below this the stack beside the words is too narrow: one column, every sheet in full */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .words { display: contents; }  /* the sentence, then the papers, then the steps that made them */
  .stage { order: 1; } .steps { order: 2; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .cap { font-size: 22px; max-width: none; margin-top: 20px; } .steps li { padding: 9px 0; } .steps span { font-size: 13.5px; line-height: 1.42; }
  .stage { display: block; place-items: normal; container-type: normal; perspective: none; margin-top: 26px; }
  .lean { transform: none; }
  .stack { --fw: 350px; width: auto; height: auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; animation: none; }
  .sheet { position: relative; width: auto; height: auto; transform: none; scroll-margin-top: 12px; animation-name: fade; background: linear-gradient(150deg, var(--glass-hi), var(--glass) 46%, var(--glass-lo)); }
  .spine { display: none; }
  .face, .front .face { position: static; min-height: 400px; opacity: 1; visibility: visible; }
}
@keyframes fade { from { opacity: 0; } }
@media (prefers-reduced-motion: reduce) {
  .stack, .sheet { animation: none; }
  .lean, .sheet, .spine, .face, .front .face { transition: none; }
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
  <div class="stage" id="stage"><div class="lean"><div class="stack" style="--n:__N__">__SHEETS__</div></div></div>
</div>
<script>
/* The stack. The paper in front is the one named in the address (/papers#no-early-warning), else the first. The sheets
   after it follow in the order written, and the ones before it go to the back. */
const stage = document.getElementById("stage"), sheets = [...stage.querySelectorAll(".sheet")];
const front = () => Math.max(0, sheets.findIndex(s => "#" + s.id === location.hash));
function show() {
  const f = front();
  sheets.forEach((s, i) => { s.style.setProperty("--k", (i - f + sheets.length) % sheets.length); s.classList.toggle("front", i === f); });
}
function go(i) { history.pushState(null, "", "#" + sheets[(i + sheets.length) % sheets.length].id); show(); }
stage.addEventListener("click", e => {
  const b = e.target.closest(".spine"); if (!b) return;
  go(sheets.indexOf(b.parentElement)); b.parentElement.querySelector(".open").focus({ preventScroll: true });  // the strip is gone: the focus goes to the paper's button
});
addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey || (e.key !== "ArrowRight" && e.key !== "ArrowLeft")) return;
  e.preventDefault(); go(front() + (e.key === "ArrowRight" ? 1 : -1));
});
addEventListener("popstate", show); addEventListener("hashchange", show); show();
/* The stack leans a few degrees toward the mouse and settles back when it leaves. */
const lean = stage.firstElementChild;
stage.addEventListener("pointermove", e => {
  const r = stage.getBoundingClientRect();
  lean.style.setProperty("--lx", ((e.clientX - r.left) / r.width * 2 - 1).toFixed(2)); lean.style.setProperty("--ly", ((e.clientY - r.top) / r.height * 2 - 1).toFixed(2));
});
stage.addEventListener("pointerleave", () => { lean.style.setProperty("--lx", 0); lean.style.setProperty("--ly", 0); });

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
