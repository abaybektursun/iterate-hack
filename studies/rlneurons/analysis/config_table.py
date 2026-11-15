"""Every full-set configuration on hard328 in one table, from committed per-problem rows (specs/SPEC_table.md, laptop).

    P="uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.config_table"
    $P --test                                                         # planted checks of the share and of the check itself
    $P --out studies/rlneurons/results/table/hard328-01 --v4-from runs    # reads the local raw answers once, writes v4_rows.jsonl
    $P --out studies/rlneurons/results/table/hard328-02 --v4-rows studies/rlneurons/results/table/hard328-01/v4_rows.jsonl

Writes run.json, table.md, table.json, checks.json (every posted number: expected, got), v4_rows.jsonl. Fails if the out
folder exists. Votes, rules and graders are imported (day1_vote, selector, frontier, mixvote, repair_v4), not copied."""
import argparse
import functools
import itertools
import json
import pathlib
import subprocess
import sys

import numpy as np

from studies.rlneurons.analysis import frontier as F
from studies.rlneurons.analysis import mixvote as M
from studies.rlneurons.grader import repair_v4 as G
from studies.rlneurons.lib import n13_score as S
from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
RES = STUDY / "results"
BOOT = 5000
RUNS = {"hard328": {"base": "day1_3/hard328_base_cue_s4r2-01", "rl": "day1_3/hard328_rl_plain_s4r2-01", "think": "thinkvote/hard328_sft1_cue_s4-01"},
        "math500": {"base": "day1_3/math500_base_cue-01", "rl": "day1_3/math500_rl-01", "think": "thinkvote/math500_sft1_cue_s4-01"}}
RAW = {"base": "abaybektursun-1114-200457-e8e6", "rl": "abaybektursun-1114-200505-5ff2", "think": "thinkvote_hard328_sft1_cue_s4"}   # under runs/, not committed
OTHER = ("bdba62b6dc1e86a807986287b03347cf9b8c1747", "studies/rlneurons/results/wsp1/hard328/{}-01/per_problem.json")   # sameraslan's branch
NAME = {"base": "base + cue", "rl": "RL plain", "think": "Think-SFT + cue"}
REWARD = {"base": "no", "rl": "yes", "think": "no"}
ORDERS = list(itertools.permutations(range(4)))
STORED = [None]
R.agree = functools.lru_cache(maxsize=None)(R.agree)          # same function, memoised: the votes compare the same pairs many times


def idx_matrix(n: int) -> np.ndarray:
    """The resamples of mixvote.paired and n13_score.paired_bootstrap(seed 0): one matrix for every column."""
    return np.random.default_rng(0).integers(0, n, (BOOT, n))


def interval(v) -> list:
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def share(x, b, r, idx) -> dict:
    """(acc(x) - acc(b)) / (acc(r) - acc(b)) in percent, with the percentile interval of the ratio over the resamples and the
    denominator's own interval. Unstable: the denominator's lower end is under half of its point value or not above 0."""
    x, b, r = (np.asarray(v, float) for v in (x, b, r))
    den = (r - b)[idx].mean(1) * 100
    lo = float(np.percentile(den, 2.5))
    point_den = float((r - b).mean() * 100)
    with np.errstate(divide="ignore", invalid="ignore"):              # a resample with a zero denominator gives inf: it stays in the interval
        ratio = 100 * (x - b)[idx].mean(1) * 100 / den
        iv = interval(ratio)
    return {"percent": float(100 * (x - b).mean() / (r - b).mean()), "interval95": iv,
            "denominator_points": point_den, "denominator_interval95": interval(den), "unstable": bool(lo <= 0 or lo < point_den / 2)}


def same(expected, got, digits: int = 0) -> tuple:
    """(got rounded to the posted digits, whether it equals the posted number)."""
    got = [round(float(g), digits) for g in got] if isinstance(got, (list, tuple, np.ndarray)) else round(float(got), digits)
    return got, got == (list(expected) if isinstance(expected, (list, tuple)) else expected)


def play(ch: dict, rule, orders=STORED) -> dict:
    """Per problem, the mean over `orders` of a frontier rule's score, abstention (no answer) and tokens."""
    out = {"s": [], "a": [], "t": []}
    for i in sorted(ch):
        os_ = [F.outcome(rule, ch[i], o) for o in orders]
        out["s"].append(np.mean([o["score"] for o in os_]))
        out["a"].append(np.mean([o["answer"] is None for o in os_]))
        out["t"].append(np.mean([o["tokens"] for o in os_]))
    return {k: np.array(v, float) for k, v in out.items()}


