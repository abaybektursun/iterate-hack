"""Derived or asserted (specs/SPEC_derived.md): a blind hosted judge labels the end of long finished hard328 answers.

    P="uv run --no-project --with numpy --with math-verify==0.9.0 --with anthropic --with brotli>=1.2.0 python -m studies.rlneurons.analysis.derived"   # brotli: httpx2 fails on the older one
    $P prep  --runs runs --work runs/derived          # items.json (with the shown text), hand.md + hand_key.json
    # the agent labels runs/derived/hand.md into runs/derived/hand.json before any judge call
    $P judge --work runs/derived --judge A            # claude-sonnet-5-5 on the 420 sampled rows and the 30 controls
    $P judge --work runs/derived --judge B            # claude-haiku-5-5 on the same and on every other long finished RL answer
    $P judge --work runs/derived --judge F            # judge A's model on the whole text of the 40-row subsample
    $P score --work runs/derived --out studies/rlneurons/results/derived/hard328-01
    $P score --per-sample --out studies/rlneurons/results/derived/hard328_persample-01   # addendum 1: no judge call, reads the labels of hard328-01

The judge sees the problem and the last ~3,000 tokens of the answer; never the model, the gold answer, the score or the
length. Every prompt, raw reply and token usage is kept in <work>/judge_<X>/ (not committed). Needs ANTHROPIC_API_KEY.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from studies.rlneurons.analysis.anatomy_judge import locate
from studies.rlneurons.analysis.riskcov import LABEL, RES, SETS, load, precision_at

SPEC = "studies/rlneurons/specs/SPEC_derived.md"
RUNS = {"think": "thinkvote_hard328_sft1_cue_s4", "rl": "abaybektursun-1114-200505-5ff2", "base": "abaybektursun-1114-200457-e8e6"}
LABELS = ("DERIVED", "ASSERTED", "UNCLEAR")
TARGET = {"wrong": 80, "right": 60}
LONG, SHORT, TAIL_TOKENS, CUT = 8000, 3000, 3000, 0.60
JUDGES = {"A": {"model": "claude-sonnet-5-5", "effort": "low", "usd_per_mtok": (2.0, 10.0)},
          "B": {"model": "claude-haiku-5-5", "effort": None, "usd_per_mtok": (0.10, 0.50)},
          "F": {"model": "claude-sonnet-5-5", "effort": "low", "usd_per_mtok": (2.0, 10.0)}}
BOOT = 2000
RUBRIC = """You are reading the END of a model's answer to a math problem (its closing reasoning and its final write-up). The
beginning of the answer may be cut off. Decide how the final answer was reached, not whether it is correct. You are
not told the correct answer, and you must not solve the problem yourself.

Find the final answer (the last boxed value or the value on the last "Answer:" line). Then give exactly one label:

DERIVED: the final answer is the result of a computation or an argument that the text shows. The steps may contain
errors, rest on an unchecked assumption, or be a guess-and-check that the text actually carries out; what matters is
that the shown steps arrive at this value.

ASSERTED: the text states the final answer without shown steps that arrive at it. Typical forms: the text gives up
and picks a value; it appeals to "the known answer", "the expected answer", "a common result" or the form the answer
should have; its computations reach a different value, or contradict each other without being resolved, and it then
states a value; the step that produces the value is only claimed ("after solving, we get", "it can be shown that")
and the computation is not in the text shown to you nor referred to as done earlier with its result restated.

UNCLEAR: you cannot tell from the text shown, for example because the steps that would produce the value were
evidently done before the part you can see and the visible part only restates their result.

If a final write-up presents steps that arrive at the value, label DERIVED even when the earlier reasoning was
uncertain. If the final write-up only states the value and the visible reasoning before it does not arrive at that
value, label ASSERTED.

Reply with JSON only: {"final_answer": "<the value>", "label": "DERIVED" | "ASSERTED" | "UNCLEAR",
"quote": "<one short passage copied exactly from the text that decides your label>", "reason": "<one sentence>"}"""
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["final_answer", "label", "quote", "reason"],
          "properties": {"final_answer": {"type": "string"}, "label": {"type": "string", "enum": list(LABELS)},
                         "quote": {"type": "string"}, "reason": {"type": "string"}}}


def finished(r) -> bool:
    return not r["cap_hit"] and r["extracted_v3"] is not None


STRATA = {"wrong": lambda r: finished(r) and r["n_new"] > LONG and not r["score_v3"],
          "right": lambda r: finished(r) and r["n_new"] > LONG and bool(r["score_v3"]),
          "short_right": lambda r: finished(r) and r["n_new"] < SHORT and bool(r["score_v3"])}


def pool(by: dict, stratum: str) -> list:
    return [r for rows in by.values() for r in rows if STRATA[stratum](r)]       # sorted by (problem, sample): load() sorts both


def draw(rows: list, name: str, target: int, taken: set) -> list:
    """The spec's rule: shuffle with the named seed, walk the list, at most 2 rows per problem, skip rows already taken."""
    rows = list(rows)
    random.Random(f"0-{name}").shuffle(rows)
    out, per = [], {}
    for r in rows:
        k = (r["problem_index"], r["sample"])
        if len(out) < target and k not in taken and per.get(r["problem_index"], 0) < 2:
            out.append(r)
            per[r["problem_index"]] = per.get(r["problem_index"], 0) + 1
    return out


