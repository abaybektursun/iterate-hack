"""retest15: three round-15 consequences of account-2 under engine 16's adversary rule (specs/SPEC_direct_retest15.md).

    uv run --no-project --with numpy --with boto3 --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 \
        python -m studies.theory.analysis.direct_retest15

Run from the worktree root. For each test the adversary's value is computed first, then the statistic, then the verdict
with forecast.verdict16. Raw texts (d1 freshness, examples) are read from RAW and SHOTS (not in git).
Writes studies/theory/results/direct/retest15-01/.
"""
import ast
import hashlib
import json
import pathlib
import subprocess

import numpy as np

from studies.rlneurons.analysis import selector as SEL
from studies.rlneurons.analysis.votek import agree_table
from studies.theory.analysis import direct_merge328 as M
from studies.theory.analysis import direct_s100vote as S1
from studies.theory.lib.forecast import verdict16

ROOT = pathlib.Path(__file__).resolve().parents[3]
TH = ROOT / "studies/theory"
RES = ROOT / "studies/rlneurons/results"
OUT = TH / "results/direct/retest15-01"
RAW = pathlib.Path("/Users/abaybektursun/projects/iterate-hack/runs")
SHOTS = pathlib.Path("/Users/abaybektursun/projects/iterate-hack-shots/runs/cap32_base_cue_joined/answers.jsonl")
B = 10000
CMD = ("uv run --no-project --with numpy --with boto3 --with math-verify==0.9.0 --with antlr4-python3-runtime==4.11 "
       "python -m studies.theory.analysis.direct_retest15")


def jl(p):
    return [json.loads(x) for x in open(p)]


def ci(m):
    return [round(float(x), 4) for x in np.percentile(m, [5, 95])]


def row(mech, claim, interval, rng, adv, n, measured):
    r = {"mechanism": mech, "claim": claim, "result": "PENDING", "measured": measured,
         "interval": interval, "range": list(rng), "adversary": round(float(adv), 4), "n": n}
    r["verdict"] = verdict16(r)
    return r


# ---------------- 1. s100vote ----------------
def per_problem(by):
    idx = sorted(by)
    assert idx == list(range(500))
    single = np.array([np.mean([r["score_v3"] for r in by[i]]) for i in idx])
    vote = np.array([SEL.tie_random(by[i]) for i in idx])
    k = np.array([sum(r["score_v3"] for r in by[i]) for i in idx])
    return k, 100 * (vote - single)


