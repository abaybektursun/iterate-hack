"""The verified data layer of the paper "Theories on trial": every number recomputed from the committed round files.

    uv run --no-project --with numpy python studies/theory/paper/build_facts.py

Reads studies/theory/results/ (engine rounds 01-07, account runs, promoted run, forecast runs, selfopen-01),
studies/theory/lib/round.py (the MODELS table) and nothing else. Writes, next to this file:
  predictions.jsonl  one row per scored prediction (fields in ROW_DOC below)
  facts.json         every number the paper uses: {value, n, unit, source, note}
  calibration.json   observed coverage at each nominal level, theories against the two readers
Fails on any missing file or any stored score that the recomputation does not reproduce. No fallbacks.

Definitions (as the engine and the site page tools/finding_theories_on_trial.py use them; this file re-implements them):
  log score     log density at the measured value of a normal with mean = the forecast and sd = (high - low) / 3.29,
                floored at 1 % of max(|forecast|, 1)                                   (lib/round.py log_density)
  gain          log score of the theory minus log of the equal mixture of the two readers' densities, clipped to
                [-3, 3] nats; exists only where both readers gave intervals (rounds 3-7)  (lib/round.py gain_rows)
  nearer        |theory forecast - measured| < |mean of the readers' forecasts - measured|; equal is a tie. This is
                the site page's rule (_build), not an engine score. nearer_both is the stricter rule (nearer than
                each reader) that the forecast page uses.
  inside        low <= measured <= high.
  cluster       the theory id; a round-1 theory and its byte-identical r1- copy in rounds 2-3 are one cluster.
Bootstrap: clusters (theories) are resampled with replacement, 10,000 times, seed 0; 95 % percentile interval.
"""
import ast
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import NormalDist

import numpy as np

HERE = Path(__file__).resolve().parent
T = HERE.parent  # studies/theory
RES = T / "results"
ENG = RES / "engine"
REL = "studies/theory/results/"
B, SEED = 10_000, 0
ROUNDS = [1, 2, 3, 4, 5, 6, 7]
VERSION = {1: "1", 2: "2", 3: "3", 4: "4 (+5/5.1 duel)", 5: "5.1", 6: "6.3", 7: "7.1"}
VERSION_CHANGE = {  # one line each, from studies/theory/README.md (sections Files, Round 01-07, Account runs, Engine version 8)
    "1": "lib/check.py: a predictor given each theory guesses 58 held-out board numbers (points, no intervals); score = closer/farther counts against 2 no-theory predictors; one planted reversed theory.",
    "2": "lib/v2.py: each author files value + 90 % interval per held-out target; score = divergent wins minus losses (both readers outside the interval), against a reversed copy; exposed targets left out; published mechanisms imported.",
    "3": "lib/round.py: headless jobs in empty directories; readers file intervals too; score = log gain in nats against the mixture of the 2 readers, clipped to [-3, 3], with a bootstrap interval; held-out items no earlier round used.",
    "4": "offline tests become the main score: 12 pairwise different mechanisms, each with 3-6 predictions and exact recipes fixed by sha256 before any row is read, computed by scripts from stored per-problem rows; 2 no-theory readers predict the same numbers; held-out claims can only remove a theory.",
    "5/5.1": "rival stages: a blind agent writes the strongest other mechanism and tests where the two differ; gain = theory minus rival log density; 5.1 adds a second turn and a +-2 nat decision rule.",
    "6-6.3": "stage account: one budget of the base-to-RL gap whose shares sum to 1, tested like a theory; 6.1 at least 3 cells; 6.2 null cell, fits and zeros by construction not scored, replicate stage; 6.3 --account-from; 'within noise' no longer counts as outside.",
    "7/7.1": "experiments stage (each side predicts the other's GPU experiments, ranked by separation per GPU minute); 7.1: a duel test where the defender's centre is inside the rival's interval adds 0 and a win needs 2 separating tests; carried duel wins kept out of round totals; account only with --with-account.",
    "8": "forecasts inside the round (targets_open, forecast): theories and readers forecast the open work items; no round run with it in these files.",
}
ROW_DOC = {
    "series": "engine | account/run-0N", "round": "engine round (null for account runs)", "engine_version": "see facts.versions",
    "kind": "r1_hand_matched | heldout_claim (rounds 2-3, the main score there) | offline_test (rounds 4-7, the main score) | "
            "carried_duel_row (round 6: a promoted rival's round-5 duel tests, 'readers' = the theory it replaced) | "
            "heldout_filter_claim (rounds 4-7, survivors only, not in the headline) | exposed_claim (round 2, left out by the engine)",
    "theory": "id as in the round files", "cluster": "bootstrap cluster", "qid": "target or test id", "quantity": "what is measured", "unit": "",
    "measured": "", "t_value/t_low/t_high": "theory's forecast and 90 % interval", "r1_*/r2_*": "reader 1 and 2 (interval null where none was filed)",
    "t_inside/r1_inside/r2_inside": "low <= measured <= high", "logp_t/logp_r1/logp_r2/logp_mix": "log scores (nats)",
    "gain": "recomputed, clipped to [-3, 3]; null without reader intervals", "gain_stored": "as in the metrics file",
    "nearer": "w theory nearer than the readers' mean, t tie, l readers nearer (site rule); null when not compared",
    "nearer_both": "theory strictly nearer than each reader", "z_t/z_r1/z_r2": "(measured - forecast) / sd",
    "flags": "headline (in the 403), compared (in the 394), reader_intervals (in the 236), carried, exposed, tie, within_noise, "
             "leak_context (round 2: readers and new authors had a commit subject with result numbers in context), divergent "
             "(both readers' centres outside the theory's interval)",
    "source": "file and key",
}


def load(p):
    return json.loads(Path(p).read_text())


def jsonl(p):
    return [json.loads(line) for line in Path(p).read_text().splitlines() if line.strip()]


def sd_of(c):
    return max((c["high"] - c["low"]) / 3.29, 0.01 * max(abs(c["value"]), 1))


def logd(x, c):
    sd = sd_of(c)
    return -0.5 * ((x - c["value"]) / sd) ** 2 - math.log(sd) - 0.5 * math.log(2 * math.pi)


def clip3(x):
    return min(3.0, max(-3.0, x))


