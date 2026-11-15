"""k=3: hold-on rate ratio, base cue T 1.0 (r4 T1.jsonl) / base cue T 0.6 (r3 F_math500.jsonl, sample 0), cap_hit false rows."""
import json, os, re, subprocess
from studies.theory.lib.noise import bootstrap, report, not_computable

D = "runs/theory-tests/repl-r3-across-2"
SRC = {
    "T1": ("s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl", f"{D}/T1.jsonl"),
    "F": ("s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/F_math500.jsonl", f"{D}/F_math500.jsonl"),
}
PAT = re.compile(r"\b(Wait|Hmm)\b")


def fetch(uri, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def load(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


try:
    for uri, path in SRC.values():
        fetch(uri, path)
    t1 = load(SRC["T1"][1])
    fm = load(SRC["F"][1])
except Exception as e:
    not_computable(f"row file not readable: {e}")
    raise SystemExit(0)

for r in t1 + fm:
    if "text" not in r or "cap_hit" not in r:
        not_computable("row lacks text or cap_hit")
        raise SystemExit(0)

fm = [r for r in fm if r.get("sample") == 0]           # sample == 0 only in F_math500
t1k = [r for r in t1 if r["cap_hit"] is False]
fmk = [r for r in fm if r["cap_hit"] is False]


def rate(rows):
    chars = sum(len(r["text"]) for r in rows)
    m = sum(len(PAT.findall(r["text"])) for r in rows)
    return None if chars == 0 else m / chars * 10000.0


def ratio(a, b):
    ra, rb = rate(a), rate(b)
    if ra is None or rb is None or rb == 0:
        return float("nan")
    return ra / rb


# one bootstrap unit per problem_index: (list of kept T1 rows, list of kept F rows) for that problem
pids = sorted({r["problem_index"] for r in t1k} | {r["problem_index"] for r in fmk})
bt1 = {}; bfm = {}
for r in t1k: bt1.setdefault(r["problem_index"], []).append(r)
for r in fmk: bfm.setdefault(r["problem_index"], []).append(r)
units = [(tuple(bt1.get(p, [])), tuple(bfm.get(p, []))) for p in pids]


def stat(sample):
    a = [r for u in sample for r in u[0]]
    b = [r for u in sample for r in u[1]]
    return ratio(a, b)


measured = stat(units)

# alt: only problems finished (cap_hit false) in both files
common = [u for u in units if u[0] and u[1]]
alt = stat(common) if common else None

print(json.dumps({"groups": {"T1 (T 1.0) cap_hit false": len(t1k), "F_math500 sample 0 (T 0.6) cap_hit false": len(fmk)}}))
ex = dict(t1k[0]); ex["text"] = ex["text"][:300]
for k in ("answer_tokens", "prefill_ids"):
    ex.pop(k, None)
report(measured, min(len(t1k), len(fmk)), bootstrap(stat, units), "bootstrap",
       refuted_by_met=False, alt_measured=alt, example_row=ex)
