"""cleanneurons Part I figures (specs/SPEC1.md): one PNG per claim from the output directory of jobs/describe_neurons.py.
Laptop only (numpy and matplotlib, no model), from the repository root:

    uv run --no-project --with numpy --with matplotlib python -m studies.cleanneurons.analysis.describe_report runs/<job id> [--to <results folder>]

Reads onset_trace.json, dose.json, neurons.json and metrics.json. Writes into --to (default: the run directory):
  onset_trace.png   item 4: activation of the selected and of the reference neurons at each offset from the loop onset (solid) and
                    at the same offsets around the middle of each stored answer (dashed, the matched control). Left: mean over
                    neurons of |z|; right: of z; z = (mean a over rows - the neuron's mean on normal text) / its sd on normal text.
                    Thin lines per offset, thick lines an 11-token moving average.
  dose.png          item 5: share of the half B rows that loop against the write factor, with Wilson 95 % intervals.
  base_vs_rl.png    item 6: distribution over neurons of the base-RL cosine of the gate, up and down vectors and of the gain
                    (mean |a| in RL / in base on the same text), selected against reference.
  summary.json      the numbers behind the three figures and the job's controls.
"""
from __future__ import annotations

import argparse
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from studies.rlneurons.lib.n13_score import wilson

COLOR = {"selected": "#c0392b", "reference": "#34495e"}
SMOOTH = 11


def smooth(y):
    k = np.ones(SMOOTH)
    return np.convolve(y, k, mode="same") / np.convolve(np.ones(len(y)), k, mode="same")


