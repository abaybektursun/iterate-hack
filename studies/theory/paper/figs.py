"""Figures of the paper, drawn from facts.json, predictions.jsonl and calibration.json (NOTES.md defines every term).
Run: uv run --no-project --with matplotlib --with numpy python studies/theory/paper/figs.py
-> fig_truth.pdf, fig_rounds.pdf, fig_duel.pdf next to this file."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

HERE = Path(__file__).parent
F = json.loads((HERE / "facts.json").read_text())
CAL = json.loads((HERE / "calibration.json").read_text())["sets"]["rounds_3_7_both_readers_filed_intervals"]
ROWS = [json.loads(line) for line in (HERE / "predictions.jsonl").read_text().splitlines()]
ROWS = [r for r in ROWS if "reader_intervals" in r["flags"]]  # rounds 3-7: theory and both readers filed intervals
THEORY, R1, R2, RIVAL, MUTED, INK, GRID = "#C2410C", "#2563EB", "#60A5FA", "#0D9488", "#6B7280", "#1F2937", "#E5E7EB"
Z90, CLIP = 1.645, 6  # a 90 % interval is +-1.645 sd (the engine's sd = width / 3.29); the x axis ends at 6 sd
# Stored references of selfopen-01, right answers of 500 (not in facts.json). Source:
# studies/theory/results/experiments/selfopen-01/metrics.json, references_stored.plain_T3 / .cue_T1 (right_of_500).
PLAIN_BASE, PREFILLED_CUE = 224, 410
for font in sorted((HERE / "fonts").glob("texgyrepagella-*.otf")):  # the body face of the paper (GUST font licence)
    font_manager.fontManager.addfont(font)
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["TeX Gyre Pagella"], "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "xtick.major.size": 3, "ytick.major.size": 3, "pdf.fonttype": 42,
})


def title(ax, text):
    ax.set_title(text, loc="left", fontsize=9, color=INK, pad=6)


def count(fact):
    """The count behind a fraction of facts.json."""
    return round(fact["value"] * fact["n"])


def swarm(xs, dx, step, limit):
    """y offsets that keep dots apart: each dot, in order of x, takes the free offset nearest the row's centre."""
    ys, placed = np.zeros(len(xs)), []
    offsets = [0] + [s * k * step for k in range(1, int(limit / step) + 1) for s in (1, -1)]
    for i in np.argsort(xs, kind="stable"):
        near = [(x, y) for x, y in placed if abs(x - xs[i]) < dx]
        free = [o for o in offsets if all((x - xs[i]) ** 2 / dx ** 2 + (y - o) ** 2 / step ** 2 >= 1 for x, y in near)]
        ys[i] = free[0] if free else offsets[len(near) % len(offsets)]
        placed.append((xs[i], ys[i]))
    return ys


