"""The main figure of the paper, drawn from facts.json only (NOTES.md defines every quantity).
Run: uv run --no-project --with matplotlib python studies/rlneurons/paper-depth-rank/figs.py [png folder]
-> fig_split.pdf next to this file; with a folder argument also a 200 dpi PNG there."""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).parent
F = json.loads((HERE / "facts.json").read_text())
RANK, DEPTH, MUTED, INK, GRID = "#2563EB", "#C2410C", "#6B7280", "#1F2937", "#E5E7EB"
for font in sorted((HERE / "fonts").glob("texgyrepagella-*.otf")):  # the body face of the paper (GUST font licence)
    font_manager.fontManager.addfont(font)
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["TeX Gyre Pagella"], "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "xtick.major.size": 3, "ytick.major.size": 3, "pdf.fonttype": 42,
})
SMALL = dict(fontsize=7.5, linespacing=1.1)
KNOCKOUT = dict(boxstyle="square,pad=0.1", fc="white", ec="none")  # hides the grid and zero lines behind a label

# The cells drawn, in drawing order: (key on hard328, key on Code, label, colour). A key absent from facts.json is skipped,
# so a cell added to the facts later appears without a change here. Code's all-8 cell is called top8x1.5 there.
# Every rank cell is at scale 1.5x; the late band at 3.0x is twice the scale of the bands (x4.5 breaks the model: not drawn).
CELLS = [
    ("all8", "top8x1.5", "all 8 directions", RANK),
    ("top1x1.5", "top1x1.5", "direction 1 alone", RANK),
    ("d2-8", "d2-8", "directions 2–8", RANK),
    ("L0-10", "L0-10", "layers 0–10", DEPTH),
    ("L11-21", "L11-21", "layers 11–21", DEPTH),
    ("L22-31", "L22-31", "layers 22–31", DEPTH),
    ("L22-31x3.0", "L22-31x3.0", "layers 22–31,\nscale 3.0", DEPTH),
    ("rand8x1.5", "rand8x1.5", "random directions", MUTED),
]
# Where each label sits, as layout only, no data: the end of the interval arm it hangs from (right/left: beyond the end of
# the horizontal arm; top/bottom: beyond the end of the vertical arm), or a corner next to the marker (ne/se: above/below
# right of it), optionally with an extra (dx, dy) in points.
PLACE = {
    "math": {"all 8 directions": "bottom", "directions 2–8": "right",
             "layers 0–10": "right", "layers 11–21": ("right", 0, 5), "direction 1 alone": ("right", 0, -3),
             "layers 22–31": "left", "layers 22–31,\nscale 3.0": "bottom-left", "random directions": "ne"},
    "code": {"all 8 directions": "bottom", "layers 0–10": ("ne", 0, 6), "layers 11–21": "left", "layers 22–31": "right",
             "random directions": ("se", 16, 0)},
}
DEFAULT_PLACE = "right"
ARM = {"right": (3, 0, "left", "center"), "left": (-3, 0, "right", "center"), "top": (0, 2, "center", "bottom"),
       "bottom": (0, -2, "center", "top"), "bottom-left": (2, -2, "right", "top"), "ne": (4, 3, "left", "bottom"),
       "se": (4, -3, "left", "top")}


def points(setting, key):
    """(right, cut_off, n_samples) of a cell minus the cued base; each of the two is (value, low, high), 95 % interval."""
    cell = F[setting][key]
    mb = cell["minus_base"]
    out = []
    for m in ("right", "cut_off"):
        lo, hi = mb[m]["ci95"]
        assert lo <= mb[m]["value"] <= hi and mb[m]["n"] == cell["n_problems"], (key, m)
        out.append((mb[m]["value"], lo, hi))
    return out[0], out[1], cell["n_samples"]


