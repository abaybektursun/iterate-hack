"""Length edge (specs/SPEC_lenedge.md): reads the per-turn table of analysis/lenedge.py and compares the training assistant-turn
lengths and Chinese content with the stored generated side (results/cap32vote, runs/drift_features). No model.

    PYTHONPATH=. uv run --no-project --with numpy --with huggingface_hub --with pyarrow --with tokenizers \
        python -m studies.rlneurons.analysis.lenedge_read --table runs/lenedge/train-01 --features runs/drift_features \
        --out studies/rlneurons/results/lenedge/train-01

Writes run.json, readout.json, table.md and examples.json to --out (a new folder).
"""
import argparse
import datetime
import glob
import json
import os
import subprocess

import numpy as np

from studies.rlneurons.analysis import lenedge as L

STUDY = "studies/rlneurons"
CAP32 = f"{STUDY}/results/cap32vote/hard328_sft1_cue_s4-01/rows.jsonl"       # Think-SFT + cue, hard328, 4 samples, cap 32,768
EDGES = [0, 2000, 4000, 6000, 8000, 10000, 12000, 14000, 16384, 20000, 24000, 28000, 32768]
MARKS = [4000, 8000, 12000, 13589, 16384, 24000, 32768]                      # 13,589: median first switch of the generated answers
QS = [50, 90, 99, 99.9]


def load(table):
    parts = sorted(glob.glob(f"{table}/part-*.json"))
    infos = [json.load(open(p)) for p in parts]
    names = sorted({s for i in infos for s in i["sources"]})
    cols = []
    for p, info in zip(parts, infos):
        t = np.load(p[:-5] + ".npz")["table"]
        t[:, L.COLS.index("source")] = np.array([names.index(s) for s in info["sources"]])[t[:, L.COLS.index("source")]]
        cols.append(np.column_stack([np.full(len(t), info["shard"]), t]))
    t = np.concatenate(cols)
    return {c: t[:, j] for j, c in enumerate(("shard",) + L.COLS)}, names, infos


def lengths(n_tok):
    q = np.percentile(n_tok, QS)
    return {"turns": int(len(n_tok)), "mean": round(float(n_tok.mean()), 1), **{f"p{p}": int(round(v)) for p, v in zip(QS, q)},
            "max": int(n_tok.max()), **{f"share_ge_{m}": float((n_tok >= m).mean()) for m in MARKS}}


def chinese(c, m):
    """Chinese content of the turns in mask m. 'English prompt' = the user turn before holds at most FLAG Chinese characters."""
    en = m & (c["user_zh"] <= L.FLAG)
    flag = en & (c["zh"] > L.FLAG)
    out = {"turns": int(m.sum()), "flagged": int((m & (c["zh"] > L.FLAG)).sum()), "english_prompt_turns": int(en.sum()),
           "english_prompt_flagged": int(flag.sum()), "english_prompt_episode": int((en & (c["ep_n"] > 0)).sum()),
           "english_prompt_any_chinese": int((en & (c["zh"] > 0)).sum())}
    out["share_flagged"] = out["flagged"] / max(1, out["turns"])
    out["share_english_prompt_flagged"] = out["english_prompt_flagged"] / max(1, out["english_prompt_turns"])
    out["share_english_prompt_episode"] = out["english_prompt_episode"] / max(1, out["english_prompt_turns"])
    if flag.sum():
        pos = c["zh_char"][flag] / c["n_chars"][flag]
        out.update(first_chinese_share_of_turn_quartiles=[round(float(x), 3) for x in np.percentile(pos, [25, 50, 75])],
                   first_chinese_token_quartiles=[int(x) for x in np.percentile(c["zh_tok"][flag], [25, 50, 75])],
                   first_chinese_inside_thinking=int((flag & ((c["think_end"] < 0) | (c["zh_char"] < c["think_end"]))).sum()),
                   chinese_share_of_characters_quartiles=[round(float(x), 4) for x in np.percentile(c["zh"][flag] / c["n_chars"][flag], [25, 50, 75])],
                   chinese_share_of_characters_max=round(float((c["zh"][flag] / c["n_chars"][flag]).max()), 4),
                   flagged_turn_tokens_median=int(np.median(c["n_tok"][flag])))
    return out


