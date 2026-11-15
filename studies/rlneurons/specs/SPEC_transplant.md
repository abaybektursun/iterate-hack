# Delta transplant: the RL-Math weight difference added to Think-SFT

Written 2026-11-15 08:10 UTC, before any run. Board: the work item names this file.

## Question

Think-SFT (`allenai/Olmo-3-7B-Think-SFT`, imitation of reasoning traces, no reward) and RL-Zero-Math
(`allenai/Olmo-3.1-7B-RL-Zero-Math`, step 2,800) are both fine-tunes of the Olmo 3 base. On the 328 harder problems, with the
cue, Think-SFT has the best single-sample score on the board (219, 212, 212 in three samples; RL 207, 190, 209, 194) but 89 cap
hits against RL's 20. Does M(a) = Think-SFT + a (RL-Math - base) score above both parents there?

The README section "Difficulty profiles" filed this run and two predictions for a = 1 before any number existed (it was not
submitted). This spec keeps them and adds the coefficients 0.5 and 2 and a control.

## What is published

2605.00610 (read in full, findings in team memory): on Qwen2.5-Math-7B, SFT and GRPO from one base on the same data, the plain
sum with coefficients (1, 1) scores 47.8 on six math sets against 44.1 (SFT) and 45.5 (RL); their searched coefficients weight
the RL vector 1.82. Not covered there: an RL run started from the base with no demonstrations, an SFT parent trained on other
data (general reasoning traces), per-problem scores on a held-out hard set, cap hits, and a matched-norm random control.

## Arms

`jobs/delta_sum.py` writes M(a) (every tensor, stochastic rounding to BF16, the run stops unless the written model carries
a within 2 %). Scored by `jobs/run_cell.py --model-path`, cue, T 1.0 / top-p 1.0, cap 16,384, grader v3, one sample.

| Arm | Model | Set, seed |
|---|---|---|
| sft1_rl10 | M(1.0) | hard328, 3,000,000 |
| sft1_rl05 | M(0.5) | hard328, 3,000,000 |
| sft1_rl20 | M(2.0) | hard328, 3,000,000 |
| sft1_rl10 | M(1.0) | MATH-500, 182,000,000 |
| sft1_rnd10 | Think-SFT + noise of the norm of (RL-Math - base), per tensor | hard328, 3,000,000; only if an M arm passes the test below |

References (stored, same harness, same problems): Think-SFT cue on hard328 (jobs of work-0a00c2 and result-32ff47: 219, 212,
212), RL plain and cue on hard328 (job 5ff2: 207, 190, 209, 194), Think-SFT cue MATH-500 454, RL cue MATH-500 456 to 464.

## Hypotheses and what refutes each

- H-add (the two changes add; filed in the README): M(1.0) has RL's errors on easy problems and Think-SFT's on hard ones.
  MATH-500: 467 of 500; 460 or less refutes it. hard328: at least 219; and, added here, cap hits fall from 89 toward RL's 20:
  more than 70 cap hits refutes "the RL change makes Think-SFT finish".
- H-inert (the RL change was learned on the base and does not act on Think-SFT; the cosine of the two changes is -0.00001):
  M(1.0) is inside the range of the three Think-SFT samples on right answers (212 to 219) and cap hits within 10 of 89.
  Refuted by a paired difference to Think-SFT whose 95 % interval excludes 0, in either direction.
- H-clash (the RL change removes Think-SFT's lead on hard problems): M(1.0) below 206 on hard328.

Test for "above both parents": per problem, M arm minus the mean of the three Think-SFT samples, 95 % bootstrap over problems
(5,000 resamples, seed 0) above 0. Three coefficients are tried on the 328 itself, so a pass by one arm alone is reported as
"1 of 3 arms" and needs a second sample with a new seed before it is posted as a score above Think-SFT.

## Instrument checks

- `delta_sum` reports effective a (inner product of the written change with RL-Math - base over its squared norm): within 2 %
  of a, or the job stops.
- The random arm must not reproduce a gain of an M arm: if sft1_rnd10 moves cap hits or right answers as much as M(1.0), the
  effect is a property of any small perturbation of Think-SFT, not of the RL change.
- Stored references are the same harness: Think-SFT through `wsp_edit --recipe interp --alpha 1.0`, RL through `run_cell --model rl`.

## Outputs

`results/transplant/<arm>-01/` per arm: `run.json`, `metrics.json`, `delta_sum.json`, `rows.jsonl`, one right and one wrong
example; `results/transplant/readout.json`. Raw answers stay in `runs/<job-id>/` on the laptop.
