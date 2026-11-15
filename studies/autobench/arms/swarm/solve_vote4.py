"""The swarm's vote configuration as a solve.py, for the finals: the opening cue, T 1.0 / top-p 1.0, 4 samples per
problem (seeds as run_cell.py: 41000000 + 10000 * sample + index), the answer most samples agree on, ties to the
shortest answer text. No restarts: under the time budget a restart would take the time of a later sample.
Requests are added sample by sample, so that the time budget cuts the last samples of every problem, not all the
samples of the last problems. Written after the Karpathy arm ended, to have a swarm configuration near the tokens
per problem that the arm's method uses; run once, not tuned.
"""

CUE_IDS = [1584, 2268, 33413]
SEED = 41000000
SAMPLES = 4


def solve(problems, h):
    jobs = [(p, s) for s in range(SAMPLES) for p in problems]
    outputs = h.generate([{"ids": h.render(p["problem"]) + CUE_IDS, "temperature": 1.0, "top_p": 1.0, "max_tokens": 16384,
                           "seed": SEED + 10000 * s + p["index"]} for p, s in jobs])
    cue = h.decode(CUE_IDS)
    texts = {p["index"]: [] for p in problems}
    for (p, s), o in zip(jobs, outputs):
        if o["finish"] != "time":
            texts[p["index"]].append(cue + o["text"])
    out = {}
    for index, candidates in texts.items():
        groups = []                                   # [answer, votes, shortest text with it]
        for text in candidates:
            answer = h.extract(text)
            if answer is None:
                continue
            for g in groups:
                if h.same(g[0], answer):
                    g[1] += 1
                    g[2] = min(g[2], text, key=len)
                    break
            else:
                groups.append([answer, 1, text])
        groups.sort(key=lambda g: (-g[1], len(g[2])))
        out[index] = groups[0][2] if groups else (candidates[0] if candidates else "")
    return out