def hazard(n, first):
    """Per bin of EDGES: answers that enter the bin with no switch yet, and first switches inside it. n: tokens of each answer;
    first: token of its first switch, -1 when none."""
    out = []
    for lo, hi in zip(EDGES, EDGES[1:]):
        enter = (n >= lo) & ((first < 0) | (first >= lo))
        sw = enter & (first >= lo) & (first < hi)
        out.append({"tokens": [lo, hi], "enter_unswitched": int(enter.sum()), "first_switch": int(sw.sum()),
                    "hazard": float(sw.sum() / enter.sum()) if enter.sum() else None})
    return out


def ranks(x):
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    for v in np.unique(x):
        r[x == v] = r[x == v].mean()
    return r


def spearman(x, y, perms=10000, seed=0):
    rx, ry = ranks(np.asarray(x, float)), ranks(np.asarray(y, float))
    rho = float(np.corrcoef(rx, ry)[0, 1])
    rng = np.random.default_rng(seed)
    null = np.array([np.corrcoef(rx, rng.permutation(ry))[0, 1] for _ in range(perms)])
    return {"rho": round(rho, 3), "p_permutation_two_sided": float((np.abs(null) >= abs(rho) - 1e-12).mean()), "bins": len(rx)}


def generated(features):
    """The generated side per bin of EDGES. Precision and Chinese from the committed cap-32,768 rows; switch hazard from the
    per-sample signs of analysis/drift.py on the laptop."""
    rows = [json.loads(x) for x in open(CAP32)]
    n = np.array([r["n_new"] for r in rows])
    fin, right, zh = (np.array([f(r) for r in rows]) for f in (lambda r: not r["cap_hit"], lambda r: r["score_v3"] == 1, lambda r: r["chinese"]))
    late = n > 16384
    check = {"more_than_16384_tokens": int(late.sum()), "finished": int((late & fin).sum()), "right": int((late & right).sum()),
             "finished_right": int((late & fin & right).sum()), "with_more_than_20_chinese_characters": int((late & zh).sum())}
    posted = json.load(open(os.path.dirname(CAP32) + "/readout.json"))["late_answers"]
    assert all(check[k] == posted[k] for k in ("more_than_16384_tokens", "finished", "right", "with_more_than_20_chinese_characters")), (check, posted)
    bins = []
    for lo, hi in zip(EDGES, EDGES[1:]):
        m = (n >= lo) & (n < hi) & fin
        bins.append({"tokens": [lo, hi], "finished": int(m.sum()), "right": int((m & right).sum()), "precision": float((m & right).sum() / m.sum()),
                     "chinese": int((m & zh).sum()), "chinese_share": float((m & zh).sum() / m.sum())})
    haz = {}
    for cell in ("hard328_sft", "cap32_sft", "hard328_rl", "hard328_base"):
        f = [json.loads(x) for x in open(f"{features}/{cell}.jsonl")]
        haz[cell] = {"samples": len(f), "with_a_switch": sum(bool(r["episodes"]) for r in f),
                     "bins": hazard(np.array([r["n_tok"] for r in f]), np.array([r["episodes"][0]["detect_tok"] if r["episodes"] else -1 for r in f]))}
    return {"rows": CAP32, "samples": len(rows), "late_answers_check": check, "bins": bins, "switch_hazard": haz}