def cut(s, n=200):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1] + "…"


def norm_id(rd, t):
    return "r1-" + t if rd == 1 else t


def make_row(series, rd, kind, theory, qid, quantity, unit, measured, claim, readers, source, gain_stored=None, flags=()):
    """claim: {value, low, high}; readers: list of numbers or {value, low, high} (0, 1 or 2 of them)."""
    rs = [r if isinstance(r, dict) else {"value": r, "low": None, "high": None} for r in readers]
    full = len(rs) == 2 and all(r["low"] is not None for r in rs)
    row = {"series": series, "round": rd, "engine_version": VERSION.get(rd), "kind": kind, "theory": theory,
           "cluster": norm_id(rd, theory) if series == "engine" else f"{series}:{theory}", "qid": qid, "quantity": cut(quantity),
           "unit": unit, "measured": measured, "t_value": claim["value"], "t_low": claim["low"], "t_high": claim["high"],
           "t_inside": claim["low"] <= measured <= claim["high"], "logp_t": round(logd(measured, claim), 4),
           "z_t": round((measured - claim["value"]) / sd_of(claim), 4)}
    for j in (0, 1):
        r = rs[j] if j < len(rs) else {"value": None, "low": None, "high": None}
        has = r["low"] is not None
        row |= {f"r{j + 1}_value": r["value"], f"r{j + 1}_low": r["low"], f"r{j + 1}_high": r["high"],
                f"r{j + 1}_inside": (r["low"] <= measured <= r["high"]) if has else None,
                f"logp_r{j + 1}": round(logd(measured, r), 4) if has else None,
                f"z_r{j + 1}": round((measured - r["value"]) / sd_of(r), 4) if has else None}
    carried = kind == "carried_duel_row"
    if full:
        a, b = (logd(measured, r) for r in rs)
        mix = max(a, b) + math.log(0.5 * (1 + math.exp(-abs(a - b))))
        row |= {"logp_mix": round(mix, 4), "gain": round(clip3(logd(measured, claim) - mix), 4)}
    else:
        row |= {"logp_mix": None, "gain": None}
    row["gain_stored"] = gain_stored
    if full and gain_stored is not None and abs(row["gain"] - gain_stored) > 2e-3:
        raise SystemExit(f"{source}: stored gain {gain_stored}, recomputed {row['gain']}")
    fl = set(flags)
    if len(rs) == 2 and not carried:
        d, dr = abs(claim["value"] - measured), abs(sum(r["value"] for r in rs) / 2 - measured)
        row["nearer"] = "w" if d < dr else "t" if d == dr else "l"
        row["nearer_both"] = all(d < abs(r["value"] - measured) for r in rs)
        row["abs_err_t"], row["abs_err_reader_mean"] = d, dr
        if all(not claim["low"] <= r["value"] <= claim["high"] for r in rs):
            fl.add("divergent")
        if row["nearer"] == "t":
            fl.add("tie")
    else:
        row |= {"nearer": None, "nearer_both": None, "abs_err_t": abs(claim["value"] - measured), "abs_err_reader_mean": None}
    if "headline" in fl and row["nearer"]:
        fl.add("compared")
        if full:
            fl.add("reader_intervals")
    row["flags"] = sorted(fl)
    row["source"] = source
    return row


