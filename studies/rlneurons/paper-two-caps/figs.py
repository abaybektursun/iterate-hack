"""The figure of the paper, drawn from facts.json only (NOTES.md defines every quantity).
Run: uv run --no-project --with matplotlib --with numpy python studies/rlneurons/paper-two-caps/figs.py [png folder]
-> fig_caps.pdf next to this file; with a folder argument also a 200 dpi PNG there."""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).parent
F = json.loads((HERE / "facts.json").read_text())
BASE, RL, MUTED, INK, GRID = "#C2410C", "#2563EB", "#6B7280", "#1F2937", "#E5E7EB"
SFT = "#0F766E"  # teal: apart from the orange and the blue in lightness and hue, also for colour-blind readers
for font in sorted((HERE / "fonts").glob("texgyrepagella-*.otf")):  # the body face of the paper (GUST font licence)
    font_manager.fontManager.addfont(font)
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["TeX Gyre Pagella"], "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "xtick.major.size": 3, "ytick.major.size": 3, "pdf.fonttype": 42, "hatch.linewidth": 0.6,
})
ROWS = {row["comparison"]: row for row in F["figure"]}
CAP32 = F["cap32_run"]
SMALL = dict(fontsize=7.5, linespacing=1.1)


def title(ax, text):
    ax.set_title(text, loc="left", fontsize=9, color=INK, pad=6)


def save(fig, name):
    fig.savefig(HERE / f"{name}.pdf")
    if len(sys.argv) > 1:
        fig.savefig(Path(sys.argv[1]) / f"{name}.png", dpi=200)


def tint(color, share):
    """The colour mixed with white: share 1 is the colour itself."""
    rgb = matplotlib.colors.to_rgb(color)
    return tuple(1 - share * (1 - c) for c in rgb)


def gain(cell):
    """(points, low, high) of a gain on hard328."""
    assert cell["n"] == 328, cell
    lo, hi = cell["ci95"]
    assert lo <= cell["value"] <= hi
    return cell["value"], lo, hi


def interval(ax, x, cell, color, **marker):
    v, lo, hi = cell
    ax.plot([x, x], [lo, hi], color=color, lw=0.9, solid_capstyle="butt", zorder=4)
    ax.plot(x, v, ls="", color=color, zorder=5, **marker)


def one(v):
    """One decimal, halves rounded up as in the text (9.45 -> 9.5; the float 9.45 is just below 9.45)."""
    return round(v + 1e-9, 1)


def signed(v):
    return f"{one(v):+.1f}".replace("-", "−")


def left_panel(a):
    """Gain on hard328 at the two token limits, one line per comparison."""
    rl, sft, m2 = ROWS["hard328 RL - base+cue"], ROWS["hard328 Think-SFT - RL"], ROWS["hard328 M(2) - Think-SFT"]
    assert all(isinstance(r[k], dict) for r in (rl, sft, m2) for k in ("cap32_run_gain_32768", "cap32_run_change"))
    lines = [  # (row, colour, marker, x dodge, label, label y)
        (rl, RL, "o", -0.09, "RL over the base", 12.6),
        (m2, INK, "D", 0.0, "weight sum over Think-SFT", 3.4),
        (sft, SFT, "s", 0.09, "Think-SFT over RL", 9.0),
    ]
    got = []
    for row, color, marker, dx, label, ly in lines:
        left, right, change = (gain(row[k]) for k in ("cap32_run_gain_16384", "cap32_run_gain_32768", "cap32_run_change"))
        got.append([one(c) for c in left[:1] + right[:1] + change])
        mk = dict(marker=marker, ms=4.4 if marker == "D" else 4.6, mec="white", mew=0.6)
        a.plot([dx, 1 + dx], [left[0], right[0]], color=color, lw=1.4, zorder=3)
        interval(a, dx, left, color, **mk)
        interval(a, 1 + dx, right, color, **mk)
        a.text(1.18, ly, f"{label} {signed(right[0])}", color=color, ha="left", va="bottom", **SMALL)
        ci = f"[{one(change[1]):.1f}, {one(change[2]):.1f}]".replace("-", "−")
        a.text(1.18, ly - 0.15, f"change {signed(change[0])} {ci}", color=MUTED, ha="left", va="top", **SMALL)
    assert got == [[12.5, 11.9, -0.6, -2.1, 0.9], [6.7, 3.4, -3.4, -6.4, -0.3], [4.3, 10.7, 6.4, 3.7, 9.5]], got

    a.axhline(0, color=MUTED, lw=0.6, zorder=0)
    a.set_xlim(-0.3, 2.35)
    a.set_ylim(-3, 21.5)
    a.set_xticks([0, 1])
    a.set_xticklabels(["limit\n16,384 tokens", "limit\n32,768 tokens"], color=INK, fontsize=7.5, linespacing=1.0)
    a.spines["bottom"].set_bounds(0, 1)
    a.set_yticks([0, 5, 10, 15])
    a.set_ylabel("gain (percentage points)")
    a.grid(axis="y", color=GRID, lw=0.5)
    a.set_axisbelow(True)
    title(a, "Gain on the 328 competition problems\nat two token limits")
    a.text(0.02, 1.0, "one sample per model at each limit, each pair on one seed;\nthe same answers scored at both limits",
           transform=a.transAxes, color=MUTED, ha="left", va="top", **SMALL)


