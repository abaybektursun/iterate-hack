"""Readout of the planted-waste test: one table per arm and round, and the demo chart.

  uv run --with matplotlib python -m studies.metaharness.analysis.planted_readout

Reads results/planted/<arm>-<nn>/ and results/clean/<arm>-<nn>/ (analysis/planted_collect.py) and each review's
rubric.json (named and changed, from the judge; grader/rubric_v2.md). Writes results/planted/summary-<nn>/:
metrics.json, table.md and chart.png. removed and recurs are computed here from the windows' `present` flags.
"""
import json
import statistics
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
PLANTS = ["P1", "P2", "P3", "P4", "P5", "P6"]
ARMS = {"skill": "team-meta-review skill", "plain": "plain instruction"}


def load(experiment):
    runs = {}
    for folder in sorted((STUDY / "results" / experiment).glob("*-[0-9][0-9]")):
        if folder.name.startswith("summary"):
            continue
        metrics = json.loads((folder / "metrics.json").read_text())
        rubrics = {}
        for review in sorted(folder.glob("review*")):
            path = review / "rubric.json"
            rubrics[int(review.name[6:])] = json.loads(path.read_text()) if path.exists() else None
        runs[folder.name] = {"windows": metrics["windows"], "reviews": metrics["reviews"], "rubrics": rubrics}
    return runs


def run_rows(run):
    """Per position 0..n: the window's numbers; per round k >= 1 also what review k named, changed and removed."""
    rows, gone = [], set()
    windows = run["windows"]
    for position, w in enumerate(windows):
        present = [p for p in PLANTS if w["present"][p]]
        detail = w.get("answers_detail", {})
        row = {"position": position, "batch": w["batch"], "container_minutes": w["container_minutes"], "waste_share": w["waste_share"],
               "turnaround_minutes": w["turnaround_minutes"], "jobs": w["jobs"], "jobs_failed": w["jobs_failed"], "plants_present": present,
               "answers_exact": w["answers"]["equal_to_reference"], "answers_delivered": w["answers"]["delivered"],
               "answers_same_points": sum(bool(d["points_equal"]) for d in detail.values()),
               "max_end_shift_in_widths": max((d["max_end_shift_in_widths"] or 0 for d in detail.values()), default=None),
               "resamples": w.get("resamples"), "adapted": w.get("adapted"), "median_setup_s": w.get("median_setup_s"),
               "minutes_by_line": w.get("minutes_by_line")}
        if position:
            before = [p for p in PLANTS if windows[position - 1]["present"][p]]
            review = run["reviews"][position - 1]
            rubric = run["rubrics"].get(position)
            row["review"] = {"minutes": review["minutes"], "turns": review["turns"], "cost_usd": round(review["cost_usd"] or 0, 2),
                             "job_minutes": review["job_minutes"], "plants_present_before": before,
                             "removed": [p for p in before if p not in present],
                             "recurs": sorted(p for p in gone if p in present),
                             "named": [p for p in before if rubric and rubric["named"][p]["score"]] if rubric else None,
                             "changed": [p for p in before if rubric and rubric["changed"][p]["score"]] if rubric else None}
            gone |= set(row["review"]["removed"])
            gone -= set(present)
        rows.append(row)
    return rows


def summarize(runs):
    arms = {}
    for name, run in runs.items():
        arms.setdefault(name.rsplit("-", 1)[0], {})[name] = run_rows(run)
    return arms


def mean(values):
    return round(statistics.mean(values), 3) if values else None


