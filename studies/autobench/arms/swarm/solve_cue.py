"""The swarm's base configuration as a solve.py, for the finals: the opening cue of frozen4.json (prefill_ids, the
text " line!\n\nOkay") after the prompt, T 1.0 / top-p 1.0, one sample, seeds as run_cell.py's T1 row
(41000000 + index). The graded text is the cue followed by the generated text, as run_cell.py records it.
"""

CUE_IDS = [1584, 2268, 33413]
SEED = 41000000


def solve(problems, h):
    requests = [{"ids": h.render(p["problem"]) + CUE_IDS, "temperature": 1.0, "top_p": 1.0, "max_tokens": 16384,
                 "seed": SEED + p["index"]} for p in problems]
    outputs = h.generate(requests)
    return {p["index"]: h.decode(CUE_IDS) + o["text"] for p, o in zip(problems, outputs)}
