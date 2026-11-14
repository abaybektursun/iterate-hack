"""ALWAYSON SPEC2 instrument (studies/reproductions/alwayson/SPEC2_edit.md §2, §5, §6): the column edit, its Frobenius norm and the strength match, the
loop flags of one generated answer, the problem draw and the paired bootstrap. Pure NumPy and Python; the job and the verdict both import it.

Edit. edit_columns(W, cols, u, s): W fp32 [hidden, width], u a unit vector of length hidden, cols distinct column indices;
W[:, cols] <- W[:, cols] - s u (u^T W[:, cols]), computed in fp32 (the job casts the result to bfloat16). The change is the rank-one matrix
-s u p^T on cols with p = u^T W[:, cols], so ||dW||_F = s ||u|| ||p||; frobenius_of_edit evaluates that in float64 from W.
strength_matching(W, cols_target, cols_ref, u, s_ref) = s_ref sqrt(sum_ref p^2 / sum_target p^2): the strength at which the edit on
cols_target has the Frobenius norm of the s_ref edit on cols_ref (SPEC2 §2, A3 and A4).

Flags (§2 "Per answer"). ids are the generated token ids with the end-of-sequence token removed, so n_new = len(ids) and the cap was hit
exactly when n_new >= cap (no EOS within the cap). text is their decoding. The thinking block ends at the first "</think>" of the text
(the prompt ends with "<think>\n", so the generation opens inside it); text_after_think is what follows it, "" when it never closes.
  rep   rep_flag(ids): there are positions p, p+d, p+2d with d >= 10 and p+2d+10 <= p+100 (so 10 <= d <= 45) and
        ids[p:p+10] == ids[p+d:p+d+10] == ids[p+2d:p+2d+10] (a 10-gram three times at equal intervals within 100 tokens, Hiraoka and
        Inui §2.2, on the generated ids). The returned 10-gram is the one at the smallest p, ties to the smallest d.
  boxed "\\boxed{" occurs in text_after_think.
  cut   cut_flag(n_new, cap, text_after_think): the cap was hit and no "\\boxed{" after the thinking block.
  loop  rep or cut.
  exact (exploratory, §6) the content of the last balanced \\boxed{...} after the thinking block equals the answer after removing every
        whitespace character and every "\\left" and "\\right".

Problems. draw_problems(rows, seed, n): np.random.default_rng(seed).permutation(len(rows)), the first n; problem index = position in that
order. row_sha256: sha256 of json.dumps(row, sort_keys=True, ensure_ascii=False) in UTF-8.

Bootstrap. draw_matrix(n, n_boot, seed): rng = default_rng(seed); one row of rng.integers(0, n, n) per draw; every statistic of a run is
computed on the same rows, so arms are resampled jointly over problems.
Fail-loud: no try/except, no fallback.
"""
from __future__ import annotations

import hashlib
import json
import re

import numpy as np

REP = {"n": 10, "times": 3, "window": 100}
BOXED = "\\boxed{"
THINK_END = "</think>"


# ------------------------------------------------------------------------------------------ (a) the edit
def _check(W: np.ndarray, cols, u: np.ndarray) -> np.ndarray:
    assert isinstance(W, np.ndarray) and W.dtype == np.float32 and W.ndim == 2, (type(W), getattr(W, "dtype", None))
    assert isinstance(u, np.ndarray) and u.dtype == np.float32 and u.shape == (W.shape[0],), (getattr(u, "dtype", None), getattr(u, "shape", None))
    assert abs(float(np.linalg.norm(u.astype(np.float64))) - 1.0) < 1e-5, f"u is not a unit vector: norm {np.linalg.norm(u.astype(np.float64))}"
    c = np.asarray(cols, dtype=np.int64)
    assert c.ndim == 1 and c.size > 0 and len(set(c.tolist())) == c.size and c.min() >= 0 and c.max() < W.shape[1], "columns not distinct or out of range"
    return c