def build_rows():
    rows, filed, theories = [], Counter(), []  # theories: (round, id, fate, state string, duel state, separating)
    # ---- round 1: the 7 interval predictions the held-out items had measured (matched by hand after scoring)
    m1 = load(ENG / "round-01/metrics.json")
    for t in m1["theories"]:
        if t != "planted":
            theories.append((1, t, "o", "did not beat the readers", None, None))
    for i, x in enumerate(load(ENG / "round-01/predictions_measured.json")):
        rows.append(make_row("engine", 1, "r1_hand_matched", x["theory"], x["targets"][0], x["experiment"], x["unit"], x["measured"],
                             {"value": x["predicted"], "low": x["low"], "high": x["high"]}, [x["null_1"], x["null_2"]],
                             f"{REL}engine/round-01/predictions_measured.json[{i}]", flags=["headline"]))
        assert rows[-1]["t_inside"] == x["inside"]
        filed[1] += 1
    # ---- rounds 2-3: claims on numbers posted to the board after the cutoff
    for rd, f in ((2, "metrics_v2.json"), (3, "metrics_v3.json")):
        d = ENG / f"round-0{rd}"
        tg = {x["id"]: x for x in jsonl(d / "targets.jsonl")}
        m = load(d / f)
        for t, v in m["theories"].items():
            rv = load(d / "reviews" / f"{t}.json") if (d / "reviews" / f"{t}.json").exists() else {}
            verdict = str(rv.get("verdict", ""))
            fate = "r" if verdict.startswith("refuted") else "s" if v["state"] == "passes" else "o"
            theories.append((rd, t, fate, "refuted by its review" if fate == "r" else v["state"], None, None))
            for x in v["rows"]:
                rows.append(make_row("engine", rd, "heldout_claim", t, x["id"], tg[x["id"]]["what"], tg[x["id"]]["unit"], x["measured"], x,
                                     x["nulls"], f"{REL}engine/round-0{rd}/{f}:theories.{t}.rows[id={x['id']}]", x.get("gain"),
                                     ["headline"] + (["leak_context"] if rd == 2 else [])))
                filed[rd] += 1
        if rd == 2:  # claims on the exposed targets: left out by the engine, kept here with a flag
            exposed = set(load(d / "exposed.json")["items"])
            assert exposed == set(m["exposed_items"])
            nulls = [{p["id"]: p["value"] for p in jsonl(d / "predictions" / f"null-{k}.jsonl")} for k in (1, 2)]
            for t in m["theories"]:
                for c in jsonl(d / "claims" / f"{t}.jsonl"):
                    if tg[c["id"]]["item"] in exposed:
                        rows.append(make_row("engine", 2, "exposed_claim", t, c["id"], tg[c["id"]]["what"], tg[c["id"]]["unit"],
                                             tg[c["id"]]["value"], c, [n[c["id"]] for n in nulls],
                                             f"{REL}engine/round-02/claims/{t}.jsonl[id={c['id']}]", flags=["exposed", "leak_context"]))
    # ---- rounds 4-7: offline predictions computed from stored rows; plus the survivors' held-out claims
    for rd in (4, 5, 6, 7):
        d = ENG / f"round-{rd:02d}"
        v4, v5 = load(d / "metrics_v4.json")["theories"], load(d / "metrics_v5.json")["theories"]
        blind = {x["id"]: x for x in jsonl(d / "tests_blind.jsonl")}
        tgt = {x["id"]: x for x in jsonl(d / "targets.jsonl")} if (d / "targets.jsonl").exists() else {}
        for t, v in v4.items():
            duel = v5.get(t)
            st = v["state"]
            fate = ("r" if st == "refuted" else "l" if duel and duel["state"] == "loses to rival" else "s" if st == "survives"
                    else "n" if st == "no gain" else "o")
            theories.append((rd, t, fate, st, duel["state"] if duel else None, duel["separating"] if duel else None))
            carried = v.get("carried_from")
            for x in v["rows"] if not carried or v["offline"] else []:
                if x.get("not_scored"):
                    continue
                filed[rd] += 1
                if "measured" not in x or x["measured"] is None:
                    continue
                k = x["k"]
                src = f"{REL}engine/round-{rd:02d}/metrics_v4.json:theories.{t}.rows[k={k}]"
                if carried:
                    s5 = load(ENG / carried / "metrics_v5.json")["theories"][t[:-len("-rival")]]["rows"][k - 1]
                    assert abs(s5["measured"] - x["measured"]) < 1e-9 and s5["rival"]["value"] == x["value"]
                    rows.append(make_row("engine", rd, "carried_duel_row", t, f"{t}:p{k}", s5["experiment"], "", x["measured"], x,
                                         x["nulls"], src, x["gain"], ["headline", "carried"]))
                else:
                    pid = x.get("id") or f"{t}:p{k}"
                    rows.append(make_row("engine", rd, "offline_test", t, pid, blind[pid]["experiment"], blind[pid]["unit"], x["measured"],
                                         x, x["nulls"], src, x["gain"], ["headline"] + (["within_noise"] if x.get("within_noise") else [])))
                    assert rows[-1]["t_inside"] == x["inside"], src
            for x in v.get("heldout_rows", []):
                rows.append(make_row("engine", rd, "heldout_filter_claim", t, x["id"], tgt[x["id"]]["what"], tgt[x["id"]]["unit"],
                                     x["measured"], x, x["nulls"],
                                     f"{REL}engine/round-{rd:02d}/metrics_v4.json:theories.{t}.heldout_rows[id={x['id']}]", x["gain"]))
    # ---- account runs: each run's own account, not part of the engine headline
    for run, name in (("run-01", "r5-account"), ("run-02", "r6-account"), ("run-03", "r7-account")):
        d = RES / "account" / run
        blind = {x["id"]: x for x in jsonl(d / "tests_blind.jsonl")}
        for x in load(d / "metrics_v4.json")["theories"][name]["rows"]:
            if "gain" in x:
                pid = x.get("id") or f"{name}:p{x['k']}"
                rows.append(make_row(f"account/{run}", None, "offline_test", name, pid, blind[pid]["experiment"], blind[pid]["unit"],
                                     x["measured"], x, x["nulls"], f"{REL}account/{run}/metrics_v4.json:theories.{name}.rows[k={x['k']}]",
                                     x["gain"], ["within_noise"] if x.get("within_noise") else []))
    return rows, filed, theories


# ---------- statistics ----------

def boot(rows, num, den=None):
    """Cluster bootstrap over theories of sum(num) / sum(den) (or sum(num) when den is None): [lo, hi] at 95 %."""
    cl = sorted({r["cluster"] for r in rows})
    if len(cl) < 2:
        return None
    ix = {c: i for i, c in enumerate(cl)}
    a, b = np.zeros(len(cl)), np.zeros(len(cl))
    for r in rows:
        a[ix[r["cluster"]]] += num(r)
        b[ix[r["cluster"]]] += den(r) if den else 0
    pick = np.random.default_rng(SEED).integers(0, len(cl), size=(B, len(cl)))
    s = a[pick].sum(1)
    if den:
        t = b[pick].sum(1)
        s = s[t > 0] / t[t > 0]
    return [round(float(np.percentile(s, 2.5)), 4), round(float(np.percentile(s, 97.5)), 4)]


def fact(value, n=None, unit="", source="", note=""):
    return {"value": value, "n": n, "unit": unit, "source": source, "note": note}


def share(rows, f, source, note=""):
    k, n = sum(bool(f(r)) for r in rows), len(rows)
    return fact(round(k / n, 4) if n else None, n, "fraction", source,
                (note + " " if note else "") + f"count {k} of {n}; clusters {len({r['cluster'] for r in rows})}; "
                f"95 % cluster bootstrap {boot(rows, lambda r: float(bool(f(r))), lambda r: 1.0)}")


def total(rows, f, source, note=""):
    s = sum(f(r) for r in rows)
    return fact(round(s, 2), len(rows), "nats", source,
                (note + " " if note else "") + f"mean per prediction {round(s / len(rows), 4) if rows else None} "
                f"(95 % cluster bootstrap {boot(rows, f, lambda r: 1.0)}); 95 % cluster bootstrap of the total {boot(rows, f)}; "
                f"clusters {len({r['cluster'] for r in rows})}")


