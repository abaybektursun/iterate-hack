"""r5-m05 prediction 1: per-hold-on revision rate, base (T1, cue) / RL (T2, plain), MATH-500.

Main: numbers compared as exact strings (recipe). alt_measured: numbers compared by numeric value
(float), so '0.5' and '0.50' count as the same number.
"""
import json
import os
import re
import subprocess

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons"
FILES = {
    "base": ("r4/base_rl-02/out/T1.jsonl", "runs/theory-tests/s3/T1.jsonl"),
    "rl": ("r4/modal_t2-01/t2/T2.jsonl", "runs/theory-tests/s3/T2.jsonl"),
}
COMMA = re.compile(r"(?<=\d),(?=\d{3})")
HOLD = re.compile(r"(?<![A-Za-z])(Wait|Hmm)(?![A-Za-z])")
NUM = re.compile(r"\d+(?:\.\d+)?")


def fail(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                      "not_computable": reason, "example_row": None}))
    raise SystemExit(0)


def fetch(key, local):
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{key}", local, "--profile", "iterate-ecr",
                            "--only-show-errors"], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(local):
            fail(f"could not fetch {key}: {r.stderr.strip()[:300]}")
    rows = []
    with open(local) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def rates(rows):
    elig = rev = rev_num = 0
    example = None
    for r in rows:
        if r is None or "cap_hit" not in r or "text" not in r:
            continue  # missing row
        if r["cap_hit"] is not False:
            continue
        text = r["text"]
        if text is None:
            continue
        text = COMMA.sub("", text)
        for m in HOLD.finditer(text):
            s, e = m.start(), m.end()
            before = NUM.findall(text[max(0, s - 300):s])
            after = NUM.findall(text[e:e + 400])
            if not before or not after:
                continue
            elig += 1
            if example is None:
                example = r
            a, b = before[-1], after[0]
            if a != b:
                rev += 1
            if float(a) != float(b):
                rev_num += 1
    return elig, rev, rev_num, example


out = {}
example = None
for name, (key, local) in FILES.items():
    rows = fetch(key, local)
    elig, rev, rev_num, ex = rates(rows)
    out[name] = (elig, rev, rev_num)
    if example is None:
        example = ex

be, br, brn = out["base"]
re_, rr, rrn = out["rl"]
if be == 0 or re_ == 0 or rr == 0:
    # base or RL rate undefined (no eligible occurrence or RL rate 0): ratio cannot be formed
    fail(f"ratio undefined: base eligible {be}, RL eligible {re_}, RL revisions {rr}")

measured = (br / be) / (rr / re_)
alt = None
if rrn > 0:
    alt = (brn / be) / (rrn / re_)

print(f"# base: {br}/{be} revisions; RL: {rr}/{re_} revisions")
print(json.dumps({"measured": measured, "refuted_by_met": bool(measured >= 0.80), "alt_measured": alt,
                  "not_computable": None, "example_row": example}))