def s100vote():
    rl = S1.first_attempts("day1_3/math500_rl-01")
    s100 = S1.step100()
    # Adversary first: final RL's mean gain at each right count k, applied to step 100's k distribution.
    k_rl, g_rl = per_problem(rl)
    k_100 = np.array([sum(r["score_v3"] for r in s100[i]) for i in range(500)])
    gk = np.array([g_rl[k_rl == k].mean() for k in range(5)])
    adv = float(gk[k_100].mean())
    assert abs(float(gk[k_rl].mean()) - g_rl.mean()) < 1e-9  # the per-k means reproduce final RL's own G
    # Statistic.
    k2, g = per_problem(s100)
    assert (k2 == k_100).all()
    G = float(g.mean())
    idx = np.random.default_rng(0).integers(0, 500, (B, 500))
    interval = ci(g[idx].mean(1))
    # Not deciding: step 100's G minus the adversary, problems resampled jointly in both cells.
    idx1 = np.random.default_rng(1).integers(0, 500, (B, 500))
    ex = []
    for i in idx1:
        kr, gr = k_rl[i], g_rl[i]
        m = np.array([gr[kr == k].mean() if (kr == k).any() else 0.0 for k in range(5)])
        ex.append(g[i].mean() - m[k_100[i]].mean())
    met = {"statistic": "G = 100 mean over problems (vote over 4, random tie-break, minus mean single sample), points",
           "adversary": {"text": "final RL's mean vote gain at each per-problem right count k (0-4), weighted by step 100's distribution of k",
                         "value": round(adv, 4), "final_rl_gain_per_k": [round(float(x), 4) for x in gk],
                         "step100_k_hist": np.bincount(k_100, minlength=5).tolist(),
                         "final_rl_k_hist": np.bincount(k_rl, minlength=5).tolist(),
                         "final_rl_G": round(float(g_rl.mean()), 4), "audit_value_own_vote": 6.237},
           "G": round(G, 4), "ci90": interval, "n": 500,
           "G_minus_adversary": {"value": round(G - adv, 4), "ci90": ci(np.array(ex)), "bootstrap": "10,000 joint resamples, default_rng(1)"},
           "bootstrap": "10,000 resamples of problems, default_rng(0)"}
    win = next(p for p in range(500) if g[p] > 0)
    lose = next(p for p in range(500) if g[p] < 0)
    exs = {f"{name}": {"problem_index": p, "gold": s100[p][0]["gold"], "vote_minus_single_points": float(g[p]),
                       "samples": [{k: r[k] for k in ("sample", "extracted_v3", "score_v3", "cap_hit")} for r in s100[p]]}
           for name, p in (("vote_beats_single", win), ("vote_loses_to_single", lose))}
    raw = [[(r["extracted_v3"], r["score_v3"], r["cap_hit"], r["gold"]) for r in s100[p]] for p in (0, 18, 5)]
    r = row("round-15/account-2/c2@16",
            "RL step 100 plain on MATH-500 gains as much from a vote over its 4 samples (vote right minus mean single-sample right) as the cued base does, 5 to 10 points, not as little as final RL.",
            interval, (5.0, 10.0), adv, 500,
            f"G = {G:+.2f} points [{interval[0]:.2f}, {interval[1]:.2f}] (90 % bootstrap over problems), n 500; adversary "
            f"(final RL's vote gain per right count k, weighted by step 100's k distribution) {adv:+.2f}, inside the interval; "
            f"G minus adversary {G - adv:+.2f} [{met['G_minus_adversary']['ci90'][0]:.2f}, {met['G_minus_adversary']['ci90'][1]:.2f}]")
    return met, exs, raw, r


# ---------------- 2. merge328 ----------------
def vote_fast(keys):
    """Random tie-break plurality vote: 1 / (number of tied top keys) if 'R' is among them."""
    c = {}
    for x in keys:
        if x is not None:
            c[x] = c.get(x, 0) + 1
    if not c:
        return 0.0
    top = [x for x, n in c.items() if n == max(c.values())]
    return 1 / len(top) if "R" in top else 0.0


