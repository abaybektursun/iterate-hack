# /// script
# dependencies = ["numpy", "math-verify==0.9.0"]
# ///
"""Build data.json for the vote-machine prototype: for every stored four-sample run of studies/rlneurons, the four samples
of every problem (extracted answer, right or wrong, cap hit) and the group of agreeing answers each sample falls in.

    uv run studies/sitelab/prototypes/vote-machine/build.py

The groups are recomputed with the team's vote rule (analysis/day1_vote.vote, grader v3 agreement) and every count is
checked against the stored readout of the run: each sample's right answers, the vote's right answers problem by problem,
the ties, the samples without an answer, the histogram of the winner's votes, and (hard328) the mean over the six pairs
of samples in results/mixvote. The build fails when one differs.
"""
import itertools, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from studies.rlneurons.analysis.day1_vote import vote  # noqa: E402

R = ROOT / "studies/rlneurons/results"
D = ROOT / "studies/rlneurons/data"
SETS = {
    "hard328": {"name": "328 harder problems", "problems": "rln3/hard.json", "runs": [
        ("base", "Base + cue", "day1_3/hard328_base_cue_s4r2-01", "1 base", "2 base"),
        ("rl", "RL", "day1_3/hard328_rl_plain_s4r2-01", "1 rl", "2 rl"),
        ("think", "Think-SFT + cue", "thinkvote/hard328_sft1_cue_s4-01", "1 think", "2 think"),
        ("edit", "Base + 1.5 x edit + cue", "day1_3/hard328_top8x1.5_cue_s4-01", None, None)]},
    "math500": {"name": "MATH-500", "problems": "rln4/math500.json", "runs": [
        ("base", "Base + cue", "day1_3/math500_base_cue-01", None, None),
        ("rl", "RL", "day1_3/math500_rl-01", None, None),
        ("think", "Think-SFT + cue", "thinkvote/math500_sft1_cue_s4-01", None, None)]},
}
MIX = json.loads((R / "mixvote/hard328-01/readout.json").read_text())["rows"]


def short(s, n):
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


def run(folder, idx, mix1, mix2):
    ro = json.loads((R / folder / "readout.json").read_text())
    assert ro["samples"] == 4 and ro["problem_indices"] == idx, folder
    by = {}
    for line in open(R / folder / "rows.jsonl"):
        r = json.loads(line)
        if r["attempt"] == 0:
            assert (r["problem_index"], r["sample"]) not in by
            by[(r["problem_index"], r["sample"])] = r
    assert len(by) == 4 * len(idx), (folder, len(by))
    cells, votes, pair_right = [], [], [0] * 6
    for i in idx:
        rows = [by[(i, s)] for s in range(4)]
        v = vote(rows)
        votes.append(v)
        g = [-1] * 4
        for n, members in enumerate(v["groups"]):
            for m in members:
                g[m] = n
        cells.append({"a": [None if r["extracted_v3"] is None else short(r["extracted_v3"], 44) for r in rows],
                      "g": g, "r": "".join(str(r["score_v3"]) for r in rows),
                      "c": "".join(str(int(r["cap_hit"])) for r in rows), "t": [r["n_new"] for r in rows]})
        # the page recounts the vote over the first k samples from the groups: check that this equals the rule on those rows
        for k in (1, 2, 3):
            vk = vote(rows[:k])
            assert [[m for m in grp if m < k] for grp in v["groups"] if grp[0] < k] == vk["groups"], (folder, i, k)
        if mix2:
            for n, pair in enumerate(itertools.combinations(range(4), 2)):
                pair_right[n] += vote([rows[s] for s in pair])["score"]
    st, each = ro["vote_stats"], ro["each_sample"]["single_right"]
    assert [v["score"] for v in votes] == ro["per_problem"]["vote"], folder
    assert sum(v["score"] for v in votes) == ro["rows"]["vote"]["right"], folder
    assert [sum(int(c["r"][s]) for c in cells) for s in range(4)] == each, folder
    assert each[0] == ro["rows"]["single"]["right"], folder
    assert sum(v["tie"] for v in votes) == st["ties_for_first"], folder
    assert sum(v["winner"] is None for v in votes) == st["no_answer_in_any_sample"], folder
    assert sum(a is None for c in cells for a in c["a"]) == st["samples_without_answer"], folder
    assert {str(k): sum(v["votes"] == k for v in votes) for k in range(5)} == st["votes_of_winner_hist"], folder
    if mix1:
        assert MIX[mix1]["right_mean"] == sum(each) / 4, (folder, mix1)
        assert abs(MIX[mix2]["right_mean"] - sum(pair_right) / 6) < 1e-9, (folder, mix2, pair_right)
    return cells, {"each": each, "vote": ro["rows"]["vote"]["right"], "ties": st["ties_for_first"],
                   "blank": st["samples_without_answer"], "pass4": ro["rows"]["pass_at_k"]["right"],
                   "pairs_mean": MIX[mix2]["right_mean"] if mix2 else None}


out = {"rule": "plurality over the samples; a sample with no extracted answer casts no vote; ties go to the answer of the "
               "earliest sample (studies/rlneurons/analysis/day1_vote.py)", "sets": {}}
for key, s in SETS.items():
    idx = None
    models = []
    for mk, name, folder, m1, m2 in s["runs"]:
        idx = idx or json.loads((R / folder / "readout.json").read_text())["problem_indices"]
        cells, stored = run(folder, idx, m1, m2)
        models.append({"k": mk, "name": name, "src": "studies/rlneurons/results/" + folder, "stored": stored, "cells": cells})
    probs = {p["index"]: p for p in json.loads((D / s["problems"]).read_text())}
    golds = {json.loads(line)["problem_index"]: json.loads(line)["gold"] for line in open(R / s["runs"][0][2] / "rows.jsonl")}
    for i in idx:
        assert probs[i]["answer"] == golds[i], (key, i)
    out["sets"][key] = {"name": s["name"], "n": len(idx), "models": models,
                        "problems": [{"i": i, "id": probs[i]["unique_id"].replace(".json", ""), "q": short(probs[i]["problem"], 640),
                                      "gold": short(probs[i]["answer"], 60)} for i in idx]}
    assert len(idx) == {"hard328": 328, "math500": 500}[key]

text = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
assert len(text.encode()) < 1_000_000, len(text.encode())
(HERE / "data.json").write_text(text)
print("data.json", len(text.encode()), "bytes;", {k: [(m["k"], m["stored"]["each"], m["stored"]["vote"]) for m in v["models"]] for k, v in out["sets"].items()})
