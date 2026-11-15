"""Direct tests codecontract-01 (round-13/s6-a) and codereliab-01 (round-13/s6-b), specs/SPEC_direct_code13.md.

    cd <checkout holding runs/> && uv run --no-project --with numpy python <worktree>/studies/theory/analysis/direct_code13.py

Reads runs/<job>/answers.jsonl (538 problems, one sample per cell, seed 51000000) from the current directory.
a: contract share of the Code-cue base failures that Code top-8 1x fixes vs those random rank-8 1.5x fixes.
b: share of those fixes that the base passes in its other base-like samples (Math cue, random 1.5x).
Writes studies/theory/results/direct/codecontract-01/ and codereliab-01/.
"""
import ast
import builtins
import json
import pathlib
import re
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = {"a": ROOT / "studies/theory/results/direct/codecontract-01", "b": ROOT / "studies/theory/results/direct/codereliab-01"}
JOBS = {"base": "abaybektursun-1114-170304-c03c", "mathcue": "abaybektursun-1114-170309-b137",
        "random": "abaybektursun-1115-101457-ef2c", "top8": "abaybektursun-1115-101423-4a7d", "rl": "abaybektursun-1114-170253-f661"}
B, RNG = 10000, np.random.default_rng(0)
BUILTIN = set(dir(builtins)) | {"math", "re", "abs", "sorted", "set", "list", "tuple"}


def load(job):
    rows = [json.loads(line) for line in open(pathlib.Path("runs") / job / "answers.jsonl")]
    return {r["uid"]: r for r in rows}


def entries(row):
    """Names the tests call: the HumanEval+ entry point, or the non-builtin names called in the MBPP+ test line (all called
    names when every one is a builtin's name)."""
    m = re.search(r"Write the complete Python function `(\w+)`", row["prompt"])
    if m:
        return {m.group(1)}
    line = row["prompt"].split("Your code should pass this test:\n")[1].split("\n")[0]
    called = set(re.findall(r"(?<![\w.])([A-Za-z_]\w*)\s*\(", line))
    assert called, line
    return (called - BUILTIN) or called      # an MBPP+ function may carry a builtin's name (sum, max)


