"""Checks or per-step error (specs/SPEC_checks.md, idea-60d3e1): checking markers in the stored four-sample texts of the
cued base and RL on MATH-500. Attempt 0 of samples 0 to 3, grader v3 scores as stored by run_cell.

    R="--base runs/abaybektursun-1114-153825-208b --rl runs/abaybektursun-1114-183640-e828"
    PY="uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.checks"
    $PY stats $R --labels studies/rlneurons/results/anatomy/judge-01/labels.json --out studies/rlneurons/results/checks/math500-01
    $PY prep  $R --work runs/checks_judge
    (one subagent per runs/checks_judge/pass?/batch_*.md writes batch_*.labels.json)
    $PY score $R --work runs/checks_judge --stats studies/rlneurons/results/checks/math500-01/readout.json --out studies/rlneurons/results/checks/judge-01

stats writes readout.json (analyses a, b, c, the rule of d, the uncaught part of e), examples.json, rule_sample.json
(the 20 rule-flagged events for the hand check) and run.json. score writes the judges' readout, labels and examples.
Both fail on an existing out folder.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import json
import pathlib
import random
import re
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis import anatomy as A
from studies.rlneurons.lib import n13_score as S

FAM = {
    "backtrack": r"\b(wait|hold on|hmm+|actually|oops|scratch that|on second thought)\b",
    "check": r"\b(double[- ]?check\w*|re-?check\w*|re-?examin\w*|re-?verif\w*|verif(?:y|ies|ied|ying)|check(?:s|ed|ing)?|confirm(?:s|ed|ing)?|sanity)\b",
    "error": r"\b(mistake\w*|error|wrong|incorrect\w*|correction|miscalculat\w*|misread|messed up)\b|that can'?t be|doesn'?t make sense|not (?:right|correct)\b",
    "alternative": r"\b(alternatively|perhaps|maybe)\b",
}
PRIMARY = ("backtrack", "check", "error")
RX = {k: re.compile(v, re.I) for k, v in FAM.items()}
CUE = re.compile(r"\b(should be|instead|mistake\w*|wrong|incorrect\w*|error|miscalculat\w*|forgot|missed|not \d|no,)", re.I)
NUMBER = re.compile(r"\d+(?:\.\d+)?")
GAP_CHARS, RULE_TOKENS = 100, 200
LABELS = ("fix", "switch", "confirm", "filler")
N_JUDGE, N_CONTROL, N_BATCH = 40, 10, 4
RUBRIC = """You are labeling short excerpts of step-by-step answers to math problems. Each item gives the problem and an excerpt of one
answer. One word or phrase of the excerpt is marked between >>> and <<< (for example >>>Wait<<<). Decide what the text
right after the marked word does, and give exactly one label:

- fix: a specific earlier statement (a number, an expression, a count, a sign, the reading of the problem) was wrong, and
  the text after the mark corrects it; the answer goes on with the corrected version.
- switch: the text after the mark changes the method or the reading of the problem, or drops the current line of work,
  without correcting one specific wrong statement.
- confirm: the text after the mark tests or re-derives an earlier statement (substitutes back, recounts, uses a second
  method) and keeps it unchanged.
- filler: nothing is re-examined: the text continues with the next step, restates, or thinks aloud.

