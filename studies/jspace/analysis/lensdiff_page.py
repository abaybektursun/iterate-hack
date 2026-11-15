"""Builds the reading page of the lens-diff run: the numbers of metrics.json and windows of real answers with both models'
readouts, inlined into analysis/page_template.html.

    PYTHONPATH=. python3 -m studies.jspace.analysis.lensdiff_page runs/<job-id> --map <map run folder> \
        --result studies/jspace/results/lensdiff/full-01

Reads <result>/metrics.json and <result>/page_examples.json (the chosen examples: problem_index, position, title, note,
base_answer; each verified by reading the answer). Writes <result>/workspace-diff.html. In a window, the readout shown for a
written token is the one read right after that token (entry i + 1 of the job's arrays).
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np

from studies.jspace.analysis.lensdiff_analyze import HOLD, WRAP, load_rows

STUDY = pathlib.Path(__file__).resolve().parents[1]
MATH = STUDY.parent / "rlneurons" / "data" / "rln4" / "math500.json"
BEFORE, AFTER = 130, 45


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--map", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--layer", type=int, default=24)
    a = ap.parse_args()
    run, mp, res = pathlib.Path(a.run), pathlib.Path(a.map), pathlib.Path(a.result)
    m = json.loads((res / "metrics.json").read_text())
    spec = json.loads((res / "page_examples.json").read_text())
    vocab = json.loads((run / "vocab.json").read_text())
    index = json.loads((run / "index.json").read_text())
    math = json.loads(MATH.read_text())
    l, q, W = a.layer, index["qscale"], index["watch"]["tokens"]
    widx = [W.index(s) for s in (" Wait", " wait", " Hmm")]
    rows = load_rows(run, "T1", ["tok", "kind", f"top_base_{l}", f"top_rl_{l}", f"watch_base_{l}", f"watch_rl_{l}"])
    maprows = load_rows(mp, "T1", ["tok", "top1_base", "top1_rl"])

    key = f"T1_L{l}"
    b = m["b_presence"][key]
    pct = lambda x: round(100 * x, 2)
    fam = lambda f: {"base": pct(b[f]["rate_b"]), "rl": pct(b[f]["rate_a"]), "diff": pct(b[f]["diff"]), "ci": [pct(x) for x in b[f]["ci95"]]}
    words = lambda k, side, n: [{"t": x["token"], "base": pct(x["base"]), "rl": pct(x["rl"])} for x in m["a_vocab_diff"][k][side][:n]]
    d = m["d_lead"][key]
    wr = m["d_lead"]["T1_wait_rates"]
    g = m["c_by_group"][f"{key}_hold_on"]
    data = {
        "layer": l, "positions_t1": sum(m["n_pos"]["T1"].values()), "problems": 500,
        "hold": fam("hold_on"), "wrap": fam("wrap_up"), "families": m["families"],
        "words": {"rl_more_24": words(key, "rl_more", 14), "base_more_24": words(key, "base_more", 14),
                  "rl_more_16": words("T1_L16", "rl_more", 10)},
        "lead": {"events": d["events"], "rl": [pct(x) for x in d["rl_readout"]["rate_by_lag_0_to_32"]],
                 "base": [pct(x) for x in d["base_readout"]["rate_by_lag_0_to_32"]],
                 "far_rl": pct(d["rl_readout"]["rate_far_from_events"]), "far_base": pct(d["base_readout"]["rate_far_from_events"])},
        "said": {"written": pct(wr["written"]), "rl_top1": pct(wr["rl_next_token_top1"]), "held_rl": pct(b["tokens"][" Wait"]["rate_a"]),
                 "held_base": pct(b["tokens"][" Wait"]["rate_b"])},
        "groups": {k: {"diff": pct(g[k]["diff"]), "ci": [pct(x) for x in g[k]["ci95"]], "n": g[k]["problems"]} for k in ("both", "rl_only")},
        "groups_dd": {"diff": pct(g["rl_only_minus_both"]["diff_of_diffs"]), "ci": [pct(x) for x in g["rl_only_minus_both"]["ci95"]]},
        "predict": json.loads((res / "predict.json").read_text())["T1"],
        "hit": {k: m["checks"]["hit"]["by_layer"][str(l)]["base_T1"][k] for k in ("jlens", "logit", "shifted_window")},
        "job": m["job_id"], "commit": m["commit"][:7], "examples": [],
    }
    for e in spec:
        pi, pos = int(e["problem_index"]), int(e["position"])
        r, mr = rows[pi], maprows[pi]
        n = len(r["tok"])
        lo, hi = max(pos - 1 - BEFORE, 0), min(pos - 1 + AFTER, n - 2)
        gap = (r[f"watch_base_{l}"][:, widx].astype(np.float64) - r[f"watch_rl_{l}"][:, widx].astype(np.float64)).sum(1) / q
        toks = []
        for i in range(lo, hi + 1):                   # written token i, readout entry i + 1
            j = i + 1
            toks.append({"t": vocab[int(r["tok"][i])], "g": round(float(gap[j]), 1),
                         "b": [vocab[int(t)] for t in r[f"top_base_{l}"][j]], "r": [vocab[int(t)] for t in r[f"top_rl_{l}"][j]],
                         "bn": vocab[int(mr["top1_base"][j])], "rn": vocab[int(mr["top1_rl"][j])]})
        data["examples"].append({"problem_index": pi, "title": e["title"], "note": e["note"], "problem": math[pi]["problem"],
                                 "gold": math[pi]["answer"], "base_answer": e["base_answer"], "focus": pos - 1 - lo,
                                 "start": lo, "of": n, "tokens": toks})
    data["hold_words"], data["wrap_words"] = list(HOLD), list(WRAP)
    html = (STUDY / "analysis" / "page_template.html").read_text()
    assert html.count("/*DATA*/") == 1
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    (res / "workspace-diff.html").write_text(html.replace("/*DATA*/", payload))
    print(f"wrote {res}/workspace-diff.html ({len(payload) // 1024} KB of data, {len(data['examples'])} examples)")


if __name__ == "__main__":
    main()
