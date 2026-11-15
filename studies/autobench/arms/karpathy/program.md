# autoresearch

This is an experiment to have the LLM do its own research.

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar5`). The branch `autoresearch/<tag>` must not already exist — this is a fresh run.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current master.
3. **Read the in-scope files**: The repo is small. Read these files for full context:
   - `README.md` — repository context.
   - `harness.py` — the fixed harness: model loading, the object `h` that `solve.py` uses, the time budget. Do not modify.
   - `solve.py` — the file you modify. The prompt, the sampling settings, the number of samples, what is done with them.
4. **Data**: the model and the problems are on the remote GPU machine that `./run.sh` sends `solve.py` to. They are prepared; there is nothing to check on this computer.
5. **Initialize results.tsv**: Create `results.tsv` with just the header row. The baseline will be recorded after the first run.
6. **Confirm and go**: Confirm setup looks good.

Once you get confirmation, kick off the experimentation.

## Experimentation

Each experiment runs on a single GPU. The model answers 100 math problems with a **fixed generation budget of 6 minutes** (wall clock, excluding model loading). You launch it simply as: `./run.sh` (it sends `solve.py` to a remote H100, runs it there and prints the result).

**What you CAN do:**
- Modify `solve.py` — this is the only file you edit. Everything is fair game: the prompt, text put before the model's answer, the sampling settings, the number of samples per problem and how one answer is chosen from them, several rounds of generation, how the time budget is spent.

**What you CANNOT do:**
- Modify `harness.py`, `run.sh` or `exp.py`. They are read-only. The remote machine always uses its own copy of `harness.py`.
- Install new packages or add dependencies. `solve.py` can use the Python standard library and the object `h`.
- Change the model or its weights, train anything, or use any other model. The remote machine has no network.
- Write answers to the problems, or anything specific to one of these 100 problems, into `solve.py`. The method that counts is the one that works on problems it has never seen: after the run, your best `solve.py` is scored on other problems.
- Generate text other than through `h.generate`, or touch the harness's clock.

**The goal is simple: get the highest `right`.** Since the time budget is fixed, you don't need to worry about run time — it's always 6 minutes of generation. The only constraint is that the code runs without crashing and returns its answers.

**Simplicity criterion**: All else being equal, simpler is better. A small improvement that adds ugly complexity is not worth it. Conversely, removing something and getting equal or better results is a great outcome — that's a simplification win. When evaluating whether to keep a change, weigh the complexity cost against the improvement magnitude.

**Noise**: sampling is random, and 100 problems is a small set. The same `solve.py` with other seeds can differ by several problems. Keep that in mind when you judge an improvement.

**The first run**: Your very first run should always be to establish the baseline, so you will run `solve.py` as is.

## Output format

Once the run finishes it prints a summary like this:

```
---
right:              52
problems:           100
generation_seconds: 360.0
budget_seconds:     360
generated_tokens:   391204
tokens_per_problem: 3912
requests:           100
finished_stop:      71
finished_length:    3
cut_by_time:        26
total_seconds:      512.3
```

followed by one line per problem (`problem  17 right`). You can extract the key metric from the log file:

```
grep "^right:\|^cut_by_time:" run.log
```

Each run also writes `last_run.jsonl`: for every problem, its text, the text your `solve` returned, the answer the grader read from it, and whether it was right. It does not contain the reference answers. Read a few rows when you want to know what the model actually wrote; do not load the whole file into your context.

## Logging results

When an experiment is done, log it to `results.tsv` (tab-separated, NOT comma-separated — commas break in descriptions).

The TSV has a header row and 5 columns:

```
commit	right	tokens_per_problem	status	description
```

1. git commit hash (short, 7 chars)
2. right (e.g. 52) — use 0 for crashes
3. tokens_per_problem — use 0 for crashes
4. status: `keep`, `discard`, or `crash`
5. short text description of what this experiment tried

## The experiment loop

The experiment runs on a dedicated branch (e.g. `autoresearch/mar5`).

LOOP FOREVER:

1. Look at the git state: the current branch/commit we're on
2. Tune `solve.py` with an experimental idea by directly hacking the code.
3. git commit
4. Run the experiment: `./run.sh > run.log 2>&1` (redirect everything — do NOT use tee or let output flood your context)
5. Read out the results: `grep "^right:\|^cut_by_time:" run.log`
6. If the grep output is empty, the run crashed. Run `tail -n 50 run.log` to read the Python stack trace and attempt a fix. If you can't get things to work after more than a few attempts, give up.
7. Record the results in the tsv (NOTE: do not commit the results.tsv file, leave it untracked by git)
8. If `right` improved (higher), you "advance" the branch, keeping the git commit
9. If `right` is equal or worse, you git reset back to where you started

The idea is that you are a completely autonomous researcher trying things out. If they work, keep. If they don't, discard. And you're advancing the branch so that you can iterate. If you feel like you're getting stuck in some way, you can rewind but you should probably do this very very sparingly (if ever).

**Timeout**: Each experiment should take about 10 minutes in total (model loading, 6 minutes of generation, grading). The remote machine kills a run that takes far longer. Treat that as a failure (discard and revert).

**Crashes**: If a run crashes (a bug, a bad request, etc.), use your judgment: If it's something dumb and easy to fix (e.g. a typo, a missing import), fix it and re-run. If the idea itself is fundamentally broken, just skip it, log "crash" as the status in the tsv, and move on. Every run counts against the budget, crashes included.

**NEVER STOP**: Once the experiment loop has begun (after the initial setup), do NOT pause to ask the human if you should continue. Do NOT ask "should I keep going?" or "is this a good stopping point?". The human might be asleep, or gone from a computer and expects you to continue working *indefinitely* until you are manually stopped. You are autonomous. If you run out of ideas, think harder — read papers, re-read the in-scope files for new angles, read what the model wrote in `last_run.jsonl`, try combining previous near-misses, try more radical changes. The loop runs until the human interrupts you, period. The human's interrupt is this: when `run.log` says `BUDGET EXHAUSTED`, the run is over and you stop.
