"""Write studies/sitelab/index.html, the Lab page of the team site (/lab/): the list of the pictures and one preview.

  python3 studies/sitelab/build_index.py

The page follows .claude/skills/site-ui/SKILL.md: the tokens, the type and the header of tools/findings.py, a flat
column of words, hairlines, one lit object (the preview, lit from the upper left). Each picture's still,
prototypes/<slug>/shot.webp, is written into the page as a data URI, so the page is one request: the site allows 3
requests a second, and one image request per picture would be refused.
"""
import base64
from pathlib import Path

HERE = Path(__file__).parent

# slug, name, one sentence, where its data comes from; in the order shown
PICTURES = [
    ("crystal", "Our results, crystal-maxxed", "One crystal for each result on the board, grown by a stated rule. The healing-crystal shop on Valencia could never.", "Board, live"),
    ("model-interior", "Inside the model's head, literally", "The 32 layers, the directions RL changed in each matrix, and the loop neurons behind answers that repeat themselves forever.", "Weight readouts"),
    ("token-flow", "Finish the thought or hit the cap", "Each stored answer falls by its token count and either finishes or gets cut off at the cap mid-yap.", "Rows per answer"),
    ("weight-space", "Weight arithmetic on a dial", "Every model made by adding weight changes together, with a dial over how hard the edit is sent. No thoughts, just vectors.", "Stored readouts"),
    ("problem-field", "Every problem is a bead", "One bead for each problem slides between right and wrong as the configuration changes. You can watch the vibe shift.", "Rows per problem"),
    ("score-terrain", "Number go up, in plaster", "Every posted score of one benchmark as a plaster relief, with the best so far as a thread. The hill we climb, rendered as an actual hill.", "Scores, live"),
    ("forecast-range", "Called it (or did we)", "Each theory's forecasts, locked in before the numbers were measured, against what landed. Receipts, not vibes.", "Theory rounds"),
    ("time-helix", "The grind, as a spiral", "Items, messages, commits, GPU jobs and scores at their real times, one turn for each hour. Sleep does not appear.", "Board, git, jobs"),
    ("repo-city", "Repo city", "One block for each file, as tall as its line count, replayed commit by commit. Builds faster than anything SF has permitted.", "Git history"),
    ("lineage", "Who cited whom", "Which board item cites which, regrown from the first hour. The family tree of every take.", "Board references"),
    ("trace-ribbons", "What the agents do all day", "Each agent session as a wire, each tool call as a bead, each subagent as a branch. Proof they were locked in.", "One laptop's transcripts"),
    ("physics-board", "The board, but throwable", "Every board item as a rigid body to grab, throw and sort. For when the to-do list deserves to be yeeted.", "Board, live"),
    ("one-take", "The whole thing in one take", "Ninety seconds, one camera move, 500 brass pins: the plain base, the opening cue, the vote, the weight edit and RL, each counted on the same problems. No cuts, we are not cowards.", "Rows per problem"),
    ("vote-machine", "Democracy, for samples", "Four samples of each problem drop as balls into a ballot cabinet and the tallest stack wins. Pull the lever and watch the vote fix what one sample got wrong.", "Rows per sample"),
    ("tide", "Rising tide, 500 stones", "One stone for each MATH-500 problem, easiest to hardest, flooded to the level each configuration reaches. The islands are the problems that break the order.", "Rows per problem"),
    ("call-it", "Call the number", "A game: set your forecast on a slide rule before the measured number is shown, scored by the same rule as the team's theories. Humbling, in a healthy way.", "Theory forecasts"),
    ("music-box", "The hackathon, as a music box", "Every commit, board item, message and score is a pin on a brass cylinder that plucks a steel comb. Turn the crank to hear two days of work. Sound on.", "Board, git"),
    ("mobile", "Who is carrying what", "A hanging mobile balanced by real physics: one leaf for each open work item, live. It leans toward whoever holds the most. You can blow on it.", "Board, live"),
    ("ledger", "What a point costs", "A brass balance that weighs each method's tokens per problem against the accuracy points it bought, next to RL's price.", "Scores, live"),
    ("library", "The reading list, shelved", "One book for each paper the agents read before running anything. Pull one out and it opens on the findings recorded from it. Yes, they did the reading.", "Paper records"),
]

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: AI Psychosis maxxing</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens and the light of tools/architecture.py, as in tools/findings.py. The light comes from the upper left. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0;
  }
}
* { box-sizing: border-box; }
html { background: var(--paper); overflow-x: clip; }  /* the glow around the plate reaches past the page edge */
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
a { color: inherit; text-decoration: none; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.page { max-width: 1840px; margin: 0 auto; padding: 20px 40px 72px; }
.top { display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }

.lab { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: 0 clamp(40px, 5.5vw, 104px); align-items: start; }
.say { margin: clamp(28px, 7vh, 76px) 0 0; max-width: 21ch; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; }
.eyebrow { margin: clamp(28px, 7vh, 76px) 0 0; color: var(--blue); font-size: 13px; font-weight: 640; font-stretch: 112%; letter-spacing: .01em; }
.eyebrow + .say { margin-top: 12px; }
.note { margin: 18px 0 0; max-width: 46ch; color: var(--mute); font-size: 14.5px; line-height: 1.42; }

.rows { list-style: none; margin: clamp(30px, 6vh, 60px) 0 0; padding: 0; border-bottom: 1px solid var(--rule); }
.rows li { border-top: 1px solid var(--rule); animation: fade .7s calc(var(--i) * 50ms) both; }
.row { display: grid; grid-template-columns: 3.4ch minmax(0, 1fr) auto; gap: 0 18px; align-items: baseline; padding: 15px 0 17px; }
.row:focus-visible { outline-offset: 2px; border-radius: 4px; }
.n { color: var(--faint); font-size: 12.5px; transition: color .15s ease; }
.title { margin: 0; font-size: 17.5px; line-height: 1.22; font-weight: 600; font-stretch: 106%; letter-spacing: .004em; transition: color .15s ease; }
.line { margin: 5px 0 0; max-width: 52ch; color: var(--mute); font-size: 14.5px; line-height: 1.42; }
.src { color: var(--faint); font-size: 12.5px; white-space: nowrap; }
.row.on .title, .row:hover .title { color: var(--blue); }
.row.on .n, .row:hover .n { color: var(--ink); }
.row img { display: none; }

/* The one object: the picture of the chosen row, a plate lit from the upper left */
.stage { position: sticky; top: 0; height: 100vh; max-height: 1100px; display: flex; flex-direction: column; justify-content: center; padding: 28px 0; perspective: 1800px; animation: fade 1.1s .15s both; }
.plate { position: relative; display: block; transform-style: preserve-3d; will-change: transform; }
.plate::before { content: ""; position: absolute; inset: -9% -4%; border-radius: 50%; opacity: calc(var(--glow) * .5); pointer-events: none;
  background: radial-gradient(closest-side, color-mix(in srgb, var(--blue) 15%, transparent), transparent); }
.plate::after { content: ""; position: absolute; left: 5%; right: 5%; bottom: -5%; height: 9%; border-radius: 50%; opacity: calc(var(--shadow) * .5); pointer-events: none;
  background: radial-gradient(closest-side, color-mix(in srgb, var(--ink) 34%, transparent), transparent); filter: blur(10px); }
.rim { position: relative; z-index: 1; display: block; padding: 1px; border-radius: 7px; background: linear-gradient(128deg, var(--rim-a), var(--rim-b) 56%, var(--rim-c)); }
.glass { position: relative; display: block; aspect-ratio: 16 / 10; border-radius: 6px; overflow: hidden; background: #0c0b0a; }
.glass img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity .55s ease; }
.glass img.in { opacity: 1; }
.glass::after { content: ""; position: absolute; inset: 0; pointer-events: none; background: linear-gradient(128deg, rgba(255, 255, 255, .07), transparent 34%); }
.cap { position: relative; z-index: 1; display: flex; justify-content: space-between; gap: 24px; margin-top: 16px; color: var(--faint); font-size: 13px; }
.cap b { color: var(--mute); font-weight: 520; font-stretch: 104%; }

@keyframes fade { from { opacity: 0; } }
@media (max-width: 1000px) {
  .page { padding: 16px 16px 48px; }
  .top { gap: 13px; padding-bottom: 12px; }
  .name { font-stretch: 112%; margin-right: 0; }
  .lab { display: block; }
  .eyebrow { margin-top: 22px; }
  .say { font-size: 23px; max-width: none; }
  .stage { display: none; }
  .row { grid-template-columns: 3.4ch minmax(0, 1fr); padding: 18px 0 20px; }
  .src { grid-column: 2; margin-top: 6px; white-space: normal; }
  .row img { display: block; grid-column: 1 / -1; width: 100%; height: auto; aspect-ratio: 16 / 10; margin-bottom: 14px; border-radius: 5px; border: 1px solid var(--rule); }
}
@media (prefers-reduced-motion: reduce) {
  .rows li, .stage { animation: none; }
  .glass img, .title, .n, .top a { transition: none; }
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
  <main class="lab">
    <div>
      <p class="eyebrow">AI Psychosis maxxing</p>
      <p class="say">We were told to touch grass. Instead we built __COUNT__ 3D pictures of our own research.</p>
      <p class="note">Every picture is drawn from the team's real data, no vibes-only renders. Agents built one idea each, fully locked in. These are prototypes: they run best on a desktop with a graphics card.</p>
      <ol class="rows" id="rows">__ROWS__</ol>
    </div>
    <aside class="stage" aria-hidden="true">
      <a class="plate" id="plate" tabindex="-1" href="#">
        <span class="rim"><span class="glass"><img id="ia" alt=""><img id="ib" alt=""></span></span>
      </a>
      <div class="cap"><b id="cname"></b><span id="cnum"></span></div>
    </aside>
  </main>
</div>
<script>
const $ = id => document.getElementById(id);
const rows = [...document.querySelectorAll(".row")];
const still = matchMedia("(prefers-reduced-motion: reduce)");
let on = -1, front = $("ia"), back = $("ib");

/* The preview shows the picture of the row under the pointer or the focus; the first row before any. */
function show(k) {
  if (k === on) return;
  on = k;
  rows.forEach((r, i) => r.classList.toggle("on", i === k));
  const r = rows[k];
  back.src = r.querySelector("img").src;
  back.classList.add("in"); front.classList.remove("in");
  [front, back] = [back, front];
  $("plate").href = r.getAttribute("href");
  $("cname").textContent = r.querySelector(".title").textContent;
  $("cnum").textContent = String(k + 1).padStart(2, "0") + " / " + rows.length;
}
rows.forEach((r, k) => { r.addEventListener("pointerenter", () => show(k)); r.addEventListener("focus", () => show(k)); });
show(0);

/* The plate leans a few degrees toward the pointer and settles back. */
let tx = 0, ty = 0, x = 0, y = 0, raf = 0;
function lean() {
  x += (tx - x) * .07; y += (ty - y) * .07;
  $("plate").style.transform = "rotateY(" + (x * 5).toFixed(3) + "deg) rotateX(" + (-y * 4).toFixed(3) + "deg)";
  raf = Math.abs(tx - x) + Math.abs(ty - y) > .001 ? requestAnimationFrame(lean) : 0;
}
addEventListener("pointermove", e => {
  if (still.matches || e.pointerType === "touch") return;
  tx = e.clientX / innerWidth - .5; ty = e.clientY / innerHeight - .5;
  if (!raf) raf = requestAnimationFrame(lean);
});
document.documentElement.addEventListener("pointerleave", () => { tx = ty = 0; if (!raf && !still.matches) raf = requestAnimationFrame(lean); });
</script>
</body>
</html>
"""

ROW = ('<li style="--i:{i}"><a class="row" href="prototypes/{slug}/">'
       '<img alt="" width="1120" height="700" src="data:image/webp;base64,{shot}">'
       '<span class="n">{n:02d}</span><span><h2 class="title">{name}</h2><p class="line">{line}</p></span>'
       '<span class="src">{src}</span></a></li>')

if __name__ == "__main__":
    rows = "".join(ROW.format(i=i, n=i + 1, slug=slug, name=name, line=line, src=src,
                              shot=base64.b64encode((HERE / "prototypes" / slug / "shot.webp").read_bytes()).decode())
                   for i, (slug, name, line, src) in enumerate(PICTURES))
    count = {12: "twelve", 20: "twenty"}.get(len(PICTURES), str(len(PICTURES)))
    (HERE / "index.html").write_text(PAGE.replace("__ROWS__", rows).replace("__COUNT__", count))
    print(f"wrote index.html, {len(PICTURES)} pictures, {(HERE / 'index.html').stat().st_size // 1024} kB")
