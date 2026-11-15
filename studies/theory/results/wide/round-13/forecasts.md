# Forecasts, round-13

Board snapshot 2026-11-15T21:27:03 UTC, written 2026-11-15T22:06:29 UTC. 25 targets; forecasters reader-1, reader-2, round-10/weights-m03, round-09/training-m01, round-13/s1-a, round-13/s3-a, round-13/s4-a, round-13/s4-b, round-13/s6-b.


- round-10/weights-m03 (weights, carried): The effect of an added RL change depends on the host. Think-SFT's high-rank imitation change (3.7 % of weight norm, top 8 directions hold 2 %) already sets the long-reasoning features that RL's directions read, so RL's push has about a quarter of its effect on the base: a=1 cut Think-SFT's cap hits by 20 %, not 74 %. The response is weak but stable, no breakdown up to 4x. Its correctness covers every domain in its traces.

- round-09/training-m01 (training, carried): Think-SFT imitated teacher traces inside its ChatML template, opened by <think> and closed by a final answer after the thinking block. Where and how it states the answer is learned conditional on that template. On the raw template with the cue it reasons as well but sometimes misplaces the final answer (on the line after 'Answer:'), which v3 misses. Its own template restores the trained ending: more MATH-500 answers counted, unchanged reasoning length and cap behaviour on hard328.

- round-13/s1-a (s1): The kept method caps every sample at 4,096 tokens. On hard328 the cued base's right answers have a median length of about 3,900 tokens, so the cap cuts roughly half of the right-answer length mass. A cut sample casts no vote. On problems whose only right routes are long, the vote sees only short finished answers, mostly wrong on hard problems. The score is bounded by problems solvable in under 4,096 tokens, not by vote size.

- round-13/s3-a (s3): On MATH-500 at T 1.0, the cued base's wrong answers to a problem spread over many values, while its right answers agree on one. So the plurality vote is right whenever the right answer is the mode, even below half the samples. The ceiling for votes over many samples is the number of problems where the right answer is the mode (about 470-475), not the number where it is a majority.

- round-13/s4-a (s4): RL-Code's code gain sits almost entirely in its own top-8 directions, and in early/middle layers it raises the pass rate of finished programs, not just how often a program finishes. At 1.5x it matches RL-Code. Math's directions help code only through the shared finishing channel (fewer cap hits and missing code blocks), passing those recovered answers at the base rate. With Code's directions already finishing nearly everything, adding Math's gives little.

- round-13/s4-b (s4): Any reasoning reward's top-8 directions share a generic commit-to-a-complete-answer component, whose input side is excited by code and math text alike. It sharpens the base onto its own most likely complete program, which on code is usually a passing one. The gain is limited by what the base can already write (its pass@k), not by RL-Code's level, so Math's and Code's directions add until that ceiling.

- round-13/s6-b (s6): HumanEval+/MBPP+ are easy for the cued base: most problems it fails in one sample it passes in others, so the code gap is almost all per-sample reliability. Code-RL's top-8 directions lower the per-step error rate on reasoning text everywhere, as Math's dial does on finished-wrong math (result-124593). On a set whose gap is reliability, that recovers nearly all of RL's gain. On hard328, where a third of the gap needs answers the base never writes, it recovers less.

## t01 (work-3d4e90): Think-SFT in its own chat format at its released sampling setting (T 0.6, top-p 0.95, cap 32,768), one sample per problem on the 328 harder problems: how many of 328 are right under grader v3?

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own chat format", "set": "hard328", "n": 328, "sampling": "T 0.6 / top-p 0.95, cap 32,768 tokens; seeds paired with the T 1.0 cells of results/native", "samples": 1, "grader": "v3"}