def headline(rows, source, label):
    """The headline block on one set of rows (already restricted to the wanted rounds and flags)."""
    cmp_ = [r for r in rows if r["nearer"]]
    ri = [r for r in cmp_ if r["gain"] is not None]
    out = {
        "nearer": share(cmp_, lambda r: r["nearer"] == "w", source, f"{label}: theory nearer than the mean of the two readers; "
                        f"ties {sum(r['nearer'] == 't' for r in cmp_)} count as not nearer;"),
        "nearer_ties_dropped": share([r for r in cmp_ if r["nearer"] != "t"], lambda r: r["nearer"] == "w", source, f"{label}: ties dropped;"),
        "nearer_than_both_readers": share(cmp_, lambda r: r["nearer_both"], source, f"{label}: strictly nearer than each reader;"),
        "coverage_theory_all_scored": share(rows, lambda r: r["t_inside"], source, f"{label}: measured inside the theory's 90 % interval, every scored prediction;"),
    }
    if ri:
        out |= {
            "coverage_theory": share(ri, lambda r: r["t_inside"], source, f"{label}: predictions where both readers filed an interval;"),
            "coverage_reader_1": share(ri, lambda r: r["r1_inside"], source, f"{label}: same predictions;"),
            "coverage_reader_2": share(ri, lambda r: r["r2_inside"], source, f"{label}: same predictions;"),
            "coverage_gap_theory_minus_readers_mean": fact(
                round(sum(r["t_inside"] - (r["r1_inside"] + r["r2_inside"]) / 2 for r in ri) / len(ri), 4), len(ri), "fraction", source,
                f"{label}: paired on the same predictions; 95 % cluster bootstrap "
                f"{boot(ri, lambda r: r['t_inside'] - (r['r1_inside'] + r['r2_inside']) / 2, lambda r: 1.0)}"),
            "gain_total": total(ri, lambda r: r["gain"], source, f"{label}: log gain against the mixture of the two readers, clipped to [-3, 3];"),
            "gain_at_clip": fact([sum(r["gain"] <= -3 for r in ri), sum(r["gain"] >= 3 for r in ri)], len(ri), "predictions at -3, at +3", source, label),
            "median_interval_width_ratio_theory_over_reader_mean": fact(
                round(float(np.median([(r["t_high"] - r["t_low"]) / (((r["r1_high"] - r["r1_low"]) + (r["r2_high"] - r["r2_low"])) / 2)
                                       for r in ri if (r["r1_high"] - r["r1_low"]) + (r["r2_high"] - r["r2_low"]) > 0])), 3),
                len(ri), "ratio", source, label),
        }
    return out


def calibration(rows):
    """Observed coverage at each nominal level. scaled_interval: the filed interval scaled about the forecast by
    z(level) / z(0.90), which keeps its asymmetry and equals the filed interval at 0.90. engine_normal: |z| <= z(level)
    with the engine's sd = (high - low) / 3.29."""
    levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    z90 = NormalDist().inv_cdf(0.95)

    def inside(r, who, s):
        v, lo, hi, m = r[f"{who}_value"], r[f"{who}_low"], r[f"{who}_high"], r["measured"]
        return v - s * (v - lo) <= m <= v + s * (hi - v)
    sets = {
        "rounds_3_7_both_readers_filed_intervals": ([r for r in rows if "reader_intervals" in r["flags"]], ["t", "r1", "r2"]),
        "rounds_4_7_offline_tests": ([r for r in rows if "reader_intervals" in r["flags"] and r["round"] >= 4], ["t", "r1", "r2"]),
        "rounds_4_7_offline_tests_without_r6_account": ([r for r in rows if "reader_intervals" in r["flags"] and r["round"] >= 4
                                                         and r["theory"] != "r6-account"], ["t", "r1", "r2"]),
        "all_rounds_compared_theory_only": ([r for r in rows if "compared" in r["flags"]], ["t"]),
    }
    out = {"definition": calibration.__doc__, "who": {"t": "theories", "r1": "reader 1", "r2": "reader 2"}, "sets": {}}
    for name, (rs, whos) in sets.items():
        table = []
        for p in levels:
            zp = NormalDist().inv_cdf(0.5 + p / 2)
            line = {"nominal": p}
            for w in whos:
                f = lambda r, w=w: float(inside(r, w, zp / z90))
                line[w] = {"scaled_interval": round(sum(f(r) for r in rs) / len(rs), 4), "ci95_cluster": boot(rs, f, lambda r: 1.0),
                           "engine_normal": round(sum(abs(r[f"z_{w}"]) <= zp for r in rs) / len(rs), 4)}
            table.append(line)
        zbins = [0, 0.5, 1, 1.645, 2, 3, 5, float("inf")]
        out["sets"][name] = {"n": len(rs), "clusters": len({r["cluster"] for r in rs}), "levels": table,
                             "abs_z_bins": {"edges": zbins[:-1] + ["inf"], **{w: [sum(a <= abs(r[f"z_{w}"]) < b for r in rs)
                                                                                 for a, b in zip(zbins, zbins[1:])] for w in whos}}}
    return out


def fates(theories):
    last, ever = {}, defaultdict(set)
    for rd, t, fate, st, duel, sep in theories:
        k = norm_id(rd, t)
        last[k] = (rd, t, fate, st, duel, sep)
        ever[k].add(fate)
    R = max(t[0] for t in theories)
    refuted = sorted(k for k, f in ever.items() if "r" in f)
    lost = sorted(k for k, f in ever.items() if "l" in f and "r" not in f)
    nogain = sorted(k for k, f in ever.items() if last[k][2] == "n" and not {"r", "l"} & f)
    survive = sorted(k for k, v in last.items() if v[0] == R and v[2] == "s")
    standing = sorted(k for k in survive if last[k][4] == "beats rival" and (last[k][5] or 0) >= 2)
    other = sorted(set(last) - set(refuted) - set(lost) - set(nogain) - set(survive))
    return {"proposed": len(last), "refuted": refuted, "lost": lost, "nogain": nogain, "survive": survive, "standing": standing,
            "other": {k: f"round {last[k][0]}: {last[k][3]}" for k in other},
            "per_round": {str(r): sum(t[0] == r for t in theories) for r in ROUNDS},
            "new_per_round": {str(r): sum(min(x[0] for x in theories if norm_id(x[0], x[1]) == k) == r for k in last) for r in ROUNDS}}