def pct(x, d=1):
    return "n/a" if x is None else f"{100 * x:.{d}f} %"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True)
    ap.add_argument("--features", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    assert not os.path.exists(a.out), f"{a.out} exists; a rerun gets the next number"
    c, names, infos = load(a.table)
    rows = sum(i["rows"] for i in infos)
    assert len(infos) == 156 and rows == L.ROWS and len(c["n_tok"]) == L.ASSISTANT_TURNS, (len(infos), rows, len(c["n_tok"]))
    every = np.ones(len(c["n_tok"]), bool)
    math_src = np.isin(c["source"], [k for k, s in enumerate(names) if "math" in s.lower()])
    groups = {"all": every, "math subset": math_src, "math subset or keyword": math_src | (c["math_kw"] == 1), "not math (neither)": ~(math_src | (c["math_kw"] == 1)),
              **{s: c["source"] == k for k, s in enumerate(names)}}
    en = c["user_zh"] <= L.FLAG
    first_ep = np.where(c["ep_n"] > 0, c["ep_tok"], -1)
    gen = generated(a.features)
    train_bins = {}
    for g in ("all", "math subset"):
        m = groups[g]
        train_bins[g] = [{"tokens": [lo, hi], "survival_at_lower_edge": float((c["n_tok"][m] >= lo).mean()),
                          "turns_ending_in_bin": int((m & (c["n_tok"] >= lo) & (c["n_tok"] < hi)).sum()),
                          "english_prompt_turns_ending_in_bin": int((m & en & (c["n_tok"] >= lo) & (c["n_tok"] < hi)).sum()),
                          "of_them_flagged": int((m & en & (c["zh"] > L.FLAG) & (c["n_tok"] >= lo) & (c["n_tok"] < hi)).sum())}
                         for lo, hi in zip(EDGES, EDGES[1:])]
        for b, h in zip(train_bins[g], hazard(c["n_tok"][m & en], first_ep[m & en])):
            b["switch_hazard"] = {k: h[k] for k in ("enter_unswitched", "first_switch", "hazard")}
    surv = [b["survival_at_lower_edge"] for b in train_bins["all"]]
    surv_math = [b["survival_at_lower_edge"] for b in train_bins["math subset"]]
    prec, zh_gen = [b["precision"] for b in gen["bins"]], [b["chinese_share"] for b in gen["bins"]]
    knee = next(k for k, b in enumerate(gen["bins"]) if b["precision"] < 0.90)
    knee_zh = next(k for k, b in enumerate(gen["bins"]) if b["chinese_share"] > 0.10)
    readout = {
        "spec": f"{STUDY}/specs/SPEC_lenedge.md", "dataset": L.W.DATASET, "revision": L.W.REVISION, "tokenizer": list(L.MODEL),
        "rows": rows, "assistant_turns": int(len(c["n_tok"])), "assistant_tokens_total": int(c["n_tok"].sum()),
        "rows_longer_than_32768_tokens_in_all_messages": int((c["ctx_tok"] + c["n_tok"] > 32768).sum()),
        "lengths": {g: lengths(c["n_tok"][m]) for g, m in groups.items()},
        "chinese": {g: chinese(c, m) for g, m in groups.items()},
        "chinese_by_length_all_sources_over_32768": chinese(c, c["n_tok"] >= 32768),
        "training_bins": train_bins, "generated": gen,
        "comparison": {
            "spearman_survival_all_vs_precision": spearman(surv, prec), "spearman_survival_math_vs_precision": spearman(surv_math, prec),
            "spearman_survival_all_vs_generated_chinese_share": spearman(surv, zh_gen),
            "spearman_bin_index_vs_precision_baseline": spearman(-np.arange(len(prec)), prec),
            "first_bin_with_precision_under_90": {"tokens": gen["bins"][knee]["tokens"], "training_survival_all": surv[knee], "training_survival_math": surv_math[knee]},
            "first_bin_with_generated_chinese_over_10": {"tokens": gen["bins"][knee_zh]["tokens"], "training_survival_all": surv[knee_zh], "training_survival_math": surv_math[knee_zh]}},
    }
    key = lambda x: x["hash"]
    examples = {"flagged_english_prompt_lowest_hash": sorted((x for i in infos for x in i["flagged"]["prompt_no_zh"]), key=key)[:L.KEEP],
                "flagged_chinese_prompt_lowest_hash": sorted((x for i in infos for x in i["flagged"]["prompt_zh"]), key=key)[:5],
                "longest": sorted((x for i in infos for x in i["longest"]), key=lambda x: -x["n_tok"])[:L.KEEP]}
    os.makedirs(a.out)
    json.dump({"command": f"python -m studies.rlneurons.analysis.lenedge_read --table {a.table} --features {a.features} --out {a.out}",
               "pass": json.load(open(f"{a.table}/pass.json")), "where": "laptop, CPU only", "job_id": None,
               "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
               "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()}, open(f"{a.out}/run.json", "w"), indent=1)
    json.dump(readout, open(f"{a.out}/readout.json", "w"), indent=1)
    json.dump(examples, open(f"{a.out}/examples.json", "w"), indent=1, ensure_ascii=False)

    T = [f"# Length edge: training assistant turns of {L.W.DATASET} against Think-SFT's generated answers\n",
         f"{rows:,} rows, {len(c['n_tok']):,} assistant turns, {c['n_tok'].sum() / 1e9:.2f} billion assistant tokens (tokenizer of {L.MODEL[0]}, "
         "every turn tokenized). A turn is the assistant message's content, thinking and answer together.\n",
         "## Tokens per assistant turn\n",
         "| Group | Turns | Mean | 50th | 90th | 99th | 99.9th | Max | at least 8,000 | 12,000 | 13,589 | 16,384 | 32,768 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for g, v in readout["lengths"].items():
        T.append(f"| {g} | {v['turns']:,} | {v['mean']:,.0f} | {v['p50']:,} | {v['p90']:,} | {v['p99']:,} | {v['p99.9']:,} | {v['max']:,} | "
                 + " | ".join(pct(v[f"share_ge_{m}"], 2) for m in (8000, 12000, 13589, 16384, 32768)) + " |")
    T += ["\n## Chinese in assistant turns (flagged: more than 20 Chinese characters; English prompt: the user turn before holds at most 20)\n",
          "| Group | Turns | Flagged | English-prompt turns | of them flagged | with a non-Latin episode | First Chinese character: share of the turn before it, quartiles | its token, quartiles | first inside the thinking | Chinese share of the turn's characters: median, max |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for g, v in readout["chinese"].items():
        q = v.get("first_chinese_share_of_turn_quartiles")
        T.append(f"| {g} | {v['turns']:,} | {v['flagged']:,} ({pct(v['share_flagged'], 3)}) | {v['english_prompt_turns']:,} | {v['english_prompt_flagged']:,} "
                 f"({pct(v['share_english_prompt_flagged'], 3)}) | {v['english_prompt_episode']:,} ({pct(v['share_english_prompt_episode'], 3)}) | "
                 + (f"{q[0]} / {q[1]} / {q[2]} | {' / '.join(f'{x:,}' for x in v['first_chinese_token_quartiles'])} | {v['first_chinese_inside_thinking']:,} | "
                    f"{pct(v['chinese_share_of_characters_quartiles'][1], 2)}, {pct(v['chinese_share_of_characters_max'], 2)} |" if q else " | | | |"))
    T += ["\n## Generated answers against training turns, by length bin\n",
          "Generated: Think-SFT + cue, hard328, 4 samples, cap 32,768 (`results/cap32vote/hard328_sft1_cue_s4-01/rows.jsonl`, 1,312 samples): finished "
          "answers whose length falls in the bin. Training: S = share of assistant turns with at least the bin's lower edge of tokens; flagged = "
          "English-prompt turns that end in the bin and hold more than 20 Chinese characters.\n",
          "| Tokens | Generated: right / finished, precision | Generated: with Chinese | Training S, all | Training S, math subset | Training turns ending in the bin, all | of them flagged (English prompt) | math subset: flagged |",
          "|---|---|---|---|---|---|---|---|"]
    for g, ta, tm in zip(gen["bins"], train_bins["all"], train_bins["math subset"]):
        T.append(f"| {g['tokens'][0]:,} to {g['tokens'][1]:,} | {g['right']} / {g['finished']}, {pct(g['precision'])} | {g['chinese']} ({pct(g['chinese_share'])}) | "
                 f"{pct(ta['survival_at_lower_edge'], 2)} | {pct(tm['survival_at_lower_edge'], 2)} | {ta['turns_ending_in_bin']:,} | "
                 f"{ta['of_them_flagged']:,} ({pct(ta['of_them_flagged'] / max(1, ta['english_prompt_turns_ending_in_bin']), 3)}) | "
                 f"{tm['of_them_flagged']:,} ({pct(tm['of_them_flagged'] / max(1, tm['english_prompt_turns_ending_in_bin']), 3)}) |")
    cmp = readout["comparison"]
    T += ["", "\n".join(f"- {k}: {json.dumps(v)}" for k, v in cmp.items()),
          "\n## First switch to a non-Latin script, by position (`drift.episodes`, the token of the 5th letter)\n",
          "Per bin: answers or turns that reach the bin with no switch yet, and those whose first switch is inside it. Generated: `runs/drift_features` "
          "(hard328, cap 16,384, 4 samples; `cap32_sft`: one sample per problem at cap 32,768). Training: English-prompt assistant turns.\n",
          "| Tokens | Think-SFT cap 16,384 | Think-SFT cap 32,768 | RL plain | base + cue | Training, all | Training, math subset |", "|---|---|---|---|---|---|---|"]
    hz = gen["switch_hazard"]
    cell = lambda h: f"{h['first_switch']:,} / {h['enter_unswitched']:,} ({pct(h['hazard'], 2 if h['enter_unswitched'] < 100000 else 3)})"
    for k in range(len(EDGES) - 1):
        T.append(f"| {EDGES[k]:,} to {EDGES[k + 1]:,} | " + " | ".join(cell(hz[x]["bins"][k]) for x in ("hard328_sft", "cap32_sft", "hard328_rl", "hard328_base"))
                 + f" | {cell(train_bins['all'][k]['switch_hazard'])} | {cell(train_bins['math subset'][k]['switch_hazard'])} |")
    open(f"{a.out}/table.md", "w").write("\n".join(T) + "\n")
    print("\n".join(T))


if __name__ == "__main__":
    main()
