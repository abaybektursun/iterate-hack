"""The Papers page of the team site: how the paper loop works, and the papers it has produced.

view.py serves page(PAPERS) at /papers; the home dial leads to it. The words column states what the loop is and names its
six steps in order; a click on a step opens its one sentence, and only one is open at a time. The picture is the papers themselves, as one stack of sheets in the order they were written, left to right. The
sheet in front is large and lit and can be read: its title, its claim, why the loop picked it, how it was checked, its
length and the one button, which opens the PDF in a new tab. The other sheets stand behind it on both sides, each farther and fainter,
and each shows its number and title on the strip that stays visible. No sheet ever changes its place: a change of
paper only changes the depths. A click on a strip, or the left and right arrow
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
    steps = "".join(f'<details name="step"><summary><i>{i}</i><b>{esc(n)}</b></summary><p>{esc(t)}</p></details>' for i, (n, t) in enumerate(STEPS, 1))
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
  --lit: 0 70px 90px -60px rgba(16, 24, 32, .55), 0 18px 36px -24px rgba(16, 24, 32, .25);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c; --on-blue: #080c11;
    --btn: linear-gradient(#f7fafc, #cbd5de); --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7);
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .5);
    --lit: 0 0 140px -30px rgba(143, 177, 255, .2);
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

/* The words: the sentence, then the six steps by name. A step opens to its one sentence. */
.words { grid-column: 1; grid-row: 2; min-height: 0; overflow: hidden auto; scrollbar-width: none; padding: clamp(28px, 7vh, 72px) 0 0; }
.cap { margin: 0; font-size: clamp(23px, 1.9vw, 33px); line-height: 1.16; font-weight: 250; font-stretch: 100%; letter-spacing: -.02em; max-width: 19ch; text-wrap: balance; }
.steps { margin: clamp(26px, 6vh, 60px) 0 0; border-bottom: 1px solid var(--rule); max-width: 340px; }
.lab { margin: 0 0 10px; font-size: 12.5px; font-weight: 600; color: var(--mute); }
.steps details { border-top: 1px solid var(--rule); }
.steps summary { display: grid; grid-template-columns: 2em minmax(0, 1fr) auto; align-items: baseline; padding: clamp(8px, 1.5vh, 12px) 0; cursor: pointer; list-style: none; }
.steps summary::-webkit-details-marker { display: none; }
.steps summary::after { content: "+"; color: var(--mute); font-weight: 300; font-size: 17px; line-height: 1; }
.steps details[open] summary::after { content: "\2212"; }
.steps i { font-style: normal; color: var(--mute); font-size: 12.5px; }
.steps b { font-weight: 500; font-stretch: 104%; }
.steps details p { margin: 0; padding: 0 1.4em 14px 2em; color: var(--mute); font-size: 13.5px; line-height: 1.45; text-wrap: pretty; }

/* The picture: the papers as one stack. A sheet never changes its place, the order written from left to right: only
   its depth --d changes, the number of sheets between it and the paper in front (set by the script; before it runs
   the first paper is in front). --d is a registered number, so the depth, the fading with distance and the light all
   move together from one transition. --fw is the width of a sheet: as tall as the stage allows, and narrow enough to
   leave every other sheet a strip of 92 px (with many papers the strips get narrower, the sheet no narrower than
   380 px). --u, a hundredth of it, sets the type on a sheet, so the text fits at every size. */
@property --d { syntax: "<number>"; inherits: true; initial-value: 0; }
.stage { grid-column: 2; grid-row: 2; min-height: 0; min-width: 0; container-type: size; display: grid; place-items: center; perspective: 2000px; }
.stack {
  --fw: min(92cqh / 1.4, 520px, max(380px, 100cqw - (var(--n) - 1) * 92px)); --strip: min(138px, (100cqw - var(--fw)) / max(var(--n) - 1, 1)); --u: calc(var(--fw) / 100);
  position: relative; width: calc(var(--fw) + (var(--n) - 1) * var(--strip)); height: calc(var(--fw) * 1.4);
  transform-style: preserve-3d; pointer-events: none;  /* its own flat box lies in front of the sheets behind and would catch their clicks */
}
@keyframes arrive { from { opacity: 0; translate: 0 18px; } }
.sheet {
  --d: var(--i); pointer-events: auto; position: absolute; left: 0; top: 0; width: var(--fw); height: 100%; border-radius: 2px;
  /* far is fainter: a sheet takes on the room's color with its distance */
  background: linear-gradient(color-mix(in srgb, var(--paper) calc(var(--d) * 13%), transparent) 0 0), linear-gradient(150deg, var(--glass-hi), var(--glass) 46%, var(--glass-lo));
  border: 0 solid var(--rim-a); border-width: 1px 0 0 1px;  /* the light catches the top and left edges */
  transform: translate3d(calc(var(--i) * var(--strip)), 0, calc(var(--d) * -70px));
  transition: --d .62s cubic-bezier(.65, 0, .35, 1);
  animation: arrive 1s cubic-bezier(.16, 1, .3, 1) both; animation-delay: calc(var(--i) * 70ms);  /* on the sheets: an opacity on the stack would flatten its depth */
}
/* One lit object: the glow or the cast shadow belongs to the paper in front and fades with the first step back */
.sheet::before { content: ""; position: absolute; inset: 0; border-radius: 2px; box-shadow: var(--lit); opacity: clamp(0, 1 - var(--d), 1); pointer-events: none; }

/* A sheet behind: all of it is the button, and its number and title sit on the strip that shows, the left one for a
   paper before the one in front and the right one for a paper after it. While the sheets change depth (.moving) no
   text shows: it fades out, the sheets move, and it fades in at its new place. */
.spine { position: absolute; inset: 0; border-radius: 2px; }
.spine span { position: absolute; top: 0; right: 0; width: var(--strip); padding: calc(var(--u) * 10) calc(var(--strip) * .1) 0 calc(var(--strip) * .14); display: grid; gap: 10px; overflow-wrap: break-word; transition: opacity .3s ease; }
.before .spine span { right: auto; left: 0; }
.spine i { font-style: normal; font-size: 12.5px; font-weight: 600; color: var(--mute); }
.spine b { font-size: clamp(12.5px, var(--strip) * .11, 14px); line-height: 1.22; font-weight: 400; letter-spacing: -.008em; color: var(--mute); transition: color .15s ease; }
.spine:hover b, .spine:focus-visible b { color: var(--ink); }
.front .spine { visibility: hidden; }
.moving .spine span, .moving .face { opacity: 0; transition-duration: .14s; }

/* The sheet in front: the paper, set to be read */
.face { position: absolute; inset: 0; display: flex; flex-direction: column; padding: calc(var(--u) * 10); visibility: hidden; transition: opacity .3s ease; }
.front .face { visibility: visible; }
.no { margin: 0; font-size: max(12.5px, var(--u) * 2.7); font-weight: 500; color: var(--mute); }
.sheet h2 { margin: calc(var(--u) * 9) 0 0; font-size: calc(var(--u) * 11.4); line-height: 1; font-weight: 250; font-stretch: 100%; letter-spacing: -.03em; text-wrap: balance; }
.claim { margin: calc(var(--u) * 6) 0 0; font-size: max(14.5px, var(--u) * 3.7); line-height: 1.45; max-width: 30em; text-wrap: pretty; }
.how { margin: auto 0 0; padding-top: 14px; font-size: max(12.5px, var(--u) * 2.8); line-height: 1.45; }
.how div { display: grid; grid-template-columns: 6em minmax(0, 1fr); padding: calc(var(--u) * 2.4) 0; border-top: 1px solid var(--rule); }
.how dt { color: var(--mute); }
.how dd { margin: 0; text-wrap: pretty; }
.foot { margin: 0; padding-top: calc(var(--u) * 5); border-top: 1px solid var(--rule); display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: max(13px, var(--u) * 2.8); color: var(--mute); }
.open {
  padding: .62em 1.35em; border-radius: 999px; background: var(--btn); color: var(--btn-ink); font-weight: 600; text-decoration: none; white-space: nowrap;
  box-shadow: inset 0 1px 0 var(--btn-edge); transition: background .15s ease, color .15s ease;
}
.open:hover { background: var(--blue); color: var(--on-blue); box-shadow: none; }

@media (max-width: 1240px) {  /* below this the stack beside the words is too narrow: one column, every sheet in full */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .words { display: contents; }  /* the sentence, then the papers, then the steps that made them */
  .stage { order: 1; } .steps { order: 2; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .cap { font-size: 26px; max-width: 24ch; margin-top: 28px; } .steps { max-width: none; margin-top: 34px; }
  .stage { display: block; place-items: normal; container-type: normal; perspective: none; margin-top: 26px; }
  .stack { --fw: 350px; width: auto; height: auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; transform: none !important; pointer-events: auto; }
  .sheet { position: relative; width: auto; height: auto; transform: none; scroll-margin-top: 12px; background: linear-gradient(150deg, var(--glass-hi), var(--glass) 46%, var(--glass-lo)); }
  .spine, .sheet::before { display: none; }
  .sheet.front { box-shadow: var(--lit); }
  .face, .moving .face { position: static; min-height: 400px; opacity: 1; visibility: visible; }
}
@media (prefers-reduced-motion: reduce) {
  .sheet { animation: none; }
  .sheet, .spine span, .face { transition: none; }
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
    <div class="steps"><p class="lab">The six steps of the loop</p>__STEPS__</div>
  </div>
  <div class="stage" id="stage"><div class="stack" style="--n:__N__">__SHEETS__</div></div>
</div>
<script>
/* The stack. The paper in front is the one named in the address (/papers#no-early-warning), else the first. A change
   of paper has three parts: the text fades out, the sheets change depth, the text fades in at its new place. */
const stage = document.getElementById("stage"), stack = stage.firstElementChild, sheets = [...stack.children];
const still = matchMedia("(prefers-reduced-motion: reduce)");
const front = () => Math.max(0, sheets.findIndex(s => "#" + s.id === location.hash));
let timers = [];
function place() {
  const f = front();
  sheets.forEach((s, i) => { s.style.setProperty("--d", Math.abs(i - f)); s.classList.toggle("front", i === f); s.classList.toggle("before", i < f); });
}
function show(focus) {
  timers.forEach(clearTimeout);
  if (still.matches || sheets[front()].classList.contains("front")) { place(); return stack.classList.remove("moving"); }
  stack.classList.add("moving");
  timers = [setTimeout(() => { place(); if (focus) sheets[front()].querySelector(".open").focus({ preventScroll: true }); }, 140),
            setTimeout(() => stack.classList.remove("moving"), 620)];
}
function go(i, focus) { history.pushState(null, "", "#" + sheets[(i + sheets.length) % sheets.length].id); show(focus); }
stage.addEventListener("click", e => {
  const b = e.target.closest(".spine"); if (b) go(sheets.indexOf(b.parentElement), true);  // the strip goes: the focus moves to the paper's button
});
addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey || (e.key !== "ArrowRight" && e.key !== "ArrowLeft")) return;
  e.preventDefault(); go(front() + (e.key === "ArrowRight" ? 1 : -1));
});
addEventListener("popstate", () => show()); place();

/* The stack turns by about a degree, slowly, and leans a little toward the mouse. One smoothed value per axis and one
   transform per frame, so the two never fight. */
let tx = 0, ty = 0, lx = 0, ly = 0;
stage.addEventListener("pointermove", e => { const r = stage.getBoundingClientRect(); tx = (e.clientX - r.left) / r.width * 2 - 1; ty = (e.clientY - r.top) / r.height * 2 - 1; });
stage.addEventListener("pointerleave", () => { tx = ty = 0; });
function frame(t) {
  lx += (tx - lx) * .04; ly += (ty - ly) * .04;
  stack.style.transform = `rotateX(${(1 - ly * 1.2 + Math.sin(t / 5300) * .3).toFixed(3)}deg) rotateY(${(lx * 2 + Math.sin(t / 7900) * 1.1).toFixed(3)}deg)`;
  if (!still.matches) requestAnimationFrame(frame);
}
frame(0);

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
