"""r5-m05 prediction 2: among base T1 finished-wrong MATH-500 answers with >=1 hold-on, the fraction whose
final answer already occurs (boundary-delimited) in the text before the last hold-on.

Main: occurrence must have a non-letter/non-digit (ASCII [A-Za-z0-9]) character, or the string boundary,
just before and just after. alt_measured: plain substring occurrence, no boundary condition.
"""
import json
import os
import re
import subprocess

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons"
KEY, LOCAL = "r4/base_rl-02/out/T1.jsonl", "runs/theory-tests/s3/T1.jsonl"
PER_PROBLEM = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
COMMA = re.compile(r"(?<=\d),(?=\d{3})")
HOLD = re.compile(r"(?<![A-Za-z])(Wait|Hmm)(?![A-Za-z])")
ALNUM = re.compile(r"[A-Za-z0-9]")


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
    with open(local) as f:
        return [json.loads(l) for l in f if l.strip()]


def unbox(s):
    """If s is exactly \\boxed{...} (the brace opened after \\boxed closes at the last char), return the inside."""
    pre = "\\boxed{"
    if not (s.startswith(pre) and s.endswith("}")):
        return s
    depth = 0
    for i in range(len(pre) - 1, len(s)):
        c = s[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[len(pre):i] if i == len(s) - 1 else s
    return s


def normalize(a):
    a = a.strip().replace("$", "")
    a = unbox(a)
    return a


def bounded_occurs(hay, needle):
    start = 0
    while True:
        i = hay.find(needle, start)
        if i < 0:
            return False
        j = i + len(needle)
        ok_before = i == 0 or not ALNUM.match(hay[i - 1])
        ok_after = j == len(hay) or not ALNUM.match(hay[j])
        if ok_before and ok_after:
            return True
        start = i + 1


if not os.path.exists(PER_PROBLEM):
    fail(f"{PER_PROBLEM} missing")
pp = json.load(open(PER_PROBLEM))
t1_right = {}
for x in pp:
    if "t1_right" not in x:
        fail("per_problem.json has no t1_right field")
    t1_right[x["problem_index"]] = x["t1_right"]

rows = fetch(KEY, LOCAL)
kept = notkept = 0
kept_alt = 0
dropped_empty_norm = 0
example = None
for r in rows:
    if r is None or "text" not in r or "cap_hit" not in r:
        continue
    pi = r.get("problem_index")
    if pi not in t1_right:
        continue  # missing in join
    if r["cap_hit"] is not False:
        continue
    if t1_right[pi] in (1, True):
        continue
    text = r["text"] or ""
    ms = list(HOLD.finditer(text))
    if not ms:
        continue
    s_last = ms[-1].start()
    ans = r.get("extracted_v2") or ""
    if not ans:
        ans = r.get("extracted") or ""
    if not ans:
        continue
    na = COMMA.sub("", normalize(ans))
    if na == "":
        dropped_empty_norm += 1
        continue  # answer normalizes to nothing: cannot be searched for
    hay = COMMA.sub("", text[:s_last])
    if example is None:
        example = r
    if bounded_occurs(hay, na):
        kept += 1
    else:
        notkept += 1
    if na in hay:
        kept_alt += 1

n = kept + notkept
if n == 0:
    fail("no base finished-wrong row with a hold-on and a non-empty answer")
measured = kept / n
alt = kept_alt / n
print(f"# kept {kept} of {n}; plain-substring kept {kept_alt}; dropped (empty after normalization) {dropped_empty_norm}")
print(json.dumps({"measured": measured, "refuted_by_met": bool(measured < 0.60), "alt_measured": alt,
                  "not_computable": None, "example_row": example}))
