"""Freeze the per-problem rows the depth/rank paper needs that are not yet in git, and pick the examples (needs the raw texts).

    uv run --no-project python studies/rlneurons/paper-depth-rank/prep_rows.py

Reads runs/<job-id>/answers.jsonl (and edit.json) of the jobs below, from any `../iterate-hack*/runs/` folder next to this
repository (`uv run tools/gpu.py get <job-id>` fetches one). Writes, next to this file:
  data/math/<cell>.jsonl   hard328 rows (attempt 0, sample 0): problem_index, seed, score_v3, cap_hit, n_new, extracted_v3, gold
  data/code/<cell>.jsonl   HumanEval+ / MBPP+ rows: uid, bench, seed, passed, cap_hit, mode, exit, n_new
  data/edit_totals.json    edit.json "totals" (Frobenius norms of the weight change) of every job that has one
  examples.json            AGENTS.md Results 6: one right and one wrong item per main cell, plus the problems where
                           directions 2-8 are right and the base (same seed) is cut off
Every frozen cell is asserted against its committed readout (right / cap hits / tokens). Fails if data/ exists.
"""
import glob
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
RES = STUDY / "results" / "xreward"
P = "abaybektursun-"

# hard328 cells whose rows are only in runs/ (one job, sample 0, seed 3,000,000); readout = edits/readout.json
MATH = {"base_cue_rerun": "1114-151534-e72c", "top8x1.5_rerun": "1115-031229-5991", "top1x1": "1115-000358-d11a",
        "top1x2": "1115-105247-1603", "top1x3": "1115-105259-789c", "top8x0.5": "1115-031219-19af", "top8x1": "1114-221034-007d",
        "top8x2": "1115-012855-d7ed", "top8x3": "1115-031240-1106", "rand8x1": "1114-221040-5f1e", "rand8x2": "1115-031304-cf34",
        "rand8x3": "1115-031315-b328"}
EDITS_KEY = {"base_cue_rerun": "base_cue_T1", "top8x1.5_rerun": "top8x1.5_math31", "top1x1": "top1_math31", "top1x2": "top1x2_math31",
             "top1x3": "top1x3_math31", "top8x0.5": "top8x0.5_math31", "top8x1": "top8_math31", "top8x2": "top8x2_math31",
             "top8x3": "top8x3_math31", "rand8x1": "rand8_math31", "rand8x2": "rand8x2_math31", "rand8x3": "rand8x3_math31"}
# Code pair cells, one job each, seed 51,000,000; readouts code_depth/ and code_dial/
CODE = {"base_cue": "1114-170304-c03c", "rl_plain": "1114-170253-f661", "rand8x1.5": "1115-101457-ef2c", "top8x1": "1115-101423-4a7d",
        "top8x1.5": "1115-101434-4511", "top8x2": "1115-101445-e35e", "math_top8x1.5": "1115-101508-33f0",
        "L0-10": "1115-120127-70c3", "L11-21": "1115-120138-c4be", "L22-31": "1115-120151-bee2"}
CODE_KEY = {"base_cue": "base_cue", "rl_plain": "rl_plain", "rand8x1.5": "code_rand8x1.5_code31", "top8x1": "code_top8_code31",
            "top8x1.5": "code_top8x1.5_code31", "top8x2": "code_top8x2_code31", "math_top8x1.5": "code_top8x1.5_math31",
            "L0-10": "code_top8x1.5_L0-10_code31", "L11-21": "code_top8x1.5_L11-21_code31", "L22-31": "code_top8x1.5_L22-31_code31"}
# raw texts of the main hard328 cells, for examples: cell -> {sample: [jobs]} (rows in git: see build_facts.py)
TEXTS = {"base_cue": {s: ["1114-200457-e8e6"] for s in range(4)}, "top8x1.5": {s: ["1115-055641-b417"] for s in range(4)},
         "L0-10": {0: ["1115-105312-7e19"], 1: ["1115-122708-c6c1", "1115-122720-ad28"]},
         "L11-21": {1: ["1115-122912-8aec", "1115-122924-d28b"]}, "L22-31": {1: ["1115-122936-1b30", "1115-122949-e563"]},
         "d2-8": {1: ["1115-122847-824c", "1115-122859-b197"]}, "rand_L0-10": {1: ["1115-122822-c211", "1115-122835-f7eb"]},
         "rand8x1.5": {0: ["1115-090241-0229"]}}