def edit_columns(W: np.ndarray, cols, u: np.ndarray, strength: float) -> np.ndarray:
    c = _check(W, cols, u)
    E = W.copy()
    S = W[:, c]
    E[:, c] = S - np.float32(strength) * np.outer(u, u @ S)
    assert E.dtype == np.float32
    return E


def proj(W: np.ndarray, u: np.ndarray) -> np.ndarray:
    """u . W[:, n] for every column, float64."""
    return u.astype(np.float64) @ W.astype(np.float64)


def frobenius_of_edit(W: np.ndarray, cols, u: np.ndarray, strength: float) -> float:
    c = _check(W, cols, u)
    return float(abs(strength) * np.linalg.norm(u.astype(np.float64)) * np.sqrt((proj(W, u)[c] ** 2).sum()))


def frobenius_from_proj(p: np.ndarray, cols, strength: float) -> float:
    """The same norm from a banked u . W (u unit): strength sqrt(sum_cols p^2)."""
    return float(abs(strength) * np.sqrt((np.asarray(p, np.float64)[np.asarray(cols, np.int64)] ** 2).sum()))


def strength_from_proj(p: np.ndarray, cols_target, cols_ref, strength_ref: float) -> float:
    p = np.asarray(p, np.float64)
    t, r = (p[np.asarray(cols_target, np.int64)] ** 2).sum(), (p[np.asarray(cols_ref, np.int64)] ** 2).sum()
    assert t > 0, "the target columns carry no component along u; no strength matches"
    return float(strength_ref * np.sqrt(r / t))


def strength_matching(W: np.ndarray, cols_target, cols_ref, u: np.ndarray, strength_ref: float) -> float:
    _check(W, cols_target, u)
    _check(W, cols_ref, u)
    return strength_from_proj(proj(W, u), cols_target, cols_ref, strength_ref)