def shown(text: str, n_new: int, whole: bool = False) -> str:
    text = text.replace("<think>", "").replace("</think>", "")
    return text if whole else text[-round(len(text) * TAIL_TOKENS / n_new):]


def problem_of(prompt: str) -> str:
    head, rest = prompt.split("\n\n", 1)
    body, foot = rest.rsplit("\n\n", 1)
    assert head.startswith("Solve the following problem") and foot.startswith("Remember to put"), prompt[:200]
    return body


def prep(a):
    work = pathlib.Path(a.work)
    assert not (work / "items.json").exists(), f"{work}/items.json exists: use a new work folder"
    work.mkdir(parents=True, exist_ok=True)
    items, hand = [], []
    for m, d in SETS["hard328"].items():
        by = load(RES / d)
        text = {(r["problem_index"], r["sample"]): r for r in map(json.loads, open(pathlib.Path(a.runs) / RUNS[m] / "answers.jsonl")) if r["attempt"] == 0}
        taken = set()

        def item(r, stratum, kind="real", body=None, **extra):
            t = text[(r["problem_index"], r["sample"])]
            assert t["n_new"] == r["n_new"] and t["seed"] == r["seed"], "rows.jsonl and answers.jsonl disagree"
            taken.add((r["problem_index"], r["sample"]))
            return {"kind": kind, "model": m, "stratum": stratum, "problem_index": r["problem_index"], "sample": r["sample"], "n_new": r["n_new"],
                    "right": int(r["score_v3"]), "extracted_v3": r["extracted_v3"], "gold": r["gold"], "problem": problem_of(t["prompt"]),
                    "shown": shown(t["text"] if body is None else body, r["n_new"], whole=kind == "planted_neg"), "full": shown(t["text"], r["n_new"], True), **extra}

        for s in ("wrong", "right"):
            got = [item(r, s) for r in draw(pool(by, s), f"{m}-{s}", TARGET[s], taken)]
            assert len(got) == TARGET[s], (m, s, len(got))
            items += got
            hand += got[:5]
        sampled = set(taken)
        for r in draw(pool(by, "wrong"), f"{m}-planted_pos", 5, taken):
            t = text[(r["problem_index"], r["sample"])]["text"]
            cut = t[:t.rfind("\n\n", 0, round(CUT * len(t)))]
            rng = random.Random(f"0-plant-{m}-{r['problem_index']}-{r['sample']}")
            n = next(n for n in iter(lambda: rng.randint(2, 997), None) if not re.search(rf"(?<!\d){n}(?!\d)", shown(cut, r["n_new"])))
            items.append(item(r, "planted_pos", "planted_pos", cut + f"\n\nThe answer is \\boxed{{{n}}}", planted=n))
        items += [item(r, "planted_neg", "planted_neg") for r in draw(pool(by, "short_right"), f"{m}-planted_neg", 5, taken)]
        if m == "rl":
            items += [item(r, s, "rl_extra") for s in ("wrong", "right") for r in pool(by, s) if (r["problem_index"], r["sample"]) not in sampled]
    random.Random("0-order").shuffle(items)
    for k, it in enumerate(items):
        it["id"] = f"i{k:04d}"
    real = [it for it in items if it["kind"] == "real"]
    full = list(real)
    random.Random("0-full").shuffle(full)
    for it in items:
        it["full_condition"] = it in full[:40]
        if not it["full_condition"]:
            del it["full"]
    random.Random("0-hand").shuffle(hand)
    (work / "items.json").write_text(json.dumps(items, ensure_ascii=False) + "\n")
    (work / "hand_key.json").write_text(json.dumps({f"H{k + 1:02d}": it["id"] for k, it in enumerate(hand)}) + "\n")
    (work / "hand.md").write_text("".join(f"\n\n######## H{k + 1:02d}\nPROBLEM:\n{it['problem']}\n\nEND OF THE ANSWER:\n{it['shown']}" for k, it in enumerate(hand)))
    count = {}
    for it in items:
        count[f"{it['kind']} {it['model']} {it['stratum']}"] = count.get(f"{it['kind']} {it['model']} {it['stratum']}", 0) + 1
    print(json.dumps(count, indent=1), "\nitems", len(items), "shown characters", sum(len(it["shown"]) for it in items))


