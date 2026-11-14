"""Planted cases for analysis/day1_length_rules.py (specs/SPEC_day1_length_rules.md): rows where each rule must change the
answer, rows where it must not, rows built to make a rule answer wrong, token counts computed by hand, and runs that must be
refused. No model, no network.

    uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules_test
"""
import contextlib
import io
import json
import pathlib
import tempfile

from studies.rlneurons.analysis import day1_length_rules as L
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

GOLD = "\\frac{1}{2}"
CAP = 16384


def smp(n_new, ans, cap=False):
    """One attempt-0 row. ans: the extracted answer (None = none); the score is grader v3's on a text that ends with it in a box."""
    return {"n_new": n_new, "cap_hit": cap, "extracted_v3": ans, "attempt": 0, "seed": 0, "gold": GOLD, "prompt": "p", "text": "t",
            "score_v3": 0 if ans is None else R.grade_v3(GOLD, f"\\boxed{{{ans}}}")["score_v3"]}


def prob(i, *samples):
    return [{**r, "problem_index": i, "sample": k} for k, r in enumerate(samples)]


def got(samples, s, l):
    o = L.apply(prob(0, *samples), s, l)
    return (o["score"], o["tokens"], o["answer"], o["stopped"], o["used"])


def raises(f):
    try:
        f()
    except AssertionError:
        return True
    return False


def write_run(d, model, set_name, problems, status="done", samples=4):
    d.mkdir()
    rows = [r for p in problems for r in p]
    (d / "answers.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    cfg = {"model": model, "prompt": "cue" if model == "base" else "plain", "set": set_name, "temperature": 1.0, "top_p": 1.0,
           "max_tokens": CAP, "seed": 1, "samples": samples, "restarts": 0, "n_problems": len(problems)}
    (d / "metrics.json").write_text(json.dumps({"status": status, "config": cfg, "commit": "c" * 40, "job_id": f"job-{model}"}))
    return d


def run(*argv):
    with contextlib.redirect_stdout(io.StringIO()):
        L.main(list(argv))