def truth_figure():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.9), constrained_layout=True, gridspec_kw={"width_ratios": [1.5, 1]})
    head = F["headline_rounds_3_7"]
    n = len(ROWS)
    a.axvspan(-Z90, Z90, color=GRID, lw=0, alpha=0.7, zorder=0)
    a.axvline(0, color="white", lw=0.8, zorder=0)
    who = (("t", "Theories", THEORY, "coverage_theory"), ("r1", "No-theory\nreader 1", R1, "coverage_reader_1"),
           ("r2", "No-theory\nreader 2", R2, "coverage_reader_2"))
    for row, (key, name, color, fact) in enumerate(who):
        y0 = 2 - row
        z = np.array([r[f"z_{key}"] for r in ROWS])
        inside = np.array([r[f"{key}_inside"] for r in ROWS])
        assert head[fact]["n"] == n and count(head[fact]) == inside.sum(), (key, inside.sum())
        x = np.clip(z, -CLIP, CLIP)
        y = y0 + swarm(x, 0.2, 0.052, 0.42)
        colors = np.where(inside, "#9CA3AF", color)  # by the filed interval, which can be asymmetric
        clipped = np.abs(z) > CLIP
        a.scatter(x[~clipped], y[~clipped], s=7, c=colors[~clipped], alpha=0.65, lw=0, zorder=2)
        for side, marker in ((-1, "<"), (1, ">")):
            at = clipped & (np.sign(z) == side)
            a.scatter(x[at], y[at], s=14, c=colors[at], marker=marker, lw=0, zorder=3, clip_on=False)
        a.text(CLIP, y0 + 0.3, f"{inside.sum()} of {n} inside ({100 * inside.sum() / n:.0f} %)", color=INK, fontsize=7.5,
               ha="right", va="bottom")
    a.set_yticks([2, 1, 0])
    a.set_yticklabels([w[1] for w in who], color=INK, linespacing=1.05)
    a.text(0, 2.74, "90 % interval", color=MUTED, fontsize=7, ha="center", va="top")
    a.tick_params(axis="y", length=0)
    a.spines["left"].set_visible(False)
    a.set_ylim(-0.5, 2.76)
    a.set_xlim(-CLIP - 0.15, CLIP + 0.15)
    a.set_xticks(range(-6, 7, 2))
    a.set_xticklabels(["−6", "−4", "−2", "0", "2", "4", "6"])
    a.set_xlabel("miss, in standard deviations of the forecast")
    a.text(-CLIP, -0.47, f"triangle: clipped at {CLIP}", color=MUTED, fontsize=7, ha="left", va="bottom")
    title(a, "Where the truth fell")

    assert CAL["n"] == n
    levels = CAL["levels"]
    nominal = [lv["nominal"] for lv in levels]
    cover = {k: [lv[k]["scaled_interval"] for lv in levels] for k in ("t", "r1", "r2")}
    assert round(cover["t"][nominal.index(0.9)] * n) == count(head["coverage_theory"])
    b.plot([0, 1], [0, 1], color=MUTED, lw=0.7, ls=(0, (4, 3)), zorder=1)
    b.fill_between(nominal, [lv["t"]["ci95_cluster"][0] for lv in levels], [lv["t"]["ci95_cluster"][1] for lv in levels],
                   color=THEORY, alpha=0.13, lw=0, zorder=1)
    b.plot(nominal, cover["r2"], color=R2, lw=1.1, zorder=2)
    b.plot(nominal, cover["r1"], color=R1, lw=1.1, zorder=3)
    b.plot(nominal, cover["t"], color=THEORY, lw=1.6, marker="o", ms=2.8, mec="white", mew=0.5, zorder=4)
    b.annotate("theories", (nominal[6], cover["t"][6]), textcoords="offset points", xytext=(3, -12), color=THEORY,
               fontsize=8, ha="left")
    b.annotate("readers 1, 2", (nominal[5], max(cover["r1"][5], cover["r2"][5])), textcoords="offset points",
               xytext=(-5, 9), color=R1, fontsize=8, ha="right")
    b.text(0.33, 0.37, "calibrated", color=MUTED, fontsize=7, rotation=45, rotation_mode="anchor", ha="center", va="bottom")
    b.set_xlim(0, 1)
    b.set_ylim(0, 1)
    b.set_aspect("equal")
    b.set_xticks([0, 0.5, 0.9])
    b.set_yticks([0, 0.5, 0.9])
    b.set_xlabel("nominal level of the interval")
    b.set_ylabel("share of intervals that held")
    b.grid(color=GRID, lw=0.5)
    b.set_axisbelow(True)
    title(b, "Calibration")
    fig.savefig(HERE / "fig_truth.pdf")