def cap_rule(L: float):
    """One sample stopped at L generated tokens: a longer answer gives no answer and costs L."""
    def rule(chains):
        a = chains[0][0]
        return {"answer": a["id"] if a["n_new"] <= L and a["extracted_v3"] is not None else None, "tokens": min(a["n_new"], L), "drawn": 1, "ran_out": False}
    return rule


def matched_cap(ch: dict, target: float) -> float:
    """L with mean min(n_new, L) over all attempt-0 samples = target tokens. Reads token counts only."""
    n = np.array([c[0]["n_new"] for i in ch for c in ch[i]], float)
    lo, hi = 0.0, float(n.max())
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if np.minimum(n, mid).mean() < target else (lo, mid)
    return round(hi)


def regrade(ch: dict, v4: dict) -> dict:
    """The chains with the v4 extraction and score in the fields the rules and the vote read."""
    return {i: [[{**a, "extracted_v3": v4[i, s, j][0], "score_v3": v4[i, s, j][1]} for j, a in enumerate(c)] for s, c in enumerate(cs)] for i, cs in ch.items()}


def samples(ch: dict, score=None) -> list:
    """mixvote's layout: samples[s][problem] = attempt-0 row. score: overwrite score_v3 (1 = count answered votes)."""
    return [[{**ch[i][s][0], **({} if score is None else {"score_v3": score})} for i in sorted(ch)] for s in range(4)]


def mixed(chs: dict, counts: dict) -> dict:
    m = M.mix({k: samples(chs[k]) for k in counts}, counts)
    answered = M.mix({k: samples(chs[k], 1) for k in counts}, counts)["per_problem_mean"]
    return {"s": np.array(m["per_problem_mean"]), "a": 1 - np.array(answered), "t": m["tokens_per_problem"], "range": [m["right_min"], m["right_max"]]}


def write_v4(runs: pathlib.Path, chs: dict, out: pathlib.Path):
    """v4a of every stored attempt of the three hard328 runs, from the local raw answers; asserts the raw v3 fields equal the committed rows."""
    lines = []
    for m, job in RAW.items():
        by = {(a["problem_index"], a["sample"], a["attempt"]): a for cs in chs[m].values() for c in cs for a in c}
        for line in open(runs / job / "answers.jsonl"):
            r = json.loads(line)
            key = (r["problem_index"], r["sample"], r["attempt"])
            assert (by[key]["extracted_v3"], by[key]["score_v3"], by[key]["n_new"]) == (r["extracted_v3"], r["score_v3"], r["n_new"]), f"{m} {key}: raw row differs from rows.jsonl"
            g = G.grade_v4(r["gold"], r["text"], r["finish_reason"], amended=True)
            lines.append({"model": m, "problem_index": key[0], "sample": key[1], "attempt": key[2], "extracted_v4": g["extracted_v4"], "score_v4": g["score_v4"], "fired_v4": g["fired_v4"]})
        assert sum(x["model"] == m for x in lines) == len(by), f"{m}: raw answers and rows.jsonl differ in size"
    lines.sort(key=lambda x: (x["model"], x["problem_index"], x["sample"], x["attempt"]))
    out.write_text("".join(json.dumps(x) + "\n" for x in lines))


