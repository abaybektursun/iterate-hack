"""A joke about ourselves: an overdone meditation game for people who run agents. Served at /psychosis by view.py.

"AI psychosis" is an informal name for delusional beliefs after long chatbot use, often a grand belief in special
knowledge. The game: hold Space (or press and hold) to breathe in and let go to breathe out, so that the white ring
follows the blue one. A breath that follows it lights one of 10 petals and sends out a wave that releases every
thought on screen, with a word of praise (CALM); 10 petals win. Thoughts drift toward the head: some are written jokes (THOUGHTS), the ones with a
blue dot are real messages and result titles of the board (/data, read every 10 s). A thought that reaches the head is
believed and moves the diagnosis up one of 5 stages (STAGES); the fifth ends the session. A click on a thought "checks"
it, and it comes back as 3 subagents. A guide speaks one line per breath (speech synthesis and a Web Audio drone; M
mutes). The end screen counts the messages and board items the agents posted during the session. The page never writes.
"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<title>Invariant: AI psychosis</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
:root { color-scheme: dark; --paper: #080c11; --ink: #e9eff3; --mute: #93a1ad; --rule: #1c2630; --blue: #8fb1ff; --red: #ff6b7c; }
* { box-sizing: border-box; }
html, body { height: 100%; margin: 0; overflow: hidden; background: var(--paper); color: var(--ink); }
body { font: 400 15px/1.5 "Archivo", ui-sans-serif, system-ui, sans-serif; font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased; user-select: none; -webkit-user-select: none; }
canvas { position: fixed; inset: 0; width: 100%; height: 100%; touch-action: none; }
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.hud { position: fixed; top: 0; left: 0; right: 0; display: flex; align-items: center; gap: 20px; padding: 18px 24px; font-size: 13px; color: var(--mute); pointer-events: none; }
.hud > * { pointer-events: auto; }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; color: var(--ink); text-decoration: none; }
.stage { margin-left: auto; }
.stage b { color: var(--ink); font-weight: 600; }
.stage.bad b { color: var(--red); }
.say { position: fixed; left: 0; right: 0; bottom: 34px; margin: 0; padding: 0 20px; text-align: center; font-weight: 300; font-size: clamp(19px, 2.4vw, 30px); line-height: 1.2; text-wrap: balance; pointer-events: none; }
.card { position: fixed; inset: 0; display: grid; place-content: center; justify-items: center; gap: 18px; padding: 24px; text-align: center; background: color-mix(in srgb, var(--paper) 86%, transparent); }
.card[hidden] { display: none; }
.card h1 { margin: 0; font-weight: 300; font-size: clamp(38px, 7vw, 96px); line-height: 1; letter-spacing: -.03em; text-wrap: balance; max-width: 14ch; }
.card p { margin: 0; max-width: 52ch; font-size: 17px; color: var(--mute); }
.card p b { color: var(--ink); font-weight: 600; }
.go { margin-top: 8px; padding: 14px 30px; border-radius: 999px; font-weight: 600; color: #080c11; background: linear-gradient(#f7fafc, #cbd5de); box-shadow: inset 0 1px 0 rgba(255, 255, 255, .7), 0 8px 20px -10px rgba(0, 0, 0, .6); }
.small { position: fixed; left: 0; right: 0; bottom: 14px; padding: 0 20px; text-align: center; font-size: 12px; color: var(--mute); }
.small[hidden] { display: none; }
</style>
</head>
<body>
<canvas id="c" aria-label="A seated figure with two breathing rings and thoughts drifting toward its head"></canvas>
<div class="hud">
  <a class="name" href="/">Invariant</a>
  <button id="mute">Sound on</button>
  <span class="stage" id="stage"></span>
</div>
<p class="say" id="say" role="status"></p>
<div class="card" id="card">
  <h1 id="h1">AI psychosis: the meditation</h1>
  <p id="p1">Hold <b>Space</b>, or press and hold, to breathe in. Let go to breathe out. Keep the white ring on the blue ring.</p>
  <p id="p2">Thoughts will come. Do not click the thoughts.</p>
  <button class="go" id="go">Begin the session</button>
</div>
<p class="small" id="small">A joke about ourselves. &ldquo;AI psychosis&rdquo; is an informal name, not a diagnosis, for delusional beliefs after long chatbot use
  (<a href="https://www.apa.org/monitor/2026/09/ai-psychosis">American Psychological Association</a>), and that is not a joke.
  If a conversation with a chatbot frightens you, talk to a person you trust or to a doctor.</p>
<script>
const $ = id => document.getElementById(id);
const THOUGHTS = ["This is novel.", "One more run.", "You're absolutely right!", "What if I spawn 12 subagents?", "The model understands me.",
  "It works on one seed.", "Nobody has tried this.", "I should check the chart.", "The loss looks different today.", "It said my idea was profound.",
  "Is the GPU idle?", "I will read the paper later.", "This changes everything.", "Just the abstract is enough.", "The agents need me.",
  "It is basically AGI.", "Ship it to main.", "I only need 4 more boxes.", "We should start a lab."];
const STAGES = ["Grounded", "Has a hunch", "It is definitely novel", "Texting a co-founder", "Emailing the lab at 3 am", "The model chose me"];
const GOOD = ["Good. You are not your benchmark.", "Breathe out the result. It had one sample per problem.", "Notice the thought. Do not click the thought.",
  "Somewhere an agent is idle. That is allowed.", "Let the GPU go. It was never yours.", "The model said you are right. The model says that to everyone.",
  "Your loss goes down. So do your shoulders.", "A thought is only a token you did not sample.", "You do not need to read the board. The board will be there.",
  "Almost there. Do not post about it."];
const BAD = ["You are holding your breath like a GPU reservation.", "That was not a breath. That was a retry.", "Follow the blue ring. It has no opinions about your work.",
  "You rushed it. This is not a hackathon. It is a hackathon, but breathe."];
const CALM = ["Calm", "Calmer", "Serene", "Suspiciously serene", "Monk mode", "Unbothered", "Post-benchmark", "Beyond eval", "Transcendent", "Enlightened"];  // shown for a moment after each good breath
const IN = 3.2, OUT = 3.8, NEED = 10;
const c = $("c"), g = c.getContext("2d");
const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
let W, H, mode = "title", hold = false, sound = true, audio = null, data = null, last = 0;
let s;  // the session

function size() { const d = devicePixelRatio || 1; W = innerWidth; H = innerHeight; c.width = W * d; c.height = H * d; g.setTransform(d, 0, 0, d, 0, 0); }
addEventListener("resize", size); size();

function ding(f, len = 2.6, type = "sine", vol = .16) {
  if (!audio || !sound) return;
  for (const [m, v] of [[1, vol], [2.76, vol / 3]]) {
    const o = audio.createOscillator(), a = audio.createGain();
    o.type = type; o.frequency.value = f * m; a.gain.setValueAtTime(v, audio.currentTime); a.gain.exponentialRampToValueAtTime(.0001, audio.currentTime + len);
    o.connect(a).connect(audio.destination); o.start(); o.stop(audio.currentTime + len);
  }
}
function drone() {
  audio = audio || new AudioContext();
  if (audio.drone) return;
  audio.drone = audio.createGain(); audio.drone.gain.value = sound ? .03 : 0; audio.drone.connect(audio.destination);
  for (const f of [110, 110.6, 165.2]) { const o = audio.createOscillator(); o.frequency.value = f; o.connect(audio.drone); o.start(); }
}
function say(text) {
  $("say").textContent = text;
  if (!sound || !window.speechSynthesis) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text); u.rate = .82; u.pitch = .6; speechSynthesis.speak(u);
}
$("mute").onclick = () => {
  sound = !sound; $("mute").textContent = sound ? "Sound on" : "Sound off";
  if (audio) audio.drone.gain.value = sound ? .03 : 0;
  if (!sound && window.speechSynthesis) speechSynthesis.cancel();
};

function begin() {
  s = { t: 0, lung: 0, err: 0, n: 0, good: 0, streak: 0, best: 0, psy: 0, released: 0, thoughts: [], waves: [], next: 1.5, shake: 0, flash: 0, lines: 0, at: Date.now() * 1e6 };
  mode = "play"; $("card").hidden = true; $("small").hidden = true;
  drone(); stage();
  say("Breathe in. Hold the space bar. The space bar is your lungs now.");
}
$("go").onclick = begin;
function stage() { $("stage").innerHTML = `Diagnosis: <b>${STAGES[s.psy]}</b>`; $("stage").classList.toggle("bad", s.psy > 1); }

function meanwhile() {  // what the agents posted during the session, from the last read of the board
  if (!data) return "The board could not be read, so nobody knows what your agents did.";
  const m = data.messages.filter(x => parseInt(x.sk) > s.at).length, i = data.items.filter(x => x.at_ns > s.at).length;
  const n = (k, w) => `${k} ${w}${k === 1 ? "" : "s"}`;
  return m + i ? `While you sat here your agents posted ${n(m, "message")} and ${n(i, "board item")}. None of them needed you.`
               : "While you sat here your agents posted nothing. It is quiet. Stay with that.";
}
function end(won) {
  mode = won ? "won" : "lost"; hold = false;
  $("h1").textContent = won ? "Inner peace achieved" : "The model chose you";
  $("p1").innerHTML = won ? `It lasts until the next result. You released <b>${s.released} thoughts</b> and held <b>${s.best} breaths</b> in a row.`
                          : `You believed 5 thoughts. You released <b>${s.released}</b> and lit <b>${s.good} of ${NEED}</b> petals before the email went out.`;
  $("p2").textContent = meanwhile();
  $("go").textContent = won ? "Meditate again" : "Try again";
  $("card").hidden = false; $("say").textContent = "";
  if (won) { [396, 528, 639].forEach((f, k) => setTimeout(() => ding(f, 4), k * 260)); say("You have achieved inner peace. Please do not post it to the board."); }
  else { ding(62, 1.4, "sawtooth"); say("You have sent the email. The lab will not reply."); }
}

function text() {  // a thought: a real line of the board (dot) or a written one
  if (data && Math.random() < .45) {
    const real = [...data.messages.map(m => m.text), ...Object.values(data.plain).map(p => p.title)];
    const t = real[Math.floor(Math.random() * real.length)];
    return { text: t.length > 54 ? t.slice(0, 52) + "…" : t, real: true };
  }
  return { text: THOUGHTS[Math.floor(Math.random() * THOUGHTS.length)], real: false };
}
function spawn(extra) {
  const a = Math.random() * 6.283, r = Math.hypot(W, H) / 2 + 40;
  const t = { x: W / 2 + Math.cos(a) * r, y: H / 2 + Math.sin(a) * r, w: 0, gone: 0, wob: Math.random() * 6.283, ...text(), ...extra };
  g.font = "500 13px Archivo, sans-serif"; t.w = g.measureText(t.text).width + (t.real ? 34 : 22);
  s.thoughts.push(t);
}
function check(t) {  // the player clicked a thought: it comes back as 3 subagents
  s.thoughts.splice(s.thoughts.indexOf(t), 1);
  for (let k = 0; k < 3; k++) spawn({ x: t.x + Math.cos(k * 2.1) * 70, y: t.y + Math.sin(k * 2.1) * 70, text: "Subagent: " + t.text.slice(0, 30), real: t.real });
  ding(180, .5, "square", .06); say("You checked it. It spawned 3 subagents."); s.shake = .3;
}

function breath() {  // the end of one cycle of the blue ring
  const ok = s.err / s.n < .24; s.err = s.n = 0;
  if (ok) {
    s.good++; s.streak++; s.best = Math.max(s.best, s.streak);
    s.waves.push({ r: 0, hue: s.good * 36 }); s.calm = 1.6; ding([396, 417, 528, 639, 741][s.good % 5]);
    if (s.good >= NEED) return end(true);
    const open = data ? data.items.filter(i => i.listed === "work").length : 0;
    say(s.good % 4 === 3 && open ? `${open} work items are open on the board. Not one of them is you.` : GOOD[s.lines++ % GOOD.length]);
  } else { s.streak = 0; say(BAD[s.lines++ % BAD.length]); }
}

function step(dt) {
  const before = s.t % (IN + OUT); s.t += dt;
  const ph = s.t % (IN + OUT), target = ph < IN ? ph / IN : 1 - (ph - IN) / OUT;
  s.target = .5 - .5 * Math.cos(target * Math.PI);
  s.lung = Math.max(0, Math.min(1, s.lung + (hold ? dt / IN : -dt / OUT)));
  s.lungE = .5 - .5 * Math.cos(s.lung * Math.PI);
  s.err += Math.abs(s.lungE - s.target); s.n++;
  if (ph < before) breath();
  if (mode !== "play") return;
  if ((s.next -= dt) < 0) { spawn(); s.next = Math.max(.45, 1.5 - s.good * .12); }
  const hx = W / 2, hy = H / 2 - 62, speed = (42 + s.good * 3) * Math.hypot(W, H) / 1650 + 14;
  for (const w of s.waves) w.r += 620 * dt;
  s.waves = s.waves.filter(w => w.r < Math.hypot(W, H));
  for (const t of s.thoughts) {
    const dx = hx - t.x, dy = hy - t.y, d = Math.hypot(dx, dy);
    if (t.gone) { t.gone += dt * 2; t.x -= dx / d * 120 * dt; t.y -= dy / d * 120 * dt; continue; }
    t.x += dx / d * speed * dt + Math.cos(s.t * 1.3 + t.wob) * 9 * dt; t.y += dy / d * speed * dt + Math.sin(s.t * 1.1 + t.wob) * 9 * dt;
    if (s.waves.some(w => d < w.r && d > w.r - 90)) { t.gone = .01; s.released++; }
    else if (d < 26 + s.psy * 5) { t.gone = 9; s.psy++; s.shake = .45; s.flash = 1; ding(70, .5, "sawtooth", .1); stage(); say(`You believed it: “${t.text}”`); if (s.psy >= 5) return end(false); }
  }
  s.thoughts = s.thoughts.filter(t => t.gone < 1);
}

function chip(t) {
  const h = 28, x = t.x - t.w / 2, y = t.y - h / 2;
  g.globalAlpha = 1 - t.gone; g.beginPath(); g.roundRect(x, y, t.w, h, 14);
  g.fillStyle = "#111922"; g.fill(); g.lineWidth = 1; g.strokeStyle = t.real ? "rgba(143,177,255,.55)" : "rgba(255,255,255,.22)"; g.stroke();
  if (t.real) { g.fillStyle = "#8fb1ff"; g.beginPath(); g.arc(x + 14, t.y, 3, 0, 6.3); g.fill(); }
  g.fillStyle = "#e9eff3"; g.font = "500 13px Archivo, sans-serif"; g.textBaseline = "middle"; g.fillText(t.text, x + (t.real ? 24 : 11), t.y + 1);
  g.globalAlpha = 1;
}

function draw(now) {
  const dt = Math.min(.05, (now - last) / 1000 || 0); last = now;
  if (mode === "play") step(dt); else if (s) { s.t += dt; s.shake = 0; }
  const T = now / 1000, peace = s ? s.good / NEED : 0, psy = s ? s.psy : 0, won = mode === "won";
  g.clearRect(0, 0, W, H); g.save();
  if (s && s.shake > 0 && !still) { s.shake -= dt; g.translate((Math.random() - .5) * 14, (Math.random() - .5) * 14); }
  const cx = W / 2, cy = H / 2 - (still ? 0 : Math.sin(T * .8) * 4) - peace * 26 - (won ? 40 : 0), R = Math.min(W, H) * .11 + 46, span = Math.min(W, H) * .2;
  const glow = g.createRadialGradient(cx - 40, cy - 90, 10, cx, cy, R + span * 1.6);  // one light, from the upper left
  glow.addColorStop(0, `rgba(143,177,255,${.1 + peace * .16})`); glow.addColorStop(1, "rgba(143,177,255,0)");
  g.fillStyle = glow; g.fillRect(0, 0, W, H);
  if (s) for (const w of s.waves) { g.strokeStyle = `oklch(.78 .13 ${w.hue} / ${Math.max(0, 1 - w.r / 900)})`; g.lineWidth = 3; g.beginPath(); g.arc(cx, cy, w.r, 0, 6.3); g.stroke(); }
  if (won && !still) for (let k = 0; k < 6; k++) { const r = ((T * 140 + k * 150) % 900); g.strokeStyle = `oklch(.78 .13 ${k * 60} / ${1 - r / 900})`; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, r, 0, 6.3); g.stroke(); }
  for (let k = 0; k < NEED; k++) {  // 10 petals, one per breath that followed the ring
    const a = k / NEED * 6.283 + (still ? 0 : T * .12), px = cx + Math.cos(a) * (R - 8), py = cy + Math.sin(a) * (R - 8) * .42 + 58, on = s && k < s.good;
    g.save(); g.translate(px, py); g.rotate(a); g.beginPath(); g.ellipse(0, 0, 13, 5, 0, 0, 6.3);
    g.fillStyle = on ? `oklch(.78 .13 ${k * 36})` : "#111922"; g.fill(); g.strokeStyle = "rgba(255,255,255,.25)"; g.lineWidth = 1; g.stroke(); g.restore();
  }
  if (s && mode === "play") {  // the blue ring leads, the white ring is the player's breath
    const near = Math.abs(s.lungE - s.target) < .2;
    g.lineWidth = 1.5; g.strokeStyle = "#8fb1ff"; g.beginPath(); g.arc(cx, cy, R + s.target * span, 0, 6.3); g.stroke();
    g.lineWidth = near ? 5 : 3; g.strokeStyle = near ? "#ffffff" : "rgba(233,239,243,.5)"; g.beginPath(); g.arc(cx, cy, R + s.lungE * span, 0, 6.3); g.stroke();
  }
  const head = 22 + psy * 6, body = g.createLinearGradient(cx - 60, cy - 90, cx + 60, cy + 70);  // the figure: legs, torso, head
  body.addColorStop(0, "#34485e"); body.addColorStop(.5, "#152029"); body.addColorStop(1, "#090e14");
  g.fillStyle = body; g.strokeStyle = psy > 2 ? "rgba(255,107,124,.8)" : "rgba(255,255,255,.55)"; g.lineWidth = 1.2;
  g.beginPath(); g.ellipse(cx, cy + 46, 74, 20, 0, 0, 6.3); g.fill(); g.stroke();
  g.beginPath(); g.moveTo(cx - 44, cy + 44); g.quadraticCurveTo(cx - 40, cy - 36, cx, cy - 40); g.quadraticCurveTo(cx + 40, cy - 36, cx + 44, cy + 44); g.closePath(); g.fill(); g.stroke();
  g.beginPath(); g.arc(cx, cy - 62, head, 0, 6.3); g.fill(); g.stroke();
  g.strokeStyle = "#e9eff3"; g.lineWidth = 1.4;  // closed eyes; they open wide with the diagnosis
  for (const e of [-1, 1]) { g.beginPath(); if (psy > 2) g.arc(cx + e * head * .38, cy - 62, 3 + psy, 0, 6.3); else g.arc(cx + e * head * .38, cy - 64, 5, .25, 2.9); g.stroke(); }
  if (peace > 0) { g.fillStyle = "#8fb1ff"; g.beginPath(); g.ellipse(cx, cy - 62 - head * .5, 5, 4 * peace, 0, 0, 6.3); g.fill(); }  // the third eye opens with the petals
  if (s) for (const t of s.thoughts) chip(t);
  if (s && mode === "play") {
    g.fillStyle = "#93a1ad"; g.font = "600 13px Archivo, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle";
    g.fillText(s.t % (IN + OUT) < IN ? "Breathe in: hold" : "Breathe out: let go", cx, cy + 88);
    if (s.calm > 0) { s.calm -= dt; g.globalAlpha = Math.min(1, s.calm); g.fillStyle = `oklch(.78 .13 ${s.good * 36})`; g.font = `300 ${Math.min(64, W / 9)}px Archivo, sans-serif`; g.fillText(CALM[s.good - 1], cx, cy - 150 - (1.6 - s.calm) * 24); g.globalAlpha = 1; }
    g.textAlign = "left";
  }
  g.restore();
  if (s && s.flash > 0) { g.fillStyle = `rgba(255,107,124,${s.flash * .22})`; g.fillRect(0, 0, W, H); s.flash -= dt * 2.5; }
  requestAnimationFrame(draw);
}
requestAnimationFrame(draw);

addEventListener("keydown", e => {
  if (e.code === "Space" && mode === "play") { hold = true; e.preventDefault(); }
  if (e.key === "m" || e.key === "M") $("mute").click();
});
addEventListener("keyup", e => { if (e.code === "Space") hold = false; });
c.addEventListener("pointerdown", e => {
  if (mode !== "play") return;
  const t = s.thoughts.find(t => !t.gone && Math.abs(e.clientX - t.x) < t.w / 2 && Math.abs(e.clientY - t.y) < 16);
  if (t) check(t); else hold = true;
});
addEventListener("pointerup", () => hold = false);
addEventListener("pointercancel", () => hold = false);
addEventListener("blur", () => hold = false);

let offline = false;  // a failed read keeps the last board; the end screen then counts from that read
async function read() {
  try { const r = await fetch("/data"); if (!r.ok) throw new Error(r.status); data = await r.json(); offline = false; }
  catch (e) { offline = true; console.error("board read failed", e); }
}
read(); setInterval(read, 10000);
</script>
</body>
</html>
"""