def right_panel(b):
    """What happens to the answers cut off at 16,384 when 16,384 more tokens are allowed."""
    models = [("base + cue", "base", BASE), ("RL plain", "RL", RL), ("M(2) (seed 3,010,000)", "weight sum", INK),
              ("Think-SFT + cue", "Think-SFT", SFT)]
    rows = []
    for key, label, color in models:
        m = CAP32["per_model"][key]
        cut, done, right = m["cut_off_at_16384"], m["of_them_finished_by_32768"], m["of_them_right_at_32768"]
        assert m["at_16384"]["cap_hits_per_sample"] == [cut] and m["at_32768"]["cap_hits_per_sample"] == [cut - done]
        rows.append((label, color, cut, right, done - right, cut - done))
    assert [r[2:] for r in rows] == [(64, 4, 59, 1), (20, 2, 18, 0), (56, 13, 43, 0), (93, 23, 68, 2)]
    for y, (label, color, cut, right, wrong, still) in enumerate(rows):
        left = 0
        for n, face, ec, hatch in [(right, color, color, None), (wrong, tint(color, 0.3), tint(color, 0.3), None),
                                   (still, "white", color, "//////")]:
            if n:
                b.barh(y, n, left=left, height=0.6, color=face, ec=ec, lw=0.6 if hatch else 0, hatch=hatch)
            if n >= 4:
                b.text(left + n / 2, y, str(n), color="white" if face == color else color, ha="center", va="center",
                       **SMALL)
            elif n:  # too narrow for its number: above the segment
                b.text(left + n / 2, y + 0.34, str(n), color=color, ha="center", va="bottom", **SMALL)
            left += n
        b.text(cut + 1.5, y, f"{cut} cut off" if y == 3 else str(cut), color=MUTED, ha="left", va="center", **SMALL)
    # names of the three parts, on the top bar
    _, color, cut, right, wrong, still = rows[3]
    b.text(right / 2, 3.62, "finish\nright", color=color, ha="center", va="bottom", **SMALL)
    b.text(right + wrong / 2, 3.62, "finish wrong", color=tint(color, 0.75), ha="center", va="bottom", **SMALL)
    b.text(cut + 3, 3.62, "still cut off\nat 32,768", color=MUTED, ha="left", va="bottom", **SMALL)
    b.set_yticks(range(4))
    b.set_yticklabels([r[0] for r in rows], color=INK, fontsize=7.5)
    b.tick_params(axis="y", length=0)
    b.spines["left"].set_visible(False)
    b.set_xlim(0, 118)
    b.set_ylim(-0.5, 4.3)
    b.set_xticks([0, 25, 50, 75, 100])
    b.spines["bottom"].set_bounds(0, 100)
    b.set_xlabel("answers cut off at 16,384 tokens (of 328)")
    title(b, "What 16,384 more tokens do\nwith a cut-off answer")


fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.9), constrained_layout=True, gridspec_kw={"width_ratios": [1.25, 1]})
left_panel(axes[0])
right_panel(axes[1])
save(fig, "fig_caps")
