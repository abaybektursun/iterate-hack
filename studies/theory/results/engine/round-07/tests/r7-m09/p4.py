"""r7-m09 prediction 4: normal length.
On E4 problems, x = ln(max(n_generated,1)/max(t2_generated_tokens,1)) for Think-SFT cue finished rows (not cap hit,
non-null score_v3) vs RL (T2) tokens on the same problem. Statistic = median(x | FW) - median(x | FR)."""
import json
import math
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, refuted_without_number, not_computable

BASE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
CUE = "studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json"
RL = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def path_of(p):
    if os.path.exists(p):
        return p
    dst = os.path.join("runs/theory-tests/r7-m09", p)
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(subprocess.run(["git", "show", "HEAD:" + p], check=True, capture_output=True).stdout)
    return dst


def load_jsonl(p):
    with open(path_of(p)) as f:
        return [json.loads(l) for l in f if l.strip()]


def first_per_problem(p):
    with open(path_of(p)) as f:
        rows = json.load(f)
    out = {}
    for r in rows:
        if r["problem_index"] not in out:
            out[r["problem_index"]] = r
    return out


def e4_set(base_rows):
    by = {}
    for r in base_rows:
        if r.get("attempt") == 0:
            by.setdefault(r["problem_index"], []).append(r)
    return sorted(pi for pi, rs in by.items()
                  if len(rs) == 4 and all(x.get("score_v3") == 1 and x.get("cap_hit") is not True for x in rs))


def median(v):
    s = sorted(v)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def build(E4, cue, rl, require_rl_finished):
    kept = []
    for pi in E4:
        c, t = cue.get(pi), rl.get(pi)
        if c is None or t is None:
            continue
        if c.get("cap_hit") is True or c.get("score_v3") is None:
            continue
        if t.get("t2_generated_tokens") is None:
            continue
        if require_rl_finished and t.get("t2_cap_hit") is True:
            continue
        if c["score_v3"] not in (0, 1):
            continue
        x = math.log(max(c.get("n_generated") or 0, 1) / max(t["t2_generated_tokens"], 1))
        kept.append({"problem_index": pi, "score_v3": c["score_v3"], "x": x, "cue": c, "rl": t})
    return kept


def diff(sample):
    fw = [e["x"] for e in sample if e["score_v3"] == 0]
    fr = [e["x"] for e in sample if e["score_v3"] == 1]
    if not fw or not fr:
        return None
    return median(fw) - median(fr)


def main():
    base = load_jsonl(BASE)
    cue = first_per_problem(CUE)
    rl = first_per_problem(RL)
    E4 = e4_set(base)
    kept = build(E4, cue, rl, require_rl_finished=False)
    n_fw = sum(e["score_v3"] == 0 for e in kept)
    n_fr = sum(e["score_v3"] == 1 for e in kept)
    print(json.dumps({"groups": {"FW": n_fw, "FR": n_fr}}))
    if n_fw < 3:
        refuted_without_number()
        return
    if n_fr == 0:
        not_computable("group FR (finished v3-right Think-SFT cue rows on E4) is empty, so its median is undefined")
        return
    m = diff(kept)

    def stat(sample):
        d = diff(sample)
        return m if d is None else d  # a resample with an empty group (very rare) falls back to the full-sample value

    kept_alt = build(E4, cue, rl, require_rl_finished=True)
    alt = diff(kept_alt) if sum(e["score_v3"] == 0 for e in kept_alt) >= 3 else None

    fw_ex = next(e for e in kept if e["score_v3"] == 0)
    ex = {"cue": fw_ex["cue"], "rl": fw_ex["rl"], "x": fw_ex["x"]}
    report(m, min(n_fw, n_fr), bootstrap(stat, kept), "bootstrap", refuted_by_met=(m > 0.40 or m < -0.40),
           alt_measured=alt, example_row=ex)


main()