EDIT_JOBS = {**{f"math {k}": v for k, v in MATH.items()}, **{f"code {k}": v for k, v in CODE.items()},
             "math L0-10": "1115-105312-7e19", "math L11-21": "1115-105324-5f61", "math L22-31": "1115-105335-a886",
             "math d2-8": "1115-122847-824c", "math rand_L0-10": "1115-122822-c211", "math rand8x1.5": "1115-090241-0229",
             "math top8x1.5 (4-sample cell)": "1115-055641-b417"}


IDX = sorted({json.loads(l)["problem_index"] for l in (STUDY / "results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl").read_text().splitlines()})
assert len(IDX) == 328


def run_dir(job):
    hits = sorted(glob.glob(str(ROOT.parent / "iterate-hack*" / "runs" / (P + job))))
    assert hits, f"runs/{P + job} not found: uv run tools/gpu.py get {P + job}"
    return pathlib.Path(hits[0])


def answers(job):
    return [json.loads(l) for l in (run_dir(job) / "answers.jsonl").read_text().splitlines()]


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))


def first(r):
    """attempt 0 (older jobs have no restarts and no attempt field); sample from the seed rule 3,000,000 + 10,000 s + i."""
    return r.get("attempt", 0) == 0


def sample_of(r):
    return (r["seed"] - 3000000 - r["problem_index"]) // 10000


def math_rows(jobs, sample):
    rows = sorted((r for j in jobs for r in answers(j) if first(r) and sample_of(r) == sample), key=lambda r: r["problem_index"])
    assert [r["problem_index"] for r in rows] == IDX, (jobs, sample, len(rows))
    assert all(r["seed"] == 3000000 + 10000 * sample + r["problem_index"] for r in rows), jobs
    return rows


def tail(t, n=700):
    return t[-n:]


