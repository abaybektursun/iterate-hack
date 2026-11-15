# autoresearch on a math benchmark

The idea is Karpathy's autoresearch: give an AI agent a small but real setup and let it experiment autonomously.
It modifies the code, runs it for a fixed time, checks if the result improved, keeps or discards, and repeats.

Here the setup is not a training script. It is the way a fixed language model is used to answer math problems.

- The model is `allenai/Olmo-3-1025-7B`, a 7B base model: pretrained only, no instruction tuning, no reinforcement
  learning. Its weights are fixed. It runs on a remote H100 under vLLM.
- The task is 100 competition math problems. The metric is **right**: how many of the 100 the grader accepts.
  Higher is better.
- The grader reads one answer from each text that `solve.py` returns: the last line of the form `Answer: ...`, or
  the last `\boxed{...}` if that comes later. It compares it with the reference answer as mathematics, so `1/2`
  and `\frac{1}{2}` are equal. `h.extract(text)` gives the string the grader would read.

## Files

- **`harness.py`** — the fixed harness: loads the model, gives `solve.py` the object `h`, enforces the time
  budget. Its docstring is the reference for `h`. Not modified.
- **`solve.py`** — the single file the agent edits: the prompt, the sampling settings, how many samples, what is
  done with them. Everything about how the model is used is fair game.
- **`program.md`** — the instructions for the agent.
- **`run.sh`** — runs one experiment on the remote GPU. `exp.py` is its client. Not modified.

Generation has a **fixed budget of 6 minutes** of wall clock for all 100 problems together (model loading
excluded). When it ends, every unfinished request is cut and returns no text.