def round1_control():
    d = ENG / "round-01"
    tg = jsonl(d / "targets.jsonl")
    val = {t["id"]: t["value"] for t in tg}
    err = {p.stem: {x["id"]: abs(x["value"] - val[x["id"]]) for x in jsonl(p)} for p in sorted((d / "predictions").glob("*.jsonl"))}
    stored = load(d / "metrics.json")["theories"]
    sub = [t["id"] for t in tg if t["item"] in ("result-9b6af3", "result-4b0d5f")]
    out = {}
    for name in err:
        if name.startswith("null"):
            continue
        res = {}
        for label, ids in (("all", list(val)), ("weight_difference_items", sub)):
            for k in (1, 2):
                c = sum(err[name][t] < err[f"null-{k}"][t] for t in ids)
                f = sum(err[name][t] > err[f"null-{k}"][t] for t in ids)
                res[f"{label}_vs_reader_{k}"] = [c, f, c - f]
        assert res["all_vs_reader_1"][:2] == [stored[name]["vs_null_1"]["closer"], stored[name]["vs_null_1"]["farther"]], name
        assert res["all_vs_reader_2"][:2] == [stored[name]["vs_null_2"]["closer"], stored[name]["vs_null_2"]["farther"]], name
        res["min_net"] = min(res["all_vs_reader_1"][2], res["all_vs_reader_2"][2])
        out[name] = res
    real = [v["min_net"] for k, v in out.items() if k != "planted"]
    noise = abs(sum(err["null-1"][t] < err["null-2"][t] for t in val) - sum(err["null-1"][t] > err["null-2"][t] for t in val))
    return out, real, noise, len(val), len(sub)


def reversal_controls():
    """Rounds 2-3: a fresh agent's claims for the theory with every effect reversed, scored like the theory."""
    out = []
    m2 = load(ENG / "round-02/metrics_v2.json")["theories"]
    for t, v in m2.items():
        if v["reversal"]:
            def stats(rows):
                w = sum(r["divergent"] and r["inside"] for r in rows)
                lo = sum(r["divergent"] and not r["inside"] for r in rows)
                near = sum(abs(r["value"] - r["measured"]) < abs(sum(r["nulls"]) / 2 - r["measured"]) for r in rows)
                return {"claims": len(rows), "wins": w, "losses": lo, "net": w - lo, "inside": sum(r["inside"] for r in rows), "nearer": near}
            a, b = stats(v["rows"]), stats(v["reversal"]["rows"])
            assert (a["wins"], a["losses"]) == (v["wins"], v["losses"]) and (b["wins"], b["losses"]) == (v["reversal"]["wins"], v["reversal"]["losses"])
            out.append({"round": 2, "theory": t, "theory_score": a, "reversal_score": b})
    m3 = load(ENG / "round-03/metrics_v3.json")["theories"]
    for t, v in m3.items():
        if v["reversal"]:
            out.append({"round": 3, "theory": t, "theory_score": {"claims": v["claims"], "gain_nats": v["total_gain"]},
                        "reversal_score": {"claims": v["reversal"]["claims"], "gain_nats": v["reversal"]["total_gain"]}})
    return out


def duels():
    """Every theory-against-rival duel. state_printed: as the metrics_v5.json of its run holds it. rule_7_1: a test where
    the defender's centre is inside the rival's interval (same_prediction) adds 0; +-2 nats over >= 2 separating tests decide."""
    out = []
    places = [(f"engine/round-{r:02d}", r) for r in (4, 5, 6, 7)] + [("account/run-03", None), ("promoted/run-01", None)]
    for place, rd in places:
        for t, d in load(RES / place / "metrics_v5.json")["theories"].items():
            rows = [r for r in d["rows"] if "gain" in r and r.get("replication") != "differs"]
            for r in rows:
                g = round(clip3(logd(r["measured"], r["theory"]) - logd(r["measured"], r["rival"])), 4)
                if abs(g - r["gain"]) > 2e-3:
                    raise SystemExit(f"{place} duel {t} k={r['k']}: stored {r['gain']}, recomputed {g}")
            apart = [r for r in rows if not r["same_prediction"]]
            tot_all, tot_apart = round(sum(r["gain"] for r in rows), 3), round(sum(r["gain"] for r in apart), 3)
            st = ("not tested" if len(rows) < 2 else "beats rival" if len(apart) >= 2 and tot_apart >= 2
                  else "loses to rival" if len(apart) >= 2 and tot_apart <= -2 else "not separated from rival")
            out.append({"where": place, "round": rd, "theory": t, "tests": len(rows), "separating": len(apart),
                        "gain_all_tests": tot_all, "gain_separating_tests": tot_apart, "gain_stored": d["total_gain"],
                        "state_printed": d["state"], "state_rule_7_1": st,
                        "theory_inside": sum(r["theory"]["low"] <= r["measured"] <= r["theory"]["high"] for r in rows),
                        "rival_inside": sum(r["rival"]["low"] <= r["measured"] <= r["rival"]["high"] for r in rows),
                        "rescore_of": "engine/round-06" if place == "engine/round-07" else None,
                        "per_test_gain": [r["gain"] for r in rows]})
    return out


def selfopen():
    m = load(RES / "experiments/selfopen-01/metrics.json")
    meas = {x["id"]: x for x in load(ENG / "round-05/experiments_measured.json")}
    e = next(x for x in load(ENG / "round-05/experiments.json")["experiments"] if x["id"] in meas)
    g = meas[e["id"]]
    assert g["measured"] == m["main"]["right_of_500"]
    p, o, x = e["proposer_prediction"], e["other_prediction"], g["measured"]
    return {"id": e["id"], "measured": x, "n": g["n"], "measured_interval": g["interval"], "board_item": g["item"],
            "theory": e["proposer"], "theory_forecast": [p["value"], p["low"], p["high"]], "theory_inside": p["low"] <= x <= p["high"],
            "rival": e["other"], "rival_forecast": [o["value"], o["low"], o["high"]], "rival_inside": o["low"] <= x <= o["high"],
            "gain_theory_minus_rival_nats": round(clip3(logd(x, p) - logd(x, o)), 3),
            "gain_unclipped": round(logd(x, p) - logd(x, o), 3),
            "cap_hits": m["main"]["cap_hits"], "mean_generated_tokens": m["main"]["mean_generated_tokens"],
            "control_on_self_opened_problems": m["control"]["on_b_problems"], "model": m["job_config"]["model_repo"],
            "model_revision": m["job_config"]["model_revision"]}