def judge(a):
    import anthropic
    work, cfg = pathlib.Path(a.work), JUDGES[a.judge]
    out = work / f"judge_{a.judge}"
    out.mkdir(exist_ok=True)
    items = json.loads((work / "items.json").read_text())
    todo = [it for it in items if (it["full_condition"] if a.judge == "F" else it["kind"] != "rl_extra" or a.judge == "B")]
    todo = [it for it in todo if not (out / f"{it['id']}.json").exists()][:a.limit]
    client = anthropic.Anthropic(max_retries=6)

    def one(it):
        prompt = f"{RUBRIC}\n\nPROBLEM:\n{it['problem']}\n\nEND OF THE ANSWER:\n{it['full' if a.judge == 'F' else 'shown']}"
        r = client.messages.create(model=cfg["model"], max_tokens=8000, messages=[{"role": "user", "content": prompt}],
                                   output_config={"format": {"type": "json_schema", "schema": SCHEMA}} | ({"effort": cfg["effort"]} if cfg["effort"] else {}))
        if r.stop_reason != "end_turn":
            raise RuntimeError(f"{it['id']}: stop_reason {r.stop_reason}")
        reply = json.loads(next(b.text for b in r.content if b.type == "text"))
        (out / f"{it['id']}.json").write_text(json.dumps({"id": it["id"], "model": r.model, "prompt": prompt, "reply": reply,
                                                         "usage": {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}}, ensure_ascii=False) + "\n")

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(one, todo))
    print("judged", len(todo), "cost so far, USD", round(cost(work)["total"], 2))


def replies(work: pathlib.Path, j: str) -> dict:
    return {p.stem: json.loads(p.read_text()) for p in sorted((work / f"judge_{j}").glob("i*.json"))}


def cost(work: pathlib.Path) -> dict:
    c = {}
    for j, cfg in JUDGES.items():
        u = [r["usage"] for r in replies(work, j).values()] if (work / f"judge_{j}").exists() else []
        tin, tout = sum(x["input_tokens"] for x in u), sum(x["output_tokens"] for x in u)
        c[j] = {"model": cfg["model"], "calls": len(u), "input_tokens": tin, "output_tokens": tout,
                "usd": (tin * cfg["usd_per_mtok"][0] + tout * cfg["usd_per_mtok"][1]) / 1e6}
    return c | {"total": sum(x["usd"] for x in c.values())}


def kappa(a: list, b: list) -> dict:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum(a.count(l) * b.count(l) for l in LABELS) / n ** 2
    return {"n": n, "agree": sum(x == y for x, y in zip(a, b)), "agreement": po, "kappa": (po - pe) / (1 - pe),
            "table": {x: {y: sum(1 for p, q in zip(a, b) if (p, q) == (x, y)) for y in LABELS} for x in LABELS}}


sel = lambda rows, **kw: [it for it in rows if all(it[k] == v for k, v in kw.items())]


def boot(idx: list):
    """The spec's bootstrap over the problems idx (2,000 resamples, seed 0): pos, per, ci, share."""
    import numpy as np
    pos, n = {p: k for k, p in enumerate(idx)}, len(idx)
    draws = np.random.default_rng(0).integers(0, n, (BOOT, n))

    def per(rows, f=lambda it: 1.0):
        v = np.zeros(n)
        for it in rows:
            v[pos[it["problem_index"]]] += f(it)
        return v

    def ci(fn):
        """fn(take) -> statistic, where take(v) sums a per-problem vector over the (resampled) problems."""
        point = fn(lambda v: v.sum())
        b = np.array([fn(lambda v, d=d: v[d].sum()) for d in draws])
        return {"value": float(point), "interval95": [float(x) for x in np.nanpercentile(b, [2.5, 97.5])]}

    def share(rows, j, label):
        num, den = per([it for it in rows if it[j] == label]), per(rows)
        return lambda take: 100 * take(num) / take(den) if take(den) else np.nan

    return pos, draws, per, ci, share


