"""duel-r8-m09 p3: finished Think-SFT MATH-500 answers, layout-miss rate at n_new <= pooled median minus rate above it."""
import json
import os
import subprocess

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable

JOBS = [("math500", j) for j in ["000512-ee03", "014843-85d9", "000607-0e92", "000621-1d7e"]]


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


def split(rows):
    m = median([x["n_new"] for x in rows])
    return m, [x for x in rows if x["n_new"] <= m], [x for x in rows if x["n_new"] > m]


def diff(units, key="layout"):
    rows = [x for u in units for x in u]
    if not rows:
        return None
    _, lo, hi = split(rows)  # the median is recomputed inside each bootstrap resample
    if not lo or not hi:
        return None
    return sum(x[key] for x in lo) / len(lo) - sum(x[key] for x in hi) / len(hi)


def main():
    rows = load()
    by_prob = {}
    for x in rows:
        by_prob.setdefault(x["pi"], []).append(x)
    units = [tuple(v) for v in by_prob.values()]
    if not rows:
        not_computable("no finished rows")
        return
    m, lo, hi = split(rows)
    groups = {"low_finished_rows": len(lo), "high_finished_rows": len(hi),
              "low_problems": len({x["pi"] for x in lo}), "high_problems": len({x["pi"] for x in hi}),
              "low_layout_rows": sum(x["layout"] for x in lo), "high_layout_rows": sum(x["layout"] for x in hi),
              "median_n_new": m}
    print(json.dumps({"groups": groups}))
    if not lo or not hi:
        not_computable(f"empty group: low {len(lo)}, high {len(hi)}")
        return
    val = diff(units)
    alt = diff(units, "layout_alt")
    ci = bootstrap(lambda s: (lambda v: v if v is not None else 0.0)(diff(s)), units)
    ex = next((x for x in lo + hi if x["layout"]), lo[0])
    report(val, min(groups["low_problems"], groups["high_problems"]), ci, "bootstrap", refuted_by_met=False,
           alt_measured=alt, example_row=slim(ex["row"]))


if __name__ == "__main__":
    main()
