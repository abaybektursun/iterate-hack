# Forecasts, round-08

Board snapshot 2026-11-15T15:46:24 UTC, written 2026-11-15T16:07:51 UTC. 16 targets; forecasters reader-1, reader-2, r3-across-2, r4-m01, r5-m03-rival, r5-m10-rival, r8-m02, r8-m09, r8-m10, r8-m12.


## t01 (work-e1b23a): How many of the 328 hard problems does the base model with a random rank-8 weight edit at 1.5x size get right with the cue, one sample each?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + random rank-8 edit at 1.5x (control for the finish dial)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> random rank-8 edit at 1.5x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 162 | [150, 174] | Random rank-8 edits at -1,1,2,3 gave 159/158/167/163 against base cue 164 (seed noise about 9), so the 1.5x random edit should land flat. |
| reader-2 | 162 | [150, 174] | Random rank-8 edits at -1,1,2,3 gave 159/158/167/163 against the cued base's 164 (result-6f1bb7), so the random dial is flat at about 160. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | 162 | [151, 173] | The theory says the edit works because it carries a weak dose of RL's own policy, so a random rank-8 edit carries no policy and should leave the cued base where it is (164 on the board; random rank-8 at -1/1/2/3 gave 159/158/167/163). |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | - |  | no forecast |
| r8-m09 | - |  | no forecast |
| r8-m10 | - |  | no forecast |
| r8-m12 | - |  | no forecast |

## t02 (work-e1b23a): How many of the 328 hard problems does the base model plus Think-SFT's 8 top weight directions, scaled to the RL-Math edit's norm (--scale 0.02), get right with the cue, one sample each?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + Think-SFT's top-8 directions per matrix scaled to Math's edit norm (--scale 0.02)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> Think-SFT's 8 directions scaled to Math's edit norm (--scale 0.02)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 162 | [145, 179] | Think-SFT directions do not point along RL (cos ~0), so at Math's small edit norm they should act like a structured perturbation near base/random level, with a wider band because it could break or help a little. |
| reader-2 | 162 | [142, 182] | At Math's norm the Think-SFT directions do not point along RL (cos ~0) and other rewards' 8 directions span 155-182, so the centre is near the base's 164 with a wide spread. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | - |  | no forecast |
| r8-m09 | - |  | no forecast |
| r8-m10 | - |  | no forecast |
| r8-m12 | - |  | no forecast |

## t03 (work-16773f): Under a majority vote over 4 samples, how many of the 136 fresh 2026 contest problems does the base model plus 1.5x the top 8 RL-Math weight directions get right with the cue (RL's vote: 57)?

