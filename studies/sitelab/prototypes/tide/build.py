"""Build data.json for the tide prototype: the 500 MATH-500 problems as stones on one difficulty order, and the right/wrong
vector of each of the 39 configurations of the axis study, from committed files of studies/rlneurons.

    python3 studies/sitelab/prototypes/tide/build.py

Definitions (the page states them and recomputes them; this file stores them so the page can check itself):
- solved share of a problem: the share of the 36 single-sample configurations that solve it. The stones stand in this order.
- height of a stone for configuration c: the share of the OTHER single-sample configurations that miss the problem (c is
  left out, so a configuration never sets the height of its own stones; the three vote configurations leave nothing out).
- level of c: the height that puts as many stones under water as c solves (the nearest count; ties go to the lower level).
- out of order: an island is a problem c solves whose stone stands above that level; a buoy is a problem c misses whose
  stone is under it.
Every total is checked against readout.json and the manifest; the build fails when one differs.
"""
import itertools, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUN = "studies/rlneurons/results/axis/math500-01/"
META = "studies/rlneurons/data/profile/math500_meta_v1.json"
TEXT = "studies/rlneurons/data/rln4/math500.json"
sys.path.insert(0, str(ROOT))
from tools import finding_one_difficulty_axis as F  # the plain names and groups of the 36 single-sample configurations

load = lambda p: json.loads((ROOT / p).read_text())
vec, readout, manifest, meta, text = load(RUN + "vectors.json"), load(RUN + "readout.json"), load(RUN + "manifest.json"), load(META), load(TEXT)

N = 500
assert vec["set"] == "math500" and vec["grader"] == "v3" and vec["problem_indices"] == list(range(N))
assert vec["unique_ids"] == meta["unique_ids"] == [t["unique_id"] for t in text], "problem order differs between files"
arms = vec["arms"]
VOTES = {"base_vote4": "Base + cue, vote over 4 samples", "base_tie_short": "Base + cue, vote over 4, ties to the shortest answer",
         "rl_vote4": "RL, vote over 4 samples"}
single = [k for k in arms if k not in VOTES]
assert single == list(F.NAMES) and len(single) == 36 and len(arms) == readout["floor"]["arms"] == 39
for k, a in arms.items():
    right = sum(x for x in a if x is not None)
    assert len(a) == N and right == readout["right"][k] == manifest["arms"][k]["right"], (k, right)

s = [sum(arms[k][i] for k in single if arms[k][i] is not None) for i in range(N)]
n = [sum(1 for k in single if arms[k][i] is not None) for i in range(N)]
assert sum(1 for i in range(N) if s[i] == 0 and not any(arms[k][i] for k in VOTES)) == readout["floor"]["no_arm_solves"]
rank = sorted(range(N), key=lambda i: (-s[i] / n[i], meta["level"][i], i))  # easiest first; ties: lower level, then index


def tide(k):
    a = arms[k]
    out = k in single
    h = []
    for i in range(N):
        if out and a[i] is not None:
            h.append(1 - (s[i] - a[i]) / (n[i] - 1))
        else:
            h.append(1 - s[i] / n[i])
    total = sum(x for x in a if x is not None)
    best = None
    for t in [-1.0] + sorted(set(h)):
        under = sum(1 for x in h if x <= t + 1e-9)
        if best is None or abs(under - total) < abs(best[1] - total):
            best = (t, under)
    t, under = best
    islands = sum(1 for i in range(N) if a[i] == 1 and h[i] > t + 1e-9)
    buoys = sum(1 for i in range(N) if a[i] == 0 and h[i] <= t + 1e-9)
    ran_under = sum(1 for i in range(N) if a[i] is not None and h[i] <= t + 1e-9)
    assert total - islands + buoys == ran_under, k
    return {"total": total, "under": under, "islands": islands, "buoys": buoys}


def resample(family):
    """Mean number of problems on which two samples of one configuration differ, over its 6 pairs of 4 samples."""
    ks = [f"{family}_s{j}" for j in range(4)]
    d = [sum(1 for i in range(N) if arms[a][i] != arms[b][i]) for a, b in itertools.combinations(ks, 2)]
    return round(sum(d) / len(d), 1)


RES = {f: resample(f) for f in ("base_cue", "rl_plain")}
out_arms = []
for k in arms:
    fam = manifest["arms"][k]["family"]
    out_arms.append({"k": k, "name": F.NAMES.get(k) or VOTES[k], "group": F.GROUP(k) if k in single else "Votes",
                     "single": k in single, "r": "".join("-" if x is None else str(x) for x in arms[k]), **tide(k),
                     **({"resample": RES[fam]} if k in single and fam in RES else {})})

SUBJECTS = sorted(set(meta["subject"]))
strip = lambda t: re.sub(r"\[asy\].*?\[/asy\]", " (figure not shown) ", t, flags=re.S).strip()
problems = [{"id": text[i]["unique_id"].removeprefix("test/").removesuffix(".json"), "sub": SUBJECTS.index(meta["subject"][i]),
             "lvl": meta["level"][i], "s": s[i], "n": n[i], "t": strip(text[i]["problem"]), "a": text[i]["answer"]} for i in range(N)]
assert all(1 <= p["lvl"] <= 5 for p in problems)

data = {"set": "MATH-500", "n": N, "singles": len(single), "grader": vec["grader"], "sampling": "T 1.0, top-p 1.0, one sample",
        "src": {"vectors": RUN + "vectors.json", "readout": RUN + "readout.json", "meta": META, "text": TEXT,
                "finding": "/finding/one-difficulty-axis", "board": "result-5da8a9"},
        "pairs": readout["different_arm_pairs"]["summary"],
        "subjects": SUBJECTS, "rank": rank, "problems": problems, "arms": out_arms}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
assert len(blob.encode()) < 1_000_000, len(blob)
assert "/home/" not in blob
(HERE / "data.json").write_text(blob)
print(f"data.json {len(blob.encode()) // 1024} KB, {N} problems, {len(out_arms)} configurations")
for a in out_arms:
    print(f"  {a['k']:16} solves {a['total']:3}  under {a['under']:3}  islands {a['islands']:3}  buoys {a['buoys']:3}")
print("  two samples of one configuration differ on", RES)
