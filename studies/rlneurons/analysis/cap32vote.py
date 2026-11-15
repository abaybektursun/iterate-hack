"""cap32vote readout (specs/SPEC_cap32vote.md): four samples of one model at a cap of 32,768 generated tokens, each answer scored
twice from the same text: as written (32,768), and cut after its 16,384th generated token and graded by grader v3 as the cap
hit a 16,384 run would have stored (16,384 view).

    uv run --no-project --with numpy --with math-verify==0.9.0 --with transformers==5.19.0 --with tokenizers==0.23.3 --with huggingface_hub --with jinja2 \
        python -m studies.rlneurons.analysis.cap32vote --run runs/<joined run of 4 samples> --stored studies/rlneurons/results/<16,384 run folder> \
        --rl studies/rlneurons/results/<RL 16,384 run folder> --out studies/rlneurons/results/cap32vote/<arm>-01

  --run     thinkvote_join's folder (answers.jsonl with the texts, metrics.json), max_tokens 32,768.
  --stored  day1_vote's folder of the same model, seeds and set at cap 16,384 (rows.jsonl): the unpaired reference.
  Rules not in the spec (added after the hard328 rows were read): seq4_short, vote4_short (ties to the shortest answer) and gate12000
  (one sample at a time; a finished answer of at most 12,000 tokens is taken at once, else stop when two agree, at most 4).
  --rl      day1_vote's folder of RL plain at cap 16,384 on the same set (readout.json: per-problem vote and single).
Writes run.json, metrics.json, rows.jsonl (no text; the 16,384 view in the *_16 fields), readout.json, readout.md, examples.json.
Rules with tokens: frontier.replay on both views (24 draw orders). Differences: paired bootstrap over problems, 5,000 resamples.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import shutil

import numpy as np

from studies.rlneurons.analysis import day1_vote as V
from studies.rlneurons.analysis import frontier as F
from studies.rlneurons.analysis.cap32vote_sim import restart1
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
OLD, NEW, BOOT = 16384, 32768, 5000
RULES = {**{m: F.RULES[m] for m in ("single", "vote2", "seq3", "seq4", "vote4", "seq4_short", "vote4_short")}, "restart1": restart1,
         "gate12000": {"plan": [1, 1, 1, 1], "stop_n": 12000}}   # *_short: not in the spec
PUBLISHED = ("aime2026", "hmmt_feb2026")
# specs/SPEC_cap32vote.md, commit 9d4ddf6: (predicted, low, high); None = no interval stated
PRED = {"hard328": {"vote4_32": (239.5, 232, 248), "single_32": (229.0, 224.5, 233.2), "cap_hit_percent_32": (0.6, None, None), "precision_percent_32": (70, 62, 78),
                    "late_wrong_pairs_agree_percent": (64, None, None), "single_32_tokens": (11820, None, None), "seq4_32_right_24": (237, None, None)},
        "fresh2026": {"vote4_32": (77.0, 71, 83), "single_32": (74.5, 71.2, 78.0), "cap_hit_percent_32": (1.0, None, None), "precision_percent_32": (55, 47, 63),
                      "late_wrong_pairs_agree_percent": (75, None, None), "single_32_tokens": (15600, None, None)}}
RESTART1_STORED = {"hard328": 222.0, "fresh2026": 68.0}     # the 16,384 rule H4 names, from the stored rows (results/cap32vote/sim-01)


def chinese(text: str) -> bool:
    return sum("一" <= c <= "鿿" for c in text) > 20


def cut(tok, fz: dict, r: dict) -> dict:
    """The row a 16,384 run would have stored for this answer."""
    if r["n_new"] <= OLD:
        return r
    ids, offs = R.encode_answer(tok, r["text"], fz["prefill_text"], fz["prefill_ids"])
    k = r["n_prefix"] + OLD
    assert len(ids) > k - 64, f"problem {r['problem_index']} sample {r['sample']}: {len(ids)} tokens in the text, n_new {r['n_new']}"
    text = r["text"][: offs[min(k, len(ids)) - 1][1]]
    return {**r, "text": text, "n_new": OLD, "cap_hit": True, "finish_reason": "length", **R.grade_v3(r["gold"], text)}


def view(rows: list, n: int) -> dict:
    res, _ = V.readout(rows, n, 4, 0)
    ch = V.chains(rows, n, 4, 0)
    per = F.replay(ch, RULES)
    fin = [r for r in rows if not r["cap_hit"]]
    by = collections.defaultdict(list)
    for r in rows:
        by[r["problem_index"]].append(r["score_v3"])
    return {"idx": res["problem_indices"], "single_each": res["each_sample"]["single_right"], "single": [float(np.mean(by[i])) for i in res["problem_indices"]],
            "vote": res["per_problem"]["vote"], "pass": res["per_problem"]["pass_at_k"], "cap_hits": len(rows) - len(fin),
            "finished": len(fin), "finished_right": sum(r["score_v3"] for r in fin), "cap_hits_with_answer": sum(r["cap_hit"] and r["extracted_v3"] is not None for r in rows),
            "cap_hits_right": sum(r["cap_hit"] and r["score_v3"] for r in rows), "tokens_per_sample": sum(r["n_new"] for r in rows) / len(rows),
            "vote_ties": res["vote_stats"]["ties_for_first"], "per": per}


def stats(v: dict, keep: list) -> dict:
    k = [j for j, i in enumerate(v["idx"]) if i in keep]
    s = lambda x: float(sum(x[j] for j in k))
    return {"n": len(k), "single_mean_of_4": round(s(v["single"]), 2), "vote4": int(s(v["vote"])), "pass_at_4": int(s(v["pass"])),
            "rules": {m: {"right": int(s(p["s0"])), "right_24": round(s(p["s"]), 1), "tokens": round(s(p["t0"]) / len(k)), "tokens_24": round(s(p["t"]) / len(k))} for m, p in v["per"].items()}}


def diff(x, y, keep_pos: list) -> dict:
    x, y = [x[j] for j in keep_pos], [y[j] for j in keep_pos]
    lo, hi = S.paired_bootstrap(x, y, BOOT)
    return {"problems": round(float(sum(x) - sum(y)), 2), "points": round(100 * float(np.mean(x) - np.mean(y)), 2), "interval95": [round(lo, 2), round(hi, 2)]}


def main():
    ap = argparse.ArgumentParser()
    for k in ("--run", "--stored", "--rl", "--out"):
        ap.add_argument(k, required=True)
    a = ap.parse_args()
    run, out = pathlib.Path(a.run), pathlib.Path(a.out)
    assert not out.exists(), f"{out} exists: a rerun gets the next number"
    m = json.loads((run / "metrics.json").read_text())
    cfg = m["config"]
    assert m["status"] == "done" and cfg["max_tokens"] == NEW and cfg["samples"] == 4 and cfg["restarts"] == 0, "not a finished 4-sample run at 32,768"
    name, n = cfg["set"], cfg["n_problems"]
    rows = sorted((json.loads(l) for l in (run / "answers.jsonl").read_text().splitlines()), key=lambda r: (r["problem_index"], r["sample"]))
    fz = json.loads((STUDY / "data" / "rln4" / "frozen4.json").read_text())
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"]))
    rows16 = [cut(tok, fz, r) for r in rows]
    v32, v16 = view(rows, n), view(rows16, n)
    idx = v32["idx"]

    if name == "hard328":
        flags = json.loads((STUDY / "results" / "wsp1" / "sft_overlap-03" / "flags.json").read_text())["hard"]
        groups = {"all": idx, "not in Think-SFT's training data (322)": [i for i in idx if flags[str(i)]["flag"] == "none"]}
    else:
        src = {p["index"]: p["source"] for p in json.loads((STUDY / "data" / "fresh" / "fresh2026_v1.json").read_text())}
        groups = {"all": idx, "published (AIME 2026 + HMMT Feb 2026, 59)": [i for i in idx if src[i] in PUBLISHED],
                  "transcribed (HMMT Feb Guts + HMMT Nov, 77)": [i for i in idx if src[i] not in PUBLISHED]}
    rl = json.loads((pathlib.Path(a.rl) / "readout.json").read_text())
    assert rl["problem_indices"] == idx, "the RL run is on other problems"
    rl_single = collections.defaultdict(list)
    for l in (pathlib.Path(a.rl) / "rows.jsonl").read_text().splitlines():
        r = json.loads(l)
        if r["attempt"] == 0:
            rl_single[r["problem_index"]].append(r["score_v3"])
    rl_single = [float(np.mean(rl_single[i])) for i in idx]
    res = {"spec": "studies/rlneurons/specs/SPEC_cap32vote.md", "set": name, "n": n, "run": str(run), "job_id": m["job_id"], "groups": {}}
    for g, keep in groups.items():
        pos = [j for j, i in enumerate(idx) if i in set(keep)]
        res["groups"][g] = {
            "at_32768": stats(v32, set(keep)), "at_16384_same_answers": stats(v16, set(keep)),
            "rl_plain_16384_stored": {"vote4": int(sum(rl["per_problem"]["vote"][j] for j in pos)), "single_mean_of_4": round(sum(rl_single[j] for j in pos), 2)},
            "differences": {"single, 32768 minus 16384": diff(v32["single"], v16["single"], pos), "vote4, 32768 minus 16384": diff(v32["vote"], v16["vote"], pos),
                            "seq4 (24 orders), 32768 minus 16384": diff(v32["per"]["seq4"]["s"], v16["per"]["seq4"]["s"], pos),
                            "vote4_short (ties to the shortest; not in the spec), 32768 minus 16384": diff(v32["per"]["vote4_short"]["s"], v16["per"]["vote4_short"]["s"], pos),
                            "vote4_short at 32768 minus vote4 at 16384": diff(v32["per"]["vote4_short"]["s"], v16["vote"], pos),
                            "vote4_short at 32768 minus RL vote4 (stored 16384)": diff(v32["per"]["vote4_short"]["s"], rl["per_problem"]["vote"], pos),
                            "single at 32768 minus restart1 at 16384 (24 orders)": diff(v32["single"], v16["per"]["restart1"]["s"], pos),
                            "single at 32768 minus vote2 at 16384 (24 orders)": diff(v32["single"], v16["per"]["vote2"]["s"], pos),
                            "vote4 at 32768 minus RL vote4 (stored 16384)": diff(v32["vote"], rl["per_problem"]["vote"], pos),
                            "vote4 at 16384 minus RL vote4 (stored 16384)": diff(v16["vote"], rl["per_problem"]["vote"], pos),
                            "single at 32768 minus RL single (stored 16384)": diff(v32["single"], rl_single, pos)}}
    for k, v in (("at_32768", v32), ("at_16384_same_answers", v16)):
        res[k] = {"single_each": v["single_each"], "cap_hits": v["cap_hits"], "cap_hit_percent": round(100 * v["cap_hits"] / len(rows), 2),
                  "cap_hits_with_an_extracted_answer": v["cap_hits_with_answer"], "cap_hits_right": v["cap_hits_right"],
                  "finished": v["finished"], "finished_right": v["finished_right"], "precision_percent": round(100 * v["finished_right"] / v["finished"], 2),
                  "tokens_per_sample": round(v["tokens_per_sample"]), "vote_ties_for_first": v["vote_ties"]}

    late = [r for r in rows if r["n_new"] > OLD]
    lw = collections.defaultdict(list)
    for r in late:
        if not r["cap_hit"] and not r["score_v3"] and r["extracted_v3"] is not None:
            lw[r["problem_index"]].append(R.norm_v3(r["extracted_v3"]))
    pairs = [R.agree(x, y) for v in lw.values() for j, x in enumerate(v) for y in v[j + 1:]]
    vote_by = {i: (v32["vote"][j], v16["vote"][j]) for j, i in enumerate(idx)}
    res["late_answers"] = {
        "more_than_16384_tokens": len(late), "finished": sum(not r["cap_hit"] for r in late), "right": sum(r["score_v3"] for r in late),
        "finished_wrong": sum(not r["cap_hit"] and not r["score_v3"] for r in late), "finished_without_extracted_answer": sum(not r["cap_hit"] and r["extracted_v3"] is None for r in late),
        "still_cut_at_32768": sum(r["cap_hit"] for r in late), "per_sample": [sum(r["sample"] == s for r in late) for s in range(4)],
        "right_per_sample": [sum(r["score_v3"] for r in late if r["sample"] == s) for s in range(4)],
        "wrong_pairs_of_one_problem": len(pairs), "wrong_pairs_agree": int(sum(pairs)), "wrong_pairs_agree_percent": round(100 * float(np.mean(pairs)), 1) if pairs else None,
        "with_more_than_20_chinese_characters": sum(chinese(r["text"]) for r in late),
        "still_cut_with_more_than_20_chinese_characters": sum(chinese(r["text"]) for r in late if r["cap_hit"]),
        "right_with_more_than_20_chinese_characters": sum(chinese(r["text"]) for r in late if r["score_v3"]),
        "loop_A": sum(r["loop_A"] for r in late), "still_cut_loop_A": sum(r["loop_A"] for r in late if r["cap_hit"]),
        "median_tokens_of_finished": float(np.median([r["n_new"] for r in late if not r["cap_hit"]])),
        "vote_changed": {"wrong to right": sum(a > b for a, b in vote_by.values()), "right to wrong": sum(a < b for a, b in vote_by.values()),
                         "right to wrong problems": [i for i, (a, b) in vote_by.items() if a < b], "wrong to right problems": [i for i, (a, b) in vote_by.items() if a > b]}}

    st = {(r["problem_index"], r["sample"]): r for r in map(json.loads, (pathlib.Path(a.stored) / "rows.jsonl").read_text().splitlines()) if r["attempt"] == 0}
    assert sorted(st) == [(r["problem_index"], r["sample"]) for r in rows] and all(st[r["problem_index"], r["sample"]]["seed"] == r["seed"] for r in rows), "the stored run has other requests"
    same = [st[r["problem_index"], r["sample"]]["n_new"] == r["n_new"] and st[r["problem_index"], r["sample"]]["extracted_v3"] == r["extracted_v3"] for r in rows16]
    sro = json.loads((pathlib.Path(a.stored) / "readout.json").read_text())
    res["stored_16384_run"] = {"folder": a.stored, "single_each": sro["each_sample"]["single_right"], "vote4": sro["rows"]["vote"]["right"],
                               "cap_hits": sum(r["cap_hit"] for r in st.values()),
                               "finished_rows_with_the_same_tokens_and_answer_as_the_16384_view": int(sum(x for x, r in zip(same, rows16) if not r["cap_hit"])), "finished_rows_in_the_16384_view": sum(not r["cap_hit"] for r in rows16)}
    al, a16 = res["groups"]["all"]["at_32768"], res["groups"]["all"]["at_16384_same_answers"]
    obs = {"vote4_32": al["vote4"], "single_32": al["single_mean_of_4"], "cap_hit_percent_32": res["at_32768"]["cap_hit_percent"],
           "precision_percent_32": res["at_32768"]["precision_percent"], "late_wrong_pairs_agree_percent": res["late_answers"]["wrong_pairs_agree_percent"],
           "single_32_tokens": res["at_32768"]["tokens_per_sample"], "seq4_32_right_24": al["rules"]["seq4"]["right_24"]}
    res["predictions"] = {k: {"predicted": p, "interval": [lo, hi], "observed": obs[k], "inside": None if lo is None else bool(lo <= obs[k] <= hi)} for k, (p, lo, hi) in PRED[name].items()}
    d = res["groups"]["all"]["differences"]
    res["hypotheses"] = {
        "H1 vote4 at 32768 >= 250 on hard328, and its gain over the 16384 vote has an interval above 0": None if name != "hard328" else
            {"vote4": al["vote4"], "gain": d["vote4, 32768 minus 16384"], "held": bool(al["vote4"] >= 250 and d["vote4, 32768 minus 16384"]["interval95"][0] > 0)},
        "H2 vote gain in points smaller than single gain": {"vote": d["vote4, 32768 minus 16384"]["points"], "single": d["single, 32768 minus 16384"]["points"],
                                                            "held": bool(d["vote4, 32768 minus 16384"]["points"] < d["single, 32768 minus 16384"]["points"])},
        "H3 single gain in points (compare the two sets)": d["single, 32768 minus 16384"],
        "H4 one sample at 32768 above restart1 at 16384 (stored rows)": {"single_32": al["single_mean_of_4"], "tokens": res["at_32768"]["tokens_per_sample"],
                                                                          "restart1_stored": RESTART1_STORED[name], "held": bool(al["single_mean_of_4"] > RESTART1_STORED[name]),
                                                                          "restart1_same_answers": a16["rules"]["restart1"], "paired": d["single at 32768 minus restart1 at 16384 (24 orders)"]},
        "H4b seq4 at 32768 not above seq4 at 16384": {"paired": d["seq4 (24 orders), 32768 minus 16384"], "held": bool(d["seq4 (24 orders), 32768 minus 16384"]["interval95"][0] <= 0)}}

    out.mkdir(parents=True)
    shutil.copy(run / "metrics.json", out / "metrics.json")
    (out / "run.json").write_text(json.dumps({"commit": m["commit"], "job_id": m["job_id"], "joined_from": m.get("joined_from"), "config": cfg, "source": str(run),
                                              "raw_answers": "s3://iterate-hack-team-769063704696/handoff/cap32vote/<job-id>/answers.jsonl"}, indent=1) + "\n")
    (out / "readout.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "rows.jsonl").write_text("".join(json.dumps({**{k: r[k] for k in V.COMPACT}, "n_new_16": c["n_new"], "cap_hit_16": c["cap_hit"], "extracted_v3_16": c["extracted_v3"],
                                                        "score_v3_16": c["score_v3"], "chinese": chinese(r["text"])}) + "\n" for r, c in zip(rows, rows16)))
    ex = lambda r: None if r is None else {**{k: r[k] for k in ("problem_index", "sample", "seed", "gold", "extracted_v3", "score_v3", "n_new", "cap_hit")},
                                           "prompt": r["prompt"], "text_at_16384_last_600": cut(tok, fz, r)["text"][-600:], "text_last_1500": r["text"][-1500:]}
    (out / "examples.json").write_text(json.dumps({"right_after_16384": ex(next((r for r in late if r["score_v3"]), None)),
                                                   "wrong_after_16384": ex(next((r for r in late if not r["cap_hit"] and not r["score_v3"]), None)),
                                                   "still_cut_at_32768": ex(next((r for r in late if r["cap_hit"]), None))}, indent=1) + "\n")
    md = [f"# cap32vote, {name}, n = {n}: Think-SFT + cue, 4 samples, each answer scored at 16,384 and at 32,768 tokens", "",
          "| group | cap | single, the 4 samples | single, mean | vote over 4 | pass@4 | cap hits | precision of finished | tokens per sample |", "|---|---|---|---|---|---|---|---|---|"]
    for g, x in res["groups"].items():
        for k, lab in (("at_16384_same_answers", "16,384"), ("at_32768", "32,768")):
            t = res[k] if g == "all" else None
            md.append(f"| {g} | {lab} | {t['single_each'] if t else ''} | {x[k]['single_mean_of_4']:.1f} | {x[k]['vote4']} | {x[k]['pass_at_4']} | "
                      + (f"{t['cap_hits']} ({t['cap_hit_percent']:.1f} %) | {t['precision_percent']:.1f} % ({t['finished_right']} of {t['finished']}) | {t['tokens_per_sample']:,} |" if t else " | | |"))
        md.append(f"| {g} | RL plain, 16,384 (stored) | | {x['rl_plain_16384_stored']['single_mean_of_4']:.1f} | {x['rl_plain_16384_stored']['vote4']} | | | | |")
    md += ["", "| group | difference | problems | points [95 %] |", "|---|---|---|---|"]
    md += [f"| {g} | {k} | {v['problems']:+.1f} | {v['points']:+.1f} [{v['interval95'][0]:+.1f}, {v['interval95'][1]:+.1f}] |" for g, x in res["groups"].items() for k, v in x["differences"].items()]
    md += ["", "| rule (all problems) | cap | right (stored order) | right (24 orders) | tokens per problem (stored order) | tokens (24 orders) |", "|---|---|---|---|---|---|"]
    md += [f"| `{r}` | {lab} | {x['right']} | {x['right_24']} | {x['tokens']:,} | {x['tokens_24']:,} |" for r in RULES for k, lab in (("at_16384_same_answers", "16,384"), ("at_32768", "32,768"))
           for x in [res["groups"]["all"][k]["rules"][r]]]
    md += ["", "Late answers (more than 16,384 tokens): " + json.dumps(res["late_answers"]), "", "Stored 16,384 run: " + json.dumps(res["stored_16384_run"]), "",
           "Predictions: " + json.dumps(res["predictions"]), "", "Hypotheses: " + json.dumps(res["hypotheses"]), ""]
    (out / "readout.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
