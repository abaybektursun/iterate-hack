# Code pair, step 1 (2026-11-15 UTC, written before the first run; work-d84808)

Question: how much of the code gain of `allenai/Olmo-3.1-7B-RL-Zero-Code` over its base `allenai/Olmo-3-1025-7B` does the base
reach with an opening cue and no training? DIRECTION.md: "The same harness then runs unchanged on the Code pair."

Closest published numbers (knowledge-9f8067): none for this pair with a cue. Third party, LiveCodeBench v6, T 0.8: base 10.1 %, RL
Code 24.3 % pass@1. Wang 2610.06851 Table 5, HumanEval, T 0.6, math prompt: base 50.2 % -> 69.8 % with a cue, RL-Zero-Math 68.5 %.
Differs here: the 3.1 Code model, its own prompt template, HumanEval+ and MBPP+ tests, T 1.0 / top-p 1.0, cap 16,384.

## Measurement

- Problems: HumanEval+ (164) and MBPP+ (378), revisions and sha256 in `data/code1/frozen_code1.json`. Training-set overlap by the
  study's 8-gram rule: 1 and 2 problems (HumanEval/47, Mbpp/641, Mbpp/804); reported with and without them.
- Prompt: the Code model's chat template (raw text), tokenizer of the Code model for both models. Content per problem:
  `lib/code_lib.problem`. One sample per problem, seed 51000000 + index, T 1.0 / top-p 1.0, cap 16,384 generated tokens.
- Grader: last fenced block of the answer (whole answer if none) followed by the benchmark's tests, exit code 0 within 60 s
  (`lib/code_lib.py`). Before any generation the job runs every reference solution (must pass) and a planted wrong program per
  problem (must fail) and stops if either check fails.
- Cells, in this order: (1) RL Code plain; (2) base plain; (3) base + cue; (4) RL Code + cue. The cue is the most frequent first
  three tokens of the RL Code model's answers in cell 1, the rule that gave the Math cue `' line!\n\nOkay'`. It is fixed from
  cell 1's texts alone, before cell 3 is scored.
- Statistics: pass counts of 542 with Wilson intervals; cell differences by paired bootstrap (5,000) over problems; cap hits and
  generated tokens per problem for every cell.

## Hypotheses

- H1, the cue carries most of the gain, as in Math (18 of 29 points): base + cue recovers at least half of (RL plain - base
  plain). Refuted if it recovers less than half, or if the interval of (base + cue - base plain) includes 0.
- H2, there is no gain to recover on these sets: RL plain - base plain interval includes 0. Then the pair needs a harder set
  (LiveCodeBench) and this step reports that.
- H3, the cue is specific to the model: the Math cue `' line!\n\nOkay'` on the base gives the same score as the Code cue (interval
  of the difference includes 0). Run only if H1 holds.

Cost: about 542 answers per cell; at the Math cells' 1,000 tokens/s and under 5,000 tokens per answer, under 45 H100 minutes per
cell. Smoke first: grader check on cpu, then `--n 5` on each model.