> Think-SFT at its released sampling setting (generation_config.json: T 0.6 / top-p 0.95, own chat format, cap 32,768), never run here: hard328 and MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 226 | [210, 240] | Think-SFT own format at T 1.0 cap 32k scored 232/328 (result-dd9239); T 0.6/top-p 0.95 is its released setting, small downside risk from more repetition at lower temperature. |
| reader-2 | 235 | [222, 248] | Own format at T 1.0, cap 32,768 gave 232 (cue samples 230-235); T 0.6 is assumed to be about level or slightly better for an SFT reasoning model, with some risk of drift or loops. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | 232 | [219, 245] | Theory: the own template leaves reasoning length and cap behaviour on hard328 unchanged, so the count stays at the cue/own-format level at cap 32,768 (own format T 1.0 232; cue cap-32k singles 230-235), widened for the untested T 0.6. |
| round-13/s1-a | 230 | [214, 245] | native T 1.0 at cap 32,768 gives 232; with no cap binding, T 0.6 changes little |
| round-13/s3-a | 236 | [224, 248] | 232 at T 1.0 in its own format. At T 0.6 / top-p 0.95 a reasoning SFT model is about level or a little better, with the same paired seeds. |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t02 (work-3d4e90): Think-SFT in its own chat format at its released sampling setting (T 0.6, top-p 0.95, cap 32,768), one sample per problem on MATH-500: how many of 500 are right under grader v3?

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own chat format", "set": "MATH-500", "n": 500, "sampling": "T 0.6 / top-p 0.95, cap 32,768 tokens; seeds paired with the T 1.0 cells of results/native", "samples": 1, "grader": "v3"}

> Think-SFT at its released sampling setting (generation_config.json: T 0.6 / top-p 0.95, own chat format, cap 32,768), never run here: hard328 and MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 471 | [460, 481] | Same model and format at T 1.0 cap 32k scored 474/500 (result-0a0a5a); T 0.6 expected near that with slight loss from loops. |
| reader-2 | 475 | [465, 484] | Own format at T 1.0, cap 32,768 gave 474 of 500 on the paired seeds; T 0.6 is expected to be about level. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | 474 | [465, 482] | Theory: the own (trained) template restores the answer ending v3 reads, so MATH-500 keeps the own-format gain over cue (own format cap 32k at T 1.0 = 474 vs cue 457-462 at 16k), assuming T 0.6 does not change the reasoning. |
| round-13/s1-a | 473 | [462, 483] | native T 1.0 gives 474; MATH-500 answers are short, so neither the cap nor T matters |
| round-13/s3-a | 476 | [466, 485] | 474 at T 1.0 in its own format with cap 32,768. T 0.6 is near level; the ceiling is close. |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t03 (work-f58d89): The base model with RL-Math's and RL-Code's top-8 weight directions both added at 1x, one sample per problem on HumanEval+ and MBPP+ at the first of two new seeds: how many problems pass (earlier seed: 411 of 538)?

Unit: problems passed. Cell: {"model": "base Olmo-3-1025-7B + RL-Math top-8 directions at 1x + RL-Code top-8 directions at 1x", "prompt": "not stated", "set": "HumanEval+ and MBPP+", "n": "not stated", "sampling": "not stated; first of 2 new seeds", "samples": 1, "grader": "not stated"}

> base + Math 1x + Code 1x on HumanEval+/MBPP+ at 2 new seeds

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 407 | [404, 410] | result-2a5195 reports base + Math 1x + Code 1x at seed 52M (first new seed) = 407/538. |
| reader-2 | 407 | [403, 411] | result-2a5195 reports 407 for the sum edit at seed 52M, the first new seed. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 405 | [390, 420] | 411 at the earlier seed, regressed toward RL-Code's 401 |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | 396 | [385, 406] | Code 1x already finishes ~97 % of answers; Math's finishing channel has <=17 failures left to recover, so this sits at Code 1x/RL-Code level (~390-400); the earlier 411 was a high draw. |
| round-13/s4-b | 416 | [407, 427] | The two commit components add toward the base's pass@k ceiling, above RL-Code; the earlier seed gave 411. |
| round-13/s6-b | 405 | [390, 420] | Math's directions add reliability on code too (368 vs random 331), partly adding to Code's; the 411 draw shrinks toward about 405. |

## t04 (work-f58d89): The base model with RL-Math's and RL-Code's top-8 weight directions both added at 1x, one sample per problem on HumanEval+ and MBPP+ at the second of two new seeds: how many problems pass (earlier seed: 411 of 538)?