def build(v4_rows) -> tuple:
    """(rows, context). A row: name, family, n_samples, reward, chosen, source, s / a (per-problem right and abstained
    fractions; a None when the rows carry no extraction), t (tokens per problem: array or posted mean), optional extras."""
    chs = {b: {m: F.load(RES / p)[1] for m, p in runs.items()} for b, runs in RUNS.items()}
    H, M5 = chs["hard328"], chs["math500"]
    idxs = sorted(H["base"])
    assert all(sorted(H[m]) == idxs for m in H)
    v4 = None
    if v4_rows:
        v4 = {m: {} for m in H}
        for line in open(v4_rows):
            x = json.loads(line)
            v4[x["model"]][x["problem_index"], x["sample"], x["attempt"]] = (x["extracted_v4"], x["score_v4"])
        H4 = {m: regrade(H[m], v4[m]) for m in H}
    rows = []

    def add(name, family, n, reward, chosen, source, d, **extra):
        rows.append({"name": name, "family": family, "n_samples": n, "reward": reward, "chosen_on_328": chosen, "source": source, **d, **extra})

    L = matched_cap(H["think"], play(H["rl"], F.RULES["single"], ORDERS)["t"].mean())
    SHORT = "no (tie rule written on MATH-500 after reading the problems it fixes: in-sample there, held out here)"
    rules = [("one sample (mean of 4)", "single", 1, "single", ORDERS, "no"),
             ("one sample, restart after a cap hit (mean of 4)", "single", 1, "restart", ORDERS, "no"),
             ("vote over 4", "vote", 4, "vote4", STORED, "no"),
             ("vote over 4 after restart", "vote", 4, "vote4_restart", STORED, "no"),
             ("vote over 4, ties to the shortest", "vote", 4, "vote4_short", STORED, SHORT),
             ("vote over 4 after restart, ties to the shortest", "vote", 4, "vote4_restart_short", STORED, SHORT),
             ("sequential vote, at most 3 (mean of 24 orders)", "vote", 3, "seq3", ORDERS, "no"),
             ("sequential vote, at most 4, restarts (mean of 24 orders)", "vote", 4, "seq4_restart", ORDERS, "no"),
             ("sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders)", "vote", 4, "seq4_restart_short", ORDERS, SHORT)]
    m5name = {"restart": "restart", "vote4_restart": "vote4_restart", "vote4_restart_short": "vote4_restart_short", "seq4_restart": "seq4_restart", "seq4_restart_short": "seq4_restart_short"}
    for m in ("base", "rl", "think"):
        for text, fam, n, rule, orders, chosen in rules:
            if m == "think" and "restart" in rule and rule not in ("seq4_restart", "seq4_restart_short", "vote4_restart_short"):
                continue                                             # Think-SFT has no restart rows: these equal the rows without restart
            d = play(H[m], F.RULES[rule], orders)
            p5 = play(M5[m], F.RULES[m5name.get(rule, rule)], orders)
            extra = {"math500": {"right": float(p5["s"].sum()), "tokens": float(p5["t"].mean())}, "key": f"{m}|{rule}"}
            if v4:
                extra["s_v4"] = play(H4[m], F.RULES[rule], orders)["s"]
            note = " (no restart rows: restart = none)" if m == "think" and "restart" in rule else ""
            add(f"{NAME[m]}, {text}{note}", fam, n, REWARD[m], chosen, RUNS["hard328"][m], d, **extra)
    d = play(H["think"], cap_rule(L), ORDERS)
    add(f"Think-SFT + cue, one sample stopped at {L:,} tokens (tokens matched to one RL sample; mean of 4)", "single", 1, "no",
        "L set from the 328's token counts, no score read", RUNS["hard328"]["think"], d, key="think|capL", cap_L=L,
        **({"s_v4": play(H4["think"], cap_rule(L), ORDERS)["s"]} if v4 else {}))
    add(f"RL plain, one sample stopped at the same {L:,} tokens (mean of 4)", "single", 1, "yes", "L set from the 328's token counts, no score read",
        RUNS["hard328"]["rl"], play(H["rl"], cap_rule(L), ORDERS), key="rl|capL", **({"s_v4": play(H4["rl"], cap_rule(L), ORDERS)["s"]} if v4 else {}))
    for counts, reward in (({"rl": 2, "think": 2}, "partly"), ({"rl": 2, "base": 2}, "partly"), ({"think": 2, "base": 2}, "no"),
                           ({"rl": 4, "think": 4}, "partly"), ({"think": 4, "base": 4}, "no")):
        d = mixed(H, counts)
        extra = {"s_v4": mixed(H4, counts)["s"]} if v4 else {}
        add("mixed vote, " + " + ".join(f"{c} {NAME[k]}" for k, c in counts.items()) + " (mean over combinations)", "vote", sum(counts.values()), reward,
            "no (every mix is reported, none picked)", "mixvote from the three runs", d, key="mix|" + "+".join(f"{c}{k}" for k, c in counts.items()), **extra)
    relay = {}
    for f in ("rl", "think"):
        for c in (25, 50):
            for line in open(RES / f"relay/{f}_c{c}-01/rows.jsonl"):
                r = json.loads(line)
                relay.setdefault((r["writer"], r["finisher"], r["cut"]), {})[r["problem_index"]] = r
    for (w, f, c), by in sorted(relay.items()):
        assert sorted(by) == idxs, f"relay {w}->{f} {c}: problems differ"
        rs = [by[i] for i in idxs]
        d = {"s": np.array([r["score_v3"] for r in rs], float), "a": np.array([r["extracted_v3"] is None for r in rs], float), "t": np.array([r["n_new"] + r["n_prefix"] for r in rs], float)}
        full = {"think": "Think-SFT + cue", "rl": "RL"}
        add(f"relay: {full[w]} writes the first {c} %, {full[f]} finishes", "single", 1, "no" if w == f == "think" else "yes" if w == f == "rl" else "partly",
            "no (arms and cuts filed in SPEC_relay)", f"relay/{f}_c{c}-01", d, key=f"relay|{w}->{f}|{c}",
            tokens_finisher_only=float(np.mean([r["n_new"] for r in rs])))
    ax = json.loads((RES / "axis/hard328-01/vectors.json").read_text())
    assert ax["problem_indices"] == idxs
    cells = json.loads((RES / "day1_wdiff328/readout.json").read_text())["cells"]
    for arm, cell, text, reward in (("base_plain", "base_plain_T1", "base plain, one sample", "no"), ("base_cue", "base_cue_T1", "base + cue, one sample, Day-1 #1 draw", "no"),
                                    ("rl_plain", "rl_plain_T1", "RL plain, one sample, Day-1 #1 draw", "yes"), ("rl_cue", "rl_cue_T1", "RL + cue, one sample", "yes"),
                                    ("theta0.25_cue", "theta0.25_cue", "base + 0.25 (RL - base) + cue, one sample", "partly"),
                                    ("theta0.5_cue", "theta0.5_cue", "base + 0.5 (RL - base) + cue, one sample", "partly"),
                                    ("code_cue", "code1_cue", "RL-Zero-Code + cue, one sample", "yes (code reward)")):
        add(text, "single", 1, reward, "no", f"axis/hard328-01/vectors.json [{arm}]", {"s": np.array(ax["arms"][arm], float), "a": None, "t": cells[cell]["mean_generated_tokens"]},
            cap_hits=cells[cell]["cap_hits"], key=f"axis|{arm}")
    for arm, text in (("sft1_cue", "Think-SFT + cue, one sample, other workspace (sameraslan)"), ("sft1_plain", "Think-SFT plain, one sample (sameraslan)")):
        pp = json.loads(subprocess.check_output(["git", "show", f"{OTHER[0]}:{OTHER[1].format(arm)}"], cwd=STUDY))
        assert [p["problem_index"] for p in pp] == idxs
        add(text, "single", 1, "no", "no", f"git {OTHER[0][:7]}:{OTHER[1].format(arm)}", {"s": np.array([p["score_v3"] for p in pp], float), "a": None,
            "t": np.array([p["n_generated"] for p in pp], float)}, cap_hits=sum(p["cap_hit"] for p in pp), key=f"other|{arm}")
    return rows, {"H": H, "M5": M5, "idxs": idxs, "relay": relay, "v4": bool(v4), "cap_L": L}