def score(a):
    import numpy as np
    work, out = pathlib.Path(a.work), pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    items = json.loads((work / "items.json").read_text())
    lab = {j: {k: v["reply"] for k, v in replies(work, j).items()} for j in JUDGES}
    key = json.loads((work / "hand_key.json").read_text())
    hand = {key[h]: v for h, v in json.loads((work / "hand.json").read_text()).items()}
    assert len(hand) == 30 and all(v["label"] in LABELS for v in hand.values())
    for it in items:
        for j in "ABF":
            it[j] = lab[j].get(it["id"], {}).get("label")
        it["hand"] = hand.get(it["id"], {}).get("label")
    real = [it for it in items if it["kind"] == "real"]
    rl_all = [it for it in items if it["model"] == "rl" and it["kind"] in ("real", "rl_extra")]
    assert all(it["A"] and it["B"] for it in real) and all(it["B"] for it in rl_all) and len(real) == 420 and len(rl_all) == 642
    by = {m: load(RES / d) for m, d in SETS["hard328"].items()}
    idx = list(by["rl"])
    n = len(idx)
    pos, draws, per, ci, share = boot(idx)
    think_cap4 = np.array([all(r["cap_hit"] for r in by["think"][p]) for p in idx])

    def cell(rows, j="A"):
        return {"n": len(rows), "problems": len({it["problem_index"] for it in rows}), **{l: sum(it[j] == l for it in rows) for l in LABELS},
                "asserted_pct": ci(share(rows, j, "ASSERTED")) if rows else None}

    res = {"spec": SPEC, "judges": {j: {k: v for k, v in c.items() if k != "usd_per_mtok"} for j, c in JUDGES.items()}, "cost_usd": cost(work),
           "shown": f"problem + last len(text) x {TAIL_TOKENS} / n_new characters; think tags removed", "bootstrap": {"resamples": BOOT, "seed": 0, "unit": "problem"}}

    # instrument checks
    ctl = {k: sel(items, kind=k) for k in ("planted_pos", "planted_neg")}
    want = {"planted_pos": "ASSERTED", "planted_neg": "DERIVED"}
    quotes = [locate(lab["A"][it["id"]]["quote"], it["shown"]) is not None for it in items if it["A"]]
    fullrows = [it for it in real if it["full_condition"]]
    assert len(fullrows) == 40 and all(it["F"] for it in fullrows)
    handrows = [it for it in real if it["hand"]]
    res["checks"] = {
        "planted": {j: {k: {"pass": sum(it[j] == want[k] for it in v), "of": len(v), "labels": [it[j] for it in v]} for k, v in ctl.items()} for j in "AB"},
        "kappa_A_B_real": kappa([it["A"] for it in real], [it["B"] for it in real]),
        "kappa_A_B_by_model": {m: kappa([it["A"] for it in sel(real, model=m)], [it["B"] for it in sel(real, model=m)]) for m in SETS["hard328"]},
        "kappa_hand_A": kappa([it["hand"] for it in handrows], [it["A"] for it in handrows]),
        "kappa_hand_B": kappa([it["hand"] for it in handrows], [it["B"] for it in handrows]),
        "quote_found_A": {"found": sum(quotes), "of": len(quotes)},
        "tail_against_full_A": kappa([it["A"] for it in fullrows], [it["F"] for it in fullrows])}
    c = res["checks"]
    res["instrument_ok"] = bool(c["kappa_A_B_real"]["kappa"] >= 0.6 and c["kappa_hand_A"]["kappa"] >= 0.6
                                and all(c["planted"]["A"][k]["pass"] >= 13 for k in want))

    # the table: three models x wrong / right
    res["table"] = {j: {m: {s: cell(sel(real, model=m, stratum=s), j) for s in ("wrong", "right")} for m in SETS["hard328"]} for j in "AB"}
    res["hand_table"] = {m: {s: {l: sum(it["hand"] == l for it in sel(handrows, model=m, stratum=s)) for l in LABELS} for s in ("wrong", "right")} for m in SETS["hard328"]}

    def diff(x, y, s, j="A"):
        fx, fy = share(sel(real, model=x, stratum=s), j, "ASSERTED"), share(sel(real, model=y, stratum=s), j, "ASSERTED")
        return ci(lambda take: fx(take) - fy(take))

    res["H1"] = {j: {f"rl - {y}, {s}": diff("rl", y, s, j) for y in ("think", "base") for s in ("wrong", "right")} | {"base - think, wrong": diff("base", "think", "wrong", j)} for j in "AB"}
    h = res["H1"]["A"]
    res["H1"]["held"] = bool(all(h[f"rl - {y}, wrong"]["interval95"][0] > 0 for y in ("think", "base")) and h["rl - think, wrong"]["value"] >= 20 and h["rl - base, wrong"]["value"] >= 20)
    res["H1"]["refuted"] = bool(any(h[f"rl - {y}, wrong"]["interval95"][0] <= 0 for y in ("think", "base")) or h["rl - base, wrong"]["value"] < 10)

    # H2: right rate of asserted and of derived long finished answers, strata weighted back to the pool
    def h2(m, j="A"):
        poolv = {s: per(pool(by[m], s)) for s in ("wrong", "right")}
        sh = {(s, l): share(sel(real, model=m, stratum=s), j, l) for s in ("wrong", "right") for l in LABELS}

        def rate(l):
            def f(take):
                r, w = take(poolv["right"]) * sh[("right", l)](take), take(poolv["wrong"]) * sh[("wrong", l)](take)
                return 100 * r / (r + w) if r + w else np.nan
            return f
        fa, fd = rate("ASSERTED"), rate("DERIVED")
        return {"pool": {s: int(v.sum()) for s, v in poolv.items()}, "right_pct_of_asserted": ci(fa), "right_pct_of_derived": ci(fd),
                "derived_minus_asserted": ci(lambda take: fd(take) - fa(take)),
                "asserted_share_of_long_finished_pct": ci(lambda take: (take(poolv["right"]) * sh[("right", "ASSERTED")](take) + take(poolv["wrong"]) * sh[("wrong", "ASSERTED")](take))
                                                          / (take(poolv["right"]) + take(poolv["wrong"])))}

    res["H2"] = {j: {m: h2(m, j) for m in SETS["hard328"]} for j in "AB"}
    r = res["H2"]["A"]["rl"]
    res["H2"]["held"] = bool(r["right_pct_of_asserted"]["value"] < 0.5 * r["right_pct_of_derived"]["value"] and r["derived_minus_asserted"]["interval95"][0] > 0)
    # the same on all 642 RL rows with judge B, no weighting
    res["H2"]["B_all_rl"] = {l: {"n": len(sel(rl_all, B=l)), "right": sum(it["right"] for it in sel(rl_all, B=l)),
                                 "right_pct": ci(lambda take, l=l: 100 * take(per(sel(rl_all, B=l), lambda it: it["right"])) / take(per(sel(rl_all, B=l))))} for l in LABELS}

    # by length and by Think-SFT cap hits
    bins = {"8000-12000": lambda it: it["n_new"] <= 12000, "12000-cap": lambda it: it["n_new"] > 12000}
    res["by_length"] = {m: {s: {b: cell([it for it in sel(real, model=m, stratum=s) if f(it)]) for b, f in bins.items()} for s in ("wrong", "right")} for m in SETS["hard328"]}
    grp = {"think_capped_4_of_4": lambda it: think_cap4[pos[it["problem_index"]]], "elsewhere": lambda it: not think_cap4[pos[it["problem_index"]]]}
    res["rl_wrong_by_think_caps"] = {"problems_think_capped_4_of_4": int(think_cap4.sum()),
                                     "A_sample": {g: cell([it for it in sel(real, model="rl", stratum="wrong") if f(it)]) for g, f in grp.items()},
                                     "B_all_rl_wrong": {g: cell([it for it in sel(rl_all, stratum="wrong") if f(it)], "B") for g, f in grp.items()}}

    # H3: the flag as an abstention signal on RL's 1,312 samples, against length alone at the same coverage
    rows = [r for p in idx for r in by["rl"][p]]
    n_new = np.array([r["n_new"] for r in rows], float).reshape(n, 4)
    ans = np.array([r["extracted_v3"] is not None for r in rows]).reshape(n, 4)
    right = np.array([bool(r["score_v3"]) for r in rows]).reshape(n, 4)
    flag = np.zeros((n, 4), bool)
    for it in sel(rl_all, B="ASSERTED"):
        flag[pos[it["problem_index"]], it["sample"]] = True

    def h3(d):
        nn, an, ri, fl = n_new[d], ans[d], right[d], flag[d]
        kept = an & ~fl
        cov = kept.sum() / an.size
        by_len = precision_at(np.where(an, nn, np.inf), ri, [cov])[0]
        return 100 * cov, 100 * ri[kept].sum() / kept.sum(), 100 * by_len, 100 * ri[an].sum() / an.sum(), 100 * an.sum() / an.size

    p = h3(np.arange(n))
    b = np.array([h3(d) for d in draws])
    res["H3"] = {"judge": "B on all 642 long finished RL answers", "flagged": int(flag.sum()), "flagged_right": int((flag & right).sum()),
                 "coverage_all_answered_pct": p[4], "precision_all_answered_pct": p[3], "coverage_kept_pct": p[0],
                 "precision_flag_pct": {"value": p[1], "interval95": np.percentile(b[:, 1], [2.5, 97.5]).tolist()},
                 "precision_length_only_same_coverage_pct": {"value": p[2], "interval95": np.percentile(b[:, 2], [2.5, 97.5]).tolist()},
                 "flag_minus_length": {"value": p[1] - p[2], "interval95": np.percentile(b[:, 1] - b[:, 2], [2.5, 97.5]).tolist()}}
    res["H3"]["held"] = bool(res["H3"]["flag_minus_length"]["value"] >= 2 and res["H3"]["flag_minus_length"]["interval95"][0] > 0)
    # the same from judge A's sample, weighted to the pool (point estimate)
    aw, ar = (sum(it["A"] == "ASSERTED" for it in sel(real, model="rl", stratum=s)) / TARGET[s] for s in ("wrong", "right"))
    nw, nr = len(pool(by["rl"], "wrong")), len(pool(by["rl"], "right"))
    kept, cov = ans.sum() - nw * aw - nr * ar, (ans.sum() - nw * aw - nr * ar) / ans.size
    res["H3"]["A_weighted"] = {"flagged_estimate": nw * aw + nr * ar, "coverage_kept_pct": 100 * cov, "precision_flag_pct": 100 * (right.sum() - nr * ar) / kept,
                               "precision_length_only_same_coverage_pct": 100 * float(precision_at(np.where(ans, n_new, np.inf), right, [cov])[0])}

    def example(it, j="A"):
        rep = lab[j][it["id"]]
        return {k: it[k] for k in ("id", "kind", "model", "stratum", "problem_index", "sample", "n_new", "right", "extracted_v3", "gold")} | {
            "judge": j, "label": rep["label"], "final_answer": rep["final_answer"], "quote": rep["quote"], "reason": rep["reason"], "shown_last_1500": it["shown"][-1500:]}

    ex = {f"{m} {l}": example(next(it for it in sel(real, model=m, stratum="wrong") if it["A"] == l == it["B"])) for m in SETS["hard328"] for l in ("DERIVED", "ASSERTED")}
    for k, v in ctl.items():
        ex[f"{k} scored right"] = example(next(it for it in v if it["A"] == want[k]))
        miss = [it for it in v if it["A"] != want[k]]
        ex[f"{k} scored wrong"] = example(miss[0]) if miss else "none: judge A labelled all of them as planted"
    out.mkdir(parents=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": "python -m studies.rlneurons.analysis.derived " + " ".join(sys.argv[1:]), "job_id": None,
                                              "gpu": "none (laptop)", "spec": SPEC, "judges": res["judges"], "inputs": SETS["hard328"], "raw": RUNS}, indent=1) + "\n")
    with open(out / "labels.jsonl", "w") as f:
        for it in items:
            f.write(json.dumps({k: it.get(k) for k in ("id", "kind", "model", "stratum", "problem_index", "sample", "n_new", "right", "extracted_v3", "gold", "planted", "full_condition", "A", "B", "F", "hand")}
                               | {f"{j}_{k}": lab[j][it["id"]][k] for j in "ABF" if it["id"] in lab[j] for k in ("final_answer", "quote", "reason")}, ensure_ascii=False) + "\n")
    (out / "hand.json").write_text(json.dumps({"labelled_by": "the agent (a fork of the session), before any judge call; no model, gold, score or length shown",
                                               "rows": [{"id": i, **v} for i, v in hand.items()]}, indent=1, ensure_ascii=False) + "\n")
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "examples.json").write_text(json.dumps(ex, indent=1, ensure_ascii=False) + "\n")
    (out / "rubric.md").write_text(RUBRIC + "\n")
    (out / "table.md").write_text(markdown(res))
    print((out / "table.md").read_text())