def main():
    assert not (HERE / "data").exists(), "data/ exists: frozen inputs are never rewritten"
    ed = json.loads((RES / "edits" / "readout.json").read_text())["cells"]
    for cell, job in MATH.items():
        rows = math_rows([job], 0)
        want = ed[EDITS_KEY[cell]]
        assert want["job_id"] == P + job, cell
        assert (sum(r["score_v3"] for r in rows), sum(bool(r["cap_hit"]) for r in rows)) == (want["right_v3"], want["cap_hits"]), cell
        assert abs(sum(r["n_new"] for r in rows) / 328 - want["mean_generated_tokens"]) < 0.06, cell
        write(HERE / "data" / "math" / f"{cell}.jsonl",
              [{k: r[k] for k in ("problem_index", "seed", "score_v3", "cap_hit", "n_new", "extracted_v3", "gold")} for r in rows])

    ro = {**json.loads((RES / "code_dial" / "readout.json").read_text())["cells"], **json.loads((RES / "code_depth" / "readout.json").read_text())["cells"]}
    seeds = None
    code_text = {}
    for cell, job in CODE.items():
        rs = sorted(answers(job), key=lambda r: r["uid"])
        want = ro[CODE_KEY[cell]]
        assert want["job_id"] == P + job, cell
        a = want["all"]
        assert (len(rs), sum(r["passed"] for r in rs), sum(bool(r["cap_hit"]) for r in rs), sum(r["mode"] == "none" for r in rs)) == \
            (a["n"], a["passed"], a["cap_hits"], a["no_block"]), cell
        s = [(r["uid"], r["seed"]) for r in rs]
        assert seeds is None or s == seeds, f"{cell}: seeds differ from base_cue, not paired"
        seeds = s
        write(HERE / "data" / "code" / f"{cell}.jsonl",
              [{k: r[k] for k in ("uid", "bench", "seed", "passed", "cap_hit", "mode", "exit", "n_new")} for r in rs])
        code_text[cell] = {r["uid"]: r for r in rs}

    totals = {}
    for name, job in EDIT_JOBS.items():
        f = run_dir(job) / "edit.json"
        if f.exists():
            e = json.loads(f.read_text())
            a = e["args"]
            totals[name] = {"job": P + job, "recipe": a["recipe"], "other": a["other"], "scale": a.get("scale", 1.0), "k": e.get("k"), "layers": e.get("layers"),
                            "skip": a.get("skip"), "n_edited": e["n_edited"], **e["totals"]}
    (HERE / "data" / "edit_totals.json").write_text(json.dumps(totals, indent=1) + "\n")

    # ---- examples: first problem index right and first wrong (finished wrong if any), per main cell, sample 1 where it exists
    ex = {"rule": "per cell: the lowest problem index scored right and the lowest scored wrong among finished answers, of the sample "
                  "named; text = last 700 characters of the generated answer; hard328 score = score_v3, Code score = passed",
          "hard328": {}, "code": {}}
    T = {cell: {s: {r["problem_index"]: r for j in jobs for r in answers(j) if first(r) and sample_of(r) == s}
                for s, jobs in ss.items()} for cell, ss in TEXTS.items()}
    for cell, ss in T.items():
        s = 1 if 1 in ss else 0
        rows = [ss[s][p] for p in sorted(ss[s])]
        pick = {"right": next(r for r in rows if r["score_v3"] == 1), "wrong": next(r for r in rows if r["score_v3"] == 0 and not r["cap_hit"])}
        ex["hard328"][cell] = {k: {"problem_index": r["problem_index"], "unique_id": r.get("unique_id"), "sample": s, "seed": r["seed"],
                                   "gold": r["gold"], "extracted_v3": r["extracted_v3"], "score_v3": r["score_v3"], "cap_hit": bool(r["cap_hit"]),
                                   "n_new": r["n_new"], "answer_tail": tail(r["text"])} for k, r in pick.items()}
    for cell in ("base_cue", "top8x1.5", "L0-10", "L11-21", "L22-31", "rand8x1.5"):
        rows = [code_text[cell][u] for u in sorted(code_text[cell])]
        pick = {"right": next(r for r in rows if r["passed"]), "wrong": next(r for r in rows if not r["passed"] and not r["cap_hit"])}
        ex["code"][cell] = {k: {"uid": r["uid"], "seed": r["seed"], "passed": r["passed"], "exit": r["exit"], "mode": r["mode"],
                                "cap_hit": bool(r["cap_hit"]), "n_new": r["n_new"], "answer_tail": tail(r["text"])} for k, r in pick.items()}
    d, b = T["d2-8"][1], T["base_cue"][1]
    both = [p for p in sorted(d) if d[p]["score_v3"] == 1 and not d[p]["cap_hit"] and b[p]["cap_hit"]]
    p = both[0]
    ex["d2-8_right_base_cut_off"] = {
        "what": "problems where directions 2-8 (sample 1) finish right and the cued base with the same seed (sample 1, seed 3,010,000 + i) "
                "hits the 16,384-token cap",
        "n_problems": len(both), "problem_indices": both,
        "example": {"problem_index": p, "unique_id": d[p].get("unique_id"), "seed": d[p]["seed"], "gold": d[p]["gold"],
                    "d2-8": {"extracted_v3": d[p]["extracted_v3"], "score_v3": d[p]["score_v3"], "n_new": d[p]["n_new"], "answer_tail": tail(d[p]["text"])},
                    "base_cue": {"extracted_v3": b[p]["extracted_v3"], "score_v3": b[p]["score_v3"], "cap_hit": True, "n_new": b[p]["n_new"],
                                 "answer_tail": tail(b[p]["text"], 400)}}}
    (HERE / "examples.json").write_text(json.dumps(ex, indent=1, ensure_ascii=False) + "\n")
    print(f"froze {len(MATH)} hard328 cells, {len(CODE)} Code cells, {len(totals)} edit totals; d2-8 right / base cut off: {len(both)}")


if __name__ == "__main__":
    main()
