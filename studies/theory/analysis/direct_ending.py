"""Direct test of run-03/f2-m04, "accuracy depends on how the answer ends" (specs/SPEC_direct_ending.md).

    uv run --no-project --with numpy python studies/theory/analysis/direct_ending.py --runs ../iterate-hack/runs

Counts finished answers with no code block (mode none, no cap hit) per code cell and the paired differences of the RL-Math
edit at 1.5x against the random rank-8 edit and the cued base, 90 % bootstrap over the 538 problems.
Writes studies/theory/results/direct/ending-01/.
"""
import argparse
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "studies" / "theory" / "results" / "direct" / "ending-01"
JOBS = {"base": "abaybektursun-1114-170304-c03c", "rand15": "abaybektursun-1115-101457-ef2c",
        "math15": "abaybektursun-1115-101508-33f0", "code1": "abaybektursun-1115-101423-4a7d",
        "code15": "abaybektursun-1115-101434-4511"}
B = 10000


def box_at_end(text):
    """True when \\boxed appears after the last ``` fence, or anywhere when the answer has no fence."""
    return "\\boxed" in text.split("```")[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    runs = pathlib.Path(ap.parse_args().runs)
    rows = {a: {r["uid"]: r for r in map(json.loads, open(runs / j / "answers.jsonl"))} for a, j in JOBS.items()}
    uids = sorted(rows["base"])
    for a in rows:
        assert sorted(rows[a]) == uids and len(uids) == 538, a
        assert all(rows[a][u]["seed"] == rows["base"][u]["seed"] for u in uids), a
    arr = {}
    for a in rows:
        rs = [rows[a][u] for u in uids]
        arr[a] = {"fnb": np.array([r["mode"] == "none" and not r["cap_hit"] for r in rs], int),
                  "cap": np.array([r["cap_hit"] for r in rs], int),
                  "noblock": np.array([r["mode"] == "none" for r in rs], int),
                  "passed": np.array([r["passed"] for r in rs], int),
                  "boxed": np.array(["\\boxed" in r["text"] for r in rs], int),
                  "box_at_end": np.array([box_at_end(r["text"]) for r in rs], int)}
    idx = np.random.default_rng(0).integers(0, len(uids), (B, len(uids)))

    def ci(x):
        s = x[idx].sum(1)
        return [int(x.sum()), [float(np.percentile(s, 5)), float(np.percentile(s, 95))]]

    out = {"spec": "studies/theory/specs/SPEC_direct_ending.md", "n_problems": len(uids), "jobs": JOBS,
           "count_and_90ci": {a: {k: ci(v) for k, v in arr[a].items()} for a in arr},
           "differences_fnb": {f"{a}-{b}": ci(arr[a]["fnb"] - arr[b]["fnb"])
                               for a, b in [("math15", "rand15"), ("math15", "base"), ("rand15", "base"),
                                            ("code1", "base"), ("code15", "base")]}}
    lo, hi = out["differences_fnb"]["math15-rand15"][1]
    out["verdict"] = "holds" if lo >= 8 else "refuted" if hi < 8 else "undecidable"
    lo, hi = out["differences_fnb"]["math15-base"][1]
    out["verdict_vs_base"] = "holds" if lo >= 8 else "refuted" if hi < 8 else "undecidable"
    out["boxed_rule"] = "refuted" if arr["math15"]["box_at_end"].sum() < 4 else "not refuted"
    m = rows["math15"]
    fnb_m = [u for u in uids if m[u]["mode"] == "none" and not m[u]["cap_hit"]]
    fnb_r = [u for u in uids if rows["rand15"][u]["mode"] == "none" and not rows["rand15"][u]["cap_hit"]]
    out["fnb_uids"] = {"math15": fnb_m, "rand15": fnb_r}
    out["read"] = [{"arm": a, "uid": u, "n_new": rows[a][u]["n_new"], "passed_base": rows["base"][u]["passed"],
                    "tail": rows[a][u]["text"][-600:]} for a, us in [("math15", fnb_m), ("rand15", fnb_r[:10 - len(fnb_m)])]
                   for u in us]
    keep = ("uid", "seed", "prompt", "text", "mode", "code", "passed", "exit", "n_new", "cap_hit")
    fail_block = next(u for u in uids if m[u]["mode"] == "block" and not m[u]["passed"] and not m[u]["cap_hit"])
    ex = [{"counted_as": "finished, no code block", **{k: m[fnb_m[0]][k] for k in keep}},
          {"counted_as": "finished with a code block, failed", **{k: m[fail_block][k] for k in keep}}]
    OUT.mkdir(parents=True, exist_ok=False)
    (OUT / "readout.json").write_text(json.dumps(out, indent=1))
    (OUT / "examples.json").write_text(json.dumps(ex, indent=1))
    print(json.dumps({k: out[k] for k in ("differences_fnb", "verdict", "verdict_vs_base", "boxed_rule")}, indent=1))
    for a in arr:
        print(a, {k: v[0] for k, v in out["count_and_90ci"][a].items()})


if __name__ == "__main__":
    main()
