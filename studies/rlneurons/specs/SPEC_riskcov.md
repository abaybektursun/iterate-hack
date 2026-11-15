# SPEC_riskcov: risk-coverage of Think-SFT, RL and the cued base. Where does the supervised model's lead sit?

Board: idea-ce2272, work-4ecc65. Builds on result-818c20 (Think-SFT + cue vote 241 of 328, RL 221, base + cue 192),
result-0033d7 (mixed vote), knowledge-dab63f (the gap is not a selection problem). Laptop only, stored rows, no GPU.
Written 2026-11-15 UTC before the analysis script existed. A planner's pilot on the same rows gave the numbers quoted under
"Pilot"; they are to be verified, not trusted (its vote used string plurality and had 238, not 241).

## Question

On the 328 harder problems Think-SFT with the cue hits the 16,384-token cap on 29 % of samples (RL 9 %) and its finished
answers are right 88.0 % of the time (RL 66.2 %). Is Think-SFT more precise than RL at the same coverage, and on which
answers: all of them, or only the long ones?

## Data (T 1.0 / top-p 1.0, cap 16,384, grader v3 as stored, 4 samples per problem)

| Model | hard328 (n = 328) | MATH-500 (n = 500) |
|---|---|---|
| Think-SFT + cue | `results/thinkvote/hard328_sft1_cue_s4-01` | `results/thinkvote/math500_sft1_cue_s4-01` |
| RL plain | `results/day1_3/hard328_rl_plain_s4r2-01` | `results/day1_3/math500_rl-01` |
| base + cue | `results/day1_3/hard328_base_cue_s4r2-01` | `results/day1_3/math500_base_cue-01` |

The RL and base runs have up to two restarts after a cap hit; Think-SFT has none. Every number here uses attempt 0 of each
sample only, for all three models. Raw text for the hand read: `runs/<job>/answers.jsonl` (job ids in each `run.json`).

## Definitions, fixed before computing

- Sample: attempt 0 of sample s of a problem. 1,312 per model on hard328, 2,000 on MATH-500.
- Answered: `extracted_v3` is not None (the sample casts a vote). Abstained: no extracted answer. Finished: `cap_hit` false.
  A cap hit can carry an extracted answer; it then counts as answered and as not finished.
- Right: `score_v3` = 1. Wrong: answered and not right.
- Coverage of a set of samples: its size over all samples. Precision: right over the set (all of the set is answered).
  Risk = 1 - precision.
- Vote: `analysis/day1_vote.vote` (groups by `rln4_lib.agree`). A vote abstains when no sample has an answer.

Label-free confidence signals (a signal sees `n_new`, `cap_hit`, `extracted_v3` of the problem's four samples, never
`score_v3` or `gold`). Samples are kept from most to least confident; abstained samples are never kept.

1. `finished`: finished answered samples before cap hits with an answer. One operating point per model.
2. `length`: fewer generated tokens first (`n_new`).
3. `agreement`: the number of the problem's four samples whose answer agrees with this one's (1 to 4), more first.
4. `agreement_length`: agreement first, then fewer tokens.
5. `finished_length`: finished first, then fewer tokens (differs from 2 only for cap hits with an answer; kept for the bins).
6. `shuffled` (null): a random order of the answered samples, seed 0.

Ties in a signal are broken by a fixed random order (seed 0), the same for every signal.

## Measurements

(a) Risk-coverage curve per model, signal and set: precision at coverage 0.05, 0.10, ..., up to the model's answered share;
95 % band from 2,000 bootstrap resamples of problems (all four samples of a problem move together). Area: mean precision
over the coverage grid up to the largest coverage all three models reach on that set (the common coverage), per signal.
Matched coverage: at each grid point up to the common coverage, precision of Think-SFT minus RL, Think-SFT minus base, RL
minus base, with a paired interval (the same resampled problems for both models).

(b) Precision of finished answered samples by length: fixed bins of `n_new` (0-2k, 2-4k, 4-8k, 8-12k, 12k-cap) and each
model's own quartiles; then the same on the problems where all three models have at least one finished answered sample.