Judge only from the excerpt. Write your labels as a JSON list, one object per item, in the order of the file:
[{"id": "<item id>", "label": "<fix|switch|confirm|filler>", "reason": "<one sentence>"}]
Judge every item on its own. Do not use any tool except reading the batch file and writing the labels file."""


def annotate(runs: dict):
    """Per sample: _tpc (tokens per character), _m (sorted character offsets of the primary markers), _fam (count per family)."""
    for Sm in runs.values():
        for i in Sm:
            for r in Sm[i]:
                r["_tpc"] = r["n_new"] / len(r["text"])
                r["_m"] = sorted(m.start() for k in PRIMARY for m in RX[k].finditer(r["text"]))
                r["_fam"] = {k: len(RX[k].findall(r["text"])) for k in FAM}
                r["_kind"] = A.kind(r)


def window(r: dict, lo: float, hi: float) -> tuple:
    """(markers, tokens) in the characters [lo, hi) of the answer, clipped to the answer."""
    lo, hi = max(0.0, lo), min(float(len(r["text"])), hi)
    if hi <= lo:
        return 0, 0.0
    return bisect.bisect_left(r["_m"], hi) - bisect.bisect_left(r["_m"], lo), (hi - lo) * r["_tpc"]


def rate(rs: list, fam=None) -> float:
    return 1000 * sum(len(r["_m"]) if fam is None else r["_fam"][fam] for r in rs) / sum(r["n_new"] for r in rs)


def paired(x, y) -> dict:
    """Mean of y - x over problems with its bootstrap interval."""
    x, y = np.array(x, float), np.array(y, float)
    if not len(x):
        return {"problems": 0}
    return {"problems": len(x), "mean_first": float(x.mean()), "mean_second": float(y.mean()), "second_minus_first": float((y - x).mean()),
            "ci95": A.boot_mean(y - x) if len(x) > 1 else None, "problems_second_higher": int((y > x).sum())}


def base_vs_rl(runs: dict, bk: np.ndarray, rk: np.ndarray) -> dict:
    out = {}
    keep = {"all_samples": lambda r: True, "finished_samples": lambda r: not r["cap_hit"], "right_samples": lambda r: r["score_v3"]}
    for name, f in keep.items():
        sub = {m: {i: [r for r in runs[m][i] if f(r)] for i in runs[m]} for m in runs}
        both = [i for i in sub["base"] if sub["base"][i] and sub["rl"][i]]
        cell = lambda idx, fam=None: paired([rate(sub["base"][i], fam) for i in idx], [rate(sub["rl"][i], fam) for i in idx])
        out[name] = {"what": "first = base with cue, second = RL; markers per 1,000 tokens, per problem (its samples pooled)",
                     "pooled_over_all_tokens": {m: rate([r for i in both for r in sub[m][i]]) for m in runs},
                     "tokens": {m: sum(r["n_new"] for i in both for r in sub[m][i]) for m in runs},
                     "per_problem": cell(both),
                     "by_family": {k: cell(both, k) for k in FAM},
                     "by_base_k": {str(k): cell([i for i in both if bk[i] == k]) for k in range(A.K + 1)},
                     "cell_base3_rl4": cell([i for i in both if bk[i] == 3 and rk[i] == 4])}
    return out


def siblings(Sm: dict) -> dict:
    out = {}
    for name, wrong in (("any_wrong", lambda r: not r["score_v3"]), ("finished_wrong", lambda r: r["_kind"] == "finished_wrong")):
        whole, trunc, fam = [], [], {k: [] for k in FAM}
        for i in Sm:
            R, W = [r for r in Sm[i] if r["score_v3"]], [r for r in Sm[i] if wrong(r)]
            if not (R and W):
                continue
            whole.append((rate(R), rate(W)))
            for k in FAM:
                fam[k].append((rate(R, k), rate(W, k)))
            pr = []
            for w in W:
                for r in R:
                    n = min(w["n_new"], r["n_new"])
                    cw, cr = window(w, 0, n / w["_tpc"])[0], window(r, 0, n / r["_tpc"])[0]
                    pr.append((1000 * cr / n, 1000 * cw / n))
            trunc.append(np.mean(pr, 0))
        col = lambda xs: paired([a for a, _ in xs], [b for _, b in xs])
        out[name] = {"what": "first = right samples, second = wrong samples of the same problem; markers per 1,000 tokens",
                     "whole_answer": col(whole), "first_N_tokens_N_is_shorter_sibling": col(trunc), "whole_answer_by_family": {k: col(fam[k]) for k in FAM}}
    return out


def around_slips(runs: dict, labels: list, w_tokens=300, flag_tokens=500, n_random=200) -> dict:
    rng = random.Random(0)
    items = []
    for it in labels:
        if it["kind"] not in ("base", "rl") or it["passA"]["quote_position"] is None:
            continue
        Sm = runs[it["model"]][it["problem_index"]]
        r = next(x for x in Sm if x["sample"] == it["sample"])
        assert r["_kind"] == "finished_wrong", it["id"]
        sib = [x for x in Sm if x["score_v3"]]

        def at(x, rel, qlen):
            s = rel * len(x["text"])
            e = s + qlen
            w, f = w_tokens / x["_tpc"], flag_tokens / x["_tpc"]
            return {"before": window(x, s - w, s), "after": window(x, e, e + w), "flag": window(x, e, e + f)[0] > 0}

        def mean(ws):
            return {"before": tuple(np.mean([w["before"] for w in ws], 0)), "after": tuple(np.mean([w["after"] for w in ws], 0)),
                    "flag": float(np.mean([w["flag"] for w in ws]))}
        q, ql = it["passA"]["quote_position"], len(it["passA"]["quote"])
        items.append({"id": it["id"], "model": it["model"], "label": it["passA"]["label"], "problem_index": it["problem_index"], "sample": it["sample"],
                      "obs": at(r, q, ql), "sibling": mean([at(x, q, ql) for x in sib]) if sib else None,
                      "random": mean([at(r, rng.random(), ql) for _ in range(n_random)])})

    def summ(sel):
        out = {"n": len(sel), "n_with_right_sibling": sum(x["sibling"] is not None for x in sel)}
        if not sel:
            return out
        for ctl in ("sibling", "random"):
            sub = [x for x in sel if x[ctl] is not None]
            if len(sub) < 2:
                continue
            for win in ("before", "after"):
                o, c = np.array([x["obs"][win] for x in sub]), np.array([x[ctl][win] for x in sub])
                stat = lambda idx: (1000 * o[idx, 0].sum() / o[idx, 1].sum(), 1000 * c[idx, 0].sum() / c[idx, 1].sum())
                ro, rc = stat(np.arange(len(sub)))
                g = np.random.default_rng(0)
                d = [np.subtract(*stat(g.integers(0, len(sub), len(sub)))) for _ in range(A.BOOT)]
                out[f"{win}_vs_{ctl}"] = {"n": len(sub), "markers_per_1k_at_step": ro, "markers_per_1k_control": rc, "step_minus_control": ro - rc,
                                          "ci95": [float(v) for v in np.percentile(d, [2.5, 97.5])]}
            fo, fc = np.array([x["obs"]["flag"] for x in sub], float), np.array([x[ctl]["flag"] for x in sub])
            out[f"marker_within_{flag_tokens}_tokens_after_vs_{ctl}"] = {"n": len(sub), "at_step": int(fo.sum()), "share_at_step": float(fo.mean()),
                                                                          "share_control": float(fc.mean()), "ci95_of_difference": A.boot_mean(fo - fc)}
        return out
    res = {"what": f"pass A first wrong steps; windows of {w_tokens} tokens before the quote and after its end; controls: the same relative position "
                   f"in the right siblings, and {n_random} random positions of the same answer. Every sample here ended wrong.",
           "base": summ([x for x in items if x["model"] == "base"]), "rl": summ([x for x in items if x["model"] == "rl"]),
           "base_slip": summ([x for x in items if x["model"] == "base" and x["label"] == "slip"]),
           "base_not_slip": summ([x for x in items if x["model"] == "base" and x["label"] != "slip"])}
    return res, items


def events(r: dict) -> list:
    """Check events of a sample: (start, end) of each primary marker with no marker in the 100 characters before it."""
    ms = sorted((m.start(), m.end()) for k in PRIMARY for m in RX[k].finditer(r["text"]))
    return [ms[j] for j in range(len(ms)) if j == 0 or ms[j][0] - ms[j - 1][0] > GAP_CHARS]


def revising(r: dict, start: int) -> bool:
    after = r["text"][start:start + int(RULE_TOKENS / r["_tpc"])]
    if not CUE.search(after):
        return False
    seen = set(NUMBER.findall(r["text"][:start]))
    return any(m.group() not in seen and (len(m.group()) >= 2 or re.search(r"=\s*$", after[:m.start()])) for m in NUMBER.finditer(after))


def rule_table(runs: dict) -> tuple:
    out, flagged = {}, []
    for m, Sm in runs.items():
        out[m] = {}
        for k in ("right", "finished_wrong", "cap_hit"):
            rs = [r for i in Sm for r in Sm[i] if r["_kind"] == k]
            ev = [(r, s) for r in rs for s, _ in events(r)]
            fl = [(r, s) for r, s in ev if revising(r, s)]
            tok = sum(r["n_new"] for r in rs)
            out[m][k] = {"samples": len(rs), "tokens": tok, "events": len(ev), "events_per_1k": 1000 * len(ev) / tok, "rule_revising": len(fl),
                         "rule_share": len(fl) / len(ev), "rule_revising_per_1k": 1000 * len(fl) / tok,
                         "samples_with_a_revising_event": sum(any(revising(r, s) for s, _ in events(r)) for r in rs)}
            flagged += [(m, r, s) for r, s in fl]
    return out, flagged


def excerpt(r: dict, s: int, e: int, tokens: int = 250) -> str:
    w = int(tokens / r["_tpc"])
    return r["text"][max(0, s - w):s] + ">>>" + r["text"][s:e] + "<<<" + r["text"][e:e + w]


def uncaught(runs: dict, labels: list) -> dict:
    out = {}
    for m, Sm in runs.items():
        rs = [r for i in Sm for r in Sm[i]]
        fin = [r for r in rs if not r["cap_hit"]]
        fw = sum(r["_kind"] == "finished_wrong" for r in rs)
        lab = [x["passA"]["label"] for x in labels if x["kind"] == m]
        tok = sum(r["n_new"] for r in fin)
        share, (lo, hi) = lab.count("slip") / len(lab), S.wilson(lab.count("slip"), len(lab))
        out[m] = {"finished_samples": len(fin), "finished_tokens": tok, "finished_wrong_samples": fw, "judged": len(lab), "judged_slip": lab.count("slip"),
                  "first_wrong_steps_per_1k_tokens": 1000 * fw / tok, "uncaught_slips_per_1k_tokens": 1000 * fw * share / tok,
                  "uncaught_slips_per_1k_tokens_wilson95_of_share": [1000 * fw * lo / 100 / tok, 1000 * fw * hi / 100 / tok],
                  "finished_wrong_per_finished_sample": fw / len(fin), "tokens_per_finished_sample": tok / len(fin)}
    b, r = out["base"], out["rl"]
    out["base_over_rl"] = {k: b[k] / r[k] for k in ("first_wrong_steps_per_1k_tokens", "uncaught_slips_per_1k_tokens", "finished_wrong_per_finished_sample")}
    return out


def load(args) -> tuple:
    runs = {"base": A.load(pathlib.Path(args.base)), "rl": A.load(pathlib.Path(args.rl))}
    annotate(runs)
    return runs, json.loads((A.HERE / "data/rln4/math500.json").read_text())


def run_json(out: pathlib.Path, args, **extra):
    (out / "run.json").write_text(json.dumps(dict({
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=A.HERE).stdout.strip(),
        "command": " ".join(sys.argv), "source_jobs": {"base_cue": pathlib.Path(args.base).name, "rl": pathlib.Path(args.rl).name},
        "grader": "v3 (score_v3 as stored by run_cell)", "rows": "attempt 0 of samples 0 to 3", "gpu": None}, **extra), indent=1))


def stats(args):
    out = pathlib.Path(args.out)
    out.mkdir(parents=True)
    runs, problems = load(args)
    labels = json.loads(pathlib.Path(args.labels).read_text())
    bk, rk = (np.array([sum(r["score_v3"] for r in runs[m][i]) for i in runs[m]]) for m in ("base", "rl"))
    slips, slip_items = around_slips(runs, labels)
    rule, flagged = rule_table(runs)
    rd = {"markers": FAM, "primary": PRIMARY, "token_position": "character x n_new / len(text)",
          "a_base_vs_rl": base_vs_rl(runs, bk, rk), "b_wrong_vs_right_siblings": {m: siblings(runs[m]) for m in runs},
          "c_around_first_wrong_steps": slips, "d_rule": rule, "e_uncaught": uncaught(runs, labels)}
    (out / "readout.json").write_text(json.dumps(rd, indent=1))
    rng = random.Random(0)
    sample = [x for m in runs for x in rng.sample([f for f in flagged if f[0] == m], 10)]
    (out / "rule_sample.json").write_text(json.dumps(
        [{"n": n, "model": m, "problem_index": r["problem_index"], "sample": r["sample"], "kind": r["_kind"], "char": s,
          "excerpt": excerpt(r, s, s + len(RX["backtrack"].match(r["text"], s).group()) if RX["backtrack"].match(r["text"], s) else s)}
         for n, (m, r, s) in enumerate(sample)], indent=1))
    # examples: a base slip with no marker in the 500 tokens after it, one with a marker, and one sibling pair with its rates
    ex = {}
    for name, flag in (("base_slip_with_no_marker_in_500_tokens_after", False), ("base_slip_with_a_marker_in_500_tokens_after_and_still_wrong", True)):
        x = next(x for x in slip_items if x["model"] == "base" and x["label"] == "slip" and x["obs"]["flag"] == flag)
        it = next(l for l in labels if l["id"] == x["id"])
        r = next(s for s in runs["base"][x["problem_index"]] if s["sample"] == x["sample"])
        c = int(it["passA"]["quote_position"] * len(r["text"]))
        ex[name] = {"problem_index": x["problem_index"], "sample": x["sample"], "problem": problems[x["problem_index"]]["problem"], "gold": r["gold"],
                    "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "judge_quote": it["passA"]["quote"], "judge_reason": it["passA"]["reason"],
                    "markers_in_300_tokens_before_and_after": [x["obs"]["before"][0], x["obs"]["after"][0]],
                    "text_from_500_chars_before_to_2500_after_the_step": r["text"][max(0, c - 500):c + 2500]}
    i = next(i for i in runs["base"] if bk[i] == 3 and any(r["_kind"] == "finished_wrong" for r in runs["base"][i]))
    ex["sibling_pair_base3"] = {"problem_index": i, "samples": [{"sample": r["sample"], "kind": r["_kind"], "n_new": r["n_new"], "markers": len(r["_m"]),
                                                               "markers_per_1k": rate([r]), "by_family": r["_fam"]} for r in runs["base"][i]]}
    (out / "examples.json").write_text(json.dumps(ex, indent=1))
    run_json(out, args)
    a = rd["a_base_vs_rl"]["all_samples"]
    print("a pooled", a["pooled_over_all_tokens"], "paired", a["per_problem"])
    for m in runs:
        print("b", m, {k: (v["whole_answer"]["second_minus_first"], v["whole_answer"]["ci95"], v["whole_answer"]["problems"]) for k, v in rd["b_wrong_vs_right_siblings"][m].items()})


def plant_filler(r: dict, rng: random.Random):
    """A span with no primary marker in about 500 tokens; `Wait, ` put before a sentence in its middle."""
    w = int(250 / r["_tpc"])
    c = [m.end() for m in re.finditer(r"\. (?=[A-Z])", r["text"]) if w < m.end() < len(r["text"]) - w and window(r, m.end() - w, m.end() + w)[0] == 0]
    if not c:
        return None
    s = rng.choice(c)
    return r["text"][s - w:s] + ">>>Wait<<<, " + r["text"][s].lower() + r["text"][s + 1:s + w]


def plant_fix(r: dict, rng: random.Random):
    """A right `lhs = value` statement preceded by the same statement with a wrong value and a retraction."""
    w = int(250 / r["_tpc"])
    c = [m for m in re.finditer(r"([^\n.=?!:]{8,60})= (\d{2,5})(?=[\s.,$])", r["text"])
         if w < m.start() < len(r["text"]) - w and window(r, m.start() - w, m.end() + w)[0] == 0]
    if not c:
        return None
    m = rng.choice(c)
    bad = str(int(m.group(2)) + rng.choice([-20, -10, 10, 20, 100]))
    return (r["text"][m.start() - w:m.start()] + m.group(1) + "= " + bad + ". >>>Wait<<<, that's not right. Let me redo that: "
            + m.group(1).lstrip() + "= " + m.group(2) + r["text"][m.end():m.end() + w])


def prep(args):
    work = pathlib.Path(args.work)
    work.mkdir(parents=True)
    runs, problems = load(args)
    rng = random.Random(0)
    items = []
    right = {m: [r for i in runs[m] for r in runs[m][i] if r["_kind"] == "right"] for m in runs}
    for m in runs:
        by_problem = collections.defaultdict(list)
        for r in right[m]:
            if events(r):
                by_problem[r["problem_index"]].append(r)
        for i in sorted(rng.sample(sorted(by_problem), N_JUDGE)):
            r = rng.choice(by_problem[i])
            s, e = rng.choice(events(r))
            items.append({"kind": m, "model": m, "problem_index": i, "sample": r["sample"], "char": s, "marker": r["text"][s:e],
                          "rule_revising": revising(r, s), "excerpt": excerpt(r, s, e)})
    pool = rng.sample([r for m in runs for r in right[m]], 400)
    for kind_, plant in (("planted_filler", plant_filler), ("planted_fix", plant_fix)):
        seen = set()
        for r in pool:
            if len(seen) == N_CONTROL:
                break
            x = plant(r, random.Random(r["seed"]))
            if x and r["problem_index"] not in seen:
                seen.add(r["problem_index"])
                items.append({"kind": kind_, "model": r["model"], "problem_index": r["problem_index"], "sample": r["sample"], "char": None,
                              "marker": "Wait", "rule_revising": None, "excerpt": x})
        assert len(seen) == N_CONTROL, (kind_, len(seen))
    for it, k in zip(items, rng.sample(range(1000, 10000), len(items))):
        it["id"] = f"c{k}"
        it["problem"] = problems[it["problem_index"]]["problem"]
    (work / "items.json").write_text(json.dumps(items))
    (work / "rubric.md").write_text(RUBRIC + "\n")
    for p, seed in (("passA", 1), ("passB", 2)):
        (work / p).mkdir()
        order = random.Random(seed).sample(items, len(items))
        for k in range(N_BATCH):
            b = order[k::N_BATCH]
            (work / p / f"batch_{k:02d}.md").write_text(f"{len(b)} items: {', '.join(x['id'] for x in b)}\n\n" + "".join(
                f"### ITEM {x['id']}\n\nPROBLEM: {x['problem']}\n\nEXCERPT:\n{x['excerpt']}\n\n" for x in b))
    print(collections.Counter(it["kind"] for it in items))


def kappa(a: list, b: list) -> float:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum(a.count(l) * b.count(l) for l in LABELS) / n ** 2
    return (po - pe) / (1 - pe)


def score(args):
    work, out = pathlib.Path(args.work), pathlib.Path(args.out)
    out.mkdir(parents=True)
    items = {it["id"]: it for it in json.loads((work / "items.json").read_text())}
    lab = {}
    for p in ("passA", "passB"):
        lab[p] = {}
        for f in sorted((work / p).glob("batch_*.md")):
            want = set(f.read_text().split("\n", 1)[0].split(": ")[1].split(", "))
            got = json.loads(f.with_suffix(".labels.json").read_text())
            assert {x["id"] for x in got} == want and all(x["label"] in LABELS for x in got), f
            lab[p].update({x["id"]: x for x in got})
        assert set(lab[p]) == set(items), p
    rows = [dict({k: v for k, v in it.items() if k not in ("problem",)}, passA=lab["passA"][i], passB=lab["passB"][i]) for i, it in items.items()]
    stats_rd = json.loads(pathlib.Path(args.stats).read_text())
    rd = {"judge": "Claude Code subagents (the agent's own model), fixed rubric rubric.md, one subagent per batch, two passes over all 100 items in "
                   "different batches and orders; no hosted provider key works on this machine",
          "items": dict(collections.Counter(r["kind"] for r in rows)), "controls": {}, "agreement": {}, "labels": {}}
    for kind_, want in (("planted_filler", "filler"), ("planted_fix", "fix")):
        rs = [r for r in rows if r["kind"] == kind_]
        rd["controls"][kind_] = {"n": len(rs), "want": want, **{p: sum(r[p]["label"] == want for r in rs) for p in lab},
                                 **{p + "_labels": dict(collections.Counter(r[p]["label"] for r in rs)) for p in lab}}
    count = lambda xs: {l: xs.count(l) for l in LABELS}
    for name, sel in (("real", ("base", "rl")), ("base", ("base",)), ("rl", ("rl",))):
        rs = [r for r in rows if r["kind"] in sel]
        a, b = [r["passA"]["label"] for r in rs], [r["passB"]["label"] for r in rs]
        rd["agreement"][name] = {"n": len(rs), "same_label": sum(x == y for x, y in zip(a, b)), "cohen_kappa": kappa(a, b),
                                 "fix_or_not_same": sum((x == "fix") == (y == "fix") for x, y in zip(a, b)),
                                 "confusion_passA_passB": {f"{x}|{y}": c for (x, y), c in sorted(collections.Counter(zip(a, b)).items())}}
        rd["labels"][name] = {"passA": count(a), "passB": count(b), "both_passes_agree": count([x for x, y in zip(a, b) if x == y]),
                              **{f"{p}_{l}_wilson95": S.wilson(xs.count(l), len(xs)) for p, xs in (("passA", a), ("passB", b)) for l in ("fix", "filler")}}
    g = np.random.default_rng(0)
    for p in lab:
        fb, fr = (np.array([r[p]["label"] == "fix" for r in rows if r["kind"] == m], float) for m in ("base", "rl"))
        d = [fr[g.integers(0, len(fr), len(fr))].mean() - fb[g.integers(0, len(fb), len(fb))].mean() for _ in range(A.BOOT)]
        rd["labels"][f"{p}_fix_share_rl_minus_base"] = {"difference": float(fr.mean() - fb.mean()), "ci95": [float(v) for v in np.percentile(d, [2.5, 97.5])]}
    real = [r for r in rows if r["kind"] in ("base", "rl")]
    for name, pos in (("fix", ("fix",)), ("fix_or_switch", ("fix", "switch"))):
        tp = sum(r["rule_revising"] and r["passA"]["label"] in pos for r in real)
        rd[f"rule_against_passA_{name}"] = {"rule_flagged": sum(r["rule_revising"] for r in real), "judge_positive": sum(r["passA"]["label"] in pos for r in real),
                                           "both": tp, "n": len(real)}
    # e: caught errors per 1k tokens of right samples = events per 1k x the judges' fix share; made = caught + uncaught
    rd["e_caught_and_made"] = {}
    for m in ("base", "rl"):
        ev = stats_rd["d_rule"][m]["right"]["events_per_1k"]
        un = stats_rd["e_uncaught"][m]
        n = sum(r["kind"] == m for r in rows)
        e = {"events_per_1k_tokens_right_samples": ev, "uncaught_slips_per_1k_tokens": un["uncaught_slips_per_1k_tokens"],
             "first_wrong_steps_per_1k_tokens": un["first_wrong_steps_per_1k_tokens"]}
        for p in lab:
            k = sum(r[p]["label"] == "fix" for r in rows if r["kind"] == m)
            lo, hi = S.wilson(k, n)
            c = ev * k / n
            e[p] = {"fix": k, "n": n, "caught_per_1k_tokens": c, "caught_per_1k_wilson95_of_share": [ev * lo / 100, ev * hi / 100],
                    "made_per_1k_tokens (caught + every first wrong step)": c + un["first_wrong_steps_per_1k_tokens"],
                    "catch_share": c / (c + un["first_wrong_steps_per_1k_tokens"])}
        rd["e_caught_and_made"][m] = e
    (out / "readout.json").write_text(json.dumps(rd, indent=1))
    (out / "labels.json").write_text(json.dumps(rows, indent=0))
    (out / "rubric.md").write_text((work / "rubric.md").read_text())
    ex = {}
    for name, cond in (("rl_check_that_fixes (both passes fix)", lambda r: r["kind"] == "rl" and r["passA"]["label"] == r["passB"]["label"] == "fix"),
                       ("base_check_that_fixes (both passes fix)", lambda r: r["kind"] == "base" and r["passA"]["label"] == r["passB"]["label"] == "fix"),
                       ("filler (both passes)", lambda r: r["kind"] in ("base", "rl") and r["passA"]["label"] == r["passB"]["label"] == "filler"),
                       ("passes_disagree", lambda r: r["kind"] in ("base", "rl") and r["passA"]["label"] != r["passB"]["label"]),
                       ("planted_fix_scored_right", lambda r: r["kind"] == "planted_fix" and r["passA"]["label"] == "fix"),
                       ("planted_fix_scored_wrong", lambda r: r["kind"] == "planted_fix" and r["passA"]["label"] != "fix"),
                       ("planted_filler_scored_right", lambda r: r["kind"] == "planted_filler" and r["passA"]["label"] == "filler"),
                       ("planted_filler_scored_wrong", lambda r: r["kind"] == "planted_filler" and r["passA"]["label"] != "filler")):
        r = next((r for r in rows if cond(r)), None)
        ex[name] = r and dict(r, problem=items[r["id"]]["problem"])
    (out / "examples.json").write_text(json.dumps(ex, indent=1))
    run_json(out, args, judge=rd["judge"], batches={p: len(list((work / p).glob("batch_*.md"))) for p in lab})
    print(json.dumps({k: rd[k] for k in ("controls", "agreement", "labels", "e_caught_and_made")}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("stats", "prep", "score"))
    ap.add_argument("--base", required=True)
    ap.add_argument("--rl", required=True)
    ap.add_argument("--labels")
    ap.add_argument("--work")
    ap.add_argument("--stats")
    ap.add_argument("--out")
    args = ap.parse_args()
    {"stats": stats, "prep": prep, "score": score}[args.cmd](args)


if __name__ == "__main__":
    main()
