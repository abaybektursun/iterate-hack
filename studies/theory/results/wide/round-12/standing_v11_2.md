# Round 12 standing under engine 11.2 (scored again on a copy)

As `standing_v11_1.md` (one score per measured number, on the earliest forecast; forecasts written after their result not scored; every `measured.json` row scored or listed), plus version 11.2: a mechanism listed in `studies/theory/results/refuted.json` (its stated cause refuted by a direct test) is not carried and goes to the graveyard whatever its forecast gain. The round's own files are unchanged.

Result: 52 carried (round 12: 42), 16 in the graveyard by forecasts, 1 by a direct test; 290 forecasts excluded as written after their result.

## Forecast well, cause refuted

| mechanism | gain (nats) | distinct results | refuted claim | result | measured |
|---|---|---|---|---|---|
| run-05/f2-m06 | +7.95 | 7 | weight edits merged in bf16 are under-applied: small changes below half a unit in the last place are lost, so 1x lands smaller than intended | result-c2edfb | projection of the written 1x change on the intended addition 0.99996 (1.5x: 0.99998) |
| r5-m03-rival | not a round-12 record (a round-07 theory) | | the top-8 edit is an incomplete switch per sample: short answers are the unswitched base and about 50 % right | result-d02d46 | short answers 82.9 % right (predicted about 50 %), share 17.8 % (predicted 10-15 %) |

## Carried

