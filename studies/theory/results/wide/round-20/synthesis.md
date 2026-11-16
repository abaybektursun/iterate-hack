# Synthesis, round-20 (version 20)

Written 2026-11-16T02:08:43 UTC. 65 direct facts; 3 accounts kept of 3. Score = minus the facts the blind marker marks as contradicting the account. Fact marks are the blind marker's (`marks-<account>.json`); the account's own count is shown beside them. The accounts' forecasts of the open work against their covariate-only adversaries are in `open_forecasts.md`; they are scored when the results post, in the next round's section below.

## Accounts of earlier rounds ranked by gain over their covariate-only adversary and over the readers

On the numbers posted after their forecasts were written (`open_scores.json`); per target clip3(log density of the account - log density of the adversary) at the measured value; the last two columns are each side's gain over the two readers (standing's rule). Ranked by the smaller of the account's two gains; an account adds something only when both are positive.

| source | account | targets | items | gain over its adversary (nats) | account vs readers | adversary vs readers | adds something |
|---|---|---|---|---|---|---|---|
| round-19 | round-19/account-3 | 2 | 1 | +0.083 | +0.994 | +0.912 | yes |
| round-19 | round-19/account-2 | 2 | 1 | -0.157 | +1.019 | +1.175 | no |
| round-19 | round-19/account-1 | 2 | 1 | -0.948 | +0.612 | +1.560 | no |

## This round's accounts on 62 held-out stored cells (`heldout.md`)

| account | gain over adversary | gain over readers | adds something |
|---|---|---|---|
| account-1 | -8.84 | -7.57 | no |
| account-2 | -8.23 | -6.06 | no |
| account-3 | -6.84 | -9.23 | no |

## Accounts of this round

| account | explained | not addressed | contradicts | self-marked contradicts | score |
|---|---|---|---|---|---|
| account-1 | 27 | 38 | 0 | 1 | 0 |
| account-2 | 27 | 38 | 0 | 1 | 0 |
| account-3 | 23 | 41 | 1 | 0 | -1 |

## account-1

