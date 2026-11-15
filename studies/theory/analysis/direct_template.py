"""Direct test template-01 of round-09/training-m01 (studies/theory/specs/SPEC_direct_template.md): does Think-SFT's own
<think> template drift less than the raw template with the cue? Drift signs from studies/rlneurons/analysis/drift.py on the
first 16,384 generated tokens of each hard328 row; null = drift-share scatter between the 4 stored raw-cue samples.

    uv run --no-project --with numpy --with tokenizers --with math-verify==0.9.0 python -m studies.theory.analysis.direct_template

Reads runs/<job>/answers.jsonl (raw texts, not in git; see the spec for the jobs). Writes studies/theory/results/direct/template-01/.
"""
import json
import pathlib
import re
import subprocess

import numpy as np

from studies.rlneurons.analysis import drift as D
from studies.rlneurons.lib import n13_score

CUT = 16384
NATIVE = "runs/native_sft_hard328_joined/answers.jsonl"
CUE32 = "runs/abaybektursun-1115-005756-309b/answers.jsonl"
TV = ["runs/abaybektursun-1115-000503-1e5f/answers.jsonl", "runs/abaybektursun-1115-000525-ea4e/answers.jsonl",
      "runs/abaybektursun-1115-014823-ef56/answers.jsonl", "runs/abaybektursun-1115-014833-1daa/answers.jsonl"]
OUT = pathlib.Path("studies/theory/results/direct/template-01")


def load(path):
    rows = [json.loads(line) for line in open(path)]
    assert all(r["attempt"] == 0 for r in rows), path
    out = {r["problem_index"]: r for r in rows}
    assert len(out) == 328, (path, len(out))
    return out


def flags(r):
    """Drift signs on the first CUT generated tokens (cue rows: the text starts with the cue tokens, which are not generated)."""
    ids, offsets = D.encode(r["text"])
    k = min(len(ids), CUT + max(0, len(ids) - r["n_new"]))
    cut = r["text"][:offsets[k - 1][1]] if k else ""
    full_switch = bool(D.episodes(r["text"]))
    switch = bool(D.episodes(cut))
    repeat = bool(D.repeated(ids[:k]).any())
    return {"problem_index": r["problem_index"], "n_new": r["n_new"], "n_tok": len(ids), "cut_tok": k, "score_v3": r["score_v3"],
            "switch": switch, "repeat": repeat, "drifted": switch or repeat, "switch_full_text": full_switch}


def answer_line(text):
    """The next non-empty line after the last line that reads just 'Answer:' (markdown stripped), or None."""
    lines = text.split("\n")
    marks = [i for i, l in enumerate(lines) if re.fullmatch(r"answer:", re.sub(r"[\s*#_]", "", l).lower())]
    if not marks:
        return None
    return next((l.strip() for l in lines[marks[-1] + 1:] if l.strip()), None)


def misplaced(rows):
    """Finished rows graded wrong whose line after a bare 'Answer:' is math-verify-equal to the gold answer."""
    hits = []
    for r in rows.values():
        if r["score_v3"] or r["cap_hit"]:
            continue
        a = answer_line(r["text"])
        if a is not None and n13_score.grade(r["gold"], a.strip("$ "))["score"]:
            hits.append({"problem_index": r["problem_index"], "line": a[:200], "gold": r["gold"], "extracted_v3": r["extracted_v3"]})
    return hits


def share(fl, key="drifted"):
    return 100 * float(np.mean([f[key] for f in fl]))