def main():
    assert [L.name(s, l) for s, l in L.GRID[:2] + L.GRID[4:6]] == ["single", "R8000", "D1000", "D1000+R8000"] and len(L.GRID) == 16
    x = smp(100, "7")                                                        # filler: a sample no rule may read in that case

    # ---- D(2000), cutoff off
    assert got([smp(800, "0.5"), smp(900, GOLD), smp(5000, "7"), x], 2000, None) == (1, 1700, 0, [], [0, 1])       # equal forms agree: no third sample
    assert got([smp(800, "7"), smp(900, "0.5"), smp(5000, GOLD), x], 2000, None) == (1, 6700, 1, [], [0, 1, 2])    # fixed: 2 of 3 right
    assert got([smp(800, "0.5"), smp(900, "7"), smp(700, "7"), smp(100, "0.5")], 2000, None) == (0, 2400, 1, [], [0, 1, 2])   # must fail: breaks a right answer
    assert got([smp(800, "7"), smp(900, "0.5"), smp(700, "9"), x], 2000, None) == (0, 2400, 0, [], [0, 1, 2])      # three different: sample 0
    assert got([smp(800, "7"), smp(900, "7"), smp(700, "0.5"), x], 2000, None) == (0, 1700, 0, [], [0, 1])         # must fail: a repeated wrong answer stays
    assert got([smp(2000, "7"), smp(900, "0.5"), smp(700, "0.5"), x], 2000, None) == (1, 3600, 1, [], [0, 1, 2])   # n_new = S is checked
    assert got([smp(2001, "7"), smp(900, "0.5"), smp(700, "0.5"), x], 2000, None) == (0, 2001, 0, [], [0])         # n_new = S + 1 is not
    assert got([smp(2001, "7"), smp(900, "0.5"), smp(700, "0.5"), x], 4000, None) == (1, 3601, 1, [], [0, 1, 2])   # the same rows at S 4000
    assert got([smp(1500, "7", cap=True), smp(900, "0.5"), smp(700, "0.5"), x], 2000, None) == (0, 1500, 0, [], [0])   # a cap hit is never checked
    assert got([smp(CAP, None, cap=True), smp(900, "0.5"), smp(700, "0.5"), x], 2000, None) == (0, CAP, 0, [], [0])
    assert got([smp(800, None), smp(900, "0.5"), smp(700, "7"), x], 2000, None) == (1, 2400, 1, [], [0, 1, 2])     # sample 0 without an answer casts no vote
    assert got([smp(800, None), smp(900, "7"), smp(700, "0.5"), x], 2000, None) == (0, 2400, 1, [], [0, 1, 2])     # ... and the lower sample of the tie wins
    assert got([smp(800, "0.5"), smp(900, None), smp(700, "0.5"), x], 2000, None) == (1, 2400, 0, [], [0, 1, 2])   # sample 1 without an answer: a third sample
    assert got([smp(800, "0.5"), smp(900, None), smp(700, "7"), x], 2000, None) == (1, 2400, 0, [], [0, 1, 2])     # 1-1 tie: sample 0
    assert got([smp(800, None), smp(900, None), smp(700, None), smp(600, None)], 2000, None) == (0, 2400, 0, [], [0, 1, 2])   # no answer anywhere: wrong
    assert got([smp(1000, "0.5"), smp(15000, "7"), smp(12000, "0.5"), x], 2000, None) == (1, 28000, 0, [], [0, 1, 2])   # check samples cost their full length
    assert got([smp(800, "7"), smp(900, "0.5"), smp(700, "0.5"), x], None, None) == (0, 800, 0, [], [0])           # both off: the single row

    # ---- R(8000), check off
    assert got([smp(8000, "7"), smp(500, "0.5"), x, x], None, 8000) == (0, 8000, 0, [], [0])                       # n_new = L is not stopped
    assert got([smp(8001, "7"), smp(500, "0.5"), x, x], None, 8000) == (1, 8500, 1, [0], [1])                      # fixed: L + 500 tokens
    assert got([smp(8001, "7"), smp(500, "0.5"), x, x], None, 10000) == (0, 8001, 0, [], [0])                      # the same rows at L 10000
    assert got([smp(9000, "0.5"), smp(3000, "7"), x, x], None, 8000) == (0, 11000, 1, [0], [1])                    # must fail: stops a right answer
    assert got([smp(9000, "0.5"), smp(CAP, None, True), smp(12000, "0.5"), smp(CAP, None, True)], None, 8000) == (0, 3 * 8000 + CAP, 3, [0, 1, 2], [3])
    assert got([smp(9000, "0.5"), smp(CAP, None, True), smp(12000, "0.5"), smp(9500, "0.5")], None, 8000) == (1, 33500, 3, [0, 1, 2], [3])   # sample 3 runs in full
    assert got([smp(CAP, None, True)] * 4, None, 12000) == (0, 3 * 12000 + CAP, 3, [0, 1, 2], [3])                 # four cap hits without an answer
    assert got([smp(9000, "0.5"), smp(3000, "7")], None, 8000) == (0, 11000, 1, [0], [1])                          # two samples only: the second is the last

    # ---- D(2000) + R(8000): the cutoff first, then the check on the answering sample
    assert got([smp(9000, "0.5"), smp(1500, "7"), smp(1000, "0.5"), smp(1200, GOLD)], 2000, 8000) == (1, 11700, 2, [0], [1, 2, 3])
    assert got([smp(9000, "7"), smp(9000, "7"), smp(1500, "0.5"), smp(800, "7")], 2000, 8000) == (1, 18300, 2, [0, 1], [2, 3])    # samples run out: tie, sample 2
    assert got([smp(9000, "7"), smp(9000, "7"), smp(1500, None), smp(800, "7")], 2000, 8000) == (0, 18300, 3, [0, 1], [2, 3])     # ... sample 2 has no answer
    assert got([smp(9000, "7"), smp(9000, "7"), smp(9000, "7"), smp(1000, "0.5")], 2000, 8000) == (1, 25000, 3, [0, 1, 2], [3])   # no sample left for a check
    assert got([smp(9000, "0.5"), smp(5000, "7"), smp(100, "0.5"), smp(100, "0.5")], 2000, 8000) == (0, 13000, 1, [0], [1])       # answering sample longer than S
    assert got([smp(800, "7"), smp(900, "0.5"), smp(5000, GOLD), x], 2000, 8000) == (1, 6700, 1, [], [0, 1, 2])                   # nothing stopped: D alone
    assert got([smp(1000, "0.5"), smp(15000, "7"), smp(12000, "0.5"), x], 2000, 8000) == (1, 28000, 0, [], [0, 1, 2])             # check samples are not stopped
    assert got([smp(CAP, None, True)] * 4, 2000, 8000) == (0, 3 * 8000 + CAP, 3, [0, 1, 2], [3])

    # ---- only attempt 0 is read; an unfinished run is refused (day1_vote.chains)
    p = prob(0, smp(CAP, None, True), smp(900, "0.5"), smp(700, "0.5"), smp(100, "7"))
    re1 = {**p[0], "attempt": 1}
    re2 = {**p[0], "attempt": 2, "cap_hit": False, "n_new": 400, "extracted_v3": "0.5", "score_v3": 1}             # the restart is right
    cfg = {"samples": 4, "restarts": 2, "n_problems": 1}
    f = L.firsts(p + [re1, re2], cfg)
    assert [r["attempt"] for r in f[0]] == [0, 0, 0, 0] and L.apply(f[0], None, None)["score"] == 0                # the restart's answer is not used
    assert raises(lambda: L.firsts(p, cfg))                                  # must fail: a cap hit without its restart (job killed)
    assert raises(lambda: L.firsts(p[:3] + [re1, re2], cfg))                 # must fail: sample 3 is missing
    assert raises(lambda: L.firsts(p + [re1, re2], {**cfg, "n_problems": 2}))   # must fail: a problem is missing
    assert raises(lambda: L.firsts(p[:3] + [re1, re2], {**cfg, "samples": 3}))  # must fail: a complete run of 3 samples

    # ---- the readout on four planted problems per model; every number below is computed by hand
    base = [prob(0, smp(800, "7"), smp(900, "0.5"), smp(700, "0.5"), smp(100, "7")),       # D fixes it
            prob(1, smp(9000, "7"), smp(500, "0.5"), smp(600, "0.5"), smp(100, "7")),      # R(8000) fixes it
            prob(2, smp(800, "0.5"), smp(900, "7"), smp(700, "7"), smp(100, "0.5")),       # D breaks it
            prob(3, smp(3000, "0.5"), smp(100, "7"), smp(100, "7"), smp(100, "7"))]        # D(4000) breaks it
    rl = [prob(0, smp(4000, "0.5"), smp(100, "0.5"), smp(100, "0.5"), smp(100, "0.5")),
          prob(1, smp(3000, "0.5"), smp(200, "0.5"), smp(100, "0.5"), smp(100, "0.5")),
          prob(2, smp(800, "0.5"), smp(900, "0.5"), smp(100, "0.5"), smp(100, "0.5")),
          prob(3, smp(9000, "7"), smp(500, "7"), smp(100, "7"), smp(100, "7"))]
    res, per = L.summarize({q[0]["problem_index"]: q for q in base}, L.GRID)
    r = res["rows"]
    want = {"single": (2, 3400, 0, 0, 0, 0), "D1000": (2, 4200, 1, 1, 2, 0), "D2000": (2, 4200, 1, 1, 2, 0), "D4000": (1, 4250, 1, 2, 3, 0),
            "R8000": (3, 3275, 1, 0, 0, 1), "R10000": (2, 3400, 0, 0, 0, 0), "R12000": (2, 3400, 0, 0, 0, 0),
            "D2000+R8000": (3, 4225, 2, 1, 3, 1), "D4000+R8000": (2, 4275, 2, 2, 4, 1), "D2000+R12000": (2, 4200, 1, 1, 2, 0)}
    for k, w in want.items():
        g = tuple(r[k][c] for c in ("right", "tokens_per_problem", "fixed", "broke", "problems_with_a_check", "samples_stopped"))
        assert g == w, (k, g, w)
    assert r["R8000"]["n"] == 4 and r["R8000"]["percent"] == 75 and tuple(r["R8000"]["wilson95"]) == S.wilson(3, 4)
    assert r["R8000"]["minus_single"]["points"] == 25 and r["D2000"]["minus_single"]["points"] == 0
    lo, hi = r["D2000"]["minus_single"]["interval95"]
    assert lo < 0 < hi and r["single"]["minus_single"]["interval95"] == (0, 0)
    assert res["sample_0"] == {"cap_hits": 0, "finished_with_at_most": {"1000": {"n": 2, "wrong": 1}, "2000": {"n": 2, "wrong": 1},
                                                                        "4000": {"n": 3, "wrong": 1}},
                               "longer_than": {"8000": {"right": 0, "wrong": 1}, "10000": {"right": 0, "wrong": 0}, "12000": {"right": 0, "wrong": 0}}}
    assert L.cell(per["D2000+R8000"][1]) == "1 9100 0x1*2" and L.cell(per["D2000"][2]) == "0 2400 01*2" and L.cell(per["single"][3]) == "1 3000 0*"

    # ---- end to end: --choose on MATH-500 rows, --fixed on another set, and the refusals
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        mb, mr = write_run(t / "mb", "base", "math500", base), write_run(t / "mr", "rl", "math500", rl)
        hb, hr = write_run(t / "hb", "base", "hard328", base), write_run(t / "hr", "rl", "hard328", rl)
        run("--base", str(mb), "--rl", str(mr), "--out", str(t / "o1"), "--choose")
        m = json.loads((t / "o1" / "metrics.json").read_text())
        assert list(m["models"]["base"]["rows"]) == [L.name(s, l) for s, l in L.GRID] and m["mode"] == "choose" and m["n"] == 4
        assert m["models"]["rl"]["rows"]["single"]["tokens_per_problem"] == 4200 and m["models"]["rl"]["rows"]["R8000"]["tokens_per_problem"] == 4075
        assert m["models"]["rl"]["rows"]["D1000"]["tokens_per_problem"] == 4425 and m["models"]["rl"]["rows"]["D4000+R8000"]["tokens_per_problem"] == 4400   # (4100 + 3200 + 1700 + 8600) / 4
        d = m["rl_minus_base"]
        assert (d["single"]["points"], d["single"]["tokens_per_problem"]) == (25, 800) and (d["R8000"]["points"], d["R8000"]["tokens_per_problem"]) == (0, 800)
        e = m["equal_tokens"]
        assert e["budget_tokens_per_problem"] == 4200
        assert (e["base"]["setting"], e["base"]["right"], e["base"]["tokens_per_problem"], e["base"]["within_budget"]) == ("R8000", 3, 3275, True)
        assert e["base"]["minus_rl_single"]["points"] == 0 and e["base"]["minus_rl_single"]["interval95"][0] < 0
        assert (e["rl"]["setting"], e["rl"]["right"], e["rl"]["tokens_per_problem"]) == ("R8000", 3, 4075)        # ties with single: fewer tokens
        ch = json.loads((t / "o1" / "chosen.json").read_text())
        assert (ch["S"], ch["L"], ch["setting"], ch["chosen_on"]["set"]) == (None, 8000, "R8000", "math500")
        tsv = [x.split("\t") for x in (t / "o1" / "per_problem.tsv").read_text().splitlines()]
        col = tsv[0].index("D2000+R8000")
        assert len(tsv) == 9 and tsv[2][:3] == ["base", "1", "9000,500,600,100"] and tsv[2][col] == "1 9100 0x1*2" and tsv[8][col] == "0 8600 0x1*2"
        ex = json.loads((t / "o1" / "examples.json").read_text())
        assert sorted(ex["base"]) == ["D2000", "R8000"] and ex["base"]["D2000"]["fixed"]["problem_index"] == 0
        assert ex["base"]["D2000"]["broke"]["problem_index"] == 2 and ex["base"]["D2000"]["broke"]["answer_sample"] == 1
        assert [s["role"][:7] for s in ex["base"]["R8000"]["fixed"]["samples"]] == ["stopped", "answeri"] and ex["base"]["R8000"]["broke"] is None
        assert json.loads((t / "o1" / "run.json").read_text())["runs"]["rl"]["job_id"] == "job-rl"

        run("--base", str(hb), "--rl", str(hr), "--out", str(t / "o2"), "--fixed", str(t / "o1" / "chosen.json"))
        m = json.loads((t / "o2" / "metrics.json").read_text())
        assert list(m["models"]["base"]["rows"]) == ["single", "R8000"] and m["mode"] == "fixed" and "chosen" not in m
        assert m["equal_tokens"]["base"]["setting"] == "R8000" and m["equal_tokens"]["rl"]["setting"] == "R8000" and not (t / "o2" / "chosen.json").exists()
        (t / "c2.json").write_text(json.dumps({**ch, "S": 4000}))                                    # a fixed setting above the budget is reported, not replaced
        run("--base", str(hb), "--rl", str(hr), "--out", str(t / "o3"), "--fixed", str(t / "c2.json"))
        m = json.loads((t / "o3" / "metrics.json").read_text())
        assert list(m["models"]["base"]["rows"]) == ["single", "D4000", "R8000", "D4000+R8000"]
        assert (m["equal_tokens"]["base"]["setting"], m["equal_tokens"]["base"]["tokens_per_problem"], m["equal_tokens"]["base"]["within_budget"]) == ("D4000+R8000", 4275, False)
        run("--base", str(mb), "--out", str(t / "o4"))                                               # one model alone: no RL-minus-base block
        m = json.loads((t / "o4" / "metrics.json").read_text())
        assert list(m["models"]) == ["base"] and "equal_tokens" not in m and "rl_minus_base" not in m

        n = 0
        def refused(*argv):
            nonlocal n
            n += 1
            return raises(lambda: run(*argv, "--out", str(t / f"r{n}"))) and not (t / f"r{n}").exists()
        assert refused("--base", str(mb), "--rl", str(mr), "--fixed", str(t / "o1" / "chosen.json"))   # must fail: the choice was made on this set
        assert refused("--base", str(hb), "--rl", str(hr), "--choose")                                 # must fail: a choice on the 328
        assert refused("--base", str(mb), "--choose")                                                  # must fail: a choice without the RL run
        assert refused("--base", str(mb), "--rl", str(hr))                                             # must fail: two problem sets
        assert refused("--base", str(mr), "--rl", str(mb))                                             # must fail: the models swapped
        assert refused("--base", str(write_run(t / "u1", "base", "math500", base, status="running")))  # must fail: the job has not finished
        assert refused("--base", str(write_run(t / "u2", "base", "math500", [base[0], base[1], base[2], base[3][:3]])))   # must fail: a sample is missing
        assert refused("--base", str(write_run(t / "u3", "base", "math500", [q[:3] for q in base], samples=3)))           # must fail: three samples
        assert refused("--base", str(mb), "--rl", str(write_run(t / "u4", "rl", "math500", rl[:3])))   # must fail: other problems
        assert raises(lambda: run("--base", str(mb), "--out", str(t / "o1")))                          # must fail: the run folder exists
        # an RL run of 3,200 tokens per problem: no setting of the base is within the budget (its cheapest, R8000, costs 3,275)
        lo = write_run(t / "u5", "rl", "math500", rl[:3] + [prob(3, smp(5000, "7"), smp(500, "7"), smp(100, "7"), smp(100, "7"))])
        assert refused("--base", str(mb), "--rl", str(lo), "--choose")                                 # must fail: nothing to choose
        run("--base", str(mb), "--rl", str(lo), "--out", str(t / "o5"))
        e = json.loads((t / "o5" / "metrics.json").read_text())["equal_tokens"]
        assert e["budget_tokens_per_problem"] == 3200 and e["base"] is None and e["rl"]["setting"] == "single"
        assert L.best({"a": {"right": 3, "tokens_per_problem": 10}, "b": {"right": 5, "tokens_per_problem": 30}, "c": {"right": 3, "tokens_per_problem": 8}},
                      ["a", "b", "c"]) == "b"
    print("day1_length_rules_test: all planted cases pass")


if __name__ == "__main__":
    main()
