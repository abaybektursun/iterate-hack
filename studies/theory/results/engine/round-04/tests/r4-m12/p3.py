"""r4-m12 prediction 3: exact-string match to gold among v3-right answers, RL (86ef) minus base cue (e72c),
on non-integer-gold problems that both models got right under v3.

Main: indicator = N(extracted_v3) == N(gold) as strings (N as in recipe 1).
Alt:  indicator = raw extracted_v3.strip() == raw gold.strip() (no normalisation), same kept set.
"""
import json
import os
import re
import subprocess

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01"
JOBS = {
    "e72c": "abaybektursun-1114-151534-e72c",  # base cue
    "86ef": "abaybektursun-1114-151540-86ef",  # RL plain
}
LOCAL = "runs/theory-tests/r4m12"


def not_computable(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                      "not_computable": reason, "example_row": None}))
    raise SystemExit(0)


def fetch(job):
    path = os.path.join(LOCAL, job, "answers.jsonl")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    r = subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{job}/answers.jsonl", path,
                        "--profile", "iterate-ecr", "--only-show-errors"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(path):
        r2 = subprocess.run(["modal", "volume", "get", "iterate-runs", f"{job}/answers.jsonl", path],
                            capture_output=True, text=True)
        if r2.returncode != 0 or not os.path.exists(path):
            not_computable(f"cannot fetch {job}/answers.jsonl: aws: {r.stderr.strip()[:200]}; "
                           f"modal: {r2.stderr.strip()[:200]}")
    return path


def load(path):
    rows = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            rows[d["problem_index"]] = d  # one row per problem in these files
    return rows


def strip_boxed(s):
    """If s is entirely \\boxed{...}, return the inside, else s."""
    t = s.strip()
    if not t.startswith("\\boxed{"):
        return s
    depth = 0
    start = len("\\boxed{") - 1
    for i in range(start, len(t)):
        c = t[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                if i == len(t) - 1:
                    return t[start + 1:i]
                return s
    return s


def N(s):
    if s is None:
        return ""
    s = str(s)
    s = strip_boxed(s)
    s = s.replace("$", "")
    s = re.sub(r"\s+", "", s)
    for tok in ["\\left", "\\right", "\\displaystyle", "\\,", "\\!", "\\;", "^\\circ", "^{\\circ}"]:
        s = s.replace(tok, "")
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    if s.endswith("."):
        s = s[:-1]
    if "=" in s and not any(x in s for x in ["<", ">", "\\le", "\\ge"]):
        s = s.split("=")[-1]
    return s


INT_RE = re.compile(r"^-?\d+$")


def score1(d):
    v = d.get("score_v3")
    try:
        return v is not None and float(v) == 1.0
    except (TypeError, ValueError):
        return False


def main():
    paths = {k: fetch(j) for k, j in JOBS.items()}
    try:
        base = load(paths["e72c"])
        rl = load(paths["86ef"])
    except Exception as e:  # noqa: BLE001
        not_computable(f"cannot read answers.jsonl: {e}")

    for name, rows in (("e72c", base), ("86ef", rl)):
        if not rows:
            not_computable(f"{name} answers.jsonl is empty")
        sample = next(iter(rows.values()))
        for fld in ("problem_index", "gold", "extracted_v3", "score_v3"):
            if fld not in sample:
                not_computable(f"{name} rows lack field {fld}")

    common = sorted(set(base) & set(rl))  # missing from either file -> dropped
    kept = []
    for pi in common:
        b, r = base[pi], rl[pi]
        gold = b.get("gold")
        if INT_RE.match(N(gold)):
            continue
        if score1(b) and score1(r):
            kept.append(pi)

    if not kept:
        not_computable("no non-integer-gold problem is v3-right in both files; the difference of means is undefined")

    def ind_main(d):
        ex = d.get("extracted_v3")
        if ex is None or str(ex) == "":
            return 0
        return 1 if N(ex) == N(d.get("gold")) else 0

    def ind_alt(d):
        ex = d.get("extracted_v3")
        if ex is None or str(ex) == "":
            return 0
        return 1 if str(ex).strip() == str(d.get("gold")).strip() else 0

    n = len(kept)
    rl_main = sum(ind_main(rl[pi]) for pi in kept) / n
    base_main = sum(ind_main(base[pi]) for pi in kept) / n
    rl_alt = sum(ind_alt(rl[pi]) for pi in kept) / n
    base_alt = sum(ind_alt(base[pi]) for pi in kept) / n
    measured = rl_main - base_main
    alt = rl_alt - base_alt

    ex = base[kept[0]]
    example = {k: ex.get(k) for k in ("problem_index", "unique_id", "gold", "extracted_v3", "score_v3",
                                      "cap_hit", "model", "prompt_arm")}
    example["N_gold"] = N(ex.get("gold"))
    example["N_extracted_v3"] = N(ex.get("extracted_v3"))

    print(f"kept problems: {n}; RL exact-match mean {rl_main:.4f}; base exact-match mean {base_main:.4f}; "
          f"alt (raw strings) RL {rl_alt:.4f} base {base_alt:.4f}")
    print(json.dumps({"measured": measured, "refuted_by_met": measured < 0.01, "alt_measured": alt,
                      "not_computable": None, "example_row": example}))


if __name__ == "__main__":
    main()
