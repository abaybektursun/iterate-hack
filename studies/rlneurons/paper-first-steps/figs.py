"""Figures of the paper, drawn from facts.json only (NOTES.md defines every quantity).
Run: uv run --no-project --with matplotlib --with numpy python studies/rlneurons/paper-first-steps/figs.py [png folder]
-> fig_curve.pdf next to this file; with a folder argument also a 200 dpi PNG there."""
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
    "ytick.major.width": 0.6, "xtick.major.size": 3, "ytick.major.size": 3, "pdf.fonttype": 42,
})
CELLS, FOUR, NOISE, DIFF, N = F["cells_T10"], F["cells_T10_four_samples"], F["seed_noise_T10"], F["differences_T10_four_sample_means"], 500
STAGES = ["base", "100", "400", "2,800"]  # the base, then the RL step of each checkpoint


def title(ax, text):
    ax.set_title(text, loc="left", fontsize=9, color=INK, pad=6)


def save(fig, name):
    fig.savefig(HERE / f"{name}.pdf")
    if len(sys.argv) > 1:
        fig.savefig(Path(sys.argv[1]) / f"{name}.png", dpi=200)


def samples(cell):
    """Right of 500 in each of the four samples of a cell."""
    s, m = FOUR[cell]["right_per_sample"], FOUR[cell]["mean_right"]
    assert s["n"] == m["n"] == N and len(s["value"]) == 4 and abs(sum(s["value"]) / 4 - m["value"]) < 0.01, cell
    assert NOISE[cell]["right_per_sample"]["value"] == s["value"], cell
    return s["value"]


def mean(values):
    return sum(values) / len(values)


def number(v):
    return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.1f}"


def tint(color, share):
    """The colour mixed with white: share 1 is the colour itself."""
    rgb = matplotlib.colors.to_rgb(color)
    return tuple(1 - share * (1 - c) for c in rgb)


def left_panel(a):
    """Colour is the model (orange: the untrained base, blue: RL), fill is the prompt (filled: plain, hollow: cue)."""
    cells = {c: samples(c) for c in ["base_cue", "s100_plain", "s100_cue", "s400_plain", "final_plain"]}
    y = {c: mean(s) for c, s in cells.items()}
    assert CELLS["base_plain"]["right"]["n"] == N
    y["base_plain"] = CELLS["base_plain"]["right"]["value"]  # one sample: the only plain run of the base
    own, edit = F["selfopen"]["right"], F["hand_written_edit"]["right"]
    assert own["n"] == edit["n"] == N
    for ref in (own, edit):  # both experiments quote the plain base this figure draws
        assert ref["value"]["base_plain_T3"] == y["base_plain"]
    cue_gain, rl_gain, first_gain = y["base_cue"] - y["base_plain"], y["final_plain"] - y["s100_plain"], y["s100_plain"] - y["base_cue"]
    assert cue_gain > rl_gain > first_gain > 0
    assert abs(DIFF["final_plain - s100_plain"]["value"] - 100 * rl_gain / N) < 0.01
    assert abs(DIFF["s100_plain - base_cue"]["value"] - 100 * first_gain / N) < 0.01
    hollow, filled = dict(mfc="white", mew=1.1), dict(mec="white", mew=0.6)
    x0, x1, lo, hi = -3.2, 4.7, 376, 472  # the axis is zoomed: the plain base is below it
    xo, edge = -0.45, lo + 7
    assert y["base_plain"] < lo < min(edit["value"]["edit"], *sum(cells.values(), [])) and max(sum(cells.values(), [])) < hi

    for cell, x, color in (("base_cue", 0, BASE), ("s100_plain", 1, RL), ("s100_cue", 1, RL), ("s400_plain", 2, RL),
                           ("final_plain", 3, RL)):  # the four samples of each mean
        a.plot([x + j for j in (-0.08, -0.027, 0.027, 0.08)], cells[cell], ls="", marker="o", ms=3.4, mew=0.7, color=color,
               mfc="white" if cell.endswith("cue") else None, alpha=0.45, zorder=3)
    a.plot([1, 2, 3], [y["s100_plain"], y["s400_plain"], y["final_plain"]], color=RL, lw=1.6, marker="o", ms=5.4, zorder=4, **filled)
    a.plot(0, y["base_cue"], ls="", marker="o", ms=5, color=BASE, zorder=5, **hollow)
    a.plot(1, y["s100_cue"], ls="", marker="o", ms=5, color=RL, zorder=5, **hollow)
    # two other ways to give the base its opening, both on the plain prompt: filled
    a.plot(xo, own["value"]["self_open"], ls="", marker="D", ms=4, color=BASE, zorder=6)
    a.plot(xo, edit["value"]["edit"], ls="", marker="s", ms=4, color=BASE, zorder=6)

    small = dict(fontsize=7.5, linespacing=1.1)
    quiet = dict(arrowstyle="-|>", color=MUTED, lw=0.6, shrinkA=0, shrinkB=0, mutation_scale=6)
    a.text(0.12, max(cells["base_cue"]) + 2, f"base + cue {number(y['base_cue'])}", color=BASE, ha="right", va="bottom", **small)
    a.text(xo - 0.16, own["value"]["self_open"], f"base, opening sampled\nfrom itself {own['value']['self_open']}", color=BASE,
           ha="right", va="center", **small)
    a.text(xo - 0.16, edit["value"]["edit"], f"base, hand-written\nedit {edit['value']['edit']}", color=BASE, ha="right",
           va="center", **small)
    a.plot(0, edge, ls="", marker="o", ms=4.4, color=BASE, zorder=5, **filled)  # the plain base, pinned at the edge
    a.annotate("", (0, lo + 0.2), (0, edge - 1.6), arrowprops=dict(quiet, color=BASE))
    a.text(0.16, edge + 2.6, f"plain base {number(y['base_plain'])} (off scale)", color=BASE, ha="left", va="center", **small)
    a.text(0.16, edge - 2.4, f"the cue adds {number(cue_gain)}", color=MUTED, ha="left", va="center", **small)
    a.text(1, max(cells["s100_cue"]) + 1.5, f"+ cue {number(y['s100_cue'])}", color=RL, ha="center", va="bottom", **small)
    a.text(1.14, y["s100_plain"] - 1, number(y["s100_plain"]), color=RL, ha="left", va="top", **small)
    a.text(2.24, y["s400_plain"] - 1.5, number(y["s400_plain"]), color=RL, ha="left", va="top", **small)
    a.text(3, max(cells["final_plain"]) + 1.5, number(y["final_plain"]), color=RL, ha="center", va="bottom", **small)
    a.plot([0.44, 0.5, 0.5, 0.44], [y["base_cue"], y["base_cue"], y["s100_plain"], y["s100_plain"]], color=MUTED, lw=0.6)
    a.text(0.5, y["base_cue"] - 1.5, f"+{first_gain:.1f}", color=MUTED, ha="center", va="top", **small)
    a.annotate("", (3.42, y["final_plain"]), (3.42, y["s100_plain"]), arrowprops=quiet)
    a.text(3.52, (y["s100_plain"] + y["final_plain"]) / 2, f"steps 100\nto 2,800:\n+{number(rl_gain)}", color=MUTED, ha="left",
           va="center", **small)
    a.set_xlim(x0, x1)
    a.set_ylim(lo, hi)
    a.set_xticks(range(4))
    a.set_xticklabels(STAGES, color=INK)
    a.set_xlabel("RL step", x=(2 - x0) / (x1 - x0))
    a.set_yticks(range(390, 471, 20))
    a.spines["bottom"].set_bounds(0, 3)
    a.grid(axis="y", color=GRID, lw=0.5)
    a.set_axisbelow(True)
    title(a, "Right answers of 500 (MATH-500, T 1.0)")


