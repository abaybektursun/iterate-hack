"""The script every finding page and /findings get: terms defined on click, and readable math.

view.py adds TAG before </body> of each page it serves from tools/finding_<slug>.py and of /findings; the page modules
need no change. TAG is computed once, at import.

Terms. In the question (.problem), the finding sentence (.say), the picture's HTML labels (.stage) and each opened
panel (.pane), or any element with the attribute data-terms (/findings marks its first view so), the first use of a
term of tools/glossary.py becomes a quiet control: a dotted underline in the page's own tokens. A click, Enter or Space
shows the term's one-sentence definition in a small box under it; Esc or a click elsewhere closes it. Only whole words
match, the longest spelling first; a spelling with a capital letter matches only as written ("RL", "T 1.0"), any other
in either case. Nothing inside SVG, a button, a link, the control switch or a data-math element is marked, nor a text
that sits directly in a flex or grid box (wrapping it would move the layout). The control is an element of its own
name, <k-term class="kterm">, so no page rule written for span applies to it. A MutationObserver marks again what a
page re-renders. Only the terms whose spelling occurs in the page's source are carried into that page.

Math. The text of every element with the attribute data-math, including elements added or changed later, is turned
from the LaTeX of the problem sets into plain readable text by clean(): delimiters removed, \\frac{a}{b} to a/b with
brackets when needed, \\sqrt{x} to √x, ^2 and _n to superscript and subscript characters where they exist (else ^ and _
are kept), symbols and Greek letters to their characters, \\text{}, \\boxed{}, \\left and \\right removed, \\\\ to a
line break, [asy]...[/asy] to "[diagram]". clean() never drops a digit or a variable; run this file to test it on the
problem texts of tools/finding_rl_edge_comes_early.py and tools/finding_imitation_beats_rl.py (needs node).

A page with no known term and no data-math gets nothing visible.
"""

import json
import re

import glossary

CSS = """
.kterm{cursor:pointer;text-decoration:underline dotted 1px;text-underline-offset:.22em;text-decoration-color:color-mix(in srgb,currentColor 50%,transparent);border-radius:2px;pointer-events:auto}
.kterm:hover,.kterm[aria-expanded=true]{text-decoration-color:var(--blue);text-decoration-style:solid}
.kterm:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.kt-pop{position:fixed;z-index:60;width:max-content;max-width:min(330px,calc(100vw - 32px));margin:0;padding:10px 14px 11px;border-radius:8px;background:var(--sheet);border:1px solid var(--rule);color:var(--mute);font:400 13.5px/1.45 "Archivo",ui-sans-serif,system-ui,sans-serif;font-stretch:100%;letter-spacing:0;text-align:left;white-space:normal}
.kt-pop b{color:var(--ink);font-weight:600}
"""