| mechanism | claim | gain (nats) | distinct results | numbers | round 12 |
|---|---|---|---|---|---|
| run-06/f2-m03 | An outcome reward pays only for a gradable final answer, so its consistent gradient piles into a few singular directions that make the model complete  | +7.51 | 8 | 26 | carried, +5.19 on 10 |
| run-05/f2-m01 | The top-8 singular directions per matrix of the RL change act as a signed termination dial spread over all layers and both module families: adding the | +7.05 | 8 | 28 | carried, +6.79 on 10 |
| run-02/f2-m01 | The autobench agent works under a fixed generation time per experiment, so it buys votes by shortening each sample (its best config: 10 samples at abo | +6.69 | 7 | 11 | not carried, -1.77 on 9 |
| run-05/f2-m03 | Each direction of an RL change acts only as far as the processed text drives its input (right) singular vectors: Math-RL's top-8 input subspaces are e | +5.14 | 7 | 24 | carried, +3.74 on 9 |
| round-10/weights-m03 | The effect of an added RL change depends on the host. Think-SFT's high-rank imitation change (3.7 % of weight norm, top 8 directions hold 2 %) already | +2.00 | 5 | 9 | carried, +2.00 on 5 |
| run-03/f2-m04 | Graded accuracy depends on how a model ends its answer: whether the last thing written is the gradable marker (a boxed value, an Answer: line, the fin | +1.97 | 4 | 11 | carried, +1.97 on 4 |
| run-02/f2-m03 | The top singular directions of the RL-Math difference set when the base stops, not whether its reasoning is right: their dose sets the cap-hit rate, w | +1.78 | 3 | 3 | graveyard, -5.28 on 4 |
| run-02/f2-m04 | A capped sample gives no answer, so in a plurality vote it abstains instead of adding a wrong value. Think-SFT's vote sits near its pass@4 because its | +1.78 | 8 | 13 | carried, +2.67 on 9 |
| run-08/f2-m02 | A count 'at 16,384' rescored from a 32k run is a different measurement from a native 16k run: rows longer than 16,384 count wrong, while a native run  | +1.72 | 4 | 7 | carried, +1.72 on 4 |
| round-09/grader-m01 | Each posted single cell is one seeded draw: new seeds on the same weights scatter by 5-7 problems per 500 and up to 9-19 per 328, and cells picked as  | +1.67 | 7 | 13 | carried, +2.39 on 12 |
| run-04/f2-m05 | Long untruncated T 1.0 generations drift off-distribution (script switches into Chinese, restarted working) at a rate set by how far the prompt templa | +1.57 | 4 | 9 | carried, +1.57 on 4 |
| run-08/f2-m06 | A cap hit casts no vote: a model that runs out of tokens abstains instead of guessing, so its vote approaches pass@k (Think-SFT 241 against 244), whil | +1.56 | 5 | 7 | carried, +1.56 on 5 |
| round-09/training-m01 | Think-SFT imitated teacher traces inside its ChatML template, opened by <think> and closed by a final answer after the thinking block. Where and how i | +1.44 | 6 | 8 | carried, +1.56 on 7 |
| run-03/f2-m02 | RL's top singular weight directions raise the model's per-token hazard of committing to an answer and ending, in proportion to their size. In-domain d | +1.37 | 7 | 25 | carried, +1.81 on 9 |
| round-10/weights-m06 | Within the top-8 RL directions, the first singular direction of each matrix carries the format and stop part: it cuts cap hits, and at large size stop | +1.20 | 4 | 15 | carried, +1.20 on 4 |
| round-09/grader-m04 | A count's size depends on the set's difficulty mix: hard328's first 164 problems are much harder than its second half (cued base 65 vs 99), and fresh2 | +1.12 | 8 | 11 | carried, +0.24 on 10 |
| round-09/grader-m06 | A count at a token cap scores every unfinished answer wrong, hiding whether it was unfinished work or a dead end. Raising the cap adds right answers i | +1.12 | 7 | 10 | carried, +1.34 on 7 |
| run-08/f2-m01 | Each one-sample count is one seed's draw: the model branches at forks with fixed per-problem probabilities, so a cell has a sampling SD of about 5-6 p | +1.06 | 12 | 29 | not carried, -1.48 on 12 |
| round-09/stopping-m04 | On a hard set part of every model's answers would end past 16,384 tokens, and a cut answer scores zero. A change that leaves the length distribution i | +1.01 | 10 | 15 | carried, +0.99 on 12 |
| round-10/problems-m04 | An edit's effect splits by problem stratum: it adds right answers on mid-difficulty problems (base right in some samples), which MATH-500 and hard328  | +1.00 | 6 | 13 | carried, +1.00 on 6 |
| run-05/f2-m05 | Imitation (Think-SFT) and RL weight changes are orthogonal (cosine -0.00001) and read different input subspaces, so their effects superpose: Think-SFT | +0.85 | 4 | 9 | carried, +0.85 on 4 |
| round-09/sampling-m05 | Ending is a sampled event: at T 1.0 the stop token is drawn at each point where an answer could close, so lengths have a long tail that the cap cuts o | +0.82 | 7 | 10 | carried, +1.59 on 8 |
| run-08/f2-m05 | Majority vote counts answer strings: the base's wrong answers scatter (only about a quarter repeat), so the right answer is the plurality once per-sam | +0.80 | 5 | 6 | carried, +0.80 on 5 |
| round-10/problems-m03 | A code problem needs a short single-function artifact judged by hidden tests. The base's code deficit is mostly answers with no closed code block or c | +0.80 | 4 | 13 | carried, +0.80 on 4 |
| round-09/weights-m04 | Moved onto another model that shares the base, the RL-Math difference acts as a finishing operator on that model's own trajectories. It does not add c | +0.76 | 7 | 12 | carried, +0.25 on 8 |
| round-09/training-m04 | Pretraining fixed, for each problem, the base's distribution over final values; the cue picks which register samples it but does not move its modal va | +0.76 | 7 | 8 | carried, +0.69 on 10 |
| round-09/weights-m06 | Edit entries smaller than half a bf16 ulp of the weight they modify are written by stochastic rounding (written/intended cosine 0.585). The written ed | +0.72 | 5 | 18 | not carried, -0.15 on 8 |
| round-09/training-m02 | Think-SFT copied teacher traces produced under long budgets, and imitation carries no pressure to stop, so its 16,384-token cuts are mid-derivation wo | +0.72 | 5 | 8 | carried, +0.48 on 6 |
| run-03/f2-m03 | Whether tokens past a cap add right answers depends on whether a model's long answers are still deriving or already guessing. Think-SFT, trained by im | +0.68 | 4 | 6 | carried, +0.68 on 4 |
| round-09/stopping-m03 | The stop decision responds to the root of the summed squared singular values an edit adds per matrix, whatever its rank: one RL direction at 1x cut ca | +0.63 | 3 | 4 | graveyard, -3.84 on 6 |
| round-10/grader-m06 | Each set holds items no model can be credited on: defective or unparseable golds, LLM-transcribed 2026 statements, and problems no arm ever solves (6  | +0.63 | 5 | 8 | carried, +0.63 on 5 |
| round-10/weights-m01 | The top RL-Math directions write stop and box logits additively: signed size s shifts the log-odds that an answer runs to the cap by a roughly fixed a | +0.62 | 4 | 14 | carried, +0.62 on 4 |
| run-06/f2-m04 | On problems the base can solve, its errors are mostly per-sample slips, drawn by chance and independently at each step. Its remaining errors are misre | +0.57 | 3 | 5 | carried, +0.57 on 3 |
| round-09/training-m03 | RL-Zero's group-relative reward gives gradient only on prompts where some rollouts succeed and others fail, so early RL moves the policy on problems t | +0.53 | 3 | 4 | carried, +0.70 on 7 |
| round-09/problems-m02 | Each problem needs a derivation of a certain length. A cap hit is a cut answer, and raising the cap or adding finishing directions helps only where th | +0.53 | 4 | 6 | not carried, -0.68 on 5 |
| run-03/f2-m01 | A sample that hits the token cap casts no vote, so the cap acts as a free precision filter that discards long, low-precision answers. A vote gains mos | +0.49 | 5 | 7 | carried, +0.49 on 5 |
| round-10/problems-m06 | An RL run's finishing habit is calibrated to the derivation lengths of its training domain. Code-RL learned to close at code-answer lengths (about 4k  | +0.42 | 4 | 15 | carried, +0.42 on 4 |
| run-06/f2-m01 | Think-SFT imitates teacher traces in which every stated value is derived and the answer comes only after the work, so it rarely asserts a guess: a sam | +0.40 | 5 | 10 | carried, +0.40 on 5 |
| round-09/stopping-m02 | Think-SFT imitates teacher traces sized for a long budget, so on hard problems its natural stopping point lies beyond 16,384 tokens while the derivati | +0.37 | 4 | 7 | not carried, -0.24 on 5 |
| round-09/weights-m03 | The part of the RL difference that sets finishing is read out late: in layers 22-31 it writes the stop and hold-on token logits ('Wait', the box, EOS) | +0.33 | 3 | 4 | graveyard, -5.98 on 6 |
| round-09/problems-m05 | Competition problems (AIME, HMMT; most of hard328, all of fresh2026) are limited by finding a working plan, not by executing steps: the base's errors  | +0.33 | 11 | 23 | not carried, -0.49 on 12 |
| round-09/problems-m06 | The best size of a finishing edit depends on how many cut answers are on problems the model cannot solve. Raising the dose turns cut answers into fini | +0.31 | 3 | 4 | not carried, -1.67 on 5 |
| run-07/f2-m02 | An RL run's top weight directions write a habit for its own domain's answers. For Math-RL that habit is to deliberate, check, and finish with one boxe | +0.23 | 5 | 21 | carried, +0.36 on 6 |
| round-09/training-m05 | The largest singular direction per matrix of RL-Math's change carries the reward's most consistent signal: write the final answer in the boxed form th | +0.21 | 6 | 16 | not carried, -0.42 on 8 |
| round-10/training-m05 | Think-SFT's teacher traces cover competition problems (olympiad-style math and contest code) far more densely than the 3.1 RL prompts, which were filt | +0.19 | 5 | 10 | carried, +0.19 on 5 |
| round-09/stopping-m01 | A cut-off sample writes no answer marker, so it abstains from the plurality vote instead of voting wrong. A vote's gain over one sample therefore scal | +0.17 | 6 | 9 | carried, +0.79 on 6 |
| round-10/problems-m05 | Each set has problems that no reweighting of a host's own solution paths reaches (hard328: about 79 the base never solves even after restarts; MATH-50 | +0.14 | 5 | 13 | carried, +0.14 on 5 |
| run-05/f2-m04 | RL writes its weight change in stages: the first 100 steps move weights along the reasoning-register directions that the cue's opening also drives (st | +0.10 | 9 | 25 | not carried, -0.28 on 9 |
| round-09/sampling-m01 | Each sample is an independent draw: problem i is solved with a fixed probability p_i, so one cell's count varies by sqrt(sum p_i(1-p_i)), about 5-7 pr | +0.10 | 9 | 13 | carried, +0.26 on 12 |
| round-09/sampling-m02 | A plurality vote counts only committed answers: a cap hit or a missing answer casts no vote, so a right answer facing abstentions wins outright, while | +0.07 | 6 | 9 | carried, +0.07 on 6 |
| round-09/weights-m05 | The weight change of the first 100 RL steps is small (0.028 % of the weight norm) and points elsewhere than the final change (cosine 0.099). It moves  | +0.05 | 5 | 6 | not carried, -0.27 on 7 |
| round-10/weights-m05 | Math-RL and Code-RL directions share part of their input subspace (overlap 0.22-0.26, random 0.002), and that part writes a reward-general readout: th | +0.05 | 3 | 12 | carried, +0.05 on 3 |

## No longer carried

- round-09/training-m06: round 12 +1.45 on 7; now not carried, -0.14 on 5
- run-05/f2-m06: round 12 +7.19 on 9; now cause refuted, +7.95 on 7
- run-07/f2-m01: round 12 +0.78 on 4; now graveyard, -2.22 on 5