The RL-Zero-Math weight change is small (about 0.25 % of each matrix's norm) with about 12 % of its squared norm in the top 8 singular directions of each matrix, which read a residual subspace the base's own step-by-step text already drives 8-11x more than random and write directions the base's next layers amplify (1.67x random); Think-SFT's no-reward change lies in this subspace on both sides (4.8x chance on the input side) and Code-RL's about 5x more than Think-SFT's, so any training on long deliberation concentrates there, even with an LM-judge reward (top-8 share 0.127 vs 0.135). Added to the base at 1.5x, these 8 directions alone match RL on hard328 (200.25 vs 200.0 right per 4-sample draw; equal-norm random rank-8 159-167, cued base 164) because they carry RL's own route preference, which lowers the per-step slip rate rather than only making answers finish: on problems the cued base finishes wrong they add 13.5 points (RL 12.3), on its 0-of-4 problems they take 0.88 of RL's per-sample gain, and where both fail their wrong answers agree with RL's more than the base's do. The gain sits in layers 0-21 and in the rank of the edit, not its norm: bands 0-10 and 11-21 each add about 20 of RL's ~40 hard328 points and nearly add up, layers 22-31 carry only the finishing and boxing habit and alone add nothing (166; 155 at 3x), one direction per matrix gives half (181 at 1x, 168 at 3x), and another model's top-8 edit helps only as far as it lies in Math 3.1's top-8 subspace (Math 3.0 182, IF-RL 155, Think-SFT's top-8 at 1x breaks the model), with no gain beyond RL's level (theta 1.25: 450 vs 457 on MATH-500). Changes made only at inference reach most of the gain because the base already has this deliberative mode and the three-token cue switches it on (a plain answer that happens to open with 'Okay' is right as often), the same stage RL's first 100 steps install (step 100 is within 1.4 points of the cued base, at its cap-hit rate and with its vote gain), which takes MATH-500 from 224 to 410 against RL's 457-463 and gives 77 % of RL's gain on non-math questions. What remains, about 10 points at T 1.0 and 22 at T 0.6 (where 52-63 % of the base's long answers are loops), is per-step reliability: 81 % of it lies on problems the base solves in some sample, and because the base's wrong answers scatter (same-problem pair agreement 0.26) a vote over 4 recovers 0.07-0.11 per contested problem, but it cannot reach the 26 of 36 problems where the base has no right sample, while RL, already reliable, gains only 2.8 points from voting. On code the input side is shared but the written directions are reward-specific: Code-RL's 8 directions raise the pass rate of finished answers 7 points over random while Math's add 1.5, and their fixes are problems the base passes in other samples (0.75), so the edit carries RL's reliability without RL's problem-specific losses (on problems the base passes and RL-Code fails it passes at a base resample's 0.45, not RL's 0.22).

Contradicts (blind marker): none

Contradicts (own marks): F25 (S4 says step 100 matches the cued base, but its right answers are 15 % longer (1.147), just outside the claimed range)

Explains worst: F25, F06, F11


## account-2

The RL weight change that matters is low-rank: the top-8 singular directions of each matrix's RL-minus-base difference hold about 13 % of its norm (as much under an LM-judge reward, 0.127, as under the math reward, 0.135, against 0.030 for Think-SFT), and they sit on input and output directions the base already uses for step-by-step text, which Think-SFT, Code-RL and Math 3.0 also move along (Think-SFT 4.8x chance; Math 3.1's per-matrix share pattern follows Think-SFT's, rho 0.59, not IF-RL's, rho -0.01), so on-policy RL picks the place from the base and the reward sets mainly how far to move along it. In behaviour this change does two things in order: by RL step 100 it switches most samples, one sample at a time, to the deliberative opening that the three-token cue selects (step-100 answers 1.15x the cued base's length, same cap-hit rate, same +7-point vote-of-4 gain, and the cue adds only 8.5 of 500); after that it lowers the per-step slip rate on that same route and moves its route choice toward RL's own (the edit's wrong answers agree with RL's by 0.29 more than the base's do), so final RL hits the cap 2.9 points less often, writes 1.6x longer answers, and its samples agree so much that a vote gains only 2.8 points. The untrained base changed only at inference gets the switch in full (a plain answer that happens to open deliberatively is right as often as a cued one, -0.03; T 1.0 removes the loops that fill 52-63 % of long T 0.6 attempts) and gets back part of the slip reduction by voting, because its wrong answers scatter (pairwise agreement 0.26; a vote with the real wrong answers beats one with them merged by 0.07-0.11), and that is the roughly 18 of 29 points it reaches. The remaining ~11 points are problems where the base has no right answer in 4 samples (26 of the 36 problems RL's vote wins), which no prompt, sampling or vote can select; adding the Math 3.1 top-8 directions at 1.5x recovers them almost entirely (0.88 of RL's per-sample edge there; 203 vs RL 205 of 328 per sample on hard328, against 164 for the cued base; vote-of-4 equal to RL's within 0.1 point), while random rank-8 edits at any scale from -1x to 3x stay at the base's 159-167. The gain lives in few directions in layers 0-21 and saturates at RL's level: layers 0-10 or 11-21 alone at 1.5x each give about half (183-184), layers 22-31 give nothing and hurt at 3x (166, then 155), top-1 gives about half (181) and drops at 3x (168), Math 3.0's top-8 at 1x gives about half (182), IF-RL's top-8 and Think-SFT's top-8 at tiny scale give nothing (155-156), and adding directions to a model that already has the switch and the slip reduction (RL, Think-SFT, theta >= 0.5) adds nothing beyond that model's own score (193-197 onto RL, 232 onto Think-SFT = Think-SFT's 230, theta 0.5 452 vs RL 457 on MATH-500). At 1x the edit acts as a per-sample route lottery more than a graded shift (on cued-solved problems m21's deliberative answers beat its non-deliberative ones by 0.57, and 41 % of its right answers stay plain-short), and on code the Code-RL top-8 1.5x edit raises the pass rate 7 points over a random edit by picking programs the base already writes in other samples (75 % of its fixes), not by copying RL-Code's outcomes (0.45 on problems RL-Code fails, as base resamples get); Math's directions add only 1.5 points on code.

Contradicts (blind marker): none

Contradicts (own marks): F01 (S6: a per-sample lottery says unswitched short answers should be right at about the plain base's rate, but they are 82.9 % right; the account does not say why short edit answers land on easy problems.)

Explains worst: F01, F11, F47


## account-3

RL-Zero-Math's weight change (norm 4.12) acts through a low-rank core: per matrix its 8 largest singular directions (about 12 % of squared norm, as for any on-policy reward, LM-judge 0.127, against 0.030 for diffuse Think-SFT) read a residual subspace the base's own step-by-step text already drives 8-11x more than random and write directions the base's next layers amplify (1.67x), so base + 1.5x those directions matches RL (hard328 200.25 vs 200.0 right per sample of 328, MATH-500 456 vs 457) while random rank-8 edits of equal norm at scales -1 to 3 stay at the cued base (159-167 vs 164). The change does two things the base already does on some of its own samples: it makes the answer open deliberatively and hold on after steps (mostly in the weights by RL step 100), and it lowers the per-step rate of one-off slips in every sample, so it adds right answers where the base already finishes (+13.5 points) and reproduces RL's outcome distribution rather than RL's per-problem outcomes; removing chance slips leaves each model's systematic wrong values, so the edit's wrong answers agree with RL's more than the base's do. The three-token cue supplies the opening, since base answers that open deliberatively are right at the cued rate (-0.03), which takes MATH-500 from 224 to 410.5 of 500, within 1.4 points of RL step 100 at the same cap-hit rate and about 80 % of RL's gain, provided T 1.0 removes the T 0.6 loops (loop share 0.52-0.63 past 4,096 tokens) and the cap is long enough for the long right routes that a 4,096 cap cuts. Steps 100 to 2,800 add the slip reduction (+42.5 of 500), and inference recovers only part of it: scattered base wrong answers (pair agreement 0.26) let a vote over 4 add 5-10 points for the base and step 100 against 2.9 for final RL, but on hard328 the base has no right sample on 26 of the 36 problems RL's vote wins, so the base's vote stays about 9.5 points (31 of 328) under RL's, while the 1.5x edit's vote ties RL's (+0.1) and the edit captures 0.88 of RL's per-sample advantage where the base has 0 of 4. Forecast rule for edit cells (hard328, cue, one sample): the count is 164 + 39c, with c about 1 (RL's level, about 203, where it saturates) for Math-RL top-8 over all layers at 1x to 2x (Math 3.0 at 1x about 0.45); about 0.5 for any single part that keeps layers 0-21 (layers 0-10 or 11-21 alone, direction 1 alone at 1x to 1.5x, or directions 2-8), with parts nearly adding; about 0 for layers 22-31 alone, random rank-8, self-distilled LoRAs, IF-RL directions or tiny Think-SFT directions; and negative (140-168) for one band or one direction at 3x, -1x, or signed pieces; the vote over 4 of any c about 1 edit equals RL's (about 216 of 328). Adding directions to a model already at RL's level changes nothing (RL + random 197, Think-SFT + 3x Math top-8 232 vs 230 alone), and on code RL-Code's own top-8 at 1.5x reaches RL-Code (399 vs 401 of 538, base 317), mostly on problems the base passes in other samples, while RL-Math's directions add only +1.5 pass points against Code's +7.0 because the rewards share the inputs that step-by-step text drives but each writes its own outputs.

Contradicts (blind marker): F27 (S6 (shared inputs driven by step-by-step text, each reward writes its own outputs) is the refuted mechanism; Think-SFT sits relatively more on the output side (2.4), not less)

Contradicts (own marks): none

Explains worst: F11, F16, F25

