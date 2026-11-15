"""How the model answers the problems. This is the file you modify.

solve(problems, h) gets every problem of the run as {"index": int, "problem": str} and the harness h (harness.py
documents it). It returns {index: text}; the grader reads the answer from each text.
"""

TEMPERATURE = 0.6
TOP_P = 0.95
MAX_TOKENS = 16384
SEED = 1000000


def solve(problems, h):
    requests = [{"ids": h.render(p["problem"]), "temperature": TEMPERATURE, "top_p": TOP_P, "max_tokens": MAX_TOKENS,
                 "seed": SEED + p["index"]} for p in problems]
    outputs = h.generate(requests)
    return {p["index"]: o["text"] for p, o in zip(problems, outputs)}