def columns(rows: list, idxs: list, flagged: list) -> None:
    """Adds every table column to each row, in place."""
    n = len(idxs)
    idx = idx_matrix(n)
    keep = np.array([i not in flagged for i in idxs])
    idx_c = idx_matrix(int(keep.sum()))
    by = {r["key"]: r for r in rows}
    ref = {"single": (by["base|single"], by["rl|single"]), "vote": (by["base|vote4"], by["rl|vote4"])}
    b1, r1 = ref["single"]
    for r in rows:
        s, (b, rl) = r["s"], ref[r["family"]]
        r["right"] = float(s.sum())
        r["abstained"] = None if r["a"] is None else float(r["a"].sum())
        r["wrong"] = None if r["a"] is None else n - r["right"] - r["abstained"]
        r["accuracy"] = {"percent": float(100 * s.mean()), "interval95": interval(100 * s[idx].mean(1))}
        for name, o in (("minus_base_single", b1), ("minus_rl_single", r1)):
            r[name] = {"points": float(100 * (s - o["s"]).mean()), "interval95": interval(100 * (s - o["s"])[idx].mean(1))}
        r["share"] = share(s, b["s"], rl["s"], idx)
        t = r["t"]
        r["tokens"] = float(np.mean(t))
        r["token_multiple"] = {"x": r["tokens"] / float(r1["t"].mean()), "interval95": list(F.ratio_interval(t, r1["t"])) if isinstance(t, np.ndarray) else None}
        r["clean322"] = {"right": float(s[keep].sum()), "n": int(keep.sum()), "share": share(s[keep], b["s"][keep], rl["s"][keep], idx_c)}
        if "s_v4" in r:
            r["v4"] = {"right": float(r["s_v4"].sum()), "share": share(r["s_v4"], b["s_v4"], rl["s_v4"], idx)}