Unit: problems passed. Cell: {"model": "base Olmo-3-1025-7B + RL-Math top-8 directions at 1x + RL-Code top-8 directions at 1x", "prompt": "not stated", "set": "HumanEval+ and MBPP+", "n": "not stated", "sampling": "not stated; second of 2 new seeds", "samples": 1, "grader": "not stated"}

> base + Math 1x + Code 1x on HumanEval+/MBPP+ at 2 new seeds

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 401 | [398, 404] | result-2a5195 reports the sum at seed 53M (second new seed) = 401/538. |
| reader-2 | 401 | [397, 405] | result-2a5195 reports 401 for the sum edit at seed 53M, the second new seed. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 405 | [390, 420] | same cell at another seed |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | 396 | [385, 406] | Same cell, other seed: Code-saturated finishing plus Math's small leftover. |
| round-13/s4-b | 416 | [407, 427] | As t03, other seed. |
| round-13/s6-b | 405 | [390, 420] | As t03, another seed. |

## t05 (work-f58d89): RL-Zero-Code, one sample per problem on HumanEval+ and MBPP+ at the first of two new seeds: how many problems pass (earlier seed: 401 of 538)?

Unit: problems passed. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Code", "prompt": "not stated", "set": "HumanEval+ and MBPP+", "n": "not stated", "sampling": "not stated; first of the 2 new seeds", "samples": 1, "grader": "not stated"}

> with RL-Code and Code-alone 1x at the same seeds

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 395 | [392, 398] | result-2a5195 reports RL-Code at seeds 51/52/53M as 401, 395, 403; first new seed = 395. |
| reader-2 | 395 | [391, 399] | result-2a5195 reports 395 for RL-Code at seed 52M. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 400 | [386, 414] | 401 at the earlier seed; seed spread about 7 |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | 399 | [385, 412] | RL-Code reseeded: 401 earlier, seed scatter SD about 8 on 538. |
| round-13/s4-b | 400 | [386, 413] | RL-Code reseeded: 401 earlier, seed scatter. |
| round-13/s6-b | 398 | [384, 412] | RL-Code 401 replicates within seed SD of about 8. |

## t06 (work-f58d89): RL-Zero-Code, one sample per problem on HumanEval+ and MBPP+ at the second of two new seeds: how many problems pass (earlier seed: 401 of 538)?

Unit: problems passed. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Code", "prompt": "not stated", "set": "HumanEval+ and MBPP+", "n": "not stated", "sampling": "not stated; second of the 2 new seeds", "samples": 1, "grader": "not stated"}

> with RL-Code and Code-alone 1x at the same seeds

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 403 | [400, 406] | result-2a5195: RL-Code at second new seed (53M) = 403. |
| reader-2 | 403 | [399, 407] | result-2a5195 reports 403 for RL-Code at seed 53M. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | - |  | no forecast |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | 399 | [385, 412] | As t05. |
| round-13/s4-b | 400 | [386, 413] | As t05. |
| round-13/s6-b | 398 | [384, 412] | As t05. |

## t07 (work-f58d89): The base model with only RL-Code's top-8 weight directions added at 1x, one sample per problem on HumanEval+ and MBPP+ at the first of two new seeds: how many problems pass (earlier seed: 386 of 538)?

Unit: problems passed. Cell: {"model": "base Olmo-3-1025-7B + RL-Code top-8 directions at 1x", "prompt": "not stated", "set": "HumanEval+ and MBPP+", "n": "not stated", "sampling": "not stated; first of the 2 new seeds", "samples": 1, "grader": "not stated"}

> with RL-Code and Code-alone 1x at the same seeds

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 397 | [394, 400] | result-2a5195: base + Code 1x at 52M = 397. |
| reader-2 | 397 | [393, 401] | result-2a5195 reports 397 for Code directions alone at 1x at seed 52M. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 389 | [374, 403] | 386 at the earlier seed and 399 at 1.5x |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | 389 | [375, 403] | Code 1x carries most of RL-Code's gain (386 earlier; 1.5x 399); reseed scatter. |
| round-13/s4-b | 385 | [371, 399] | Code 1x: 386 earlier; less sharpening than 1.5x (399). |
| round-13/s6-b | 390 | [375, 405] | The dial cells 386/399/394 fit one true rate near 390, and 386 was a slightly low draw. |

