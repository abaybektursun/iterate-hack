"""r5-m11 prediction 2: share of hard328 answers with code markers, Code-RL 3.1 cue minus base cue.

Main: plain case-sensitive substring test on field `text` for
'```', 'def ', 'for i in range', 'print(', 'import '.
alt_measured: same, but 'def ' and 'import ' must start at a word boundary
(so e.g. 'undef ' would not count).
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.getcwd()
BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5"
FILES = {
    "code": ("day1_wdiff328-01", "abaybektursun-1114-181216-a619"),
    "base": ("day1_hard328-01", "abaybektursun-1114-151534-e72c"),
}
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
    rows = [json.loads(l) for l in open(path) if l.strip()]
    by = {}
    for r in rows:
        if "problem_index" not in r:
            nc(f"row without problem_index in {path}")
        p = r["problem_index"]
        if "attempt" in r:
            if r["attempt"] == 0 and p not in by:
                by[p] = r
        elif p not in by:
            by[p] = r  # first row when there is no attempt field
    return by


def marked(t):
    return any(m in t for m in MARKERS)


def marked_alt(t):
    return ALT_RE.search(t) is not None


shares, alts, ex = {}, {}, None
for k, (folder, job) in FILES.items():
    by = load(fetch(folder, job))
    if not by:
        nc(f"no rows after filter in {job}")
    for r in by.values():
        if "text" not in r or not isinstance(r["text"], str):
            nc(f"row without a text string in {job}")
    m = [marked(r["text"]) for r in by.values()]
    ma = [marked_alt(r["text"]) for r in by.values()]
    shares[k] = sum(m) / len(m)
    alts[k] = sum(ma) / len(ma)
    print(f"diag: {k} {job} rows={len(by)} marked={sum(m)} marked_alt={sum(ma)}")
    if k == "code":
        r0 = next((r for r in by.values() if marked(r["text"])), next(iter(by.values())))
        ex = {kk: vv for kk, vv in r0.items() if kk != "logprobs"}
        if len(ex.get("text", "")) > 3000:
            ex["text"] = ex["text"][:3000] + " ...[truncated in example_row only]"

stat = shares["code"] - shares["base"]
alt = alts["code"] - alts["base"]
out({"measured": stat, "refuted_by_met": bool(stat < 0.04), "alt_measured": alt,
     "not_computable": None, "example_row": ex})