def checks(rows: list, ctx: dict, flagged: list) -> list:
    """Every posted number against the committed rows. (where posted, what, expected, got)."""
    H, M5, idxs = ctx["H"], ctx["M5"], ctx["idxs"]
    by = {r["key"]: r for r in rows}
    out = []

    def chk(where, what, expected, got, digits=0):
        got, ok = same(expected, got, digits)
        out.append({"posted_in": where, "what": what, "expected": expected, "got": got, "pass": ok})

    def stored(bench, m, rule):
        return play({"hard328": H, "math500": M5}[bench][m], F.RULES[rule])

    A, B, C = "README 'The 328 with four samples and restarts' / result-5c961a", "README 'Think-SFT with the cue under the vote rules' / result-818c20", "README 'Mixed-model vote' / result-0033d7"
    st = {}
    for m, exp in (("base", {"single": (161, 9074), "restart": (172, 13665), "vote4": (192, 36902), "vote4_restart": (195, 55306)}),
                   ("rl", {"single": (207, 9437), "restart": (213, 11484), "vote4": (221, 37299), "vote4_restart": (224, 44108)})):
        for rule, (right, tok) in exp.items():
            st[m, rule] = d = stored("hard328", m, rule)
            chk(A, f"{NAME[m]} {rule} right, stored order", right, d["s"].sum())
            chk(A, f"{NAME[m]} {rule} tokens per problem", tok, d["t"].mean())
    for rule, pts, ci in (("single", 14.0, (9.5, 18.9)), ("restart", 12.5, (7.9, 17.4)), ("vote4", 8.8, (5.2, 12.8)), ("vote4_restart", 8.8, (5.5, 12.5))):
        x, y = st["rl", rule]["s"], st["base", rule]["s"]
        chk(A, f"RL minus base, {rule}, points", pts, 100 * (x - y).mean(), 1)
        chk(A, f"RL minus base, {rule}, interval", ci, S.paired_bootstrap(x, y, BOOT), 1)
    for m, exp in (("base", (161, 161, 152, 160)), ("rl", (207, 190, 209, 194)), ("think", (212, 212, 211, 201))):
        chk(A if m != "think" else B, f"{NAME[m]} right of each sample", exp, [sum(H[m][i][s][0]["score_v3"] for i in idxs) for s in range(4)])
    chk(A, "base + cue vote over 4, ties to the shortest (prediction 5)", 191, by["base|vote4_short"]["right"])
    for m, exp in (("think", {"single": (212, 209.0, 10137), "vote4": (241, None, 40410), "seq3": (241, 233.2, 26269), "seq4_restart": (241, 238.9, 30904),
                              "seq4_restart_short": (240, 239.5, 30904), "vote4_restart_short": (239, None, 40410)}),
                   ("rl", {"seq3": (216, 212.7, 23613), "seq4_restart": (224, 218.2, 31326), "seq4_restart_short": (222, 220.5, 31326), "vote4_restart_short": (220, None, 44108)}),
                   ("base", {"seq3": (183, 178.8, 25601), "seq4_restart": (194, 190.8, 46317), "seq4_restart_short": (198, 198.5, 46317), "vote4_restart_short": (199, None, 55306)})):
        for rule, (right, r24, tok) in exp.items():
            d = stored("hard328", m, rule)
            chk(B, f"{NAME[m]} {rule} right, stored order", right, d["s"].sum())
            chk(B, f"{NAME[m]} {rule} tokens per problem, stored order", tok, d["t"].mean())
            if r24 is not None:
                chk(B, f"{NAME[m]} {rule} right, mean of 24 orders", r24, by[f"{m}|{rule}"]["right"], 1)
    for key, right, tok in (("base|single", 158.5, 9225), ("rl|single", 200.0, 9325), ("think|single", 209.0, 10103), ("think|vote4", 241, 40410),
                            ("mix|2rl+2think", 228.1, 38855), ("mix|2rl+2base", 207.6, 37101), ("mix|2think+2base", 220.8, 38656), ("mix|4rl+4think", 239.0, 77710),
                            ("mix|4think+4base", 238.0, 77312)):
        chk(C, f"{key} right", right, by[key]["right"], 1)
        chk(C, f"{key} tokens per problem", tok, by[key]["tokens"])
    chk(C, "2 RL + 2 Think-SFT range over combinations", (214, 237), by["mix|2rl+2think"]["range"])
    for what, x, y, pts, ci in (("Think-SFT minus RL, one sample", "think|single", "rl|single", 2.7, (0.4, 5.2)), ("Think-SFT minus RL, vote over 4", "think|vote4", "rl|vote4", 6.1, (3.0, 9.5)),
                                ("2 RL + 2 Think-SFT minus 4 RL", "mix|2rl+2think", "rl|vote4", 2.2, (0.3, 4.2)), ("2 RL + 2 Think-SFT minus 4 Think-SFT", "mix|2rl+2think", "think|vote4", -3.9, (-6.2, -1.8))):
        p = M.paired(by[x]["s"], by[y]["s"])
        chk(C, what + ", points", pts, p["points"], 1)
        chk(C, what + ", interval", ci, p["interval95"], 1)
    D = "README 'Risk-coverage', outcome tables / result-b006f5"
    for key, exp in (("think|vote4", (30, 57, 241)), ("rl|vote4", (0, 107, 221))):
        chk(D, f"{key} abstained, wrong, right", exp, [by[key]["abstained"], by[key]["wrong"], by[key]["right"]])
    for key, exp in (("think|single", (326, 150, 836)), ("rl|single", (36, 476, 800))):
        chk(D, f"{key} abstained, wrong, right, summed over the 4 samples", exp, [4 * by[key]["abstained"], 4 * by[key]["wrong"], 4 * by[key]["right"]])
    E = "README 'Think-SFT training-data overlap' (sft_overlap-03) / result-d484cb"
    keep = np.array([i not in flagged for i in idxs])
    chk(E, "problems flagged", 6, len(flagged))
    chk(E, "vote over 4 without the 6 flagged: Think-SFT, RL", (235, 215), [by["think|vote4"]["clean322"]["right"], by["rl|vote4"]["clean322"]["right"]])
    p = M.paired(by["think|vote4"]["s"][keep], by["rl|vote4"]["s"][keep])
    chk(E, "Think-SFT minus RL without the 6, points", 6.2, p["points"], 1)
    chk(E, "Think-SFT minus RL without the 6, interval", (3.1, 9.6), p["interval95"], 1)
    chk(B, "one sample (sample 0) without the 6 flagged: Think-SFT, RL", (207, 201), [sum(H[m][i][0][0]["score_v3"] for i in idxs if i not in flagged) for m in ("think", "rl")])
    fr = json.loads((RES / "frontier/hard328-01/readout.json").read_text())["base_minus_rl_single"]["single"]
    chk("results/frontier/hard328-01/readout.json", "base single minus RL single (24-order means), points", round(fr["points"], 2), by["base|single"]["minus_rl_single"]["points"], 2)
    chk("results/frontier/hard328-01/readout.json", "base single token multiple of one RL sample, interval", [round(v, 3) for v in fr["token_multiple_interval95"]], by["base|single"]["token_multiple"]["interval95"], 3)
    Rl = "README 'Relay' / result-bce075"
    for key, right, tok in (("think->rl|50", 209, 8923), ("think->rl|25", 207, 8900), ("rl->think|25", 204, 10511), ("rl->think|50", 199, 10664),
                            ("think->think|50", 211, None), ("think->think|25", 219, None), ("rl->rl|25", 206, None), ("rl->rl|50", 193, None)):
        r = by["relay|" + key]
        chk(Rl, f"relay {key} right", right, r["right"])
        if tok:
            chk(Rl, f"relay {key} tokens per problem (prefix + continuation)", tok, r["tokens"])
    for c, pts, ci in ((50, -0.6, (-4.3, 3.0)), (25, -3.7, (-7.6, 0.3))):
        x, y = by[f"relay|think->rl|{c}"]["s"], by[f"relay|think->think|{c}"]["s"]
        chk(Rl, f"Think->RL minus Think->Think at {c} %, points", pts, 100 * (x - y).mean(), 1)
        chk(Rl, f"Think->RL minus Think->Think at {c} %, interval", ci, S.paired_bootstrap(x, y, BOOT, 0), 1)
    W = "README 'Harder 328: four cells' and 'The same cells on the 328 harder problems' (day1_hard328, day1_wdiff328 readouts)"
    for arm, right in (("base_plain", 76), ("base_cue", 164), ("rl_plain", 206), ("rl_cue", 205), ("theta0.25_cue", 182), ("theta0.5_cue", 190), ("code_cue", 187)):
        chk(W, f"{arm} right", right, by["axis|" + arm]["right"])
    O = "board result-32ff47 (sameraslan)"
    cue, plain = by["other|sft1_cue"], by["other|sft1_plain"]
    chk(O, "Think-SFT cue: right, cap hits, tokens", (219, 89, 10123), [cue["right"], cue["cap_hits"], cue["tokens"]])
    chk(O, "Think-SFT plain: right, cap hits", (203, 86), [plain["right"], plain["cap_hits"]])
    for what, x, y, pts, ci in (("cue minus the cued base (Day-1 #1 draw)", cue, by["axis|base_cue"], 16.8, (12.5, 21.3)), ("cue minus RL plain (Day-1 #1 draw)", cue, by["axis|rl_plain"], 4.0, (0.0, 7.9)),
                                ("cue minus RL cue", cue, by["axis|rl_cue"], 4.3, (0.9, 7.6)), ("plain minus RL plain", plain, by["axis|rl_plain"], -0.9, (-5.2, 3.4))):
        chk(O, what + ", points", pts, 100 * (x["s"] - y["s"]).mean(), 1)
        chk(O, what + ", interval", ci, S.paired_bootstrap(x["s"], y["s"], BOOT), 1)
    T = "README 'Token frontier' and 'Think-SFT with the cue under the vote rules', MATH-500 rows"
    for m, exp in (("base", {"single": (405, 410.5, 3808), "vote4": (446, None, 16034), "vote4_short": (453, None, 16034), "vote4_restart_short": (454, None, 19697), "seq4": (446, 448.2, 11369),
                             "seq4_short": (451, 452.0, 11369)}),
                   ("rl", {"single": (456, 460.0, 4675), "vote4": (474, None, 18747), "vote4_restart": (475, None, 19864), "seq4": (474, 474.3, 11098), "seq4_short": (475, 474.5, 11098)}),
                   ("think", {"single": (461, 460.2, 4900), "vote4": (481, None, 19503), "seq4": (481, 480.8, 11521), "seq4_short": (481, 480.5, 11521)})):
        for rule, (right, r24, tok) in exp.items():
            d = stored("math500", m, rule)
            chk(T, f"MATH-500 {NAME[m]} {rule} right, stored order", right, d["s"].sum())
            chk(T, f"MATH-500 {NAME[m]} {rule} tokens per problem, stored order", tok, d["t"].mean())
            if r24 is not None:
                chk(T, f"MATH-500 {NAME[m]} {rule} right, mean of 24 orders", r24, play(M5[m], F.RULES[rule], ORDERS)["s"].sum(), 1)
    return out