Unit: right answers of 136 (vote over 4). Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top 8 directions of (RL-Math - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 55 | [47, 63] | On hard328 the 1.5x dial matched RL (203 vs 206, new samples 200.25 vs 200.0), so expect slightly under RL's fresh vote of 57. |
| reader-2 | 53 | [45, 61] | The 1.5x edit matched RL on single samples off its chosen set (200.25 vs 200.0) but trailed RL's vote (214 vs 221), so this is RL's fresh vote of 57 minus a few. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | 55 | [48, 62] | The theory says the top-8 edit puts most answers on a weak dose of RL's policy, and the cue removes the plain-base share, so 1.5x top8+cue should sit at or just below RL's fresh vote of 57 (it matched RL on hard328: 200.25 vs 200.0, and on MATH-500: 456 vs 460). |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | - |  | no forecast |
| r8-m09 | - |  | no forecast |
| r8-m10 | - |  | no forecast |
| r8-m12 | - |  | no forecast |

## t04 (work-16773f): Averaged over 4 single samples, how many of the 136 fresh 2026 contest problems does the base model plus 1.5x the top 8 RL-Math weight directions get right with the cue (RL's single-sample mean: 50.5)?

Unit: mean right answers of 136 per single sample. Cell: {"model": "Olmo-3-1025-7B base + 1.5 x top 8 directions of (RL-Math - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 48.5 | [42.5, 54.5] | The dial is level with RL on hard328 and its size was chosen there, so expect slightly under RL's fresh single mean of 50.5. |
| reader-2 | 48.5 | [43, 54] | The 1.5x edit sits at or a little below RL on single samples (hard328 203 vs 206, held-out mean 200.25 vs 200), so RL's 50.5 minus a little for a size not chosen here. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | 49 | [43.5, 54.5] | Same weak-dose-of-RL reading: 1.5x top8 with the cue should be close to RL's single-sample mean of 50.5 on fresh2026, slightly below because the dose is partial. |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | - |  | no forecast |
| r8-m09 | - |  | no forecast |
| r8-m10 | - |  | no forecast |
| r8-m12 | - |  | no forecast |

## t05 (work-60f040): Under a majority vote over 9 samples at T 1.0, how many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right (grader v3)?

Unit: right answers of 500 (vote over 9). Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0 (same cell as the stored 4 samples); top-p and token cap not stated", "samples": 9, "grader": "v3"}

> vote over 9 = 456 [449, 462] of 500 (result-c637b2)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 453 | [445, 461] | Vote over 4 is 446 with pass@4 467; Wang's majority curve adds about 2.5 points from 4 to 8 samples, and an odd k removes ties. |
| reader-2 | 453 | [446, 460] | Vote over 4 gives 446 and pass@4 467; Wang's majority curve adds about 2.5 points from 4 to 8 samples, and the board finds votes falling short of independent-sample predictions. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | 455 | [448, 462] | Switch-induced wrong answers come from diverse abandoned lines and scatter, so votes absorb them; vote 4 = 446-450, the vote grows about 2 points per doubling up to 9. |
| r8-m09 | - |  | no forecast |
| r8-m10 | - |  | no forecast |
| r8-m12 | - |  | no forecast |

## t06 (work-60f040): Under a majority vote over 12 samples at T 1.0, how many of the 500 MATH-500 problems does the untrained Olmo 3 base with the opening cue get right (grader v3)?

Unit: right answers of 500 (vote over 12). Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0 (same cell as the stored 4 samples); top-p and token cap not stated", "samples": 12, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 455 | [447, 463] | The vote curve flattens past 9 samples, so expect about 1-2 problems above the vote over 9. |
| reader-2 | 454 | [447, 461] | The vote flattens past 9 samples, so this is the vote-over-9 value plus about 1. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | 457 | [450, 464] | Same scattering of switch-made wrong answers; 12 samples add 1-3 problems over 9 as the remaining errors are reach and repeated wrong values. |
| r8-m09 | - |  | no forecast |
| r8-m10 | - |  | no forecast |
| r8-m12 | - |  | no forecast |

## t07 (work-ceccc0): With the token cap raised to 32,768, how many of the 328 hard problems does the untrained base with the cue get right in one sample at T 1.0 (grader v3)?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0, token cap 32,768, seed 3000000; top-p not stated", "samples": 1, "grader": "v3"}

> Token cap 32,768 on hard328 for Think-SFT cue, RL plain and base cue

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 168 | [156, 181] | The 16k score is about 161; of the ~75 base cap hits, extra tokens should rescue only a few because long base answers are right 17% of the time (RL gained +2, Think-SFT +23). |
| reader-2 | 170 | [157, 184] | About 162 at 16k, plus perhaps 10-12% of the base's ~75 cap hits turning right with more room (the base's long answers are right about 17% of the time; forced commits recover almost none). |
| r3-across-2 | 174 | [161, 188] | The theory says untruncated T 1.0 keeps the base's tail escape mass, so its hard328 cap hits (77 at 16,384) are unfinished runs, not locked loops; doubling the cap lets roughly half of them finish, and at about a quarter right (RL solves 19 of those 77) that adds about 10 to the 164 base rate. |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | 170 | [158, 182] | The theory says the cued deliberative register survives untruncated T 1.0 sampling rather than derailing, so its 16k cap hits (about 70-77, 0 loops at T 1.0) are unfinished reasoning; doubling the cap lets many of them finish, but at the low accuracy the base has on its long answers (about 15 % right past 12k tokens), so roughly +8 over the 16k score of about 162. |
| r8-m02 | 168 | [157, 179] | The base's long answers keep switching rather than finishing a line, so the extra 16k tokens convert few of its 67-77 cap hits to right answers (about 8). |
| r8-m09 | - |  | no forecast |
| r8-m10 | - |  | no forecast |
| r8-m12 | 169 | [159, 179] | The 16k score (about 161) plus about 70 cap hits that convert at roughly 0.11 over 16k more tokens, the late per-problem rate after selection. |

## t08 (work-ceccc0): In the same cap-32,768 run of the cued untrained base on the 328 hard problems, how many answers are right using at most 16,384 tokens (one sample, T 1.0, grader v3)?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0, run at cap 32,768, counted right only if finished within 16,384 tokens, seed 3000000; top-p not stated", "samples": 1, "grader": "v3"}

> each new cell also gives its own score at 16,384 (right with <= 16,384 tokens)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 161 | [150, 172] | Counting only answers finished within 16k makes this a fresh base-cue sample at seed 3000000 (stored 160-164, seed spread about 9). |
| reader-2 | 161 | [149, 173] | Single cued-base samples on hard328 at seed 3000000 range 155-168 (164, 160, 161), and sharding adds noise. |
| r3-across-2 | 163 | [152, 174] | Under the theory the same T 1.0 untruncated sampling reproduces the 16,384-cap behaviour, so the count within 16,384 tokens should match the board's cued-base single-sample rate on hard328 (164 at seed 3000000, reruns 155-172). |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | 161 | [152, 170] | Under the theory the cued register at T 1.0 is the same robust mode whatever the cap, so the score within 16,384 tokens is the usual cued-base single sample on hard328 at seed 3000000 (164, 160, 161 in stored runs; reruns spread about 155-168). |
| r8-m02 | 160 | [151, 169] | Counting only answers finished within 16,384 tokens reproduces the stored seed-3,000,000 sample (160-164), less run-to-run noise. |
| r8-m09 | - |  | no forecast |
| r8-m10 | - |  | no forecast |
| r8-m12 | 161 | [152, 170] | Same seed and setting as the stored samples (160, 161, 164); text cut at 16,384 tokens is unchanged by the larger cap. |

## t09 (work-8b4030): Under a majority vote over 4 samples, how many of the 136 fresh 2026 contest problems does Think-SFT plus twice the RL-Math weight change get right?

Unit: right answers of 136 (vote over 4). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> Think-SFT + 2 x (RL-Math - base) on fresh2026 (136 problems, 4 samples, seeds of SPEC_fresh)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 69 | [60, 77] | Expected single mean of about 63 plus a vote gain of about 6, like RL's 50.5 to 57. |
| reader-2 | 67 | [59, 75] | A single-sample mean of about 62, plus a vote gain of about 6 like RL's (50.5 -> 57). |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | - |  | no forecast |
| r8-m09 | 73 | [66, 80] | Single ~66 plus a vote gain of about +7 (between RL's +6.5 and Think-SFT's larger abstention-driven gain). |
| r8-m10 | 71 | [63, 79] | Single-sample mean of about 65 plus a vote gain smaller than Think-SFT's, because fewer cap hits leave more wrong answers that agree. |
| r8-m12 | - |  | no forecast |

## t10 (work-8b4030): Averaged over 4 single samples, how many of the 136 fresh 2026 contest problems does Think-SFT plus twice the RL-Math weight change get right (Think-SFT 60.0, RL 50.5)?

Unit: mean right answers of 136 per single sample. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> Fresh references: Think-SFT 60.0, RL 50.5 of 136.

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 63 | [55, 70] | a=2 added 6.9 points over Think-SFT on hard328, where a was chosen; expect a smaller transfer above Think-SFT's 60.0 on fresh. |
| reader-2 | 62 | [55, 69] | a=2 added about 11% over Think-SFT on hard328 where it was chosen; with some shrinkage on fresh that is Think-SFT's 60.0 plus about 2. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | - |  | no forecast |
| r8-m09 | 66 | [60, 72] | Think-SFT 60.0 per sample; the hybrid's hard328 relative gain (+11 %) plus ~0.5 from grading on 136. |
| r8-m10 | 65 | [57, 72] | As on hard328, the RL difference trades Think-SFT's cap hits for finishes, a net gain of a few problems over 60.0. |
| r8-m12 | - |  | no forecast |

## t11 (work-8b4030): Under a majority vote over 4 samples, how many of the 328 hard problems does Think-SFT plus twice the RL-Math weight change get right?

Unit: right answers of 328 (vote over 4). Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated (samples 3-4 at seeds 3,200,000 and 3,300,000 added to the two stored samples)", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 248 | [238, 258] | Singles are 234/229; with fewer cap hits and lower finished precision than Think-SFT, the vote gain should sit between RL's +21 and Think-SFT's +32. |
| reader-2 | 249 | [238, 259] | Singles are 234 and 229; with fewer cap hits than Think-SFT, its vote gain should fall between RL's +21 and Think-SFT's +32. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | - |  | no forecast |
| r8-m09 | 250 | [241, 258] | Singles 234/229 (mean 231.5), each with ~2 grading points recovered; a vote adds less than Think-SFT's +32 because the hybrid finishes (54 cap hits) at lower precision, so about +18. |
| r8-m10 | 248 | [238, 258] | The RL difference converts cap hits into finishes (cap hits 94 to 54), so the vote gains less than Think-SFT's +32: singles 231.5 plus about 17. |
| r8-m12 | - |  | no forecast |

## t12 (work-8b4030): In one sample per problem, how many of the 500 MATH-500 problems does Think-SFT plus twice the RL-Math weight change get right?

Unit: right answers of 500. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 466 | [456, 475] | Think-SFT cue singles are 457-462 and a=1 gave 467; a=2 finishes more but is a bit less precise. |
| reader-2 | 466 | [456, 475] | Think-SFT+1x scored 467 and Think-SFT cue singles score 457-462; doubling the dose helps hard problems more than MATH-500. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | - |  | no forecast |
| r8-m09 | 468 | [461, 474] | Think-SFT single 459.5 + ~4 from the boxed ending ending the v3 layout miss + ~4 reliability from the RL delta; a=2 at the MATH-500 plateau, about like a=1's 467. |
| r8-m10 | 466 | [458, 474] | MATH-500 answers are mostly short, before both drop points, so a = 2 is about level with a = 1 (467). |
| r8-m12 | - |  | no forecast |

## t13 (work-dc9359): Under a majority vote over 4 samples with a 32,768-token cap, how many of the 328 hard problems does Think-SFT with the cue get right?

Unit: right answers of 328 (vote over 4). Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "token cap 32,768; temperature and top-p not stated", "samples": 4, "grader": "not stated"}

