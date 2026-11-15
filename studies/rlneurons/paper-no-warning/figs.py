"""The figure of the paper, drawn from facts.json only (NOTES.md defines every quantity).
Run: uv run --no-project --with matplotlib --with numpy python studies/rlneurons/paper-no-warning/figs.py [png folder]
-> fig_warning.pdf next to this file; with a folder argument also a 200 dpi PNG there."""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).parent
F = json.loads((HERE / "facts.json").read_text())
BASE, RL, MUTED, INK, GRID, NONE = "#C2410C", "#2563EB", "#6B7280", "#1F2937", "#E5E7EB", "#ECEEF1"
for font in sorted((HERE / "fonts").glob("texgyrepagella-*.otf")):  # the body face of the paper (GUST font licence)
    font_manager.fontManager.addfont(font)
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["TeX Gyre Pagella"], "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "xtick.major.size": 3, "ytick.major.size": 3, "pdf.fonttype": 42, "hatch.linewidth": 0.6,
})
REC, PROBE, CEIL, N = F["recomputed"]["math500_base_cue"], F["copied"]["probe"]["cells"], F["ceiling_math500"], 500
TOKENS = [0, 250, 500, 1000, 2000, 4000, 8000, 12000]  # evenly spaced; 0 is the last prompt token
END = len(TOKENS) + 0.7  # "end of answer", set apart from the token positions
LAYERS = [12, 20, 28]
SMALL = dict(fontsize=7.5, linespacing=1.1)


def title(ax, text):
    ax.set_title(text, loc="left", fontsize=9, color=INK, pad=6)


def save(fig, name):
    fig.savefig(HERE / f"{name}.pdf")
    if len(sys.argv) > 1:
        fig.savefig(Path(sys.argv[1]) / f"{name}.png", dpi=200)


def number(v):
    return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.1f}"


def within(cell):
    """(AUROC, low, high) of a within-problem cell."""
    assert cell["unit"] == "AUROC, pairs within one problem", cell
    lo, hi = cell["ci95"]
    assert lo <= cell["value"] <= hi
    return cell["value"], lo, hi


def interval(ax, x, cell, color, **marker):
    v, lo, hi = cell
    ax.plot([x, x], [lo, hi], color=color, lw=0.9, solid_capstyle="butt", zorder=4)
    ax.plot(x, v, ls="", color=color, zorder=5, **marker)


def left_panel(a):
    """Within-problem AUROC of each instrument against how much of the answer it has seen."""
    x = {t: i for i, t in enumerate(TOKENS)}
    lo_y, hi_y = 0.40, 0.95  # the widest probe interval reaches 0.43

    # the token counter: length so far at t, then the final length
    at = [1000, 2000, 4000, 8000, 12000]
    counter = [within(REC[f"length_so_far_{t}"]["within"]) for t in at] + [within(REC["shorter_final"]["within"])]
    assert [round(v, 3) for v, _, _ in counter] == [0.497, 0.521, 0.572, 0.625, 0.662, 0.680]
    xs = [x[t] for t in at] + [END]
    a.fill_between(xs, [c[1] for c in counter], [c[2] for c in counter], color=INK, alpha=0.10, lw=0, zorder=1)
    a.plot(xs, [c[0] for c in counter], color=INK, lw=1.4, marker="o", ms=3.6, mec="white", mew=0.5, zorder=3)

    # the linear probe: the label-free flag as target (the spec's cells, the README table), the best of
    # layers 12 / 20 / 28 at each position; at the last prompt token every layer gives 0.5 exactly
    best = {}
    for t in TOKENS[:5]:
        cells = {layer: within(PROBE[f"probe_L{layer}@{t}/within_flag"]) for layer in LAYERS}
        layer = max(cells, key=lambda k: cells[k][0])
        best[t] = (layer, cells[layer])
        interval(a, x[t] - (0.16 if t else 0), cells[layer], BASE, marker="o", ms=4.6, mec="white", mew=0.6)
    assert all(within(PROBE[f"probe_L{layer}@0/within_flag"]) == (0.5, 0.5, 0.5) for layer in LAYERS)
    head = F["copied"]["probe"]["summary"]["within_flag"]
    assert head["best_cell"] == "probe_L12@1000/within_flag" and best[1000] == (12, within(head["best"]))
    assert [round(c, 3) for c in best[1000][1]] == [0.571, 0.509, 0.634]
    assert max(c[0] for _, c in best.values()) == best[1000][1][0] and min(c[1] for _, c in best.values()) > lo_y

    # the zlib ratio of the first 6,000 characters, about 2,000 tokens
    z = within(REC["zratio_6000"]["within"])
    assert [round(c, 3) for c in z] == [0.564, 0.497, 0.629]
    interval(a, x[2000] + 0.16, z, MUTED, marker="s", ms=4, mfc="white", mew=1.0)

    # agreement with the other three samples, known only at the end
    agree = within(REC["agreement"]["within"])
    assert [round(c, 3) for c in agree] == [0.893, 0.855, 0.929]
    interval(a, END, agree, RL, marker="D", ms=5, mec="white", mew=0.6)

    # the same probe across problems, at the last prompt token (no interval stored)
    across = [PROBE[f"probe_L{layer}@0/pooled_correct"]["value"] for layer in LAYERS]
    assert [round(v, 2) for v in (min(across), max(across))] == [0.73, 0.77]
    a.fill_between([-0.16, x[500] + 0.16], min(across), max(across), color=BASE, alpha=0.13, lw=0, zorder=1)

    a.axhline(0.5, color=MUTED, lw=0.6, ls=(0, (4, 3)), zorder=0)
    a.text(END + 0.7, 0.494, "chance", color=MUTED, ha="right", va="top", **SMALL)
    a.text(-0.16, max(across) + 0.008, f"the same probe across problems: {min(across):.2f}–{max(across):.2f}", color=tint(BASE, 0.6),
           ha="left", va="bottom", **SMALL)
    a.plot([-0.16, -0.16, x[2000] + 0.16, x[2000] + 0.16], [0.652, 0.66, 0.66, 0.652], color=MUTED, lw=0.6)
    a.text(-0.16, 0.667, "first 2,000 tokens: no instrument above 0.59", color=MUTED, ha="left", va="bottom", **SMALL)
    a.text(-0.16, 0.407, "linear probe, best of 3 layers", color=BASE, ha="left", va="bottom", **SMALL)
    a.text(x[1000] - 0.3, best[1000][1][0], f"{best[1000][1][0]:.2f}", color=BASE, ha="right", va="center", **SMALL)
    a.text(x[2000] + 0.34, 0.452, f"text compression ratio {z[0]:.2f}", color=MUTED, ha="left", va="center", **SMALL)
    a.annotate("", (x[2000] + 0.2, z[0] - 0.012), (x[2000] + 0.75, 0.466),
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5, shrinkA=0, shrinkB=0))
    a.text(x[8000] + 0.5, 0.574, "token counter: which attempts\nhave ended, and when", color=INK, ha="left", va="top", **SMALL)
    a.text(END + 0.2, counter[-1][0], f"{counter[-1][0]:.2f}", color=INK, ha="left", va="center", **SMALL)
    a.text(END - 0.25, agree[0], f"agreement with\n3 other samples {agree[0]:.2f}", color=RL, ha="right", va="center", **SMALL)

    a.set_xlim(-0.5, END + 0.75)
    a.set_ylim(lo_y, hi_y)
    a.set_xticks(list(x.values()) + [END])
    a.set_xticklabels(["0", "250", "500", "1,000", "2,000", "4,000", "8,000", "12,000", "end of\nanswer"], color=INK,
                      fontsize=7.5, linespacing=1.0)
    a.set_xlabel("answer tokens written", x=(3.5 + 0.5) / (END + 1.25))
    a.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9])
    a.spines["bottom"].set_visible(False)  # two pieces: the token positions, then the end
    a.plot([0, x[12000]], [lo_y, lo_y], color=MUTED, lw=0.6, clip_on=False, solid_capstyle="butt")
    a.plot([END - 0.3, END + 0.3], [lo_y, lo_y], color=MUTED, lw=0.6, clip_on=False, solid_capstyle="butt")
    a.grid(axis="y", color=GRID, lw=0.5)
    a.set_axisbelow(True)
    title(a, "Telling the right attempt from the wrong one\nof the same problem (AUROC, MATH-500)")