def panel(ax, setting, which, title):
    n = F[setting]["base_cue"]["n_problems"]
    drawn = {}
    for math_key, code_key, label, color in CELLS:
        key = math_key if which == "math" else code_key
        if key not in F[setting]:
            continue
        (x, xlo, xhi), (y, ylo, yhi), samples = points(setting, key)
        drawn[label] = (x, y)
        ax.plot([xlo, xhi], [y, y], color=color, lw=0.55, alpha=0.6, solid_capstyle="butt", zorder=3)
        ax.plot([x, x], [ylo, yhi], color=color, lw=0.55, alpha=0.6, solid_capstyle="butt", zorder=3)
        filled = samples >= 2  # so a second sample of a cell turns its marker filled
        if label.startswith("layers 22–31,") and "layers 22–31" in drawn:  # the same band at twice the scale
            ax.annotate("", (x, y), xytext=drawn["layers 22–31"], zorder=4, arrowprops=dict(
                arrowstyle="-|>,head_length=0.45,head_width=0.2", color=color, lw=0.8, shrinkA=4, shrinkB=4))
        ax.plot(x, y, ls="", marker="o", ms=5, mew=1.0, color=color, mfc=color if filled else "white", zorder=5)
        side, ex, ey = (lambda p: (p, 0, 0) if isinstance(p, str) else p)(PLACE[which].get(label, DEFAULT_PLACE))
        anchor = {"right": (xhi, y), "left": (xlo, y), "top": (x, yhi), "bottom": (x, ylo), "bottom-left": (x, ylo),
                  "ne": (x, y), "se": (x, y)}[side]
        dx, dy, ha, va = ARM[side]
        ax.annotate(label, anchor, xytext=(dx + ex, dy + ey), textcoords="offset points", ha=ha, va=va, color=color,
                    zorder=6, bbox=KNOCKOUT, **SMALL)
    ax.plot(0, 0, ls="", marker="o", ms=5, color=INK, zorder=5)
    ax.annotate("base + cue", (0, 0), xytext=(-4, -3), textcoords="offset points", ha="right", va="top", color=INK,
                bbox=KNOCKOUT, **SMALL)
    ax.axhline(0, color=MUTED, lw=0.6, ls=(0, (4, 3)), zorder=1)
    ax.axvline(0, color=MUTED, lw=0.6, ls=(0, (4, 3)), zorder=1)
    ax.grid(color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    ax.set_xlabel("change in right answers (points)")
    ax.set_title(f"{title} ({n} problems)", loc="left", fontsize=9, color=INK, pad=6)
    return drawn


fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.9), constrained_layout=True)
math = panel(axes[0], "hard328_cells", "math", "Math")
code = panel(axes[1], "code_cells", "code", "Code")
axes[0].set_xlim(-6.5, None)
axes[0].set_ylim(-22.5, None)
axes[1].set_xlim(-4.5, None)
axes[1].set_ylim(-7, None)
axes[0].set_ylabel("change in answers cut off\nat the token limit (points)")

# The headline values the text relies on: a change in the facts must fail here, not move the picture silently.
one = lambda v: round(v + 1e-9, 1)  # one decimal, halves up as in the text
r = {k: tuple(one(v) for v in xy) for k, xy in math.items()}
assert r["directions 2–8"] == (9.5, -0.6), r
assert r["direction 1 alone"] == (7.5, -9.3), r
assert r["layers 0–10"] == (7.6, 6.3), r
assert r["layers 11–21"] == (6.9, -8.1), r
assert r["layers 22–31"] == (1.5, -4.7), r
assert r["layers 22–31,\nscale 3.0"] == (-1.2, -13.4), r
assert r["all 8 directions"] == (12.7, -16.0), r
c = {k: tuple(one(v) for v in xy) for k, xy in code.items()}
assert c["layers 0–10"] == (10.2, -2.8) and c["layers 22–31"] == (4.7, 1.3), c

fig.savefig(HERE / "fig_split.pdf")
if len(sys.argv) > 1:
    fig.savefig(Path(sys.argv[1]) / "fig_split.png", dpi=200)