> Simulation predicts vote-4 at 32k = 240/328 [232, 248]

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 245 | [234, 256] | Singles at 32k are about 228-230 against 209 at 16k, but less abstention narrows the vote gain; the simulation says 240, or 254 if late wrong answers disagree. |
| reader-2 | 245 | [236, 254] | The simulation gives 240 [232, 248], or 254 if late wrong answers disagree; sample 0 rose from 207 to 230 at 32k, so I lean a little above the simulation. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | 250 | [240, 260] | Think-SFT stays on one line (36 % asserted, 88 % precision when finished), so its 29 % cap hits finish right at 32k and the vote nears its pass@4. |
| r8-m09 | 248 | [238, 257] | Think-SFT vote 241 at 16k; at 32k many of its 29 % cap hits finish with ~68 % precision on long answers; the v3 layout loss (~2 per sample) persists because the teacher ending is unchanged. |
| r8-m10 | 251 | [240, 262] | Think-SFT's precision holds past 16k, so many of its 29 % cap hits finish right at 32k; the vote rises from 241 by about 10. |
| r8-m12 | 250 | [240, 261] | Think-SFT's cap hits (about 95 per sample) convert at about 2.8x the base rate. Its vote tracks pass@4 because it abstains, so about +9 over the 16k vote. |

