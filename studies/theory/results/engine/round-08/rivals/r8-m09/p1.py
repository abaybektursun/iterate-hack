"""duel-r8-m09 p1: layout-miss rate in Short (n_new < 3000) minus Long (n_new >= 8000), finished Think-SFT cue answers,
8 files pooled (4 hard328, 4 MATH-500)."""
import json
import os
import subprocess

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable

HARD = ["000503-1e5f", "000525-ea4e", "014823-ef56", "014833-1daa"]
MATH = ["000512-ee03", "014843-85d9", "000607-0e92", "000621-1d7e"]
JOBS = [("hard328", j) for j in HARD] + [("math500", j) for j in MATH]


def fetch(job):
    rel = f"abaybektursun-1115-{job}/answers.jsonl"
    path = os.path.join("runs", "theory-tests", rel)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", rel, path], check=True)
    return path


def boxed_content(c):
    i = c.rfind("\\boxed{")
    j = i + len("\\boxed{")
    depth, k = 1, j
    while k < len(c):
        if c[k] == "{":
            depth += 1
        elif c[k] == "}":
            depth -= 1
            if depth == 0:
                return c[j:k]
        k += 1
    return c[j:]  # unbalanced: rest of the string


def candidate(text):
    if "Answer:" in text:
        s = text[text.rfind("Answer:") + len("Answer:"):]
        lines = [ln for ln in s.split("\n") if ln.strip()]
        return lines[0] if lines else ""
    lines = [ln for ln in text.split("\n") if ln.strip()]
    return lines[-1] if lines else ""


def clean(c, restrip=False):
    """Literal order: strip; remove '$' and '*'; drop leading \\[ or \\( and trailing \\] or \\); drop one trailing '.';
    last \\boxed{...} content. restrip=True (alt reading) strips whitespace again after every step."""
    st = (lambda x: x.strip()) if restrip else (lambda x: x)
    c = c.strip()
    c = st(c.replace("$", "").replace("*", ""))
    if c.startswith("\\[") or c.startswith("\\("):
        c = st(c[2:])
    if c.endswith("\\]") or c.endswith("\\)"):
        c = st(c[:-2])
    if c.endswith("."):
        c = st(c[:-1])
    if "\\boxed{" in c:
        c = st(boxed_content(c))
    return c


_agree_cache = {}


def agree(c, gold):
    key = (c, gold)
    if key not in _agree_cache:
        _agree_cache[key] = bool(rln4_lib.agree(c, gold))
    return _agree_cache[key]


def load():
    """Finished rows with n_new present, each with layout flags (main and alt cleaning)."""
    out = []
    for bench, job in JOBS:
        seen = set()
        with open(fetch(job)) as f:
            for line in f:
                r = json.loads(line)
                pi = r["problem_index"]
                if pi in seen:
                    continue
                seen.add(pi)
                finished = r.get("cap_hit") is not True and r.get("finish_reason") != "length"
                if not finished or r.get("n_new") is None:
                    continue
                wrong = r.get("score_v3") != 1
                lay, lay_alt = False, False
                if wrong:
                    raw = candidate(r.get("text") or "")
                    c, ca = clean(raw), clean(raw, restrip=True)
                    lay = c != "" and agree(c, r["gold"])
                    lay_alt = ca != "" and agree(ca, r["gold"])
                out.append({"bench": bench, "job": job, "pi": pi, "n_new": r["n_new"], "layout": lay,
                            "layout_alt": lay_alt, "row": r})
    return out


def slim(r):
    d = {k: v for k, v in r.items() if k not in ("logprobs", "prompt")}
    t = d.get("text") or ""
    if len(t) > 600:
        d["text"] = t[:200] + " [...] " + t[-400:]
    return d


def diff(units, key="layout"):
    rows = [x for u in units for x in u]
    s = [x for x in rows if x["n_new"] < 3000]
    l = [x for x in rows if x["n_new"] >= 8000]
    if not s or not l:
        return None
    return sum(x[key] for x in s) / len(s) - sum(x[key] for x in l) / len(l)


def main():
    rows = load()
    by_prob = {}
    for x in rows:
        by_prob.setdefault((x["bench"], x["pi"]), []).append(x)
    units = [tuple(v) for v in by_prob.values()]
    short = [x for x in rows if x["n_new"] < 3000]
    long_ = [x for x in rows if x["n_new"] >= 8000]
    groups = {"short_finished_rows": len(short), "long_finished_rows": len(long_),
              "short_problems": len({(x["bench"], x["pi"]) for x in short}),
              "long_problems": len({(x["bench"], x["pi"]) for x in long_}),
              "short_layout_rows": sum(x["layout"] for x in short), "long_layout_rows": sum(x["layout"] for x in long_)}
    print(json.dumps({"groups": groups}))
    if not short or not long_:
        not_computable(f"empty group: short {len(short)} finished rows, long {len(long_)}")
        return
    m = diff(units)
    alt = diff(units, "layout_alt")

    def stat(sample):
        v = diff(sample)
        return v if v is not None else 0.0

    ci = bootstrap(stat, units)
    ex = next((x for x in short + long_ if x["layout"]), short[0])
    n = min(groups["short_problems"], groups["long_problems"])
    report(m, n, ci, "bootstrap", refuted_by_met=False, alt_measured=alt, example_row=slim(ex["row"]))


if __name__ == "__main__":
    main()
