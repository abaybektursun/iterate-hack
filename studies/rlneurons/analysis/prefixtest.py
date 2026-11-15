"""Generation test from the prefix before each located wrong step: readout (specs/SPEC_prefixtest.md).

    uv run --no-project --with numpy python -m studies.rlneurons.analysis.prefixtest <arm>=<job>,<job>,... [<arm>=...]

Run from the repository root; the first arm is the control. Inputs (not committed): runs/<job-id>/ of jobs/prefix_cell.py shards
(`uv run tools/gpu.py get <job-id>`). Writes results/wrongstep/prefix-01/ (metrics.json, per_prefix.json, examples.json, run.json).
Per prefix: the share of its continuations scored right (grader v3). Differences: paired bootstrap over prefixes, 5,000 resamples, seed 0.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

import numpy as np

RUNS = pathlib.Path("runs")
OUT = pathlib.Path(__file__).resolve().parents[1] / "results" / "wrongstep" / "prefix-01"


def main():
    arms = {x.split("=")[0]: x.split("=")[1].split(",") for x in sys.argv[1:]}
    rows, cfg = {}, {}
    for arm, jobs in arms.items():
        rows[arm] = []
        for j in jobs:
            m = json.loads((RUNS / j / "metrics.json").read_text())
            assert m["status"] == "done", (j, m["status"])
            cfg.setdefault(arm, {k: m["config"][k] for k in ("model", "alpha", "k", "cap", "seed", "arm")})
            assert cfg[arm] == {k: m["config"][k] for k in cfg[arm]}, j
            rows[arm] += [json.loads(line) for line in open(RUNS / j / "answers.jsonl")]
        assert len({(r["item"], r["k"]) for r in rows[arm]}) == len(rows[arm]), arm
    items = sorted({r["item"] for r in rows[next(iter(arms))]})
    label = {r["item"]: r["label"] for r in rows[next(iter(arms))]}
    per = {arm: {it: [r["score_v3"] for r in rs if r["item"] == it] for it in items} for arm, rs in rows.items()}
    for arm in arms:
        assert all(len(per[arm][it]) == cfg[arm]["k"] for it in items), arm
    rng = np.random.default_rng(0)
    bs = rng.integers(0, len(items), (5000, len(items)))

    def ci(v):
        b = v[bs].mean(1) * 100
        return [round(float(np.percentile(b, 2.5)), 1), round(float(np.percentile(b, 97.5)), 1)]

    share = {arm: np.array([np.mean(per[arm][it]) for it in items]) for arm in arms}
    ctrl = next(iter(arms))
    res = {"prefixes": len(items), "labels": dict(collections.Counter(label.values())), "config": cfg, "arms": {}}
    for arm in arms:
        rs = rows[arm]
        row = {"jobs": arms[arm], "continuations": len(rs), "right": int(sum(r["score_v3"] for r in rs)), "right_percent": round(float(share[arm].mean() * 100), 1),
               "right_percent_ci95": ci(share[arm]), "cap_hits": int(sum(r["cap_hit"] for r in rs)), "tokens_per_continuation": round(float(np.mean([r["n_new"] for r in rs]))),
               "right_and_ended": int(sum(r["score_v3"] and not r["cap_hit"] for r in rs)),
               "prefixes_with_any_right": int((share[arm] > 0).sum()),
               "by_label_right_percent": {l: round(float(np.mean([share[arm][i] for i, it in enumerate(items) if label[it] == l]) * 100), 1) for l in sorted(set(label.values()))}}
        if arm != ctrl:
            d = share[arm] - share[ctrl]
            row["minus_control_points"] = {"value": round(float(d.mean() * 100), 1), "ci95": ci(d)}
            row["minus_control_by_label"] = {l: round(float(np.mean([d[i] for i, it in enumerate(items) if label[it] == l]) * 100), 1) for l in sorted(set(label.values()))}
        res["arms"][arm] = row
    ex = {}
    for arm in arms:
        ex[arm] = [{k: r[k] for k in ("item", "label", "k", "n_prefix_tokens", "n_new", "finish_reason", "extracted_v3", "gold", "score_v3")} | {"text_tail": r["text"][-600:]}
                   for want in (1, 0) for r in rows[arm] if r["score_v3"] == want][:1] + [
                  {k: r[k] for k in ("item", "label", "k", "n_prefix_tokens", "n_new", "finish_reason", "extracted_v3", "gold", "score_v3")} | {"text_tail": r["text"][-600:]}
                  for r in rows[arm] if r["score_v3"] == 0][:1]
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(res, indent=1) + "\n")
    (OUT / "per_prefix.json").write_text(json.dumps({arm: {it: per[arm][it] for it in items} for arm in arms} | {"label": label}, indent=1) + "\n")
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    (OUT / "run.json").write_text(json.dumps({"command": "python -m studies.rlneurons.analysis.prefixtest " + " ".join(sys.argv[1:]), "arms": arms}, indent=1) + "\n")
    print(json.dumps(res["arms"], indent=1))


if __name__ == "__main__":
    main()