## t14 (work-dc9359): From the same cap-32,768 samples cut at 16,384 tokens, how many of the 328 hard problems does Think-SFT with the cue get right under a majority vote over 4?

Unit: right answers of 328 (vote over 4). Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "run at token cap 32,768, each answer scored at 16,384 from the same text; temperature and top-p not stated", "samples": 4, "grader": "not stated"}

> each answer scored at 16,384 and 32,768 from the same text

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 238 | [228, 248] | Cut at 16k this is the stored setting, where the vote was 241 from singles around 209; this run's sample 0 scored 207 at 16k. |
| reader-2 | 238 | [229, 246] | Think-SFT's 16k vote over 4 was 241, and sample 0 of this run scores 207 at 16k against 212 stored, so slightly below 241. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | 240 | [232, 248] | Cutting the same samples at 16,384 tokens reproduces the stored 241 vote within seed noise. |
| r8-m09 | 240 | [232, 248] | Same samples cut at 16,384 tokens reproduce the stored 16k vote (241) up to seed noise; layout loss unchanged. |
| r8-m10 | 240 | [232, 248] | The same text cut at 16,384 reproduces the stored 16k vote (241) up to seed noise. |
| r8-m12 | 239 | [231, 247] | Cut at 16,384 this reproduces the stored Think-SFT 4-sample vote (241) within seed noise. |