def merge328():
    rows = {}
    for r in jl(M.SRC):
        if r["attempt"] == 0:
            rows.setdefault(r["problem_index"], {})[r["sample"]] = r
    probs = sorted(rows)
    assert len(probs) == 328 and all(sorted(rows[p]) == [0, 1, 2, 3] for p in probs)
    rows = {p: [rows[p][s] for s in range(4)] for p in probs}
    same = {p: agree_table(rows[p]) for p in probs}

    def wrong_pairs(ps):
        a = t = 0
        for p in ps:
            w = [s for s in range(4) if rows[p][s]["extracted_v3"] is not None and rows[p][s]["score_v3"] == 0 and not rows[p][s]["cap_hit"]]
            for i in range(len(w)):
                for j in range(i + 1, len(w)):
                    t += 1
                    a += same[p][w[i]][w[j]]
        return a, t

    # Adversary first: measured pair agreement over all 328 problems, shared-attractor model on the kept problems.
    a_n, t_n = wrong_pairs(probs)
    agree = a_n / t_n
    q = agree ** 0.5
    K = {p: M.keys(rows[p], same[p], True) for p in probs}
    band = [p for p in probs if "R" in K[p] and any(x not in (None, "R") for x in K[p])]
    shape = {p: (K[p].count("R"), sum(x not in (None, "R") for x in K[p])) for p in band}
    vm = {p: vote_fast(["R"] * shape[p][0] + ["W"] * shape[p][1]) for p in band}
    rng = np.random.default_rng(16)
    sims, sim_agree = [], []
    for _ in range(2000):
        ds, ag, tt = [], 0, 0
        for p in band:
            nr, nw = shape[p]
            sh = rng.random(nw) < q
            w = ["A" if s else ("u", i) for i, s in enumerate(sh)]
            ds.append(vote_fast(["R"] * nr + w) - vm[p])
            ag += sum(sh[i] and sh[j] for i in range(nw) for j in range(i + 1, nw))
            tt += nw * (nw - 1) // 2
        sims.append(np.mean(ds))
        sim_agree.append(ag / tt)
    adv = float(np.mean(sims))
    assert abs(np.mean(sim_agree) - agree) < 0.01, (np.mean(sim_agree), agree)
    indep = float(np.mean([vote_fast(["R"] * shape[p][0] + [("u", i) for i in range(shape[p][1])]) - vm[p] for p in band]))

    # Statistic, with the test's own vote (24-order mean) and a check that the fast vote equals it.
    res = {p: (M.v(K[p]), M.v(M.merged(K[p]))) for p in band}
    for p in band:
        assert abs(vote_fast(K[p]) - res[p][0]) < 1e-12 and abs(vote_fast(M.merged(K[p])) - res[p][1]) < 1e-12, p
        assert abs(vm[p] - res[p][1]) < 1e-12, p
    d = np.array([res[p][0] - res[p][1] for p in band])
    n = len(band)
    D = float(d.mean())
    interval = ci(d[np.random.default_rng(0).integers(0, n, (B, n))].mean(1))
    a_k, t_k = wrong_pairs(band)
    met = {"statistic": "D = mean over kept hard328 problems of V_S - V_M (cued base vote of 4, random tie-break; real vs merged wrong answers; cap hits abstain)",
           "adversary": {"text": "wrong answers are shared attractor values: each finished wrong answer equals one shared value per problem with probability q, else its own value; q^2 = measured same-problem wrong-pair agreement; right counts and wrong counts per problem kept; mean D over 2,000 simulations",
                         "measured_wrong_pair_agreement_hard328": [round(agree, 4), t_n], "q": round(q, 4),
                         "simulated_pair_agreement_on_kept": round(float(np.mean(sim_agree)), 4),
                         "value": round(adv, 4), "sim_sd": round(float(np.std(sims)), 4),
                         "simulations": 2000, "rng": "default_rng(16)"},
           "reference_independent_wrong_answers_D": round(indep, 4),
           "measured_wrong_pair_agreement_on_kept_problems": [round(a_k / t_k, 4), t_k],
           "shape_hist_right_wrong": {f"{a}R{b}W": sum(shape[p] == (a, b) for p in band) for a in range(1, 4) for b in range(1, 4) if any(shape[p] == (a, b) for p in band)},
           "D": round(D, 4), "ci90": interval, "n": n, "bootstrap": "10,000 resamples of kept problems, default_rng(0)"}
    yes = next(p for p in band if d[band.index(p)] > 0)
    no = next(p for p in band if d[band.index(p)] == 0)
    exs = {name: {"problem_index": p, "gold": rows[p][0]["gold"], "V_S": res[p][0], "V_M": res[p][1], "keys": K[p],
                  "answers": [{k: r[k] for k in ("sample", "extracted_v3", "score_v3", "cap_hit", "n_new")} for r in rows[p]]}
           for name, p in (("merging_changes_vote", yes), ("merging_no_change", no))}
    raw = [[(r["extracted_v3"], r["score_v3"], r["cap_hit"], r["gold"]) for r in rows[p]] for p in band[:4]]
    r = row("round-15/account-2/c1@16",
            "Cued-base wrong answers on hard328 are independent one-off slips that scatter, so a vote of 4 with the real wrong answers is right more often than with every finished wrong answer merged into one (D 0.06 to 0.40).",
            interval, (0.06, 0.40), adv, n,
            f"D = {D:.3f} [{interval[0]:.3f}, {interval[1]:.3f}] (90 % bootstrap over problems), n {n}; adversary (wrong answers "
            f"are shared attractor values at the measured pair agreement {agree:.3f} of {t_n} pairs, q {q:.3f}, 2,000 simulations) "
            f"{adv:.3f}; fully independent wrong answers would give {indep:.3f}")
    return met, exs, raw, r


# ---------------- 3. edit0of4 and d1 ----------------
def constants(path, names):
    tree = ast.parse(path.read_text())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
            out[node.targets[0].id] = ast.unparse(node.value)
    return out


