"""SPEC1 Part B, two records that replay.py does not write:

    uv run --with modal --with boto3 python -m studies.metaharness.analysis.replay_extra \
        --cancelled whole_b200=<job> --paired shard4_h100=<job>,<job>,<job>,<job> whole_h200=<job>

--cancelled: a job that was cancelled before it started. Writes results/replay/<name>-01/ with its queue minutes
(submit to cancel) from the Modal job record. It has no rows.
--paired A B: per problem_index, the v3 scores of two arms (runs/<job>/answers.jsonl). Writes results/replay/paired-01/
with the 2x2 counts and the exact two-sided sign test on the discordant pairs (McNemar).
Refuses an existing folder.
"""
import argparse
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import gpu  # noqa: E402

OUT = ROOT / "studies" / "metaharness" / "results" / "replay"


def scores(ids):
    rows = [json.loads(line) for i in ids.split(",") for line in (ROOT / "runs" / i / "answers.jsonl").read_text().splitlines()]
    return {r["problem_index"]: r["score_v3"] for r in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cancelled", required=True, help="name=job")
    ap.add_argument("--paired", nargs=2, required=True, help="name=job[,job...] twice")
    a = ap.parse_args()

    name, job_id = a.cancelled.split("=")
    r = gpu.load()[job_id]
    assert "cancel" in r and "start" not in r, f"{job_id} was not cancelled in the queue"
    folder = OUT / f"{name}-01"
    folder.mkdir(parents=True)
    (folder / "metrics.json").write_text(json.dumps({"arm": name, "state": "cancelled in the queue, never started", "class": r["job"]["class"],
                                                      "queue_min": (r["cancel"]["at"] - r["job"]["at"]) / 60, "n": 0}, indent=1))
    (folder / "run.json").write_text(json.dumps({"job_ids": [job_id], "commit": r["job"]["sha"], "command": r["job"]["cmd"]}, indent=1))

    (na, ia), (nb, ib) = (s.split("=") for s in a.paired)
    sa, sb = scores(ia), scores(ib)
    assert set(sa) == set(sb), "the two arms hold different problems"
    both = sum(sa[i] and sb[i] for i in sa)
    only_a = sum(sa[i] and not sb[i] for i in sa)
    only_b = sum(sb[i] and not sa[i] for i in sa)
    d = only_a + only_b
    p = min(1.0, 2 * sum(math.comb(d, k) for k in range(min(only_a, only_b) + 1)) / 2 ** d)
    folder = OUT / "paired-01"
    folder.mkdir(parents=True)
    out = {"a": na, "b": nb, "n": len(sa), "right_a": sum(sa.values()), "right_b": sum(sb.values()), "both_right": both,
           "only_a_right": only_a, "only_b_right": only_b, "neither": len(sa) - both - d, "sign_test_two_sided_p": p}
    (folder / "metrics.json").write_text(json.dumps(out, indent=1))
    (folder / "run.json").write_text(json.dumps({"command": " ".join(sys.argv), "job_ids": ia.split(",") + ib.split(",")}, indent=1))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
