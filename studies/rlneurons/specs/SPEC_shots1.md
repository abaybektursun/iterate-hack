# SPEC shots1: does a context window carry the RL gain? (board idea-607778, work-be7af1)

Written 2026-11-15 02:20 UTC, before any run.

## Question

The cued base scores 410/500 on MATH-500 (T 1.0 / top-p 1.0, grader v3) and Math-RL with the cue 457. SFT on RL's answers is
reported to transfer the RL gain while SFT on the base's own correct answers does not (2505.14216 Table 1). Does the same hold
with no training, when the answers are only placed in the context of the base model?

## Cells

Base model, cue, MATH-500, T 1.0 / top-p 1.0, cap 16,384, seed 71000000 + index, `run_cell --shots`. Three solved problems
(MATH-500 indices 0, 1, 2: the first three that the three source cells all answered right and finished) stand in front of every
prompt, each as prompt + answer + blank line. The arms differ only in who wrote the three answers:

| arm | answers written by | source rows | example tokens |
|---|---|---|---|
| base | base, cue, T 1.0 | results/day1/check_t1_n10-01 | 686 + 2,668 + 1,128 |
| rl | Math-RL 3.1, cue, T 1.0 | results/day1_wdiff/rl_cue-01 | 969 + 3,844 + 3,056 |
| code | Code-RL 3.1, cue, T 1.0 | results/day1_wdiff/code_cue-01 | 488 + 4,433 + 1,346 |

Files: `data/shots1/{base,rl,code}.json`, built by `prep/shots1_build.py`. Generation also stops when the model starts a
further example (`SHOT_STOP` in run_cell.py); such an answer is scored as finished and flagged `shot_stop`.

## Count

Problems 0, 1, 2 are left out everywhere: n = 497. Baselines recounted on the same 497 from their rows: base cue (T1, 410/500),
theta 0.25 cue (441/500), RL cue (457/500). Differences are paired by problem, 95 % interval by bootstrap over problems
(10,000 resamples). Generated tokens per problem and prompt tokens are reported for every cell.

## Hypotheses and what refutes them

- H1, RL's answers in context carry the gain: rl arm minus base cue >= +4 points and rl arm minus base arm > 0 with an interval
  above 0. Refuted if the rl arm is within 2 points of the base arm.
- H2, the base's own right answers in context are enough (a route with no RL model): base arm minus base cue >= +4 points with
  an interval above 0. Refuted if the interval contains 0.
- H3, not math-specific: code arm within 2 points of the rl arm. Refuted otherwise.
- Null for all: any three examples help by showing the format. The base arm is this control for H1 and H3.

Confound to state with any H1 result: RL's answers are longer (7,869 against 4,482 example tokens), which is part of how RL
writes. If H1 holds, a follow-up arm truncates or length-matches.

## Instrument check before the full cells

Smoke, 13 problems per arm (10 counted). Read the rows: the stop at `SHOT_STOP` fires and cuts cleanly, the answer ends with an
"Answer:" line, no row continues into a new problem, cap hits are not above the base cue's rate (1 of 10).

## After

The best arm on MATH-500 is scored once on the 328 harder problems, against base cue 164 and RL plain 206.