## t08 (work-f58d89): The base model with only RL-Code's top-8 weight directions added at 1x, one sample per problem on HumanEval+ and MBPP+ at the second of two new seeds: how many problems pass (earlier seed: 386 of 538)?

Unit: problems passed. Cell: {"model": "base Olmo-3-1025-7B + RL-Code top-8 directions at 1x", "prompt": "not stated", "set": "HumanEval+ and MBPP+", "n": "not stated", "sampling": "not stated; second of the 2 new seeds", "samples": 1, "grader": "not stated"}

> with RL-Code and Code-alone 1x at the same seeds

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 391 | [388, 394] | result-2a5195: base + Code 1x at 53M = 391. |
| reader-2 | 391 | [387, 395] | result-2a5195 reports 391 for Code directions alone at 1x at seed 53M. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | - |  | no forecast |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | 389 | [375, 403] | As t07. |
| round-13/s4-b | 385 | [371, 399] | As t07. |
| round-13/s6-b | 390 | [375, 405] | As t07. |

## t09 (work-f58d89): Think-SFT with RL-Math's top-8 weight directions added at 3x, one sample per problem on the 328 harder problems at seed 3100000: how many of 328 are right (earlier seed: 232)?

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT + RL-Math top-8 directions at 3x", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated; seed 3100000", "samples": 1, "grader": "not stated"}

> Think-SFT + Math top-8 3x on hard328 at seed 3100000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 240 | [237, 243] | result-2a5195: Think-SFT + Math top-8 3x at seed 3.1M = 240/328. |
| reader-2 | 240 | [237, 243] | result-2a5195 reports 240 (42 cap hits) at seed 3.1M. |
| round-10/weights-m03 | 226 | [213, 239] | Theory: on the Think-SFT host the RL push is weak but stable with no breakdown up to 4x, so 3x top-8 sits a few points above Think-SFT's 209 (1.5x 220, full 3x change 227); the 232 seed regresses toward ~226. |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 228 | [214, 242] | 232 at the earlier seed, single-sample spread about 7 |
| round-13/s3-a | 240 | [236, 244] | result-2a5195 already posts 240 (42 cap hits) for this cell at seed 3,100,000. |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t10 (work-16b37f): The base model with RL-Math's top-8 directions added only in layers 22-31 at 4.5x size, with the cue, one sample per problem on the 328 harder problems: how many of 328 are right?

Unit: right answers of 328. Cell: {"model": "base Olmo-3-1025-7B + RL-Math top-8 directions in layers 22-31 only, at 4.5x (activation-matched up)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated; seed of sample 1", "samples": 1, "grader": "not stated"}

> L22-31 x4.5, x3.0, L0-10 x0.2 (sample 1)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 102 | [98, 106] | result-e18bd8: top8 x4.5 on L22-31 = 102/328 (broken ' which ' loops). |
| reader-2 | 102 | [98, 106] | result-e18bd8 reports 102 for the L22-31 x4.5 cell, a broken model with ' which ' loops. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | - |  | no forecast |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t11 (work-16b37f): The base model with RL-Math's top-8 directions added only in layers 22-31 at 3.0x size, with the cue, one sample per problem on the 328 harder problems: how many of 328 are right?

