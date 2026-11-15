"""Slip against wrong plan (specs/SPEC_anatomy.md): a blind judge labels finished-wrong samples of the Day-1 #3 runs.

    python -m studies.rlneurons.analysis.anatomy_judge prep  --base runs/<base job> --rl runs/<rl job> --work runs/anatomy_judge
    # the judges (Claude Code subagents, one per batch file) read <work>/pass{A,B}/batch_NN.md and the rubric, and write batch_NN.labels.json
    python -m studies.rlneurons.analysis.anatomy_judge score --work runs/anatomy_judge --pairs studies/rlneurons/results/anatomy/math500-01/pairs.json \
        --out studies/rlneurons/results/anatomy/judge-01

prep draws 60 base and 30 RL finished-wrong samples (seed 0, at most one per problem per model), 15 shuffled pairs and 15
planted slips. Pass A holds all 120 items, pass B a random half of the real items (30 base, 15 RL) and all 30 controls;
each pass is packed into batches of at most BUDGET characters with its own seed. Item ids are random; the batch files name
no model. A right sibling longer than SIB characters is shown by its last SIB characters. score fails if a label is missing
or outside LABELS.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import random
import re
import subprocess
import sys

from studies.rlneurons.analysis import anatomy as A
from studies.rlneurons.lib import n13_score as S

LABELS = ("slip", "wrong_plan", "misread", "format", "mismatch", "unclear")
N = {"base": 60, "rl": 30, "shuffled": 15, "planted": 15}
BUDGET, SIB = 130_000, 12_000
STEP = re.compile(r"(\d+)\s*(\+|-|\*|×|\\times|\\cdot)\s*(\d+)\s*=\s*(\d+)(?![\d.])")
RUBRIC = """You are grading wrong answers to math problems. Each item gives a problem, its gold answer, a reference solution, one
ANSWER UNDER JUDGMENT whose final answer was scored wrong, and sometimes a CORRECT ANSWER to the same problem for comparison.
Read the whole answer under judgment, find the first step where it goes wrong, and give exactly one label:

- slip: the method would give the gold answer; an arithmetic, algebra, sign, counting or copying error changes the result.
- wrong_plan: the method or the concept is wrong, or the solution is abandoned or guessed; carried out without error it
  would still not give the gold answer.
- misread: the answer solves a different problem than the one stated (a condition dropped or changed, the wrong quantity
  reported), and solves that other problem consistently.
- format: the work reaches the gold value; the final stated answer differs in form or is garbled.
- mismatch: the answer under judgment is about a different problem altogether, not this one.
- unclear: none of the above can be decided.