def right_panel(b):
    """Per problem, in how many of the four samples it is right: all four, one to three, none."""
    bars = [("base_cue", "base\n+ cue", BASE), ("s100_plain", "100", RL), ("s400_plain", "400", RL), ("final_plain", "2,800", RL)]
    for x, (cell, _, color) in enumerate(bars):
        counts = NOISE[cell]["problems_by_right_count"]
        k = counts["value"]
        assert counts["n"] == N and len(k) == 5 and sum(k) == N, cell
        assert sum(i * c for i, c in enumerate(k)) == sum(samples(cell)), cell
        all4, some, none = k[4], sum(k[1:4]), k[0]
        b.bar(x, all4, width=0.66, color=color, lw=0)
        b.bar(x, some, bottom=all4, width=0.66, color=tint(color, 0.35), lw=0)
        b.bar(x, none, bottom=all4 + some, width=0.66, color=NONE, lw=0)
        b.text(x, all4 / 2, str(all4), color="white", fontsize=8, ha="center", va="center")
        b.text(x, all4 + some / 2, str(some), color=INK, fontsize=7.5, ha="center", va="center")
        b.text(x, N + 5, str(none), color=MUTED, fontsize=7.5, ha="center", va="bottom")
    for yy, text, color in ((all4 / 2, "all 4", INK), (all4 + some / 2, "1 to 3", INK), (N + 5, "none", MUTED)):
        b.text(3.42, yy, text, color=color, fontsize=7.5, ha="left", va="bottom" if text == "none" else "center")
    b.set_xlim(-0.5, 4.2)
    b.set_ylim(0, 545)
    b.set_xticks(range(4))
    b.set_xticklabels([label for _, label, _ in bars], color=INK, linespacing=1.0)
    b.set_xlabel("RL step", x=2 / 4.7)
    b.set_yticks([0, 250, 500])
    b.spines["left"].set_bounds(0, N)
    b.spines["bottom"].set_bounds(-0.33, 3.33)
    title(b, "Solved in all 4, some,\nor none of 4 samples")


fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.9), constrained_layout=True, gridspec_kw={"width_ratios": [1.5, 1]})
left_panel(axes[0])
right_panel(axes[1])
save(fig, "fig_curve")