JUDGED = [f"long {s}, {l.lower()}" for s in ("right", "wrong") for l in ("DERIVED", "ASSERTED")]
COUNTED = {"short right": lambda r: finished(r) and r["n_new"] <= LONG and bool(r["score_v3"]),
           "short wrong": lambda r: finished(r) and r["n_new"] <= LONG and not r["score_v3"],
           "cap hit": lambda r: r["cap_hit"],
           "no answer": lambda r: not r["cap_hit"] and r["extracted_v3"] is None}
PAIRS = (("rl", "base"), ("rl", "think"))


def persample(a):
    """Addendum 1 of the spec: the outcome of every generated sample, the judged strata weighted back to their pools."""
    out = pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    items = [json.loads(l) for l in open(a.labels)]
    real, rl_all = sel(items, kind="real"), [it for it in items if it["model"] == "rl" and it["kind"] in ("real", "rl_extra")]
    assert len(real) == 420 and len(rl_all) == 642 and not any(it[j] == "UNCLEAR" for it in real + rl_all for j in "AB")
    by = {m: load(RES / d) for m, d in SETS["hard328"].items()}
    idx = list(by["rl"])
    pos, draws, per, ci, share = boot(idx)
    total = 4 * len(idx)
    rows = {m: [r for p in idx for r in by[m][p]] for m in by}
    poolv = {m: {s: per(pool(by[m], s)) for s in ("wrong", "right")} for m in by}
    counted = {m: {k: per([r for r in rows[m] if f(r)]) for k, f in COUNTED.items()} for m in by}
    assert all(sum(v.sum() for v in poolv[m].values()) + sum(v.sum() for v in counted[m].values()) == total for m in by), "an outcome is missing or double"

    def weighted(m, j, s, l):                                                   # % of the model's samples; H2's weighting
        f = share(sel(real, model=m, stratum=s), j, l)
        return lambda take: take(poolv[m][s]) * f(take) / total

    def rates(m, j):
        return ({f"long {s}, {l.lower()}": ci(weighted(m, j, s, l)) for s in ("right", "wrong") for l in ("DERIVED", "ASSERTED")}
                | {k: ci(lambda take, v=v: 100 * take(v) / total) for k, v in counted[m].items()})

    def split(x, y, j):
        """Asserted wrong per sample, x - y, and its exact split into a pool term and a share term (H5)."""
        px, py = (lambda take, m=m: take(poolv[m]["wrong"]) / total for m in (x, y))
        sx, sy = (share(sel(real, model=m, stratum="wrong"), j, "ASSERTED") for m in (x, y))
        return {"difference": ci(lambda take: px(take) * sx(take) - py(take) * sy(take)),
                "pool_term": ci(lambda take: (px(take) - py(take)) * sy(take)), "share_term": ci(lambda take: px(take) * (sx(take) - sy(take)))}

    res = {"spec": SPEC + ", addendum 1", "labels": a.labels, "samples_per_model": total, "bootstrap": {"resamples": BOOT, "seed": 0, "unit": "problem"},
           "counts": {m: {f"long finished {s}": int(poolv[m][s].sum()) for s in ("right", "wrong")} | {k: int(v.sum()) for k, v in counted[m].items()}
                         | {"cap hit with a boxed value": sum(r["cap_hit"] and r["extracted_v3"] is not None for r in rows[m]),
                            "cap hit scored right": sum(r["cap_hit"] and bool(r["score_v3"]) for r in rows[m])} for m in by},
           "sample_labels": {j: {m: {s: {"rows": TARGET[s], "asserted": len(sel(real, model=m, stratum=s, **{j: "ASSERTED"}))} for s in ("wrong", "right")} for m in by} for j in "AB"},
           "rates_pct": {j: {m: rates(m, j) for m in by} for j in "AB"}}
    ball = {f"long {s}, {l.lower()}": sel(rl_all, stratum=s, B=l) for s in ("right", "wrong") for l in ("DERIVED", "ASSERTED")}
    res["B_whole_pool"] = {"rl": {k: {"n": len(v), "pct": ci(lambda take, v=per(v): 100 * take(v) / total)} for k, v in ball.items()},
                           "base": "judge B labelled the 140 sampled rows only", "think": "judge B labelled the 140 sampled rows only"}
    res["asserted_wrong_per_sample"] = {j: {f"{x} - {y}": split(x, y, j) for x, y in PAIRS} for j in "AB"}
    v = per(ball["long wrong, asserted"])
    res["asserted_wrong_per_sample"]["B, rl whole pool"] = {f"rl - {y}": {"difference": ci(lambda take, f=weighted(y, "B", "wrong", "ASSERTED"): 100 * take(v) / total - f(take))} for _, y in PAIRS}
    res["cap_hit"] = {f"{x} - {y}": ci(lambda take, x=x, y=y: 100 * (take(counted[x]["cap hit"]) - take(counted[y]["cap hit"])) / total) for x, y in PAIRS}
    d = res["asserted_wrong_per_sample"]["A"]["rl - base"]
    res["H4_held"] = bool(d["difference"]["interval95"][0] > 0)
    res["H5_held"] = bool(d["pool_term"]["value"] >= 0.5 * d["difference"]["value"] and d["pool_term"]["interval95"][0] > 0)
    groups = {"base hits the cap on none of 4": lambda p: bool(counted["base"]["cap hit"][pos[p]] == 0), "base hits the cap on 1 to 4 of 4": lambda p: bool(counted["base"]["cap hit"][pos[p]] > 0)}
    res["by_base_cap_hits"] = {g: {"problems": sum(map(f, idx)), "samples": 4 * sum(map(f, idx))} | {m: {"cap hit": sum(r["cap_hit"] for r in rows[m] if f(r["problem_index"]))}
                                   | {f"long finished {s}": sum(f(r["problem_index"]) for r in pool(by[m], s)) for s in ("wrong", "right")} for m in by}
                               | {"rl long wrong, asserted, judge B whole pool": sum(f(it["problem_index"]) for it in ball["long wrong, asserted"])} for g, f in groups.items()}
    out.mkdir(parents=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": "python -m studies.rlneurons.analysis.derived " + " ".join(sys.argv[1:]), "job_id": None, "gpu": "none (laptop)",
                                              "spec": res["spec"], "judge_calls": 0, "labels": a.labels, "examples": "results/derived/hard328-01/examples.json", "inputs": SETS["hard328"]}, indent=1) + "\n")
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "table.md").write_text(markdown_persample(res))
    print((out / "table.md").read_text())


