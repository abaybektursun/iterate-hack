"""r5-m11 prediction 3: within Code-RL 3.1 cue hard328 answers, accuracy of marked minus unmarked,
stratified into 4 quartiles of 82 problems by RL plain (86ef) n_generated (ties by problem_index).

Statistic = sum_q n_marked_q * (acc_m - acc_u) / sum_q n_marked_q over quartiles with both
marked and unmarked answers; -1 if no quartile is kept. Cap hits and missing score_v3 -> 0.
Main marker rule: plain case-sensitive substrings. alt_measured: word-boundary rule for
'def ' and 'import ' (as in p2's alt).
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.getcwd()
BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5"
CODE = ("day1_wdiff328-01", "abaybektursun-1114-181216-a619")
RL = ("day1_hard328-01", "abaybektursun-1114-151540-86ef")
MARKERS = ["```", "def ", "for i in range", "print(", "import "]
ALT_RE = re.compile(r"```|\bdef |for i in range|print\(|\bimport ")


def out(d):
    print(json.dumps(d))
    sys.exit(0)


def nc(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None,
         "not_computable": reason, "example_row": None})


def fetch(folder, job):
    path = os.path.join(ROOT, "runs/theory-tests", job, "answers.jsonl")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{folder}/{job}/answers.jsonl", path,
                            "--profile", "iterate-ecr", "--only-show-errors"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            nc(f"fetch failed for {job}: {r.stderr.strip()[:300]}")
    return path


def load(path):
    by = {}
    for l in open(path):
        if not l.strip():
            continue
        r = json.loads(l)
        p = r["problem_index"]
        if "attempt" in r:
            if r["attempt"] == 0 and p not in by:
                by[p] = r
        elif p not in by:
            by[p] = r
    return by


code = load(fetch(*CODE))
rl = load(fetch(*RL))

if len(rl) != 328:
    nc(f"RL file 86ef has {len(rl)} problems after filter, recipe needs 328 for 4 x 82")
for p, r in rl.items():
    if not isinstance(r.get("n_generated"), (int, float)):
        nc(f"RL row {p} has no numeric n_generated")

order = sorted(rl, key=lambda p: (rl[p]["n_generated"], p))
quartiles = [order[i * 82:(i + 1) * 82] for i in range(4)]


def score(r):
    if r.get("cap_hit") is True:
        return 0
    s = r.get("score_v3")
    if s is None:
        return 0
    return int(s)


def stat(is_marked):
    num, den, kept, diag = 0.0, 0, 0, []
    for q in quartiles:
        m = [score(code[p]) for p in q if p in code and is_marked(code[p].get("text") or "")]
        u = [score(code[p]) for p in q if p in code and not is_marked(code[p].get("text") or "")]
        diag.append((len(m), len(u)))
        if not m or not u:
            continue
        kept += 1
        num += len(m) * (sum(m) / len(m) - sum(u) / len(u))
        den += len(m)
    return (num / den if kept else -1.0), diag


main, dmain = stat(lambda t: any(x in t for x in MARKERS))
alt, dalt = stat(lambda t: ALT_RE.search(t) is not None)
missing = sum(1 for p in order if p not in code)
print(f"diag: code rows={len(code)} missing_from_code={missing} "
      f"(n_marked,n_unmarked) per quartile main={dmain} alt={dalt}")

p0 = next((p for p in order if p in code and any(x in (code[p].get("text") or "") for x in MARKERS)),
          next(p for p in order if p in code))
ex = {k: v for k, v in code[p0].items() if k != "logprobs"}
if len(ex.get("text", "")) > 3000:
    ex["text"] = ex["text"][:3000] + " ...[truncated in example_row only]"
ex["_rl_n_generated"] = rl[p0]["n_generated"]

out({"measured": main, "refuted_by_met": bool(main < -0.05), "alt_measured": alt,
     "not_computable": None, "example_row": ex})
