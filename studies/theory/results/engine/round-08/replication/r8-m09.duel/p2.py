"""k=2: median n_new of Think-SFT layout-miss rows / median n_new of all finished Think-SFT rows (8 files pooled).

Layout row (first recipe of the theory file): first row per problem_index per file; finished = cap_hit not true and
finish_reason != 'length'; wrong = score_v3 != 1 (null/missing = wrong); candidate C after the last 'Answer:' (else last
non-empty line), cleaned; counts if C non-empty and rln4_lib.agree(C, gold).
"""
import json
import os
import subprocess

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable

JOBS = [("hard328", "abaybektursun-1115-000503-1e5f"), ("hard328", "abaybektursun-1115-000525-ea4e"),
        ("hard328", "abaybektursun-1115-014823-ef56"), ("hard328", "abaybektursun-1115-014833-1daa"),
        ("math500", "abaybektursun-1115-000512-ee03"), ("math500", "abaybektursun-1115-014843-85d9"),
        ("math500", "abaybektursun-1115-000607-0e92"), ("math500", "abaybektursun-1115-000621-1d7e")]


def fetch(job):
    path = os.path.join("runs", "theory-tests", job, "answers.jsonl")
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "--force", "iterate-runs", f"{job}/answers.jsonl", path], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    return path


def last_boxed_content(s):
    i = s.rfind("\\boxed{")
    j = i + len("\\boxed{")
    depth, out = 1, []
    while j < len(s):
        ch = s[j]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        out.append(ch)
        j += 1
    return "".join(out)   # unclosed box: everything after '\boxed{'


def candidate(text):
    text = text or ""
    if "Answer:" in text:
        s = text[text.rfind("Answer:") + len("Answer:"):]
        parts = [p for p in s.split("\n") if p.strip()]
        return parts[0] if parts else ""
    parts = [p for p in text.split("\n") if p.strip()]
    return parts[-1] if parts else ""


def clean(c, loose=False):
    c = c.strip()
    c = c.replace("$", "").replace("*", "")
    if loose:
        c = c.strip()
    for p in ("\\[", "\\("):
        if c.startswith(p):
            c = c[len(p):]
            break
    if loose:
        c = c.strip()
    for p in ("\\]", "\\)"):
        if c.endswith(p):
            c = c[:-len(p)]
            break
    if loose:
        c = c.strip().rstrip(".").strip()
    elif c.endswith("."):
        c = c[:-1]
    if "\\boxed{" in c:
        c = last_boxed_content(c)
        if loose:
            c = c.strip()
    return c


def is_finished(r):
    return r.get("cap_hit") is not True and r.get("finish_reason") != "length"


def is_layout(r, loose=False):
    if not is_finished(r) or r.get("score_v3") == 1:
        return False
    c = clean(candidate(r.get("text")), loose)
    return bool(c) and rln4_lib.agree(c, r.get("gold"))


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def main():
    problems = {}   # (set, problem_index) -> list of annotated rows (one per file)
    for bench, job in JOBS:
        path = fetch(job)
        if path is None:
            return not_computable(f"file iterate-runs:{job}/answers.jsonl not readable")
        seen = set()
        with open(path) as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                pi = r.get("problem_index")
                if pi in seen:
                    continue
                seen.add(pi)
                if not is_finished(r):
                    continue   # cap hits are not finished
                if r.get("n_new") is None:
                    continue   # drop finished rows with missing / null n_new
                ann = {"n_new": r["n_new"], "layout": is_layout(r), "layout_alt": is_layout(r, loose=True), "row": r}
                problems.setdefault((bench, pi), []).append(ann)

    units = [tuple(v) for _, v in sorted(problems.items(), key=lambda kv: (kv[0][0], kv[0][1]))]

    def stat_with(key):
        def stat(sample):
            fin = [a["n_new"] for u in sample for a in u]
            lay = [a["n_new"] for u in sample for a in u if a[key]]
            if not lay or not fin:
                return 0.0
            return median(lay) / median(fin)
        return stat

    stat = stat_with("layout")
    lay_rows = [a for u in units for a in u if a["layout"]]
    fin_rows = [a for u in units for a in u]
    alt_rows = [a for u in units for a in u if a["layout_alt"]]
    print(json.dumps({"groups": {"layout rows": len(lay_rows), "finished rows": len(fin_rows),
                                 "layout rows (alt cleaning)": len(alt_rows)}}))
    if not lay_rows:
        return not_computable("no layout rows among finished Think-SFT rows; median of an empty set is undefined")
    measured = stat(units)
    alt = stat_with("layout_alt")(units) if alt_rows else None
    ex = dict(lay_rows[0]["row"])
    ex["text"] = "..." + (ex.get("text") or "")[-400:]
    ex.pop("prompt", None)
    report(measured, len(lay_rows), bootstrap(stat, units), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=ex)


if __name__ == "__main__":
    main()
