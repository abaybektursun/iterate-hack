# SPEC: direct test of round-13/s4-b, "the top-8 directions sharpen the base onto its own passing programs"

Board work-8e9805. Written before D, f_E or f_R was computed. Stored rows only: no GPU job, no forward pass.

## The claim

Rival `round-13/s4-b` (`studies/theory/results/wide/round-13/jobs/rivals-s4.json`): any reasoning reward's top-8
directions share a commit-to-a-complete-answer component that sharpens the base onto its own most likely complete
program; the gain is bounded by what the base can already write. Consequence: the problems that Code top-8 1.5x
passes and the cued base fails are problems the untrained base solves under another prompt (plain or Math cue) as
often as the extra passes of a random rank-8 1.5x edit are.

Rival `round-13/s4-a` says Code's directions raise the pass rate of finished programs through code-specific
directions, which allows new solutions outside the base's solved set: it predicts D clearly below 0. Caveat stated
now: rival a does not strictly require new solutions, so D near 0 separates the rivals only weakly; D < -0.10
refutes b.

## Files (per-problem rows, `answers.jsonl` of each job, copied with `uv run tools/gpu.py get`)

| arm | job | committed metrics |
|---|---|---|
| base, Code cue | abaybektursun-1114-170304-c03c | `studies/rlneurons/results/code1/base_cue-01` |
| base, plain | abaybektursun-1114-170258-388e | `studies/rlneurons/results/code1/base_plain-01` |
| base, Math cue | abaybektursun-1114-170309-b137 | `studies/rlneurons/results/code1/base_mathcue-01` |
| Code top-8 1.5x, Code cue | abaybektursun-1115-101434-4511 | `studies/rlneurons/results/xreward/code_dial/code_top8x1.5_code31-01` |
| random rank-8 1.5x, Code cue | abaybektursun-1115-101457-ef2c | `studies/rlneurons/results/xreward/code_dial/code_rand8x1.5_code31-01` |

All five: 538 scored problems (HumanEval+ 163, MBPP+ 375), T 1.0, top-p 1.0, seed 51000000, one sample each.
The per-problem pass table (uid and five booleans, no text) is saved as `per_problem.json` in the results folder.

## Computation

U = problems passed by base plain or base Math cue. G_E = problems Code 1.5x passes and base cue fails; G_R = same
for random 1.5x. f_E = |G_E in U| / |G_E|, f_R = |G_R in U| / |G_R|, D = f_E - f_R. 90 % percentile bootstrap over
the 538 problems (10,000 resamples, numpy default_rng(0)).

## Null and its strength

f_R is the null. The test can fail only if f_R is well below 1. Seen before writing (base rows only, no edit rows):
|U| = 378 of 538, the cued base fails 221, and 96 of those 221 (0.43) are in U. So a draw that lands at random among
the cued-base failures falls in U 43 % of the time; the random edit's extra passes favour easy problems and will sit
above that, but f_R is not forced to 1. Reported beside D: the floor 0.43 (extra passes spread at random over the
cued-base failures), and f for the planted arm "base Math cue" (its extra passes over the cued base are in U by
construction, f = 1) to show the instrument reads both ends.

## Refuting observation and frozen threshold

Refuted if D < -0.10 (point estimate). Holds if D >= -0.10. The 90 % interval is reported; if it contains -0.10
the result is stated as weakly decided. If f_R > 0.90 the test cannot separate the rivals and is reported as
undecided.
