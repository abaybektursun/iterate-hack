"""k=5: fraction of base->RL hold-on rate increase reached by theta0.25 (cue), cap_hit false rows, one row per problem."""
import json, math, os, re, subprocess
from studies.theory.lib.noise import bootstrap, report, not_computable

D = "runs/theory-tests/repl-r3-across-2"
T1 = ("s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl", f"{D}/T1.jsonl")
TH = ("abaybektursun-1114-153102-b029/answers.jsonl", f"{D}/b029/answers.jsonl")
RL = ("abaybektursun-1114-153110-e985/answers.jsonl", f"{D}/e985/answers.jsonl")
PAT = re.compile(r"\b(Wait|Hmm)\b")


def fetch_s3(uri, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def fetch_modal(rem, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", rem, path], check=True,
                       stdout=subprocess.DEVNULL)


def load(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def dedup(rows):
    """One row per problem_index: highest attempt (missing attempt = 0); on equal attempt the later row in the file."""
    best = {}
    for r in rows:
        p = r["problem_index"]
        a = r.get("attempt") or 0
        if p not in best or a >= (best[p].get("attempt") or 0):
            best[p] = r
    return best


try:
    fetch_s3(*T1); fetch_modal(*TH); fetch_modal(*RL)
    raw = {"T1": load(T1[1]), "theta0.25_cue": load(TH[1]), "rl_cue": load(RL[1])}
except Exception as e:
    not_computable(f"row file not readable: {e}")
    raise SystemExit(0)

for rows in raw.values():
    for r in rows:
        if "text" not in r or "cap_hit" not in r or "problem_index" not in r:
            not_computable("row lacks text, cap_hit or problem_index")
            raise SystemExit(0)

# dedup first (highest attempt), then keep cap_hit false
kept = {g: {p: r for p, r in dedup(rows).items() if r["cap_hit"] is False} for g, rows in raw.items()}
G = ("T1", "theta0.25_cue", "rl_cue")


def rate(rows):
    chars = sum(len(r["text"]) for r in rows)
    m = sum(len(PAT.findall(r["text"])) for r in rows)
    return None if chars == 0 else m / chars * 10000.0


def frac(groups):
    r0, rt, r1 = (rate(groups[g]) for g in G)
    if None in (r0, rt, r1) or r1 - r0 == 0:
        return float("nan")
    return (rt - r0) / (r1 - r0)


pids = sorted(set().union(*[set(kept[g]) for g in G]))
units = [tuple(kept[g].get(p) for g in G) for p in pids]   # (T1 row|None, theta row|None, rl row|None)


def stat(sample):
    return frac({g: [u[i] for u in sample if u[i] is not None] for i, g in enumerate(G)})


measured = stat(units)
common = [u for u in units if all(x is not None for x in u)]
alt = stat(common) if common else None
if alt is not None and isinstance(alt, float) and math.isnan(alt):
    alt = None

print(json.dumps({"groups": {g: len(kept[g]) for g in G}}))
ex = dict(kept["theta0.25_cue"][min(kept["theta0.25_cue"])]); ex["text"] = ex["text"][:300]
for k in ("answer_tokens", "prefill_ids", "prompt"):
    ex.pop(k, None)
report(measured, min(len(kept[g]) for g in G), bootstrap(stat, units), "bootstrap",
       refuted_by_met=False, alt_measured=alt, example_row=ex)
