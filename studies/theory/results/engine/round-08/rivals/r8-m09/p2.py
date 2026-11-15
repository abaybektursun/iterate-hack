"""duel-r8-m09 p2: median n_new of Think-SFT layout-miss rows / median n_new of all finished rows, 8 files pooled."""
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


def median(v):
    v = sorted(v)
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def ratio(units, key="layout"):
    rows = [x for u in units for x in u]
    lay = [x["n_new"] for x in rows if x[key]]
    if not lay or not rows:
        return None
    mf = median([x["n_new"] for x in rows])
    return median(lay) / mf if mf else None


def main():
    rows = load()
    by_prob = {}
    for x in rows:
        by_prob.setdefault((x["bench"], x["pi"]), []).append(x)
    units = [tuple(v) for v in by_prob.values()]
    lay = [x for x in rows if x["layout"]]
    groups = {"layout_rows": len(lay), "layout_problems": len({(x["bench"], x["pi"]) for x in lay}),
              "finished_rows": len(rows), "finished_problems": len(units)}
    print(json.dumps({"groups": groups}))
    if not lay:
        not_computable("no layout rows: median of an empty set")
        return
    m = ratio(units)
    alt = ratio(units, "layout_alt")
    ci = bootstrap(lambda s: (lambda v: v if v is not None else 0.0)(ratio(s)), units)
    report(m, groups["layout_problems"], ci, "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=slim(lay[0]["row"]))


if __name__ == "__main__":
    main()