def boot(a, b, rng_seed=0, n=10000):
    """Paired bootstrap over problems of 100*(mean a - mean b); 95 % and 90 % percentile intervals."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    idx = np.random.default_rng(rng_seed).integers(0, len(a), (n, len(a)))
    d = 100 * (a[idx].mean(1) - b[idx].mean(1))
    return {"point": float(100 * (a.mean() - b.mean())), "ci95": [float(x) for x in np.percentile(d, [2.5, 97.5])],
            "ci90": [float(x) for x in np.percentile(d, [5, 95])]}


def main():
    nat, c32 = load(NATIVE), load(CUE32)
    tv = {}
    for p in TV:
        rows = load(p)
        s = {(r["seed"] - 3000000 - i) // 10000 for i, r in rows.items()}
        assert len(s) == 1, s
        tv[s.pop()] = rows
    assert sorted(tv) == [0, 1, 2, 3] and nat.keys() == c32.keys() == tv[0].keys()
    right = lambda rows, cap: sum(r["score_v3"] for r in rows.values() if r["n_new"] <= cap)
    counts = {"native": [right(nat, 32768), right(nat, CUT)], "cue32": [right(c32, 32768), right(c32, CUT)]}
    assert counts == {"native": [232, 204], "cue32": [230, 207]}, counts

    P = sorted(nat)
    fn = {i: flags(nat[i]) for i in P}
    fc = {i: flags(c32[i]) for i in P}
    ft = {k: {i: flags(tv[k][i]) for i in P} for k in tv}
    assert all(f["cut_tok"] == f["n_tok"] for k in ft for f in ft[k].values()), "thinkvote rows are capped at 16,384: no cut expected"

    # instrument check: describe-01's switch counts from the full texts
    tv_switch = sum(f["switch_full_text"] for k in ft for f in ft[k].values())
    c32_switch_full = sum(f["switch_full_text"] for f in fc.values())
    assert (tv_switch, c32_switch_full) == (156, 83), (tv_switch, c32_switch_full)

    A = [fn[i]["drifted"] for i in P]
    B = [fc[i]["drifted"] for i in P]
    d = boot(A, B)
    tv_share = {k: share(list(ft[k].values())) for k in ft}
    pairs = {f"{a}-{b}": tv_share[a] - tv_share[b] for a in tv for b in tv if a < b}
    s_max = max(abs(v) for v in pairs.values())
    d_k = {k: boot(A, [ft[k][i]["drifted"] for i in P]) for k in ft}
    refuted = d["point"] <= -2.0 and d["ci95"][1] < 0 and abs(d["point"]) > s_max

    signs = {}
    for key in ("switch", "repeat", "drifted"):
        signs[key] = {"native_rows": sum(fn[i][key] for i in P), "cue32_rows": sum(fc[i][key] for i in P),
                      "thinkvote_rows": {k: sum(ft[k][i][key] for i in P) for k in ft},
                      "native_minus_cue32_pts": boot([fn[i][key] for i in P], [fc[i][key] for i in P])}
    fin = lambda rows: float(np.median([r["n_new"] for r in rows.values() if not r["cap_hit"]]))
    mis_c, mis_n = misplaced(c32), misplaced(nat)
    readout = {
        "spec": "studies/theory/specs/SPEC_direct_template.md", "mechanism": "round-09/training-m01", "n_problems": len(P),
        "right_v3_at_32768_and_16384": counts,
        "deciding": {"D_native_minus_cue32_drifted_pts": d, "native_drifted_rows": sum(A), "cue32_drifted_rows": sum(B),
                     "S_max_pts": s_max, "discordant_rows": {"native_only": sum(a and not b for a, b in zip(A, B)),
                     "cue32_only": sum(b and not a for a, b in zip(A, B)), "both": sum(a and b for a, b in zip(A, B))}, "thinkvote_drifted_share_pts": tv_share, "thinkvote_pairwise_pts": pairs},
        "D_native_minus_thinkvote_sample_k_pts": d_k,
        "by_sign": signs,
        "rule": "refuted if D <= -2.0 and D's 95 % upper bound < 0 and |D| > S_max; otherwise holds",
        "verdict": "refuted" if refuted else "holds",
        "instrument": {"describe01_thinkvote_switch_full_text": tv_switch, "describe01_cue32_switch_full_text": c32_switch_full,
                       "switch_only_after_cut_native": sum(fn[i]["switch_full_text"] and not fn[i]["switch"] for i in P),
                       "switch_only_after_cut_cue32": sum(fc[i]["switch_full_text"] and not fc[i]["switch"] for i in P),
                       "retokenized_minus_n_new_median": {"native": float(np.median([fn[i]["n_tok"] - fn[i]["n_new"] for i in P])),
                                                          "cue32": float(np.median([fc[i]["n_tok"] - fc[i]["n_new"] for i in P]))}},
        "secondary": {"cap_hits_at_16384": {"native": sum(r["n_new"] > CUT for r in nat.values()), "cue32": sum(r["n_new"] > CUT for r in c32.values())},
                      "cap_hits_at_32768": {"native": sum(r["cap_hit"] for r in nat.values()), "cue32": sum(r["cap_hit"] for r in c32.values())},
                      "median_n_new_finished": {"native": fin(nat), "cue32": fin(c32)},
                      "finished_wrong_with_right_answer_after_bare_Answer_line": {"cue32": len(mis_c), "native": len(mis_n),
                                                                                  "cue32_rows": mis_c, "native_rows": mis_n}},
    }
    OUT.mkdir(parents=True, exist_ok=False)
    (OUT / "readout.json").write_text(json.dumps(readout, indent=1) + "\n")
    with open(OUT / "rows.jsonl", "w") as f:
        for cell, fl in [("native", fn), ("cue32", fc)] + [(f"thinkvote_s{k}", ft[k]) for k in ft]:
            for i in P:
                f.write(json.dumps({"cell": cell, **fl[i]}, separators=(",", ":")) + "\n")

    def excerpt(r, f):
        ids, offsets = D.encode(r["text"])
        cut = r["text"][:offsets[f["cut_tok"] - 1][1]]
        eps = D.episodes(cut)
        at = eps[0][0] if eps else None
        rep = D.repeated(ids[:f["cut_tok"]])
        rt = int(np.argmax(rep)) if rep.any() else None
        return {**f, "extracted_v3": r["extracted_v3"], "gold": r["gold"], "text_start": r["text"][:300],
                "first_switch_excerpt": None if at is None else cut[max(0, at - 200): at + 300],
                "first_repeat_excerpt": None if rt is None else r["text"][offsets[rt][0]: offsets[min(rt + 50, len(ids)) - 1][1]],
                "text_end": r["text"][-300:]}
    i_drift = next(i for i in P if fn[i]["drifted"] and fn[i]["switch"])
    i_clean = next(i for i in P if not fn[i]["drifted"] and fc[i]["drifted"])
    (OUT / "examples.json").write_text(json.dumps({
        "supports_claim_own_template_still_drifts": excerpt(nat[i_drift], fn[i_drift]),
        "against_claim_own_template_clean_where_cue32_drifted": {"native": excerpt(nat[i_clean], fn[i_clean]), "cue32": excerpt(c32[i_clean], fc[i_clean])}}, indent=1) + "\n")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (OUT / "run.json").write_text(json.dumps({
        "spec": "studies/theory/specs/SPEC_direct_template.md", "commit": commit, "board": "work-996b09",
        "command": "uv run --no-project --with numpy --with tokenizers --with math-verify==0.9.0 python -m studies.theory.analysis.direct_template",
        "inputs": {"native": "runs/native_sft_hard328_joined/answers.jsonl (jobs ih-1115-163313-7486 + ih-1115-163401-a4ba)",
                   "cue32": "runs/abaybektursun-1115-005756-309b/answers.jsonl", "thinkvote": TV},
        "tokenizer": list(D.TOKENIZER), "bootstrap": "10,000 resamples of the 328 problems, numpy default_rng(0), paired", "gpu": "none"}, indent=1) + "\n")
    print(json.dumps(readout["deciding"], indent=1), readout["verdict"])


if __name__ == "__main__":
    main()