## t15 (work-dc9359): Under a majority vote over 4 samples with a 32,768-token cap, how many of the 136 fresh 2026 contest problems does Think-SFT with the cue get right?

Unit: right answers of 136 (vote over 4). Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "token cap 32,768; temperature and top-p not stated", "samples": 4, "grader": "not stated"}

> and fresh2026 (4 samples)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 72 | [63, 80] | Think-SFT fresh single is 60 at 16k, about +8% at 32k, times the hard328 vote/single ratio of about 1.1-1.15. |
| reader-2 | 70 | [61, 78] | Think-SFT's fresh single is 60.0 at 16k; the 32k cap adds about 7%, and its vote adds about 10% of n, as on hard328. |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | 70 | [62, 78] | A one-line model gains from budget: Think-SFT single 60 of 136 at 16k, vote adds about 5, the 32k cap adds about 4. |
| r8-m09 | 71 | [64, 78] | Think-SFT 60.0 per sample on fresh2026, vote adds about +8 as on hard328 scaled, 32k adds ~3 from finished long answers; layout loss ~0.5 stays. |
| r8-m10 | 75 | [67, 83] | Fresh contest problems demand long answers; the 32k cap adds about 7 to Think-SFT's 16k vote. |
| r8-m12 | 76 | [68, 84] | Fresh contest problems are harder with more Think-SFT cap hits, so the 32k extension adds about 7 to the 16k vote. |

## t16 (work-dc9359): From the same cap-32,768 samples cut at 16,384 tokens, how many of the 136 fresh 2026 contest problems does Think-SFT with the cue get right under a majority vote over 4?

Unit: right answers of 136 (vote over 4). Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "run at token cap 32,768, each answer scored at 16,384 from the same text; temperature and top-p not stated", "samples": 4, "grader": "not stated"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768 from the same text

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 68 | [60, 76] | Think-SFT fresh single is 60.0 at 16k, scaled by the hard328 vote/single ratio of 241/209. |
| reader-2 | 66 | [58, 74] | Think-SFT's fresh single of 60.0 plus its vote gain at 16k (about +6 to +8 of 136). |
| r3-across-2 | - |  | theory says nothing |
| r4-m01 | - |  | theory says nothing |
| r5-m03-rival | - |  | theory says nothing |
| r5-m10-rival | - |  | theory says nothing |
| r8-m02 | 65 | [58, 73] | The same samples cut at 16,384 tokens: single 60 plus about 5 from the vote. |
| r8-m09 | 68 | [61, 75] | Same samples scored at 16k: the fresh vote without the long-answer finishes. |
| r8-m10 | 68 | [61, 75] | At 16k, Think-SFT's vote over 4 is about its single-sample mean (60) plus the usual vote gain. |
| r8-m12 | 69 | [62, 76] | The 16k vote: single mean 60.0 plus a vote gain near Think-SFT's hard328 ratio. |