Unit: right answers of 328. Cell: {"model": "base Olmo-3-1025-7B + RL-Math top-8 directions in layers 22-31 only, at 3.0x", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated; seed of sample 1", "samples": 1, "grader": "not stated"}

> L22-31 x4.5, x3.0, L0-10 x0.2 (sample 1)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 155 | [152, 158] | result-e18bd8: top8 x3.0 on L22-31 = 155/328. |
| reader-2 | 155 | [152, 158] | result-e18bd8 reports 155 for the L22-31 x3.0 cell. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | - |  | no forecast |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t12 (work-16b37f): The base model with RL-Math's top-8 directions added only in layers 0-10 at 0.2x size, with the cue, one sample per problem on the 328 harder problems: how many of 328 are right?

Unit: right answers of 328. Cell: {"model": "base Olmo-3-1025-7B + RL-Math top-8 directions in layers 0-10 only, at 0.2x (norm-matched down)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated; seed of sample 1", "samples": 1, "grader": "not stated"}

> L22-31 x4.5, x3.0, L0-10 x0.2 (sample 1)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 156 | [153, 159] | result-e18bd8: top8 x0.2 on L0-10 = 156/328. |
| reader-2 | 156 | [153, 159] | result-e18bd8 reports 156 for the L0-10 x0.2 cell. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | - |  | no forecast |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t13 (work-16b37f): The base model with only the first singular direction per matrix of RL-Math's weight change added at 1.5x, with the cue, sample 0 on the 328 harder problems: how many of 328 are right?

Unit: right answers of 328. Cell: {"model": "base Olmo-3-1025-7B + first RL-Math direction per matrix only, at 1.5x", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated; seed of sample 0", "samples": 1, "grader": "not stated"}

> dir-1 x1.5 samples 0,1

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 182 | [178, 187] | result-e18bd8: direction 1 only x1.5, two samples 182 and 184 (first listed taken as sample 0). |
| reader-2 | 182 | [179, 186] | result-e18bd8 reports direction 1 at x1.5 as 182 and 184; 182 is assumed to be sample 0. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 182 | [168, 196] | one direction gave 181 at 1x and 184 at 2x; 1.5x sits between |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | 182 | [170, 194] | One direction finishes (1x 181/51, 2x 184/23) but the correctness part lies in directions 2-8, so 1.5x stays near 182. |
| round-13/s4-b | 186 | [174, 198] | The first direction carries much of the commit component: 1x 181, 2x 184; 1.5x a little above both. |
| round-13/s6-b | - |  | no forecast |

## t14 (work-16b37f): The base model with only the first singular direction per matrix of RL-Math's weight change added at 1.5x, with the cue, sample 1 on the 328 harder problems: how many of 328 are right?

Unit: right answers of 328. Cell: {"model": "base Olmo-3-1025-7B + first RL-Math direction per matrix only, at 1.5x", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated; seed of sample 1", "samples": 1, "grader": "not stated"}

> dir-1 x1.5 samples 0,1

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 184 | [179, 188] | result-e18bd8: direction 1 only x1.5, second listed sample 184. |
| reader-2 | 184 | [180, 187] | result-e18bd8 reports direction 1 at x1.5 as 182 and 184; 184 is assumed to be sample 1. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 182 | [168, 196] | same cell, second sample |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | 182 | [170, 194] | As t13, other sample. |
| round-13/s4-b | 186 | [174, 198] | As t13, other sample. |
| round-13/s6-b | - |  | no forecast |

## t15 (work-8ea654): Think-SFT (no reward) with the Code cue at T 1.0, one sample per problem on HumanEval+ and MBPP+: how many of 538 problems pass (RL-Code 401, cued base 317)?

Unit: problems passed of 538. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated; seed 51000000", "samples": 1, "grader": "not stated"}

> HumanEval+ and MBPP+ (538), Code cue and Math cue, T 1.0, 1 sample, seed 51000000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 395 | [358, 428] | Think-SFT is trained on code reasoning and beats RL on math; expected near RL-Code's 401 of 538, with risk from cap hits and code-block extraction in the raw template. |
| reader-2 | 395 | [360, 428] | Think-SFT matched or beat RL elsewhere (MMLU/BBH 342 vs 332), so it should land near RL-Code's 401 on code, less some cap hits and drift at T 1.0. |
| round-10/weights-m03 | 400 | [370, 430] | Theory: Think-SFT's imitation change carries correctness in every domain in its traces, so on code with the Code cue it sits near RL-Code (401), well above the cued base (317). |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | - |  | no forecast |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | 398 | [382, 414] | Think-SFT is a reliable reasoner (ties RL on MATH-500, beats it out of domain 342 vs 332). On an easy, reliability-bound set it reaches RL-Code's level. |

## t16 (work-8ea654): Think-SFT (no reward) with the Math cue at T 1.0, one sample per problem on HumanEval+ and MBPP+: how many of 538 problems pass?

Unit: problems passed of 538. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Math cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0; top-p and token cap not stated; seed 51000000", "samples": 1, "grader": "not stated"}

> HumanEval+ and MBPP+ (538), Code cue and Math cue, T 1.0, 1 sample, seed 51000000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 383 | [340, 420] | Same model with the Math cue on code; a math-style opening likely costs a few code-block endings relative to the Code cue. |
| reader-2 | 385 | [345, 422] | Same as the Code-cue cell; the cue matters little for Think-SFT, but the Math cue may cost a few code-block endings. |
| round-10/weights-m03 | 380 | [340, 420] | Same domain-general correctness claim, discounted for the Math cue's mismatched format on code (base Math-direction cell 368). |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | - |  | no forecast |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | 394 | [377, 411] | Reliability does not depend on the cue (base: Math cue 326 vs Code cue 317), so this lands at t15's level. |

## t17 (work-f33794): The untrained base with the cue, plurality vote over 6 samples per problem (4 stored plus 2 new) on the 328 harder problems: how many of 328 does the vote get right (vote over 4 was 192)?

Unit: right answers of 328. Cell: {"model": "base Olmo-3-1025-7B", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 6, "grader": "not stated"}

> cued base, 2 new samples per problem first (vote over 6)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 198 | [190, 207] | Cued base vote over 4 = 192 on hard328; on MATH-500, going from a vote over 4 to 6 added about 1.5 points, and readers have tended to set vote ceilings too low. |
| reader-2 | 196 | [189, 204] | The vote over 4 was 192; on MATH-500, going from 4 to 6 votes added about 1.5 points, so expect about +4 on the 328. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 198 | [189, 207] | uncapped long answers stay votable at 16,384, so 6 votes add about 6 to the 4-vote's 192 |
| round-13/s3-a | 203 | [198, 210] | hard328 has more problems with a per-sample right rate of 0.2-0.5 and spread-out wrong answers than MATH-500 does. Going from 4 to 6 samples gained +7.4 on MATH-500 (449.2 to 456.6), so expect about +9 to +11 over 192 here. |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t18 (work-8b4030): Think-SFT plus twice the RL-Math weight change, the fourth single sample (seed 3,300,000) on the 328 harder problems: how many of 328 are right (earlier samples 234, 229, 237)?

Unit: right answers of 328. Cell: {"model": "Think-SFT + 2 x (RL-Math - base), M(2)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated; seed 3,300,000", "samples": 1, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 233 | [222, 244] | M(2) samples so far 234, 229, 237 (mean 233.3); seed scatter about 5. |
| reader-2 | 233 | [222, 244] | The three earlier M(2) samples were 234, 229 and 237 (mean 233.3), with seed scatter of about ±5. |
| round-10/weights-m03 | 233 | [222, 244] | Theory: the a=2 response on Think-SFT is stable, so the fourth sample repeats the first three (234, 229, 237; mean 233). |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 233 | [222, 244] | the earlier samples were 234, 229, 237 |
| round-13/s3-a | 233 | [224, 242] | Single samples of M(2) were 234, 229 and 237; their mean, with seed scatter. |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t19 (work-8b4030): Think-SFT plus twice the RL-Math weight change, plurality vote over 4 samples per problem on the 328 harder problems: how many of 328 does the vote get right (Think-SFT alone's vote: 241)?

Unit: right answers of 328. Cell: {"model": "Think-SFT + 2 x (RL-Math - base), M(2)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated; seeds 3,000,000, 3,100,000, 3,200,000, 3,300,000", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 245 | [238, 252] | M(2) vote over 3 = 246; adding a 4th sample typically leaves it within a few problems; Think-SFT vote over 4 is 241. |
| reader-2 | 247 | [240, 254] | M(2)'s vote over 3 is 246 and a fourth sample moves a vote little (Think-SFT's votes over 3 were 231-241, over 4 was 241). |
| round-10/weights-m03 | 247 | [239, 255] | A stable, modest RL push on Think-SFT (a cut in cap hits plus slightly lower precision) keeps the vote over 3 (246) a few points above Think-SFT's vote of 241, so the vote over 4 lands about 247. |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 246 | [238, 254] | the vote over 3 was 246, and a 4th vote adds about 0-2 |
| round-13/s3-a | 250 | [246, 256] | The M(2) vote over 3 is 246. A fourth sample (about 233 right) only adds plurality wins when wrong answers are spread out, so the vote over 4 should be at or above the vote over 3. |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t20 (work-8b4030): Think-SFT plus twice the RL-Math weight change, one sample per problem on MATH-500: how many of 500 are right?

Unit: right answers of 500. Cell: {"model": "Think-SFT + 2 x (RL-Math - base), M(2)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 466 | [455, 476] | Think-SFT cue singles 457-462 on MATH-500 and a=1 transplant 467; M(2) finishes more, so mid-460s. |
| reader-2 | 467 | [457, 476] | Think-SFT cue singles score 457-462 and Think-SFT + 1x(RL-base) scored 467; the 2x transplant adds finishing. |
| round-10/weights-m03 | 465 | [455, 475] | Theory: a=2 on Think-SFT trims cap hits with a weak, non-breaking effect, so MATH-500 lands just above Think-SFT + cue's 457-462 at cap 16,384. |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | - |  | no forecast |
| round-13/s3-a | 462 | [452, 471] | Think-SFT gets 454 with one cue sample. The RL delta mostly helps answers finish under 16k (+5 to +10 on long problems). |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t21 (work-8b4030): Think-SFT plus twice the RL-Math weight change with the token cap raised to 32,768, one sample (seed 3,000,000) on the 328 harder problems: how many of 328 are right (seed 3,010,000 gave 245)?

Unit: right answers of 328. Cell: {"model": "Think-SFT + 2 x (RL-Math - base), M(2)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "cap 32,768 tokens; temperature and top-p not stated; seed 3,000,000", "samples": 1, "grader": "not stated"}

> M(2) at cap 32,768 on hard328, seed 3,000,000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 241 | [238, 244] | result-c5dafe reports M(2) cap 32,768 seed 3,000,000 = 241/328. |
| reader-2 | 243 | [234, 252] | Seed 3,010,000 at cap 32,768 gave 245 and the cap-16,384 singles were 229-237, so the raised cap adds roughly +8-10 with seed scatter of about ±5. |
| round-10/weights-m03 | 242 | [232, 252] | Theory: the RL change mainly finishes Think-SFT's long answers, so at cap 32,768 M(2) lands near the other seed's 245, adjusted for this seed's Think-SFT baseline (230 vs 234). |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 244 | [234, 254] | seed 3,010,000 gave 245 with 0 cap hits; the larger cap frees the long answers |
| round-13/s3-a | 243 | [234, 252] | Seed 3,010,000 gave 245 at cap 32,768, with 0 cap hits. A new seed adds about ±8 of scatter. |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t22 (work-c51f89): How strongly the base's MLP inputs on its own 538 Code-cue answers drive RL-Math 3.1's top-8 input subspace, as a ratio to the drive on math text (predicted 0.54; 0.40-0.70 supports f2-m03, above 0.85 refutes)?

Unit: ratio R_math (drive on code text / drive on math text). Cell: {"model": "base Olmo-3-1025-7B (forward pass; RL-Math 3.1 top-8 input subspace)", "prompt": "Code cue", "set": "538 stored base Code-cue answers (HumanEval+ and MBPP+) against math text", "n": 538, "sampling": "not stated (stored answers, no generation)", "samples": 1, "grader": "not stated"}

> drive of Math 3.1 top-8 input subspace on code text over math text (predicted 0.54)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 0.78 | [0.52, 1.02] | RL-Math directions also act on code (368 vs 331 random) and the subspace looks like general reasoning (result-3abd6f), so code drive is probably above the theory's 0.54, though still below math. |
| reader-2 | 0.72 | [0.45, 1] | The base's activations strongly drive RL's input directions, and RL-Math's directions also help on code (368 vs random 331), so the drive from code text is assumed to be well above the predicted 0.54 but below the 1.0 of math text. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | - |  | no forecast |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | 0.55 | [0.4, 0.72] | Math's top-8 input subspace is math-specific; code text drives it about half as much, and only its shared finishing part carries over. |
| round-13/s4-b | 0.92 | [0.78, 1.1] | The commit subspace is generic reasoning text, so code answers drive Math's top-8 inputs nearly as much as math text does. |
| round-13/s6-b | 0.97 | [0.84, 1.1] | The directions act on generic reasoning steps ('Okay', checks, derivations) that code answers contain in the same register; drive barely varies across texts (CV 6.8 %, result-0b3807). |

## t23 (work-c51f89): For a random rank-8 subspace as control, the ratio of the drive from the base's 538 Code-cue answers to the drive from math text.

Unit: ratio (drive on code text / drive on math text). Cell: {"model": "base Olmo-3-1025-7B (forward pass; random rank-8 subspace control)", "prompt": "Code cue", "set": "538 stored base Code-cue answers (HumanEval+ and MBPP+) against math text", "n": 538, "sampling": "not stated (stored answers, no generation)", "samples": 1, "grader": "not stated"}

> random rank-8 control

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 0.98 | [0.8, 1.18] | A random rank-8 subspace should track overall activation norm, giving a code/math ratio near 1. |
| reader-2 | 1 | [0.82, 1.18] | A random subspace's drive just tracks activation norm, which should be similar on code and math text. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | - |  | no forecast |
| round-13/s3-a | - |  | no forecast |
| round-13/s4-a | 1 | [0.85, 1.18] | A random subspace sees only overall activation energy, about equal on code and math text. |
| round-13/s4-b | 1 | [0.85, 1.18] | A random subspace has no domain preference. |
| round-13/s6-b | 1 | [0.9, 1.1] | A random subspace reads generic activation energy, which is shared across domains. |

## t24 (work-dc9359): Think-SFT with the cue at a 32,768-token cap, plurality vote over 4 samples per problem on the 136 fresh 2026 contest problems: how many of 136 does the vote get right (75 at cap 16,384)?

Unit: right answers of 136. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "cap 32,768 tokens; temperature and top-p not stated", "samples": 4, "grader": "not stated"}

> Think-SFT + cue vote over 4 at token cap 32,768 on hard328 (samples 1-3 new, sample 0 = the cap32 run) and fresh2026 (4 samples)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 81 | [74, 88] | Vote over 4 at 16k = 75; Think-SFT hits the cap on 46 % of fresh samples, so a 32k cap should add a few votes, similar to M(2) finishing more (vote 83). |
| reader-2 | 80 | [73, 87] | The vote was 75 at cap 16,384; on hard328 cap 32,768 added about 6 to the vote, and fresh2026 has more cap hits but harder late answers. |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 80 | [71, 89] | 75 at 16,384; Think-SFT's cut answers are unfinished work and resolve at 32k (as on hard328, +6 to the vote) |
| round-13/s3-a | 82 | [76, 88] | At 32k, cap hits turn into answers. The late wrong ones are scattered drift (Chinese text), so they rarely form a wrong plurality, while the right ones add up. Expect +6 to +8 over 75, more than hard328's +6 because fresh2026 has about 46 % cap hits. |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |

## t25 (work-dc9359): Think-SFT with the cue at a 32,768-token cap on the 136 fresh 2026 contest problems: the mean number right of 136 over its 4 single samples (60.0 at cap 16,384).

Unit: mean right answers of 136 per sample. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "cap 32,768 tokens; temperature and top-p not stated", "samples": 4, "grader": "not stated"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768 from the same text

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 71 | [65, 77] | Mean 60.0 at 16k with about 62 cap hits per sample; at 32k most of these finish and about 20 % come out right (hard328: 23 of 93), so about +11. |
| reader-2 | 71.5 | [65, 78] | 60.0 at 16,384 plus about 62 cap hits per sample, about 20% of which end right at 32,768 (hard328 rate 23 of 93, set lower for the harder 2026 problems). |
| round-10/weights-m03 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-13/s1-a | 66 | [59, 73] | 60.0 at 16,384; 46 % cap hits, of which about 1 in 4 are right when allowed to finish |
| round-13/s3-a | 68 | [62, 74] | About 63 cap hits per sample at 16k. Roughly 40 of them finish under 32k, and about 20-25 % end right, as Think-SFT's late answers did on hard328 (23 of 93). That gives 60 + about 8-9. |
| round-13/s4-a | - |  | no forecast |
| round-13/s4-b | - |  | no forecast |
| round-13/s6-b | - |  | no forecast |
