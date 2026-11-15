"""Prediction 12: Share of hard328-code-T1 gap problems no rule takes.
Main: share of gap problems assigned to part 'unassigned' by the ordered rules R1-R5 (literal R3).
alt_measured: the same share with R3 read as 'a line containing Answer: anywhere (e.g. Final Answer:) is an answer line'.
refuted_by: computed share above 0.03.
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
    e72 = load_jsonl(fetch_s3("r5/day1_hard328-01/abaybektursun-1114-151534-e72c/answers.jsonl", "r5_day1_hard328-01_e72c.jsonl"))
    a619 = load_jsonl(fetch_s3("r5/day1_wdiff328-01/abaybektursun-1114-181216-a619/answers.jsonl", "r5_day1_wdiff328-01_a619.jsonl"))
    fh = load_jsonl(fetch_s3("r3/base-01/out/F_hard.jsonl", "r3_base-01_F_hard.jsonl"))
    ph = load_jsonl(fetch_s3("r3/base-01/out/P_hard.jsonl", "r3_base-01_P_hard.jsonl"))
    b7 = load_jsonl(fetch_s3("r5/day1_hard328-01/abaybektursun-1114-132922-7ba0/answers.jsonl", "r5_day1_hard328-01_7ba0.jsonl"))
    em, am, b7m = first_by(e72, "problem_index"), first_by(a619, "problem_index"), first_by(b7, "problem_index")
    fhu, phu = first_by(fh, "unique_id"), first_by(ph, "unique_id")
    items = []
    for pi in sorted(set(em) & set(am)):
        if not (am[pi].get("score_v3") == 1 and em[pi].get("score_v3") != 1):   # null counts as wrong
            continue
        b = em[pi]
        cap = is_cap(b)
        uid = b.get("unique_id")
        er = []
        if uid is not None and uid in fhu:
            er.append(fhu[uid].get("score") == 1)
        if uid is not None and uid in phu:
            er.append(phu[uid].get("score") == 1)
        if pi in b7m:
            er.append(b7m[pi].get("score_v3") == 1)
        ex = {"problem_index": pi, "B_e72c_row": slim(b), "code_a619_row": slim(am[pi]), "E_rights": er}
        items.append((assign(cap, b.get("text"), b.get("gold"), er), assign(cap, b.get("text"), b.get("gold"), er, alt=True), ex))
    return items


PART = 'unassigned'


def main():
    try:
        items = build()
    except Missing as e:
        not_computable(str(e))
        return
    if not items:
        not_computable("no gap problems; the share has a zero denominator")
        return

    def stat(sample):
        return sum(1 for it in sample if it[0] == PART) / len(sample)

    def stat_alt(sample):
        return sum(1 for it in sample if it[1] == PART) / len(sample)

    m = stat(items)
    ex = next((it[2] for it in items if it[0] == PART), items[0][2])
    report(m, len(items), bootstrap(stat, items), "bootstrap", refuted_by_met=(m > 0.03),
           alt_measured=stat_alt(items), example_row=ex)


main()