def planted() -> list:
    """The share on planted configurations, and a check that must fail."""
    rng = np.random.default_rng(1)
    b = (rng.random(328) < 0.48).astype(float)
    r = np.maximum(b, (rng.random(328) < 0.3).astype(float))
    idx = idx_matrix(328)
    res = []
    for name, x, want in (("equal to RL", r, 100.0), ("equal to the base", b, 0.0), ("the mean of base and RL", (b + r) / 2, 50.0)):
        sh = share(x, b, r, idx)
        ok = abs(sh["percent"] - want) < 1e-9 and all(abs(v - want) < 1e-9 for v in sh["interval95"])
        res.append({"planted": name, "expected_percent": want, "got_percent": sh["percent"], "got_interval95": sh["interval95"], "pass": bool(ok)})
    flip = r.copy()
    flip[0] = 1 - flip[0]
    res.append({"planted": "RL with one problem flipped: the check against RL's count has to fail", "expected": float(r.sum()), "got": float(flip.sum()),
                "pass": not same(float(r.sum()), flip.sum())[1] and same(float(r.sum()), r.sum())[1]})
    wide = share(r, b, b + (r - b) * (np.arange(328) < 6), idx)          # a denominator of 6 problems at most
    res.append({"planted": "a denominator carried by at most 6 problems is marked unstable", "denominator_interval95": wide["denominator_interval95"], "pass": wide["unstable"]})
    return res