(c) H2. Problems grouped by k = number of Think-SFT samples (of 4) that hit the cap. Per k: RL's and the base's precision on
finished answered samples, and their cap rate. Matched control for difficulty: problems are put in five strata by the
base's number of right samples (0 to 4). Expected RL precision on a group = RL's stratum precision (over all problems of the
set) weighted by the group's RL finished samples per stratum. Reported: observed, expected, observed minus expected with a
bootstrap interval over problems. The same with the roles reversed (problems by k RL cap hits, Think-SFT's precision,
strata still by the base).

(d) Per-problem outcomes right / wrong / abstained per model and the 3 x 3 table Think-SFT against RL (and against the
base): on single samples (sample s of one model against sample s of the other, the four tables summed) and on votes.

(e) H3. Rule `cut_L`: before the vote, drop every sample with `n_new` > L (it casts no vote). Variants: `strict` (no sample
left: the vote abstains) and `fallback` (no sample left: the plain vote). L in 2,000, 3,000, 4,000, 6,000, 8,000, 10,000,
12,000, 14,000, 16,000. Selection on MATH-500 only, per model: the (variant, L) with the most vote-right problems; ties to
the larger L, then to `fallback`. The selected rule is scored once on the 328 against the plain vote over 4 (paired
bootstrap, 5,000 resamples). The whole L grid on the 328 is printed as a description and never used to choose. Tokens per
problem under two accountings: `as_run` (every sample ran to its end) and `stopped` (generation stops at L: a sample costs
min(n_new, L)). Prior, related rows: `seq4_L8000`, `seq4_L12000` of `analysis/frontier.py` (sequential vote with samples
abandoned at L) were candidates there and were not chosen.

(f) Score with a penalty: right - lambda x wrong, lambda in 0, 0.5, 1, per model, for one sample (mean of the four) and for
the vote, as problems of the set.

## Hypotheses and what refutes them

- H1: Think-SFT's lead over RL on the 328 is in the long answers. Under `length`, the precision difference at matched
  coverage is inside +-3 points with an interval covering 0 up to coverage 0.50, and positive with an interval excluding 0
  at the common coverage. In the bins, the difference is in 8k and above. Refuted if the difference at matched coverage has
  an interval covering 0 at every grid point (no lead in precision), or if it excludes 0 at coverage 0.30 and below as well
  (the lead is uniform across length).
- H2: RL answers wrong where Think-SFT abstains. On the problems with at least one Think-SFT cap hit, RL's precision on
  finished answers is below the number expected from the base strata by more than 5 points, interval excluding 0. Refuted if
  observed minus expected covers 0: then difficulty alone explains RL's low precision there.
- H3 (the pilot says no): `cut_L` chosen on MATH-500 does not raise RL's or the base's vote on the 328 (difference to the
  plain vote covers 0 or is negative). Refuted if the chosen rule gains with an interval excluding 0.

## Pilot numbers to verify

Coverage 0.30 to 0.50: RL and Think-SFT equally precise (99 / 98 %, 93 / 94 %); coverage 0.71: Think-SFT 88.1 %, RL 78.6 %;
longest quartile of finished answers right 71 % Think-SFT, 24 % RL, 16 % base; RL's vote with a 14k cut 220 against 222.

## Instrument checks (in `analysis/riskcov_test.py` and asserted in the script)

1. The vote over attempt 0 reproduces 241 / 221 / 192 on hard328 and 481 / 474 / 446 on MATH-500 exactly, else the script
   stops.
2. Planted perfect abstention: a copy of RL's rows in which every wrong sample loses its answer must show precision 1 at
   every coverage and its coverage = RL's right share.
3. Shuffled lengths: with `n_new` permuted among the answered samples, the `length` curve must be flat: every grid
   point's band contains the overall precision of answered samples.
4. Planted informative signal: with `n_new` replaced by 1 for right and 2 for wrong samples, precision is 1 up to the right
   share.

## Hand read (step 4, a hand read of 25 rows, not a measurement)

10 finished RL answers of at least 8,000 tokens that are wrong, on problems where Think-SFT hit the cap; 10 finished
Think-SFT answers of at least 8,000 tokens that are right; 5 Think-SFT cap hits on the problems of the first group. Picked
by a fixed seed, not by eye. Per row: does the text derive the boxed answer, or does it stop and state one?

## Outputs

`results/riskcov/hard328-01/`, `results/riskcov/math500-01/`: `run.json`, `readout.json`, `curves.json`, `table.md`,
`examples.json` (one right, one wrong with text). `results/riskcov/read-01/`: the 25 rows read and the notes.