def forecasts():
    readers, out, rows = ["reader-1", "reader-2"], {}, []
    for d in sorted((RES / "forecast").glob("run-*")):
        found = [load(p) for p in d.glob("scores*.json")]
        s = max(found, key=lambda x: x["scored_utc"])
        fc = load(d / "forecasts.json")
        meas = {m["id"]: m for m in s["measured"] if m["value"] is not None}
        by = {n: {f["id"]: f for f in fs} for n, fs in fc.items()}
        for name, p in s["forecasters"].items():
            for r in p["rows"]:
                rr = [by[k][r["id"]] for k in readers]
                a, b = (logd(r["measured"], q) for q in rr)
                g = round(clip3(logd(r["measured"], r) - (max(a, b) + math.log(0.5 * (1 + math.exp(-abs(a - b)))))), 4)
                if abs(g - r["gain"]) > 2e-3:
                    raise SystemExit(f"{d.name} {name} {r['id']}: stored gain {r['gain']}, recomputed {g}")
                dist, rd = abs(r["value"] - r["measured"]), min(abs(q["value"] - r["measured"]) for q in rr)
                rows.append({"run": d.name, "who": name, "id": r["id"], "item": meas[r["id"]]["item"], "measured": r["measured"],
                             "value": r["value"], "low": r["low"], "high": r["high"], "gain": r["gain"],
                             "inside": r["low"] <= r["measured"] <= r["high"], "near": "n" if dist < rd else "t" if dist == rd else "f",
                             "apart": all(not q["low"] <= r["value"] <= q["high"] for q in rr),
                             "kind": "reader" if name in readers else "written_for_the_targets" if name.startswith("f") else "engine_theory"})
        out[d.name] = {"targets": len(s["measured"]), "measured": len(meas), "scored_utc": s["scored_utc"],
                       "snapshot_utc": load(d / "run.json")["utc"], "forecasters": list(fc)}

    def block(rs):
        return {"forecasts": len(rs), "nearer_than_both_readers": sum(r["near"] == "n" for r in rs), "ties": sum(r["near"] == "t" for r in rs),
                "inside_own_interval": sum(r["inside"] for r in rs), "gain_nats": round(sum(r["gain"] for r in rs), 2),
                "centre_outside_both_reader_intervals": sum(r["apart"] for r in rs),
                "of_those_inside_own_interval": sum(r["apart"] and r["inside"] for r in rs)}
    th = [r for r in rows if r["kind"] != "reader"]
    pairs = {(r["run"], r["id"]) for r in rows if r["kind"] == "reader"}
    return {"runs": out, "landed_target_run_pairs": len(pairs),
            "landed_distinct_targets": len({(r["item"], r["measured"]) for r in rows}),
            "target_run_pairs_asked": sum(v["targets"] for v in out.values()),
            "theory_forecasts_on_landed": block(th),
            "engine_theories_only": block([r for r in th if r["kind"] == "engine_theory"]),
            "mechanisms_written_for_the_targets_only": block([r for r in th if r["kind"] == "written_for_the_targets"]),
            "reader_1_inside": [sum(r["inside"] for r in rows if r["who"] == "reader-1"), len(pairs)],
            "reader_2_inside": [sum(r["inside"] for r in rows if r["who"] == "reader-2"), len(pairs)],
            "per_forecaster": {f"{run}/{w}": block([r for r in th if r["run"] == run and r["who"] == w])
                               for run, w in sorted({(r["run"], r["who"]) for r in th})}}


def models():
    src = (T / "lib/round.py").read_text()
    m = re.search(r"^MODELS = (\{.*?\})\n", src, re.S | re.M)
    if not m:
        raise SystemExit("lib/round.py: MODELS table not found")
    out = {"round.py MODELS (alias passed to `claude -p --model`)": ast.literal_eval(m.group(1))}
    for rd in ROUNDS:
        j = load(ENG / f"round-{rd:02d}/run.json")
        out[f"round-{rd:02d}/run.json"] = j.get("subagents") or j.get("jobs") or "no per-stage model recorded in run.json"
    return out