JS = r"""
(() => {
const T = __TERMS__;  // [term, spellings, definition] of tools/glossary.py
/*math*/
window.KIT_MATH = 1;
const pairs = s => new Map([...s.matchAll(/(.)(.)/gu)].map(m => [m[1], m[2]]));
const SUP = pairs("0⁰1¹2²3³4⁴5⁵6⁶7⁷8⁸9⁹+⁺-⁻−⁻=⁼(⁽)⁾nⁿiⁱ"), SUB = pairs("0₀1₁2₂3₃4₄5₅6₆7₇8₈9₉+₊-₋−₋=₌(₍)₎aₐeₑoₒxₓhₕkₖlₗmₘnₙpₚsₛtₜiᵢjⱼrᵣuᵤvᵥ");
const kv = s => { const l = s.split(" "), o = {}; for (let i = 0; i < l.length; i += 2) o[l[i]] = l[i + 1]; return o; };
const SYM = Object.assign(kv("alpha α beta β gamma γ delta δ epsilon ε varepsilon ε zeta ζ eta η theta θ vartheta ϑ iota ι kappa κ lambda λ mu μ nu ν xi ξ pi π rho ρ sigma σ tau τ upsilon υ phi φ varphi φ chi χ psi ψ omega ω Gamma Γ Delta Δ Theta Θ Lambda Λ Xi Ξ Pi Π Sigma Σ Phi Φ Psi Ψ Omega Ω infty ∞ angle ∠ measuredangle ∠ triangle △ circ ∘ deg ° degree ° prime ′ ldots … dots … dotsc … cdots ⋯ dotsm ⋯ dotsb ⋯ emptyset ∅ varnothing ∅ sum ∑ prod ∏ int ∫ partial ∂ forall ∀ exists ∃ neg ¬ star ⋆ bullet • square □ diamond ◇ clubsuit ♣ spadesuit ♠ heartsuit ♡ diamondsuit ♢ ell ℓ lfloor ⌊ rfloor ⌋ lceil ⌈ rceil ⌉ langle ⟨ rangle ⟩ vert | lvert | rvert | Vert ‖ | ‖ { { } } $ $ % % & & # # _ _ backslash \\"),
  { "\\": "\u2028", " ": " ", ",": " ", ";": " ", ":": " ", ">": " ", quad: " ", qquad: " ", "!": "", "[": "\u2028", "]": "\u2028", "(": "", ")": "", mod: " mod ", bmod: " mod " });
const BIN = kv("cdot · times × div ÷ pm ± mp ∓ le ≤ leq ≤ leqslant ≤ ge ≥ geq ≥ geqslant ≥ ne ≠ neq ≠ approx ≈ equiv ≡ sim ∼ cong ≅ in ∈ notin ∉ subset ⊂ subseteq ⊆ cup ∪ cap ∩ to → rightarrow → Rightarrow ⇒ implies ⇒ leftarrow ← iff ⇔ Leftrightarrow ⇔ perp ⊥ parallel ∥ mid | wedge ∧ vee ∨ oplus ⊕ over /");
const DROP = new Set("left right big Big bigg Bigg bigl bigr Bigl Bigr displaystyle textstyle allowbreak limits nolimits hline noindent centering".split(" "));
const KEEP = new Set("text textbf textit textrm textsf texttt textnormal mathrm mathbf mathit mathsf mathtt mathcal mathfrak mathscr boldsymbol bold bm mbox emph operatorname boxed fbox underline mathop underbrace overbrace hbox".split(" "));
const SKIPARG = new Set("color label hspace vspace phantom hphantom vphantom".split(" "));
const ACC = { overline: "\u0305", bar: "\u0304", hat: "\u0302", widehat: "\u0302", vec: "\u20d7", overrightarrow: "\u20d7", tilde: "\u0303", widetilde: "\u0303", dot: "\u0307", ddot: "\u0308" };
const BB = { R: "ℝ", Z: "ℤ", N: "ℕ", Q: "ℚ", C: "ℂ" };
function arg(s, i) {  // the next argument at i: a {group}, a \command or one character; [text, index after it]
  while (s[i] === " " || s[i] === "\n") i++;
  if (s[i] === "{") {
    let d = 0, j = i;
    for (; j < s.length; j++) { if (s[j] === "\\") { j++; continue; } if (s[j] === "{") d++; else if (s[j] === "}" && --d === 0) break; }
    return [s.slice(i + 1, j), j + 1];
  }
  if (s[i] === "\\") { const m = /^\\(?:[A-Za-z]+|[^])/.exec(s.slice(i)); return [m[0], i + m[0].length]; }
  return [s[i] ?? "", i + 1];
}
const atom = t => /^[^\s+\-−*/·×÷=<>≤≥,±:;]*$/.test(t.replace(/\([^()]*\)/g, "X").replace(/\([^()]*\)/g, "X"));
const wrap = t => (t = t.trim(), atom(t) ? t : "(" + t + ")");
const under = t => (t = t.trim(), /^(?:[\d.]+|√?\p{L}|√?\d+|\([^()]*\))[⁰-⁹¹²³⁺⁻ⁿⁱ₀-₉ₐ-ₜ]*$/u.test(t) ? t : "(" + t + ")");  // a denominator
function script(t, c) {
  const u = t.trim(), map = c === "^" ? SUP : SUB, v = u.replace(/\s+/g, "");
  if (c === "^" && /^[∘°]$/.test(v)) return "°";
  if (/^′+$/.test(v)) return v;
  if (v && [...v].every(ch => map.has(ch))) return [...v].map(ch => map.get(ch)).join("");
  return c + (v.length === 1 ? v : wrap(u));
}
function tex(s) {
  let out = "", i = 0, a, b;
  while (i < s.length) {
    const c = s[i];
    if (c === "\\") {
      const m = /^\\(?:([A-Za-z]+)|([^]))/.exec(s.slice(i)), name = m[1] || m[2];
      i += m[0].length;
      if (/^[dtc]?frac$/.test(name)) {
        [a, i] = arg(s, i); [b, i] = arg(s, i);
        out += (/[\w)]$/.test(out) ? " " : "") + wrap(tex(a)) + "/" + under(tex(b));
      } else if (/^[dt]?binom$/.test(name)) { [a, i] = arg(s, i); [b, i] = arg(s, i); out += `C(${tex(a).trim()}, ${tex(b).trim()})`; }
      else if (name === "sqrt") {
        let n = "";
        if (s[i] === "[") { const j = s.indexOf("]", i); n = tex(s.slice(i + 1, j < 0 ? s.length : j)); i = j < 0 ? s.length : j + 1; }
        [a, i] = arg(s, i);
        out += (n ? script(n, "^").replace(/^\^/, "") : "") + "√" + wrap(tex(a));
      } else if (KEEP.has(name)) { [a, i] = arg(s, i); out += tex(a); }
      else if (SKIPARG.has(name)) { [a, i] = arg(s, i); }
      else if (ACC[name]) { [a, i] = arg(s, i); out += tex(a).replace(/[\p{L}\p{N}]/gu, ch => ch + ACC[name]); }
      else if (name === "mathbb") { [a, i] = arg(s, i); out += BB[a.trim()] ?? tex(a); }
      else if (name === "not") { [a, i] = arg(s, i); out += tex(a) + "\u0338"; }
      else if (name === "pmod") { [a, i] = arg(s, i); out += ` (mod ${tex(a).trim()})`; }
      else if (name === "tag") { [a, i] = arg(s, i); out += ` (${tex(a).trim()})`; }
      else if (name === "begin" && /matrix/.test(s.slice(i, i + 20))) {
        [a, i] = arg(s, i);
        const j = s.indexOf("\\end{" + a, i), rows = s.slice(i, j < 0 ? s.length : j).split("\\\\").map(r => r.split("&").map(x => tex(x).trim()).join(" ")).filter(r => r);
        out += "(" + rows.join(rows.some(r => r.includes(" ")) ? "; " : ", ") + ")";
        i = j < 0 ? s.length : j;
      } else if (name === "begin" || name === "end") { [a, i] = arg(s, i); if (name === "begin" && /array|tabular/.test(a)) [b, i] = arg(s, i); out += " "; }
      else if (DROP.has(name)) { if (s[i] === ".") i++; }
      else if (BIN[name]) out += " " + BIN[name] + " ";
      else if (name in SYM) out += SYM[name];
      else out += (/^[a-z]{2,}$/.test(name) && /[\p{L}\p{N}]$/u.test(out) ? " " : "") + name;
    } else if (c === "^" || c === "_") { [a, i] = arg(s, i + 1); out += script(tex(a), c); }
    else if (c === "{") { [a, i] = arg(s, i); out += tex(a); }
    else if (c === "}" || c === "$") i++;
    else { out += c === "~" || c === "&" ? " " : c; i++; }
  }
  return out;
}
function clean(text) {
  return tex(String(text).replace(/\[asy\][^]*?(?:\[\/asy\]|$)/g, " [diagram] ")).replace(/[ \t]{2,}/g, " ").replace(/ ([,;)])| \.(?=\s|$)/g, (m, c) => c || ".").replace(/\s*\u2028[\s\u2028]*/g, "\u2028").replace(/^\u2028|\u2028$/g, "");
}
const DONE = new WeakMap();  // text node -> the text clean() wrote into it
function math(el) {
  const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), nodes = [];
  while (w.nextNode()) nodes.push(w.currentNode);
  for (const n of nodes) {
    if (DONE.get(n) === n.data || !/[\\^_$\[{~]/.test(n.data)) continue;
    const parts = clean(n.data).split("\u2028");
    n.data = parts[0]; DONE.set(n, n.data);
    let at = n;
    for (const p of parts.slice(1)) { const t = document.createTextNode(p); DONE.set(t, p); at.after(document.createElement("br"), t); at = t; }
  }
}
/*end math*/

const REG = ".problem,.say,.stage,.pane,[data-terms]";
const NOT = "svg,button,a,input,textarea,select,label,.switch,[role=button],[role=switch],[role=tab],[role=slider],[data-math],.kterm,[contenteditable],script,style";
const SPELL = new Map();
T.forEach(t => t[1].forEach(s => SPELL.set(/[A-Z]/.test(s) ? s : s.toLowerCase(), t)));
const RX = new RegExp("(?<![\\w-])(?:" + [...SPELL.keys()].sort((a, b) => b.length - a.length).map(s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")(?![\\w-])", "gi");
const termOf = w => SPELL.get(w) ?? SPELL.get(w.toLowerCase());
const busy = new WeakMap();  // region -> [passes, since]: a region rewritten over and over is left alone
function mark(r) {
  if (r.closest("svg")) return;
  const now = performance.now(), b = busy.get(r) ?? [0, now];
  if (now - b[1] > 3000) b.splice(0, 2, 0, now);
  if (++b[0] > 40) return;
  busy.set(r, b);
  const used = new Set([...r.querySelectorAll(".kterm")].map(e => e.dataset.k));
  const w = document.createTreeWalker(r, NodeFilter.SHOW_TEXT, { acceptNode: n => {
    const p = n.parentElement;
    return p && !p.closest(NOT) && p.closest(REG) === r && !/flex|grid/.test(getComputedStyle(p).display) ? 1 : 2;
  } });
  const nodes = [];
  while (w.nextNode()) nodes.push(w.currentNode);
  for (let n of nodes) {
    RX.lastIndex = 0;
    for (let m; (m = RX.exec(n.data));) {
      const t = termOf(m[0]);
      if (!t || used.has(t[0])) continue;
      used.add(t[0]);
      const word = n.splitText(m.index), s = document.createElement("k-term");
      n = word.splitText(m[0].length);
      s.className = "kterm"; s.tabIndex = 0; s.dataset.k = t[0];
      s.setAttribute("role", "button"); s.setAttribute("aria-expanded", "false");
      word.replaceWith(s); s.append(word);
      RX.lastIndex = 0;
    }
  }
}

let pop = null, cur = null;
function place() {
  const r = cur.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight, below = r.bottom + 8 + h <= innerHeight || r.top - 8 - h < 0;
  pop.style.left = Math.max(16, Math.min(innerWidth - 16 - w, r.left)) + "px";
  pop.style.top = (below ? r.bottom + 8 : r.top - 8 - h) + "px";
}
function hide() {
  if (!cur) return;
  cur.setAttribute("aria-expanded", "false"); cur.removeAttribute("aria-describedby");
  cur = null; pop.hidden = true;
}
function show(s) {
  const was = cur, t = T.find(t => t[0] === s.dataset.k);
  hide();
  if (was === s || !t) return;
  if (!pop) { pop = document.createElement("p"); pop.className = "kt-pop"; pop.id = "kt-pop"; pop.setAttribute("role", "tooltip"); document.body.append(pop); }
  const b = document.createElement("b");
  b.textContent = t[0];
  pop.replaceChildren(b, " " + t[2]);
  pop.hidden = false; cur = s;
  s.setAttribute("aria-expanded", "true"); s.setAttribute("aria-describedby", "kt-pop");
  place();
}
addEventListener("click", e => {
  const s = e.target.closest?.(".kterm");
  if (s) { e.preventDefault(); e.stopPropagation(); show(s); }
  else if (cur && !pop.contains(e.target)) hide();
}, true);
addEventListener("keydown", e => {
  const s = e.target.closest?.(".kterm");
  if (s && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); e.stopPropagation(); show(s); }
  else if (cur && e.key === "Escape") { e.stopPropagation(); const was = cur; hide(); was.focus(); }
}, true);
addEventListener("scroll", () => { if (cur) cur.isConnected ? place() : hide(); }, true);
addEventListener("resize", () => { if (cur) place(); });

function run(regs, maths) {
  if (window.KIT_MATH) maths.forEach(math);
  regs.forEach(mark);
  if (cur && !cur.isConnected) hide();
}
const all = () => run(document.querySelectorAll(REG), document.querySelectorAll("[data-math]"));
const mo = new MutationObserver(recs => {
  const regs = new Set(), maths = new Set();
  const up = el => { const r = el.closest(REG), m = el.closest("[data-math]"); if (r) regs.add(r); if (m) maths.add(m); };
  for (const r of recs) {
    const el = r.target.nodeType === 1 ? r.target : r.target.parentElement;
    if (el) up(el);
    for (const n of r.addedNodes) if (n.nodeType === 1) { up(n); n.querySelectorAll(REG).forEach(e => regs.add(e)); n.querySelectorAll("[data-math]").forEach(e => maths.add(e)); }
  }
  run(regs, maths);
  mo.takeRecords();  // the marks just written
});
all();
mo.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ["data-math"] });
})();
"""


