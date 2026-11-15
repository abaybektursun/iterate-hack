"""r5-m06 prediction 2: A - B, A = solved / n over the RL-solved base-0/4 problems (rl_k >= 1), B = solved / n over the RL-never
base-0/4 problems (rl_k == 0), pool (a)-(f) and rules of prediction 1, divided by the actual class sizes. alt_measured: the same
without source (d) (frustea e383 reuses the per-request seed of Day-1 #3 sample 0)."""
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(os.getcwd())
R = ROOT / "studies/rlneurons/results"
CACHE = ROOT / "runs/theory-tests"
F_PATH = CACHE / "s3/F_math500.jsonl"
E383_PATH = CACHE / "frustea-1114-180853-e383/answers.jsonl"
RANDOM_JOB = "abaybektursun-1114-153047-6429"
SHOTS_JOB = "abaybektursun-1114-183855-e840"


def fetch():
    if not F_PATH.exists():
        F_PATH.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/F_math500.jsonl",
                        str(F_PATH), "--profile", "iterate-ecr", "--only-show-errors"], check=False)
    if not E383_PATH.exists():
        E383_PATH.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", "frustea-1114-180853-e383/answers.jsonl", str(E383_PATH)], check=False)
    missing = [str(p) for p in (F_PATH, E383_PATH) if not p.exists() or p.stat().st_size == 0]
    return missing


def classes():
    probs = json.load(open(R / "anatomy/math500-01/pool_k_le3.json"))["problems"]
    rl_solved = sorted(p["index"] for p in probs if p["base_k"] == 0 and p["rl_k"] >= 1)
    rl_never = sorted(p["index"] for p in probs if p["base_k"] == 0 and p["rl_k"] == 0)
    return rl_solved, rl_never


def build_pool(targets):
    """Return {problem_index: [(source, score 0/1, row dict), ...]} over sources (a)-(f)."""
    from studies.rlneurons.lib import rln4_lib
    t = set(targets)
    pool = {i: [] for i in targets}

    # (a) Day-1 #3 base cue rows, attempt in {1, 2}, stored score_v3 (cap hits keep their stored score)
    for line in open(R / "day1_3/math500_base_cue-01/rows.jsonl"):
        r = json.loads(line)
        if r["problem_index"] in t and r.get("attempt") in (1, 2):
            pool[r["problem_index"]].append(("a_day1_3_attempt12", 1 if r["score_v3"] == 1 else 0, r))

    # (b), (c) axis vectors.json arms chosen by job id in manifest.json
    man = json.load(open(R / "axis/math500-01/manifest.json"))["arms"]
    vec = json.load(open(R / "axis/math500-01/vectors.json"))
    pos = {p: k for k, p in enumerate(vec["problem_indices"])}
    for tag, job in (("b_random_cue", RANDOM_JOB), ("c_shots_base", SHOTS_JOB)):
        names = [n for n, a in man.items() if a.get("job_id") == job]
        assert len(names) == 1, (job, names)
        v = vec["arms"][names[0]]
        for i in targets:
            if i not in pos:
                continue
            x = v[pos[i]]
            if x is None:  # problem not scored in this arm (shots examples 0-2): absent
                continue
            pool[i].append((tag, 1 if x == 1 else 0, {"arm": names[0], "job_id": job, "problem_index": i, "score_v3": x}))

    # (d) frustea e383 answers, attempt 0 or no attempt field, stored score_v3
    for line in open(E383_PATH):
        r = json.loads(line)
        if r["problem_index"] in t and r.get("attempt", 0) == 0:
            pool[r["problem_index"]].append(("d_e383", 1 if r.get("score_v3") == 1 else 0, r))

    # (e) r3 base-01 F_math500, every row, v3 recomputed from text and gold (grader/rln4_grader_v3.py calls rln4_lib.grade_v3)
    for line in open(F_PATH):
        r = json.loads(line)
        if r["problem_index"] in t:
            g = rln4_lib.grade_v3(r["gold"], r["text"])
            pool[r["problem_index"]].append(("e_F_math500", 1 if g["score_v3"] == 1 else 0, dict(r, **{"recomputed_" + k: v for k, v in g.items()})))

    # (f) wsp1 screen100 base_cue per_problem.json score_v3 (problems 0-99)
    for r in json.load(open(R / "wsp1/screen100/base_cue-01/per_problem.json")):
        if r["problem_index"] in t:
            pool[r["problem_index"]].append(("f_wsp1_base_cue", 1 if r.get("score_v3") == 1 else 0, r))
    return pool


def slim(row):
    out = {}
    for k, v in row.items():
        if k in ("answer_tokens", "prompt", "prefill_ids"):
            continue
        if isinstance(v, str) and len(v) > 600:
            v = v[:300] + " ... " + v[-300:]
        out[k] = v
    return out


def solved_fraction(pool, targets, drop=()):
    solved = [i for i in targets if any(s == 1 for src, s, _ in pool[i] if src not in drop)]
    return solved


def main():
    missing = fetch()
    if missing:
        print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                          "not_computable": "row file not readable: " + ", ".join(missing), "example_row": None}))
        return
    rl_solved, rl_never = classes()
    if not rl_solved or not rl_never:
        print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                          "not_computable": f"empty class: rl_solved {len(rl_solved)}, rl_never {len(rl_never)}", "example_row": None}))
        return
    pool = build_pool(rl_solved + rl_never)
    sa, sb = solved_fraction(pool, rl_solved), solved_fraction(pool, rl_never)
    sa2, sb2 = solved_fraction(pool, rl_solved, drop=("d_e383",)), solved_fraction(pool, rl_never, drop=("d_e383",))
    measured = len(sa) / len(rl_solved) - len(sb) / len(rl_never)
    alt = len(sa2) / len(rl_solved) - len(sb2) / len(rl_never)
    ex = None
    for i in rl_never + rl_solved:
        for src, s, row in pool[i]:
            if s == 1:
                ex = dict(slim(row), _source=src, _score_used=s)
                break
        if ex:
            break
    if ex is None:
        for i in rl_solved + rl_never:
            if pool[i]:
                src, s, row = pool[i][0]
                ex = dict(slim(row), _source=src, _score_used=s)
                break
    print(f"n_A={len(rl_solved)} n_B={len(rl_never)} solved_A={sa} solved_B={sb} alt_A={sa2} alt_B={sb2}", file=sys.stderr)
    print(json.dumps({"measured": measured, "refuted_by_met": bool(measured <= 0.0), "alt_measured": alt,
                      "not_computable": None, "example_row": ex}))


if __name__ == "__main__":
    main()