# ------------------------------------------------------------------------------------------ (b) the flags
def rep_flag(ids, n: int = REP["n"], times: int = REP["times"], window: int = REP["window"]):
    """(True, the 10-gram) when the rule of the module docstring holds, else (False, None)."""
    assert times >= 2 and window >= times * n, (n, times, window)
    x = np.asarray(ids, dtype=np.int64)
    L = x.size
    best = None
    for d in range(n, (window - n) // (times - 1) + 1):
        P = L - (times - 1) * d - n + 1
        if P <= 0:
            break
        eq = (x[d:] == x[:-d]).astype(np.int64)
        c = np.concatenate([[0], np.cumsum(eq)])
        m = (c[n:] - c[:-n]) == n
        ok = np.ones(P, dtype=bool)
        for k in range(times - 1):
            ok &= m[k * d:k * d + P]
        hit = np.flatnonzero(ok)
        if hit.size and (best is None or hit[0] < best[0]):
            best = (int(hit[0]), d)
    if best is None:
        return False, None
    return True, [int(t) for t in x[best[0]:best[0] + n]]


def text_after_think(text: str) -> str:
    return text.split(THINK_END, 1)[1] if THINK_END in text else ""


def cut_flag(n_new: int, cap: int, after_think: str) -> bool:
    return bool(n_new >= cap and BOXED not in after_think)


def boxed_last(text: str):
    """The content of the last balanced \\boxed{...} in text, or None."""
    last, i = None, text.find(BOXED)
    while i >= 0:
        depth, j = 1, i + len(BOXED)
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        if depth == 0:
            last = text[i + len(BOXED):j - 1]
        i = text.find(BOXED, i + 1)
    return last


def normalise(s: str) -> str:
    return re.sub(r"\s+", "", s.replace("\\left", "").replace("\\right", ""))


def answer_flags(ids, text: str, cap: int, answer: str, rep: dict = REP) -> dict:
    after = text_after_think(text)
    r, gram = rep_flag(ids, rep["n"], rep["times"], rep["window"])
    n_new = len(ids)
    cut = cut_flag(n_new, cap, after)
    b = boxed_last(after)
    return {"n_new": n_new, "cap_hit": bool(n_new >= cap), "think_closed": THINK_END in text, "boxed": BOXED in after, "boxed_content": b,
            "rep": bool(r), "rep_ngram": gram, "cut": cut, "loop": bool(r or cut), "exact": bool(b is not None and normalise(b) == normalise(answer))}


FLAG_KEYS = ("n_new", "cap_hit", "think_closed", "boxed", "boxed_content", "rep", "rep_ngram", "cut", "loop", "exact")


def planted_sequence(n: int = REP["n"], times: int = REP["times"], first: int = 100) -> list:
    """The detector's planted input: a 10-gram repeated three times at stride 10."""
    return list(range(first, first + n)) * times


def shuffled_copy(seq: list, seed: int = 0) -> list:
    return [int(t) for t in np.random.default_rng(seed).permutation(np.asarray(seq))]


# ------------------------------------------------------------------------------------------ (c) problems and the bootstrap
def row_sha256(row: dict) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def draw_problems(rows: list, seed: int, n: int) -> list:
    perm = np.random.default_rng(seed).permutation(len(rows))
    return [{"problem_index": k, "row": int(r), **{f: rows[r][f] for f in ("problem", "answer", "unique_id")}, "row_sha256": row_sha256(rows[r])}
            for k, r in enumerate(perm[:n])]


def completeness(recs: list, n: int, batch: int, seed_base: int) -> dict:
    """One arm's answers: n of them, problem indices 0..n-1 in order, no empty text, each seed = seed_base + its batch's first index."""
    idx = [r["problem_index"] for r in recs]
    v = {"n": len(recs), "distinct": len(set(idx)), "in_order": idx == list(range(len(recs))), "empty": sum(r["text"] == "" for r in recs),
         "seeded": all(r["seed"] == seed_base + (r["problem_index"] // batch) * batch for r in recs)}
    v["pass"] = bool(v["n"] == n and v["distinct"] == n and v["in_order"] and v["empty"] == 0 and v["seeded"])
    return v


def draw_matrix(n: int, n_boot: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.stack([rng.integers(0, n, n) for _ in range(n_boot)])


def interval(draws: np.ndarray, q=(2.5, 97.5)) -> dict:
    ok = draws[np.isfinite(draws)]
    assert ok.size >= 2, "fewer than two finite bootstrap draws"
    lo, hi = np.percentile(ok, q)
    return {"lo": float(lo), "hi": float(hi), "n_boot": int(draws.size), "n_nonfinite": int(draws.size - ok.size)}


def side(iv: dict, line: float) -> str:
    return "above" if iv["lo"] > line else "below" if iv["hi"] < line else "contains"


# ------------------------------------------------------------------------------------------ (d) selfcheck
def selfcheck() -> dict:
    rng = np.random.default_rng(0)
    H, Wd = 64, 96
    W = rng.standard_normal((H, Wd)).astype(np.float32)
    u = rng.standard_normal(H).astype(np.float32)
    u = (u / np.linalg.norm(u.astype(np.float64))).astype(np.float32)
    cols = [3, 7, 11, 50, 90]
    E = edit_columns(W, cols, u, 6.0)
    other = sorted(set(range(Wd)) - set(cols))
    assert np.array_equal(E[:, other], W[:, other]), "the edit changed columns outside cols"
    assert np.allclose(u @ E[:, cols], -5.0 * (u @ W[:, cols]), atol=1e-4), "u^T W' != (1 - s) u^T W on the edited columns"
    assert np.allclose(u @ edit_columns(W, cols, u, 1.0)[:, cols], 0.0, atol=1e-5), "strength 1 does not project u out"
    fd = float(np.linalg.norm((E.astype(np.float64) - W.astype(np.float64))))
    fe = frobenius_of_edit(W, cols, u, 6.0)
    assert abs(fd - fe) < 1e-4 * fe, (fd, fe)
    assert abs(frobenius_from_proj(proj(W, u), cols, 6.0) - fe) < 1e-6 * fe
    tgt = [0, 1, 2, 4, 5]
    s = strength_matching(W, tgt, cols, u, 6.0)
    assert abs(frobenius_of_edit(W, tgt, u, s) - fe) < 1e-9 * fe, "strength_matching does not match the norm"
    assert abs(strength_matching(W, cols, cols, u, 6.0) - 6.0) < 1e-12
    # rep: planted fires; shuffled does not; the window and stride edges
    pl = planted_sequence()
    assert rep_flag(pl) == (True, list(range(100, 110))) and not rep_flag(shuffled_copy(pl))[0]
    noise = [int(t) for t in rng.permutation(5000)[:400] + 1000]
    g = list(range(10))
    for d, fires in ((10, True), (45, True), (46, False)):
        seq = noise[:50] + g + noise[50:50 + d - 10] + g + noise[100:100 + d - 10] + g + noise[200:260]
        assert rep_flag(seq)[0] is fires, (d, fires)
    assert not rep_flag(noise)[0] and not rep_flag(g + g)[0] and not rep_flag([])[0]
    assert rep_flag([7] * 30) == (True, [7] * 10) and not rep_flag([7] * 29)[0]
    seq = noise[:5] + (g + [55, 56]) * 4
    assert rep_flag(seq) == (True, g), rep_flag(seq)
    # boxed, cut, exact
    assert boxed_last("a \\boxed{1} b \\boxed{\\frac{1}{2}} c") == "\\frac{1}{2}" and boxed_last("\\boxed{3} \\boxed{4") == "3" and boxed_last("x") is None
    assert text_after_think("think</think> ans") == " ans" and text_after_think("never closes \\boxed{1}") == ""
    assert cut_flag(32, 32, "") and not cut_flag(31, 32, "") and not cut_flag(32, 32, "so \\boxed{2}")
    f = answer_flags([1, 2, 3], "t</think>So \\boxed{\\left( 3, \\frac{\\pi}{2} \\right)}", 32, "\\left( 3, \\frac{\\pi}{2} \\right)")
    assert f["exact"] and f["boxed"] and not f["cut"] and not f["loop"] and f["n_new"] == 3, f
    f = answer_flags(pl + [1] * 2, "\\boxed{1} still thinking", 32, "1")
    assert f["rep"] and f["cut"] and f["loop"] and not f["boxed"] and not f["exact"] and f["cap_hit"], f
    # problems and the bootstrap
    rows = [{"problem": f"p{i}", "answer": str(i), "unique_id": f"u{i}", "level": 1} for i in range(500)]
    d1, d2 = draw_problems(rows, 0, 200), draw_problems(rows, 0, 200)
    assert d1 == d2 and len({x["unique_id"] for x in d1}) == 200 and [x["row"] for x in d1] == np.random.default_rng(0).permutation(500)[:200].tolist()
    recs = [{"problem_index": i, "text": "x", "seed": 1000 + (i // 4) * 4} for i in range(10)]
    assert completeness(recs, 10, 4, 1000)["pass"] and not completeness(recs[:-1], 10, 4, 1000)["pass"]
    assert not completeness(recs[:3] + [{**recs[3], "text": ""}] + recs[4:], 10, 4, 1000)["pass"]
    assert not completeness(recs[:3] + [{**recs[3], "seed": 1003}] + recs[4:], 10, 4, 1000)["pass"]
    M = draw_matrix(200, 50, 0)
    assert M.shape == (50, 200) and np.array_equal(M, draw_matrix(200, 50, 0)) and M.min() >= 0 and M.max() < 200
    assert side({"lo": 0.6, "hi": 0.9}, 0.5) == "above" and side({"lo": 0.1, "hi": 0.4}, 0.5) == "below" and side({"lo": 0.4, "hi": 0.6}, 0.5) == "contains"
    return {"frobenius_direct": fd, "frobenius_formula": fe, "matched_strength": s}


if __name__ == "__main__":
    print(json.dumps(selfcheck()))
    print("ALWAYSON_EDIT_SELFCHECK_OK")
