# Direct test of run-05/f2-m03: does a text's input-side drive set the top-8 edit's effect on it?

Written 2026-11-15 before any per-answer number below was computed. Board work-cd2924. Offline, stored rows only, no GPU.

## The mechanism and its rival

- run-05/f2-m03 (+5.14 nats over 7 results, `results/forecast/run-05/mechanisms.json`): "Each direction of an RL change acts only
  as far as the processed text drives its input (right) singular vectors ... an edit works in full on any problem set of its own
  domain and transfers to another domain in proportion to input-subspace overlap."
- run-05/f2-m01 (rival): the top-8 directions are a signed finishing dial that acts the same on every text.

What follows from f2-m03 and not from f2-m01: the size of the edit's effect on a text is set by that text's drive of the input
subspace. So (a) across texts, a text that projects more onto the 8 input directions gets a larger effect, in proportion;
(b) across domains, the transfer ratio equals the ratio of drives. f2-m01 predicts no relation between drive and effect.

## What the stored data can decide

- (b), cross-domain, is not stored: every stored forward pass with the edit's input directions (xreward trace-01, xshift run-01)
  ran on hard328 math text only. No activation of any code text is stored. So (b) is undecidable offline. Cheapest GPU cell that
  decides it: `jobs/xreward_trace.py` on the base's stored Code-cue answers of HumanEval+/MBPP+ (538 short answers, one H100,
  minutes), conditions math31, code31, random. f2-m03 predicts drive(Math dirs | code text) / drive(Math dirs | math text) of
  about 0.54, the measured transfer ratio (368 - 331) / (399 - 331); f2-m01 predicts nothing about drive and the same per-text effect.
- (a), per text within math, is decidable from stored rows: trace-01 stored the drive per position for each of the 328 base
  answers, and seven stored generation cells give the per-problem behaviour of the edit and of matched random edits on the same
  328 problems. Known before this spec (group means only): drive of cap-hit over finished answers in matched length bins is
  0.99 to 1.01 (result-a7c052). Not yet looked at: the per-answer spread of drive and its relation to per-problem effect.

## Claim tested

Within hard328, the top-8 edit's per-problem effect is proportional to the per-problem drive of Math 3.1's top-8 input subspace
by the problem's text.

## Readout (`analysis/direct_input.py`, numpy)

Drive, per problem p (from the base + cue answer of p, the text trace-01 ran):
`D_p` = mean over the answer's positions of the mean over 3 matrices (up, gate, q) and 4 layer bands of
`r_math31 = ||diag(s) V^T x|| / ||W_base x||` (trace-01's definition: the relative size of the edit's change of the matrix output
at that position, at size 1). Secondary: `A_p = D_p / Drand_p` (Drand = the same for the mean of the 3 random-V conditions with
math31's singular values).

Inputs: `runs/abaybektursun-1115-005830-2145/trace_00{0..3}.npz` (Modal Volume `iterate-runs`).

Behaviour, per problem p, hard328, cue, T 1.0 / top-p 1.0, seed 3000000, one sample per cell (`answers.jsonl` of each job):

| arm | job |
|---|---|
| base + cue (the traced text) | abaybektursun-1114-151534-e72c |
| top-8 Math 3.1 at 0.5 | abaybektursun-1115-031219-19af |
| top-8 at 1 | abaybektursun-1114-221034-007d |
| top-8 at 1.5 | abaybektursun-1115-031229-5991 |
| top-8 at 2 | abaybektursun-1115-012855-d7ed |
| random rank-8 at 1 | abaybektursun-1114-221040-5f1e |
| random rank-8 at 1.5 | abaybektursun-1115-090241-0229 |

Effect of the edit on p, measured against the random edits (both fresh samples, so regression to the mean of the traced base
sample drops out):
- `E_len(p)` = mean over the 4 top-8 sizes of log(n_new) - mean over the 2 random arms of log(n_new). Primary.
- `E_fin(p)` = mean over the 4 top-8 sizes of finished - mean over the 2 random arms of finished (finished = not cap hit).

Primary statistic: `b = beta / mean(E)`, with beta the least-squares slope of `E_len(p)` on `D_p / mean(D)` over the 328
problems. Under strict proportionality `E(p) = mean(E) * D_p / mean(D)`, so `b = 1`. 90 % percentile bootstrap over problems
(2,000 resamples, seed 0; each resample recomputes beta and mean(E)). Also reported: the spread of D (coefficient of variation,
mean of top tertile / bottom tertile), Spearman rho(D, E_len) and rho(D, E_fin), `b` for E_fin, `b` with A in place of D, and `b`
with the mean log length of the random arms as a covariate (problem difficulty from fresh samples).

## Predictions and what refutes them

- f2-m03: `b` = 1 for E_len. Refuted if the upper 90 % bound of `b` is below 0.5.
- f2-m01: `b` = 0. Refuted if the lower 90 % bound of `b` is above 0.5.
- Neither refuted (the interval covers 0.5): undecided offline; the drive spread across math texts is then too small to separate
  them, and the verdict rests on the cross-domain GPU cell above.

## Instrument checks (run first, in the same script)

1. Planted proportional effect: replace E_len by `mean(E) * D_p / mean(D)` plus the observed residuals shuffled over problems; the
   readout must return `b` within its interval of 1 (also shows the interval width the data can give when f2-m03 is true).
2. Shuffled drive: D permuted over problems; the interval of `b` must cover 0.
3. trace-01's published level reproduces: mean r of math31, band 0-8, up = 0.005 (readout.json `mods.up.mean_r`).
4. Every arm has 328 rows with problem indices equal to the trace's 328 answers.

## Outputs

`results/direct/input-01/`: `readout.json` (every number above, n, intervals), `examples.json` (one problem with high drive and
one with low drive: drive, the lengths and finish flags of every arm, the heads of the texts), `run.json` (commit, command, input
jobs).

## Amendment 1 (after the first run, before any board post)

The primary readout is confounded, as the raw rows show. Drive D correlates with answer length (Spearman 0.58 with the traced
base answer's log length, 0.55 with the random arms'), and the edit's length effect changes sign with length (it lengthens
short answers and cuts long ones, result-1b6bf2), so its mean is near zero (0.042 [0.005, 0.078]) and `b` for E_len is
-64 [-252, -30]: the frozen rule says "f2-m03 refuted", but that number measures length, not drive. The verdict therefore uses
the two readouts that control for problem difficulty (mean log length of the two fresh random arms as a covariate), one of
them listed above (E_len) and one added here (E_fin): f2-m03 refuted if both upper bounds are below 0.5, f2-m01 refuted if
both lower bounds are above 0.5, otherwise undecided. The planted check is replaced by an exact one (adding
`mean(E) * (D / mean(D) - 1)` to E must raise `b` by exactly 1), and the shuffled-drive check by the central 90 % of `b` over
500 shuffles of D, which also gives the spread of `b` when drive has no effect.