def tint(color, share):
    """The colour mixed with white: share 1 is the colour itself."""
    rgb = matplotlib.colors.to_rgb(color)
    return tuple(1 - share * (1 - c) for c in rgb)


def right_panel(b):
    """Right of 500 for the base + cue under each way of choosing among 4 samples; the last bar is a ceiling."""
    bars = [("base_cue_single", "one\nsample"), ("base_cue_shortest", "shortest\nof 4"), ("base_cue_vote", "vote\nof 4"),
            ("base_cue_oracle4", "perfect\ncritic, 4")]
    assert CEIL["n_problems"] == N and all(CEIL[k]["n"] == N for k, _ in bars)
    y = [CEIL[k]["value"] for k, _ in bars]
    rl = CEIL["rl_single"]["value"]
    assert y == [410.5, 434.0, 446.0, 467.0] and rl == 460.0
    lo, hi = 380, 480
    assert lo < min(y) and y[2] < rl < y[3] < hi
    b.bar(range(3), [v - lo for v in y[:3]], bottom=lo, width=0.66, color=BASE, lw=0)
    b.bar(3, y[3] - lo, bottom=lo, width=0.66 - 0.04, color="white", ec=BASE, lw=0.9, hatch="////")
    for i, v in enumerate(y):
        b.text(i, v + 1.5, number(v), color=BASE, ha="center", va="bottom", **SMALL)
    b.plot([-0.5, 3.5], [rl, rl], color=RL, lw=1.2, zorder=3)
    b.text(-0.5, rl + 1.5, f"RL, one sample {number(rl)}", color=RL, ha="left", va="bottom", **SMALL)
    b.set_xlim(-0.6, 3.6)
    b.set_ylim(lo, hi)
    b.set_xticks(range(4))
    b.set_xticklabels([label for _, label in bars], color=INK, fontsize=7.5, linespacing=1.0)
    b.set_xlabel("base + cue")
    b.set_yticks(range(lo, hi + 1, 20))
    b.spines["bottom"].set_bounds(-0.33, 3.33)
    b.set_ylabel(f"axis starts at {lo}", color=MUTED, fontsize=7.5)
    title(b, "What a critic is worth\n(right of 500)")


fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.9), constrained_layout=True, gridspec_kw={"width_ratios": [1.6, 1]})
left_panel(axes[0])
right_panel(axes[1])
save(fig, "fig_warning")
