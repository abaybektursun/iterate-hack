"""data.json of the Lab picture "one-take": the 500 MATH-500 problems, right or wrong at each step of the main line.

  uv run studies/sitelab/prototypes/one-take/build.py

The five steps, all at T 1.0 / top-p 1.0, grader v3, 16,384 tokens allowed: the base with the plain prompt, the base with
the opening cue, a vote over 4 samples of the cued base, the cued base plus RL's 8 largest directions per weight matrix
at size 1.5, and RL itself (one sample). Every per-problem row is read from a committed artifact of studies/rlneurons;
every count is compared with the total stored in the artifact's readout and in the finding page that shows it
(tools/finding_*.py). A mismatch stops the build.
"""
import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
R = "studies/rlneurons/"
sys.path.insert(0, str(REPO / "tools"))
cue_page = importlib.import_module("finding_opening_cue")
vote_page = importlib.import_module("finding_vote_over_four")
dial_page = importlib.import_module("finding_the_finish_dial")


def load(path):
    return json.loads((REPO / path).read_text())


def same(what, *values):
    assert len(set(map(json.dumps, values))) == 1, f"{what}: {values}"
    return values[0]


N = 500
problems = load(R + "data/rln4/math500.json")
items = load(R + "results/rln4/t1_t3_items-01/per_problem.json")
items_total = load(R + "results/rln4/t1_t3_items-01/metrics.json")
vectors = load(R + "results/axis/math500-01/vectors.json")
vote = load(R + "results/day1_3/math500_base_cue-01/readout.json")
rl = load(R + "results/day1_3/math500_rl-01/readout.json")
dial = load(R + "results/xreward/dial15_math500-01/readout.json")
dial_rows = [json.loads(x) for x in (REPO / R / "results/xreward/dial15_math500-01/rows.jsonl").read_text().splitlines()]

order = list(range(N))
same("problem order", order, [p["index"] for p in problems], [r["problem_index"] for r in items], vectors["problem_indices"],
     vote["problem_indices"], rl["problem_indices"], dial["problem_indices"], [r["problem_index"] for r in dial_rows])
same("problem ids", [p["unique_id"] for p in problems], vectors["unique_ids"])
same("grader", "v3", vectors["grader"])

OC, VO, FD = cue_page.DATA, vote_page.DATA, dial_page.DATA
plain = [r["t3_right"] for r in items]
cue = [r["t1_right"] for r in items]
voted = same("vote rows", vectors["arms"]["base_vote4"], vote["per_problem"]["vote"])
edit = same("edit rows", dial["per_problem"]["single"], [r["score_v3"] for r in dial_rows])
rl_one = same("RL rows", vectors["arms"]["rl_plain_s0"], rl["per_problem"]["single"])
first_sample = vectors["arms"]["base_cue_s0"]

steps = [
    {"key": "plain", "name": "Base, plain prompt", "rows": plain, "source": R + "results/rln4/t1_t3_items-01/per_problem.json (t3_right)",
     "right": same("plain", sum(plain), OC["plain"]["right"], items_total["t3"]["right"])},
    {"key": "cue", "name": "Base + opening cue", "rows": cue, "source": R + "results/rln4/t1_t3_items-01/per_problem.json (t1_right)",
     "right": same("cue", sum(cue), OC["cue"]["right"], items_total["t1"]["right"])},
    {"key": "vote", "name": "Base + cue, vote over 4 samples", "rows": voted, "source": R + "results/axis/math500-01/vectors.json (base_vote4)",
     "right": same("vote", sum(voted), VO["rows"][0]["vote"], vote["rows"]["vote"]["right"])},
    {"key": "edit", "name": "Base + cue + 8 RL directions at size 1.5", "rows": edit, "source": R + "results/xreward/dial15_math500-01/readout.json (per_problem.single)",
     "right": same("edit", sum(edit), FD["rep"]["m500"], dial["rows"]["single"]["right"])},
    {"key": "rl", "name": "RL, one sample", "rows": rl_one, "source": R + "results/axis/math500-01/vectors.json (rl_plain_s0)",
     "right": same("RL", sum(rl_one), FD["rep"]["m500_rl"][0], VO["rows"][1]["single"], rl["rows"]["single"]["right"])},
]
for s in steps:
    assert len(s["rows"]) == N and set(s["rows"]) <= {0, 1}, s["key"]