def contract(row):
    """(is_contract_failure, reason) for one answer."""
    if row["cap_hit"]:
        return True, "cap_hit"
    if row["mode"] == "none":
        return True, "no_block"
    try:  # a parse failure is a graded category here, not a hidden error
        tree = ast.parse(row["code"])
    except SyntaxError:
        return True, "unparsable"
    defs = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    defs |= {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    if not (entries(row) & defs):
        return True, "no_entry"
    return False, "logic"


def q90(x):
    return [float(np.quantile(x, 0.05)), float(np.quantile(x, 0.95))]


rows = {k: load(j) for k, j in JOBS.items()}
uids = sorted(rows["base"])
assert len(uids) == 538 and all(sorted(rows[k]) == uids for k in rows)
P = {k: np.array([rows[k][u]["passed"] for u in uids], bool) for k in rows}
assert P["base"].sum() == 317 and P["top8"].sum() == 386 and P["random"].sum() == 331 and P["mathcue"].sum() == 326
cls = [contract(rows["base"][u]) for u in uids]
C = np.array([c for c, _ in cls])
reason = [r for _, r in cls]
fail = ~P["base"]

# Instrument checks.
he0 = rows["base"]["HumanEval/0"]
assert contract({**he0, "cap_hit": False, "mode": "block", "code": "def wrong():\n    pass\n"}) == (True, "no_entry")
assert contract({**he0, "cap_hit": False, "mode": "block", "code": "def f(:\n"}) == (True, "unparsable")
pass_flag = {r: int(sum(1 for i in range(538) if P["base"][i] and reason[i] == r)) for r in set(reason)}
pass_rows_flagged = int((P["base"] & C).sum())   # passing base answers flagged contract (cap-hit passes are expected)

IDX = RNG.integers(0, 538, (B, 538))


def share(num, den, idx=None):
    if idx is None:
        return num.sum() / den.sum()
    return num[idx].sum(1) / den[idx].sum(1)


def part_a(top):
    Ft, Fr = fail & P[top], fail & P["random"]
    St, Sr = share(Ft & C, Ft), share(Fr & C, Fr)
    rc, rl = share(Ft & C, fail & C), share(Ft & ~C, fail & ~C)
    Stb, Srb = share(Ft & C, Ft, IDX), share(Fr & C, Fr, IDX)
    ratiob = share(Ft & C, fail & C, IDX) / share(Ft & ~C, fail & ~C, IDX)
    lo = q90(Stb - Srb)[0]
    verdict = "holds" if (St >= 0.50 and lo > 0 and rc / rl >= 2.0) else "refuted"
    return {"F_top8": int(Ft.sum()), "F_rand": int(Fr.sum()), "S_top8": float(St), "S_top8_90": q90(Stb),
            "S_rand": float(Sr), "S_rand_90": q90(Srb), "S_diff": float(St - Sr), "S_diff_90": q90(Stb - Srb),
            "r_c": float(rc), "r_l": float(rl), "r_c_over_r_l": float(rc / rl), "ratio_90": q90(ratiob), "verdict": verdict}


k2 = P["mathcue"].astype(int) + P["random"].astype(int)
k1 = P["mathcue"].astype(int)


def part_b(fix, kk):
    Ft = fail & fix
    Qt, Qb = share(Ft & (kk >= 1), Ft), share(fail & (kk >= 1), fail)
    Qtb, Qbb = share(Ft & (kk >= 1), Ft, IDX), share(fail & (kk >= 1), fail, IDX)
    verdict = "holds" if (Qt >= 0.60 and q90(Qtb - Qbb)[0] > 0.10) else "refuted"
    return {"F": int(Ft.sum()), "Q": float(Qt), "Q_90": q90(Qtb), "Q_base": float(Qb), "Q_base_90": q90(Qbb),
            "Q_diff": float(Qt - Qb), "Q_diff_90": q90(Qtb - Qbb), "verdict": verdict}


A = part_a("top8")
planted_a = part_a("random")
assert abs(planted_a["S_diff"]) < 1e-12 and planted_a["verdict"] == "refuted"
Bm = part_b(P["top8"], k2)
rand_fix = np.zeros(538, bool)
rand_fix[RNG.choice(np.flatnonzero(fail), Bm["F"], replace=False)] = True
planted_b = part_b(rand_fix, k2)
assert planted_b["verdict"] == "refuted"
fixrate = {f"k2={v}": {"n": int((fail & (k2 == v)).sum()), "fixed_by_top8": int((fail & (k2 == v) & P["top8"]).sum())} for v in (0, 1, 2)}
cross = {f"{'contract' if c else 'logic'}_k2>=1": {"n": int((fail & (C == c) & (k2 >= 1)).sum()),
                                                  "fixed": int((fail & (C == c) & (k2 >= 1) & P["top8"]).sum())} for c in (True, False)}
cross.update({f"{'contract' if c else 'logic'}_k2=0": {"n": int((fail & (C == c) & (k2 == 0)).sum()),
                                                      "fixed": int((fail & (C == c) & (k2 == 0) & P["top8"]).sum())} for c in (True, False)})

reasons_fail = {r: int(sum(1 for i in range(538) if fail[i] and reason[i] == r)) for r in sorted(set(reason))}
reasons_fixed = {r: int(sum(1 for i in range(538) if fail[i] and P["top8"][i] and reason[i] == r)) for r in sorted(set(reason))}
reasons_rfixed = {r: int(sum(1 for i in range(538) if fail[i] and P["random"][i] and reason[i] == r)) for r in sorted(set(reason))}
commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
run = {"commit": commit, "command": "uv run --no-project --with numpy python " + " ".join(sys.argv), "input_jobs": JOBS,
       "inputs": "runs/<job>/answers.jsonl (gpu.py get copies, not committed)"}

ra = {"n_problems": 538, "n_base_failures": int(fail.sum()), "n_contract_failures": int((fail & C).sum()),
      "contract_share_all_failures": float((fail & C).sum() / fail.sum()),
      "rule": "holds iff S_top8 >= 0.50 and 90 % lower bound of S_top8 - S_rand > 0 and r_c / r_l >= 2.0; 90 % bootstrap, 10,000 draws",
      **A, "reasons_base_failures": reasons_fail, "reasons_fixed_by_top8": reasons_fixed, "reasons_fixed_by_random": reasons_rfixed,
      "base_passes_by_reason": pass_flag, "base_passes_flagged_contract": pass_rows_flagged,
      "planted_top8_eq_random": {"S_diff": planted_a["S_diff"], "verdict": planted_a["verdict"]}}
rb = {"n_problems": 538, "n_base_failures": int(fail.sum()),
      "rule": "holds iff Q_top8 >= 0.60 and 90 % lower bound of Q_top8 - Q_base > 0.10; k2 = passes in Math-cue and random 1.5x cells",
      **{f"top8_{k}": v for k, v in Bm.items()}, "Q_RL": part_b(P["rl"], k2), "secondary_k1_mathcue_only": part_b(P["top8"], k1),
      "secondary_k1_RL": part_b(P["rl"], k1), "fix_rate_by_k2": fixrate, "contract_x_k2": cross,
      "planted_random_subset": {"Q": planted_b["Q"], "Q_diff_90": planted_b["Q_diff_90"], "verdict": planted_b["verdict"]}}


def example(i, label):
    r = rows["base"][uids[i]]
    t = rows["top8"][uids[i]]
    return {"label": label, "uid": uids[i], "prompt_tail": r["prompt"][-300:], "base_reason": reason[i], "k2": int(k2[i]),
            "base": {"passed": r["passed"], "cap_hit": r["cap_hit"], "mode": r["mode"], "code_head": r["code"][:400], "stderr_tail": r["stderr_tail"][-200:]},
            "top8": {"passed": t["passed"], "cap_hit": t["cap_hit"], "mode": t["mode"], "code_head": t["code"][:400]}}


fixed = np.flatnonzero(fail & P["top8"])
ex_a = [example(next(i for i in fixed if C[i]), "supports a: contract failure fixed by top8"),
        example(next(i for i in fixed if not C[i]), "against a: logic failure fixed by top8")]
ex_b = [example(next(i for i in fixed if k2[i] >= 1), "supports b: base passes elsewhere (k2>=1), top8 fixes"),
        example(next(i for i in fixed if k2[i] == 0), "against b: base never passes (k2=0), top8 fixes")]
for key, ro, ex in (("a", ra, ex_a), ("b", rb, ex_b)):
    OUT[key].mkdir(parents=True, exist_ok=False)
    (OUT[key] / "readout.json").write_text(json.dumps(ro, indent=1) + "\n")
    (OUT[key] / "examples.json").write_text(json.dumps(ex, indent=1) + "\n")
    (OUT[key] / "run.json").write_text(json.dumps(run, indent=1) + "\n")
# 10 raw rows to read: the first 10 top8 fixes.
for i in fixed[:10]:
    r = rows["base"][uids[i]]
    print(uids[i], reason[i], "k2", k2[i], "cap", r["cap_hit"], r["mode"], "| base stderr:", r["stderr_tail"][-120:].replace("\n", " "))
print(json.dumps({"a": {k: ra[k] for k in ("S_top8", "S_top8_90", "S_rand", "S_diff_90", "r_c_over_r_l", "ratio_90", "verdict")},
                  "b": {k: rb[k] for k in ("top8_Q", "top8_Q_90", "top8_Q_base", "top8_Q_diff_90", "top8_verdict")}}, indent=1))
