"""Prefix hand-off (specs/SPEC_handoff.md): the constants and the prefix rule shared by prep/handoff_plan.py,
jobs/handoff_gen.py and analysis/handoff.py. Fail loud: no try/except, no fallback."""
from __future__ import annotations

import hashlib
import json

from studies.rlneurons.lib import rln4_lib as R

WRITERS = {"base": "abaybektursun-1114-153825-208b", "rl": "abaybektursun-1114-183640-e828"}   # Day-1 #3 jobs; sample 0, attempt 0
CUTS = (0, 25, 50, 75, 100)                                                                    # 0 and 100: check arms only
SEED = 90_000_000


def seed(writer: str, cut: int, index: int) -> int:
    return SEED + 100_000 * (5 * list(WRITERS).index(writer) + CUTS.index(cut)) + index


def sha(x) -> str:
    return hashlib.sha256((x if isinstance(x, str) else json.dumps(x)).encode()).hexdigest()


def writer_texts(path) -> dict:
    """{problem index: the answer row of sample 0, attempt 0} from a writer job's answers.jsonl."""
    out = {}
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            if r["sample"] == 0 and r["attempt"] == 0:
                out[r["problem_index"]] = r
    return out


def answer_ids(tok, fz, text: str) -> list:
    """Token ids of a stored answer text (the cue's three sampled ids kept when the text starts with the cue)."""
    return R.encode_answer(tok, text, fz["prefill_text"], fz["prefill_ids"])[0]


def cut_len(n_ids: int, cut: int) -> int:
    return round(cut * n_ids / 100)
