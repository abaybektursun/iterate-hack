"""Seen against unseen (specs/SPEC_seen.md): the 72 harder problems that are in the RL training prompts (43 exact, 29 near) against
130 source-matched unseen ones, four arms, 4 samples per problem at T 1.0 / top-p 1.0, grader v3 as written by run_cell.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.seen [--read]

Run from the repository root. Inputs (not committed): runs/<job-id>/answers.jsonl and metrics.json of the jobs in JOBS
(`uv run tools/gpu.py get <job-id>`). Writes results/seen/readout.json, readout.md and one run folder per arm and set
(run.json, metrics.json, rows.jsonl without texts, examples.json). --read prints, instead, RL's answers on the seen problems that
RL solves (at least 3 of 4) and the base does not (at most 1 of 4), for the hand read.

D(control) = [acc(RL) - acc(control)] on seen minus the same on unseen, in points. Every unseen number is the mean of the family
means (AIME, AMC 23, OlympiadBench) weighted by the family shares of the seen set it is compared with. Bootstrap over problems:
seen problems and each unseen family resampled separately, all arms together, 5,000 resamples, seed 0, 95 % percentile.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil

import numpy as np

from studies.rlneurons.analysis.day1_vote import compact, vote

STUDY = pathlib.Path(__file__).resolve().parents[1]
RUNS = pathlib.Path("runs")
OUT = STUDY / "results" / "seen"
BOOT, SAMPLES = 5000, 4
ARMS = ("base", "rl", "code", "sft")
LABEL = {"base": "base, cue", "rl": "RL, plain", "code": "Code-RL, cue", "sft": "Think-SFT, cue"}
CONTROLS = ("code", "base", "sft")
# arm -> set -> job id. base and rl on the unseen set: the hard328 jobs of work-1a972a (--samples 4 --restarts 2; attempt 0 used).
JOBS = {
    "base": {"hard72": "", "hardmatch": "abaybektursun-1114-200457-e8e6"},
    "rl": {"hard72": "", "hardmatch": "abaybektursun-1114-200505-5ff2"},
    "code": {"hard72": "", "hardmatch": ""},
    "sft": {"hard72": "", "hardmatch": ""},
}


def family(source):
    return "aime" if source.startswith("aime") else source


def sets():
    """{problem index: (group, family)}: group exact or near (the 72) or unseen (the 130 of run_cell --set hardmatch)."""
    hard = json.loads((STUDY / "data" / "rln3" / "hard.json").read_text())
    flags = json.loads((STUDY / "results" / "rln3" / "rln3_overlap.json").read_text())["sets"]["hard"]["flags"]
    clean = sorted(int(i) for i, f in flags.items() if f["flag"] == "none")
    oly = [i for i in clean if hard[i]["source"] == "olympiadbench"]
    match = [i for i in clean if hard[i]["source"].startswith(("aime", "amc"))] + oly[::6]
    meta = {i: ("unseen", family(hard[i]["source"])) for i in match}
    meta.update({int(i): (f["flag"], family(hard[int(i)]["source"])) for i, f in flags.items() if f["flag"] != "none"})
    assert len(meta) == 202 and len(match) == 130
    return meta


def per_problem(rows, idx):
    """rows of one job -> {problem index: {ps, vote, tok, cap, n}} over attempt 0 of each sample; idx: the problems wanted.
    Returns it with the number of missing rows (a job that died near its end)."""
    by = {i: [] for i in idx}
    for r in rows:
        if r["attempt"] == 0 and r["problem_index"] in by:
            by[r["problem_index"]].append(r)
    out, missing = {}, 0
    for i, rs in by.items():
        rs = sorted(rs, key=lambda r: r["sample"])
        assert [r["sample"] for r in rs] == sorted({r["sample"] for r in rs}) and len(rs) <= SAMPLES, i
        missing += SAMPLES - len(rs)
        assert rs, f"problem {i} has no row"
        out[i] = {"ps": float(np.mean([r["score_v3"] for r in rs])), "vote": int(vote(rs)["score"]),
                  "tok": float(np.mean([r["n_new"] for r in rs])), "cap": float(np.mean([r["cap_hit"] for r in rs])), "n": len(rs)}
    return out, missing


def contrast(val, seen, unseen, rng=None):
    """val: {arm: {index: value}}; seen: [indices]; unseen: {family: [indices]}; the seen set's family shares weight the unseen
    families. Returns {arm: (seen mean, unseen weighted mean)} in the units of val; with rng, of one bootstrap resample."""
    fam_w = {f: w for f, w in seen["weights"].items() if w > 0}
    s = seen["idx"] if rng is None else list(rng.choice(seen["idx"], len(seen["idx"])))
    u = {f: (unseen[f] if rng is None else list(rng.choice(unseen[f], len(unseen[f])))) for f in fam_w}
    return {a: (float(np.mean([v[i] for i in s])), float(sum(w * np.mean([v[i] for i in u[f]]) for f, w in fam_w.items())))
            for a, v in val.items()}


def stats(val, seen_idx, meta, boot=BOOT):
    """Every number of one seen subset and one metric, in points (val in 0..1): per arm seen, unseen, seen - unseen; per control
    RL - control on seen, on unseen, and D; each with a 95 % bootstrap interval."""
    fams = [meta[i][1] for i in seen_idx]
    seen = {"idx": list(seen_idx), "weights": {f: fams.count(f) / len(fams) for f in sorted(set(fams))}}
    unseen = {f: [i for i, (g, ff) in meta.items() if g == "unseen" and ff == f] for f in seen["weights"]}

    def numbers(c):
        o = {}
        for a, (s, u) in c.items():
            o[f"{a} seen"], o[f"{a} unseen"], o[f"{a} seen - unseen"] = s, u, s - u
        for k in CONTROLS:
            if k in c:
                ds, du = c["rl"][0] - c[k][0], c["rl"][1] - c[k][1]
                o[f"rl - {k} seen"], o[f"rl - {k} unseen"], o[f"D({k})"] = ds, du, ds - du
        return o

    point = numbers(contrast(val, seen, unseen))
    rng = np.random.default_rng(0)
    bs = [numbers(contrast(val, seen, unseen, rng)) for _ in range(boot)]
    res = {k: {"points": round(100 * v, 2), "interval95": [round(100 * float(x), 2) for x in np.percentile([b[k] for b in bs], [2.5, 97.5])]}
           for k, v in point.items()}
    return {"n_seen": len(seen_idx), "family_weights": seen["weights"], "n_unseen": {f: len(v) for f, v in unseen.items()}, **res}


def load(job):
    m = json.loads((RUNS / job / "metrics.json").read_text())
    rows = [json.loads(l) for l in (RUNS / job / "answers.jsonl").open()]
    return m, rows


def examples(rows):
    def ex(r):
        return {k: r[k] for k in ("problem_index", "sample", "seed", "gold", "extracted_v3", "score_v3", "n_new", "cap_hit", "prompt")} | {
            "text_first_1500": r["text"][:1500], "text_last_2000": r["text"][-2000:]}
    fin = [r for r in rows if not r["cap_hit"]]
    return {"right": ex(next(r for r in fin if r["score_v3"] == 1)), "wrong": ex(next(r for r in fin if r["score_v3"] == 0))}


def read(data, meta, rows):
    """Print RL's answers on seen problems RL solves (>= 3 of 4) and the base does not (<= 1 of 4)."""
    pick = [i for i, (g, _) in sorted(meta.items()) if g != "unseen" and data["rl"][i]["ps"] >= 0.75 and data["base"][i]["ps"] <= 0.25]
    print(len(pick), "seen problems: RL >= 3 of 4, base <= 1 of 4:", pick)
    for i in pick:
        for r in sorted((r for r in rows["rl"]["hard72"] if r["problem_index"] == i), key=lambda r: r["sample"])[:2]:
            print(f"\n===== problem {i} ({meta[i]}) sample {r['sample']} n_new {r['n_new']} score {r['score_v3']} gold {r['gold']}")
            print(r["text"][:1200], "\n[...]\n", r["text"][-500:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--read", action="store_true")
    a = ap.parse_args()
    meta = sets()
    want = {"hard72": [i for i, (g, _) in meta.items() if g != "unseen"], "hardmatch": [i for i, (g, _) in meta.items() if g == "unseen"]}
    data, rows, runs = {x: {} for x in ARMS}, {x: {} for x in ARMS}, {}
    for arm in ARMS:
        for st, job in JOBS[arm].items():
            m, rs = load(job)
            rs = [r for r in rs if r["attempt"] == 0 and r["problem_index"] in set(want[st])]
            d, missing = per_problem(rs, want[st])
            assert missing < 0.02 * SAMPLES * len(want[st]), f"{job}: {missing} rows missing, 2 % or more"
            assert m["config"]["temperature"] == 1.0 and m["config"]["top_p"] == 1.0 and m["config"]["seed"] == 3000000 and m["job_id"] == job
            data[arm].update(d)
            rows[arm][st] = rs
            runs[f"{arm}_{st}"] = {"job_id": job, "status": m["status"], "commit": m["commit"], "rows": len(rs), "rows_missing": missing,
                                   "model": m["config"].get("model_repo") or m["config"]["model_label"], "prompt": m["config"]["prompt"],
                                   "set_of_job": m["config"]["set"], "restarts_of_job": m["config"]["restarts"]}
    if a.read:
        return read(data, meta, rows)

    groups = {"all 72": want["hard72"], "exact 43": [i for i in want["hard72"] if meta[i][0] == "exact"],
              "near 29": [i for i in want["hard72"] if meta[i][0] == "near"]}
    res = {"spec": "studies/rlneurons/specs/SPEC_seen.md", "grader": "v3 (run_cell)", "bootstrap": {"resamples": BOOT, "seed": 0}, "runs": runs}
    for metric, name in (("ps", "per_sample"), ("vote", "vote_over_4"), ("tok", "tokens_per_answer"), ("cap", "cap_hit_share")):
        val = {arm: {i: (d[metric] / 100 if metric == "tok" else d[metric]) for i, d in data[arm].items()} for arm in ARMS}
        res[name] = {g: stats(val, idx, meta) for g, idx in groups.items()}                 # tokens: "points" are tokens
    res["per_problem"] = {arm: {str(i): data[arm][i] for i in sorted(data[arm])} for arm in ARMS}
    res["problems"] = {str(i): list(meta[i]) for i in sorted(meta)}

    OUT.mkdir(parents=True, exist_ok=True)
    for arm in ARMS:
        for st, job in JOBS[arm].items():
            d = OUT / f"{arm}_{st}-01"
            assert not d.exists(), f"{d} exists: a rerun gets the next number"
            d.mkdir()
            m = json.loads((RUNS / job / "metrics.json").read_text())
            (d / "run.json").write_text(json.dumps({**runs[f"{arm}_{st}"], "config": m["config"],
                                                    "raw_answers": f"runs/{job}/answers.jsonl (uv run tools/gpu.py get {job})"}, indent=1) + "\n")
            shutil.copy(RUNS / job / "metrics.json", d / "metrics.json")
            (d / "rows.jsonl").write_text(compact(rows[arm][st]))
            (d / "examples.json").write_text(json.dumps(examples(rows[arm][st]), indent=1) + "\n")
    (OUT / "readout.json").write_text(json.dumps(res, indent=1) + "\n")

    def cell(s, k, digits=1):
        return f"{s[k]['points']:.{digits}f} [{s[k]['interval95'][0]:.{digits}f}, {s[k]['interval95'][1]:.{digits}f}]"

    md = ["# Seen against unseen: readout (`analysis/seen.py`, spec `specs/SPEC_seen.md`)", "",
          "Percent right with grader v3, 4 samples per problem, T 1.0 / top-p 1.0; 95 % bootstrap interval over problems. Unseen =",
          "family means of the 130 unseen problems weighted by the seen set's family shares. Tokens = generated tokens per answer.", ""]
    for g in groups:
        ps, vt, tk = res["per_sample"][g], res["vote_over_4"][g], res["tokens_per_answer"][g]
        md += [f"## {g} (unseen families: {ps['n_unseen']}, weights {({f: round(w, 3) for f, w in ps['family_weights'].items()})})", "",
               "| Arm | Per sample: seen | unseen | seen - unseen | Vote over 4: seen | unseen | seen - unseen | Tokens: seen | unseen |",
               "|---|---|---|---|---|---|---|---|---|"]
        md += [f"| {LABEL[x]} | {ps[f'{x} seen']['points']:.1f} | {ps[f'{x} unseen']['points']:.1f} | {cell(ps, f'{x} seen - unseen')} | "
               f"{vt[f'{x} seen']['points']:.1f} | {vt[f'{x} unseen']['points']:.1f} | {cell(vt, f'{x} seen - unseen')} | "
               f"{100 * tk[f'{x} seen']['points']:,.0f} | {100 * tk[f'{x} unseen']['points']:,.0f} |" for x in ARMS]
        md += ["", "| Control | Per sample: RL - control, seen | unseen | D | Vote over 4: RL - control, seen | unseen | D |", "|---|---|---|---|---|---|---|"]
        md += [f"| {LABEL[k]} | {cell(ps, f'rl - {k} seen')} | {cell(ps, f'rl - {k} unseen')} | {cell(ps, f'D({k})')} | "
               f"{cell(vt, f'rl - {k} seen')} | {cell(vt, f'rl - {k} unseen')} | {cell(vt, f'D({k})')} |" for k in CONTROLS]
        md += [""]
    (OUT / "readout.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
