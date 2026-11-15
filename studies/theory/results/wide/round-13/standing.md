# Standing, round-13

From round-12, round-11, round-10, round-09, run-02, run-03, run-04, run-05, run-06, run-07, run-08, cells-01. Gain per number: log density of the forecast minus the equal mixture of the two readers, clipped to [-3, 3] nats, at most 0 when the measured value is outside the forecast's own 90 % interval. A mechanism is scored once per measured number (board item and value), on the forecast it wrote earliest, and only when that forecast was written before the result was posted. The numbers of one board item are one experiment. Carried: total above 0 on numbers from 3 or more items; graveyard: at or below -2 on 2 or more items.

| mechanism | family | scored | items | inside | total gain | state | statement |
|---|---|---|---|---|---|---|---|
| run-05/f2-m06 | weights | 28 | 7 | 24 | +8.21 | cause refuted | Weight edits merged in bf16 are realized only where an entry's change exceeds half a unit in the last place of that weight, so small edits are thresholded onto  |
| run-06/f2-m03 | training | 29 | 10 | 25 | +6.73 | cause refuted | An outcome reward pays only for a gradable final answer, so its consistent gradient piles into a few singular directions that make the model complete the task i |
| run-02/f2-m01 | run-02 | 11 | 7 | 8 | +6.69 | cause refuted | The autobench agent works under a fixed generation time per experiment, so it buys votes by shortening each sample (its best config: 10 samples at about 1,100 t |
| run-05/f2-m01 | weights | 30 | 9 | 27 | +6.49 | cause refuted | The top-8 singular directions per matrix of the RL change act as a signed termination dial spread over all layers and both module families: adding them at size  |
| run-05/f2-m03 | weights | 24 | 7 | 21 | +5.14 | carried | Each direction of an RL change acts only as far as the processed text drives its input (right) singular vectors: Math-RL's top-8 input subspaces are excited 8-1 |
| round-09/stopping-m03 | stopping | 5 | 4 | 5 | +3.61 | graveyard (earlier round) | The stop decision responds to the root of the summed squared singular values an edit adds per matrix, whatever its rank: one RL direction at 1x cut cap hits as  |
| round-10/weights-m03 | weights | 9 | 5 | 9 | +2.00 | carried; direct test holds | The effect of an added RL change depends on the host. Think-SFT's high-rank imitation change (3.7 % of weight norm, top 8 directions hold 2 %) already sets the  |
| run-03/f2-m04 | stopping | 11 | 4 | 8 | +1.97 | cause refuted | Graded accuracy depends on how a model ends its answer: whether the last thing written is the gradable marker (a boxed value, an Answer: line, the final python  |
| round-10/weights-m06 | weights | 16 | 4 | 15 | +1.85 | carried | Within the top-8 RL directions, the first singular direction of each matrix carries the format and stop part: it cuts cap hits, and at large size stops the mode |
| run-08/f2-m02 | grader | 7 | 4 | 7 | +1.72 | carried | A count 'at 16,384' rescored from a 32k run is a different measurement from a native 16k run: rows longer than 16,384 count wrong, while a native run lets grade |
| round-09/grader-m01 | grader | 13 | 7 | 13 | +1.67 | carried | Each posted single cell is one seeded draw: new seeds on the same weights scatter by 5-7 problems per 500 and up to 9-19 per 328, and cells picked as notable (b |
| run-08/f2-m06 | grader | 7 | 5 | 6 | +1.56 | carried | A cap hit casts no vote: a model that runs out of tokens abstains instead of guessing, so its vote approaches pass@k (Think-SFT 241 against 244), while a model  |
| round-09/training-m01 | training | 8 | 6 | 7 | +1.44 | carried | Think-SFT imitated teacher traces inside its ChatML template, opened by <think> and closed by a final answer after the thinking block. Where and how it states t |
| run-08/f2-m01 | grader | 30 | 12 | 27 | +1.24 | carried | Each one-sample count is one seed's draw: the model branches at forks with fixed per-problem probabilities, so a cell has a sampling SD of about 5-6 problems on |
| run-04/f2-m05 | sampling | 10 | 5 | 10 | +1.22 | carried | Long untruncated T 1.0 generations drift off-distribution (script switches into Chinese, restarted working) at a rate set by how far the prompt template is from |
| run-03/f2-m02 | stopping | 29 | 9 | 24 | +1.22 | carried | RL's top singular weight directions raise the model's per-token hazard of committing to an answer and ending, in proportion to their size. In-domain directions  |
| round-09/grader-m04 | grader | 11 | 8 | 10 | +1.12 | carried | A count's size depends on the set's difficulty mix: hard328's first 164 problems are much harder than its second half (cued base 65 vs 99), and fresh2026 is har |
| round-09/grader-m06 | grader | 10 | 7 | 10 | +1.12 | carried | A count at a token cap scores every unfinished answer wrong, hiding whether it was unfinished work or a dead end. Raising the cap adds right answers in proporti |
| round-10/problems-m04 | problems | 14 | 6 | 13 | +1.02 | carried | An edit's effect splits by problem stratum: it adds right answers on mid-difficulty problems (base right in some samples), which MATH-500 and hard328 both hold  |
| round-09/stopping-m04 | stopping | 15 | 10 | 13 | +1.01 | carried | On a hard set part of every model's answers would end past 16,384 tokens, and a cut answer scores zero. A change that leaves the length distribution in place (1 |
| round-09/weights-m06 | weights | 20 | 6 | 17 | +0.93 | carried | Edit entries smaller than half a bf16 ulp of the weight they modify are written by stochastic rounding (written/intended cosine 0.585). The written edit is unbi |
| round-10/problems-m03 | problems | 14 | 4 | 13 | +0.91 | carried | A code problem needs a short single-function artifact judged by hidden tests. The base's code deficit is mostly answers with no closed code block or cut off, no |
| run-05/f2-m05 | weights | 9 | 4 | 8 | +0.85 | carried | Imitation (Think-SFT) and RL weight changes are orthogonal (cosine -0.00001) and read different input subspaces, so their effects superpose: Think-SFT supplies  |
| round-09/sampling-m05 | sampling | 10 | 7 | 10 | +0.82 | carried | Ending is a sampled event: at T 1.0 the stop token is drawn at each point where an answer could close, so lengths have a long tail that the cap cuts off. Raisin |
| run-08/f2-m05 | grader | 6 | 5 | 5 | +0.80 | carried | Majority vote counts answer strings: the base's wrong answers scatter (only about a quarter repeat), so the right answer is the plurality once per-sample succes |
| round-09/weights-m04 | weights | 12 | 7 | 11 | +0.76 | carried | Moved onto another model that shares the base, the RL-Math difference acts as a finishing operator on that model's own trajectories. It does not add correctness |
| round-09/training-m04 | training | 8 | 7 | 7 | +0.76 | carried | Pretraining fixed, for each problem, the base's distribution over final values; the cue picks which register samples it but does not move its modal value. A vot |
| round-09/training-m02 | training | 8 | 5 | 7 | +0.72 | carried | Think-SFT copied teacher traces produced under long budgets, and imitation carries no pressure to stop, so its 16,384-token cuts are mid-derivation work, not lo |
| round-10/grader-m06 | grader | 8 | 5 | 7 | +0.63 | carried | Each set holds items no model can be credited on: defective or unparseable golds, LLM-transcribed 2026 statements, and problems no arm ever solves (6 of MATH-50 |
| round-10/weights-m01 | weights | 14 | 4 | 13 | +0.62 | carried | The top RL-Math directions write stop and box logits additively: signed size s shifts the log-odds that an answer runs to the cap by a roughly fixed amount per  |
| run-02/f2-m06 | run-02 | 4 | 3 | 4 | +0.59 | carried | Think-SFT's difference from the base carries long derivation; the RL-Math difference carries a controller that stops once an answer is derived. The two are orth |
| run-06/f2-m04 | training | 7 | 4 | 6 | +0.58 | carried | On problems the base can solve, its errors are mostly per-sample slips, drawn by chance and independently at each step. Its remaining errors are misreadings and |
| round-09/training-m03 | training | 4 | 3 | 4 | +0.53 | carried | RL-Zero's group-relative reward gives gradient only on prompts where some rollouts succeed and others fail, so early RL moves the policy on problems the base so |
| round-09/problems-m02 | problems | 6 | 4 | 6 | +0.53 | carried | Each problem needs a derivation of a certain length. A cap hit is a cut answer, and raising the cap or adding finishing directions helps only where the cut text |
| round-10/problems-m06 | problems | 16 | 4 | 14 | +0.43 | carried | An RL run's finishing habit is calibrated to the derivation lengths of its training domain. Code-RL learned to close at code-answer lengths (about 4k tokens), s |
| run-06/f2-m01 | training | 12 | 6 | 11 | +0.41 | carried | Think-SFT imitates teacher traces in which every stated value is derived and the answer comes only after the work, so it rarely asserts a guess: a sample cut at |
| run-03/f2-m03 | stopping | 8 | 5 | 7 | +0.40 | carried | Whether tokens past a cap add right answers depends on whether a model's long answers are still deriving or already guessing. Think-SFT, trained by imitation, k |
| round-09/stopping-m02 | stopping | 8 | 5 | 6 | +0.37 | carried | Think-SFT imitates teacher traces sized for a long budget, so on hard problems its natural stopping point lies beyond 16,384 tokens while the derivation is prog |
| round-09/weights-m03 | weights | 4 | 3 | 4 | +0.33 | graveyard (earlier round) | The part of the RL difference that sets finishing is read out late: in layers 22-31 it writes the stop and hold-on token logits ('Wait', the box, EOS) straight  |
| round-09/problems-m05 | problems | 23 | 11 | 20 | +0.33 | carried | Competition problems (AIME, HMMT; most of hard328, all of fresh2026) are limited by finding a working plan, not by executing steps: the base's errors on problem |
| round-09/problems-m06 | problems | 5 | 4 | 4 | +0.31 | carried | The best size of a finishing edit depends on how many cut answers are on problems the model cannot solve. Raising the dose turns cut answers into finished ones: |
| round-09/sampling-m04 | sampling | 3 | 2 | 3 | +0.23 | not carried | A weight edit shifts every next-token logit by an amount that grows with its size. Small edits move only tokens that were already uncertain (stop, hold-on, open |
| run-05/f2-m04 | weights | 26 | 9 | 23 | +0.22 | carried | RL writes its weight change in stages: the first 100 steps move weights along the reasoning-register directions that the cue's opening also drives (step-100 cha |
| run-03/f2-m01 | stopping | 9 | 6 | 7 | +0.21 | carried | A sample that hits the token cap casts no vote, so the cap acts as a free precision filter that discards long, low-precision answers. A vote gains most over one |
| round-10/training-m05 | training | 10 | 5 | 9 | +0.19 | carried | Think-SFT's teacher traces cover competition problems (olympiad-style math and contest code) far more densely than the 3.1 RL prompts, which were filtered to pr |
| round-09/stopping-m01 | stopping | 9 | 6 | 7 | +0.17 | carried | A cut-off sample writes no answer marker, so it abstains from the plurality vote instead of voting wrong. A vote's gain over one sample therefore scales with th |
| round-10/problems-m05 | problems | 13 | 5 | 10 | +0.14 | carried | Each set has problems that no reweighting of a host's own solution paths reaches (hard328: about 79 the base never solves even after restarts; MATH-500: about 1 |
| round-09/sampling-m01 | sampling | 13 | 9 | 11 | +0.10 | carried | Each sample is an independent draw: problem i is solved with a fixed probability p_i, so one cell's count varies by sqrt(sum p_i(1-p_i)), about 5-7 problems on  |
| round-09/sampling-m02 | sampling | 9 | 6 | 8 | +0.07 | carried | A plurality vote counts only committed answers: a cap hit or a missing answer casts no vote, so a right answer facing abstentions wins outright, while one facin |
| run-07/f2-m02 | problems | 22 | 6 | 16 | +0.06 | carried | An RL run's top weight directions write a habit for its own domain's answers. For Math-RL that habit is to deliberate, check, and finish with one boxed answer;  |
| round-09/weights-m05 | weights | 6 | 5 | 5 | +0.05 | carried | The weight change of the first 100 RL steps is small (0.028 % of the weight norm) and points elsewhere than the final change (cosine 0.099). It moves the openin |
| round-10/weights-m05 | weights | 12 | 3 | 10 | +0.05 | carried | Math-RL and Code-RL directions share part of their input subspace (overlap 0.22-0.26, random 0.002), and that part writes a reward-general readout: the delibera |
| round-09/weights-m02 | weights | 4 | 3 | 3 | -0.04 | not carried | The RL-direction edit acts as a sum of small logit pushes, one from every layer and direction it contains, roughly proportional to each part's share of the edit |
| round-09/stopping-m05 | stopping | 7 | 4 | 6 | -0.09 | not carried | As an answer grows past 12,000 tokens, the terminator the model writes is less often attached to a derived result. Base and RL end long unsolved attempts by ass |
| round-09/training-m06 | training | 14 | 5 | 13 | -0.14 | not carried | The RL update is written onto features that pretraining placed in the early and middle layers: the input directions of RL-Math's top-8 change are the ones math  |
| run-06/f2-m05 | training | 13 | 6 | 10 | -0.18 | not carried | Imitation and reward write different things. Think-SFT's update, orthogonal to RL's (cosine about 0), supplies derivation quality. RL-Math's update, shaped by a |
| run-07/f2-m06 | problems | 9 | 6 | 8 | -0.22 | not carried | A problem set's hardness distribution sets how much any change can move it. fresh2026 is bimodal: most problems are beyond every 7B model's reach, and a thin mi |
| round-09/grader-m05 | grader | 9 | 6 | 8 | -0.27 | not carried | Plurality votes break ties toward the lowest sample index, so at even k a 2-2 or 1-1-1-1 split is decided by sample order, not by the answers. Odd k dissolves 2 |
| round-09/problems-m04 | problems | 6 | 5 | 5 | -0.36 | not carried | RL fixes problems in order of the length of the derivation they need. The first 100 steps install the deliberative opening and cut per-step slips, which pays on |
| run-07/f2-m04 | problems | 8 | 6 | 6 | -0.41 | not carried | Answer type sets what voting and grading can recover. Contest answers are integers from a wide range, so wrong answers scatter and a right answer with modest pe |
| round-09/sampling-m06 | sampling | 9 | 7 | 8 | -0.43 | not carried | Problems differ in solve rate far beyond binomial noise. Each arm has a block of problems it almost never samples right (base: 33 at 0 of 4 on MATH-500, against |
| run-02/f2-m03 | run-02 | 5 | 4 | 3 | -0.49 | not carried | The top singular directions of the RL-Math difference set when the base stops, not whether its reasoning is right: their dose sets the cap-hit rate, while right |
| round-09/training-m05 | training | 18 | 8 | 15 | -0.51 | not carried | The largest singular direction per matrix of RL-Math's change carries the reward's most consistent signal: write the final answer in the boxed form the verifier |
| run-05/f2-m02 | weights | 11 | 4 | 7 | -0.52 | not carried | The RL change beyond its top-8 directions is a dense per-step error reducer: it lowers the base's chance of writing a slip or misreading at each step and makes  |
| round-09/grader-m02 | grader | 19 | 8 | 16 | -0.61 | not carried | Under a plurality vote a cap hit or missing answer is an abstention, while a finished wrong answer is a vote against. A model's vote gain over its singles is se |
| run-04/f2-m01 | sampling | 6 | 4 | 4 | -0.65 | not carried | At T 1.0 / top-p 1.0 the cued base's wrong final answers are spread over many values (high answer-level entropy), while its right answers coincide. A plurality  |
| run-04/f2-m02 | sampling | 5 | 4 | 2 | -0.81 | not carried | Vote gains come in parity steps. At even k many problems end in exact ties (36 of 500 at k=4) broken by the lowest sample index, i.e. by one random draw, so an  |
| run-02/f2-m04 | run-02 | 15 | 9 | 11 | -0.83 | not carried | A capped sample gives no answer, so in a plurality vote it abstains instead of adding a wrong value. Think-SFT's vote sits near its pass@4 because its unsolved  |
| run-06/f2-m02 | training | 15 | 6 | 9 | -0.84 | not carried | Olmo 3's pretraining and midtraining mix already contains long first-person reasoning traces, so the base holds a complete deliberative register. The cue, a sel |
| round-09/problems-m01 | problems | 6 | 5 | 5 | -1.00 | not carried | Per-problem solve probability is bimodal: each model has a block of problems it essentially never solves (base 33 of 500 at 0/4, 79 of 328 with no right sample) |
| round-09/stopping-m06 | stopping | 9 | 7 | 7 | -1.05 | not carried | In the terse register the base emits end-of-text almost right after its first stated result, with no check, so terse answers end within about 1,000 tokens and a |
| round-10/stopping-m03 | stopping | 9 | 5 | 7 | -1.17 | not carried | Think-SFT was trained to end its reasoning at a </think> boundary and then write one short final answer and end-of-text. The raw template with the base's cue gi |
| round-10/stopping-m04 | stopping | 17 | 4 | 15 | -1.45 | not carried | RL's top directions shift the lm_head readout toward commit tokens (the box, end-of-text, the 'Okay' cue). The shift raises the per-token chance of ending at po |
| run-03/f2-m06 | stopping | 13 | 7 | 9 | -1.51 | not carried | Early RL (step 100) installs the deliberative 'Okay' opening on most answers but not all. Answers that miss it fall into the base's terse register and stop befo |
| run-07/f2-m03 | problems | 9 | 4 | 8 | -1.83 | not carried | MATH-500 errors split by problem. A slip is a per-step chance error that independent samples rarely repeat. A misreading is set up by how the problem is worded, |
| round-09/sampling-m03 | sampling | 10 | 6 | 8 | -2.02 | graveyard | Temperature sets how often a plain prompt opens in the deliberative 'Okay' register. At T 0.6 the first tokens collapse onto the modal opening (step 100: 478 of |
| run-07/f2-m01 | problems | 10 | 6 | 9 | -2.26 | graveyard | Each problem needs a derivation of a given length; past the 16,384 cap the answer is cut and scores zero. Extra budget or a finishing weight edit only converts  |
| run-08/f2-m04 | grader | 12 | 4 | 8 | -2.28 | graveyard | Grader v3 and the code harness score only what they extract where they look: a final 'Answer:' line or box for math, a code block for code. A template or weight |
| run-04/f2-m04 | sampling | 15 | 8 | 12 | -2.33 | graveyard | A T 1.0 run is a set of independent per-problem Bernoulli draws: the run-to-run spread of a count is sqrt(sum p(1-p)), about 5-6 problems on MATH-500 and 6 on h |
| run-07/f2-m05 | problems | 10 | 4 | 6 | -2.48 | graveyard | Too large a finishing dose makes the model stop before its derivation is complete. The cost grows with how long a derivation the problem needs: on hard328's lon |
| run-04/f2-m03 | sampling | 33 | 12 | 26 | -2.77 | graveyard | Under T 1.0 stopping is a sampled event: at each position the model draws a commit/stop token with a small hazard, so the cap-hit share is a survival probabilit |
| run-06/f2-m06 | training | 13 | 7 | 10 | -2.93 | graveyard | No model's score depends on having seen the test problems. RL's training prompts were filtered to problems the base fails, Think-SFT's data matches the test set |
| round-11/s4-b | s4 | 10 | 2 | 7 | -3.94 | graveyard | Besides finishing, the top RL directions sharpen the base toward its own most likely correct solution on problems it already solves in some samples. HumanEval+  |
| run-03/f2-m05 | stopping | 30 | 10 | 23 | -4.17 | graveyard | A trace can degenerate before it ends, into word strings, a switch to Chinese script or repeated windows, and a degenerate trace almost never ends right. The ha |
| round-09/weights-m01 | weights | 21 | 7 | 17 | -4.18 | graveyard | The commit-and-stop readout sits mainly in the top singular direction of each matrix of the RL-Math difference. The size of that one direction (its singular val |
| round-11/s2-b | s2 | 10 | 2 | 7 | -4.66 | graveyard | An RL run's task-specific policy lies almost entirely in the top-8 directions per matrix of that run's own delta, read through the inputs of its own task. So 1. |
| round-09/grader-m03 | grader | 20 | 8 | 16 | -5.04 | graveyard | An edited model is not seed-paired with the stored base: BF16 rounding of any edit changes every text, so a functionless edit lands at the edit null (random ran |
| run-02/f2-m05 | run-02 | 3 | 2 | 1 | -5.42 | graveyard | The RL-Math difference carries RL's habit of ending a long unsolved attempt with an asserted, underived number (per 1,312 hard328 samples RL finishes long and w |
| run-04/f2-m06 | sampling | 11 | 6 | 5 | -5.63 | graveyard | Adding RL-direction weight to a model concentrates its answer-level distribution: samples of one problem agree more, right or wrong. Higher dose therefore raise |
| round-09/problems-m03 | problems | 8 | 6 | 5 | -6.36 | graveyard | Easy problems need short derivations, and on them a model answers in a short register. At T 1.0 the plain prompt's terse register derails on these short problem |
| run-02/f2-m02 | run-02 | 6 | 4 | 2 | -7.26 | graveyard | The cued base's wrong answers on a problem rarely share a value: slips are per-sample chance events that land on scattered numbers, while right answers coincide |
| round-11/s6-b | s6 | 10 | 2 | 6 | -8.11 | graveyard | Overdose costs accuracy only where the edit pushes a quantity that trades against correctness past its RL optimum. Math directions carry a math-specific stop-ch |
| run-08/f2-m03 | grader | 11 | 6 | 6 | -11.06 | graveyard | The RL-direction edits add to a count mostly by converting cap hits into finished answers; the count hides the split: gain = cap hits removed x right rate on co |

## Forecast well, cause refuted

Forecast gain is not evidence for the stated cause (`studies/theory/results/refuted.json`).

| mechanism | scored | items | total gain | refuted claim | result | measured |
|---|---|---|---|---|---|---|
| run-05/f2-m06 | 28 | 7 | +8.21 | weight edits merged in bf16 are under-applied: small changes below half a unit in the last place are lost, so 1x lands smaller than intended | result-c2edfb | projection of the written 1x change on the intended addition 0.99996 (1.5x: 0.99998) |
| run-06/f2-m03 | 29 | 10 | +6.73 | an outcome reward pays only for a gradable final answer, so its gradient piles into a few singular directions; the rest of the update is diffuse | result-82eb02 | RL-Zero-General (LM-judge reward, no gradable answer) top-8 share 0.127 vs Math 3.0 0.135, Think-SFT 0.030: P = 0.685 [0.609, 0.765] (refuted if lower bound >= 0.5), n 224 matrices |
| run-02/f2-m01 | 11 | 7 | +6.69 | hard328 solutions need 6,000-14,000 tokens and short samples never reach them: under 20 % of the hard328 problems the cued base solves have a right sample of 2,000 tokens or fewer | result-ebf7a4 | hard328: 72 of 220 solved problems, 32.7 % [27.7, 38.2] (refuted if lower bound >= 20 %); median right length 3,921 tokens [3,541, 4,390]; MATH-500 control 67.5 % [63.9, 71.1] of 474 |
| run-05/f2-m01 | 30 | 9 | +6.49 | the top-8 RL-Math directions are a signed termination dial: they add finished answers, not right answers on problems the base already finishes | result-124593 | hard328, edit 1.5x on problems where a cued-base sample finished wrong: 36.4 % right vs 22.9 % for a second base sample, +13.5 points [9.7, 17.3] (RL +12.3); only 26 % of the edit's gain sits on base cap hits; at -1x finished answers 51.5 % vs base 70.0 % right |
| run-03/f2-m04 | 11 | 4 | +1.97 | on code, the RL-Math edit at 1x to 1.5x adds at least 8 finished answers with no code block, because Math's directions push a boxed ending that displaces the final python block | result-6e4536 | HumanEval+/MBPP+ 538, edit 1.5x: finished no-block 6 vs random rank-8 1.5x 23, -17 [-26, -8] (refuted if upper end < +8); vs cued base 12, -6 [-13, 1]; 0 of 538 answers hold \boxed; no Math-alone 1x code cell |
| r5-m03-rival | no forecast record in these folders | | | the top-8 edit is an incomplete switch per sample: short answers are the unswitched base and about 50 % right | result-d02d46 | short answers 82.9 % right (predicted about 50 %), share 17.8 % (predicted 10-15 %) |

## Direct test holds

- round-10/weights-m03: holds (result-3abd6f: Think-SFT's own weight change lies along RL-Math 3.1's top-8 input directions at least 2x more than a random rank-8 subspace (sharpened: and 1.5x more than the top-8 input subspaces of IF-RL, General-RL and the base matrix))

## Written after the result, not scored (290 forecasts)

| source | target | result | written | posted | mechanisms |
|---|---|---|---|---|---|
| round-09 forecasts | t04 | result-6832a8 | 2026-11-15T18:03:05 | 2026-11-15T17:54:56 | 17 |
| round-09 forecasts | t05 | result-6832a8 | 2026-11-15T18:03:05 | 2026-11-15T17:54:56 | 12 |
| round-09 forecasts | t06 | result-6832a8 | 2026-11-15T18:03:05 | 2026-11-15T17:54:56 | 13 |
| round-09 forecasts | t07 | result-6832a8 | 2026-11-15T18:03:05 | 2026-11-15T17:54:56 | 12 |
| round-09 forecasts | t08 | result-306787 | 2026-11-15T18:03:05 | 2026-11-15T18:00:54 | 25 |
| round-09 forecasts | t09 | result-306787 | 2026-11-15T18:03:05 | 2026-11-15T18:00:54 | 21 |
| round-09 forecasts | t10 | result-306787 | 2026-11-15T18:03:05 | 2026-11-15T18:00:54 | 18 |
| round-09 forecasts | t11 | result-306787 | 2026-11-15T18:03:05 | 2026-11-15T18:00:54 | 19 |
| round-09 forecasts | t12 | result-306787 | 2026-11-15T18:03:05 | 2026-11-15T18:00:54 | 19 |
| round-09 forecasts | t13 | result-d02d46 | 2026-11-15T18:03:05 | 2026-11-15T17:56:01 | 31 |
| round-09 forecasts | t14 | result-d02d46 | 2026-11-15T18:03:05 | 2026-11-15T17:56:01 | 17 |
| round-11 forecasts | t01 | result-ac7104 | 2026-11-15T20:17:21 | 2026-11-15T20:13:12 | 15 |
| round-11 forecasts | t07 | result-dd9239 | 2026-11-15T20:17:21 | 2026-11-15T20:07:48 | 11 |
| round-11 forecasts | t08 | result-dd9239 | 2026-11-15T20:17:21 | 2026-11-15T20:07:48 | 10 |
| round-11 forecasts | t09 | result-0a0a5a | 2026-11-15T20:17:21 | 2026-11-15T20:15:44 | 11 |
| round-11 forecasts | t10 | result-0a0a5a | 2026-11-15T20:17:21 | 2026-11-15T20:15:44 | 10 |
| round-11 forecasts | t11 | result-dd9239 | 2026-11-15T20:17:21 | 2026-11-15T20:07:48 | 9 |
| round-11 forecasts | t12 | result-dd9239 | 2026-11-15T20:17:21 | 2026-11-15T20:07:48 | 8 |
| run-02 forecasts | t10 | result-95a4dc | 2026-11-15T15:07:24 | 2026-11-15T15:00:31 | 3 |
| run-02 forecasts | t11 | result-95a4dc | 2026-11-15T15:07:24 | 2026-11-15T15:00:31 | 5 |
| run-02 forecasts | t12 | result-95a4dc | 2026-11-15T15:07:24 | 2026-11-15T15:00:31 | 4 |

## measured.json rows not scored

none
