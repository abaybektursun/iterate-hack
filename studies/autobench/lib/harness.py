"""The fixed harness of one experiment. Runs in the GPU container, in a directory that holds only solve.py:

    /opt/rln-vllm/bin/python /trusted/harness.py      $AUTOBENCH_IN: the problems, no answers; $AUTOBENCH_OUT: the record

It loads the model with the engine settings, tokenizer and model revision that the repository's other runs on
these problems use (run_cell.py: frozen4.json, rln4_gen.VllmEngine, at most 16,384 generated tokens per request),
calls solve(problems, h) of solve.py, and writes what solve returned. It holds no answer: grading happens
afterwards on another machine.

solve.py generates text only through h.generate, which has a fixed budget of wall-clock seconds. The clock starts
at the first call. At the deadline every unfinished request is aborted and returns no text.

What solve.py may use (the object h):
  h.render(problem)     token ids of the study's prompt for a problem text (the tokenizer's chat template, pair1)
  h.encode(text)        token ids of a text, no special tokens;  h.decode(ids)  the text of token ids
  h.generate(requests)  run a list of requests to the end, return one result per request, in order.
                        request: {"ids": [...], "temperature": 1.0, "top_p": 1.0, "max_tokens": 16384, "seed": 0}
                                 and optionally top_k, min_p, repetition_penalty, presence_penalty, frequency_penalty
                        result:  {"text": str, "ids": [...], "n_tokens": int, "finish": "stop" | "length" | "time"}
  h.seconds_left()      seconds of the budget that remain (the whole budget before the first generate call)
  h.extract(text)       the answer string the grader would read from a text (grader v3), or None
  h.same(a, b)          True when the grader treats two answer strings as equal

solve returns {problem index: the text to grade}. A problem that is missing counts as wrong.
"""
import json
import os
import runpy
import time

CAP = 16384               # frozen4.json "cap": the most tokens one request may generate
MAX_LEN = 2048 + CAP      # run_cell.py's max_model_len: prompt plus generated tokens of one request
SAMPLING = ("temperature", "top_p", "top_k", "min_p", "repetition_penalty", "presence_penalty", "frequency_penalty")


class Harness:
    def __init__(self, engine, tok, stop_id, budget_s, render, extract, same, clock=time.time):
        self._engine, self._tok, self._stop_id, self._clock = engine, tok, stop_id, clock
        self._render, self.extract, self.same = render, extract, same
        self.budget_s, self.deadline = budget_s, None
        self.stats = {"calls": 0, "requests": 0, "generated_tokens": 0, "finish": {"stop": 0, "length": 0, "time": 0}}

    def render(self, problem):
        return self._render(self._tok, problem)

    def encode(self, text):
        return [int(i) for i in self._tok(text, add_special_tokens=False)["input_ids"]]

    def decode(self, ids):
        return self._tok.decode(ids, skip_special_tokens=False)

    def seconds_left(self):
        return self.budget_s if self.deadline is None else max(0.0, self.deadline - self._clock())

    def _done(self, i, results, text, ids, finish):
        results[i] = {"text": text, "ids": ids, "n_tokens": len(ids), "finish": finish}
        self.stats["generated_tokens"] += len(ids)
        self.stats["finish"][finish] += 1

    def generate(self, requests):
        if self.deadline is None:
            self.deadline = self._clock() + self.budget_s
        self.stats["calls"] += 1
        results, live = [None] * len(requests), {}
        for i, r in enumerate(requests):
            unknown = set(r) - {"ids", "max_tokens", "seed", *SAMPLING}
            if unknown:
                raise ValueError(f"request {i}: unknown fields {sorted(unknown)}")
            ids = [int(t) for t in r["ids"]]
            if not 0 < len(ids) < MAX_LEN:
                raise ValueError(f"request {i}: {len(ids)} prompt tokens, the limit is {MAX_LEN - 1}")
            self.stats["requests"] += 1
            if self._clock() >= self.deadline:
                self._done(i, results, "", [], "time")
                continue
            rid = f"r{self.stats['requests']}"
            sampling = {"repetition_penalty": 1.0, **{k: r[k] for k in SAMPLING if k in r}}
            self._engine.add(rid, ids, sampling, int(r.get("seed", 0)), min(int(r.get("max_tokens", CAP)), CAP, MAX_LEN - len(ids)))
            live[rid] = i
        while live:
            if self._clock() >= self.deadline:
                self._engine.abort(list(live))
                for i in live.values():
                    self._done(i, results, "", [], "time")
                break
            for rid, out_ids, _, _ in self._engine.step():
                stop = next((j for j, t in enumerate(out_ids) if t == self._stop_id), None)
                ids = list(out_ids if stop is None else out_ids[:stop])
                self._done(live.pop(rid), results, self.decode(ids), ids, "length" if stop is None else "stop")
        return results


def main():
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer

    from studies.rlneurons.jobs import rln4_gen as J
    from studies.rlneurons.lib import n13_gen as G
    from studies.rlneurons.lib import n13_score as S
    from studies.rlneurons.lib import rln4_lib as R

    t0 = time.time()
    spec = json.loads(open(os.environ["AUTOBENCH_IN"]).read())
    fz = json.loads(open("/repo/studies/rlneurons/data/rln4/frozen4.json").read())
    tok_dir = snapshot_download(fz["tokenizer"][0], revision=fz["tokenizer"][1], allow_patterns=["*.json", "*.jinja", "*.txt"])
    tok = AutoTokenizer.from_pretrained(tok_dir)
    repo, _, revision = fz["models"]["base"]
    model_dir = snapshot_download(repo, revision=revision, allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"])
    os.environ.update(G.ENGINE_ENV)
    engine = J.VllmEngine(model_dir, tok_dir, MAX_LEN)
    h = Harness(engine, tok, S.STOP_ID, spec["budget_s"], S.render_ids, lambda text: R.extract_v3(text)[1], R.agree)
    load_s = time.time() - t0

    solve = runpy.run_path("solve.py")["solve"]
    answers = solve([dict(p) for p in spec["problems"]], h)
    wanted = {p["index"] for p in spec["problems"]}
    bad = [k for k, v in answers.items() if k not in wanted or not isinstance(v, str)]
    if bad:
        raise ValueError(f"solve returned keys that are not problem indices, or texts that are not strings: {bad[:5]}")
    record = {"answers": [[k, v] for k, v in answers.items()], **h.stats, "budget_s": spec["budget_s"], "load_seconds": round(load_s, 1),
              "generation_seconds": round(spec["budget_s"] - h.seconds_left(), 1), "model": [repo, revision], "engine": engine.info,
              **engine.memory()}
    with open(os.environ["AUTOBENCH_OUT"], "w") as f:
        json.dump(record, f)


if __name__ == "__main__":
    main()
