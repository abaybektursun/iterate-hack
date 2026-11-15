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

## Amendment 1 (2026-11-15 10:03 UTC, after the first sample of a = 1 and a = 2, before any run below)

Seen so far, one sample each on hard328: a = 1 220 right, 75 cap hits; a = 2 234 right, 51 cap hits (Think-SFT alone 201 to
219 right, 89 to 95 cap hits). MATH-500 a = 1: 467, the filed number. The a = 0.5 job hung at its last request and the control
had not run (its norm check was wrong: BF16 rounding inflates dense noise to 1.40 times the intended norm; the control now
checks that the noise carries none of the RL delta, and its larger norm is stated with its result).

New arms, hard328, cue, T 1.0, one sample: a = 3 and a = 4 at seed 3,000,000; a second sample of a = 2 at seed 3,100,000;
a = 0.5 again at seed 3,000,000.

- H-dose (more of the RL delta keeps helping until the model breaks): right answers at a = 3 are at least 228 (within one
  sample's noise of a = 2 or above it) and cap hits at most 51. Refuted for a = 3 by fewer than 220 right.
- H-peak (a = 2 was a lucky sample): the second sample of a = 2 is below 222, the middle of a = 1's 220 and 234 rounded down
  to Think-SFT's best sample plus 3. If it is 222 or more, a = 2 is reported as above Think-SFT with both samples.
- Test against the parents as in the spec, now with a = 2's two samples averaged per problem.

Outputs as written (deviation from the Outputs section): one folder per set, `results/transplant/hard328-01/` and `math500-01/`, each holding all arms.

## Amendment 2 (2026-11-15 12:25 UTC, before any run below): a = 2 on a set it was not chosen on

a = 2 was chosen on the 328. Three checks with the coefficient fixed at 2:

1. fresh2026_v1 (136 competition problems of 2026, `specs/SPEC_fresh.md`, branch fresh): M(2), cue, T 1.0, 4 samples at the
   seeds of that spec (7,000,000 + 10,000 s), through `jobs/run_fresh.py`. Reference: the 4 Think-SFT cue samples and the 4 RL
   plain samples of work-7c069c (one known so far: Think-SFT sample 0 has 65 of 136). Prediction: the gain transfers, M(2)
   minus Think-SFT is above 0 with the paired 95 % interval above 0 (the 328 gave +6.9 points). Refuted if the point estimate
   is +2 points or less; between +2 and an interval that includes 0 is reported as undecided.
2. hard328 samples 2 and 3 of M(2) (seeds 3,200,000 and 3,300,000), for the vote over 4 by `analysis/day1_vote.py`'s rule.
   Prediction: vote above Think-SFT's 241; refuted at 241 or below.
3. MATH-500, M(2), one sample, seed 182,000,000. Prediction: 462 to 472 (M(1) had 467); below 460 means a = 2 costs
   accuracy on easier problems.