For every item also copy, character for character, the first wrong step from the answer under judgment (40 to 150
characters, one line of the answer, no ellipsis, no rewording). For format, mismatch and unclear the quote may be "".
Write your labels as a JSON list, one object per item, in the order of the file:
[{"id": "<item id>", "label": "<one of the six>", "quote": "<verbatim>", "reason": "<one sentence>"}]
Judge every item on its own. Do not use any tool except reading the batch file and writing the labels file."""


def plant(text: str, gold: str, rng: random.Random):
    """A planted slip: the last correct step `a op b = c` with c equal to the gold answer gets a wrong c, which replaces c
    from that step to the end. Returns (new text, character offset of the step, wrong value) or None."""
    if not re.fullmatch(r"\d+", gold):
        return None
    ops = {"+": int.__add__, "-": int.__sub__}
    hits = [m for m in STEP.finditer(text)
            if m.group(4) == gold and ops.get(m.group(2), int.__mul__)(int(m.group(1)), int(m.group(3))) == int(gold)]
    if not hits:
        return None
    m, bad = hits[-1], str(int(gold) + rng.choice([-2, -1, 1, 2, 10]))
    tail = re.sub(rf"(?<![\d.]){gold}(?![\d.])", bad, text[m.start(4):])
    return text[:m.start(4)] + tail, m.start(), bad


def sibling(samples: list, skip=None):
    right = [r for r in samples if r["score_v3"] and r is not skip]
    return min(right, key=lambda r: r["n_new"]) if right else None


def render(it: dict) -> str:
    sib = it["sibling_text"]
    if sib and len(sib) > SIB:
        sib = f"[the first {len(sib) - SIB} characters are left out]\n" + sib[-SIB:]
    return (f"=== ITEM {it['id']} ===\nPROBLEM:\n{it['problem']}\n\nGOLD ANSWER: {it['gold']}\n\nREFERENCE SOLUTION:\n{it['solution']}\n\n"
            f"ANSWER UNDER JUDGMENT (its final answer: {it['final']}):\n<<<\n{it['text']}\n>>>\n\n"
            + (f"A CORRECT ANSWER TO THE SAME PROBLEM, for comparison:\n<<<\n{sib}\n>>>\n" if sib else "No correct answer to the same problem is available.\n")
            + f"=== END OF ITEM {it['id']} ===\n\n")


def prep(args):
    work = pathlib.Path(args.work)
    work.mkdir(parents=True)
    runs = {"base": A.load(pathlib.Path(args.base)), "rl": A.load(pathlib.Path(args.rl))}
    problems = json.loads((A.HERE / "data/rln4/math500.json").read_text())
    meta = json.loads((A.HERE / "data/anatomy/math500_meta.json").read_text())["rows"]
    rng = random.Random(0)
    items = []

    def add(kind_, model, i, r, text, sib, **extra):
        items.append(dict({"kind": kind_, "model": model, "problem_index": i, "sample": r["sample"], "problem": problems[i]["problem"],
                           "gold": problems[i]["answer"], "solution": meta[i]["solution"], "final": r["extracted_v3"] if "final" not in extra else extra.pop("final"),
                           "text": text, "sibling_text": sib["text"] if sib else None, "sibling_sample": sib["sample"] if sib else None,
                           "n_new": r["n_new"]}, **extra))

    for model in ("base", "rl"):
        Sm = runs[model]
        wrong = [i for i in Sm if any(A.kind(r) == "finished_wrong" for r in Sm[i])]
        for i in sorted(rng.sample(wrong, N[model])):
            r = rng.choice([r for r in Sm[i] if A.kind(r) == "finished_wrong"])
            add(model, model, i, r, r["text"], sibling(Sm[i]))
    # shuffled: a right finished answer of problem j shown under problem i (i != j)
    finished = [(m, i, r) for m in runs for i in runs[m] for r in runs[m][i] if r["score_v3"] and r["n_new"] < 4000]
    for m, j, r in rng.sample(finished, N["shuffled"]):
        i = rng.choice([x for x in runs[m] if x != j and meta[x]["subject"] != meta[j]["subject"]])
        add("shuffled", m, i, r, r["text"], sibling(runs[m][i]), answer_from_problem=j)
    # planted slips
    cand = []
    for m, i, r in finished:
        p = plant(r["text"], problems[i]["answer"], random.Random(i))
        if p:
            cand.append((m, i, r, p))
    assert len(cand) >= N["planted"], f"only {len(cand)} right samples whose last step equals the gold answer"
    seen = set()
    for m, i, r, (text, at, bad) in rng.sample(cand, len(cand)):
        if i in seen or len(seen) == N["planted"]:
            continue
        seen.add(i)
        add("planted", m, i, r, text, sibling(runs[m][i], skip=r), final=bad, planted_at_char=at, planted_value=bad)
    assert collections.Counter(it["kind"] for it in items) == N, collections.Counter(it["kind"] for it in items)
    ids = rng.sample(range(1000, 10000), len(items))
    for it, k in zip(items, ids):
        it["id"] = f"q{k}"
    (work / "items.json").write_text(json.dumps(items))
    (work / "rubric.md").write_text(RUBRIC + "\n")
    half = {it["id"] for k, n in (("base", 30), ("rl", 15)) for it in random.Random(3).sample([x for x in items if x["kind"] == k], n)}
    for p, seed in (("passA", 1), ("passB", 2)):
        (work / p).mkdir()
        order = random.Random(seed).sample([it for it in items if p == "passA" or it["id"] in half or it["kind"] in ("shuffled", "planted")], len(items) if p == "passA" else len(half) + N["shuffled"] + N["planted"])
        batches = []                                              # first fit, largest item first; then a random order inside the batch
        for it in sorted(order, key=lambda x: -len(render(x))):
            b = next((b for b in batches if sum(len(render(x)) for x in b) + len(render(it)) <= BUDGET), None)
            if b is None:
                batches.append([it])
            else:
                b.append(it)
        for k, b in enumerate(batches):
            random.Random(seed * 100 + k).shuffle(b)
            (work / p / f"batch_{k:02d}.md").write_text(f"{len(b)} items: {', '.join(x['id'] for x in b)}\n\n" + "".join(render(x) for x in b))
        print(p, len(batches), "batches, items per batch", [len(b) for b in batches])


def locate(quote: str, text: str):
    """Relative character offset of the judge's quote in the answer; whitespace-insensitive, then its first 30 characters."""
    sq = lambda s: re.sub(r"\s+", "", s)
    if not quote or not sq(quote):
        return None
    t, q = sq(text), sq(quote)
    for cand in (q, q[:30]):
        k = t.find(cand)
        if k >= 0:
            return k / len(t)
    return None


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
            for x in json.loads(f.with_suffix(".labels.json").read_text()):
                assert x["label"] in LABELS and x["id"] in items and x["id"] not in lab[p], (f, x)
                lab[p][x["id"]] = x
        assert set(lab[p]) == set(items), f"{p}: {len(set(items) - set(lab[p]))} items without a label"
    proxy = {(x["problem_index"], x["wrong_sample"]): x["proxy_position"] for x in json.loads(pathlib.Path(args.pairs).read_text())}
    rows = []
    for k, it in items.items():
        pos = {p: locate(lab[p][k]["quote"], it["text"]) for p in lab}
        rows.append({"id": k, "kind": it["kind"], "model": it["model"], "problem_index": it["problem_index"], "sample": it["sample"],
                     "has_right_sibling": it["sibling_text"] is not None, "final": it["final"], "gold": it["gold"], "n_new": it["n_new"],
                     "planted_at": it.get("planted_at_char") and it["planted_at_char"] / len(it["text"]), "answer_from_problem": it.get("answer_from_problem"),
                     "proxy_position": proxy.get((it["problem_index"], it["sample"])) if it["kind"] == "base" else None,
                     **{p: dict(lab[p][k], quote_position=pos[p]) for p in lab}})
    rd = {"judge": "Claude Code subagents (the agent's own model), fixed rubric rubric.md, one subagent per batch, two passes in different batches",
          "n_items": dict(N), "controls": {}, "agreement": {}, "labels": {}, "first_wrong_step": {}}
    for kind_, want in (("shuffled", "mismatch"), ("planted", "slip")):
        rs = [r for r in rows if r["kind"] == kind_]
        rd["controls"][kind_] = {"n": len(rs), "want": want, **{p: sum(r[p]["label"] == want for r in rs) for p in lab},
                                 **{p + "_labels": dict(collections.Counter(r[p]["label"] for r in rs)) for p in lab}}
    rs = [r for r in rows if r["kind"] == "planted"]
    rd["controls"]["planted"]["quote_within_5pct_of_planted_step"] = {
        p: sum(r[p]["quote_position"] is not None and abs(r[p]["quote_position"] - r["planted_at"]) <= 0.05 for r in rs) for p in lab}
    for name, sel in (("real_90", ("base", "rl")), ("base_60", ("base",)), ("rl_30", ("rl",))):
        rs = [r for r in rows if r["kind"] in sel]
        a, b = [r["passA"]["label"] for r in rs], [r["passB"]["label"] for r in rs]
        rd["agreement"][name] = {"n": len(rs), "same_label": sum(x == y for x, y in zip(a, b)), "cohen_kappa": kappa(a, b),
                                 "confusion_passA_passB": {f"{x}|{y}": c for (x, y), c in sorted(collections.Counter(zip(a, b)).items())}}
        both = [x for x, y in zip(a, b) if x == y]
        rd["labels"][name] = {"passA": {l: a.count(l) for l in LABELS}, "passB": {l: b.count(l) for l in LABELS},
                              "both_passes_agree": {l: both.count(l) for l in LABELS}, "n_agree": len(both),
                              "slip_share_wilson95": {p: S.wilson(x.count("slip"), len(x)) for p, x in (("passA", a), ("passB", b))}}
        for sib in (True, False):
            sub = [r for r in rs if r["has_right_sibling"] == sib]
            rd["labels"][name][f"passA_{'with' if sib else 'without'}_right_sibling"] = {"n": len(sub), **{l: sum(r["passA"]["label"] == l for r in sub) for l in LABELS}}
        import numpy as np
        pos = {p: [r[p]["quote_position"] for r in rs if r[p]["quote_position"] is not None] for p in lab}
        both_pos = [(r["passA"]["quote_position"], r["passB"]["quote_position"]) for r in rs
                    if r["passA"]["quote_position"] is not None and r["passB"]["quote_position"] is not None]
        rd["first_wrong_step"][name] = {
            **{p: {"quotes_found_in_answer": len(v), "median_position": float(np.median(v)), "quartiles": [float(x) for x in np.percentile(v, [25, 75])],
                   "share_in_first_third": float(np.mean(np.array(v) < 1 / 3)), "share_in_last_third": float(np.mean(np.array(v) > 2 / 3))} for p, v in pos.items()},
            "both_found": len(both_pos), "passes_within_15pct": sum(abs(x - y) <= 0.15 for x, y in both_pos)}
    pr = [r for r in rows if r["proxy_position"] is not None]
    rd["proxy_check"] = {"what": "base items with a right sibling and a proxy position: the proxy is confirmed on an item if it is within 0.15 of the judge's quoted first wrong step",
                         **{p: {"n": sum(r[p]["quote_position"] is not None for r in pr),
                                "confirmed": sum(r[p]["quote_position"] is not None and abs(r[p]["quote_position"] - r["proxy_position"]) <= 0.15 for r in pr),
                                "proxy_earlier_by_over_0.15": sum(r[p]["quote_position"] is not None and r["proxy_position"] < r[p]["quote_position"] - 0.15 for r in pr)} for p in lab}}
    (out / "readout.json").write_text(json.dumps(rd, indent=1))
    (out / "labels.json").write_text(json.dumps(rows, indent=0))
    (out / "rubric.md").write_text((work / "rubric.md").read_text())
    ex = {}
    for name, cond in (("slip_both_passes", lambda r: r["kind"] == "base" and r["passA"]["label"] == r["passB"]["label"] == "slip"),
                       ("wrong_plan_both_passes", lambda r: r["kind"] == "base" and r["passA"]["label"] == r["passB"]["label"] == "wrong_plan"),
                       ("passes_disagree", lambda r: r["kind"] == "base" and r["passA"]["label"] != r["passB"]["label"]),
                       ("planted_control_scored_right", lambda r: r["kind"] == "planted" and r["passA"]["label"] == "slip"),
                       ("planted_control_scored_wrong", lambda r: r["kind"] == "planted" and r["passA"]["label"] != "slip"),
                       ("shuffled_control_scored_right", lambda r: r["kind"] == "shuffled" and r["passA"]["label"] == "mismatch"),
                       ("shuffled_control_scored_wrong", lambda r: r["kind"] == "shuffled" and r["passA"]["label"] != "mismatch")):
        r = next((r for r in rows if cond(r)), None)
        ex[name] = r and dict(r, problem=items[r["id"]]["problem"], answer_last_1500=items[r["id"]]["text"][-1500:])
    (out / "examples.json").write_text(json.dumps(ex, indent=1))
    (out / "run.json").write_text(json.dumps({
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=A.HERE).stdout.strip(),
        "command": " ".join(sys.argv), "judge": rd["judge"], "gpu": None,
        "batches": {p: len(list((work / p).glob("batch_*.md"))) for p in lab}}, indent=1))
    print(json.dumps({k: rd[k] for k in ("controls", "agreement", "labels", "proxy_check")}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prep")
    p.add_argument("--base", required=True)
    p.add_argument("--rl", required=True)
    p.add_argument("--work", required=True)
    s = sub.add_parser("score")
    s.add_argument("--work", required=True)
    s.add_argument("--pairs", required=True)
    s.add_argument("--out", required=True)
    args = ap.parse_args()
    {"prep": prep, "score": score}[args.cmd](args)


if __name__ == "__main__":
    main()
