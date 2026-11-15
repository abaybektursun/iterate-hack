"""Drift (specs/SPEC_drift.md): label-free signs in the text of a sample, per token position: a switch to a non-Latin script,
repeated 50-token windows, the runner's loop rule A, restart phrases, "wait". This file computes the signs; drift_read.py
reads them.

    uv run --no-project --with numpy --with tokenizers python -m studies.rlneurons.analysis.drift --runs <runs root> --out <runs root>/drift_features

  --runs  the folder that holds the job folders with answers.jsonl (CELLS below; not in git).
  --out   a new folder: <cell>.jsonl, one line per attempt-0 sample (not committed; drift_read.py reads it).

Token positions are positions in the text re-tokenized with the run's tokenizer (allenai/Olmo-3.1-7B-RL-Zero-Math @ 364820b,
tokenizer.json from the local Hugging Face cache, no weights). A sign at token t is computed from the first t tokens only.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing
import pathlib
import re
import unicodedata

import numpy as np

from studies.rlneurons.lib import rln4_lib as R

TOKENIZER = ("allenai/Olmo-3.1-7B-RL-Zero-Math", "364820b002fc8e81d11a81c7fc9dd6b49c83cd05")
CELLS = {                                             # cell: answers.jsonl under --runs
    "hard328_sft": "thinkvote_hard328_sft1_cue_s4", "hard328_rl": "abaybektursun-1114-200505-5ff2", "hard328_base": "abaybektursun-1114-200457-e8e6",
    "fresh_sft": "fresh_sft1_cue_s4", "fresh_rl": "fresh_rl_plain_s4", "fresh_base": "fresh_base_cue_s4",
    "math500_sft": "thinkvote_math500_sft1_cue_s4", "cap32_sft": "cap32vote_handoff/abaybektursun-1115-005756-309b",
}
GRID = 1000                                           # signs are stored at every multiple of GRID tokens
# A letter counts as non-Latin when its Unicode name starts with one of these scripts. Greek is left out on purpose (mathematics),
# and so are the letterlike and mathematical-alphanumeric blocks, whose names start with other words (DOUBLE-STRUCK, MATHEMATICAL).
CJK = ("CJK", "HIRAGANA", "KATAKANA", "HANGUL", "BOPOMOFO")
SCRIPTS = CJK + ("CYRILLIC", "ARABIC", "HEBREW", "THAI", "DEVANAGARI", "BENGALI", "TAMIL", "TELUGU", "GEORGIAN", "ARMENIAN", "ETHIOPIC",
                 "KHMER", "LAO", "TIBETAN", "MYANMAR", "GUJARATI", "GURMUKHI", "KANNADA", "MALAYALAM", "SINHALA")
MIN_LETTERS, GAP = 5, 200                             # an episode: at least 5 non-Latin letters, neighbours at most 200 characters apart
BACK_CHARS, BACK_WORDS = 1000, 10                     # switched back: 10 English function words in the 1,000 characters after an episode
ENGLISH = re.compile(r"\b(the|is|so|we|of|and|that|this|to|in|but|then|let|if)\b", re.I)
WAIT = re.compile(r"\bwait\b", re.I)
RESTART = re.compile(r"\b(let me start over|start over|start again|start from scratch|let me try again|let's try again|try a different approach|"
                     r"try another approach|another approach|different approach|let me re-?think|let me reconsider|let me re-?examine|"
                     r"let me re-?read|go back to the (beginning|start|problem)|i'm stuck|i am stuck|this is getting (too )?(complicated|messy))\b", re.I)
WINDOW = 50


def script(c: str):
    """The script of a non-Latin letter, or None for everything else (Latin with diacritics, Greek, digits, symbols, punctuation)."""
    if c < "Ͱ" or not c.isalpha():
        return None
    w = unicodedata.name(c, "").split(" ")[0]
    return w if w in SCRIPTS else None


def episodes(text: str) -> list:
    """Episodes of non-Latin text: [first char, char of the 5th letter (when a reader of the prefix can first see it), last char,
    letters, {script: letters}]. Fewer than MIN_LETTERS letters within GAP characters of each other are no episode."""
    hits = [(i, s) for i, c in enumerate(text) if (s := script(c))]
    out, cur = [], []
    for h in hits + [(None, None)]:
        if cur and (h[0] is None or h[0] - cur[-1][0] > GAP):
            if len(cur) >= MIN_LETTERS:
                by = {}
                for _, s in cur:
                    by[s] = by.get(s, 0) + 1
                out.append([cur[0][0], cur[MIN_LETTERS - 1][0], cur[-1][0], len(cur), by])
            cur = []
        if h[0] is not None:
            cur.append(h)
    return out


def back(text: str, ep: list):
    """True when English resumes after the episode, False when it does not, None when fewer than BACK_CHARS characters follow."""
    after = text[ep[2] + 1: ep[2] + 1 + BACK_CHARS]
    return None if len(after) < BACK_CHARS else len(ENGLISH.findall(after)) >= BACK_WORDS


def repeated(ids: list) -> np.ndarray:
    """rep[i] = 1 when the window of WINDOW tokens that starts at token i equals a window that starts earlier."""
    if len(ids) < WINDOW + 1:
        return np.zeros(0, int)
    w = np.lib.stride_tricks.sliding_window_view(np.asarray(ids, np.int32), WINDOW)
    _, first, inv = np.unique(np.ascontiguousarray(w).view(np.dtype((np.void, w.dtype.itemsize * WINDOW))).ravel(), return_index=True, return_inverse=True)
    return (first[inv.ravel()] < np.arange(len(w))).astype(int)


def loop_detect_char(text: str):
    """The character at which rule A (rln4_lib.onset_lines) first verifies a loop on a prefix: the end of its first verified window."""
    c = next((c for c, _ in R._lines(text) if len(text) - c >= R.W and R.zratio(text[c:c + R.W]) < R.THR), None)
    assert (c is None) == (R.onset_lines(text) is None)
    return None if c is None else c + R.W


def signs(text: str, ids: list, offsets: list) -> dict:
    """Every sign of one text. Token of a character = tokens that end at or before it (rln4_lib.tokens_before)."""
    ends = np.array([b for _, b in offsets])
    tok = lambda char: int(np.searchsorted(ends, char, side="right"))
    n = len(ids)
    marks = [k for k in range(GRID, n + 1, GRID)]
    char_at = lambda t: offsets[t - 1][1]                                    # the prefix of t tokens is text[:char_at(t)]
    eps = episodes(text)
    rep = repeated(ids)
    cum = np.concatenate([[0], np.cumsum(rep)])
    wait = np.array([tok(m.end()) for m in WAIT.finditer(text)])
    rest = np.array([tok(m.end()) for m in RESTART.finditer(text)])
    ld = loop_detect_char(text)
    letters = [script(c) is not None for c in text[eps[0][0]:]] if eps else []
    return {
        "n_tok": n, "chinese_chars": sum("一" <= c <= "鿿" for c in text),
        "episodes": [{"start_tok": tok(e[0]), "detect_tok": tok(e[1]) + 1, "end_tok": tok(e[2]) + 1, "letters": e[3], "scripts": e[4], "back": back(text, e),
                      "start_char": e[0], "end_char": e[2]} for e in eps],
        "nonlatin_share_after_first": (sum(letters) / max(1, sum(c.isalpha() for c in text[eps[0][0]:]))) if eps else None,
        "loop_tok": None if ld is None else tok(ld) + 1,
        # at each mark t (tokens): share of the windows inside the first t tokens that repeat an earlier one; counts so far
        "rep50": [float(cum[max(0, t - WINDOW + 1)] / max(1, t - WINDOW + 1)) for t in marks],
        "wait": [int((wait <= t).sum()) for t in marks], "restart": [int((rest <= t).sum()) for t in marks],
        "zratio": [R.zratio(text[:char_at(t)]) for t in marks],
        "rep50_end": float(rep.mean()) if len(rep) else 0.0, "wait_end": len(wait), "restart_end": len(rest),
    }


_TOK = None


def tokenizer():
    global _TOK
    if _TOK is None:
        from tokenizers import Tokenizer
        p = pathlib.Path.home() / ".cache/huggingface/hub" / ("models--" + TOKENIZER[0].replace("/", "--")) / "snapshots" / TOKENIZER[1] / "tokenizer.json"
        _TOK = Tokenizer.from_file(str(p))
    return _TOK


def encode(text: str) -> tuple:
    e = tokenizer().encode(text, add_special_tokens=False)
    return e.ids, e.offsets


KEEP = ("problem_index", "sample", "attempt", "unique_id", "n_new", "cap_hit", "loop_A", "extracted_v3", "score_v3", "max_tokens")


def one(line: str):
    r = json.loads(line)
    if r["attempt"] != 0:
        return None
    ids, offsets = encode(r["text"])
    return {**{k: r[k] for k in KEEP}, **signs(r["text"], ids, offsets)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True)
    with multiprocessing.Pool() as pool:
        for cell, d in CELLS.items():
            lines = (pathlib.Path(a.runs) / d / "answers.jsonl").read_text().splitlines()
            rows = sorted((r for r in pool.imap(one, lines, chunksize=8) if r), key=lambda r: (r["problem_index"], r["sample"]))
            (out / f"{cell}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
            caps = [r for r in rows if r["cap_hit"]]
            off = np.array([r["n_tok"] - r["n_new"] for r in rows])
            print(cell, "samples", len(rows), "cap hits", len(caps), "with > 20 Chinese characters", sum(r["chinese_chars"] > 20 for r in caps),
                  "with an episode", sum(bool(r["episodes"]) for r in caps), "| re-tokenized minus n_new: median", int(np.median(off)),
                  "max abs", int(np.abs(off).max()), flush=True)


if __name__ == "__main__":
    main()
