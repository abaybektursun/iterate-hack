"""r4-m09 p2: MATH-500, Code-RL cue (0203) minus random-difference cue (6429) fix rate on base clean-finished-wrong problems W."""
import json
import os
import subprocess
import sys

DIR = "runs/theory-tests/r4m09"
PER_PROBLEM = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def out(measured, met, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": met, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))
    sys.exit(0)


def fetch_modal(job):
    path = os.path.join(DIR, job, "answers.jsonl")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", job + "/answers.jsonl", path],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return path


def first_rows(path):
    rows = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r["problem_index"] not in rows:
                rows[r["problem_index"]] = r
    return rows


def strip(r):
    return {k: v for k, v in r.items() if k not in ("text", "prompt", "answer_tokens")}


try:
    pp = json.load(open(PER_PROBLEM))
except Exception as e:
    out(None, False, None, "per_problem.json not readable: %s" % e, None)

tabs = {}
for job in ("abaybektursun-1114-162452-0203", "abaybektursun-1114-153047-6429"):
    path = fetch_modal(job)
    if not os.path.exists(path):
        out(None, False, None, "iterate-runs:%s/answers.jsonl could not be fetched" % job, None)
    tabs[job] = first_rows(path)
    if tabs[job] and "score_v3" not in next(iter(tabs[job].values())):
        out(None, False, None, "score_v3 field missing in %s rows" % job, None)
code = tabs["abaybektursun-1114-162452-0203"]
rand = tabs["abaybektursun-1114-153047-6429"]

W = [p["problem_index"] for p in pp if p["t1_right"] == 0 and p["t1_cap_hit"] is False]
if not W:
    out(None, False, None, "set W is empty", None)

c_right = sum(1 for i in W if i in code and code[i].get("score_v3") == 1)
r_right = sum(1 for i in W if i in rand and rand[i].get("score_v3") == 1)
measured = (c_right - r_right) / len(W)

# alt: restrict W to problems present in both files (missing rows dropped rather than counted wrong)
Wb = [i for i in W if i in code and i in rand]
alt = None
if Wb:
    alt = (sum(1 for i in Wb if code[i].get("score_v3") == 1)
           - sum(1 for i in Wb if rand[i].get("score_v3") == 1)) / len(Wb)

example = next((strip(code[i]) for i in W if i in code), None)
out(measured, measured > 0.12, alt, None, example)
