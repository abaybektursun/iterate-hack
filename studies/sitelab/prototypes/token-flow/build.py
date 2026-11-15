"""Build data.json for the token-flow prototype from committed per-problem rows of studies/rlneurons.

  python3 studies/sitelab/prototypes/token-flow/build.py

Every answer keeps its stored token count (n_new), score (score_v3), cap hit and rule-A loop flag. The totals are
checked against the stored readouts; a mismatch stops the build.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
RL = os.path.join(HERE, "..", "..", "..", "rlneurons")
R = lambda p: os.path.join(RL, "results", p)
rows = lambda p: [json.loads(l) for l in open(R(p))]

hard = {x["index"]: x for x in json.load(open(os.path.join(RL, "data", "rln3", "hard.json")))}

FOUR = [  # key, label, run folder, board result, model key of that result's score line
    ("base_cue", "Base + cue", "day1_3/hard328_base_cue_s4r2-01", "result-5c961a"),
    ("rl", "RL-Zero-Math", "day1_3/hard328_rl_plain_s4r2-01", "result-5c961a"),
    ("sft", "Think-SFT + cue", "thinkvote/hard328_sft1_cue_s4-01", "result-818c20"),
    ("edit", "1.5x edit + cue", "day1_3/hard328_top8x1.5_cue_s4-01", "result-95a4dc"),
]
CAP32 = {"rl": "rl_plain", "sft": "sft_cue"}

idx = None
sets = []
for key, label, folder, result in FOUR:
    rr = sorted((r for r in rows(folder + "/rows.jsonl") if r["attempt"] == 0), key=lambda r: (r["problem_index"], r["sample"]))
    pi = sorted({r["problem_index"] for r in rr})
    idx = idx or pi
    assert pi == idx and len(rr) == 4 * len(idx) == 1312, key
    ro = json.load(open(R(folder + "/readout.json")))
    s0 = sum(r["score_v3"] for r in rr if r["sample"] == 0)
    assert s0 == ro["rows"]["single"]["right"], (key, s0)
    assert all(r["cap_hit"] == (r["finish_reason"] == "length") for r in rr)
    sets.append({
        "key": key, "label": label, "cap": 16384, "per": 4, "path": "studies/rlneurons/results/" + folder + "/rows.jsonl",
        "result": result, "sample0_right": s0,
        "tok": [r["n_new"] for r in rr], "ok": [r["score_v3"] for r in rr],
        "cap_hit": [int(r["cap_hit"]) for r in rr], "loop": [int(r["loop_A"]) for r in rr],
        "ans": [(r["extracted_v3"] or "")[:40] for r in rr],
    })

ro = json.load(open(R("cap32/readout.json")))["cells"]
for key, cell in CAP32.items():
    by = {r["problem_index"]: r for r in rows("cap32/rows-01/%s.jsonl" % cell)}
    assert sorted(by) == idx
    rr = [by[i] for i in idx]
    c = ro[cell]
    assert sum(r["score_v3"] for r in rr) == c["right_at_32768"]
    assert sum(r["score_v3"] for r in rr if r["n_new"] <= 16384) == c["right_at_16384_same_answers"]
    assert sum(r["n_new"] > 16384 for r in rr) == c["answers_longer_than_16384"]
    assert sum(r["cap_hit"] for r in rr) == c["cap_hits_at_32768"]
    assert all(hard[r["problem_index"]]["unique_id"] == r["unique_id"] for r in rr)
    label = next(s["label"] for s in sets if s["key"] == key)
    sets.append({
        "key": key + "_cap32", "label": label, "cap": 32768, "per": 1,
        "path": "studies/rlneurons/results/cap32/rows-01/%s.jsonl" % cell, "result": "result-c8b994",
        "tok": [r["n_new"] for r in rr], "ok": [r["score_v3"] for r in rr],
        "cap_hit": [int(r["cap_hit"]) for r in rr], "ans": [(r["extracted_v3"] or "")[:40] for r in rr],
    })

problems = [{"i": i, "id": hard[i]["unique_id"], "text": hard[i]["problem"][:420], "gold": str(hard[i]["answer"])[:40]} for i in idx]
out = os.path.join(HERE, "data.json")
json.dump({"problems": problems, "sets": sets}, open(out, "w"), separators=(",", ":"))
print(out, os.path.getsize(out), "bytes")
for s in sets:
    n = len(s["tok"])
    print(s["key"], n, "right", sum(s["ok"]), "cap", sum(s["cap_hit"]), "loops", sum(s.get("loop", [])))
