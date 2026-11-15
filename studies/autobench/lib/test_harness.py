"""Checks of lib/harness.py's Harness with a stand-in engine and tokenizer (no vLLM, no GPU): the time budget ends
generation, the stop token is cut, limits and unknown fields are refused.

    python3 studies/autobench/lib/test_harness.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import CAP, MAX_LEN, Harness  # noqa: E402

STOP = 99


class Tok:
    def decode(self, ids, skip_special_tokens=False):
        return " ".join(str(i) for i in ids)

    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": [len(w) for w in text.split()]}


class Engine:
    """Each step advances the clock by 10 s and finishes one request, in the order added. A request with seed 1
    ends with the stop token, any other runs to its max_tokens (capped at 3 tokens here)."""

    def __init__(self, clock):
        self.clock, self.queue, self.added, self.aborted = clock, [], [], []

    def add(self, rid, ids, sampling, seed, max_tokens):
        self.queue.append((rid, seed))
        self.added.append({"rid": rid, "sampling": sampling, "max_tokens": max_tokens})

    def step(self):
        self.clock[0] += 10
        rid, seed = self.queue.pop(0)
        return [(rid, [7, 8, STOP] if seed == 1 else [7, 8, 9], None, "stop" if seed == 1 else "length")]

    def abort(self, rids):
        self.aborted += rids
        self.queue = [q for q in self.queue if q[0] not in rids]


def harness(budget_s):
    clock = [1000.0]
    engine = Engine(clock)
    return Harness(engine, Tok(), STOP, budget_s, lambda tok, problem: [1, 2], lambda text: text, lambda a, b: a == b,
                   clock=lambda: clock[0]), engine


h, engine = harness(15)
assert h.seconds_left() == 15                                   # the clock has not started
out = h.generate([{"ids": [1], "seed": 1}, {"ids": [1], "seed": 2}, {"ids": [1], "seed": 1}, {"ids": [1], "seed": 1}])
assert [o["finish"] for o in out] == ["stop", "length", "time", "time"], out          # the deadline (15 s) is passed after the 2nd step of 10 s
assert out[0] == {"text": "7 8", "ids": [7, 8], "n_tokens": 2, "finish": "stop"}     # the stop token is cut
assert out[2] == {"text": "", "ids": [], "n_tokens": 0, "finish": "time"} and len(engine.aborted) == 2
assert h.generate([{"ids": [1]}])[0]["finish"] == "time" and len(engine.added) == 4   # after the deadline nothing reaches the engine
assert h.stats == {"calls": 2, "requests": 5, "generated_tokens": 5, "finish": {"stop": 1, "length": 1, "time": 3}}, h.stats

h, engine = harness(1000)
h.generate([{"ids": [1] * 3000, "max_tokens": 10 ** 9, "temperature": 0.6}, {"ids": [1]}])
assert engine.added[0]["max_tokens"] == MAX_LEN - 3000 and engine.added[1]["max_tokens"] == CAP
assert engine.added[0]["sampling"] == {"repetition_penalty": 1.0, "temperature": 0.6}
for bad in ({"ids": [1], "stop": ["x"]}, {"ids": []}, {"ids": [1] * MAX_LEN}):
    try:
        h.generate([bad])
    except ValueError:
        continue
    raise AssertionError(f"accepted {str(bad)[:60]}")
assert h.encode("ab cde") == [2, 3] and h.render("x") == [1, 2]
print("harness.py: checks passed")
