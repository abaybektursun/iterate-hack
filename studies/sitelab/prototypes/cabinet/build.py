"""Build data.json for the cabinet prototype: the 500 MATH-500 problems as the drawers of one cabinet, and for eight
configurations whether each problem was solved, the tokens generated and the extracted final answer, from committed
files of studies/rlneurons.

    python3 studies/sitelab/prototypes/cabinet/build.py

Definitions (the page states them and recomputes the counts; this file checks them against stored totals):
- configurations: one sample each at T 1.0 / top-p 1.0 under grader v3, except the two votes (plurality over the 4
  samples of that configuration; tokens = the sum over the 4 samples; answer = the answer of the sample the vote picked).
- opens: the number of the eight configurations that solve a problem.
- order of the drawers (left to right, then top to bottom): by subject (alphabetical), then most opens first, then lower
  level, then the problem's index in MATH-500.
- shut for all: opens = 0. RL only: solved by an RL configuration (sample or vote) and by none of the six others.
The build fails when a total differs from the run's stored total, or when private text is in the output.
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
R = "studies/rlneurons/results/"
AXIS = R + "axis/math500-01/"
META = "studies/rlneurons/data/profile/math500_meta_v1.json"
TEXT = "studies/rlneurons/data/rln4/math500.json"
N = 500

load = lambda p: json.loads((ROOT / p).read_text())
lines = lambda p: [json.loads(x) for x in (ROOT / p).read_text().splitlines()]
vec, manifest, readout, meta, text = load(AXIS + "vectors.json"), load(AXIS + "manifest.json"), load(AXIS + "readout.json"), load(META), load(TEXT)
arms = vec["arms"]
assert vec["grader"] == "v3" and vec["problem_indices"] == list(range(N))
assert vec["unique_ids"] == meta["unique_ids"] == [t["unique_id"] for t in text], "problem order differs between files"


def rows(path, sample):  # rows.jsonl of run_cell: the first attempt of one sample
    r = {x["problem_index"]: x for x in lines(path) if x["sample"] == sample and x["attempt"] == 0}
    assert sorted(r) == list(range(N)), path
    return [r[i] for i in range(N)]


def per_problem(path):
    r = load(path)
    assert [x["problem_index"] for x in r] == list(range(N)), path
    return r


def single(path, sample=0):
    r = rows(path, sample)
    return [x["score_v3"] for x in r], [x["n_new"] for x in r], [x["extracted_v3"] for x in r]


def vote(rows_path, selector):
    s = [rows(rows_path, j) for j in range(4)]
    sel = load(selector)
    pick = sel["picks"]["vote"]
    tok = [sum(s[j][i]["n_new"] for j in range(4)) for i in range(N)]
    assert abs(sum(tok) / N - sel["rows"]["vote"]["tokens_per_problem"]) < 0.01, selector
    return sel["per_problem"]["vote"], tok, [None if pick[i] is None else s[pick[i]][i]["extracted_v3"] for i in range(N)]


def plain(path):
    r = per_problem(path)
    return [x["score_v3"] for x in r], [x["n_generated"] for x in r], None


t3 = per_problem(R + "rln4/t1_t3_items-01/per_problem.json")
BASE, RL = R + "day1_3/math500_base_cue-01/rows.jsonl", R + "day1_3/math500_rl-01/rows.jsonl"
DIAL = R + "xreward/dial15_math500-01/"
# key, name, short name, kind, source, (right, tokens, answers), stored total, the axis study's vector of the same run
CONFIGS = [
    ("base_plain", "Base, plain prompt", "Base", "base", R + "rln4/t1_t3_items-01/per_problem.json",
     ([x["t3_right"] for x in t3], [x["t3_generated_tokens"] for x in t3], [x["t3_extracted_v3"] for x in t3]),
     load(R + "rln4/t1_t3_items-01/metrics.json")["t3"]["right"], None),
    ("base_cue", "Base + opening cue", "Cue", "base", BASE, single(BASE), manifest["arms"]["base_cue_s0"]["right"], "base_cue_s0"),
    ("base_vote4", "Base + cue, vote over 4 samples", "Cue, vote of 4", "base", BASE,
     vote(BASE, R + "selector/math500_base_cue-01/readout.json"), manifest["arms"]["base_vote4"]["right"], "base_vote4"),
    ("top8_plain", "Base + top 8 directions of RL − base, plain prompt", "Weight edit", "edit", R + "wsp1/full500/top8_plain-01/per_problem.json",
     plain(R + "wsp1/full500/top8_plain-01/per_problem.json"), manifest["arms"]["top8_plain"]["right"], "top8_plain"),
    ("top8x15_cue", "Base + 1.5 × top 8 directions, opening cue", "Weight edit × 1.5, cue", "edit", DIAL + "rows.jsonl",
     single(DIAL + "rows.jsonl"), load(DIAL + "metrics.json")["counts"]["correct_v3"], None),
    ("sft1_cue", "Think-SFT checkpoint + opening cue", "Think-SFT, cue", "other", R + "wsp1/full500/sft1_cue-01/per_problem.json",
     plain(R + "wsp1/full500/sft1_cue-01/per_problem.json"), manifest["arms"]["sft1_cue"]["right"], "sft1_cue"),
    ("rl_plain", "RL checkpoint, plain prompt", "RL", "rl", RL, single(RL), manifest["arms"]["rl_plain_s0"]["right"], "rl_plain_s0"),
    ("rl_vote4", "RL checkpoint, vote over 4 samples", "RL, vote of 4", "rl", RL,
     vote(RL, R + "selector/math500_rl-01/readout.json"), manifest["arms"]["rl_vote4"]["right"], "rl_vote4"),
]

cut = lambda t, n: t if len(t) <= n else t[: n - 1].rstrip() + "…"
configs = []
for k, name, short, kind, src, (right, tok, ans), total, arm in CONFIGS:
    assert len(right) == len(tok) == N and set(right) <= {0, 1} and sum(right) == total, (k, sum(right), total)
    assert arm is None or right == arms[arm], k
    configs.append({"k": k, "name": name, "short": short, "kind": kind, "src": src, "total": total,
                    "r": "".join(map(str, right)), "tok": tok,
                    "ans": None if ans is None else [None if a is None else cut(a.strip(), 60) for a in ans]})

opens = [sum(int(c["r"][i]) for c in configs) for i in range(N)]
SUBJECTS = sorted(set(meta["subject"]))
order = sorted(range(N), key=lambda i: (SUBJECTS.index(meta["subject"][i]), -opens[i], meta["level"][i], i))
rl = [c for c in configs if c["kind"] == "rl"]
others = [c for c in configs if c["kind"] != "rl"]
shut = sum(1 for o in opens if o == 0)
rl_only = sum(1 for i in range(N) if any(c["r"][i] == "1" for c in rl) and not any(c["r"][i] == "1" for c in others))
# the floor of the axis study (39 configurations) is a subset of the drawers shut here
floor = readout["floor"]["no_arm_solves_ids"]["problem_indices"]
assert all(opens[i] == 0 for i in floor) and shut >= len(floor)

strip = lambda t: re.sub(r"\s+", " ", re.sub(r"\[asy\].*?\[/asy\]", " (figure not shown) ", t, flags=re.S)).strip()
data = {
    "set": "MATH-500", "n": N, "cols": 25, "rows": 20, "grader": "v3", "sampling": "T 1.0, top-p 1.0",
    "src": {"text": TEXT, "meta": META, "axis": AXIS + "vectors.json"},
    "check": {"shut": shut, "rl_only": rl_only, "floor39": len(floor)},
    "subjects": SUBJECTS, "order": order,
    "id": [t["unique_id"].removeprefix("test/").removesuffix(".json") for t in text],
    "sub": [SUBJECTS.index(s) for s in meta["subject"]], "lvl": meta["level"],
    "t": [cut(strip(t["problem"]), 400) for t in text], "a": [cut(t["answer"], 80) for t in text],
    "configs": configs,
}
assert len(order) == N == data["cols"] * data["rows"] and all(1 <= x <= 5 for x in data["lvl"])
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
assert len(blob.encode()) < 600_000, len(blob.encode())
private = re.search(r"/home/|/Users/|[\w.+-]+@[\w-]+\.[a-z]{2,}|sk-[A-Za-z0-9]{16}|AKIA[A-Z0-9]{12}|hf_[A-Za-z0-9]{20}", blob)
assert not private, f"private text: {private.group(0)}"
(HERE / "data.json").write_text(blob)

print(f"data.json {len(blob.encode()) // 1024} kB, {N} problems, {len(configs)} configurations")
for c in configs:
    print(f"  {c['k']:12} solves {c['total']:3}  mean tokens {sum(c['tok']) / N:8.0f}  answers {'yes' if c['ans'] else 'no'}")
print(f"  shut for all {len(configs)}: {shut} (the axis study's 39 configurations: {len(floor)})   RL only: {rl_only}")
