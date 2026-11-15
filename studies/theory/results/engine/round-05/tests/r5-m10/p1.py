"""r5-m10 prediction 1: D = A - B.
A = mean grader-v3 score of self-opened T3 (plain base, T 1.0) rows; B = mean t1_right (cued base) on the same problems.
Self-opened (main): text[:60] contains '\\nOkay' (newline immediately followed by 'Okay').
alt_measured: same D with self-opened = an occurrence of newline, optional whitespace, 'Okay' that STARTS within the first
60 characters (regex r'\\n\\s*Okay', match start < 60), i.e. 'contain' read as 'begins within the window'.
"""
import json
import pathlib
import re
import subprocess

from studies.rlneurons.lib import rln4_lib as R

ROOT = pathlib.Path.cwd()
T3_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
T3 = ROOT / "runs/theory-tests/s3/T3.jsonl"
PP = ROOT / "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"


def nc(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None, "not_computable": reason, "example_row": None}))
    raise SystemExit(0)


def fetch():
    if not T3.exists():
        T3.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", T3_S3, str(T3), "--profile", "iterate-ecr"], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not T3.exists():
        nc("T3.jsonl could not be fetched from S3")
    if not PP.exists():
        nc("per_problem.json not found")


def self_open_main(text):
    return "\nOkay" in text[:60]


ALT_RE = re.compile(r"\n\s*Okay")


def self_open_alt(text):
    m = ALT_RE.search(text)
    return m is not None and m.start() < 60


def trunc(r):
    r = dict(r)
    if isinstance(r.get("text"), str) and len(r["text"]) > 400:
        r["text"] = r["text"][:400] + "...[truncated]"
    return r


def main():
    fetch()
    t3 = {}
    for line in T3.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            t3.setdefault(r["problem_index"], []).append(r)
    pp = {}
    for e in json.loads(PP.read_text()):
        pp.setdefault(e["problem_index"], []).append(e)
    for k, v in t3.items():
        if len(v) != 1:
            nc(f"T3 has {len(v)} rows for problem_index {k}; recipe assumes one sample per problem")
    for k, v in pp.items():
        if len(v) != 1:
            nc(f"per_problem.json has {len(v)} entries for problem_index {k}")
    for v in t3.values():
        for f in ("text", "gold", "problem_index"):
            if f not in v[0]:
                nc(f"T3 row lacks field {f}")
    for v in pp.values():
        if "t1_right" not in v[0]:
            nc("per_problem.json entry lacks t1_right")

    scores = {}
    for k, v in t3.items():
        r = v[0]
        text = r["text"] if isinstance(r["text"], str) else ""
        scores[k] = R.grade_v3(r["gold"], text)["score_v3"]  # None extraction -> 0 inside grade_v3; cap hits keep score

    def D(pred):
        S = [k for k, v in t3.items() if isinstance(v[0]["text"], str) and pred(v[0]["text"])]
        S = [k for k in S if k in pp and pp[k][0]["t1_right"] is not None]
        if not S:
            return None, S
        A = sum(scores[k] for k in S) / len(S)
        B = sum(float(pp[k][0]["t1_right"]) for k in S) / len(S)
        return A - B, S

    d, S = D(self_open_main)
    d_alt, _ = D(self_open_alt)
    if d is None:
        nc("no self-opened T3 rows present in both files (empty S); refuted_by is not defined for an empty group")
    k0 = sorted(S)[0]
    ex = trunc(t3[k0][0])
    ex["_v3_score"] = scores[k0]
    ex["_per_problem_entry"] = pp[k0][0]
    refuted = (d < -0.10) or (d > 0.08)
    print(json.dumps({"n_S": len(S), "A_minus_B": d}))
    print(json.dumps({"measured": d, "refuted_by_met": bool(refuted), "alt_measured": d_alt, "not_computable": None, "example_row": ex}))


if __name__ == "__main__":
    main()
