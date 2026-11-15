"""Self-distillation training sets (specs/SELFDISTILL_2026-11-15.md), built on the laptop from the stored base + cue rows of
Day-1 #3 (job abaybektursun-1114-153825-208b, MATH-500, 4 samples per problem, T 1.0 / top-p 1.0). No model, no gold answer:
`load` keeps only KEEP, so no gold, score or parsed-gold field reaches the builder.

    uv run --no-project --with math-verify==0.9.0 python -m studies.rlneurons.jobs.distill_data \
        --answers runs/abaybektursun-1114-153825-208b/answers.jsonl --job abaybektursun-1114-153825-208b

Per problem, over attempt 0 of the four samples:
  plurality  answers grouped as in analysis/day1_vote.vote (a row joins the first group whose first member's norm_v3 answer
             agrees, rln4_lib.agree; a row with no extracted answer casts no vote). The plurality is the largest group if it has
             at least 2 members and no other group is as large; otherwise the problem has no plurality and is dropped.
  V (vote)   the shortest finished (finish_reason "stop", no cap hit) member of the plurality group; dropped if it has none.
  U (random) on V's problems, one finished sample drawn at random (random.Random(0), problems in index order).
  S (short)  on V's problems, the shortest finished sample regardless of its answer.
Ties in length go to the lower sample number.

Writes data/selfdistill/arms-v1.json (per arm: problem index, sample, tokens, extracted answer, sha256 of the text; no texts)
and --texts (default runs/selfdistill/arms-v1.jsonl: the same rows with the texts, for S3; not committed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random

from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
KEEP = ("problem_index", "sample", "attempt", "cap_hit", "finish_reason", "extracted_v3", "n_new", "text")


def load(path) -> dict:
    """{problem index: [attempt-0 rows in sample order]}, each row with the KEEP fields only."""
    by = {}
    for line in pathlib.Path(path).read_text().splitlines():
        r = json.loads(line)
        if r["attempt"] == 0:
            by.setdefault(r["problem_index"], []).append({k: r[k] for k in KEEP})
    for i, rows in by.items():
        rows.sort(key=lambda r: r["sample"])
        assert [r["sample"] for r in rows] == list(range(len(rows))), f"problem {i}: samples {[r['sample'] for r in rows]}"
    return by


def finished(r) -> bool:
    return r["finish_reason"] == "stop" and not r["cap_hit"]


def plurality(rows) -> list | None:
    """Rows of the plurality group, or None."""
    groups = []
    for r in rows:
        if r["extracted_v3"] is None:
            continue
        x = R.norm_v3(r["extracted_v3"])
        g = next((g for g in groups if R.agree(R.norm_v3(g[0]["extracted_v3"]), x)), None)
        if g is None:
            groups.append([r])
        else:
            g.append(r)
    sizes = sorted((len(g) for g in groups), reverse=True)
    if not sizes or sizes[0] < 2 or (len(sizes) > 1 and sizes[1] == sizes[0]):
        return None
    return max(groups, key=len)


def shortest(rows):
    return min(rows, key=lambda r: (r["n_new"], r["sample"]))


def build(by: dict) -> tuple:
    rng = random.Random(0)
    arms, why = {"V": [], "U": [], "S": []}, {"no_plurality": 0, "plurality_none_finished": 0}
    for i in sorted(by):
        rows = by[i]
        g = plurality(rows)
        if g is None:
            why["no_plurality"] += 1
            continue
        gf = [r for r in g if finished(r)]
        if not gf:
            why["plurality_none_finished"] += 1
            continue
        fin = [r for r in rows if finished(r)]
        arms["V"].append(shortest(gf))
        arms["U"].append(rng.choice(fin))
        arms["S"].append(shortest(fin))
    return arms, why


def entry(r) -> dict:
    return {"problem_index": r["problem_index"], "sample": r["sample"], "n_new": r["n_new"], "extracted_v3": r["extracted_v3"],
            "text_sha256": hashlib.sha256(r["text"].encode()).hexdigest()}


def stats(arms, by) -> dict:
    out = {}
    for k, rows in arms.items():
        n = [r["n_new"] for r in rows]
        out[k] = {"examples": len(rows), "mean_tokens": sum(n) / len(n), "max_tokens": max(n), "total_tokens": sum(n),
                  "starts_with_cue": sum(r["text"].startswith(" line!\n\nOkay") for r in rows)}
    same = lambda a, b: sum(x["sample"] == y["sample"] for x, y in zip(arms[a], arms[b]))
    out["same_sample"] = {"V_U": same("V", "U"), "V_S": same("V", "S"), "U_S": same("U", "S")}
    out["problems"] = len(by)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True)
    ap.add_argument("--job", required=True)
    ap.add_argument("--out", default=str(STUDY / "data" / "selfdistill" / "arms-v1.json"))
    ap.add_argument("--texts", default="runs/selfdistill/arms-v1.jsonl")
    a = ap.parse_args()
    out, texts = pathlib.Path(a.out), pathlib.Path(a.texts)
    assert not out.exists(), f"{out} exists: a changed input is a new file with a new version"
    by = load(a.answers)
    assert len(by) == 500 and all(len(v) == 4 for v in by.values()), "expected 500 problems with 4 samples each"
    arms, why = build(by)
    st = {**stats(arms, by), "dropped": why}
    res = {"source": {"job_id": a.job, "file": "answers.jsonl", "sha256": hashlib.sha256(pathlib.Path(a.answers).read_bytes()).hexdigest()},
           "rule": __doc__.split("Per problem,")[1].split("Writes")[0].strip(), "stats": st,
           "arms": {k: [entry(r) for r in v] for k, v in arms.items()}}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1) + "\n")
    texts.parent.mkdir(parents=True, exist_ok=True)
    texts.write_text("".join(json.dumps({"arm": k, **entry(r), "text": r["text"]}) + "\n" for k, v in arms.items() for r in v))
    print(json.dumps(st, indent=1))
    print(out, hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