def rounds_figure():
    per, sens = F["per_round"], F["sensitivity"]
    units = [("3", per["3"]), ("4", per["4"]), ("5", per["5"]), ("6\nother\ntheories", sens["round_6_without_account"]),
             ("6\nthe\nbudget", sens["r6_account_alone"]), ("7", per["7"])]
    ns = [u["coverage_theory"]["n"] for _, u in units]
    assert sum(ns) == len(ROWS) == F["headline_rounds_3_7"]["coverage_theory"]["n"]
    assert ns[3] + ns[4] == per["6"]["coverage_theory"]["n"]
    theory = [u["coverage_theory"]["value"] for _, u in units]
    readers = [(u["coverage_reader_1"]["value"] + u["coverage_reader_2"]["value"]) / 2 for _, u in units]
    account = [r["theory"] == "r6-account" for r in ROWS]
    picks = [[r for r, acc in zip(ROWS, account) if r["round"] == rd and (acc if only else not acc)]
             for rd, only in ((3, False), (4, False), (5, False), (6, False), (6, True), (7, False))]
    assert [len(p) for p in picks] == ns
    gain = [sum(r["gain"] for r in p) for p in picks]  # unrounded sums, so the labels round once
    assert all(abs(g - u["gain_total"]["value"]) < 0.01 for g, (_, u) in zip(gain, units)), gain
    assert abs(sum(gain) - F["headline_rounds_3_7"]["gain_total"]["value"]) < 0.01
    xs = np.arange(len(units))
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.5), constrained_layout=True)
    for ax in (a, b):
        ax.set_xticks(xs)
        ax.set_xticklabels([name for name, _ in units], color=INK, fontsize=7.5, linespacing=1.05)
        ax.tick_params(axis="x", length=0)
        ax.set_xlim(-0.6, len(units) - 0.4)
        ax.grid(axis="y", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        ax.set_xlabel("round")

    a.axhline(0.9, color=MUTED, lw=0.7, ls=(0, (4, 3)), zorder=1)
    a.text(len(units) - 0.42, 0.91, "nominal 0.90", color=MUTED, fontsize=7, ha="right", va="bottom")
    a.vlines(xs, theory, readers, color=MUTED, lw=0.8, zorder=2)
    a.scatter(xs, readers, s=22, color=R1, edgecolor="white", lw=0.6, zorder=3)
    a.scatter(xs, theory, s=22, color=THEORY, edgecolor="white", lw=0.6, zorder=4)
    a.annotate("readers\n(mean of 2)", (3, readers[3]), textcoords="offset points", xytext=(6, 0), color=R1,
               fontsize=7.5, va="center", linespacing=1.05)
    a.annotate("theories", (3, theory[3]), textcoords="offset points", xytext=(6, 0), color=THEORY, fontsize=7.5, va="center")
    for x, n in zip(xs, ns):
        a.text(x, 0.215, f"n = {n}", color=MUTED, fontsize=7, ha="center", va="bottom")
    a.set_ylim(0.2, 1.03)
    a.set_yticks([0.3, 0.5, 0.7, 0.9])
    a.set_ylabel("share of intervals that held")
    title(a, "Coverage of the 90 % intervals")

    b.bar(xs, gain, width=0.6, color=THEORY, lw=0, zorder=2)  # the sign shows the direction
    b.axhline(0, color=MUTED, lw=0.6, zorder=3)
    for x, g in zip(xs, gain):
        b.annotate(f"{g:+.1f}".replace("-", "−"), (x, g), textcoords="offset points", xytext=(0, 3 if g > 0 else -3),
                   ha="center", va="bottom" if g > 0 else "top", fontsize=7.5, color=INK)
    b.set_ylim(min(gain) - 8, max(gain) + 8)
    b.set_ylabel("log gain over the readers (nats)")
    title(b, "Log gain of the theories")
    fig.savefig(HERE / "fig_rounds.pdf")


def duel_figure():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.4), constrained_layout=True)
    so = F["selfopen_01"]["value"]
    measured, (m_low, m_high) = so["measured"], so["measured_interval"]
    a.axvspan(m_low, m_high, color=INK, alpha=0.08, lw=0, zorder=0)
    a.axvline(measured, color=INK, lw=1, zorder=1)
    a.text(measured - 16, 2.5, f"measured {measured} (prefilled cue {PREFILLED_CUE})", color=INK, fontsize=8, ha="right",
           va="center")
    a.axvline(PLAIN_BASE, color=MUTED, lw=0.8, ls=(0, (4, 3)), zorder=1)
    a.text(PLAIN_BASE + 4, 0.3, f"plain base {PLAIN_BASE}", color=MUTED, fontsize=7.5, ha="left", va="bottom")
    for y, name, color, (value, low, high) in ((1.7, "theory", THEORY, so["theory_forecast"]),
                                                (0.8, "rival", RIVAL, so["rival_forecast"])):
        a.plot([low, high], [y, y], color=color, lw=1.6, solid_capstyle="butt", zorder=2)
        a.scatter([value], [y], s=30, color=color, edgecolor="white", lw=0.8, zorder=3)
        a.text(low - 4, y, f"{name} {value}", color=color, fontsize=8, ha="right", va="center")
    a.set_ylim(0.2, 2.8)
    a.set_xlim(200, 432)
    a.set_yticks([])
    a.spines["left"].set_visible(False)
    a.set_xlabel(f"right answers of {so['n']} (bars: 90 % intervals)")
    title(a, "The one GPU experiment")

    duels = [d for d in F["duels"]["rows"]["value"] if d["rescore_of"] is None]  # a re-scored duel is drawn once
    assert len(duels) == F["duels"]["n_distinct"]["value"]
    duels.sort(key=lambda d: d["gain_all_tests"])
    ys = np.arange(len(duels))
    gains = [d["gain_all_tests"] for d in duels]
    b.barh(ys, gains, height=0.62, color=[THEORY if g > 0 else RIVAL for g in gains], lw=0, zorder=2)
    b.axvline(0, color=MUTED, lw=0.6, zorder=3)
    lim = max(abs(g) for g in gains) * 1.08
    b.set_xlim(-lim, lim)
    b.set_ylim(-0.6, len(duels) + 0.5)
    b.set_yticks([])
    b.spines["left"].set_visible(False)
    b.text(-lim, len(duels) - 0.2, "rival ahead", color=RIVAL, fontsize=7.5, ha="left", va="center")
    b.text(lim, len(duels) - 0.2, "theory ahead", color=THEORY, fontsize=7.5, ha="right", va="center")
    b.text(lim, -0.45, f"{len(duels)} contests", color=MUTED, fontsize=7, ha="right", va="bottom")
    b.set_xlabel("theory minus rival, nats over each contest's tests")
    title(b, "Theory against rival")
    fig.savefig(HERE / "fig_duel.pdf")


truth_figure()
rounds_figure()
duel_figure()
