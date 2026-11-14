"""RLN-5 map readout (specs/SPEC5_map.md §6): reads the shards of jobs/rln5_map.py and writes metrics.json and examples.json.

    PYTHONPATH=. uv run --no-project --with numpy --with transformers==5.22.2 --with huggingface_hub --with jinja2 \
        python -m studies.rlneurons.analysis.rln5_map_analyze runs/<job-id> --t1 <T1.jsonl> --t2 <T2.jsonl> --out <result folder>

runs/<job-id> is the job's $OUT_DIR copied with `uv run tools/gpu.py get <job-id>`. The stored rows give the texts; the
tokenizer (files only, no weights) maps characters to token positions and must reproduce the job's token ids (asserted).
Groups come from results/rln4/t1_t2_items-01/per_problem.json. Positions are counted after the prompt: the cue (T1) or the
answer's first token (T2) is position 0. All log-probs and KL are in nats. Fail loud: no try/except, no fallback.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re

import numpy as np

from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
LN2 = float(np.log(2))
RNG = np.random.default_rng(0)


def f32(v):
    return np.asarray(v, dtype=np.float32)


def load_cell(run, cell):
    index = json.loads((run / "index.json").read_text())
    rows = {}
    for sh in index["shards"]:
        if sh["cell"] != cell:
            continue
        z = np.load(run / sh["file"])
        off = z["offsets"]
        for r, pi in enumerate(z["problem_index"]):
            rows[int(pi)] = {**{k: z[k][off[r]:off[r + 1]] for k in index["arrays"]},
                             **{k: int(z[k][r]) for k in ("n_prompt", "n_cue", "n_gen", "has_stop", "n_new")}}
    return rows


def quart(v):
    v = f32(v)
    if len(v) == 0:
        return {"n": 0}
    q = np.percentile(v, [25, 50, 75])
    boot = np.median(RNG.choice(v, size=(2000, len(v))), axis=1)
    return {"n": int(len(v)), "q25": float(q[0]), "median": float(q[1]), "q75": float(q[2]), "mean": float(v.mean()),
            "median_boot95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]}


def perm_median(a, b, n=10000):
    a, b = f32(a), f32(b)
    if len(a) == 0 or len(b) == 0:
        return None
    obs, allv = abs(np.median(a) - np.median(b)), np.concatenate([a, b])
    hits = 0
    for _ in range(n):
        p = RNG.permutation(allv)
        hits += abs(np.median(p[:len(a)]) - np.median(p[len(a):])) >= obs
    return (hits + 1) / (n + 1)


def answer_span(text):
    """(mode, extracted, first char, last char + 1 of the marker, char of a 'Final Answer' header before it or None)."""
    mode, ext, start = R.extract_v3(text)
    if mode == "none":
        return None
    if mode == "boxed":
        c0, c1 = start, start + len("\\boxed{")
    else:
        m = [m for m in R.MARK_V3.finditer(text) if m.end() == start][-1]
        c0, c1 = m.start(), m.end()
    lo = max(0, c0 - 60)
    h = text[lo:c0].rfind("Final Answer")
    return mode, ext, c0, c1, (lo + h if h >= 0 else None)


def tok_at(offsets, char):
    return next(p for p, (a, b) in enumerate(offsets) if b > char)


def share_top(kl, frac):
    kl = np.sort(f32(kl))[::-1]
    return float(kl[:max(1, int(round(frac * len(kl))))].sum() / kl.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", help="runs/<job-id>")
    ap.add_argument("--t1", required=True)
    ap.add_argument("--t2", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--per-problem", default=str(STUDY / "results" / "rln4" / "t1_t2_items-01" / "per_problem.json"))
    a = ap.parse_args()
    run, out = pathlib.Path(a.run), pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    fz = json.loads((STUDY / "data" / "rln4" / "frozen4.json").read_text())
    math = json.loads((STUDY / "data" / "rln4" / "math500.json").read_text())
    pp = {r["problem_index"]: r for r in json.loads(pathlib.Path(a.per_problem).read_text())}
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    dec = lambda i: tok.decode([int(i)])

    cells = {}
    for c, path in (("T1", a.t1), ("T2", a.t2)):
        text = {r["problem_index"]: r for r in (json.loads(l) for l in open(path))}
        cells[c] = load_cell(run, c)
        for i, row in cells[c].items():
            ids, offsets = R.encode_answer(tok, text[i]["text"], fz["prefill_text"], fz["prefill_ids"])
            assert [int(t) for t in row["tok"][:len(ids)]] == [int(t) for t in ids], (c, i, "token ids differ from the job's")
            row.update(text=text[i]["text"], offsets=offsets, n_tok=len(ids), cap_hit=text[i]["cap_hit"], gold=text[i]["gold"])
    M = {"run": str(run), "job_metrics": json.loads((run / "metrics.json").read_text()).get("controls"),
         "answers": {c: len(v) for c, v in cells.items()}, "units": "nats; probabilities as stated"}

    # ---------------------------------------------------------------- a. top-1 disagreement and concentration of KL
    A = {}
    for c, rows in cells.items():
        own, other = ("kl_base_rl", "kl_rl_base") if c == "T1" else ("kl_rl_base", "kl_base_rl")
        g = {k: np.concatenate([r[k][r["kind"] >= 1] for r in rows.values()]) for k in ("top1_base", "top1_rl", own, other, "ent_base", "ent_rl")}
        diff = g["top1_base"] != g["top1_rl"]
        per = [float((r["top1_base"] != r["top1_rl"])[r["kind"] >= 1].mean()) for r in rows.values()]
        fin = [float((r["top1_base"] != r["top1_rl"])[r["kind"] >= 1].mean()) for r in rows.values() if not r["cap_hit"]]
        A[c] = {"positions": int(len(diff)), "answers": len(rows), "top1_differ_share_pooled": float(diff.mean()),
                "top1_differ_share_per_answer": quart(per), "top1_differ_share_finished_answers": quart(fin),
                "kl_own_direction": own, "mean_kl_own": float(f32(g[own]).mean()), "mean_kl_other": float(f32(g[other]).mean()),
                "kl_own_share_top_1pct": share_top(g[own], 0.01), "kl_own_share_top_4pct": share_top(g[own], 0.04),
                "kl_other_share_top_1pct": share_top(g[other], 0.01), "kl_other_share_top_4pct": share_top(g[other], 0.04),
                "mean_entropy_base": float(f32(g["ent_base"]).mean()), "mean_entropy_rl": float(f32(g["ent_rl"]).mean()),
                "mean_entropy_base_where_top1_differs": float(f32(g["ent_base"])[diff].mean()),
                "mean_entropy_base_where_top1_agrees": float(f32(g["ent_base"])[~diff].mean())}
    M["a"] = A

    # ---------------------------------------------------------------- b. KL by position
    B = {}
    for c, rows in cells.items():
        own = "kl_base_rl" if c == "T1" else "kl_rl_base"
        first, dec10, last, stop, opening, alln = [], [], [], [], [], []
        for r in rows.values():
            kl = f32(r[own])
            n_open = 3 if r["text"].startswith(fz["prefill_text"]) else None
            if n_open is None:
                continue                                              # T2 answers that do not open with the cue text
            opening.append(kl[:3])
            body = kl[3:]                                             # after the opening; includes the stop token
            if len(body) < 100:
                continue
            first.append(body[:10])
            dec10.append([float(x.mean()) for x in np.array_split(body, 10)])
            alln.append(float(body.mean()))
            if not r["cap_hit"]:
                last.append(body[-51:-1])
                stop.append(float(body[-1]))
        B[c] = {"kl": own, "answers": len(first), "opening_positions_mean_kl": [float(x) for x in np.mean(opening, axis=0)],
                "first_10_after_opening_mean_kl": [float(x) for x in np.mean(first, axis=0)],
                "first_10_after_opening_median_kl": [float(x) for x in np.median(first, axis=0)],
                "decile_mean_kl_mean_over_answers": [float(x) for x in np.mean(dec10, axis=0)],
                "decile_mean_kl_median_over_answers": [float(x) for x in np.median(dec10, axis=0)],
                "mean_kl_per_answer": quart(alln), "finished_answers": len(last),
                "last_50_before_stop_mean_kl": float(np.mean(last)) if last else None,
                "last_50_before_stop_by_tens": [float(np.mean([x[i:i + 10] for x in last])) for i in range(0, 50, 10)] if last else None,
                "stop_position_kl": quart(stop)}
    M["b"] = B

    # ---------------------------------------------------------------- c. the test of H at the answer-start token
    def group(i):
        p = pp[i]
        if p["cell"] == "rl_only" and not p["t1_cap_hit"] and p["t1_generated_tokens"] < 4000:
            return "i_wrong_under_4000_rl_right"
        if p["t1_right"] and p["t1_generated_tokens"] <= 2000:
            return "ii_right_at_most_2000"
        if not p["t1_right"] and not p["t1_cap_hit"]:
            return "iii_other_wrong_finished"
        if p["t1_right"]:
            return "iv_right_over_2000"
        return None

    items, no_span = [], collections.Counter()
    for i, r in cells["T1"].items():
        gname = group(i)
        if gname is None:
            continue
        sp = answer_span(r["text"])
        if sp is None:
            no_span[gname] += 1
            continue
        mode, ext, c0, c1, head = sp
        c0 += len(r["text"][c0:]) - len(r["text"][c0:].lstrip())
        p0, p1 = tok_at(r["offsets"], c0), tok_at(r["offsets"], c1 - 1)
        lb, lr, kl = f32(r["lp_base"]), f32(r["lp_rl"]), f32(r["kl_base_rl"])
        gen = r["kind"] == 1
        it = {"problem_index": i, "group": gname, "mode": mode, "extracted": ext, "gold": r["gold"], "right": pp[i]["t1_right"],
              "failure_type": pp[i]["failure_type"], "tokens": r["n_tok"], "position": p0, "relative_position": p0 / r["n_tok"],
              "token": dec(r["tok"][p0]), "lp_base": float(lb[p0]), "lp_rl": float(lr[p0]), "D": float(lr[p0] - lb[p0]),
              "D_span": float((lr[p0:p1 + 1] - lb[p0:p1 + 1]).sum()), "span_tokens": p1 - p0 + 1,
              "rl_top1": dec(r["top1_rl"][p0]), "base_top1": dec(r["top1_base"][p0]), "rl_top1_is_written": bool(r["top1_rl"][p0] == r["tok"][p0]),
              "rank_rl": int(r["rank_rl"][p0]), "rank_base": int(r["rank_base"][p0]), "kl_base_rl": float(kl[p0]),
              "kl_percentile_in_answer": float((kl[gen] < kl[p0]).mean() * 100), "p_eos_rl": float(np.exp(f32(r["lp_eos_rl"])[p0])),
              "p_mark_rl": float(np.exp(f32(r["lp_mark_rl"])[p0])), "p_mark_base": float(np.exp(f32(r["lp_mark_base"])[p0])),
              "context_before": r["text"][max(0, c0 - 300):c0], "context_after": r["text"][c0:c0 + 120]}
        if head is not None:
            ph = tok_at(r["offsets"], head)
            it.update(D_header=float(lr[ph] - lb[ph]), header_token=dec(r["tok"][ph]), header_rl_top1=dec(r["top1_rl"][ph]))
        if not r["cap_hit"]:
            it.update(p_eos_rl_at_end=float(np.exp(lr[-1])), p_eos_base_at_end=float(np.exp(lb[-1])))
        items.append(it)
    C = {"no_extracted_span": dict(no_span), "groups": {}}
    by = collections.defaultdict(list)
    for it in items:
        by[it["group"]].append(it)
    for gname, its in sorted(by.items()):
        D = [it["D"] for it in its]
        C["groups"][gname] = {"D": quart(D), "share_D_below_minus_ln2": float(np.mean(f32(D) < -LN2)), "share_D_above_ln2": float(np.mean(f32(D) > LN2)),
                              "D_span": quart([it["D_span"] for it in its]), "D_header": quart([it["D_header"] for it in its if "D_header" in it]),
                              "lp_base": quart([it["lp_base"] for it in its]), "lp_rl": quart([it["lp_rl"] for it in its]),
                              "rl_top1_is_written_share": float(np.mean([it["rl_top1_is_written"] for it in its])),
                              "kl_percentile_in_answer": quart([it["kl_percentile_in_answer"] for it in its]),
                              "relative_position": quart([it["relative_position"] for it in its]),
                              "modes": dict(collections.Counter(it["mode"] for it in its)),
                              "written_tokens_top10": collections.Counter(it["token"] for it in its).most_common(10),
                              "rl_top1_top10": collections.Counter(it["rl_top1"] for it in its).most_common(10),
                              "p_eos_rl_at_end": quart([it["p_eos_rl_at_end"] for it in its if "p_eos_rl_at_end" in it]),
                              "p_eos_base_at_end": quart([it["p_eos_base_at_end"] for it in its if "p_eos_base_at_end" in it])}
    gi, gii, giii = (by[k] for k in ("i_wrong_under_4000_rl_right", "ii_right_at_most_2000", "iii_other_wrong_finished"))
    C["permutation_p_median_D_i_vs_ii"] = perm_median([x["D"] for x in gi], [x["D"] for x in gii])
    C["permutation_p_median_D_i_vs_iii"] = perm_median([x["D"] for x in gi], [x["D"] for x in giii])
    C["permutation_p_median_D_span_i_vs_ii"] = perm_median([x["D_span"] for x in gi], [x["D_span"] for x in gii])
    if gi and gii:
        med_i, med_ii = np.median([x["D"] for x in gi]), np.median([x["D"] for x in gii])
        r1, r2 = bool(med_i > -LN2), bool(med_ii <= -LN2 or C["permutation_p_median_D_i_vs_ii"] > 0.05)
        r3 = bool(np.median([x["kl_percentile_in_answer"] for x in gi]) < 90)
        C["verdict"] = {"median_D_i": float(med_i), "median_D_ii": float(med_ii), "refuted_1_within_factor_2": r1,
                        "refuted_2_control_shows_the_same": r2, "refuted_3_kl_at_answer_start_below_p90": r3, "H_refuted": r1 or r2 or r3}
    M["c"] = C

    # ---------------------------------------------------------------- d. the cap-hit base answers that RL solved
    caps, top_tokens, gold_rows = [], collections.Counter(), []
    for i, r in sorted(cells["T1"].items()):
        if not (pp[i]["cell"] == "rl_only" and pp[i]["t1_cap_hit"]):
            continue
        lb, lr = f32(r["lp_base"]), f32(r["lp_rl"])
        d = lr - lb
        worst = [int(p) for p in np.argsort(d)[:5]]
        pos = []
        for p in worst:
            ca, cb = r["offsets"][p]
            top_tokens[dec(r["top1_rl"][p])] += 1
            pos.append({"position": p, "relative_position": p / r["n_tok"], "token": dec(r["tok"][p]), "rl_top1": dec(r["top1_rl"][p]),
                        "lp_base": float(lb[p]), "lp_rl": float(lr[p]), "D": float(d[p]), "p_rl_top1": float(np.exp(f32(r["lp_top1_rl"])[p])),
                        "context_before": r["text"][max(0, ca - 200):ca], "context_after": r["text"][ca:ca + 80]})
        caps.append({"problem_index": i, "gold": r["gold"], "tokens": r["n_tok"], "top1_differ_share": float((r["top1_base"] != r["top1_rl"]).mean()),
                     "mean_D": float(d.mean()), "share_D_below_minus_ln2": float((d < -LN2).mean()),
                     "max_p_eos_rl": float(np.exp(f32(r["lp_eos_rl"]).max())), "max_p_eos_base": float(np.exp(f32(r["lp_eos_base"]).max())),
                     "largest_gaps": pos})
        g = r["gold"].strip()
        hits = [m for m in re.finditer(r"(?:=\s*|\bis\s+|boxed\{|[Aa]nswer\s*:?\s*)\$?(?:\\\()?\s*" + re.escape(g) + r"(?![\w^])", r["text"])]
        hits = [m for m in hits if tok_at(r["offsets"], m.end() - 1) + 51 <= r["n_tok"]]     # a full 50-token window must follow
        if hits:
            w = slice(tok_at(r["offsets"], hits[-1].end() - 1) + 1, tok_at(r["offsets"], hits[-1].end() - 1) + 51)
            pe_r, pm_r = np.exp(f32(r["lp_eos_rl"])), np.exp(f32(r["lp_mark_rl"]))
            pe_b, pm_b = np.exp(f32(r["lp_eos_base"])), np.exp(f32(r["lp_mark_base"]))
            starts = RNG.integers(0, r["n_tok"] - 50, size=200)
            gold_rows.append({"problem_index": i, "gold": g, "times_stated": len(hits), "last_statement_relative_position": w.start / r["n_tok"],
                              "context": r["text"][max(0, hits[-1].start() - 150):hits[-1].end() + 150],
                              "max_p_eos_rl": float(pe_r[w].max()), "max_p_mark_rl": float(pm_r[w].max()),
                              "max_p_eos_base": float(pe_b[w].max()), "max_p_mark_base": float(pm_b[w].max()),
                              "random_windows_median_max_p_eos_rl": float(np.median([pe_r[s:s + 50].max() for s in starts])),
                              "random_windows_median_max_p_mark_rl": float(np.median([pm_r[s:s + 50].max() for s in starts])),
                              "random_windows_median_max_p_mark_base": float(np.median([pm_b[s:s + 50].max() for s in starts]))})
    M["d"] = {"answers": len(caps), "top1_differ_share": quart([x["top1_differ_share"] for x in caps]),
              "rl_top1_at_the_5_largest_gaps_top15": top_tokens.most_common(15),
              "largest_gap_D": quart([p["D"] for x in caps for p in x["largest_gaps"]]),
              "largest_gap_relative_position": quart([p["relative_position"] for x in caps for p in x["largest_gaps"]]),
              "gold_stated_in_text": {"answers": len(gold_rows),
                                      **{k: quart([x[k] for x in gold_rows]) for k in ("max_p_eos_rl", "max_p_mark_rl", "max_p_eos_base", "max_p_mark_base",
                                                                                      "random_windows_median_max_p_eos_rl", "random_windows_median_max_p_mark_rl",
                                                                                      "random_windows_median_max_p_mark_base")}}}

    # ---------------------------------------------------------------- e. RL's own answers
    rows = cells["T2"]
    tokv = np.concatenate([r["tok"][r["kind"] >= 1] for r in rows.values()])
    klv = f32(np.concatenate([r["kl_rl_base"][r["kind"] >= 1] for r in rows.values()]))
    topv = np.concatenate([r["top1_rl"][r["kind"] >= 1] for r in rows.values()])

    def by_token(keys):
        s, n = np.bincount(keys, weights=klv), np.bincount(keys)
        return [{"token": dec(t), "id": int(t), "positions": int(n[t]), "sum_kl": float(s[t]), "share_of_total_kl": float(s[t] / klv.sum()),
                 "mean_kl": float(s[t] / n[t])} for t in np.argsort(s)[::-1][:30]]

    E = {"positions": int(len(klv)), "total_kl_rl_base": float(klv.sum()), "by_written_token_top30": by_token(tokv), "by_rl_top1_token_top30": by_token(topv)}
    for c in ("T1", "T2"):
        ends = [r for r in cells[c].values() if not r["cap_hit"]]
        pr, pb = np.exp([f32(r["lp_rl"])[-1] for r in ends]), np.exp([f32(r["lp_base"])[-1] for r in ends])
        E[f"stop_probability_at_true_end_{c}"] = {"answers": len(ends), "p_rl": quart(pr), "p_base": quart(pb),
                                                  "share_p_rl_below_0.5": float((pr < 0.5).mean()), "share_p_base_below_0.5": float((pb < 0.5).mean()),
                                                  "share_p_rl_below_0.1": float((pr < 0.1).mean()), "share_p_base_below_0.1": float((pb < 0.1).mean())}
    M["e"] = E

    (out / "metrics.json").write_text(json.dumps(M, indent=1) + "\n")
    gi_sorted = sorted(gi, key=lambda x: x["D"])
    ex = {"what": "Real items behind metrics.json. c_group_i: every group-i answer at its answer-start token, most negative D first (the first "
                  "support H, the last go against it), with the problem (input), the base answer's text around the token (output) and the score. "
                  "c_control_sample: 12 group-ii answers, evenly spaced by D. d_cap_hits: the 5 largest gaps of each cap-hit answer. d_gold_stated: the windows after the gold.",
          "c_group_i": [{**x, "problem": math[x["problem_index"]]["problem"], "score_v3": x["right"]} for x in gi_sorted],
          "c_control_sample": [{**x, "problem": math[x["problem_index"]]["problem"], "score_v3": x["right"]}
                               for x in sorted(gii, key=lambda x: x["D"])[::max(1, len(gii) // 12)]],
          "c_group_iii": sorted(giii, key=lambda x: x["D"]), "d_cap_hits": caps, "d_gold_stated": gold_rows}
    (out / "examples.json").write_text(json.dumps(ex, indent=1, ensure_ascii=False) + "\n")
    brief = {"a": {c: {k: A[c][k] for k in ("positions", "top1_differ_share_pooled", "kl_own_share_top_1pct", "kl_own_share_top_4pct", "mean_kl_own")} for c in A},
             "c": {g: {"n": v["D"].get("n"), "median_D": v["D"].get("median"), "q25": v["D"].get("q25"), "q75": v["D"].get("q75")} for g, v in C["groups"].items()},
             "verdict": C.get("verdict"), "p_i_vs_ii": C["permutation_p_median_D_i_vs_ii"]}
    print(json.dumps(brief, indent=1))


if __name__ == "__main__":
    main()
