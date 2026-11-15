"""Prediction 20: on math500-rl-T1 gap problems (per_problem t2_right true, t1_right false), theta0.5-cue (683b)
fix rate on the reliability part minus its fix rate on the budget part.
Main: literal R3. alt_measured: R3 read as 'a line containing Answer: anywhere is an answer line'.
Undefined if either part is empty (reported as not computable). In bootstrap resamples where a part is empty its fix
rate is taken as 0 (the helper needs a number for every resample).
refuted_by: computed difference below 0.05.
"""
import json
import os
import re
import subprocess
import sys
import zlib

from studies.theory.lib.noise import bootstrap, binomial, report, not_computable, refuted_without_number

TESTS = os.path.join(os.getcwd(), "runs", "theory-tests")
S3 = "s3://pg-lineage-769063704696/results/rlneurons/"


class Missing(Exception):
    pass


def fetch_s3(key, local):
    path = os.path.join(TESTS, local)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", S3 + key, path, "--profile", "iterate-ecr", "--only-show-errors"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            raise Missing("cannot fetch " + S3 + key + ": " + r.stderr.strip()[:300])
    return path


def fetch_vol(remote, local):
    path = os.path.join(TESTS, local)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run(["modal", "volume", "get", "iterate-runs", remote, path], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            raise Missing("cannot fetch iterate-runs:" + remote + ": " + (r.stderr or r.stdout).strip()[:300])
    return path


def repo_file(rel):
    path = os.path.join(os.getcwd(), rel)
    if not os.path.exists(path):
        raise Missing("file not found: " + rel)
    return path


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def first_by(rows, key, keep=lambda r: True):
    """First row per value of `key` among rows passing `keep`; rows without the key are skipped."""
    out = {}
    for r in rows:
        if key in r and r[key] is not None and keep(r) and r[key] not in out:
            out[r[key]] = r
    return out


def is_cap(row):
    """cap_hit true, or cap_hit missing and finish_reason == 'length'."""
    c = row.get("cap_hit")
    if c is None:
        return row.get("finish_reason") == "length"
    return c is True


def rule_a(text):
    """Rule A: p = 0 or right after a '\\n', with >= 8,000 characters from p to the end; w = text[p:p+8000];
    fires if any zlib(default level) compressed/raw byte ratio of w < 0.10. Missing or shorter text: no."""
    if not isinstance(text, str) or len(text) < 8000:
        return False
    positions = [0] + [i + 1 for i, c in enumerate(text) if c == "\n"]
    for p in positions:
        if len(text) - p < 8000:
            break
        b = text[p:p + 8000].encode("utf-8")
        if len(zlib.compress(b)) / len(b) < 0.10:
            return True
    return False


_WS = re.compile(r"\s")


def N(s):
    s = _WS.sub("", s)
    for t in ("$", "*", "#", "\\left", "\\right"):
        s = s.replace(t, "")
    return s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")


def r3_takes(text, gold):
    """Main (literal) reading of R3 on normalized lines."""
    if not isinstance(text, str):
        return True
    g = N(gold if isinstance(gold, str) else ("" if gold is None else str(gold)))
    lines = [N(l) for l in text.split("\n")]
    no_marker = not any("\\boxed{" in l for l in lines) and not any(l.startswith("Answer:") for l in lines)
    match = any(("\\boxed{" + g + "}") in l for l in lines) or any(l == "Answer:" + g or l == "Answer:" + g + "." for l in lines)
    return no_marker or match


def r3_takes_alt(text, gold):
    """Other reading: an answer line is any normalized line that CONTAINS 'Answer:' (e.g. 'FinalAnswer:'), and it
    matches if what follows its last 'Answer:' equals g or g + '.'."""
    if not isinstance(text, str):
        return True
    g = N(gold if isinstance(gold, str) else ("" if gold is None else str(gold)))
    lines = [N(l) for l in text.split("\n")]
    no_marker = not any("\\boxed{" in l for l in lines) and not any("Answer:" in l for l in lines)
    match = any(("\\boxed{" + g + "}") in l for l in lines) or any(
        "Answer:" in l and l.rsplit("Answer:", 1)[1] in (g, g + ".") for l in lines)
    return no_marker or match


def assign(cap, text, gold, e_rights, alt=False):
    """Ordered rules R1..R5; e_rights is the list of right/wrong flags of the rows in E."""
    kb = sum(1 for x in e_rights if x)
    if cap and rule_a(text):
        return "loop"
    if cap:
        return "budget"
    if (r3_takes_alt if alt else r3_takes)(text, gold):
        return "answer-statement"
    if kb >= 1:
        return "reliability"
    if len(e_rights) > 0 and kb == 0:
        return "capability"
    return "unassigned"


def slim(row):
    if row is None:
        return None
    out = {k: v for k, v in row.items() if k not in ("text", "prompt")}
    if "text" in row:
        out["text_chars"] = len(row["text"]) if isinstance(row["text"], str) else None
    return out


def e_math500_cue(day1_rows):
    """E for MATH-500: day1_3 base_cue rows, attempt == 0, sample in {0,1,2,3}, first row per (problem_index, sample);
    right = score_v3 == 1 (null wrong). Returns {problem_index: [(sample, right), ...]}."""
    seen = set()
    out = {}
    for r in day1_rows:
        if r.get("attempt") != 0 or r.get("sample") not in (0, 1, 2, 3) or r.get("problem_index") is None:
            continue
        key = (r["problem_index"], r["sample"])
        if key in seen:
            continue
        seen.add(key)
        out.setdefault(r["problem_index"], []).append(r.get("score_v3") == 1)
    return out


def build():
    pp = json.load(open(repo_file("studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"), encoding="utf-8"))
    t1 = load_jsonl(fetch_s3("r4/base_rl-02/out/T1.jsonl", "r4_base_rl-02_T1.jsonl"))
    day1 = load_jsonl(repo_file("studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"))
    th = load_jsonl(fetch_vol("abaybektursun-1114-152855-683b/answers.jsonl", "683b/answers.jsonl"))
    ppm, t1m, thm, E = first_by(pp, "problem_index"), first_by(t1, "problem_index"), first_by(th, "problem_index"), e_math500_cue(day1)
    items = []
    for pi in sorted(ppm):
        p = ppm[pi]
        t1r, t2r = p.get("t1_right"), p.get("t2_right")
        if t1r is None or t2r is None or not (t2r == True and t1r == False):
            continue
        b = t1m.get(pi)
        cap = p.get("t1_cap_hit") == True
        text = b.get("text") if b is not None else None
        gold = b.get("gold") if b is not None else None
        er = E.get(pi, [])
        r = thm.get(pi)
        fixed = r is not None and r.get("score_v3") == 1
        ex = {"problem_index": pi, "per_problem": p, "B_T1_row": slim(b), "E_rights": er, "theta05_row": slim(r)}
        items.append((assign(cap, text, gold, er), assign(cap, text, gold, er, alt=True), fixed, ex))
    return items


def diff(sample, idx, empty_as_zero):
    rel = [it[2] for it in sample if it[idx] == "reliability"]
    bud = [it[2] for it in sample if it[idx] == "budget"]
    if not rel or not bud:
        if not empty_as_zero:
            return None
    fr = (sum(rel) / len(rel)) if rel else 0.0
    fb = (sum(bud) / len(bud)) if bud else 0.0
    return fr - fb


def main():
    try:
        items = build()
    except Missing as e:
        not_computable(str(e))
        return
    m = diff(items, 0, False)
    if m is None:
        not_computable("reliability part or budget part is empty on the gap problems; the recipe says undefined")
        return
    alt = diff(items, 1, False)
    n_used = sum(1 for it in items if it[0] in ("reliability", "budget"))
    ex = next(it[3] for it in items if it[0] == "reliability")
    report(m, len(items), bootstrap(lambda s: diff(s, 0, True), items), "bootstrap", refuted_by_met=(m < 0.05),
           alt_measured=alt, example_row=dict(ex, n_problems_in_reliability_or_budget=n_used))


main()