def a0(cell):
    """{problem: [score of samples 0-3]} from attempt-0 rows."""
    g = {}
    for r in jl(RES / cell / "rows.jsonl"):
        if r["attempt"] == 0:
            g.setdefault(r["problem_index"], {})[r["sample"]] = r["score_v3"]
    assert all(sorted(v) == [0, 1, 2, 3] for v in g.values()) and len(g) == 328, cell
    return {p: [v[s] for s in range(4)] for p, v in g.items()}


def d1():
    c_e = constants(TH / "analysis/direct_edit0of4.py", {"D13", "CELLS", "CAP32_ROWS", "CUT", "JOBS"})
    c_r = constants(TH / "analysis/direct_editreach.py", {"CELLS", "CAP32_ROWS", "CAP32_RAW", "CUT"})
    cells = {"base": "day1_3/hard328_base_cue_s4r2-01", "edit": "day1_3/hard328_top8x1.5_cue_s4-01", "rl": "day1_3/hard328_rl_plain_s4r2-01"}
    for k, v in cells.items():  # both scripts name the same three rows files
        assert v.split("/")[1] in c_e["CELLS"] and v in c_r["CELLS"], k
    assert "cap32/rows-02/base_cue.jsonl" in c_e["CAP32_ROWS"] and "cap32/rows-02/base_cue.jsonl" in c_r["CAP32_ROWS"]
    assert c_e["CUT"] == c_r["CUT"] == "16384"

    s = {k: a0(v) for k, v in cells.items()}
    cap = {r["problem_index"]: r for r in jl(RES / "cap32/rows-02/base_cue.jsonl")}
    # Adversary first: S from accuracy alone, overall attempt-0 per-sample rates on all 328 problems.
    acc = {k: float(np.mean([x for v in s[k].values() for x in v])) for k in s}
    adv = (acc["edit"] - acc["base"]) / (acc["rl"] - acc["base"])

    # Selections: edit0of4 (base 0 of 4) and d1 (minus cap32 texts that repeat a base sample-0..3 text).
    base0 = sorted(p for p, v in s["base"].items() if sum(v) == 0)
    job = json.load(open(RES / cells["base"] / "run.json"))["job_id"]
    bsha = {}
    for r in jl(RAW / job / "answers.jsonl"):
        if r["attempt"] == 0:
            bsha.setdefault(r["problem_index"], set()).add(hashlib.sha256(r["text"].encode()).hexdigest())
    craw = {r["problem_index"]: r for r in jl(SHOTS)}
    sel = [p for p in base0 if hashlib.sha256(craw[p]["text"].encode()).hexdigest() not in bsha[p]]
    stored_e = json.load(open(TH / "results/direct/edit0of4-01/metrics.json"))["problems"]
    stored_d = json.load(open(TH / "results/direct/editreach-02/metrics.json"))["selected_problems"]
    assert base0 == stored_e and sel == stored_d and set(sel) <= set(base0), "selections differ from the stored ones"

    # Statistic.
    e = np.array([np.mean(s["edit"][p]) for p in sel])
    r_ = np.array([np.mean(s["rl"][p]) for p in sel])
    b = np.array([int(cap[p]["score_v3"] == 1 and cap[p]["n_new"] <= 16384 and not cap[p]["cap_hit"]) for p in sel], float)
    n = len(sel)
    S = float((e.mean() - b.mean()) / (r_.mean() - b.mean()))
    idx = np.random.default_rng(0).integers(0, n, (B, n))
    Sb = (e[idx].mean(1) - b[idx].mean(1)) / (r_[idx].mean(1) - b[idx].mean(1))
    interval = ci(Sb)
    met = {"same_measurement_check": {
               "edit0of4_inputs": c_e, "editreach_inputs": c_r,
               "same_rows_files": True, "edit0of4_problems": len(base0), "d1_problems": len(sel),
               "d1_subset_of_edit0of4": True, "dropped_from_d1": sorted(set(base0) - set(sel)),
               "statistics": "edit0of4: E - R; d1: (E - B) / (R - B); both from the same E and R counts",
               "decision": "edit0of4 (round-15/account-2/c3) rejected, same measurement as d1: no row"},
           "d1": {"statistic": "S = (E - B) / (R - B) on hard328 problems the cued base gets 0 of 4 (fresh cap32 base sample)",
                  "adversary": {"text": "S expected from accuracy alone: (acc_edit - acc_base) / (acc_rl - acc_base) with attempt-0 samples 0-3 per-sample right rates on all 328 hard328 problems",
                                "acc": {k: round(v, 4) for k, v in acc.items()}, "value": round(adv, 4)},
                  "S": round(S, 4), "ci90": interval, "n": n, "E": round(float(e.mean()), 4), "R": round(float(r_.mean()), 4),
                  "B": round(float(b.mean()), 4), "R_minus_B_ci90": ci(r_[idx].mean(1) - b[idx].mean(1)),
                  "bootstrap": "10,000 resamples of problems, default_rng(0), one draw for E, R, B"}}
    eraw = {(x["problem_index"], x["sample"]): x for x in jl(RAW / json.load(open(RES / cells["edit"] / "run.json"))["job_id"] / "answers.jsonl")}
    exs = {}
    for label, want in (("edit_right", 1), ("edit_wrong", 0)):
        p, k = next((p, k) for p in sel for k in range(4) if s["edit"][p][k] == want)
        x = eraw[(p, k)]
        exs[label] = {"problem_index": p, "sample": k, "prompt": x["prompt"], "output_tail": x["text"][-800:],
                      "extracted_v3": x["extracted_v3"], "gold": x["gold"], "score_v3": x["score_v3"], "cap_hit": x["cap_hit"]}
    raw = [{"problem": p, "edit": s["edit"][p], "rl": s["rl"][p], "base": s["base"][p],
            "cap32": {k: cap[p][k] for k in ("score_v3", "n_new", "cap_hit", "extracted_v3", "gold")}} for p in sel[:3]]
    r = row("round-15/account-2/d1@16",
            "The 1.5x top-8 edit lowers the per-step slip rate the way RL does, so on hard328 problems outside the cued base's 4-sample reach it captures most or all (0.60-1.40) of RL plain's per-sample advantage over a fresh base sample.",
            interval, (0.60, 1.40), adv, n,
            f"S = (E - B) / (R - B) = {S:.3f} [{interval[0]:.3f}, {interval[1]:.3f}] (90 % bootstrap over problems), n {n}; "
            f"adversary (S from overall hard328 accuracy alone: edit {acc['edit']:.3f}, RL {acc['rl']:.3f}, cued base {acc['base']:.3f}) "
            f"{adv:.3f}. edit0of4 (c3) is the same measurement on the same rows: no separate row")
    return met, exs, raw, r