flips = {"up": sum(c > p for p, c in zip(plain, cue)), "down": sum(c < p for p, c in zip(plain, cue))}
same("cue flips", flips, OC["flips"], {"up": items_total["two_by_two"]["cue_only"], "down": items_total["two_by_two"]["plain_only"]})
same("vote flips", [sum(v > s for s, v in zip(first_sample, voted)), sum(v < s for s, v in zip(first_sample, voted))],
     [VO["wrong_to_right"], VO["right_to_wrong"]])
same("vote's first sample", sum(first_sample), VO["rows"][0]["single"], VO["rows"][0]["each"][0])
same("RL vote", VO["rows"][1]["vote"], rl["rows"]["vote"]["right"])
edit_minus_rl = dial["minus"]["differences_points"]["single"]
assert dial["minus"]["readout"] == R + "results/day1_3/math500_rl-01/readout.json"
same("edit minus RL", round(edit_minus_rl["points"], 1), round(100 * (sum(edit) - sum(rl_one)) / N, 1))
same("RL samples", FD["rep"]["m500_rl"], OC["rl"]["samples"], rl["each_sample"]["single_right"])
same("nothing extracted", OC["plain"]["nothing_extracted"], items_total["t3"]["nothing_extracted"])

solved_by = [sum(s["rows"][i] for s in steps) for i in range(N)]
none, every = solved_by.count(0), solved_by.count(len(steps))
# The order of the pins in every register: by the steps that solve the problem, earliest first, so a register fills like a gauge.
pins = sorted(order, key=lambda i: [-s["rows"][i] for s in steps] + [i])


def subject(uid):
    return uid.split("/")[1].replace("_", " ").capitalize()


out = {
    "n": N,
    "setting": "MATH-500, one sample per problem at T 1.0 and top-p 1.0, 16,384 tokens allowed, grader v3",
    "steps": [{"key": s["key"], "name": s["name"], "right": s["right"], "source": s["source"],
               "rows": "".join(map(str, s["rows"]))} for s in steps],
    "pins": pins,
    "none": none, "every": every,
    "facts": {
        "cue_text": OC["cue_text"], "cue_tokens": OC["cue_tokens"], "cue_up": flips["up"], "cue_down": flips["down"],
        "plain_nothing_extracted": OC["plain"]["nothing_extracted"],
        "vote_first_sample": VO["rows"][0]["single"], "vote_samples": VO["rows"][0]["each"], "vote_gain": VO["rows"][0]["gain"],
        "vote_gain_ci": VO["rows"][0]["gain_ci"], "vote_times_tokens": vote_page.TIMES, "rl_vote": VO["rows"][1]["vote"],
        "edit_minus_rl": [round(edit_minus_rl["points"], 1)] + [round(x, 1) for x in edit_minus_rl["interval95"]],
        "edit_norm_percent": round(100 * FD["cells"]["1.5"]["add_rel"], 2), "edit_k": FD["k"], "edit_matrices": FD["n_edited"],
        "hard_n": FD["n"], "hard_base_cue": FD["cells"]["0"]["right"], "hard_edit": FD["cells"]["1.5"]["right"],
        "hard_rl": FD["cells"]["rl"]["right"],
        "rl_samples": FD["rep"]["m500_rl"], "rl_first_run": OC["rl_first"]["right"],
    },
    "pages": {"cue": "/finding/opening-cue", "vote": "/finding/vote-over-four", "edit": "/finding/the-finish-dial"},
    "problems": [{"subject": subject(p["unique_id"]), "text": p["problem"], "answer": p["answer"]} for p in problems],
}
text = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
assert len(text.encode()) < 1_000_000, len(text.encode())
assert "/home/" not in text, "a home path in data.json"
(HERE / "data.json").write_text(text)
print(f"data.json: {len(text.encode()):,} bytes; " + ", ".join(f"{s['key']} {s['right']}" for s in steps) + f"; none {none}, every {every}")