def _lean(text):  # leading spaces, end-of-line comments ("  // ...") and blank lines out; nothing else is changed
    return "\n".join(re.sub(r"\s{2}// .*$", "", line).strip() for line in text.strip().splitlines() if line.strip())


CODE, START, END = _lean(JS), "/*math*/", "/*end math*/"


def terms(page=None):
    """The glossary as the kit carries it, [term, spellings, definition]: the terms a spelling of which is in the page."""
    def found(s):
        return re.search(r"(?<![\w-])" + re.escape(s) + r"(?![\w-])", page, 0 if re.search("[A-Z]", s) else re.I)
    return [[t["term"], t["match"], t["definition"]] for t in glossary.TERMS if page is None or any(found(s) for s in t["match"])]


def tag(page):
    """The kit for one page: its terms, and the math code only when the page holds data-math; nothing when it needs neither."""
    used, math = terms(page), "data-math" in page
    if not used and not math:
        return ""
    code = CODE if math else CODE[:CODE.index(START)] + CODE[CODE.index(END):]
    return "<style>" + _lean(CSS) + "</style>\n<script>\n" + code.replace("__TERMS__", json.dumps(used, ensure_ascii=False, separators=(",", ":"))) + "\n</script>\n"


def add(page):
    """The page with its kit before its </body>."""
    assert page.count("</body>") == 1, "a page for the kit has one </body>"
    return page.replace("</body>", tag(page) + "</body>")


