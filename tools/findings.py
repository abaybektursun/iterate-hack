"""The findings page of the team site: one tile per finding, each a link to the page of that finding. The tab Proof
(/proof) is the same page for the experiments that test the team's method itself; PROOF at the end holds its differences.

view.py serves PAGE at /findings, after writing the icons into it. The page reads `findings` (slug, title, line) from
/data once, and again every 10 s while a read fails. A tile holds a small lit glass icon, the finding's TITLE and its
LINE, and nothing else; the whole tile is one link to /finding/<slug>. The looks are those of tools/architecture.py
(.claude/skills/site-ui/SKILL.md): its tokens, one light from the upper left, a slow sway, a lean toward the mouse, and
one still frame with reduced motion.

One finding, one file: a module tools/finding_<slug>.py draws its own icon. It defines ICON, the source of a
JavaScript arrow function `(kit, t, tilt) => "<svg markup>"`. view.py replaces __ICONS__ below with the object literal
`{"<slug>": <ICON source>, ...}` when it builds the page, so the functions are plain page code. The page calls an icon
about 30 times a second while its tile is on screen. `kit` is the object of that name below (the projection, a glass
slab, a lit face, a line, the theme tokens), `t` is the time in seconds, and `tilt` is the lean toward the mouse as
[x, y] from -1 to 1. The kit's view already sways and leans, so most icons use only `t`, for their own slow motion.
The icon's space is 112 by 80 units around the centre (56, 36). A module without ICON gets a plain glass slab.
"""

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
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.page { max-width: 1840px; margin: 0 auto; padding: 20px 40px 64px; }
.top { display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }
.status { margin-left: auto; color: var(--red); white-space: nowrap; }

/* The words above the tiles: one line */
.say { margin: clamp(28px, 7vh, 76px) 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; }

/* The tiles: an icon, a title and one sentence, under a hairline. No box. */
.grid { list-style: none; margin: clamp(26px, 5vh, 52px) 0 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 52px 56px; }
.tile { display: block; height: 100%; padding: 26px 0 0; border-top: 1px solid var(--rule); text-decoration: none; }
.tile:focus-visible { outline-offset: 8px; border-radius: 4px; }
.icon { display: block; width: 168px; height: 120px; overflow: visible; }
.title { margin: 20px 0 0; font-size: 20px; line-height: 1.2; font-weight: 580; font-stretch: 108%; letter-spacing: .004em; transition: color .15s ease; }
.tile:hover .title { color: var(--blue); }
.line { margin: 7px 0 0; color: var(--mute); font-size: 15px; line-height: 1.45; max-width: 38ch; }

/* The icon: glass, its light and its lines */
.icon * { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.spec { opacity: var(--spec); }
.body { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: .6; stroke-linejoin: round; }
.face { fill: url(#body) var(--sheet); }
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1; stroke-linejoin: round; }
.plain { fill: var(--ink); }
.lit { fill: var(--core); }
.halo { fill: var(--blue); opacity: calc(var(--bloom) * .28); }

@keyframes fade { from { opacity: 0; } }
.grid li { animation: fade .7s calc(var(--i, 0) * 90ms) both; }
@media (max-width: 900px) {
  .page { padding: 16px 16px 48px; }
  .top { gap: 13px; padding-bottom: 12px; }
  .name { font-stretch: 112%; margin-right: 0; }
  .grid { grid-template-columns: minmax(0, 1fr); gap: 36px; }
  .tile { padding-top: 22px; }
}
@media (prefers-reduced-motion: reduce) {
  .grid li { animation: none; }
  .top a, .title { transition: none; }
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
</defs></svg>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings" aria-current="page">Findings</a>
    <span class="status" id="status" role="status" hidden>Offline</span>
  </header>
  <p class="say">What the team has found so far.</p>
  <ul class="grid" id="grid"></ul>
</div>
<script>
const $ = id => document.getElementById(id);
const S = { key: "", tiles: [], last: 0 };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1), h = n => n.toFixed(2);

/* Geometry: an icon lives in a small 3D space around one centre (x right, y down, z toward the viewer), as in
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

/* The tiles are built when the list changes. Each frame then redraws only the icons that are on screen: the view
   sways, each tile at its own phase, and leans toward the mouse. With reduced motion there is one still frame. */
function paint(o, t) {
  aim(G.yaw + (still.matches ? 0 : 6 * Math.sin(t * .13 + o.i * 1.3) + 9 * o.px), still.matches ? 0 : 2.5 * Math.sin(t * .09 + o.i * .8) - 5 * o.py);
  o.g.innerHTML = o.icon(kit, t, [o.px, o.py]);
}
function tiles(list) {
  const key = JSON.stringify(list);
  if (key === S.key) return;
  S.key = key;
  $("grid").innerHTML = list.map((x, i) =>
    `<li style="--i:${i}"><a class="tile" href="/finding/${esc(x.slug)}">` +
    `<svg class="icon" viewBox="0 0 ${G.w} ${G.h}" aria-hidden="true">` +
    `<ellipse class="atmo" cx="${G.cx}" cy="${G.cy + 3}" rx="70" ry="42" fill="url(#atmo)"/>` +
    `<ellipse class="shade" cx="${G.cx + 3}" cy="${G.cy + 11}" rx="60" ry="29" fill="url(#shade)"/><g></g></svg>` +
    `<h2 class="title">${esc(x.title)}</h2><p class="line">${esc(x.line)}</p></a></li>`).join("");
  S.tiles = [...$("grid").querySelectorAll(".tile")].map((el, i) =>
    ({ i, el, svg: el.querySelector("svg"), g: el.querySelector("g"), icon: ICONS[list[i].slug] || SLAB, seen: true, px: 0, py: 0, tx: 0, ty: 0 }));
  S.tiles.forEach(o => { paint(o, 0); watch.observe(o.el); });
}
const watch = new IntersectionObserver(found => found.forEach(e => {
  const o = S.tiles.find(o => o.el === e.target);
  if (o) o.seen = e.isIntersecting;
}));
function frame(now) {
  if (!still.matches && now - S.last >= 32) {  // a slow sway needs no more than about 30 frames a second
    S.last = now;
    for (const o of S.tiles) {
      if (!o.seen) continue;
      o.px += (o.tx - o.px) * .1;
      o.py += (o.ty - o.py) * .1;
      paint(o, now / 1000);
    }
  }
  requestAnimationFrame(frame);
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
still.addEventListener("change", () => { S.tiles.forEach(o => paint(o, 0)); });

/* The list changes only when the site is deployed, so one read is enough. A failed read says so and is tried again. */
function read() {
  fetch("/data").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(d => { $("status").hidden = true; tiles(d.findings || []); })
    .catch(e => { console.error(e); $("status").hidden = false; setTimeout(read, 10000); });
}
read();
requestAnimationFrame(frame);
</script>
</body>
</html>
"""

# The tab Proof (/proof) is the same page with these five differences: its tiles are the experiments that test the
# team's method itself (tools/proof_<slug>.py, /proof/<slug>), read from `proofs` of /data. view.py applies them.
PROOF = [
    ('<title>Invariant: Findings</title>', '<title>Invariant: Proof</title>'),
    ('<a href="/proof">Proof</a>\n    <a href="/findings" aria-current="page">Findings</a>',
     '<a href="/proof" aria-current="page">Proof</a>\n    <a href="/findings">Findings</a>'),
    ('What the team has found so far.', 'Experiments that test the harness itself.'),
    ('href="/finding/${esc(x.slug)}"', 'href="/proof/${esc(x.slug)}"'),
    ('tiles(d.findings || [])', 'tiles(d.proofs || [])'),
]