def fmt(x, d=1) -> str:
    return f"{x:,.{d}f}".replace(".0", "") if d and abs(x - round(x)) < 1e-9 else f"{x:,.{d}f}"


def ci(v: dict, key="points", sign=True) -> str:
    s = "+" if sign else ""
    return f"{v[key]:{s}.1f} [{v['interval95'][0]:{s}.1f}, {v['interval95'][1]:{s}.1f}]"


def markdown(rows: list, ctx: dict) -> str:
    by = {r["key"]: r for r in rows}
    den = {f: by[f"rl|{k}"]["share"] for f, k in (("single", "single"), ("vote", "vote4"))}
    head = ["Configuration", "Family", "Samples", "Right", "Wrong", "Abstained", "Accuracy, % [95 %]", "minus base + cue one sample, points", "minus RL one sample, points",
            "Share of the gap closed, % [95 %]", "Tokens per problem", "Tokens, multiple of one RL sample [95 %]", "Clean 322: right, share %", "Grader v4: right, share %",
            "Reward-trained weights", "Chosen on the 328", "MATH-500: right of 500, tokens", "Rows"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        tm = r["token_multiple"]
        lines.append("| " + " | ".join([
            r["name"], r["family"], str(r["n_samples"]), fmt(r["right"]), "n/a" if r["wrong"] is None else fmt(r["wrong"]),
            f"cap hits {r['cap_hits']} (no extraction stored)" if r["abstained"] is None else fmt(r["abstained"]),
            ci(r["accuracy"], "percent", False), ci(r["minus_base_single"]), ci(r["minus_rl_single"]),
            ci(r["share"], "percent", False) + (" unstable" if r["share"]["unstable"] else ""),
            fmt(r["tokens"], 0) + (f" ({fmt(r['tokens_finisher_only'], 0)} by the finisher)" if "tokens_finisher_only" in r else ""),
            f"{tm['x']:.2f}" + (f" [{tm['interval95'][0]:.2f}, {tm['interval95'][1]:.2f}]" if tm["interval95"] else " (posted mean)"),
            f"{fmt(r['clean322']['right'])}, {r['clean322']['share']['percent']:.0f} [{r['clean322']['share']['interval95'][0]:.0f}, {r['clean322']['share']['interval95'][1]:.0f}]",
            f"{fmt(r['v4']['right'])}, {r['v4']['share']['percent']:.0f} [{r['v4']['share']['interval95'][0]:.0f}, {r['v4']['share']['interval95'][1]:.0f}]" if "v4" in r else "no text read",
            r["reward"], r["chosen_on_328"], f"{fmt(r['math500']['right'])}, {fmt(r['math500']['tokens'], 0)}" if "math500" in r else "", f"`{r['source']}`"]) + " |")
    notes = [
        "", "Share of the gap closed = (accuracy - base) / (RL - base), base = base + cue and RL = RL plain in the row's family. Family single: the mean of the four stored samples "
        f"({fmt(by['base|single']['right'])} and {fmt(by['rl|single']['right'])} of 328; denominator {ci({'points': den['single']['denominator_points'], 'interval95': den['single']['denominator_interval95']})} points). "
        f"Family vote: the plain vote over 4 ({fmt(by['base|vote4']['right'])} and {fmt(by['rl|vote4']['right'])}; denominator "
        f"{ci({'points': den['vote']['denominator_points'], 'interval95': den['vote']['denominator_interval95']})} points). "
        "Intervals: percentile bootstrap over the 328 problems, 5,000 resamples, seed 0, the same resamples in every column; the share's interval is the interval of the ratio. "
        "Abstained = no extracted answer (for a vote: no sample with one). Tokens = generated tokens per problem over every sample and restart drawn (relay: the writer's prefix plus the continuation). "
        "A row named 'mean of 4' or 'mean of 24 orders' has fractional counts; the stored-order counts are in checks.json. "
        "Grader v3 everywhere except the v4 column (v4a, `grader/repair_v4.py` amended; votes recounted on the v4 extraction; text read from the local raw answers, `v4_rows.jsonl`). "
        "Clean 322 = without the 6 problems of `results/wsp1/sft_overlap-03/flags.json`. T 1.0 / top-p 1.0, cap 16,384."]
    return "\n".join(lines + notes) + "\n"


def jsonable(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        return o.item()
    raise TypeError(type(o))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--v4-from", help="folder of local raw answers (runs/): compute v4_rows.jsonl")
    ap.add_argument("--v4-rows", help="a v4_rows.jsonl written earlier")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.test:
        res = planted()
        print(json.dumps(res, indent=1))
        sys.exit(0 if all(r["pass"] for r in res) else 1)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True)                                             # a run folder is never written twice
    v4_rows = out / "v4_rows.jsonl"
    if a.v4_from:
        write_v4(pathlib.Path(a.v4_from), {m: F.load(RES / p)[1] for m, p in RUNS["hard328"].items()}, v4_rows)
    elif a.v4_rows:
        v4_rows.write_text(pathlib.Path(a.v4_rows).read_text())
    rows, ctx = build(v4_rows if v4_rows.exists() else None)
    flags = json.loads((RES / "wsp1/sft_overlap-03/flags.json").read_text())["hard"]
    flagged = sorted(int(i) for i, f in flags.items() if f["flag"] != "none" and int(i) in ctx["idxs"])
    columns(rows, ctx["idxs"], flagged)
    ck = checks(rows, ctx, flagged)
    pl = planted()
    (out / "checks.json").write_text(json.dumps({"posted_numbers": ck, "passed": sum(c["pass"] for c in ck), "failed": [c for c in ck if not c["pass"]], "planted": pl}, indent=1))
    (out / "table.md").write_text(markdown(rows, ctx))
    drop = ("s", "a", "t", "s_v4")
    (out / "table.json").write_text(json.dumps({"n": len(ctx["idxs"]), "problem_indices": ctx["idxs"], "flagged_by_sft_overlap_03": flagged, "cap_L_matched": ctx["cap_L"],
                                                "rows": [{k: v for k, v in r.items() if k not in drop} for r in rows],
                                                "per_problem_right": {r["key"]: r["s"] for r in rows}}, default=jsonable))
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=STUDY, text=True).strip()
    (out / "run.json").write_text(json.dumps({"commit": commit, "command": "python -m studies.rlneurons.analysis.config_table " + " ".join(sys.argv[1:]), "job_id": None,
                                              "where": "laptop, no GPU", "spec": "studies/rlneurons/specs/SPEC_table.md", "sources": RUNS, "raw_answers_for_v4": RAW,
                                              "other_branch": {"commit": OTHER[0], "path": OTHER[1]}}, indent=1))
    print(f"{sum(c['pass'] for c in ck)} of {len(ck)} posted numbers reproduce; planted {sum(p['pass'] for p in pl)} of {len(pl)}")
    for c in ck:
        if not c["pass"]:
            print("  DOES NOT REPRODUCE:", c["posted_in"], "|", c["what"], "| expected", c["expected"], "got", c["got"])


if __name__ == "__main__":
    main()