def main():
    rows, filed, theories = build_rows()
    S = REL + "engine/round-<nn>/ via predictions.jsonl"
    head = [r for r in rows if "headline" in r["flags"]]
    cmp_ = [r for r in head if "compared" in r["flags"]]
    by = lambda rs, rd: [r for r in rs if r["round"] == rd]
    facts = {"_about": "Written by studies/theory/paper/build_facts.py from the committed round files. Each entry: value, n, unit, source, note.",
             "_row_fields": ROW_DOC}

    # ---- counts and the four denominators
    n_filed = sum(filed.values())
    facts["counts"] = {
        "predictions_filed": fact(n_filed, None, "predictions", S, "round 1: the 7 hand-matched interval predictions; rounds 2-3: claims "
                                  "on scored held-out targets; rounds 4-7: offline predictions the engine scores (fits, zeros by construction and "
                                  "one failed replication left out), carried duel rows of round 6 included. Per round: " + json.dumps(dict(filed))),
        "predictions_computed": fact(len(head), n_filed, "predictions", S, f"filed minus {n_filed - len(head)} offline predictions with no number "
                                     "(missing packages, rows or fields). Per round: " + json.dumps({rd: len(by(head, rd)) for rd in ROUNDS})),
        "predictions_compared_with_readers": fact(len(cmp_), len(head), "predictions", S, f"computed minus the {sum('carried' in r['flags'] for r in head)} "
                                                  "carried duel rows of round 6, whose comparison is the theory they replaced, not a reader"),
        "predictions_with_reader_intervals": fact(sum("reader_intervals" in r["flags"] for r in head), len(cmp_), "predictions", S,
                                                  "compared minus rounds 1-2, where the readers filed point forecasts only; log gain and reader "
                                                  "coverage exist only here (rounds 3-7)"),
        "distinct_quantities_compared": fact(len({(r["round"], r["qid"]) for r in cmp_}), len(cmp_), "quantities", S,
                                             "rounds 2-3: several theories claim the same target. Distinct per round: " + json.dumps(
                                                 {rd: len({r["qid"] for r in by(cmp_, rd)}) for rd in ROUNDS})),
        "per_round": {str(rd): {"engine_version": VERSION[rd], "theories": sum(t[0] == rd for t in theories), "filed": filed[rd],
                                "computed": len(by(head, rd)), "compared": len(by(cmp_, rd)),
                                "theories_with_a_scored_prediction": len({r["cluster"] for r in by(head, rd)})} for rd in ROUNDS},
        "extra_rows_not_in_headline": dict(Counter(f"{r['series']}:{r['kind']}" for r in rows if "headline" not in r["flags"])),
    }
    f8 = fates(theories)
    facts["theories"] = {
        "proposed": fact(f8["proposed"], None, "theories", REL + "engine/round-<nn>/metrics*.json",
                         "distinct ids over rounds 1-7; includes 3 promoted rivals (r5-m03-rival, r5-m10-rival, r6-account-rival) and 1 account "
                         "(r6-account); the planted control is not counted. New per round: " + json.dumps(f8["new_per_round"])),
        "entries_per_round": fact(f8["per_round"], None, "theories", "", "carried theories count in each round they were scored in"),
        "refuted": fact(len(f8["refuted"]), f8["proposed"], "theories", "", "ever refuted: by a review (rounds 2-3), by its own computed predictions, "
                        "2 held-out strikes or its review (rounds 4-7). " + ", ".join(f8["refuted"])),
        "lost_to_rival": fact(len(f8["lost"]), f8["proposed"], "theories", "", "never refuted, state 'loses to rival' as printed. " + ", ".join(f8["lost"])),
        "no_gain": fact(len(f8["nogain"]), f8["proposed"], "theories", "", "last state 'no gain', never refuted or lost. " + ", ".join(f8["nogain"])),
        "survive_last_round": fact(f8["survive"], None, "", "", "state 'survives' in round 7"),
        "standing": fact(len(f8["standing"]), f8["proposed"], "theories", "", "survives in round 7 and beat its rival with >= 2 separating tests"),
        "other": fact(len(f8["other"]), f8["proposed"], "theories", "", "neither refuted, lost, no gain nor surviving: failed the round 1-3 score, "
                      "untested, or survived a round and was not carried. " + json.dumps(f8["other"])),
    }

    # ---- headline, per round, per version group, sensitivity sets
    facts["headline_all_rounds"] = headline(head, S, "rounds 1-7")
    facts["headline_rounds_3_7"] = headline([r for r in head if r["round"] >= 3], S, "rounds 3-7")
    facts["per_round"] = {str(rd): headline(by(head, rd), S, f"round {rd} (engine {VERSION[rd]})") for rd in ROUNDS}
    sets = {
        "rounds_4_7_offline_tests": [r for r in head if r["round"] >= 4],
        "rounds_3_7_without_r6_account": [r for r in head if r["round"] >= 3 and r["theory"] != "r6-account"],
        "rounds_4_7_without_r6_account": [r for r in head if r["round"] >= 4 and r["theory"] != "r6-account"],
        "all_rounds_without_r6_account": [r for r in head if r["theory"] != "r6-account"],
        "r6_account_alone": [r for r in head if r["theory"] == "r6-account"],
        "round_6_without_account": [r for r in head if r["round"] == 6 and r["theory"] != "r6-account"],
        "leak_exposed_claims_put_back": head + [r for r in rows if "exposed" in r["flags"]],
        "leak_round_2_dropped": [r for r in head if r["round"] != 2],
        "leak_rounds_1_2_dropped_headless_only": [r for r in head if r["round"] >= 3],
        "exposed_claims_alone": [r for r in rows if "exposed" in r["flags"]],
        "rounds_2_3_divergent_claims_only": [r for r in head if r["round"] in (2, 3) and "divergent" in r["flags"]],
        "rounds_4_7_divergent_only": [r for r in head if r["round"] >= 4 and "divergent" in r["flags"]],
        "survivors_heldout_filter_claims_rounds_4_7": [r for r in rows if r["kind"] == "heldout_filter_claim"],
        "account_runs_01_03": [r for r in rows if r["series"].startswith("account/")],
    }
    facts["sensitivity"] = {k: headline(v, S, k) for k, v in sets.items()}
    facts["leak"] = {
        "exposed_item": fact(load(ENG / "round-02/exposed.json")["items"], None, "", REL + "engine/round-02/exposed.json",
                             cut(load(ENG / "round-02/exposed.json")["why"], 420)),
        "exposed_targets": fact(load(ENG / "round-02/run.json")["exposed_targets"], load(ENG / "round-02/run.json")["targets"], "targets",
                                REL + "engine/round-02/run.json", "left out of metrics_v2.json by the engine, so the headline already excludes them"),
        "claims_on_exposed_targets": fact(len(sets["exposed_claims_alone"]), None, "claims", REL + "engine/round-02/claims/*.jsonl",
                                          "kept in predictions.jsonl with flag exposed, kind exposed_claim"),
        "note": "All 151 scored round-2 claims carry flag leak_context: the same agents (both readers, the 5 new generators) had the commit "
                "subject in context, and its numbers (cued base 405, RL 456 of 500 on MATH-500) bear on other targets. Rounds 1-2 ran as "
                "Claude Code subagents; rounds 3-7 as headless jobs in empty directories.",
    }

    # ---- controls
    r1, real, noise, n1, nsub = round1_control()
    facts["round1_planted_control"] = {
        "planted_min_net": fact(r1["planted"]["min_net"], n1, "targets (closer minus farther, worse of the two readers)",
                                REL + "engine/round-01/predictions/*.jsonl, targets.jsonl; equals metrics.json",
                                f"real theories' min net: {sorted(real, reverse=True)}; planted ranks {1 + sum(x > r1['planted']['min_net'] for x in real)} "
                                f"of 7; reader-1 against reader-2 noise {noise}. No predictor beats the noise."),
        "per_predictor": fact(r1, n1, "[closer, farther, net]", REL + "engine/round-01/predictions/*.jsonl",
                              f"weight_difference_items = the {nsub} targets of result-9b6af3 and result-4b0d5f"),
    }
    facts["reversal_controls_rounds_2_3"] = fact(reversal_controls(), None, "", REL + "engine/round-02/metrics_v2.json, round-03/metrics_v3.json (key reversal)",
                                                 "the reversal's claims were written by a fresh agent, the theory's by its author: not a matched control "
                                                 "(README round 02, point 3). No reversal control exists from round 4 on.")
    du = duels()
    distinct = [d for d in du if not d["rescore_of"]]
    facts["duels"] = {
        "n_distinct": fact(len(distinct), None, "duels", REL + "{engine/round-04..06,account/run-03,promoted/run-01}/metrics_v5.json",
                           "round 7's one duel is round 6's r5-m03-rival duel re-scored under rule 7.1, not a new duel"),
        "outcomes_as_printed": fact(dict(Counter(d["state_printed"] for d in distinct)), len(distinct), "duels", "", "the rule of the engine version that ran it"),
        "outcomes_rule_7_1": fact(dict(Counter(d["state_rule_7_1"] for d in distinct)), len(distinct), "duels", "",
                                  "one rule for all: same-prediction tests add 0; +-2 nats over >= 2 separating tests decide"),
        "gain_all_tests_total": fact(round(sum(d["gain_all_tests"] for d in distinct), 2), sum(d["tests"] for d in distinct), "nats over tests", "",
                                     f"theory minus rival; mean per duel {round(sum(d['gain_all_tests'] for d in distinct) / len(distinct), 2)}"),
        "interval_coverage_in_duels": fact([sum(d["theory_inside"] for d in distinct), sum(d["rival_inside"] for d in distinct)],
                                           sum(d["tests"] for d in distinct), "tests inside: defender's interval, rival's interval", "", ""),
        "rows": fact(du, None, "", "", "per duel: tests, separating, nats (all tests, separating tests only), both states"),
    }
    facts["selfopen_01"] = fact(selfopen(), 500, "right answers of 500", REL + "experiments/selfopen-01/metrics.json; engine/round-05/experiments.json, "
                                "experiments_measured.json", "the only GPU experiment run from a theory's entry; gain by the engine's duel rule, computed here "
                                "(no metrics file of the engine holds it: gpu_tests.json of round 7 is empty)")
    facts["forecast_runs"] = fact(forecasts(), None, "", REL + "forecast/run-0<n>/ (newest scores*.json, forecasts.json)",
                                  "nearer here = nearer than BOTH readers of the same run (the forecast page's rule). Measured values were read from board "
                                  "posts by a model job (forecast_score), not by a script. Whether each forecast was committed before its result was "
                                  "posted needs the board and git history and is not recomputed here (the site literal says 10 of 25).")
    facts["versions"] = fact(VERSION_CHANGE, None, "", "studies/theory/README.md", "round -> version: " + json.dumps(VERSION))
    facts["models"] = fact(models(), None, "", "studies/theory/lib/round.py MODELS; results/engine/round-<nn>/run.json (subagents / jobs)",
                           "Only the CLI aliases 'opus' and 'sonnet' are recorded; no run file holds a dated model id. Theories, readers, rivals, defenders, "
                           "test writers and reviews: opus. Targets (reading held-out numbers off board items): sonnet. Round 1: predictors and the "
                           "planted theory sonnet, generators opus. Round 3 reversal text: sonnet.")

    # ---- examples for the text (picked by hand from predictions.jsonl; values read from the rows)
    def ex(rd, theory, qid):
        r = next(x for x in rows if x["round"] == rd and x["theory"] == theory and x["qid"] == qid and "headline" in x["flags"])
        d = ENG / f"round-{rd:02d}/theories/{theory}.json"
        return {k: r[k] for k in ("round", "theory", "qid", "quantity", "unit", "measured", "t_value", "t_low", "t_high", "r1_value", "r1_low",
                                  "r1_high", "r2_value", "r2_low", "r2_high", "gain", "z_t", "source")} | {"statement": cut(load(d)["statement"], 400)}
    facts["examples"] = {
        "confidently_wrong": [ex(4, "r4-m04", "r4-m04:p1"), ex(5, "r5-m07", "r5-m07:p1")],
        "right_where_readers_wrong": [ex(4, "r4-m10", "r4-m10:p2"), ex(5, "r5-m08", "r5-m08:p1")],
    }

    cal = calibration(rows)
    (HERE / "predictions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    (HERE / "facts.json").write_text(json.dumps(facts, indent=1) + "\n")
    (HERE / "calibration.json").write_text(json.dumps(cal, indent=1) + "\n")

    # ---- readout
    h, h3 = facts["headline_all_rounds"], facts["headline_rounds_3_7"]
    print(f"rows {len(rows)} (headline {len(head)}); filed {n_filed}, computed {len(head)}, compared {len(cmp_)}, with reader intervals {h3['gain_total']['n']}")
    print("theories", f8["proposed"], "refuted", len(f8["refuted"]), "lost", len(f8["lost"]), "no gain", len(f8["nogain"]), "survive", f8["survive"],
          "standing", f8["standing"], "other", len(f8["other"]))
    for k in ("nearer", "nearer_than_both_readers", "coverage_theory_all_scored"):
        print("all rounds", k, h[k]["value"], h[k]["note"])
    for k in ("coverage_theory", "coverage_reader_1", "coverage_reader_2", "coverage_gap_theory_minus_readers_mean", "gain_total", "gain_at_clip"):
        print("rounds 3-7", k, h3[k]["value"], h3[k]["note"])
    for rd in ROUNDS:
        p = facts["per_round"][str(rd)]
        print(f"round {rd}: nearer {p['nearer']['value']} n {p['nearer']['n']}"
              + (f"; cover t/r1/r2 {p['coverage_theory']['value']}/{p['coverage_reader_1']['value']}/{p['coverage_reader_2']['value']}; gain {p['gain_total']['value']}"
                 if "gain_total" in p else f"; cover t {p['coverage_theory_all_scored']['value']}"))
    for k, v in facts["sensitivity"].items():
        print(f"  {k}: nearer {v['nearer']['value']} of {v['nearer']['n']}" + (f"; gain {v['gain_total']['value']} n {v['gain_total']['n']}; cover "
              f"{v['coverage_theory']['value']}/{v['coverage_reader_1']['value']}/{v['coverage_reader_2']['value']}" if "gain_total" in v else ""))
    print("duels printed", facts["duels"]["outcomes_as_printed"]["value"], "| rule 7.1", facts["duels"]["outcomes_rule_7_1"]["value"])
    print("selfopen", {k: facts["selfopen_01"]["value"][k] for k in ("measured", "theory_forecast", "rival_forecast", "gain_theory_minus_rival_nats")})
    fr = facts["forecast_runs"]["value"]
    print("forecasts", fr["landed_distinct_targets"], "distinct landed;", fr["theory_forecasts_on_landed"])
    print("wrote", HERE / "predictions.jsonl", HERE / "facts.json", HERE / "calibration.json")


if __name__ == "__main__":
    main()
