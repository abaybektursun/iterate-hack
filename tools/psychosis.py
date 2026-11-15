"""A joke about ourselves: a thought record (the worksheet of cognitive therapy) for the team's own results.

Served at /psychosis by view.py; not a header tab. "AI psychosis" is an informal name for delusional beliefs after long
chatbot use, often a grand belief in special knowledge. The team's version of that belief is a result title. The page
takes one result of the board that has a caveat line (`plain` of /data: title, what, caveat) and walks it through the
worksheet with one button: the belief, the evidence for it (what), the evidence against it (caveat), the balanced
thought (the title with its caveat), and then the count of messages and board items the team's agents posted since the
page was opened. Every sentence about a result is the board's own text; nothing is invented. The belief is mirrored
in the address (/psychosis#result-95a4dc). Esc starts the belief again. The page reads /data every 10 s and never writes.
"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: AI psychosis</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
:root {  /* the tokens of architecture.py */
  color-scheme: light dark;
  --paper: #eceef0; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de; --blue: #1f43d6; --red: #c41e34;
  --btn: linear-gradient(#27323e, #0d141b); --btn-ink: #f5f8fa; --btn-edge: rgba(255, 255, 255, .18); --btn-drop: rgba(16, 24, 32, .42);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630; --blue: #8fb1ff; --red: #ff6b7c;
    --btn: linear-gradient(#f7fafc, #cbd5de); --btn-ink: #080c11; --btn-edge: rgba(255, 255, 255, .7); --btn-drop: rgba(0, 0, 0, .6);
  }
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.page { max-width: 1840px; min-height: 100vh; margin: 0 auto; padding: 20px 40px 24px; display: flex; flex-direction: column; }
.top { display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; }
.top a:hover { color: var(--ink); }
.status { margin-left: auto; color: var(--mute); white-space: nowrap; }
.status.bad { color: var(--red); }

.sheet { flex: 1; display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 72px; align-items: start; padding: 56px 0 40px; }
.label { font-size: 13px; font-weight: 600; color: var(--mute); margin: 0 0 12px; }
.belief { font-weight: 300; font-size: clamp(30px, 4.3vw, 66px); line-height: 1.08; letter-spacing: -.02em; margin: 0; text-wrap: balance; }
.belief .but { color: var(--blue); }
.belief .but.in { animation: but 1.4s cubic-bezier(.2, 0, .1, 1) both; }
@keyframes but { from { opacity: 0; letter-spacing: .06em; } }
.source { margin: 22px 0 0; font-size: 13px; color: var(--mute); }

.row { border-top: 1px solid var(--rule); padding: 16px 0 20px; min-height: 96px; }
.row p { margin: 0; font-size: 17px; line-height: 1.45; max-width: 60ch; }
.row.blank .label { color: var(--faint); opacity: .6; }
.go {
  margin-top: 12px; padding: 13px 26px; border-radius: 999px; font-weight: 600; color: var(--btn-ink); background: var(--btn);
  box-shadow: inset 0 1px 0 var(--btn-edge), 0 8px 20px -10px var(--btn-drop);
}
.foot { border-top: 1px solid var(--rule); padding-top: 14px; font-size: 13px; color: var(--mute); max-width: 110ch; }
@media (max-width: 900px) {
  .page { padding: 16px 16px 24px; }
  .top { gap: 13px; padding-bottom: 12px; }
  .name { font-stretch: 112%; margin-right: 0; }
  .status { display: none; }
  .sheet { display: block; padding: 28px 0 28px; }
  .rows { margin-top: 32px; }
  .row { min-height: 0; }
  .go { width: 100%; }
}
@media (prefers-reduced-motion: reduce) { .belief .but.in { animation: none; } }
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
    <span class="status" id="status" role="status">Reading the board</span>
  </header>
  <main class="sheet">
    <section>
      <p class="label">Therapy for AI psychosis: test one belief this team holds</p>
      <h2 class="belief" id="belief" aria-live="polite"></h2>
      <p class="source" id="source"></p>
    </section>
    <section class="rows">
      <div class="row blank" id="row1"><p class="label">Evidence for</p><p></p></div>
      <div class="row blank" id="row2"><p class="label">Evidence against</p><p></p></div>
      <div class="row blank" id="row3"><p class="label">Balanced thought</p><p></p></div>
      <div class="row blank" id="row4"><p class="label">Meanwhile</p><p></p></div>
      <button class="go" id="go">Test this belief</button>
    </section>
  </main>
  <p class="foot">This is a joke about ourselves: every belief here is a result title from our own board, and the evidence against it is that result's own caveat.
    &ldquo;AI psychosis&rdquo; is an informal name, not a diagnosis, for delusional beliefs after long chatbot use
    (<a href="https://www.apa.org/monitor/2026/09/ai-psychosis">American Psychological Association</a>), and that is not a joke.
    If a conversation with a chatbot frightens you, talk to a person you trust or to a doctor.</p>
</div>
<script>
const $ = id => document.getElementById(id);
const opened = Date.now() * 1e6;  // ns, the unit of the board's times
const BUTTON = ["Test this belief", "Now the evidence against", "Say the balanced thought", "Let it go", "Next belief"];
let data = null, beliefs = [], step = 0, readAt = "";

const lower = s => /^[A-Z][a-z]/.test(s) ? s[0].toLowerCase() + s.slice(1) : s;  // "One sample" joins a sentence; "RL" and "T 0.6" stay
const first = s => s.match(/^.*?[.;:](?=\s|$)/)?.[0].slice(0, -1) || s;  // the first sentence of a caveat, without its end mark
const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;
function current() { return beliefs.find(b => b.id === location.hash.slice(1)) || beliefs[0]; }

function meanwhile() {  // what the agents posted since this page was opened, from the last read
  const messages = data.messages.filter(m => parseInt(m.sk) > opened).length;
  const items = data.items.filter(i => i.at_ns > opened).length;
  if (!messages && !items) return "Since you opened this page your agents have posted nothing. It is quiet. Stay with that.";
  return `Since you opened this page your agents posted ${plural(messages, "message")} and ${plural(items, "board item")}. None of them needed you.`;
}

function draw(animate) {
  const b = current();
  if (!b) return;
  const fill = (id, on, text) => { $(id).classList.toggle("blank", !on); $(id).lastElementChild.textContent = on ? text : ""; };
  $("belief").textContent = b.title;
  if (step >= 3) {
    const but = document.createElement("span");
    but.className = "but" + (animate ? " in" : "");
    but.textContent = ", but " + lower(first(b.caveat)) + ".";
    $("belief").append(but);
  }
  $("source").innerHTML = `<a href="/#${b.id}">${b.id}</a>, belief ${beliefs.indexOf(b) + 1} of ${beliefs.length} on the board`;
  fill("row1", step >= 1, b.what);
  fill("row2", step >= 2, b.caveat);
  fill("row3", step >= 3, "Read the sentence again, out loud, with its new ending.");
  fill("row4", step >= 4, step >= 4 ? meanwhile() : "");
  $("go").textContent = BUTTON[step];
}

$("go").onclick = () => {
  if (step < 4) { step++; return draw(step === 3); }
  step = 0;
  const next = beliefs[(beliefs.indexOf(current()) + 1) % beliefs.length];
  if (next.id === location.hash.slice(1)) draw(); else location.hash = next.id;  // hashchange draws
};
addEventListener("hashchange", () => { step = 0; draw(); });
addEventListener("keydown", e => { if (e.key === "Escape") { step = 0; draw(); } });

async function read() {
  try {
    const r = await fetch("/data");
    if (!r.ok) throw new Error(r.status);
    data = await r.json();
    // a belief is a result with a caveat line, newest first where the board still lists it
    const at = Object.fromEntries(data.items.map(i => [i.id, i.at_ns]));
    beliefs = Object.entries(data.plain).filter(([, p]) => p.caveat && p.what).map(([id, p]) => ({ id, ...p }))
      .sort((a, b) => (at[b.id] || 0) - (at[a.id] || 0));
    readAt = new Date().toTimeString().slice(0, 5);
    $("status").className = "status";
    $("status").textContent = `${beliefs.length} beliefs with a caveat on the board`;
    draw();
  } catch (e) {
    $("status").className = "status bad";
    $("status").textContent = readAt ? `Offline, last read ${readAt}` : "Offline";
  }
}
read();
setInterval(read, 10000);
</script>
</body>
</html>
"""
