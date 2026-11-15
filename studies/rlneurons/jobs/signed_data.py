"""Builds data/signed/arms-v1.json for signed self-training (specs/SPEC_signed1.md) from the stored 4 samples per MATH-500 problem
(attempt 0) of the cued base, job abaybektursun-1114-153825-208b.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.jobs.signed_data --answers runs/abaybektursun-1114-153825-208b/answers.jsonl

Per problem, each sample gets a return r and the advantage a = r - mean(r over the problem's 4 samples). A problem whose 4
returns are equal gives no example.
  P (pseudo)  r = 1 for a finished sample in the plurality group (distill_data.plurality: largest group of agreeing answers, at
              least 2 members, no tie), else 0. Problems without a plurality give no example. No answer key.
  G (gold)    r = the sample's v3 score against the key. The ceiling: what the same update does with the true reward.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

from studies.rlneurons.jobs import distill_data as D

STUDY = pathlib.Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True)
    a = ap.parse_args()
    path = pathlib.Path(a.answers)
    by = {}
    for line in path.read_text().splitlines():
        r = json.loads(line)
        if r["attempt"] == 0:
            by.setdefault(r["problem_index"], []).append(r)
    arms, stats = {"P": [], "G": []}, {"P": {}, "G": {}}
    same = total = 0
    for i, rows in sorted(by.items()):
        rows.sort(key=lambda r: r["sample"])
        assert len(rows) == 4
        g = D.plurality(rows)
        ret = {"G": [r["score_v3"] for r in rows],
               "P": None if g is None else [int(D.finished(r) and any(r is x for x in g)) for r in rows]}
        for arm, rs in ret.items():
            if rs is None or len(set(rs)) == 1:
                continue
            mean = sum(rs) / 4
            arms[arm] += [{"problem_index": i, "sample": r["sample"], "return": x, "advantage": x - mean, "n_new": r["n_new"],
                           "cap_hit": r["cap_hit"], "text_sha256": hashlib.sha256(r["text"].encode()).hexdigest()} for r, x in zip(rows, rs)]
        if ret["P"] is not None and len(set(ret["P"])) > 1:
            same += sum(p == q for p, q in zip(ret["P"], ret["G"]))
            total += 4
    for arm, ex in arms.items():
        stats[arm] = {"problems": len(ex) // 4, "samples": len(ex), "positive": sum(e["return"] for e in ex),
                      "cap_hits": sum(e["cap_hit"] for e in ex), "target_tokens": sum(e["n_new"] for e in ex)}
    stats["P_return_equals_key_score"] = [same, total]
    out = {"source": {"job": path.parent.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}, "stats": stats, "arms": arms}
    (STUDY / "data" / "signed" / "arms-v1.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