if __name__ == "__main__":  # test clean() on the problem texts of two finding modules, with node
    import os
    import subprocess
    import sys
    import tempfile

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import finding_imitation_beats_rl as imitation
    import finding_rl_edge_comes_early as edge

    texts = [p[1] for p in edge.PROBLEMS] + [p[2] for p in edge.PROBLEMS]
    texts += [x for rows in imitation.PROBLEMS.values() for p in rows for x in (p[2], p[3])]
    texts = list(dict.fromkeys(t for t in texts if isinstance(t, str)))
    code = JS[JS.index("/*math*/"):JS.index("/*end math*/")]
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write("const window = {};\n" + code + "\nconst fs = require('fs');\nconst T = JSON.parse(fs.readFileSync(0, 'utf8'));\n"
                "process.stdout.write(JSON.stringify(T.map(clean)));\n")
    out = json.loads(subprocess.run(["node", f.name], input=json.dumps(texts), capture_output=True, text=True, check=True).stdout)
    os.unlink(f.name)
    back = {**{v: k for k, v in zip("0123456789+-=()ni", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ")},
            **{v: k for k, v in zip("0123456789+-=()aeoxhklmnpstijruv", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜᵢⱼᵣᵤᵥ")},
            "ℝ": "R", "ℤ": "Z", "ℕ": "N", "ℚ": "Q", "ℂ": "C"}

    def kept(text):  # the digits and letters a reader must still see: commands, environment names and diagrams aside
        text = re.sub(r"\[asy\][\s\S]*?(\[/asy\]|$)", " ", text)
        text = re.sub(r"\\(begin|end)\{[^}]*(\}|$)(\{[^}]*\})?|\\[A-Za-z]+", " ", text)
        return sorted(c for c in text if c.isascii() and c.isalnum())

    bad = []
    for t, o in zip(texts, out):
        seen = sorted(c for c in "".join(back.get(c, c) for c in o) if c.isascii() and c.isalnum())
        missing = [c for c in set(kept(t)) if kept(t).count(c) > seen.count(c)]
        raw = re.search(r"\\[A-Za-z]", o)
        if missing or raw:
            bad.append((t, o, missing, raw and raw.group(0)))
    full = tag("data-math " + " ".join(s for t in glossary.TERMS for s in t["match"]))
    print(f"{len(texts)} texts, {len(bad)} with a dropped digit or letter or a leftover command; kit with every term and math {len(full.encode())} bytes")
    for t, o, missing, raw in bad[:10]:
        print("---", missing, raw, "\n", t[:300], "\n =>", o[:300])
    if "--show" in sys.argv:
        for t, o in list(zip(texts, out))[:: max(1, len(texts) // 10)][:10]:
            print("BEFORE", json.dumps(t)[:400], "\nAFTER ", json.dumps(o, ensure_ascii=False)[:400], "\n")
    sys.exit(1 if bad else 0)
