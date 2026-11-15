"""Figures of the paper, drawn from facts.json (every number there names its artifact).
Run: uv run --with matplotlib python studies/rlneurons/paper/figs.py   -> fig_dial.pdf, fig_plane.pdf next to this file."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

HERE = Path(__file__).parent
F = json.loads((HERE / "facts.json").read_text())
N = 328
DIAL, RL, SFT, CTRL, INK, MUTED, GRID = "#C2410C", "#2563EB", "#0D9488", "#6B7280", "#1F2937", "#6B7280", "#E5E7EB"
for font in sorted((HERE / "fonts").glob("texgyrepagella-*.otf")):  # the body face of the paper (GUST font licence)
    font_manager.fontManager.addfont(font)
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["TeX Gyre Pagella"], "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "xtick.major.size": 3, "ytick.major.size": 3, "pdf.fonttype": 42,
})


def cell(c):
    """(right, cap hits, % finished, % right among finished) of one cell of facts.json; means when several samples."""
    right, cap = c["right"]["value"], c["cap_hits"]["value"]
    fin = c["right_among_finished"]
    return right, cap, 100 * (N - cap) / N, fin["percent"] if "percent" in fin else 100 * fin["value"] / fin["n"]


top = {float(k.split()[0]): cell(v) for k, v in F["dial"]["top8"].items()}
rnd = {float(k): cell(v) for k, v in F["dial"]["random_rank8"].items() if k != "not_run_at"}
rl = cell(F["dial"]["references"]["rl_plain_single"])
rank = F["rank_sweep_size_1"]
rl_cue = cell(F["dial"]["references"]["rl_cue_single_other_seed"])
rl_minus_top = cell(rank["rl_minus_its_top8 (bulk)"])
rl_minus_rnd = cell(rank["rl_minus_random_rank8 (rbulk, control of bulk)"])
tr = F["transplant"]
transplant = {0: cell(tr["a=0 (Think-SFT, cue, 4 samples)"]), **{a: cell(tr[f"a={a}"]) for a in (1, 2, 3, 4)}}
tr_noise = cell(next(v for k, v in tr.items() if k.startswith("noise_control")))


def dial_figure():
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.45), constrained_layout=True)
    sizes, rsizes = sorted(top), sorted(rnd)
    for ax, i, title, ref_label in ((axes[0], 1, "Answers cut at the token cap", "RL"), (axes[1], 0, "Right answers", "RL")):
        ax.axhline(rl[i], color=RL, lw=0.9, ls=(0, (4, 3)), zorder=1)
        ax.plot(rsizes, [rnd[s][i] for s in rsizes], color=CTRL, lw=1.2, ls=(0, (1, 1.5)), marker="o", ms=3.5,
                mfc="white", mew=1, zorder=2)
        ax.plot(sizes, [top[s][i] for s in sizes], color=DIAL, lw=1.8, marker="o", ms=4.5, mec="white", mew=0.8, zorder=3)
        ax.axvline(0, color=GRID, lw=0.8, zorder=0)
        ax.set_title(title, loc="left", fontsize=9, color=INK, pad=6)
        ax.set_xticks(sizes)
        ax.set_xticklabels(["−1", "0\nbase", "0.5", "1\nRL's size", "1.5", "2", "3"])
        ax.set_xlabel("size of the edit")
        ax.grid(axis="y", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
    a, b = axes
    a.set_ylim(0, 105)
    a.set_ylabel(f"of {N} problems")
    a.text(-1.05, rl[1] + 3, f"RL model: {rl[1]}", color=INK, fontsize=8, ha="left", va="bottom")
    a.text(3.05, rnd[3][1] + 5, "random 8 directions", color=INK, fontsize=8, ha="right", va="bottom")
    a.text(1.72, 36, "top 8 directions", color=INK, fontsize=8, ha="left", va="bottom")
    for s, xy in ((-1, (9, 2)), (0, (9, 3)), (0.5, (-2, -11)), (1, (9, 3)), (1.5, (9, 3)), (2, (0, 6)), (3, (0, 6))):
        a.annotate(str(top[s][1]), (s, top[s][1]), textcoords="offset points", xytext=xy, ha="center",
                   fontsize=7.5, color=INK)
    b.set_ylim(100, 225)
    b.text(-1.05, rl[0] + 3, f"RL model: {rl[0]}", color=INK, fontsize=8, ha="left", va="bottom")
    b.text(0.42, 153, "random 8 directions", color=INK, fontsize=8, ha="left", va="top")
    for s, dx, dy in ((-1, 12, -2), (0, -9, 4), (0.5, 11, -5), (1, -9, 4), (1.5, 0, 7), (2, 11, 2), (3, -12, -2)):
        b.annotate(str(top[s][0]), (s, top[s][0]), textcoords="offset points", xytext=(dx, dy), ha="center",
                   fontsize=7.5, color=INK)
    fig.savefig(HERE / "fig_dial.pdf")


def plane_figure():
    fig, ax = plt.subplots(figsize=(6.3, 3.5), constrained_layout=True)
    x0, x1, y0, y1 = 66, 100, 48, 93
    xs = np.linspace(x0, x1, 200)
    for right in (140, 170, 200, 230, 260):  # lines of equal score: finished % x precision % = right / N
        ys = 100 * 100 * right / N / xs
        keep = (ys >= y0) & (ys <= y1)
        ax.plot(xs[keep], ys[keep], color="#D1D5DB", lw=0.7, zorder=0)
        if ys[-1] >= y0:
            ax.text(x1 + 0.3, ys[-1], f"{right} right", color=MUTED, fontsize=7, va="center", ha="left")
        else:
            ax.text(100 * 100 * right / N / y0 + 0.4, y0 + 0.6, f"{right} right", color=MUTED, fontsize=7, va="bottom", ha="left")

    # the random control: four sizes, one cluster
    ax.scatter([rnd[s][2] for s in rnd], [rnd[s][3] for s in rnd], s=16, facecolor="white", edgecolor=CTRL, lw=1, zorder=2)
    ax.text(75.2, 58.6, "random 8 directions", color=INK, fontsize=7.5, ha="left", va="top")

    # the dial on the base
    path = [-1, 0, 0.5, 1, 1.5, 2]
    ax.plot([top[s][2] for s in path], [top[s][3] for s in path], color=DIAL, lw=1.6, zorder=3)
    ax.scatter([top[s][2] for s in path], [top[s][3] for s in path], s=26, color=DIAL, edgecolor="white", lw=0.8, zorder=4)
    for s, (dx, dy, ha) in {-1: (0, -10, "center"), 0: (3, 6, "center"), 0.5: (0, -10, "center"), 1: (0, 7, "center"),
                            1.5: (-3, 8, "center"), 2: (0, -10, "center")}.items():
        label = {0: "0", -1: "−1"}.get(s, f"{s:g}")
        ax.annotate(label, (top[s][2], top[s][3]), textcoords="offset points", xytext=(dx, dy), ha=ha, fontsize=7.5,
                    color=INK)
    ax.text(90.5, 53.3, "base + size × top 8 directions\n(size 0 = base)", color=INK, fontsize=7.5, ha="center", va="center", linespacing=1.1,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))

    # RL, and RL with the 8 directions taken out
    ax.annotate("", xy=(rl_minus_top[2], rl_minus_top[3]), xytext=(rl_cue[2], rl_cue[3]),
                arrowprops=dict(arrowstyle="-|>", color=RL, lw=1.1, shrinkA=7, shrinkB=4, mutation_scale=8), zorder=3)
    ax.scatter([rl_cue[2]], [rl_cue[3]], s=75, facecolor="none", edgecolor=RL, lw=1.4, zorder=5)
    ax.scatter([rl_minus_top[2]], [rl_minus_top[3]], s=30, facecolor="white", edgecolor=RL, lw=1.3, zorder=5)
    ax.scatter([rl_minus_rnd[2]], [rl_minus_rnd[3]], s=14, facecolor="white", edgecolor=RL, lw=0.9, zorder=5)
    ax.annotate("RL model", (rl_cue[2], rl_cue[3]), textcoords="offset points", xytext=(9, -3), fontsize=8, color=INK)
    ax.annotate("RL − its top 8", (rl_minus_top[2], rl_minus_top[3]), textcoords="offset points", xytext=(-6, 5),
                ha="right", fontsize=7.5, color=INK)
    ax.annotate("RL − random 8", (rl_minus_rnd[2], rl_minus_rnd[3]), textcoords="offset points", xytext=(-2, -11),
                ha="center", fontsize=7, color=INK)

    # the transplant onto the imitation model
    aa = sorted(transplant)
    ax.plot([transplant[a][2] for a in aa], [transplant[a][3] for a in aa], color=SFT, lw=1.6, zorder=3)
    ax.scatter([transplant[a][2] for a in aa], [transplant[a][3] for a in aa], s=26, color=SFT, edgecolor="white", lw=0.8,
               zorder=4)
    ax.scatter([tr_noise[2]], [tr_noise[3]], s=16, facecolor="white", edgecolor=CTRL, lw=1, zorder=4)
    ax.annotate("Think-SFT + noise", (tr_noise[2], tr_noise[3]), textcoords="offset points", xytext=(6, 3), ha="left", fontsize=7,
                color=INK)
    for a in aa:
        label = "Think-SFT (a = 0)" if a == 0 else str(a)
        ax.annotate(label, (transplant[a][2], transplant[a][3]), textcoords="offset points",
                    xytext=(0, -11) if a == 0 else (5, 4), ha="center" if a == 0 else "left", fontsize=7.5, color=INK)
    ax.text(84.6, 86.3, "Think-SFT + a × (RL − base)", color=INK, fontsize=7.5, ha="left",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))

    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_xlabel("finishing: answers finished within the token cap (%)")
    ax.set_ylabel("precision: right among finished answers (%)")
    fig.savefig(HERE / "fig_plane.pdf")


dial_figure()
plane_figure()
