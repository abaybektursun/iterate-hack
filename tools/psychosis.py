"""A joke about ourselves: an overdone meditation game for people who run agents. Served at /psychosis by view.py.

"AI psychosis" is an informal name for delusional beliefs after long chatbot use, often a grand belief in special
knowledge. The game is a retreat of 5 levels (LEVELS). Hold Space (or press and hold) to breathe in and let go to
breathe out, so that the white ring follows the blue one. A breath that follows it is good or perfect: it scores, raises
the streak multiplier, charges the Om (key O or the button: clears the screen) and sends out a wave that releases
thoughts into their letters. Thoughts are bodies: they are pulled to the meditator (an emoji, FACES), collide, and are
held off by the white ring for a while. Some are written jokes (THOUGHTS); the ones with a blue dot are real messages
and result titles of the board (/data, read every 10 s). A thought that reaches the meditator is believed and moves the
diagnosis up one of 5 stages (STAGES); the fifth ends the session. A click on a thought brings it back as 3 subagents.
From level 2 on there are kinds (KIND): fast pings, hype that grows, reviewers that take two waves. After a level's
breaths its boss arrives, a heavy thought that sends out its own kind and that each good wave weakens once it is close
enough. After each boss the player picks one of three practices (PERKS) that stay. After level 5 the retreat can go on
without end (samsara), harder each round. Power-ups (POWER) are caught by
the white ring while it is on the blue one. The 2D canvas is not shown: a WebGL fragment shader draws fog that follows the
breath and turns red with the diagnosis, and over it the canvas with glow, ripples under each wave and a colour split. Sound: a drone with one more layer per level, 8 plucked notes per breath, a pentatonic note per good
breath, a spoken guide (M mutes). The end screen gives score, rank, achievements (ACH) and what the agents posted during
the session; the best score is kept in the browser. Spawns use a random generator seeded with the date, so a day's
retreat is the same for everyone. No image files and no drawn figures: emoji, type, rings and the shader.
"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<title>Invariant: AI Psychosis detox</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
:root { color-scheme: dark; --paper: #080c11; --ink: #e9eff3; --mute: #93a1ad; --blue: #8fb1ff; --red: #ff6b7c; }
* { box-sizing: border-box; }
html, body { height: 100%; margin: 0; overflow: hidden; background: var(--paper); color: var(--ink); }
body { font: 400 15px/1.5 "Archivo", ui-sans-serif, system-ui, sans-serif; font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased; user-select: none; -webkit-user-select: none; }
canvas { position: fixed; inset: 0; width: 100%; height: 100%; touch-action: none; }
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.hud { position: fixed; top: 0; left: 0; right: 0; display: flex; flex-wrap: wrap; align-items: center; gap: 4px 20px; padding: 16px 24px; font-size: 13px; color: var(--mute); pointer-events: none; }
.hud > * { pointer-events: auto; }
.hud b { color: var(--ink); font-weight: 600; }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; color: var(--ink); text-decoration: none; }
.right { margin-left: auto; display: flex; gap: 20px; }
.bad b { color: var(--red); }
.say { position: fixed; left: 0; right: 0; bottom: 34px; margin: 0; padding: 0 20px; text-align: center; font-weight: 300; font-size: clamp(18px, 2.3vw, 29px); line-height: 1.2; text-wrap: balance; pointer-events: none; text-shadow: 0 0 18px var(--paper); }
.toast { position: fixed; top: 58px; left: 50%; translate: -50% 0; padding: 9px 18px; border-radius: 999px; background: #111922; border: 1px solid rgba(143, 177, 255, .5); font-size: 13px; font-weight: 600; white-space: nowrap; transition: opacity .4s; }
.toast[hidden] { display: block; opacity: 0; pointer-events: none; }
.card { position: fixed; inset: 0; display: grid; place-content: center; justify-items: center; gap: 16px; padding: 24px; text-align: center; background: color-mix(in srgb, var(--paper) 90%, transparent); }
.card[hidden], .om[hidden], .small[hidden], #copy[hidden], #go[hidden], #more[hidden], .perks[hidden] { display: none; }
.perks { display: grid; gap: 10px; width: min(460px, 86vw); }
.perks .go { margin: 0; border-radius: 16px; padding: 12px 20px; text-align: left; display: grid; }
.perks .go span { font-weight: 400; font-size: 13px; }
.card h1 { margin: 0; font-weight: 300; font-size: clamp(38px, 7vw, 92px); line-height: 1; letter-spacing: -.03em; text-wrap: balance; max-width: 14ch; }
.card p { margin: 0; max-width: 56ch; font-size: 16px; color: var(--mute); }
.card p b { color: var(--ink); font-weight: 600; }
.go, .om { padding: 14px 30px; border-radius: 999px; font-weight: 600; color: #080c11; background: linear-gradient(#f7fafc, #cbd5de); box-shadow: inset 0 1px 0 rgba(255, 255, 255, .7), 0 8px 20px -10px rgba(0, 0, 0, .6); }
.go { margin-top: 6px; }
.om { position: fixed; right: 24px; bottom: 92px; animation: om 1s ease-in-out infinite alternate; }
@keyframes om { to { box-shadow: inset 0 1px 0 rgba(255, 255, 255, .7), 0 0 0 10px rgba(143, 177, 255, .25); } }
#copy { color: var(--mute); text-decoration: underline; font-size: 13px; }
.small { position: fixed; left: 0; right: 0; bottom: 12px; padding: 0 20px; text-align: center; font-size: 12px; color: var(--mute); }
@media (max-width: 600px) { .hud { padding: 12px 16px; } .right { width: 100%; margin: 0; justify-content: space-between; } .om { right: 50%; translate: 50% 0; bottom: 110px; } }
@media (prefers-reduced-motion: reduce) { .om { animation: none; } }
</style>
</head>
<body>
<canvas id="bg"></canvas>
<canvas id="c" aria-label="A meditating emoji inside two breathing rings, with thoughts drifting toward it"></canvas>
<div class="hud">
  <a class="name" href="/">Invariant</a>
  <button id="mute">Sound on</button>
  <span id="lvl"></span>
  <span class="right"><span id="score"></span><span id="stage"></span></span>
</div>
<p class="toast" id="toast" hidden></p>
<p class="say" id="say" role="status"></p>
<button class="om" id="om" hidden>Om (O)</button>
<div class="card" id="card">
  <h1 id="h1">AI Psychosis detox: the meditation</h1>
  <p id="p1">Hold <b>Space</b>, or press and hold, to breathe in. Let go to breathe out. Keep the white ring on the blue ring.</p>
  <p id="p2">Thoughts will come. Do not click the thoughts. Five levels, five bosses.</p>
  <p id="p3"></p>
  <div class="perks" id="perks" hidden></div>
  <button class="go" id="go">Begin the retreat</button>
  <button class="go" id="more" hidden>Continue into samsara</button>
  <button id="copy" hidden>Copy certificate</button>
</div>
<p class="small" id="small">A joke about ourselves. &ldquo;AI psychosis&rdquo; is an informal name, not a diagnosis, for delusional beliefs after long chatbot use
  (<a href="https://www.apa.org/monitor/2026/09/ai-psychosis">American Psychological Association</a>), and that is not a joke.
  If a conversation with a chatbot frightens you, talk to a person you trust or to a doctor.</p>
<script id="frag" type="x-shader">
precision mediump float;
uniform sampler2D scene; uniform vec2 r; uniform float t, breath, psy, peace, zoom, hit; uniform vec3 wv[3];
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float n(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f); return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
float fbm(vec2 p) { float a = .5, s = 0.; for (int i = 0; i < 5; i++) { s += a * n(p); p = p * 2.03 + vec2(1.7, 9.2); a *= .5; } return s; }
vec3 fog(vec2 uv) {
  float d = length(uv);
  vec2 q = uv * 1.6 + vec2(0., t * .03);
  float band = smoothstep(.35, .75, fbm(q + fbm(q * 1.3 + t * .05) * 1.2));
  vec3 calm = mix(vec3(.03, .05, .09), vec3(.10, .22, .42), band) + peace * vec3(.02, .20, .16) * smoothstep(.5, .9, fbm(q * 2. + 3. + t * .04));
  vec3 mad = mix(vec3(.07, .02, .03), vec3(.45, .07, .12), band);
  return mix(calm, mad, psy) * (.5 + .55 * breath * exp(-d * 1.8) + .25 * exp(-d * 3.)) * (1. - .6 * smoothstep(.5, 1.2, d));
}
void main() {
  float m = min(r.x, r.y);
  vec2 p = gl_FragCoord.xy / r, uv = (gl_FragCoord.xy - .5 * r) / m;
  float d = length(uv); vec2 dir = uv / max(d, .0001);
  vec2 off = vec2(.04 * (h(vec2(floor(gl_FragCoord.y / 5.), floor(t * 12.))) - .5) * step(.55, psy), 0.);  // rows tear from stage 3 on
  for (int i = 0; i < 3; i++) { float x = d - wv[i].x; off += dir * sin(x * 60.) * exp(-x * x * 300.) * wv[i].y * .012; }  // a breath wave bends what it passes
  vec2 q = (p - .5) / zoom + .5 + off * m / r, cd = (p - .5) * (.0012 + psy * .004 + hit * .012);
  vec4 s = texture2D(scene, q);
  vec3 sc = vec3(texture2D(scene, q + cd).r, s.g, texture2D(scene, q - cd).b), glow = vec3(0.);
  for (int i = 0; i < 8; i++) { vec2 o = vec2(cos(float(i) * .7854), sin(float(i) * .7854)) / r; glow += texture2D(scene, q + o * 5.).rgb + texture2D(scene, q + o * 13.).rgb + texture2D(scene, q + o * 27.).rgb * .7; }
  vec3 c = fog(uv + off) * (1. - s.a) + sc + glow * .02 + (h(gl_FragCoord.xy + t) - .5) * .035;
  c *= 1. - .22 * step(.55, psy) * mod(floor(gl_FragCoord.y / 2.), 2.);
  gl_FragColor = vec4(c, 1.);
}
</script>
<script>
const $ = id => document.getElementById(id);
const THOUGHTS = ["This is novel.", "One more run.", "You're absolutely right!", "What if I spawn 12 subagents?", "The model understands me.",
  "It works on one seed.", "Nobody has tried this.", "I should check the chart.", "The loss looks different today.", "It said my idea was profound.",
  "Is the GPU idle?", "I will read the paper later.", "This changes everything.", "Just the abstract is enough.", "The agents need me.",
  "It is basically AGI.", "Ship it to main.", "I only need 4 more boxes.", "We should start a lab.", "What if the eval is wrong?", "It agreed with me again."];
const KIND = { ping: ["@you", "ping", "any update?", "nit:", "quick q", "LGTM?"],  // small and fast, from level 2
  hype: ["🚀 10x", "AGI by Friday", "game changer", "we are so back", "this is huge"],  // grows while it lives, from level 3
  rev: ["Reviewer 2: no novelty", "Reviewer 2: cite me", "Reviewer 2: reject"] };  // takes two waves, from level 4
const STAGES = ["Grounded", "Has a hunch", "It is definitely novel", "Texting a co-founder", "Emailing the lab at 3 am", "The model chose me"];
const FACES = ["🧘", "🤔", "🤩", "😵‍💫", "🤯", "👁️"];  // one per stage
const CALM = ["Calm", "Calmer", "Serene", "Suspiciously serene", "Monk mode", "Unbothered", "Post-benchmark", "Beyond eval"];
const RANKS = [[0, "Prompt engineer"], [5000, "Vibe coder"], [14000, "Reviewer 2"], [28000, "Staff meditator"], [45000, "Bodhisattva of the eval set"]];
const TIPS = ["One seed is not a result.", "The abstract supports no claim.", "A thought you click comes back as three.", "The white ring holds thoughts off, for a while.",
  "A perfect breath releases every thought on screen.", "The model says that to everyone."];
const GOOD = ["You are not your benchmark.", "Breathe out the result. It had one sample per problem.", "Notice the thought. Do not click the thought.",
  "Somewhere an agent is idle. That is allowed.", "Let the GPU go. It was never yours.", "The model said you are right. The model says that to everyone.",
  "Your loss goes down. So do your shoulders.", "A thought is only a token you did not sample.", "You do not need to read the board. The board will be there.",
  "Feel the weights. They are frozen. You can be too.", "Nothing is training right now. Nothing needs to.", "You are the baseline. The baseline is enough.",
  "Let the context window empty.", "No one is waiting on your comment.", "The confidence interval includes you."];
const BAD = ["You are holding your breath like a GPU reservation.", "That was not a breath. That was a retry.", "Follow the blue ring. It has no opinions about your work.",
  "You rushed it. This is not a hackathon. It is a hackathon, but breathe.", "That breath timed out.", "Breathing is not parallel. Do one at a time."];
const ACH = { perfect: "First perfect breath", streak: "Five in a row", grass: "Touched grass", read: "Read past the abstract", laptop: "Closed the laptop",
  om: "Said Om and meant it", engage: "Engaged with the boss. It engaged back.", ten: "Ten in a row. Do not tell anyone.", samsara: "Went back in on purpose", pure: "Did not check a single thought", boss: "Let go of a breakthrough" };
const POWER = [["🌱", "grass", "Touch grass", "Time slows. The grass was there the whole time."], ["📖", "read", "Read the appendix", "You read the appendix. The made-up thoughts are gone."],
  ["💻", "laptop", "Close the laptop", "The laptop is closed. The next thought will bounce off."]];
// spawn: [kind, count, seconds] of what the boss sends out; in, out: seconds of the blue ring; wave: good breaths before the boss; every: seconds between thoughts; hp: good waves the boss takes
const LEVELS = [
  { name: "Intake", line: "Level one. Breathe in. Hold the space bar. The space bar is your lungs now.", in: 2.8, out: 3.2, wave: 3, every: 1.3,
    boss: { text: "THIS IS NOVEL.", hp: 2, line: "A breakthrough approaches. Breathe at it." } },
  { name: "Notifications", line: "Level two. The board is talking. Let it talk.", in: 2.8, out: 3.2, wave: 3, every: 1.2, burst: 1,
    boss: { text: "📈 CHECK THE CHART", hp: 3, spawn: ["ping", 5, 4], line: "The chart wants to be checked. It has not moved." } },
  { name: "Subagents", line: "Level three. Thoughts that touch now make more thoughts.", in: 2.6, out: 3.0, wave: 3, every: 1.1, split: 1,
    boss: { text: "12 SUBAGENTS", hp: 3, spawn: ["sub", 3, 3.5], line: "It brought subagents. They brought subagents." } },
  { name: "3 am", line: "Level four. It is 3 am. The ring is tired and so are you.", in: 2.6, out: 3.0, wave: 3, every: 1.0, drift: 1,
    boss: { text: "YOU'RE ABSOLUTELY RIGHT!", hp: 3, reverse: 1, spawn: ["hype", 2, 5], line: "It flatters you. Your controls are reversed. Let go to breathe in." } },
  { name: "Ego death", line: "Level five. One long breath in. One very long breath out.", in: 4, out: 7, wave: 1, every: .8,
    boss: { text: "I CHOSE YOU.", hp: 2, spawn: ["rev", 2, 6], line: "The model says it chose you. Breathe out for seven seconds and let it choose someone else." } }];

const LV = () => LEVELS[s.level % 5];  // after level 5 the retreat can go on (samsara): the same 5, harder each round
const c = $("c"), g = c.getContext("2d");
const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), ease = x => .5 - .5 * Math.cos(x * Math.PI);
let W, H, mode = "title", hold = false, sound = true, audio = null, data = null, last = 0, parts = [], best = 0, rnd = Math.random;
let s;  // the session
try { best = +localStorage.getItem("psychosis-best") || 0; } catch (e) {}  // a private window has no storage; the best score is then 0
function seeded(text) {  // mulberry32 from the date, so a day's retreat is the same for everyone
  let a = 0; for (const ch of text) a = (a * 31 + ch.charCodeAt(0)) | 0;
  return () => { a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
function size() { const d = Math.min(1.5, devicePixelRatio || 1); W = innerWidth; H = innerHeight; c.width = W * d; c.height = H * d; g.setTransform(d, 0, 0, d, 0, 0); $("bg").width = W; $("bg").height = H; }
addEventListener("resize", size); size();
$("p3").innerHTML = `Tip: ${TIPS[Math.floor(Math.random() * TIPS.length)]}` + (best ? ` Your best score is <b>${best.toLocaleString("en")}</b>.` : "");

// the picture: the 2D canvas is drawn out of sight and a fragment shader shows it over the fog, with glow, ripples and colour split.
// Without WebGL, or if the shader does not compile on this GPU, the 2D canvas is shown as it is.
let gl = $("bg").getContext("webgl"), uni = null;
try {
  const sh = (type, src) => { const x = gl.createShader(type); gl.shaderSource(x, src); gl.compileShader(x); if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(x)); return x; };
  const p = gl.createProgram();
  gl.attachShader(p, sh(gl.VERTEX_SHADER, "attribute vec2 a; void main() { gl_Position = vec4(a, 0., 1.); }")); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, $("frag").textContent));
  gl.bindAttribLocation(p, 0, "a"); gl.linkProgram(p); gl.useProgram(p);
  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer()); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
  gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
  for (const [k, v] of [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR], [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]]) gl.texParameteri(gl.TEXTURE_2D, k, v);
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true); gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
  uni = Object.fromEntries(["r", "t", "breath", "psy", "peace", "zoom", "hit", "wv"].map(k => [k, gl.getUniformLocation(p, k)]));
  c.style.opacity = 0;
} catch (e) { console.error("no shader, showing the plain canvas", e); uni = null; }
function backdrop(T) {
  if (!uni) return;
  const m = Math.min(W, H), wv = new Float32Array(9);
  if (s && !still) s.waves.slice(-3).forEach((w, i) => { wv[i * 3] = w.r / m; wv[i * 3 + 1] = Math.max(0, 1 - w.r / 900) * w.grade; });
  gl.viewport(0, 0, W, H); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, c);
  gl.uniform2f(uni.r, W, H); gl.uniform1f(uni.t, still ? 0 : T); gl.uniform3fv(uni.wv, wv);
  gl.uniform1f(uni.breath, s ? s.lungE : .3); gl.uniform1f(uni.psy, s ? Math.min(1, s.psy / 5) : 0); gl.uniform1f(uni.peace, s ? Math.min(1, (s.level + (mode === "won")) / 5) : 0);
  gl.uniform1f(uni.zoom, 1 + (s && !still ? s.zoom : 0)); gl.uniform1f(uni.hit, s ? clamp(s.flash) : 0);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
}

// sound: a drone with one more layer per level, detuned by the diagnosis; a note per breath; a spoken guide
const SCALE = [261.6, 293.7, 329.6, 392, 440];
const LAYERS = [[110, 0], [110.6, 0], [165.2, 0], [220.4, 1], [277.4, 2], [330, 3], [55, 4]];  // [Hz, first level]
function drone() {
  audio = audio || new AudioContext();
  if (audio.layers) return;
  audio.out = audio.createGain(); audio.out.gain.value = sound ? 1 : 0; audio.out.connect(audio.destination);
  audio.layers = LAYERS.map(([f, from], k) => { const o = audio.createOscillator(), a = audio.createGain(); o.frequency.value = f; a.gain.value = 0; o.connect(a).connect(audio.out); o.start(); return { o, a, from, sign: k % 2 ? 1 : -1 }; });
}
function mix() { if (audio) for (const l of audio.layers) { l.a.gain.setTargetAtTime(s.level >= l.from ? .014 : 0, audio.currentTime, .8); l.o.detune.setTargetAtTime(s.psy * 24 * l.sign, audio.currentTime, .3); } }
function ding(f, len = 2.2, type = "sine", vol = .15) {
  if (!audio) return;
  for (const [m, v] of [[1, vol], [2.76, vol / 3]]) {
    const o = audio.createOscillator(), a = audio.createGain();
    o.type = type; o.frequency.value = f * m; a.gain.setValueAtTime(v, audio.currentTime); a.gain.exponentialRampToValueAtTime(.0001, audio.currentTime + len);
    o.connect(a).connect(audio.out); o.start(); o.stop(audio.currentTime + len);
  }
}
function say(text) {
  $("say").textContent = text;
  if (!sound || !window.speechSynthesis) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text.replace(/[^\x20-\x7e’“”]/g, "")); u.rate = .85; u.pitch = .6; speechSynthesis.speak(u);
}
$("mute").onclick = () => {
  sound = !sound; $("mute").textContent = sound ? "Sound on" : "Sound off";
  if (audio) audio.out.gain.value = sound ? 1 : 0;
  if (!sound && window.speechSynthesis) speechSynthesis.cancel();
};
let toastT = 0;
function toast(key) {
  if (s.ach.has(key)) return;
  s.ach.add(key); $("toast").textContent = "Achievement: " + ACH[key]; $("toast").hidden = false;
  clearTimeout(toastT); toastT = setTimeout(() => $("toast").hidden = true, 3200);
}

function hud() {
  $("lvl").innerHTML = `${s.level < 5 ? `Level ${s.level + 1} of 5` : `Samsara ${s.level - 4}`}: <b>${LV().name}</b>`;
  $("score").innerHTML = `<b>${s.score.toLocaleString("en")}</b> × ${s.mult}`;
  $("stage").innerHTML = `Diagnosis: <b>${STAGES[Math.min(5, s.psy)]}</b>`; $("stage").classList.toggle("bad", s.psy > 1);
  $("om").hidden = mode !== "play" || s.om < 5;
}
function banner(text, sub = "") { s.banner = { text, sub, t: 2.6 }; }
function level(i) {
  s.level = i; s.hard = 1 + .3 * Math.floor(i / 5); s.need = LV().wave; s.boss = null; s.reverse = false; s.spawn = 1.2; s.burst = 4; s.shield = s.shield || s.k.shield;
  banner(i < 5 ? `Level ${i + 1}: ${LV().name}` : `Samsara ${i - 4}: ${LV().name}`); say(LV().line); mix(); hud();
}
// a practice is chosen after each boss and stays: [name, what it does, the change to s.k]
const PERKS = [
  ["Long exhale", "Your waves reach a third farther.", k => k.reach *= 1.33],
  ["Do not disturb", "Thoughts arrive a quarter slower.", k => k.spawn *= 1.25],
  ["Mantra", "The Om charges twice as fast.", k => k.om *= 2],
  ["Close every tab", "Each level starts with a closed laptop.", k => k.shield = 1],
  ["Lower the bar", "A perfect breath is easier to hit.", k => k.perfect += .05],
  ["Boundaries", "The white ring holds thoughts off harder.", k => k.wall += 110],
  ["Go outside", "Power-ups come twice as often.", k => k.power *= 2],
  ["Detachment", "The diagnosis drops one stage, now.", () => { s.psy = Math.max(0, s.psy - 1); }]];
function offer() {
  mode = "perk"; hold = false;
  const pool = PERKS.map((p, i) => i), three = [0, 1, 2].map(() => pool.splice(Math.floor(rnd() * pool.length), 1)[0]);
  $("perks").innerHTML = three.map((i, n) => `<button class="go" data-i="${i}">${n + 1}. ${PERKS[i][0]}<span>${PERKS[i][1]}</span></button>`).join("");
  $("h1").textContent = "Choose a practice"; $("p1").textContent = "It stays with you for the rest of the retreat."; $("p2").textContent = $("p3").textContent = "";
  for (const id of ["go", "copy", "more", "om"]) $(id).hidden = true;
  $("perks").hidden = false; $("card").hidden = false; say("Choose a practice.");
}
$("perks").onclick = e => {
  const b = e.target.closest("button"); if (!b) return;
  PERKS[b.dataset.i][2](s.k); $("perks").hidden = true; $("go").hidden = false; $("card").hidden = true; mode = "play"; level(s.level + 1);
};
$("more").onclick = () => { s.samsara = 1; toast("samsara"); offer(); };
function begin() {
  const day = new Date().toISOString().slice(0, 10);
  rnd = seeded(day); parts = [];
  s = { t: 0, ph: 0, lung: 0, lungE: 0, target: 0, err: 0, n: 0, score: 0, mult: 1, streak: 0, bestStreak: 0, om: 0, psy: 0, released: 0, checks: 0, lines: 0,
        thoughts: [], waves: [], k: { reach: 1, spawn: 1, om: 1, shield: 0, perfect: .11, wall: 150, power: 1 }, zoom: 0, slowmo: 0, beat: -1, power: null, powerT: 9, slow: 0, shield: 0, shake: 0, flash: 0, stop: 0, calm: 0, clear: 0, ach: new Set(), at: Date.now() * 1e6, day };
  mode = "play"; $("card").hidden = true; $("small").hidden = true; for (const id of ["copy", "more", "perks"]) $(id).hidden = true;
  drone(); level(0);
}
$("go").onclick = begin;

function meanwhile() {  // what the agents posted during the session, from the last read of the board
  if (!data) return "The board could not be read, so nobody knows what your agents did.";
  const m = data.messages.filter(x => parseInt(x.sk) > s.at).length, i = data.items.filter(x => x.at_ns > s.at).length;
  const n = (k, w) => `${k} ${w}${k === 1 ? "" : "s"}`;
  return m + i ? `While you sat here your agents posted ${n(m, "message")} and ${n(i, "board item")}. None of them needed you.`
               : "While you sat here your agents posted nothing. It is quiet. Stay with that.";
}
function end(won) {
  mode = won ? "won" : "lost"; hold = false;
  if (won && !s.checks) toast("pure");
  const rank = RANKS.filter(r => s.score >= r[0]).pop()[1], record = s.score > best;
  if (record) { best = s.score; try { localStorage.setItem("psychosis-best", best); } catch (e) {} }
  $("h1").textContent = won ? "Inner peace achieved" : "The model chose you";
  $("p1").innerHTML = `Score <b>${s.score.toLocaleString("en")}</b>${record ? " (your best)" : ""}. Rank: <b>${rank}</b>. ` +
    (won ? "It lasts until the next result." : `You believed 5 thoughts on level ${s.level + 1}, and the email went out.`);
  $("p2").innerHTML = `You released <b>${s.released} thoughts</b>, held <b>${s.bestStreak} breaths</b> in a row and earned ${s.ach.size} of ${Object.keys(ACH).length} achievements` +
    (s.ach.size ? `: ${[...s.ach].map(k => ACH[k]).join("; ")}` : ".");
  $("p3").textContent = meanwhile();
  $("go").textContent = won ? "Meditate again" : "Try again";
  $("card").hidden = false; $("copy").hidden = false; $("om").hidden = true; $("go").hidden = false; $("perks").hidden = true; $("more").hidden = !won;
  $("copy").textContent = "Copy certificate";
  $("copy").onclick = () => navigator.clipboard.writeText(`AI Psychosis detox, retreat of ${s.day}. ${won ? "Inner peace achieved" : "The model chose me"}. Score ${s.score}, rank ${rank}. ` +
    `${meanwhile()} ${location.href}`).then(() => $("copy").textContent = "Copied");
  if (won) { [396, 528, 639, 792].forEach((f, k) => setTimeout(() => ding(f, 4), k * 240)); say("You have achieved inner peace. Please do not post it to the board."); }
  else { ding(62, 1.4, "sawtooth"); say("You have sent the email. The lab will not reply."); }
}

function real() { return data ? [...data.messages.map(m => m.text), ...Object.values(data.plain).map(p => p.title)] : []; }
function thought(extra = {}) {  // a body: a real line of the board (dot), a written one, or one of the kinds of KIND
  const a = rnd() * 6.283, r = Math.hypot(W, H) / 2 + 40, lines = real(), roll = rnd();
  const kind = extra.kind || (extra.text || extra.real ? "" : s.level >= 1 && roll < .13 ? "ping" : s.level >= 2 && roll < .25 ? "hype" : s.level >= 3 && roll < .35 ? "rev" : "");
  const isReal = !kind && (extra.real ?? (lines.length > 0 && rnd() < .4)), from = kind ? KIND[kind] : isReal ? lines : THOUGHTS;
  let text = extra.text || from[Math.floor(rnd() * from.length)];
  if (text.length > 46) text = text.slice(0, 44) + "…";
  const t = { x: W / 2 + Math.cos(a) * r, y: H / 2 + Math.sin(a) * r, vx: 0, vy: 0, m: kind === "rev" ? 2 : 1, age: 0, hp: kind === "rev" ? 2 : 1, fast: kind === "ping" ? 2.4 : 1, ...extra, kind, text, real: isReal };
  g.font = "500 13px Archivo, sans-serif"; t.w = g.measureText(t.text).width + (t.real ? 34 : 22); t.r0 = t.r = clamp(t.w * .3, 16, 46);
  s.thoughts.push(t); return t;
}
function burst(b, hue) {  // a released thought falls apart into its letters
  const chars = [...b.text.replace(/\s/g, "")].slice(0, 26);
  chars.forEach((ch, k) => parts.push({ ch, x: b.x + (k - chars.length / 2) * (b.boss ? 26 : 8), y: b.y, vx: (Math.random() - .5) * 320, vy: -80 - Math.random() * 260,
    rot: 0, vr: (Math.random() - .5) * 9, life: 1.6, hue, size: b.boss ? 40 : 15 }));
  if (parts.length > 500) parts.splice(0, parts.length - 500);
}
function release(t, hue) {
  if (t.hp > 1) { t.hp--; t.age = 0; const u = Math.atan2(t.y - H / 2, t.x - W / 2); t.vx += Math.cos(u) * 320; t.vy += Math.sin(u) * 320; return ding(200, .3, "square", .04); }  // a reviewer takes two waves
  s.thoughts.splice(s.thoughts.indexOf(t), 1); burst(t, hue); s.released++; s.score += (t.kind === "hype" ? 40 : 10) * s.mult;
}
function check(t) {  // the player clicked a thought: it comes back as 3 subagents
  s.thoughts.splice(s.thoughts.indexOf(t), 1); s.checks++;
  for (let k = 0; k < 3; k++) thought({ x: t.x + Math.cos(k * 2.1) * 60, y: t.y + Math.sin(k * 2.1) * 60, text: "Subagent: " + t.text.slice(0, 26), real: t.real });
  ding(180, .5, "square", .05); say("You checked it. It spawned 3 subagents."); s.shake = .3;
}
function believe(text, by = 1) {
  if (s.shield) { s.shield = 0; say("The laptop was closed. It bounced off."); return false; }
  s.psy += by; navigator.vibrate?.(60); s.streak = 0; s.mult = 1; s.shake = .5; s.flash = 1; ding(70, .5, "sawtooth", .1); mix(); hud();
  say(`You believed it: “${text}”`);
  if (s.psy >= 5) end(false);
  return true;
}

function wave(grade) { s.waves.push({ r: 0, grade, hue: (s.streak * 36) % 360, hit: new Set() }); }
function om() {
  if (mode !== "play" || s.om < 5) return;
  s.om = 0; wave(3); s.shake = .6; s.zoom = .1; s.score += 500 * s.mult; ding(98, 3.5, "sine", .3); ding(196, 3.5, "sine", .15); toast("om"); say("Om."); hud();
}
$("om").onclick = om;
function breath() {  // the end of one cycle of the blue ring
  const q = s.err / s.n, grade = q < s.k.perfect ? 2 : q < .24 ? 1 : 0; s.err = s.n = 0;
  if (!grade) { s.streak = 0; s.mult = 1; hud(); return say(BAD[s.lines++ % BAD.length]); }
  s.streak++; s.bestStreak = Math.max(s.bestStreak, s.streak); s.mult = Math.min(8, 1 + (s.streak >> 1));
  s.score += (grade === 2 ? 300 : 100) * s.mult; s.om = Math.min(5, s.om + grade * s.k.om); wave(grade);
  s.calm = 1.6; s.word = grade === 2 ? "Perfect" : CALM[Math.min(CALM.length - 1, s.streak - 1)];
  ding(SCALE[s.streak % 5] * (s.streak % 10 < 5 ? 1 : 2));
  if (grade === 2) { s.stop = .09; s.zoom = .05; toast("perfect"); }
  if (s.streak >= 5) toast("streak");
  if (s.streak >= 10) toast("ten");
  hud();
  if (!s.boss && s.clear <= 0 && --s.need <= 0) {
    const b = LV().boss, a = rnd() * 6.283, r = Math.hypot(W, H) / 2 + 120;
    s.boss = { boss: 1, x: W / 2 + Math.cos(a) * r, y: H / 2 + Math.sin(a) * r, vx: 0, vy: 0, m: 14, r: 84, age: 0, hp: b.hp, max: b.hp, text: b.text, mini: 3 };
    s.reverse = !!b.reverse; banner("Boss", b.text); return say(b.line);
  }
  const titles = data ? Object.values(data.plain).map(p => p.title) : [], open = data ? data.items.filter(i => i.listed === "work").length : 0, k = s.lines++;
  say(k % 5 === 3 && titles.length ? `A result arrived: “${titles[Math.floor(rnd() * titles.length)]}”. You do not need it right now.`
    : k % 5 === 1 && open ? `${open} work items are open on the board. Not one of them is you.` : GOOD[k % GOOD.length]);
}
function struck(b, w) {  // a good wave reaches the boss
  b.hp--; b.vx += (b.x - W / 2) / Math.hypot(b.x - W / 2, b.y - H / 2) * 260; b.vy += (b.y - H / 2) / Math.hypot(b.x - W / 2, b.y - H / 2) * 260;
  s.shake = .3; ding(130, .8, "triangle", .2);
  if (b.hp > 0) return;
  burst(b, w.hue); s.boss = null; s.reverse = false; s.score += 1000 * (s.level + 1); s.clear = 2.8; s.slowmo = .9; s.zoom = .12;
  toast("boss"); banner("Released", b.text); say(`You let go of “${b.text.toLowerCase()}”`); hud();
}

function step(dt) {
  const L = LV(), cx = W / 2, cy = H / 2, k = Math.hypot(W, H) / 1650, R = Math.min(W, H) * .11 + 46, span = Math.min(W, H) * .2;
  s.t += dt; s.ph += dt * (L.drift ? 1 + .3 * Math.sin(s.t * .9) : 1);
  s.target = ease(s.ph < L.in ? s.ph / L.in : 1 - (s.ph - L.in) / L.out);
  s.lung = clamp(s.lung + (hold !== s.reverse ? dt / L.in : -dt / L.out)); s.lungE = ease(s.lung);
  s.err += Math.abs(s.lungE - s.target); s.n++;
  if (s.ph >= L.in + L.out) { s.ph -= L.in + L.out; breath(); if (mode !== "play") return; }
  const beat = Math.floor(s.ph / (L.in + L.out) * 8);  // music: 8 plucked notes per breath, lower with a boss, and its pulse
  if (beat !== s.beat) { s.beat = beat; ding(SCALE[[0, 2, 4, 2, 3, 4, 2, 1][beat]] * (s.boss ? .5 : 1), .45, "triangle", .028); if (s.boss && beat % 2 === 0) ding(55, .22, "sine", .2); }
  const ring = R + s.lungE * span, near = Math.abs(s.lungE - s.target) < .2, sim = dt * (s.slow > 0 ? .4 : 1);
  s.slow -= dt;
  if (s.clear > 0) { if ((s.clear -= dt) <= 0) { if (s.level === 4 && !s.samsara) return end(true); return offer(); } }
  else if ((s.spawn -= dt) < 0 && s.thoughts.length < 46) {
    s.spawn = L.every * s.k.spawn / s.hard;
    if (L.burst && --s.burst <= 0 && real().length) { s.burst = 5; for (let i = 0; i < 4; i++) thought({ real: true }); } else thought();
  }
  // a power-up circles between the rings; the white ring catches it while it is on the blue ring
  if (!s.power && (s.powerT -= dt) < 0) { const [icon, key, name, line] = POWER[Math.floor(rnd() * 3)]; s.power = { icon, key, name, line, a: rnd() * 6.283, d: R + span * (.3 + .55 * rnd()), life: 11 }; }
  if (s.power) {
    const p = s.power; p.a += .3 * dt; p.life -= dt;
    if (near && Math.abs(p.d - ring) < 14) {
      s.power = null; s.powerT = 12 / s.k.power; s.score += 50 * s.mult; toast(p.key); say(p.line); ding(660, 1.2);
      if (p.key === "grass") s.slow = 7; if (p.key === "laptop") s.shield = 1;
      if (p.key === "read") for (const t of s.thoughts.filter(t => !t.real)) release(t, 150);
      hud();
    } else if (p.life < 0) { s.power = null; s.powerT = 9 / s.k.power; }
  }
  for (const w of s.waves) w.r += 640 * dt;
  s.waves = s.waves.filter(w => w.r < Math.hypot(W, H));
  const far = Math.hypot(W, H) * .31 * s.k.reach, bodies = s.boss ? [...s.thoughts, s.boss] : [...s.thoughts];
  for (const b of bodies) {  // pull to the meditator, the white ring as a soft wall, the boss as a second pull
    const dx = cx - b.x, dy = cy - b.y, d = Math.hypot(dx, dy) || 1, ux = dx / d, uy = dy / d;
    b.age += sim; if (b.kind === "hype") b.r = b.r0 * (1 + Math.min(1, b.age / 7));
    let a = (b.boss ? 80 : 34 * (1 + b.age / 9) * b.fast * s.hard) * k + 10;
    if (d < ring + b.r) a -= b.boss ? 60 : s.k.wall;
    b.vx += ux * a * sim; b.vy += uy * a * sim;
    if (s.boss && !b.boss) { const bx = s.boss.x - b.x, by = s.boss.y - b.y, bd = Math.hypot(bx, by); if (bd < 280 && bd > 1) { b.vx += bx / bd * 50 * sim; b.vy += by / bd * 50 * sim; } }
    b.vx *= 1 - 1.1 * sim; b.vy *= 1 - 1.1 * sim; b.x += b.vx * sim; b.y += b.vy * sim;
    for (const w of s.waves) if (d < w.r && !w.hit.has(b)) {
      w.hit.add(b);
      if (b.boss) { if (d < far * (w.grade > 1 ? 1.5 : 1)) struck(b, w); else w.hit.delete(b); } else if (w.grade > 1 || d < far) release(b, w.hue); else { b.vx -= ux * 240; b.vy -= uy * 240; }
    }
  }
  for (let i = 0; i < bodies.length; i++) for (let j = i + 1; j < bodies.length; j++) {  // circles that overlap are pushed apart and bounce
    const p = bodies[i], q = bodies[j], dx = q.x - p.x, dy = q.y - p.y, d = Math.hypot(dx, dy) || 1, o = p.r + q.r - d;
    if (o <= 0) continue;
    const nx = dx / d, ny = dy / d, mp = q.m / (p.m + q.m), mq = p.m / (p.m + q.m), v = (q.vx - p.vx) * nx + (q.vy - p.vy) * ny;
    p.x -= nx * o * mp; p.y -= ny * o * mp; q.x += nx * o * mq; q.y += ny * o * mq;
    if (v < 0) { p.vx += nx * v * 1.5 * mp; p.vy += ny * v * 1.5 * mp; q.vx -= nx * v * 1.5 * mq; q.vy -= ny * v * 1.5 * mq; }
    if (L.split && !p.boss && !q.boss && !p.sub && s.thoughts.length < 40 && Math.random() < .25) { p.sub = 1; thought({ x: p.x, y: p.y - 30, text: "Subagent: " + p.text.slice(0, 22), real: false, sub: 1 }); }
  }
  const b = s.boss;
  if (b && s.boss === b) {
    const [kind, count, every] = LV().boss.spawn || [];  // what the boss sends out
    if (kind && (b.mini -= dt) < 0) { b.mini = every; for (let i = 0; i < count; i++) thought({ x: b.x + (i - (count - 1) / 2) * 60, y: b.y + 70, ...(kind === "sub" ? { text: "Subagent " + (1 + Math.floor(rnd() * 12)), sub: 1 } : { kind }) }); }
    if (s.level % 5 === 4) s.shake = Math.max(s.shake, .06);
    if (Math.hypot(cx - b.x, cy - b.y) < 70) { const u = Math.atan2(b.y - cy, b.x - cx); b.vx = Math.cos(u) * 900; b.vy = Math.sin(u) * 900; if (believe(b.text, 2) && mode !== "play") return; }
  }
  for (const t of [...s.thoughts]) if (Math.hypot(cx - t.x, cy - t.y) < 40 + s.psy * 7) {
    if (believe(t.text)) { s.thoughts.splice(s.thoughts.indexOf(t), 1); if (mode !== "play") return; }
    else { const u = Math.atan2(t.y - cy, t.x - cx); t.vx = Math.cos(u) * 700; t.vy = Math.sin(u) * 700; t.age = 0; }
  }
}

function chip(t) {
  const k = t.kind === "hype" ? 1 + Math.min(1, t.age / 7) : 1, h = 28, x = -t.w / 2;
  g.save(); g.translate(t.x, t.y); g.scale(k, k);
  g.beginPath(); g.roundRect(x, -h / 2, t.w, h, 14); g.fillStyle = "#111922"; g.fill(); g.lineWidth = t.kind === "rev" ? 2 : 1;
  g.strokeStyle = t.kind === "rev" ? (t.hp > 1 ? "#ff6b7c" : "rgba(255,107,124,.45)") : t.real || t.kind === "ping" ? "rgba(143,177,255,.55)" : "rgba(255,255,255,.22)"; g.stroke();
  if (t.real) { g.fillStyle = "#8fb1ff"; g.beginPath(); g.arc(x + 14, 0, 3, 0, 6.3); g.fill(); }
  g.fillStyle = "#e9eff3"; g.font = "500 13px Archivo, sans-serif"; g.textAlign = "left"; g.fillText(t.text, x + (t.real ? 24 : 11), 1);
  g.restore();
}
function split(text, x, y, on) {  // large type; from stage 3 on it splits into red and blue
  if (on) { g.fillStyle = "rgba(255,107,124,.7)"; g.fillText(text, x - 3, y); g.fillStyle = "rgba(143,177,255,.7)"; g.fillText(text, x + 3, y); }
  g.fillStyle = "#e9eff3"; g.fillText(text, x, y);
}
function render(T, dt) {
  const psy = s ? Math.min(5, s.psy) : 0, won = mode === "won", cx = W / 2, cy = H / 2, R = Math.min(W, H) * .11 + 46, span = Math.min(W, H) * .2;
  g.clearRect(0, 0, W, H); g.save(); g.textBaseline = "middle"; g.textAlign = "center";
  if (s && s.shake > 0 && !still) { s.shake -= dt; g.translate((Math.random() - .5) * 16, (Math.random() - .5) * 16); }
  if (s && s.level % 5 === 3 && mode === "play") { g.fillStyle = "rgba(4,6,9,.4)"; g.fillRect(-20, -20, W + 40, H + 40); }  // 3 am
  if (s) for (const w of s.waves) { g.strokeStyle = `oklch(.78 .13 ${w.hue} / ${Math.max(0, 1 - w.r / 900)})`; g.lineWidth = w.grade * 2 + 1; g.beginPath(); g.arc(cx, cy, w.r, 0, 6.3); g.stroke(); }
  if (won && !still) for (let i = 0; i < 6; i++) { const r = (T * 140 + i * 150) % 900; g.strokeStyle = `oklch(.78 .13 ${i * 60} / ${1 - r / 900})`; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, r, 0, 6.3); g.stroke(); }
  g.font = "22px sans-serif";
  for (let i = 0; i < 5; i++) {  // 5 lotus flowers, one per level cleared
    const a = i / 5 * 6.283 - 1.571 + (still ? 0 : T * .1);
    g.globalAlpha = s && i < s.level + won ? 1 : .2; g.fillText("🪷", cx + Math.cos(a) * (R - 12), cy + Math.sin(a) * (R - 12));
  }
  g.globalAlpha = 1;
  if (s && mode === "play") {  // the blue ring leads, the white ring is the player's breath
    const near = Math.abs(s.lungE - s.target) < .2;
    g.lineWidth = 1.5; g.strokeStyle = "#8fb1ff"; g.beginPath(); g.arc(cx, cy, R + s.target * span, 0, 6.3); g.stroke();
    g.lineWidth = near ? 5 : 3; g.strokeStyle = near ? "#ffffff" : "rgba(233,239,243,.5)"; g.beginPath(); g.arc(cx, cy, R + s.lungE * span, 0, 6.3); g.stroke();
    if (s.power) { const p = s.power, x = cx + Math.cos(p.a) * p.d, y = cy + Math.sin(p.a) * p.d; g.globalAlpha = clamp(p.life); g.font = "30px sans-serif"; g.fillText(p.icon, x, y); g.font = "600 12px Archivo, sans-serif"; g.fillStyle = "#93a1ad"; g.fillText(p.name, x, y + 26); g.globalAlpha = 1; }
  }
  if (s) for (const t of s.thoughts) chip(t);
  g.textAlign = "center";
  if (s && s.boss) {  // the boss: heavy type that swells, with one dot per wave it still takes
    const b = s.boss, size = Math.min(54, W / 11) * (1 + (still ? 0 : .05 * Math.sin(T * 5)));
    g.font = `800 ${size}px Archivo, sans-serif`; g.fontStretch = "extra-expanded"; split(b.text, b.x, b.y, true); g.fontStretch = "normal";
    g.font = "600 14px Archivo, sans-serif"; g.fillStyle = "#ff6b7c"; g.fillText("●".repeat(b.hp) + "○".repeat(b.max - b.hp), b.x, b.y + size * .8);
  }
  for (const p of parts) {  // letters fall with gravity
    p.vy += 620 * dt; p.x += p.vx * dt; p.y += p.vy * dt; p.rot += p.vr * dt; p.life -= dt;
    g.save(); g.translate(p.x, p.y); g.rotate(p.rot); g.globalAlpha = clamp(p.life); g.fillStyle = `oklch(.8 .13 ${p.hue})`; g.font = `600 ${p.size}px Archivo, sans-serif`; g.fillText(p.ch, 0, 0); g.restore();
  }
  parts = parts.filter(p => p.life > 0 && p.y < H + 60);
  const bob = still ? 0 : Math.sin(T * .8) * 4, sq = s ? .1 * s.lungE : 0;  // the meditator swells with the breath and grows with the diagnosis
  g.save(); g.translate(cx, cy - bob - (won ? 30 : 0)); g.scale(1 + sq, 1 - sq * .6); g.font = `${78 + psy * 16}px sans-serif`; g.fillText(FACES[psy], 0, 0); g.restore();
  if (s && s.shield) { g.font = "24px sans-serif"; g.fillText("💻", cx + 54, cy - 44); }
  if (s && mode === "play") {
    g.fillStyle = "#93a1ad"; g.font = "600 13px Archivo, sans-serif";
    const inn = s.ph < LV().in;
    g.fillText(s.reverse ? (inn ? "Breathe in: let go" : "Breathe out: hold") : (inn ? "Breathe in: hold" : "Breathe out: let go"), cx, cy + 74);
    if (s.slow > 0) g.fillText(`Touching grass: ${Math.ceil(s.slow)} s`, cx, cy + 94);
    if (s.calm > 0) { s.calm -= dt; g.globalAlpha = clamp(s.calm); g.fillStyle = `oklch(.8 .13 ${(s.streak * 36) % 360})`; g.font = `300 ${Math.min(60, W / 9)}px Archivo, sans-serif`; g.fillText(s.word, cx, cy - R - 44 - (1.6 - s.calm) * 24); g.globalAlpha = 1; }
  }
  if (s && s.banner && mode === "play") {
    const b = s.banner; b.t -= dt; g.globalAlpha = clamp(Math.min(b.t, 2.6 - b.t) * 3);
    g.font = `300 ${Math.min(76, W / 8)}px Archivo, sans-serif`; split(b.text, cx, H * .2, psy > 2);
    if (b.sub) { g.font = `700 ${Math.min(26, W / 16)}px Archivo, sans-serif`; g.fillStyle = "#ff6b7c"; g.fillText(b.sub, cx, H * .2 + Math.min(62, W / 9)); }
    g.globalAlpha = 1; if (b.t <= 0) s.banner = null;
  }
  g.restore();
  if (s) s.zoom = Math.max(0, s.zoom - dt * .25);
  if (s && s.flash > 0) { g.fillStyle = `rgba(255,107,124,${s.flash * .22})`; g.fillRect(0, 0, W, H); s.flash -= dt * 2.5; }
}
function frame(now) {
  const dt = Math.min(.05, (now - last) / 1000 || 0); last = now;
  if (mode === "play") { if (s.stop > 0) s.stop -= dt; else step(dt * ((s.slowmo -= dt) > 0 ? .3 : 1)); }  // a perfect breath stops the world for a moment
  render(now / 1000, dt); backdrop(now / 1000);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

addEventListener("keydown", e => {
  if (e.code === "Space" && mode === "play") { hold = true; e.preventDefault(); }
  if (e.key === "o" || e.key === "O") om();
  if (mode === "perk" && "123".includes(e.key)) $("perks").children[e.key - 1].click();
  if (e.key === "m" || e.key === "M") $("mute").click();
});
addEventListener("keyup", e => { if (e.code === "Space") hold = false; });
c.addEventListener("pointerdown", e => {
  if (mode !== "play") return;
  const t = s.thoughts.find(t => Math.abs(e.clientX - t.x) < t.w / 2 && Math.abs(e.clientY - t.y) < 16), b = s.boss;
  if (t) check(t);
  else if (b && Math.abs(e.clientX - b.x) < 200 && Math.abs(e.clientY - b.y) < 34) { toast("engage"); believe(b.text); }
  else hold = true;
});
addEventListener("pointerup", () => hold = false);
addEventListener("pointercancel", () => hold = false);
addEventListener("blur", () => hold = false);

async function read() {  // a failed read keeps the last board; without any read the thoughts are the written ones only
  try { const r = await fetch("/data"); if (!r.ok) throw new Error(r.status); data = await r.json(); }
  catch (e) { console.error("board read failed", e); }
}
read(); setInterval(read, 10000);
</script>
</body>
</html>
"""