def main():
    assert not OUT.exists(), f"{OUT} exists: a rerun gets the next number"
    m2, e2, raw2, r2 = s100vote()
    m1, e1, raw1, r1 = merge328()
    m3, e3, raw3, r3 = d1()
    print("RAW step 100 (answer, score, cap_hit, gold):", json.dumps(raw2))
    print("RAW merge328 kept:", json.dumps(raw1))
    print("RAW d1:", json.dumps(raw3))
    rows = [r1, r2, r3]
    metrics = {"spec": "studies/theory/specs/SPEC_direct_retest15.md", "rule": "verdict16 (studies/theory/lib/forecast.py)",
               "s100vote_c2": {**m2, "verdict": r2["verdict"]}, "merge328_c1": {**m1, "verdict": r1["verdict"]},
               "edit0of4_c3_and_d1": {**m3, "d1_verdict": r3["verdict"]},
               "raw_rows": {"s100vote": raw2, "merge328": raw1, "d1": raw3}}
    OUT.mkdir(parents=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
    (OUT / "examples.json").write_text(json.dumps({"s100vote": e2, "merge328": e1, "d1": e3}, indent=1, ensure_ascii=False) + "\n")
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({"spec": metrics["spec"], "commit": commit, "command": CMD, "board": "work-b6d38d",
                                              "raw_inputs": [str(RAW), str(SHOTS)]}, indent=1) + "\n")
    for r in rows:
        print(r["mechanism"], r["verdict"], "|", r["measured"])


if __name__ == "__main__":
    main()