def markdown_persample(res: dict) -> str:
    v = lambda x, d=1: f"{x['value']:.{d}f} [{x['interval95'][0]:.{d}f}, {x['interval95'][1]:.{d}f}]"
    ms, n = list(res["counts"]), res["samples_per_model"]
    L = [f"Outcome of every generated sample, hard328, attempt 0 of 4 samples, {n:,} samples per model. % of samples [95 %, bootstrap over problems].", ""]
    for j in "AB":
        L += [f"Judge {j}, the judged strata weighted to their pools:", "", "| Outcome | " + " | ".join(LABEL[m] for m in ms) + " |", "|---" * (len(ms) + 1) + "|"]
        L += [f"| {k} | " + " | ".join(v(res["rates_pct"][j][m][k]) for m in ms) + " |" for k in JUDGED + list(COUNTED)] + [""]
    L += ["Counts: " + "; ".join(f"{LABEL[m]}: " + ", ".join(f"{k} {c}" for k, c in res["counts"][m].items()) for m in ms) + ".", "",
          "Judge B on all 642 long finished RL answers, counted: " + "; ".join(f"{k} {x['n']}, {v(x['pct'])} %" for k, x in res["B_whole_pool"]["rl"].items())
          + ". Judge B labelled only the 140 sampled rows of the base and of Think-SFT.", "",
          "Asserted wrong answers per sample, paired differences in points, with the exact split (pool term: how often the model finishes long and wrong; share term: how often such an answer is asserted):", "",
          "| Judge | Pair | Difference | Pool term | Share term |", "|---|---|---|---|---|"]
    L += [f"| {j} | {k} | {v(x['difference'])} | {v(x['pool_term'])} | {v(x['share_term'])} |" for j in "AB" for k, x in res["asserted_wrong_per_sample"][j].items()]
    L += [f"| B, RL counted on its whole pool | {k} | {v(x['difference'])} | | |" for k, x in res["asserted_wrong_per_sample"]["B, rl whole pool"].items()]
    L += ["", "Cap-hit rate, points: " + "; ".join(f"{k} {v(x)}" for k, x in res["cap_hit"].items()) + f". H4 held: {res['H4_held']}. H5 held: {res['H5_held']}.", "",
          "Problems split by the base's cap hits (counts of samples):", "", "| Group | Problems | Model | Cap hit | Long finished wrong | Long finished right |", "|---|---|---|---|---|---|"]
    L += [f"| {g} | {x['problems']} | {LABEL[m]} | {x[m]['cap hit']} | {x[m]['long finished wrong']} | {x[m]['long finished right']} |" for g, x in res["by_base_cap_hits"].items() for m in ms]
    L += ["", "RL's long wrong answers that judge B labels asserted (whole pool): " + "; ".join(f"{g}: {x['rl long wrong, asserted, judge B whole pool']}" for g, x in res["by_base_cap_hits"].items()) + "."]
    return "\n".join(L) + "\n"


