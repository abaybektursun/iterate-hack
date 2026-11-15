"""r4-m07 offline prediction 5: hard328, base cue (e72c) vs RL plain (86ef), one sample each;
among problems where both rows are wrong and finished, share with identical normalised answers."""
import json
import os
import subprocess

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01/"
JOBS = {"base": "abaybektursun-1114-151534-e72c", "rl": "abaybektursun-1114-151540-86ef"}


def out(d):
    print(json.dumps(d))


def nc(reason):
    out({"measured": None, "refuted_by_met": False, "alt_measured": None,
         "not_computable": reason, "example_row": None})


def norm(s):
    if s is None:
        return ""
    s = "".join(s.split())
    s = s.strip("$")
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    s = s.replace("\\left", "").replace("\\right", "")
    if s.endswith("."):
        s = s[:-1]
    return s


def fetch(job):
    local = "runs/theory-tests/%s/answers.jsonl" % job
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3 + job + "/answers.jsonl", local,
                        "--profile", "iterate-ecr", "--only-show-errors"], check=False)
    return local if os.path.exists(local) else None


def load(path):
    rows = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                if r["problem_index"] in rows:
                    raise ValueError("duplicate problem_index %s in %s" % (r["problem_index"], path))
                rows[r["problem_index"]] = r
    return rows


def wrong(r, require_finished=True):
    if require_finished and r.get("cap_hit") is not False:
        return None
    a = norm(r.get("extracted_v3"))
    if a == "" or r.get("score_v3") != 0:
        return None
    return a


def stat(b, rl, require_finished):
    num = den = 0
    ex = None
    for p in sorted(set(b) & set(rl)):
        a1 = wrong(b[p], require_finished)
        a2 = wrong(rl[p], require_finished)
        if a1 is None or a2 is None:
            continue
        den += 1
        if a1 == a2:
            num += 1
            if ex is None:
                ex = {"problem_index": p, "base_extracted_v3": b[p]["extracted_v3"],
                      "rl_extracted_v3": rl[p]["extracted_v3"], "gold": b[p].get("gold"),
                      "base_cap_hit": b[p]["cap_hit"], "rl_cap_hit": rl[p]["cap_hit"],
                      "base_score_v3": b[p]["score_v3"], "rl_score_v3": rl[p]["score_v3"]}
        elif ex is None and num == 0 and den == 1:
            first = {"problem_index": p, "base_extracted_v3": b[p]["extracted_v3"],
                     "rl_extracted_v3": rl[p]["extracted_v3"], "gold": b[p].get("gold"),
                     "base_cap_hit": b[p]["cap_hit"], "rl_cap_hit": rl[p]["cap_hit"],
                     "base_score_v3": b[p]["score_v3"], "rl_score_v3": rl[p]["score_v3"]}
    if ex is None and den > 0:
        ex = first
    return num, den, ex


def main():
    paths = {}
    for k, j in JOBS.items():
        p = fetch(j)
        if p is None:
            return nc("could not fetch %s answers.jsonl" % j)
        paths[k] = p
    try:
        b = load(paths["base"])
        rl = load(paths["rl"])
    except (ValueError, KeyError) as e:
        return nc("row format problem: %s" % e)
    for rows in (b, rl):
        for k in ("cap_hit", "extracted_v3", "score_v3"):
            if any(k not in r for r in rows.values()):
                return nc("field missing: " + k)
    num, den, ex = stat(b, rl, True)
    if den == 0:
        return nc("no problem where both rows are wrong and finished (denominator 0)")
    measured = num / den
    # alt: 'wrong' without the cap_hit filter (any non-empty extracted answer scored 0)
    n2, d2, _ = stat(b, rl, False)
    alt = n2 / d2 if d2 else None
    out({"measured": measured, "refuted_by_met": measured < 0.20, "alt_measured": alt,
         "not_computable": None, "example_row": ex, "numerator": num, "denominator": den})


main()