def fig_onset(o, path):
    x, sets, rows = np.array(o["offsets"]), o["sets"], len(o["rows"])
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharex=True)
    for ax, key, label in ((axes[0], "mean_abs_z", "mean |z| over neurons (sd units)"), (axes[1], "mean_z", "mean z over neurons (sd units)")):
        for s in ("selected", "reference"):
            for kind, style in (("loop", "-"), ("normal", "--")):
                y, have = np.array(sets[s][kind][key]), np.array(sets[s][kind]["events_per_offset"]) > 0
                if kind == "loop":
                    ax.plot(x[have], y[have], color=COLOR[s], lw=0.5, alpha=0.35)
                ax.plot(x[have], smooth(y)[have], color=COLOR[s], lw=1.8, ls=style,
                        label=f"{s}, " + (f"loop onset ({rows} rows)" if kind == "loop" else f"middle of a stored answer ({sets[s][kind]['events']})"))
        ax.axvline(0, color="k", lw=0.8)
        ax.axvline(o["median_period"], color="k", lw=0.8, ls=":")
        ax.set_xlabel("offset from the loop onset (tokens)")
        ax.set_ylabel(label)
    axes[0].legend(fontsize=8, frameon=False)
    n = sets["selected"]["normal"]["events"]
    fig.suptitle(f"Activation around the loop onset: {rows} looped rows, {sets['selected']['neurons']} selected and "
                 f"{sets['reference']['neurons']} reference neurons; control: {n} stored answers\n"
                 f"z = (mean activation over rows - the neuron's mean on normal text) / its sd on normal text. Offset 0: first token of the "
                 f"first cycle; dotted: the median period ({o['median_period']} tokens), where the repeat starts", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_dose(d, path):
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    one = next(c for c in d["summary"] if c["name"] == "selected_x1")
    out = []
    for s, shift in (("selected", -0.012), ("reference", 0.012)):
        pts = sorted([c for c in d["summary"] if c["set"] == s and c["name"] != "selected_x1_repeat"] + ([one] if s == "reference" else []),
                     key=lambda c: c["factor"])
        f, rate = np.array([c["factor"] for c in pts]), np.array([100 * c["loops"] / c["n"] for c in pts])
        ci = np.array([wilson(c["loops"], c["n"]) for c in pts])
        ax.errorbar(f + shift, rate, yerr=[rate - ci[:, 0], ci[:, 1] - rate], color=COLOR[s], marker="o", lw=1.5, capsize=3,
                    label=f"{s} neurons" + (" (factor 1 = no change, shared)" if s == "reference" else ""))
        out += [{"set": s, "factor": c["factor"], "loops": c["loops"], "n": c["n"], "loop_rate_percent": round(100 * c["loops"] / c["n"], 1),
                 "wilson95_percent": [round(v, 1) for v in wilson(c["loops"], c["n"])], "stopped": c["stopped"]} for c in pts if c["set"] == s]
    ax.set_xlabel("write factor (the set's activations are multiplied by it)")
    ax.set_ylabel("rows that loop (% of the half B rows; bars: Wilson 95 %)")
    ax.set_ylim(-3, 103)
    ax.legend(fontsize=8, frameon=False)
    ax.set_title(f"Loop rate against the write factor: {one['n']} half B rows, {d['config']['steps']} tokens\nfrom "
                 f"{d['config']['restart_before_onset']} tokens before the onset, T {d['config']['temperature']}", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return out


def fig_rl(neurons, path):
    keys = (("cos_gate", "cosine base-RL, gate vector"), ("cos_up", "cosine base-RL, up vector"), ("cos_down", "cosine base-RL, down vector"),
            ("gain", "gain: mean |a| in RL / in base (same text)"))
    fig, axes = plt.subplots(1, 4, figsize=(17, 4.2))
    out, count = {}, {}
    for ax, (k, label) in zip(axes, keys):
        for s in ("selected", "reference"):
            v = np.sort([u["rl"][k] for u in neurons if u["set"] == s])
            count[s] = len(v)
            ax.step(v, (np.arange(len(v)) + 1) / len(v), where="post", color=COLOR[s], lw=1.6, label=f"{s} (n = {len(v)})")
            out.setdefault(s, {})[k] = {q: float(np.quantile(v, p)) for q, p in (("q10", 0.1), ("q25", 0.25), ("median", 0.5), ("q75", 0.75), ("q90", 0.9))}
        ax.axvline(1, color="k", lw=0.6, ls=":")
        if k == "gain":
            ax.set_xscale("log")
        ax.set_xlabel(label)
        ax.set_ylabel("share of neurons at or below")
    axes[0].legend(fontsize=8, frameon=False)
    fig.suptitle(f"Base against RL on the same neurons: {count['selected']} selected and {count['reference']} reference neurons "
                 "(dotted: no change)", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    for s in out:
        out[s]["act_corr_median"] = float(np.median([u["rl"]["act_corr"] for u in neurons if u["set"] == s]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", help="output directory of jobs/describe_neurons.py")
    ap.add_argument("--to", default=None, help="where the figures and summary.json go (default: the run directory)")
    a = ap.parse_args()
    run = pathlib.Path(a.run)
    to = pathlib.Path(a.to or a.run)
    to.mkdir(parents=True, exist_ok=True)
    m, o, d, n = (json.loads((run / f).read_text()) for f in ("metrics.json", "onset_trace.json", "dose.json", "neurons.json"))
    assert m["status"] == "done", f"{run}/metrics.json: status {m['status']}"
    fig_onset(o, to / "onset_trace.png")
    x = np.array(o["offsets"])
    spans = {"before": (x >= -200) & (x < -50), "just_before": (x >= -50) & (x < 0), "after_onset": (x >= 0) & (x < o["median_period"]),
             "after_first_repeat": x >= o["median_period"]}
    onset = {s: {kind: {w: round(float(np.mean(np.array(o["sets"][s][kind]["mean_abs_z"])[sel])), 4) for w, sel in spans.items()}
                 for kind in ("loop", "normal")} for s in ("selected", "reference")}
    summary = {"run": str(run), "commit": m["commit"], "job_id": m["job_id"], "edit": m["edit"], "counts": m["counts"], "controls": m["controls"],
               "onset_trace": {"rows": len(o["rows"]), "median_period": o["median_period"],
                               "what": "mean |z| over neurons and offsets in each span; spans by the median period; 'normal' = middle of stored answers",
                               "mean_abs_z": onset, "per_row_windows_from_the_job": o["window_summary"]},
               "dose": {"rows": fig_dose(d, to / "dose.png"), "controls": d["controls"]},
               "base_vs_rl": fig_rl(n["neurons"], to / "base_vs_rl.png")}
    (to / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: summary[k] for k in ("onset_trace", "dose", "base_vs_rl")}, indent=1))


if __name__ == "__main__":
    main()