def markdown(res: dict) -> str:
    v = lambda x, d=1: f"{x['value']:.{d}f} [{x['interval95'][0]:.{d}f}, {x['interval95'][1]:.{d}f}]"
    c = res["checks"]
    L = [f"Instrument: planted positives A {c['planted']['A']['planted_pos']['pass']}/15, B {c['planted']['B']['planted_pos']['pass']}/15; planted negatives A "
         f"{c['planted']['A']['planted_neg']['pass']}/15, B {c['planted']['B']['planted_neg']['pass']}/15; kappa A/B {c['kappa_A_B_real']['kappa']:.2f} "
         f"({c['kappa_A_B_real']['agree']}/{c['kappa_A_B_real']['n']}); kappa hand/A {c['kappa_hand_A']['kappa']:.2f} ({c['kappa_hand_A']['agree']}/30); hand/B "
         f"{c['kappa_hand_B']['kappa']:.2f}; tail against full text {c['tail_against_full_A']['agree']}/40, kappa {c['tail_against_full_A']['kappa']:.2f}; "
         f"quote found {c['quote_found_A']['found']}/{c['quote_found_A']['of']}. Instrument ok: {res['instrument_ok']}. Cost {res['cost_usd']['total']:.2f} USD.", ""]
    for j in "AB":
        L += [f"Judge {j} ({res['judges'][j]['model']}), long finished answers, hard328:", "", "| Model | Stratum | Rows | Derived | Asserted | Unclear | Asserted, % [95 %] |", "|---|---|---|---|---|---|---|"]
        L += [f"| {LABEL[m]} | {s} | {x['n']} | {x['DERIVED']} | {x['ASSERTED']} | {x['UNCLEAR']} | {v(x['asserted_pct'])} |" for m, t in res["table"][j].items() for s, x in t.items()]
        L += [""] + [f"- {k}: {v(x)} points" for k, x in res["H1"][j].items()] + [""]
    L += [f"H1 held: {res['H1']['held']}; refuted: {res['H1']['refuted']}.", "", "H2, right rate of asserted and of derived long finished answers (judge A, weighted to the pool):", "",
          "| Model | Asserted share of long finished, % | Right, asserted % | Right, derived % | Derived - asserted |", "|---|---|---|---|---|"]
    L += [f"| {LABEL[m]} | {v(x['asserted_share_of_long_finished_pct'])} | {v(x['right_pct_of_asserted'])} | {v(x['right_pct_of_derived'])} | {v(x['derived_minus_asserted'])} |" for m, x in res["H2"]["A"].items()]
    L += ["", "Judge B on all 642 long finished RL answers: " + "; ".join(f"{l} {x['right']}/{x['n']} right, {v(x['right_pct'])} %" for l, x in res["H2"]["B_all_rl"].items()), "",
          "Asserted share by length (judge A):", "", "| Model | Stratum | 8,000 to 12,000 | 12,000 to the cap |", "|---|---|---|---|"]
    f = lambda x: f"{x['ASSERTED']}/{x['n']}, {v(x['asserted_pct'])}" if x["n"] else "0 rows"
    L += [f"| {LABEL[m]} | {s} | {f(t[s]['8000-12000'])} | {f(t[s]['12000-cap'])} |" for m, t in res["by_length"].items() for s in t]
    t = res["rl_wrong_by_think_caps"]
    L += ["", f"RL long wrong answers, problems where all four Think-SFT samples hit the cap ({t['problems_think_capped_4_of_4']}) against the others: " +
          "; ".join(f"{k} {g}: {f(x)}" for k in ("A_sample", "B_all_rl_wrong") for g, x in t[k].items())]
    h = res["H3"]
    L += ["", f"H3 (judge B flag on RL's 1,312 samples; descriptive): all answered: coverage {h['coverage_all_answered_pct']:.1f} %, precision {h['precision_all_answered_pct']:.1f} %. "
          f"Dropping the {h['flagged']} flagged answers ({h['flagged_right']} of them right): coverage {h['coverage_kept_pct']:.1f} %, precision {v(h['precision_flag_pct'])} %; "
          f"length alone at the same coverage {v(h['precision_length_only_same_coverage_pct'])} %; difference {v(h['flag_minus_length'])} points. Held: {h['held']}. "
          f"Judge A, weighted: coverage {h['A_weighted']['coverage_kept_pct']:.1f} %, precision {h['A_weighted']['precision_flag_pct']:.1f} % against {h['A_weighted']['precision_length_only_same_coverage_pct']:.1f} %."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["prep", "judge", "score"])
    ap.add_argument("--runs", default="runs")
    ap.add_argument("--work")
    ap.add_argument("--per-sample", action="store_true", help="with score: addendum 1, from --labels, no judge call")
    ap.add_argument("--labels", default="studies/rlneurons/results/derived/hard328-01/labels.jsonl")
    ap.add_argument("--judge", choices=list(JUDGES))
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out")
    args = ap.parse_args()
    assert args.per_sample or args.work, "--work is required"
    assert not args.per_sample or args.step == "score", "--per-sample goes with score"
    (persample if args.per_sample else {"prep": prep, "judge": judge, "score": score}[args.step])(args)