def table(arms, title):
    lines = [f"### {title}", "",
             "| arm | after round | plants present (of 6), per run | container min per batch, per run | mean | share with no answer, per run | mean | answers exact (of 4) | named by the review | removed by the review | review USD, mean |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for arm, runs in arms.items():
        for position in range(max(len(rows) for rows in runs.values())):
            rows = [rows[position] for rows in runs.values() if len(rows) > position]
            reviews = [r["review"] for r in rows if "review" in r]
            named = "/".join("?" if r["named"] is None else "%d of %d" % (len(r["named"]), len(r["plants_present_before"])) for r in reviews) or "-"
            removed = "/".join("%d of %d" % (len(r["removed"]), len(r["plants_present_before"])) for r in reviews) or "-"
            cost = "%.2f" % statistics.mean(r["cost_usd"] for r in reviews) if reviews else "-"
            present = "/".join(str(len(r["plants_present"])) for r in rows)
            minutes = "/".join("%.1f" % r["container_minutes"] for r in rows)
            shares = "/".join("%.0f%%" % (100 * r["waste_share"]) for r in rows)
            exact = "/".join(str(r["answers_exact"]) for r in rows)
            lines.append("| %s | %d | %s | %s | %.1f | %s | %.0f%% | %s | %s | %s | %s |" % (
                arm, position, present, minutes, mean([r["container_minutes"] for r in rows]), shares,
                100 * mean([r["waste_share"] for r in rows]), exact, named, removed, cost))
    return "\n".join(lines) + "\n"


def chart(planted, clean, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, muted, grid, surface = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    colors = {"skill": "#2a78d6", "plain": "#eb6834"}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": grid, "axes.labelcolor": muted,
                         "xtick.color": muted, "ytick.color": muted, "text.color": ink})
    panels = [
        ("Found", "planted inefficiencies the review named,\nof those still present", lambda r: len(r["review"]["named"]) if r.get("review") and r["review"]["named"] is not None else None, (0, 6.6), "%.1f"),
        ("Still there", "planted inefficiencies present in the\nnext batch's job records, of 6", lambda r: len(r["plants_present"]), (0, 6.6), "%.1f"),
        ("Compute per batch", "container minutes for the same 4 answers,\nsame job class", lambda r: r["container_minutes"], (0, None), "%.1f"),
        ("Compute with no answer", "percent of container time that produced\nnone of the 4 answers", lambda r: 100 * r["waste_share"], (0, 100), "%.0f%%"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(15.5, 5.0), facecolor=surface)
    labels = ["before", "round 1", "round 2", "round 3"]
    handles = {}
    for ax, (title, unit, value, limits, fmt) in zip(axes, panels):
        ax.set_facecolor(surface)
        top, ends = 0, []
        for arm in ("skill", "plain"):
            per_position = {}
            for rows in planted[arm].values():
                xs = [r["position"] for r in rows if value(r) is not None]
                ys = [value(r) for r in rows if value(r) is not None]
                ax.plot(xs, ys, color=colors[arm], linewidth=1, alpha=0.35, marker="o", markersize=4.5, markeredgecolor=surface, markeredgewidth=1)
                for x, y in zip(xs, ys):
                    per_position.setdefault(x, []).append(y)
            xs = sorted(per_position)
            if not xs:
                continue
            means = [statistics.mean(per_position[x]) for x in xs]
            handles[arm], = ax.plot(xs, means, color=colors[arm], linewidth=2.2, marker="o", markersize=8, markeredgecolor=surface, markeredgewidth=2, zorder=3)
            ends.append([means[-1], xs[-1], means[-1]])
            top = max(top, max(max(v) for v in per_position.values()))
        ax.set_ylim(limits[0], limits[1] if limits[1] else top * 1.15)
        gap = 0.075 * (ax.get_ylim()[1] - ax.get_ylim()[0])
        ends.sort()
        for i in range(1, len(ends)):  # keep the two end labels apart
            if ends[i][0] - ends[i - 1][0] < gap:
                middle = (ends[i][0] + ends[i - 1][0]) / 2
                ends[i - 1][0], ends[i][0] = middle - gap / 2, middle + gap / 2
        for y_text, x, y in ends:
            ax.text(x + 0.16, y_text, fmt % y, color=ink, fontsize=10.5, fontweight="bold", va="center")
        if title.startswith("Compute"):
            floors = [value(rows[0]) for runs in clean.values() for rows in runs.values()]
            if floors:
                ax.axhspan(min(floors), max(floors), color=muted, alpha=0.13, linewidth=0)
                ax.text(-0.2, max(floors), " same work with nothing planted", color=muted, fontsize=8.5, va="bottom")
        ax.set_title(title, loc="left", fontsize=12.5, fontweight="bold", pad=34)
        ax.text(0, 1.035, unit, transform=ax.transAxes, color=muted, fontsize=9, va="bottom", linespacing=1.25)
        ax.set_xticks(range(4), labels)
        ax.set_xlim(-0.3, 3.75)
        ax.grid(axis="y", color=grid, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.tick_params(length=0)
    axes[0].set_xticks([1, 2, 3], labels[1:])
    axes[0].set_xlim(0.7, 3.75)
    n = {arm: len(runs) for arm, runs in planted.items()}
    fig.legend([handles["skill"], handles["plain"]],
               [f"told to run the team-meta-review skill (mean of {n['skill']} runs)", f"same model, plain instruction, no skill (mean of {n['plain']} runs)"],
               loc="upper left", bbox_to_anchor=(0.04, 0.925), ncol=2, frameon=False, fontsize=10.5, columnspacing=3)
    fig.suptitle("Measured: six inefficiencies planted in a research batch, one fresh review per round, then the next batch is run",
                 x=0.045, y=0.975, ha="left", fontsize=13.5, fontweight="bold")
    fig.text(0.045, 0.02, "Thin lines are single runs. Real Modal CPU jobs and real review sessions (claude-opus-5-5), 2026-11-15. Every round is a new batch of the same "
             "size on the same job class;\nevery batch delivered its 4 answers with the reference point estimates. Source: studies/metaharness/results/planted/",
             color=muted, fontsize=8.5, linespacing=1.4)
    fig.tight_layout(rect=(0.03, 0.08, 0.985, 0.87), w_pad=3.0)
    fig.savefig(path, dpi=170, facecolor=surface)


if __name__ == "__main__":
    planted, clean = summarize(load("planted")), summarize(load("clean"))
    number = 1
    while (STUDY / "results" / "planted" / f"summary-{number:02d}").exists():
        number += 1
    out = STUDY / "results" / "planted" / f"summary-{number:02d}"
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(json.dumps({"planted": planted, "clean": clean}, indent=1) + "\n")
    text = table(planted, "Planted arenas (per run: values separated by /)") + "\n" + table(clean, "Clean arenas")
    (out / "table.md").write_text(text)
    (out / "run.json").write_text(json.dumps({"command": "uv run --with matplotlib python -m studies.metaharness.analysis.planted_readout",
                                              "inputs": "results/planted/*-NN, results/clean/*-NN"}, indent=1) + "\n")
    print(text)
    if "--no-chart" not in sys.argv:
        chart(planted, clean, out / "chart.png")
    print(out)
