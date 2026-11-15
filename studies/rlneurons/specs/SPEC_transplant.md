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

## Amendment 3 (2026-11-15 17:40 UTC, before the run below): M(2) at token cap 32,768

Known: at cap 16,384 M(2) has 231.5 right and 54 cap hits on the 328 (Think-SFT 209.0 and 94.5). Think-SFT at cap 32,768
(result-c8b994, one sample, seed 3,000,000) has 230 right and 2 cap hits: with the cap doubled, Think-SFT alone reaches the
count M(2) has at 16,384. So the question is whether the RL delta only makes Think-SFT finish in fewer tokens, or also makes
it right more often.

Run: M(2), hard328, cue, T 1.0, `run_cell --max-tokens 32768`, one sample, seed 3,000,000 (the seed of the Think-SFT run).
Each answer is also counted at 16,384 tokens.

- H-tokens (the delta buys only earlier finishing): M(2) at 32,768 is 230 +- 5 (225 to 235), the Think-SFT count.
- H-more (it also adds right answers): 240 or more. Expected from the 16,384 runs: 54 cap hits, of which a quarter become
  right as for Think-SFT (23 of 91), gives about 245.
- 236 to 239 is reported as undecided: one sample against one sample, and the four Think-SFT samples at 16,384 span 11.
- Also reported: tokens per problem against Think-SFT's 11,795 at this cap.

## Amendment 4 (2026-11-15 21:00 UTC, before the run below): a second sample of M(2) at cap 32,768, on Modal

Amendment 3's run (seed 3,000,000, board work-8b4030) is on one vast.ai box. This adds a second sample with another seed, so the
two runs are two samples, not a duplicate. Board work-441e5b, branch m2cap.

Run: M(2) (`jobs/delta_sum.py --host think_sft --donor rl_math --alpha 2.0`, built inside each job), hard328, cue, T 1.0 /
top-p 1.0, `run_cell --max-tokens 32768`, seed 3,010,000 (the seed of Think-SFT's sample 1 in `SPEC_cap32vote.md`, jobs
-082022-5d48 and -093636-bb67), as 4 shards (`--shard k/4`, joined by `analysis/shard_join.py`), Modal H100, grader v3.
Smoke first: 8 problems, same command with `--n 8`.

Readout `analysis/cap32_m2.py`, folder `results/transplant/cap32_m2_s1-01/`: right at 32,768 and right with at most 16,384
generated tokens from the same answers (the `analysis/cap32.py` rule), cap hits at each, tokens per problem, and the paired
difference to Think-SFT sample 1 at 32,768 (same per-problem seeds), 95 % bootstrap over problems (10,000 resamples, seed 0).

Readings as filed in amendment 3, for this sample: 225 to 235 at 32,768 = H-tokens (the delta only saves tokens); 240 or more
= H-more (it adds right answers); 236 to 239 undecided. Also: the paired difference to Think-SFT at 32,768 has its interval
above 0 under H-more and includes 0 under H-tokens.
