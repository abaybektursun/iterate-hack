"""r5-m10 prediction 2: R = median n_generated of self-opened T3 rows / median t1_generated_tokens on the same problems.
Self-opened (main): text[:60] contains '\\nOkay'. S restricted to problems present in per_problem.json. Cap hits at their length.
Even count -> mean of the two middle values.
alt_measured: same R with self-opened = regex r'\\n\\s*Okay' match starting within the first 60 characters.
"""
import json
import pathlib
import re
import subprocess

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


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n % 2:
        return float(xs[n // 2])
    return (xs[n // 2 - 1] + xs[n // 2]) / 2.0


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
        if "n_generated" not in v[0] or "text" not in v[0]:
            nc("T3 row lacks n_generated or text")
    for k, v in pp.items():
        if len(v) != 1:
            nc(f"per_problem.json has {len(v)} entries for problem_index {k}")
        if "t1_generated_tokens" not in v[0]:
            nc("per_problem.json entry lacks t1_generated_tokens")

    def ratio(pred):
        S = [k for k, v in t3.items() if isinstance(v[0]["text"], str) and pred(v[0]["text"]) and k in pp
             and v[0]["n_generated"] is not None and pp[k][0]["t1_generated_tokens"] is not None]
        if not S:
            return None, S
        num = median([t3[k][0]["n_generated"] for k in S])
        den = median([pp[k][0]["t1_generated_tokens"] for k in S])
        if den == 0:
            return None, S
        return num / den, S

    R, S = ratio(self_open_main)
    R_alt, _ = ratio(self_open_alt)
    if R is None:
        nc("empty S (no self-opened T3 rows in per_problem.json) or zero denominator median")
    k0 = sorted(S)[0]
    ex = trunc(t3[k0][0])
    ex["_per_problem_entry"] = pp[k0][0]
    refuted = (R < 0.70) or (R > 1.40)
    print(json.dumps({"n_S": len(S)}))
    print(json.dumps({"measured": R, "refuted_by_met": bool(refuted), "alt_measured": R_alt, "not_computable": None, "example_row": ex}))


if __name__ == "__main__":
    main()
