"""r5-m09 prediction 4: base share of numeric finished-wrong finals (attempt 0) equal to a problem-statement number,
minus the share of numeric golds (one per problem, first attempt-0 base row) equal to one (prompts from 456c)."""
import json
import os
import re
import subprocess

BASE = "studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl"
JOB = "frustea-1114-180849-456c"
PROMPTS_ROWS = f"runs/theory-rows/{JOB}/answers.jsonl"     # where the recipe says it was fetched
PROMPTS_TESTS = f"runs/theory-tests/{JOB}/answers.jsonl"   # where this script fetches it if missing

NUM_RE = re.compile(r"\d+(?:\.\d+)?")
NUMERIC_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
SUFFIXES = ("^{\\circ}", "^\\circ", "\\%", "%")


class NC(Exception):
    pass


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))


def prompts_path():
    for p in (PROMPTS_ROWS, PROMPTS_TESTS):
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    os.makedirs(os.path.dirname(PROMPTS_TESTS), exist_ok=True)
    try:
        subprocess.run(["modal", "volume", "get", "iterate-runs", f"{JOB}/answers.jsonl", PROMPTS_TESTS],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        raise NC(f"could not fetch iterate-runs:{JOB}/answers.jsonl ({e})")
    if not os.path.exists(PROMPTS_TESTS):
        raise NC(f"iterate-runs:{JOB}/answers.jsonl not readable")
    return PROMPTS_TESTS


def load_problem_numbers(alt_commas=False):
    """Prompt of the first row per problem_index; all regex matches; drop number strings present in all prompts.
    alt_commas: also read thousands-separated numbers (1,000 -> 1000) before the regex, as the answers lose commas."""
    path = prompts_path()
    first = {}
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if "problem_index" not in r or "prompt" not in r:
            raise NC(f"{JOB} rows lack problem_index or prompt")
        i = r["problem_index"]
        if i not in first:
            first[i] = r["prompt"]
    nums = {}
    for i, p in first.items():
        if alt_commas:
            p = re.sub(r"(?<![\d.])\d{1,3}(?:,\d{3})+(?![\d])", lambda m: m.group(0).replace(",", ""), p)
        nums[i] = set(NUM_RE.findall(p))
    if not nums:
        raise NC("no prompts")
    common = set.intersection(*nums.values())  # number strings present in every prompt
    return {i: [float(s) for s in (v - common)] for i, v in nums.items()}, len(first)


def normalize(s):
    s = re.sub(r"\s+", "", s).replace("$", "").replace(",", "")
    for suf in SUFFIXES:
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    return s


def numeric_value(s):
    if not isinstance(s, str):
        return None
    n = normalize(s)
    if NUMERIC_RE.fullmatch(n):
        return float(n)
    return None


def matches(v, numbers):
    a = abs(v)
    return any(abs(a - x) <= 1e-9 for x in numbers)


def load_rows(path):
    if not os.path.exists(path):
        raise NC(f"{path} not found")
    rows = [json.loads(l) for l in open(path) if l.strip()]
    need = ("problem_index", "attempt", "cap_hit", "score_v3", "extracted_v3")
    if not rows or any(k not in rows[0] for k in need):
        raise NC(f"{path} lacks one of {need}")
    return rows


def finished_wrong(r):
    return (r["attempt"] == 0 and r["cap_hit"] is False and r["score_v3"] == 0
            and isinstance(r["extracted_v3"], str) and len(r["extracted_v3"]) > 0)


def share(rows, numbers):
    m = n = 0
    ex = None
    for r in rows:
        if not finished_wrong(r):
            continue
        if r["problem_index"] not in numbers:
            continue
        v = numeric_value(r["extracted_v3"])
        if v is None:
            continue
        n += 1
        if ex is None:
            ex = r
        if matches(v, numbers[r["problem_index"]]):
            m += 1
    return m, n, ex


def gold_share(rows, numbers):
    """One gold per problem_index: the first attempt-0 row of the base file (file order)."""
    seen = set()
    m = n = 0
    for r in rows:
        if r["attempt"] != 0 or r["problem_index"] in seen:
            continue
        seen.add(r["problem_index"])
        if r["problem_index"] not in numbers:
            continue
        v = numeric_value(r.get("gold"))
        if v is None:
            continue
        n += 1
        if matches(v, numbers[r["problem_index"]]):
            m += 1
    return m, n


def main():
    try:
        base = load_rows(BASE)
        if "gold" not in base[0]:
            raise NC(f"{BASE} lacks the field gold")
        numbers, _ = load_problem_numbers()
        numbers_alt, _ = load_problem_numbers(alt_commas=True)
    except NC as e:
        return out(None, False, None, str(e), None)
    bm, bn, ex = share(base, numbers)
    gm, gn = gold_share(base, numbers)
    if bn == 0 or gn == 0:
        return out(None, False, None, f"empty group: base numeric finished-wrong {bn}, numeric golds {gn}", None)
    measured = bm / bn - gm / gn
    abm, abn, _ = share(base, numbers_alt)
    agm, agn = gold_share(base, numbers_alt)
    alt = (abm / abn - agm / agn) if abn and agn else None
    out(measured, measured < 0.05, alt, None, ex)


main()
