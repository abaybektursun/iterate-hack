"""How the model answers the problems. This is the file you modify.

solve(problems, h) gets every problem of the run as {"index": int, "problem": str} and the harness h (harness.py
documents it). It returns {index: text}; the grader reads the answer from each text.

Method: several samples per problem, the answer most samples agree on wins. A sample first gets a short token
limit. The samples that reach it are continued, unless they repeat themselves or the vote of their problem is
clear already. A sample that never ends votes, for half, with the answer it gives when it is asked at the first limit.
"""

TEMPERATURE = 0.6
TOP_P = 0.95
FIRST_TOKENS = 1536   # the limit of the first pass
MORE_TOKENS = 2560    # what a continued sample gets on top
SAMPLES = 12
CLEAR = 0.6           # no sample of a problem is continued when this share of its samples agree already
GUESS = 0.5           # the vote of a guess
ASK = "\n\nAnswer:"    # put after a truncated sample to read the answer it has so far
SEED = 1000000
# after the study's prompt: samples get shorter and stay as often right
BRIEF = ". Keep your reasoning brief and to the point: once you have the answer, state it and stop"


def looping(text):
    """True when the end of the text already occurs earlier in it, word for word."""
    return len(text) > 400 and text[-120:] in text[:-120]


def tally(texts, h):
    """The answers of (text, votes) pairs as [answer, votes, first text with it], the most votes first."""
    groups = []
    for t, votes in texts:
        a = h.extract(t) if t else None
        if a is None:
            continue
        for g in groups:
            if h.same(g[0], a):
                g[1] += votes
                break
        else:
            groups.append([a, votes, t])
    return sorted(groups, key=lambda g: -g[1])


def solve(problems, h):
    def request(ids, seed, max_tokens):
        return {"ids": ids, "temperature": TEMPERATURE, "top_p": TOP_P, "max_tokens": max_tokens, "seed": seed}

    def by_problem(texts):
        out = {p["index"]: [] for p in problems}
        for (p, s), t in zip(jobs, texts):
            out[p["index"]].append((t, 1))
        return out

    # first pass, sample by sample, so that what the deadline cuts is the last samples of every problem
    jobs = [(p, s) for s in range(SAMPLES) for p in problems]
    requests = [request(h.render(p["problem"]) + h.encode(BRIEF), SEED + p["index"] + 1000 * s, FIRST_TOKENS) for p, s in jobs]
    outputs = h.generate(requests)
    texts = [o["text"] for o in outputs]

    # second pass. First every truncated sample is asked for the answer it would give now: a guess that counts when
    # the sample gets no further. Then the truncated samples that do not loop are continued, for the problems whose
    # vote is still open.
    cut = [i for i, o in enumerate(outputs) if o["finish"] == "length"]
    settled = {k for k, v in by_problem(texts).items() if (tally(v, h) or [[None, 0]])[0][1] >= CLEAR * SAMPLES}
    again = [i for i in cut if jobs[i][0]["index"] not in settled and not looping(texts[i])]
    ask = h.encode(ASK)
    more = h.generate([request(requests[i]["ids"] + outputs[i]["ids"] + ask, requests[i]["seed"], 24) for i in cut]
                      + [request(requests[i]["ids"] + outputs[i]["ids"], requests[i]["seed"], MORE_TOKENS) for i in again])
    for i, o in zip(again, more[len(cut):]):
        texts[i] += o["text"]

    votes = by_problem(texts)
    for i, o in zip(cut, more):   # after the samples that ended by themselves: those win a tie
        if h.extract(texts[i]) is None and o["text"].strip():
            votes[jobs[i][0]["index"]].append((texts[i] + ASK + o["text"].strip().split("\n")[0], GUESS))

    out = {}
    for k, v in votes.items():
        groups = tally(v, h)
        out[k] = groups[0][2] if groups else next((t for t, _ in v if t), "")
    return out
