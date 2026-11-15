# Forecasts, round-09

Board snapshot 2026-11-15T17:45:51 UTC, written 2026-11-15T18:03:05 UTC. 27 targets; forecasters reader-1, reader-2, run-06/f2-m03, run-02/f2-m01, run-05/f2-m03, run-05/f2-m01, run-07/f2-m02, run-05/f2-m06, run-03/f2-m02, run-02/f2-m04, run-03/f2-m05, run-04/f2-m03, round-09/stopping-m01, round-09/stopping-m02, round-09/stopping-m03, round-09/stopping-m04, round-09/stopping-m05, round-09/stopping-m06, round-09/sampling-m01, round-09/sampling-m02, round-09/sampling-m03, round-09/sampling-m04, round-09/sampling-m05, round-09/sampling-m06, round-09/weights-m01, round-09/weights-m02, round-09/weights-m03, round-09/weights-m04, round-09/weights-m05, round-09/weights-m06, round-09/training-m01, round-09/training-m02, round-09/training-m03, round-09/training-m04, round-09/training-m05, round-09/training-m06, round-09/problems-m01, round-09/problems-m02, round-09/problems-m03, round-09/problems-m04, round-09/problems-m05, round-09/problems-m06, round-09/grader-m01, round-09/grader-m02, round-09/grader-m03, round-09/grader-m04, round-09/grader-m05, round-09/grader-m06.


- run-06/f2-m03 (training, carried): An outcome reward pays only for a gradable final answer, so its consistent gradient piles into a few singular directions that make the model complete the task in the rewarded form (boxed answer, final code block) before the cap; the rest of the update is diffuse. In-domain, the top-8 directions at 1.5x reproduce nearly all of RL's gain over the cued base. Another reward's directions give about half, random rank-8 gives nothing, and 2x commits too early.

- run-02/f2-m01 (run-02, carried): The autobench agent works under a fixed generation time per experiment, so it buys votes by shortening each sample (its best config: 10 samples at about 1,100 tokens each). Most MATH-500 problems are solved in under 2,000 tokens, so short samples plus a vote score well on dev100, but hard328 solutions need 6,000-14,000 tokens and short samples never reach them. For the base, each doubling of the token budget past 8,000 buys fewer problems.

- run-05/f2-m03 (weights, carried): Each direction of an RL change acts only as far as the processed text drives its input (right) singular vectors: Math-RL's top-8 input subspaces are excited 8-11x above random by math-solution text and Code-RL's 6-9x, so an edit works in full on any problem set of its own domain and transfers to another domain in proportion to input-subspace overlap (Math with Code about 0.22-0.26, giving roughly half the in-domain effect).

- run-05/f2-m01 (weights, carried): The top-8 singular directions per matrix of the RL change act as a signed termination dial spread over all layers and both module families: adding them at size s raises, monotonically in s, the chance an answer closes with a boxed result before the cap (negative s lengthens and unboxes), and modestly raises correctness on problems already finished; past 1.5x it closes unfinished hard solutions on guesses. Random rank-8 edits and Think-SFT's directions carry no dial.

- run-07/f2-m02 (problems, carried): An RL run's top weight directions write a habit for its own domain's answers. For Math-RL that habit is to deliberate, check, and finish with one boxed answer; for Code-RL it is to reason, then finish with one final python block that passes the tests. In its own domain the top-8 edit carries about two thirds of RL's gain at 1x and nearly all of it at 1.5x. On another domain it carries about half as much.

- run-05/f2-m06 (weights, carried): Weight edits merged in bf16 are realized only where an entry's change exceeds half a unit in the last place of that weight, so small edits are thresholded onto small-magnitude weights and their effective size grows faster than nominal size (a=0.25 acts like about 0.12; top-8 at nominal 1.5 acts like RL's own top-8 share). Smaller deltas such as Code-RL's lose more at 1x and peak at a larger nominal size; trained checkpoints carry no such loss.

- run-03/f2-m02 (stopping, carried): RL's top singular weight directions raise the model's per-token hazard of committing to an answer and ending, in proportion to their size. In-domain directions therefore turn unfinished answers into finished ones and lengthen premature short ones. Overall right-of-finished stays roughly flat, because fixes on problems already finished offset guesses on converted cap hits. Past about 1.5x the hazard closes hard problems with guesses. The full RL delta added to Think-SFT acts the same way.

- run-02/f2-m04 (run-02, carried): A capped sample gives no answer, so in a plurality vote it abstains instead of adding a wrong value. Think-SFT's vote sits near its pass@4 because its unsolved samples run to the cap rather than box a guess. Anything that makes it finish, a 32k cap or the RL difference, turns abstentions into mostly wrong, scattered answers that tie or outvote lone right samples: single scores rise, vote gains shrink.

- run-03/f2-m05 (stopping, carried): A trace can degenerate before it ends, into word strings, a switch to Chinese script or repeated windows, and a degenerate trace almost never ends right. The hazard of this grows with edit size (word strings at 2-3x) and with tokens already generated (median first script switch near token 13,600). So oversized edits, and the late part of very long Think-SFT traces, lose answers. A smaller edit or a shorter trace keeps them. At T 1.0 classic loops are absent.

- run-04/f2-m03 (sampling, carried): Under T 1.0 stopping is a sampled event: at each position the model draws a commit/stop token with a small hazard, so the cap-hit share is a survival probability. RL's top-8 directions add a near-constant logit to that hazard (cap hits 96, 77, 46, 25, 5 along the dial); dose multiplies it. Where the base fails by not stopping (short code tasks, fresh contests) the dial converts unfinished samples, at precision below the base's finished answers.

- round-09/stopping-m01 (stopping): A cut-off sample writes no answer marker, so it abstains from the plurality vote instead of voting wrong. A vote's gain over one sample therefore scales with the cap-hit share times the precision of finished answers: Think-SFT (29-46 % capped, 80-88 % precise) votes near pass@4, while RL and the 1.5x edit (5-15 % capped) gain less. A longer cap turns abstentions into mostly wrong late answers, so a vote gains far less from it than one sample does.

- round-09/stopping-m02 (stopping): Think-SFT imitates teacher traces sized for a long budget, so on hard problems its natural stopping point lies beyond 16,384 tokens while the derivation is progressing; the cap cuts work in progress, not loops, and a longer cap recovers about a quarter of the cuts. Adding RL-delta weight moves the stopping point earlier: cap hits fall with dose (Think-SFT 94.5 to 33, base 77 to 5), and the cut work becomes finished answers at the host's long-problem precision.

- round-09/stopping-m03 (stopping): The stop decision responds to the root of the summed squared singular values an edit adds per matrix, whatever its rank: one RL direction at 1x cut cap hits as eight at 0.5x did (51 vs 50). So top-1 at 2x and 3x act like top-8 near 1.1x and 1.6x. Above a top-subspace energy near that of the top-8 3x edit, the model degenerates into word strings that never reach an answer marker; every target edit stays below that level.

- round-09/stopping-m04 (stopping): On a hard set part of every model's answers would end past 16,384 tokens, and a cut answer scores zero. A change that leaves the length distribution in place (100 RL steps, the cue on a checkpoint, a new seed or more samples) can move only the precision of finished answers. Step 100 writes cued-base lengths at T 1.0 (4,120 vs 4,008 tokens), so on hard problems it keeps the cued base's cap hits and adds a few right answers.

- round-09/stopping-m05 (stopping): As an answer grows past 12,000 tokens, the terminator the model writes is less often attached to a derived result. Base and RL end long unsolved attempts by asserting a number (66-73 % of long wrong answers); Think-SFT keeps working but drifts into Chinese past about 13,600 tokens and rarely finishes right (1 of 24). So late tokens and late finishes pay little, except for undrifted Think-SFT traces, and RL-delta hosts convert late work at RL's low long-answer precision.

- round-09/stopping-m06 (stopping): In the terse register the base emits end-of-text almost right after its first stated result, with no check, so terse answers end within about 1,000 tokens and are wrong on any problem needing a longer derivation. A deliberative opening, self-opening, RL training or a later hold-on word lowers that post-result stop hazard. Scores of plain-prompt cells therefore depend on how many samples stay terse; on contest problems terse samples score almost nothing.

- round-09/sampling-m01 (sampling): Each sample is an independent draw: problem i is solved with a fixed probability p_i, so one cell's count varies by sqrt(sum p_i(1-p_i)), about 5-7 problems on MATH-500 and 6-9 on the 328, and same-seed reruns give new texts because vLLM is not batch-invariant. A stored single cell is one draw. New samples land around the arm's mean, not around the stored count, and a gap of a few problems between single cells is noise.

- round-09/sampling-m02 (sampling): A plurality vote counts only committed answers: a cap hit or a missing answer casts no vote, so a right answer facing abstentions wins outright, while one facing scattered wrong values wins only through the tie rule. A model that abstains instead of guessing (Think-SFT) votes close to pass@4. Anything that turns abstentions into finished answers (a longer cap, finishing weights) raises single samples but adds wrong votes, so the vote gains less than the singles.

- round-09/sampling-m03 (sampling): Temperature sets how often a plain prompt opens in the deliberative 'Okay' register. At T 0.6 the first tokens collapse onto the modal opening (step 100: 478 of 500); at T 1.0 a share 1-q starts elsewhere (step 100: 117 of 500; base: about 400). A prefilled cue or fixed template removes that branch, so the cue's worth at T 1.0 is (1-q) times the gap between openings, which widens on harder problems.

- round-09/sampling-m04 (sampling): A weight edit shifts every next-token logit by an amount that grows with its size. Small edits move only tokens that were already uncertain (stop, hold-on, opening) and keep T 1.0 sampling coherent. Past a threshold they put mass on tokens that were near-certain, untruncated T 1.0 sampling draws them, and text decays into word strings and wrong finishes, more on long answers. The threshold follows the edit's total logit shift, so a rank-1 edit tolerates larger multiples.

- round-09/sampling-m05 (sampling): Ending is a sampled event: at T 1.0 the stop token is drawn at each point where an answer could close, so lengths have a long tail that the cap cuts off. Raising the cap finishes the cut samples, right at the rate of that model's long finished answers at the same difficulty: high for Think-SFT, whose cut answers are unfinished work, low for the base and RL, whose long answers mostly guess.

- round-09/sampling-m06 (sampling): Problems differ in solve rate far beyond binomial noise. Each arm has a block of problems it almost never samples right (base: 33 at 0 of 4 on MATH-500, against 0.5 expected) and a block where a wrong value is as likely as the right one. A vote wins only problems where the right answer is the most likely one, so it plateaus a few samples past 4, and the near-zero block caps votes on hard sets.

- round-09/weights-m01 (weights): The commit-and-stop readout sits mainly in the top singular direction of each matrix of the RL-Math difference. The size of that one direction (its singular value times the scale) sets how often the model finishes. Breakdown into word strings also depends on that per-direction size, not on how many directions are added: about 2x over-commits on long problems, and about 3x on the top direction breaks generation, whether 1 direction or 8 are scaled.

- round-09/weights-m02 (weights): The RL-direction edit acts as a sum of small logit pushes, one from every layer and direction it contains, roughly proportional to each part's share of the edit. No single layer band or direction holds the finishing effect. A part of the edit acts like the whole edit scaled to that share: one third of the layers at 1.5x behaves like the whole edit at about 0.5x, and one direction like top-8 at its norm share.

- round-09/weights-m03 (weights): The part of the RL difference that sets finishing is read out late: in layers 22-31 it writes the stop and hold-on token logits ('Wait', the box, EOS) straight into the unembedding. The changes in early and middle layers alter representations that the late readout does not use for finishing. Restricted to a layer band, the late band gives most of the dial, and the early and middle bands give little over the cued base.

- round-09/weights-m04 (weights): Moved onto another model that shares the base, the RL-Math difference acts as a finishing operator on that model's own trajectories. It does not add correctness. On Think-SFT it closes long, unfinished but sound work earlier, so cap hits fall and right-of-finished drops toward RL's level. The gain is limited by how much of the recipient's cut work was sound. Prompt or template changes on Think-SFT alone (no delta) leave its finishing rate and precision unchanged.

- round-09/weights-m05 (weights): The weight change of the first 100 RL steps is small (0.028 % of the weight norm) and points elsewhere than the final change (cosine 0.099). It moves the opening and register subspace and sharpens finished answers, but it does not contain the finishing directions that grow later. So step 100 writes deliberative answers with the cued base's cap-hit behaviour, adding the cue to it is redundant, and its lead over the cued base is small on every set.

- round-09/weights-m06 (weights): Edit entries smaller than half a bf16 ulp of the weight they modify are written by stochastic rounding (written/intended cosine 0.585). The written edit is unbiased: the intended direction comes through at full nominal size, and the rounding residue is a random edit, which is inert like the random rank-8 and noise controls. Scores therefore follow the nominal dose. The residue and GPU-dependent rounding draws add sample-to-sample spread, but they do not shift the mean.

- round-09/training-m01 (training): Think-SFT imitated teacher traces inside its ChatML template, opened by <think> and closed by a final answer after the thinking block. Where and how it states the answer is learned conditional on that template. On the raw template with the cue it reasons as well but sometimes misplaces the final answer (on the line after 'Answer:'), which v3 misses. Its own template restores the trained ending: more MATH-500 answers counted, unchanged reasoning length and cap behaviour on hard328.

- round-09/training-m02 (training): Think-SFT copied teacher traces produced under long budgets, and imitation carries no pressure to stop, so its 16,384-token cuts are mid-derivation work, not loops or guesses. More budget turns cut answers right at the problem's difficulty rate (about a quarter on hard328, fewer on 2026 problems). Late finishes are mostly wrong but scattered, so in a vote they seldom beat an existing right answer and add less than to single samples. RL's delta adds stopping, leaving fewer cuts to convert.

- round-09/training-m03 (training): RL-Zero's group-relative reward gives gradient only on prompts where some rollouts succeed and others fail, so early RL moves the policy on problems the base solves sometimes, mostly short and medium ones, and leaves problems the base rarely solves for late training. By step 100 the gain sits on MATH-500's mid-difficulty problems; on hard problems, where the cued base mostly fails or runs to the cap, step 100 plain is no better than the cued base.

- round-09/training-m04 (training): Pretraining fixed, for each problem, the base's distribution over final values; the cue picks which register samples it but does not move its modal value. A vote converges to that mode, so its ceiling is the problems whose modal value is right, and samples beyond about eight only resolve ties. The plain prompt samples pretraining's terse solution register, whose accuracy falls faster with difficulty than the cued register's, so plain's share of the cued score shrinks on harder sets.

- round-09/training-m05 (training): The largest singular direction per matrix of RL-Math's change carries the reward's most consistent signal: write the final answer in the boxed form the verifier reads, which also ends some answers. Deciding to stop deliberating on long problems is spread over the next directions. One direction therefore cuts cap hits only partly, and scaling it mostly changes answer form, not stopping: top-1 at 2x gains little over top-1 at 1x, while eight directions together act as the finishing dial.

- round-09/training-m06 (training): The RL update is written onto features that pretraining placed in the early and middle layers: the input directions of RL-Math's top-8 change are the ones math text drives most, and most of RL's change in model output comes from layers 0-15. Adding the directions only in the first or middle third therefore gives more of the hard-problem gain than the last third, whose main distinct job, writing the opening cue, is redundant when the cue is prefilled.

- round-09/problems-m01 (problems): Per-problem solve probability is bimodal: each model has a block of problems it essentially never solves (base 33 of 500 at 0/4, 79 of 328 with no right sample) and a block it solves most of the time. A plurality vote only converts problems in the narrow middle band, so vote curves plateau within a few samples at the solvable fraction; a model that abstains (cap hits) instead of answering wrong has a vote close to pass@k.

- round-09/problems-m02 (problems): Each problem needs a derivation of a certain length. A cap hit is a cut answer, and raising the cap or adding finishing directions helps only where the cut text is an unfinished correct derivation (Think-SFT: about a quarter finish right). The base's and RL's cut answers are stalled, so finishing them yields guesses (base 4 of 64). So the payoff of more budget or more finishing scales with how many cut answers hold real long derivations.

- round-09/problems-m03 (problems): Easy problems need short derivations, and on them a model answers in a short register. At T 1.0 the plain prompt's terse register derails on these short problems (plain base loses 28 points on short quartiles, none on the longest), while the deliberative register survives. Edits or prompts that install deliberation lengthen short answers on easy problems; the leftover short answers are mostly right, and the residual quick wrong answers sit on problems the cued base usually solves.

- round-09/problems-m04 (problems): RL fixes problems in order of the length of the derivation they need. The first 100 steps install the deliberative opening and cut per-step slips, which pays on short and medium problems (step-100 finished answers +4.6 points). Finishing long derivations under the cap is learned only after step 400. So early checkpoints sit near the cued base on long, hard problems and gain mainly on short ones, and the cue adds little to a checkpoint that already opens this way.

- round-09/problems-m05 (problems): Competition problems (AIME, HMMT; most of hard328, all of fresh2026) are limited by finding a working plan, not by executing steps: the base's errors on problems it never solves are wrong plans, and RL's finished wrong answers are 67 % wrong plans. RL weights and their top directions add finishing and fewer slips but no plans, so on contest sets they track RL; only imitation of long expert traces supplies plans, visible as high precision of finished long answers.

- round-09/problems-m06 (problems): The best size of a finishing edit depends on how many cut answers are on problems the model cannot solve. Raising the dose turns cut answers into finished ones: on solvable problems these are right, on unsolvable ones they are guesses that replace an abstention and, under a vote, outvote right samples. So the optimum dose is lower and the fall past it steeper on harder sets, while easy sets (MATH-500, code) show a flat top.

- round-09/grader-m01 (grader): Each posted single cell is one seeded draw: new seeds on the same weights scatter by 5-7 problems per 500 and up to 9-19 per 328, and cells picked as notable (best size, first run) sit above their model's mean. Multi-sample means regress to the pooled level of near-identical cells: step-100 plain pools with step-100 cue (same opening policy), and the 164-problem references come from draws above their own 4-sample means.

- round-09/grader-m02 (grader): Under a plurality vote a cap hit or missing answer is an abstention, while a finished wrong answer is a vote against. A model's vote gain over its singles is set by how often it abstains instead of answering wrong: Think-SFT's vote nearly equals pass@4, while RL's and the edits' lose more. Raising the cap or adding finishing weight turns abstentions into mostly wrong finished answers, so singles rise while vote gains shrink.

- round-09/grader-m03 (grader): An edited model is not seed-paired with the stored base: BF16 rounding of any edit changes every text, so a functionless edit lands at the edit null (random rank-8 cells 158-167, mean about 161 on hard328 with the cue), not at the base's 164 draw. A partial edit's count is that null plus its share of the replicated full-edit gain (200.25, not the selected 203); halves of the edit add up to the whole.

- round-09/grader-m04 (grader): A count's size depends on the set's difficulty mix: hard328's first 164 problems are much harder than its second half (cued base 65 vs 99), and fresh2026 is harder still. On hard items the opening (cue, step 100, self-opening) moves few problems, while answers past 16k tokens are mostly unfinished or guessed, so cap raises and votes yield less per abstention than on hard328, and plain prompts keep a falling share of the cued count.

- round-09/grader-m05 (grader): Plurality votes break ties toward the lowest sample index, so at even k a 2-2 or 1-1-1-1 split is decided by sample order, not by the answers. Odd k dissolves 2-2 ties, and going from 9 to 12 samples brings them back, so the base's MATH-500 vote plateaus near 453. When abstentions become finished wrong singletons (32k cap), lone right answers end up tied and lose about half the time.

- round-09/grader-m06 (grader): A count at a token cap scores every unfinished answer wrong, hiding whether it was unfinished work or a dead end. Raising the cap adds right answers in proportion to the model's share of unfinished-work cap hits: Think-SFT about one in four, RL one in ten, the base one in sixteen. Scoring the 32k text at 16,384 reproduces a 16k run, so the 32k-minus-16k difference is that yield alone.

## t01 (work-844e38): How many of the first 164 hard328 problems the RL-Zero-Math step-100 checkpoint answers right with the plain prompt, one sample at T 1.0 / top-p 1.0, cap 16,384, grader v3.

Unit: right answers of 164. Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 100", "prompt": "plain", "set": "hard328, first 164 problems", "n": 164, "sampling": "T 1.0 / top-p 1.0, cap 16,384", "samples": 1, "grader": "v3"}

> Cell m06: RL-Zero-Math step 100, plain, first 164 of hard328, 1 sample, T 1.0 / top-p 1.0, cap 16,384, v3

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 67 | [55, 79] | On MATH-500 step 100 plain (418) is level with the cued base (410), and the cued base has 65 right on these 164 against 84 for final RL, so step 100 should land near the cued base. |
| reader-2 | 70 | [57, 83] | On these 164 the cued base gets 65 and final RL 84; step 100 plain sits at or slightly above the cued base (418 vs 410 on MATH-500). |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | 68 | [59, 77] | Step 100's change is 0.028 % of the weight norm, with only 3 % of it in the final top-8 subspace, so its stop energy is negligible: cap hits stay the cued base's and the score is near 65 plus a few. |
| round-09/stopping-m04 | 69 | [60, 78] | The cued base gets 65 of these 164 with about 45 cap hits; step 100 keeps those cap hits and gains about 4.6 % on about 119 finished answers: 65 + 4. |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 68 | [59, 77] | Step 100 has almost no terse samples left (plain 418 vs cue 427 on MATH-500), so on the hard 164 it scores like the cued base (65) plus a little. |
| round-09/sampling-m01 | 67 | [56, 78] | Step 100 is level with the cued base on MATH-500; the cued base has 65 of these 164, and one sample adds sd about 6. |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | 63 | [52, 74] | 23 % of step-100 plain answers open outside 'Okay' at T 1.0; on the hardest 164 that branch keeps about 0.6 of the Okay branch's rate (0.8 on MATH-500), so step 100 falls about 4 below the cued base's parity point. |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | 63 | [52, 74] | Step 100's finished answers are about 2.25x the base's length, so on the hardest 164 more of its samples reach the 16,384 cap than the cued base's, costing a few right answers relative to MATH-500 parity. |
| round-09/sampling-m06 | 67 | [56, 78] | Step 100 mostly moves problems with mid p (5.4 points at T 0.6 on finished answers); on the hardest 164 the near-zero block is large, so it gains only a few over the cued base's 65. |
| round-09/weights-m01 | 67 | [56, 78] | Only 3.1 % of step 100's change lies in the final top-8 subspace, so it has no finishing direction and cap hits stay at the cued base's level: near 65. |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | 68 | [57, 79] | Step 100's change barely touches the final late readout (output-side top-8 overlap 0.087), so finishing stays the cued base's. |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | 67 | [56, 78] | Cued-base cap-hit behaviour (no finishing directions) plus a small sharpening of finished answers: 65 plus 1-3. |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | 66 | [56, 76] | On the first 164 the cued base gets 65; step 100's early gain is on mid-difficulty problems, which are rare here, so about +1. |
| round-09/training-m04 | 68 | [57, 79] | Step 100 plain mostly opens in the cued register (383 of 500 'Okay' at T 1.0), so near the cued base's 65 plus a small gain. |
| round-09/training-m05 | 68 | [57, 79] | Step 100 already boxes; its hard-set score sits near the cued base's 65. |
| round-09/training-m06 | 68 | [57, 79] | Step 100's change is 0.028 % of weight norm and too small in the early features to move hard problems much beyond the cued base's 65. |
| round-09/problems-m01 | 68 | [57, 79] | The first 164 hold a larger never-solved block (cued base 65, RL 84); step 100 shifts only the middle band a little above the cued base. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 68 | [57, 79] | The first 164 hard problems have few short ones, so the register effect is small; near the cued base's 65 plus a little. |
| round-09/problems-m04 | 67 | [56, 78] | The first 164 are long hard problems (cued base 65, RL 84); step 100's gain lives on short problems, so it adds only about 2. |
| round-09/problems-m05 | 68 | [57, 79] | Step 100 has the base's plans; on the 164 contest-heavy problems it stays near the cued base's 65. |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | 65 | [55, 75] | Base 65 on these 164 comes from the 164/328 draw (4-sample mean 158.5, about 2.7 high on this half); step 100 adds ~15 % of the 19-problem gap (8 of 53 on MATH-500). |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | 66 | [55, 77] | Released checkpoint, no edit null; step 100 ~ cued base plus a small share of the gap. |
| round-09/grader-m04 | 66 | [55, 77] | On this hard half the step-100 opening adds ~1-2 problems over the cued base's 65 (step 100 took 8 of 53 gap problems on MATH-500, mostly short ones). |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | 66 | [55, 77] | Step 100 at 16k has about the cued base's cap rate, so censoring costs both alike. |

## t02 (work-16773f): Right answers of 136 for the majority vote over 4 samples of the base plus 1.5x the top 8 RL-Math directions per matrix, with the cue, on the 136 fresh 2026 contest problems.

Unit: right answers of 136. Cell: {"model": "base + 1.5 x top 8 singular directions per matrix of (RL-Math - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 55 | [49, 61] | Single samples sit level with RL (sample 0 = 50, RL 50.5), but on hard328 the edit's vote gained less than RL's (214 vs 221), so the vote should land a little under RL's 57. |
| reader-2 | 55 | [48, 62] | Single samples are near RL (sample 0 = 50), and on hard328 the edit's vote gain was about two thirds of RL's, so the vote should land a little under RL's 57. |
| run-06/f2-m03 | 55 | [48, 62] | Theory: in-domain top-8 at 1.5x reproduces nearly all of RL's gain over the cued base, so the vote sits near RL's 57 (base 38), shaded slightly as on hard328 (214 vs 221). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 56 | [50, 62] | Theory: an RL-Math edit works in full on any problem set in its own domain, so the 1.5x top-8 edit should be level with RL's vote of 57 on fresh2026. Set slightly below 57 because on hard328 this edit's vote fell short of RL's (214 vs 221). |
| run-05/f2-m01 | 55 | [49, 61] | Dial at 1.5x makes the edit finish like RL (hard328 singles 200.25 vs RL 200), but its vote gained less than RL's there (214 vs 221), so the vote sits a little under RL's 57 on fresh2026. |
| run-07/f2-m02 | 55 | [48, 62] | Theory: in its own domain (math) the top-8 edit at 1.5x carries nearly all of RL's gain, so the vote over 4 should sit near RL's 57 against the cued base's 38; I put it slightly under 57 because the same edit's vote on hard328 was 214 against RL's 221. |
| run-05/f2-m06 | 53 | [47, 59] | Theory: top-8 at nominal 1.5 acts like RL's own top-8 share, so the edit sits at RL level on singles; on hard328 its vote fell 7 short of RL's (214 vs 221), so fresh2026 vote ~ RL's 57 minus ~4. |
| run-03/f2-m02 | 54 | [48, 60] | Theory: at 1.5x the higher hazard of ending turns cap hits into guesses (cap hits 14 against RL's 20-23), and wrong guesses split the vote, so the vote gains less over its singles than RL does (57 vote vs 50.5 single), as on hard328 (edit vote 214 vs RL 221). |
| run-02/f2-m04 | 56 | [50, 62] | Abstention part of the theory: the 1.5x edit finishes almost everything (14 cap hits vs RL 20-23), so its wrong finished answers vote like RL's and the vote adds only about RL's +6 over a ~50 single (RL 57 vote; edit vote on hard328 gained 14 vs RL 21). |
| run-03/f2-m05 | 56 | [48, 64] | Theory: a smaller edit keeps answers, and 1.5x is below the 2-3x word-string zone, so the edit should behave like RL; RL's vote is 57, minus a little because on hard328 the edit's vote trailed RL's (214 vs 221). |
| run-04/f2-m03 | 56 | [50, 62] | Theory: on fresh contests the dial turns unfinished samples into finished ones, but those convert at low precision, so the vote over 4 adds only modestly to the ~49 single; the hard328 vote added ~14 of 328 and RL's added 6.5 on this set. |
| round-09/stopping-m01 | 54 | [49, 59] | The edit caps about 10 % of samples, below RL's 15 % (RL vote +6.5 over single), so its vote adds about +4.5 to a single-sample mean of about 50. |
| round-09/stopping-m02 | 55 | [49, 61] | The 1.5x edit's stopping point is like RL's (14 cut samples vs RL's 20-23), so its vote is near RL's 57, a little under. |
| round-09/stopping-m03 | 55 | [49, 61] | The 1.5x edit is below collapse and stops as RL does on fresh2026 (14 cap hits). |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 54 | [48, 60] | On fresh2026 the edit finishes long answers at RL-like long precision (RL finished precision 43 %), so the vote sits just under RL's 57. |
| round-09/stopping-m06 | 55 | [49, 61] | With the cue and RL directions, no sample stays terse; the vote adds a little to about 50. |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | 55 | [49, 61] | The edit finishes like RL (14 cap hits against RL's 20-23), so its vote gain is RL's +6.5 minus a little: 50.5 + 5. |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | 55 | [49, 61] | 1.5x is below the threshold (4 samples on the 328 = RL), so the vote behaves like RL's: about +5. |
| round-09/sampling-m05 | 55 | [49, 61] | The edit's stop draws make it finish like RL; the vote gains like RL's. |
| round-09/sampling-m06 | 55 | [49, 61] | About half of fresh2026 is in the edit's near-zero block, so the vote converts only mid-p problems: about +5. |
| round-09/weights-m01 | 54 | [48, 60] | At 1.5x the edit finishes like RL, but on fresh2026 RL's finished precision is about 43 %, so the vote gains about 4-5 over the single mean. |
| round-09/weights-m02 | 55 | [49, 61] | The full edit at 1.5x is a near-complete RL-sized push; its vote gain on hard328 was about two thirds of RL's. |
| round-09/weights-m03 | 55 | [49, 61] | The full edit includes the full late readout, so it behaves like RL with a smaller vote gain. |
| round-09/weights-m04 | 55 | [49, 61] | The top-8 operator on the base finishes the base's own trajectories at RL-like precision (about 43 % on fresh), so the vote gain is modest. |
| round-09/weights-m05 | 55 | [49, 61] | As on hard328, the vote gains a bit less than RL's. |
| round-09/weights-m06 | 55 | [48, 62] | Unbiased written edit = the nominal 1.5x behaviour; the vote gains a little less than RL's. |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | 54 | [48, 60] | The 1.5x edit cuts cap hits (14 against RL's 20-23), so it abstains less than RL and its vote gains less than RL's +6.5. |
| round-09/training-m03 | 54 | [48, 60] | The edit comes from the final checkpoint, which has the late hard-problem part only partly in its top 8; vote under RL's 57. |
| round-09/training-m04 | 54 | [48, 60] | The edit's samples agree more than the base's, so voting has fewer ties to resolve than for RL; under 57. |
| round-09/training-m05 | 54 | [48, 60] | The edit finishes more than RL (14 cap hits against 20-23), so fewer abstentions and a smaller vote gain than RL's. |
| round-09/training-m06 | 54 | [48, 60] | The all-layer 1.5x edit matched RL's singles on hard328 and voted under RL; same on fresh2026. |
| round-09/problems-m01 | 54 | [48, 60] | The edit finishes most answers (few abstentions), so its vote gain over singles is like its hard328 ratio 214/200 = 1.07 applied to about 50. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | 54 | [48, 60] | The edit lacks RL's late long-derivation part, which fresh problems need, so its vote gain is a little below RL's 57. |
| round-09/problems-m05 | 54 | [48, 60] | The edit has RL's plan quality on contest problems; its wrong answers spread like RL's, so the vote lands near RL's 57 minus the hard328 shortfall. |
| round-09/problems-m06 | 54 | [48, 60] | 1.5x is past the optimum on fresh problems (hardest set): its finished guesses dilute the vote, so it stays below RL's 57. |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | 54 | [48, 60] | Single ~50; the edit abstains less than RL (14 cap hits vs 20-23), so its vote gain is about two thirds of RL's +6.5. |
| round-09/grader-m03 | 54 | [48, 60] | The edit's singles sit at RL's level; vote gain about two thirds of RL's as on hard328 (214 vs 221). |
| round-09/grader-m04 | 54 | [48, 60] | Fresh problems are hard enough that the edit's vote gain stays below RL's +6.5. |
| round-09/grader-m05 | 54 | [48, 60] | Edit finishes ~90 %, so even-k singleton ties on hard fresh problems trim its vote gain below RL's. |
| round-09/grader-m06 | 54 | [48, 60] | Few abstentions, so the vote adds less than RL's. |

## t03 (work-16773f): Mean right answers of 136 per single sample, averaged over 4 samples, of the base plus 1.5x the top 8 RL-Math directions per matrix, with the cue, on the 136 fresh 2026 contest problems.

Unit: mean right answers of 136 per sample (4 samples). Cell: {"model": "base + 1.5 x top 8 singular directions per matrix of (RL-Math - base)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "not stated (seeds of SPEC_fresh)", "samples": 4, "grader": "not stated"}

> is it level with RL (57 vote, 50.5 single)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 50 | [46, 54.5] | Sample 0 = 50; hard328 replicates had a mean equal to RL (200.25 vs 200), and RL singles on fresh2026 are 49-53. |
| reader-2 | 50 | [45.5, 54.5] | Sample 0 = 50 of 136, the RL singles are 49-53 and on hard328 the edit's singles matched RL's mean. |
| run-06/f2-m03 | 50 | [45.5, 54.5] | Theory: top-8 at 1.5x reproduces nearly all RL gain, so per-sample mean near RL's 50.5 (base 29.5); sample 0 already 50. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 50.5 | [47, 54.5] | Theory: in-domain edits work in full, so the per-sample mean equals RL's single-sample 50.5 of 136. Sample 0 already scored 50, and hard328 showed the same match (200.25 vs 200.0). |
| run-05/f2-m01 | 50.5 | [47, 54] | Dial at 1.5x matches RL's finishing and correctness per sample (hard328 200.25 vs 200), so the mean is about RL's 50.5; sample 0 already gave 50. |
| run-07/f2-m02 | 49.5 | [44.5, 54.5] | Theory: at 1.5x the edit carries nearly all of RL's gain in its own domain, so a single sample should be near RL's 50.5 (cued base 29.5); sample 0 already scored 50. |
| run-05/f2-m06 | 50 | [46.5, 54] | Theory: nominal 1.5 top-8 = RL's realized top-8 share, so per-sample accuracy = RL's 50.5 single; sample 0 already 50 of 136. |
| run-03/f2-m02 | 50 | [47, 53.5] | Theory: right-of-finished stays flat while the hazard finishes more answers, so per-sample accuracy is level with RL (singles 49-53); sample 0 already scored 50. |
| run-02/f2-m04 | 50 | [45, 55] | Finishing raises singles to RL's level: sample 0 is 50 of 136 with few cap hits, level with RL singles 49-53, so the 4-sample mean sits near 50. |
| run-03/f2-m05 | 50.5 | [46.5, 54.5] | Theory: 1.5x is below the degeneration zone, so per-sample accuracy holds at RL's level (RL single 50.5); sample 0 already gave 50 of 136. |
| run-04/f2-m03 | 49 | [45, 53] | Theory says fresh contests are where the base fails by not stopping, and the 1.5x dial converts those cap hits (sample 0: 50 right, 14 cap hits vs the base's ~55); converted samples have below-base precision, so the mean sits at RL's single 50.5 rather than above it. |
| round-09/stopping-m01 | 50 | [46.5, 53.5] | Single samples count cap hits as wrong; sample 0 had 50 with 14 cap hits, near RL's cap share and precision, so the mean stays near 50. |
| round-09/stopping-m02 | 50 | [46.5, 53.5] | Same stopping point as RL on fresh2026, so the same single-sample count (49-53). |
| round-09/stopping-m03 | 50 | [46.5, 53.5] | Sample 0 had 50; the others share its stop behaviour. |
| round-09/stopping-m04 | 50 | [46.5, 53.5] | New seeds of a fixed edit keep its length distribution (about 14 cap hits); mean near sample 0's 50. |
| round-09/stopping-m05 | 50 | [46.5, 53.5] | Same long-answer precision as RL gives RL's single 50.5. |
| round-09/stopping-m06 | 50 | [46.5, 53.5] | No terse samples under the cue; mean near sample 0's 50. |
| round-09/sampling-m01 | 50.5 | [46.5, 54.5] | Sample 0 = 50; three new draws scatter about the arm's mean (RL-level, 49-53) with sd about 5 each. |
| round-09/sampling-m02 | 50.5 | [46.5, 54.5] | Singles are finished x precision, about 122 x 0.41 per sample, as in sample 0. |
| round-09/sampling-m03 | 50.5 | [46.5, 54.5] | The cue fixes the opening, so there is no opening term; singles follow sample 0. |
| round-09/sampling-m04 | 50 | [46, 54] | Below threshold; fresh answers are long, but the edit stays coherent (sample 0 = 50). |
| round-09/sampling-m05 | 50 | [46, 54] | 122 finished per sample x 41 % (RL-like precision) = 50. |
| round-09/sampling-m06 | 50.5 | [46.5, 54.5] | The mean single is the sum of p_i, which sample 0 already estimates. |
| round-09/weights-m01 | 50 | [46, 54] | The same direction size as the hard328 cell, where four samples matched RL; sample 0 here is 50. |
| round-09/weights-m02 | 50 | [46, 54] | The full push matches RL's single samples, as on hard328. |
| round-09/weights-m03 | 50 | [46, 54] | Same readout as on hard328, where singles matched RL. |
| round-09/weights-m04 | 50 | [46, 54] | Finishing the base's trajectories reproduced RL's single score on hard328. |
| round-09/weights-m05 | 50 | [46, 54] | The final top-8 directions (not step 100's) carry finishing; at 1.5x they match RL singles. |
| round-09/weights-m06 | 49.5 | [45, 54.5] | Nominal 1.5x matches RL's mean; sample 0 = 50, and rounding draws widen the spread. |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | 50 | [46, 54] | Sample 0 = 50; singles level with RL as on hard328. |
| round-09/training-m03 | 50 | [46, 54] | Singles level with RL as on hard328; sample 0 = 50. |
| round-09/training-m04 | 50 | [46, 54] | Singles level with RL; sample 0 = 50. |
| round-09/training-m05 | 50 | [46, 54] | Singles level with RL; sample 0 = 50. |
| round-09/training-m06 | 50 | [46, 54] | Sample 0 = 50, RL singles 49-53. |
| round-09/problems-m01 | 50 | [45.5, 54.5] | Single-sample mean equals sample 0 (50) and RL's 50.5; nothing in the difficulty mix moves it. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | 50 | [45.5, 54.5] | Single samples equal RL's on fresh problems because RL's late part has low precision there. |
| round-09/problems-m05 | 50 | [45.5, 54.5] | No plans added, finishing like RL: single mean equals RL's 50.5. |
| round-09/problems-m06 | 50 | [45.5, 54.5] | Single samples are not hurt by dilution: about 50. |
| round-09/grader-m01 | 49.5 | [45.5, 53.5] | Sample 0 = 50; the hard328 replicates of this edit averaged RL's mean, so new samples scatter around RL's 50.5. |
| round-09/grader-m02 | 49.5 | [45.5, 53.5] | Singles near RL's; the vote mechanism says nothing new here. |
| round-09/grader-m03 | 49.5 | [45.5, 53.5] | Replicated edit mean equalled RL's on hard328; RL singles here 49-53. |
| round-09/grader-m04 | 49.5 | [45.5, 53.5] | Sample 0 = 50, RL singles 49-53. |
| round-09/grader-m05 | 49.5 | [45.5, 53.5] | Single samples carry no tie rule. |
| round-09/grader-m06 | 49.5 | [45.5, 53.5] | Edit has fewer cap hits (14) than RL, but its singles match RL's. |

## t04 (work-f8ecb6): Mean right answers of 500 per sample, over 4 samples (3 new plus the stored one), of the RL-Zero-Math step-100 checkpoint with the plain prompt on MATH-500 at T 1.0, grader v3.

Unit: mean right answers of 500 per sample (4 samples). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 100", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 416 | [410, 422] | Stored sample 418, shrunk slightly toward the mean because single samples of one cell spread about 13 problems. |
| reader-2 | 417 | [410, 424] | Stored step-100 plain sample is 418; the three new samples should scatter around it with a per-sample sd of about 7. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | 416 | [410, 422] | No stop shift at step 100; 4-sample mean near the stored 418. |
| round-09/stopping-m04 | 416 | [411, 421] | Unchanged lengths; three new seeds scatter around the stored 418 with shrinkage. |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 416 | [410, 422] | A small residual terse share; mean near the stored 418. |
| round-09/sampling-m01 | 417 | [411, 423] | No selection on the stored 418, so the mean is about 417 and the 3 new draws average with sd about 3.5. |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | 417 | [410, 424] | q is fixed by checkpoint and temperature, so new samples keep the stored mixture (418). |
| round-09/sampling-m04 | 417 | [411, 423] | Step 100's change is 0.028 % of the weights, far below any entropy effect; it stays at its stored level. |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 416 | [409, 423] | Step 100 has none of the finishing direction, so only sampling spread around the stored 418 is left. |
| round-09/weights-m02 | 417 | [410, 424] | Step 100's push is 0.028 % of the weight norm, about a quarter of the 1.5x edit's size and pointing elsewhere: no finishing change, only sampling spread. |
| round-09/weights-m03 | 416 | [409, 423] | No late readout at step 100: the stored 418, shrunk. |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | 416 | [409, 423] | Register plus small sharpening: the stored 418, shrunk toward 4-sample noise. |
| round-09/weights-m06 | 417 | [410, 424] | A released checkpoint, not an edit: no rounding residue, only seed spread around 418. |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | 417 | [411, 423] | MATH-500's mid problems already moved by step 100; stored 418, single-sample sd about 6. |
| round-09/training-m04 | 417 | [411, 423] | Stored 418, sd about 6 per sample. |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | 416 | [410, 422] | Single samples scatter about 7 problems from the middle band; the stored 418 shrinks toward the mean. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 416 | [410, 422] | Step 100 is in the deliberative register on most answers, so its easy-side losses are the cued base's; stored 418 shrinks. |
| round-09/problems-m04 | 416 | [410, 422] | Short-problem gain of about 6 problems over the cued base's 410.5; the stored 418 is slightly high. |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | 420 | [413, 427] | Step-100 plain 418 and step-100 cue 427 are two draws of nearly one policy (it opens with 'Okay' unprompted, and the cue moves RL checkpoints by -5 to +2); pooled mean ~421, so (418 + 3 x 421)/4 = 420. |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t05 (work-f8ecb6): Mean right answers of 500 per sample, over 4 samples (3 new plus the stored one), of the RL-Zero-Math step-100 checkpoint with the opening cue on MATH-500 at T 1.0, grader v3.

Unit: mean right answers of 500 per sample (4 samples). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 100", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 424 | [417, 431] | Stored step-100 cue sample 427, shrunk a little toward the plain cell and the mean. |
| reader-2 | 424 | [416, 431] | Stored step-100 cue sample is 427, the cue effect on step 100 is +1.8 [-1.2, 4.8], and I allow some regression toward the mean. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | 423 | [417, 429] | The cue on a checkpoint leaves lengths as they are (4,118 tokens), so its stored +9 regresses toward the plain cell. |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 424 | [418, 430] | The cue removes the last terse samples, worth about +1 to +2 points over plain. |
| round-09/sampling-m01 | 422 | [416, 428] | The +9 of the stored cue cell over plain is mostly draw noise (the cue gives -5 at step 400), so the true cue mean is about 420 and (427 + 3 x 420) / 4 = 422. |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | 423 | [416, 430] | The cue moves the 23 % non-Okay answers to the Okay branch: about +5 on average, so (427 + 3 x 422) / 4. |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 424 | [416, 431] | The cue does not touch the finishing direction, so step-100 cue stays near its stored 427, shrunk. |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | 424 | [416, 431] | The cue does not reach the late readout either: the stored 427, shrunk. |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | 423 | [415, 430] | The cue is redundant on a model that already opens deliberatively; the stored 427 shrinks toward the plain cell. |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | 424 | [417, 431] | The cue adds about 1.8 on top of step 100's mid-problem gain; stored 427 shrunk. |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | 423 | [416, 430] | Stored 427 shrinks toward the plain cell; the cue adds about 1-2 problems on the middle band. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 423 | [416, 430] | The cue moves the remaining non-deliberative answers on easy problems, about +1-2 problems. |
| round-09/problems-m04 | 423 | [416, 430] | The cue fixes the openings step 100 has not yet learned, worth about 1-2 problems; stored 427 shrinks. |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | 423 | [416, 430] | Stored 427 regresses toward the pooled step-100 level ~422: (427 + 3 x 422)/4. |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t06 (work-f8ecb6): Mean right answers of 500 per sample, over 4 samples (3 new plus the stored one), of the RL-Zero-Math step-400 checkpoint with the plain prompt on MATH-500 at T 1.0, grader v3.

Unit: mean right answers of 500 per sample (4 samples). Cell: {"model": "Olmo-3.1-7B-RL-Zero-Math checkpoint step 400", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and cap not stated", "samples": 4, "grader": "v3"}

> 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 434 | [427, 441] | Stored step-400 plain sample 436, shrunk slightly toward the mean. |
| reader-2 | 434 | [427, 441] | Stored step-400 plain sample is 436; new samples should scatter around it. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | 434 | [428, 440] | Step 400 lengths are also unchanged (4,080 tokens); its gain is in finished precision; stored 436 shrunk. |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 434 | [428, 440] | Step 400 has no terse samples (cue changes it by -1.0); mean near the stored 436. |
| round-09/sampling-m01 | 434 | [428, 440] | Pooling stored plain 436 and cue 431 (cue effect near 0) gives a mean of about 433.5; (436 + 3 x 433.5) / 4 = 434. |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | 434 | [427, 441] | At step 400 the gap between openings is about 0 (cue -1.0), so plain sits at its stored level. |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 434 | [427, 441] | By step 400 only part of the top direction has grown; the stored 436 stands. |
| round-09/weights-m02 | 434 | [427, 441] | Step 400 holds a larger push; the stored 436 stands. |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | 434 | [427, 441] | By step 400 part of the later change has arrived (+3.6 over step 100): the stored 436. |
| round-09/weights-m06 | 434 | [427, 441] | A released checkpoint: seed spread around 436. |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | 434 | [427, 441] | By step 400 more medium problems have moved (18 of 53); stored 436 shrunk. |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | 434 | [427, 441] | Stored 436 shrinks slightly. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 434 | [427, 441] | Stored 436 shrinks slightly. |
| round-09/problems-m04 | 434 | [427, 441] | Step 400 adds medium-length problems (+18 of 53 gap problems), stored 436 shrinks slightly. |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | 435 | [428, 442] | Step-400 plain 436 and cue 431 pool to ~434.5 with plain slightly ahead; (436 + 3 x 434.5)/4. |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t07 (work-f8ecb6): Difference in percentage points on MATH-500 (T 1.0, grader v3, 4 samples each) between the RL-Zero-Math step-100 checkpoint with the plain prompt and the untrained base with the cue.

Unit: points (step-100 plain minus cued base, 4 samples each). Cell: {"model": "RL-Zero-Math step 100 (plain) vs untrained base Olmo-3-1025-7B (cue)", "prompt": "plain (step 100) vs cue (base)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and cap not stated", "samples": 4, "grader": "v3"}

> so the step-100 vs cued-base difference has a 4-sample interval

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 1.1 | [-0.3, 2.5] | Expected step-100 4-sample mean of about 416 minus the cued base's 4-sample mean of 410.5, in points. |
| reader-2 | 1.3 | [-0.6, 3.2] | Expected step-100 4-sample mean of about 417 minus the cued base's 4-sample mean of 410.5, divided by 5. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | 1.1 | [-0.3, 2.5] | About 416 minus the cued base's 410.5, over 500, in points. |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 1.2 | [-0.2, 2.6] | Without a terse share, step 100 plain is about 416 against the cued base's 410.5. |
| round-09/sampling-m01 | 1.3 | [0, 2.6] | (417 - 410.5) / 5; the 4-sample means differ by sd about 4 problems. |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | 1.3 | [-0.1, 2.7] | (417 - 410.5) / 5. |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 1.2 | [-0.6, 3] | Neither arm carries the finishing direction, so the difference is register plus noise. |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | 1.2 | [-0.6, 3] | Neither arm has the readout; the difference is noise plus a small sharpening. |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | 1.1 | [-0.6, 2.8] | Small sharpening only: about 416 against 410.5. |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | 1.3 | [-0.3, 2.9] | About 417 minus 410.5, over 5. |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | 1.1 | [-0.4, 2.6] | About 416 minus the cued base's 4-sample mean 410.5, divided by 5. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 1.1 | [-0.4, 2.6] | Step 100 plain about 416 against 410.5. |
| round-09/problems-m04 | 1.1 | [-0.4, 2.6] | About +5.5 problems over 410.5, divided by 5. |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | 1.9 | [0.5, 3.3] | (420 - 410.5)/5 from the pooled step-100 plain mean against the cued base's fixed 4-sample mean. |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t08 (work-d80b27): Right answers of 328 on hard328, one sample with the cue, for the base plus the single top RL-Math direction per matrix at 2x size.

Unit: right answers of 328. Cell: {"model": "base + top 1 singular direction per matrix of (RL-Math - base) at 2x", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> one direction per matrix of RL-Math at 2x and 3x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 186 | [174, 198] | Top-1 at 1x scored 181 and top-8 at 2x scored 190; doubling one direction should finish more answers with only a small gain. |
| reader-2 | 187 | [171, 202] | Top-1 at 1x gave 181 with 51 cap hits; at 2x it should cut more cap hits, as top-8 went from 1x to 1.5x, but not reach top-8 at 1.5x (203). |
| run-06/f2-m03 | 188 | [174, 202] | Theory: the outcome-reward gradient piles into the top singular directions that make the model finish; top-1 at 2x has about the energy of top-8 at 1x (192), and k=1 at 1x already gave 181 with cap hits cut to 51. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 187 | [175, 199] | Theory: math text drives the top input direction, so on hard328 its effect scales with size. At 1x the top-1 edit scored 181; doubling it pushes toward the top-8 1x level of 192 without reaching it. |
| run-05/f2-m01 | 188 | [175, 201] | The dial rises monotonically with size: one direction at 1x already gave 181 right and 51 cap hits, so 2x closes more answers, landing near the top-8 values at 1.5-2x (190-203). |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | 190 | [176, 203] | Theory: the single top direction has small per-entry changes that bf16 thresholds heavily at 1x (181, 51 cap hits), so 2x realizes more than double, near the top-8 1x-1.5x effect (192-203). |
| run-03/f2-m02 | 188 | [176, 200] | Theory: the hazard grows with the size of the edit; one direction at 2x has roughly the norm of the 8 directions at about 1.1x, so cap hits fall below k=1's 51 and accuracy lands near k=8 at 1x (192), not past it. |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | 186 | [172, 200] | Theory: hazard grows with edit size, but one direction at 2x is a much smaller edit than 8 directions at 2x (190), so it finishes more than k=1 at 1x (181) without degenerating. |
| run-04/f2-m03 | 184 | [170, 198] | Dose multiplies the near-constant stop-hazard logit: top-1 at 1x already gives 51 cap hits (181 right); doubling it should drive cap hits to ~15-25 and convert a few at low precision, so right answers rise slightly to ~184. |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | 188 | [176, 200] | A single direction at 2x moves the base's stopping point earlier than top-1 at 1x (51 cut samples), to about 35; the converted work is right about 25 % of the time, plus a small precision gain. |
| round-09/stopping-m03 | 192 | [181, 203] | If the leading direction holds about 30 % of the top-8 energy, top-1 at 2x has the energy of top-8 at about 1.1x (192 right, 46 cap hits). |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 188 | [177, 199] | Extra finishes are long base-like answers ending in assertions, right about 20 % of the time; cap hits 51 to about 33 add about 4 to 181, plus small precision gains. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | 189 | [177, 201] | If one direction carries about a third of the top-8 energy, 2x is about top-8 at 1.15x: cap hits about 40, precision about 0.65, so about 189. |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 191 | [178, 204] | Top-1 at 1x already removed 26 of the 31 cap hits that top-8 removed; doubling the top direction lands near top-8 at 1.5-2x for finishing. |
| round-09/weights-m02 | 189 | [177, 201] | Top-1 at 1x acted like top-8 at about 0.6-0.8x; at 2x it acts like top-8 at about 1.2-1.5x, partly offset by the right-rate loss seen at high doses. |
| round-09/weights-m03 | 187 | [175, 199] | The top-1 direction includes the late readout direction; at 2x it cuts more cap hits than top-1 at 1x (181). |
| round-09/weights-m04 | 187 | [175, 201] | A partial operator: more finishing than top-1 at 1x (181/51), no added correctness. |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | 186 | [173, 199] | Top-1 entries are smaller, so more of them are rounded, but the edit stays unbiased: the nominal 2x of one direction, between top-1 at 1x (181) and top-8 at 1.5x. |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | 186 | [173, 199] | A larger dose of one direction finishes more answers on problems the base sometimes solves; between k=1 at 1x (181) and top-8 at 1.5x (203). |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | 185 | [173, 197] | Top-1 at 1x gave 181/51 cap; doubling it mostly converts the remaining unboxed endings, a few more finishes: about +4. |
| round-09/training-m06 | 186 | [173, 199] | One direction per matrix in all layers at 2x reaches the early features at double size; between 181 and 203. |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 187 | [174, 200] | Doubling one direction finishes some of top-1's 51 cut base answers, but they are stalled base derivations, so only a few are right. |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | 187 | [174, 200] | One direction of the early finishing part at 2x cuts some cap hits on long problems without the late skill. |
| round-09/problems-m05 | 187 | [174, 200] | RL directions add finishing, not plans: a few more right on hard328. |
| round-09/problems-m06 | 187 | [174, 200] | Top-1 at 2x is still below the hard328 optimum: it converts some of 51 cut answers, about a third right. |
| round-09/grader-m01 | 185 | [172, 198] | Top-1 at 1x was 181 (one draw); doubling adds finishing, partly offset by regression of a single draw. |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | 184 | [171, 197] | Top-1 at 1x is null + 20; at 2x it finishes more (top-8 went 46 -> 25 cap hits from 1x to 1.5x), +3 to +5. |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t09 (work-d80b27): Right answers of 328 on hard328, one sample with the cue, for the base plus the single top RL-Math direction per matrix at 3x size.

Unit: right answers of 328. Cell: {"model": "base + top 1 singular direction per matrix of (RL-Math - base) at 3x", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> one direction per matrix of RL-Math at 2x and 3x

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 178 | [150, 200] | At 3x, top-8 collapsed to 117, but one direction carries less norm, so expect a mild decline from 2x with a long tail toward breakage. |
| reader-2 | 180 | [146, 206] | Larger size could finish more answers or start to degrade, as top-8 did at 3x (117); I made the interval wide for that. |
| run-06/f2-m03 | 180 | [155, 203] | Theory's finishing directions plus '2x commits too early': top-1 at 3x is about as large as top-8 at 1.5x but all in one direction, so it should push toward committing too early and fall below the 1.5x top-8 score of 203. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 179 | [156, 200] | Same in-domain drive as t08, but at 3x the single direction's norm is about that of top-8 at 1.5x and concentrated in one direction. The board's dial shows overdrive breaks the model (top-8 at 3x scored 117), so the interval is wide on the low side. |
| run-05/f2-m01 | 182 | [160, 200] | At 3x the dial is past 1.5x, so it closes unfinished hard solutions on guesses; one direction carries less norm than top-8 at 3x (117, broke), so it degrades less. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | 184 | [160, 203] | Theory: effective size grows faster than nominal, so top-1 at 3x is realized about like top-8 at 1.5-2x (190-203), with a risk of overshoot and decay like top-8 at 3x (117), hence the wide low side. |
| run-03/f2-m02 | 183 | [165, 200] | Theory: one direction at 3x pushes the hazard past the ~1.5x-equivalent level, where it closes hard problems with guesses, so right answers fall a little below the 2x cell. |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | 172 | [145, 196] | Theory: at 3x the edit enters the word-string zone (8 directions at 3x fell to 117); a single direction is smaller, so it loses some answers to degeneration, not most. |
| run-04/f2-m03 | 178 | [155, 198] | Tripling the top-1 hazard shift leaves almost no cap hits; the converted answers have low precision, and at 3x there is some risk of decay like top-8 at 3x (117), so roughly level with 2x but with a wider interval. |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | 196 | [183, 208] | Top-1 at 3x has the energy of top-8 at about 1.6x (203 at 1.5x, 190 at 2x), a third of the collapse level, so no word strings and about 15-25 cap hits. |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 186 | [170, 201] | At 3x most cut answers end with an asserted number (as the top-8 2x edit: 14 of 77 right), so right answers stay near those at 2x. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | 189 | [168, 208] | At 3x the rank-1 edit's total shift is about top-8 at 1.7x, below the 2x point that stayed coherent: cap hits about 15, precision about 0.61, so about 189. |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 160 | [128, 190] | At 3x the top direction has the same size as in the top-8 3x edit, which broke (117), so partial breakdown is expected. |
| round-09/weights-m02 | 192 | [174, 210] | Top-1 at 3x carries only about half the top-8 norm times 3, equal to top-8 at about 1.4x, which scored 203; nowhere near the norm at which top-8 broke. |
| round-09/weights-m03 | 180 | [150, 205] | A larger readout push over-commits; breakdown risk is wide. |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | 180 | [150, 206] | Nominal 3x on one direction; the rounding residue adds no damage, so the outcome rests on the nominal dose, with a wide breakdown range. |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | 179 | [150, 203] | Past 2x, overshoot starts to cost; wide for the breakage seen at top-8 3x. |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | 178 | [151, 202] | At 3x the format direction overshoots like top-8 at 3x's top component; mild decline, wide tail for breakage. |
| round-09/training-m06 | 179 | [150, 203] | At 3x early-layer features are pushed far enough to start to distort; wide tail. |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 186 | [168, 201] | One direction at 3x carries about as much squared norm as eight at 1.5x, so it finishes more without breaking; converted cut answers are mostly guesses. |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | 185 | [167, 201] | At 3x one direction still adds no plans and finishes most answers without breaking. |
| round-09/problems-m06 | 186 | [168, 201] | Top-1 at 3x is near the dose where top-8 peaked (squared norm comparable to top-8 at 1.5x minus the precision part), so no collapse. |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | 178 | [150, 202] | At 3x one direction still carries less norm than top-8 at 2x but starts to cost precision; wide tail toward breakage. |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t10 (work-d80b27): Right answers of 328 on hard328, one sample with the cue, for the base plus the top 8 RL-Math directions at 1.5x added only in layers 0-10.

Unit: right answers of 328. Cell: {"model": "base + top 8 singular directions per matrix of (RL-Math - base) at 1.5x, layers 0-10 only", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> the 8 directions at 1.5x in layers 0-10, 11-21, 22-31 only

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 176 | [162, 190] | All layers at 1.5x gave 203 against base 164; a third of the layers should give part of the gain, and early MLP layers carry a large share of the KL. |
| reader-2 | 174 | [159, 190] | The edit's weight is flat across layers, so one third of the layers should carry a partial share of the 164 -> 203 gain. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 176 | [163, 190] | Theory: math text drives Math-RL's input subspaces about equally in every layer band (8.1-11.2x). So each third of the layers should carry roughly a third of the all-layer 1.5x gain: base 164 to 203, with some redundancy. |
| run-05/f2-m01 | 175 | [162, 190] | The dial is spread over all layers, so one third of the layers gives a partial dial, roughly size 0.5 overall (170/50 cap hits), short of 1.5x at all layers (203). |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | 177 | [163, 192] | Theory: per-entry thresholding is the same as in the all-layer 1.5x edit (realized = RL's top-8 share), but only a third of the layers carry it, so about a third to half of the +39 gain over base 164. |
| run-03/f2-m02 | 172 | [158, 186] | Theory: the hazard is proportional to the size of the edit, so one third of the layers gives about a third of the 1.5x hazard, close to the size-0.5 cell (170 right, 50 cap hits). |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | 173 | [160, 187] | If the 8 directions add a roughly additive stop-hazard logit across layers, one third of the layers at 1.5x is about a 0.5x dose, which scored 170 right with 50 cap hits. |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | 172 | [160, 184] | A third of the layers gives about half the push of the full 1.5x edit (like 0.5x: 170/50). |
| round-09/stopping-m03 | 172 | [160, 184] | Contributions from different layers add linearly in the residual stream, so a third of the layers at 1.5x acts like the whole edit at 0.5x (170, 50 cap hits). |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 172 | [161, 184] | Partial finishing push; converted long answers right about 20 % of the time. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | 173 | [160, 187] | One third of the layers gives about a third of the logit shift, like the 0.5x all-layer dial (170), far below threshold. |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 175 | [162, 188] | Each third holds its own layers' top directions at 1.5x, so each gets a partial share of the 164 to 203 gain. |
| round-09/weights-m02 | 172 | [159, 185] | One third of the push at 1.5x = the whole edit at about 0.5x, which scored 170 with 50 cap hits. |
| round-09/weights-m03 | 166 | [154, 178] | Early layers hold no finishing readout: near the cued base's 164 plus a small share. |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | 175 | [161, 189] | Entries in the edited layers are written exactly as in the all-layer edit: a nominal partial share. |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | 181 | [168, 194] | The early third holds a large share of the RL-driven change (layers 0-15 carry twice the KL of 16-31); about 40 % of the 164-to-203 gain. |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 172 | [159, 186] | A third of the layers is roughly half the finishing dose (0.5x gave 170 with 50 cap hits). |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | 172 | [159, 186] | A third of layers is a sub-optimal dose on hard328: about half the finishing gain. |
| round-09/grader-m01 | 174 | [161, 187] | One third of the replicated 1.5x gain over the edit null; one draw, SD ~6. |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | 173 | [160, 186] | Null 161 + one third of the replicated gain (200.25 - 161 = 39), additive as attention-only and MLP-only were (17 + 20 = 37). |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t11 (work-d80b27): Right answers of 328 on hard328, one sample with the cue, for the base plus the top 8 RL-Math directions at 1.5x added only in layers 11-21.

Unit: right answers of 328. Cell: {"model": "base + top 8 singular directions per matrix of (RL-Math - base) at 1.5x, layers 11-21 only", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> the 8 directions at 1.5x in layers 0-10, 11-21, 22-31 only

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 178 | [164, 192] | Partial share of the all-layer gain (164 to 203) from the middle third. |
| reader-2 | 177 | [162, 193] | Middle-layer third gets a partial share of the 164 -> 203 gain; the best-attributed neurons sat in layers 1-15. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 177 | [163, 191] | Theory: input drive is similar across layer bands (8.1-11.2x), so layers 11-21 alone carry about a third of the 1.5x edit's gain over the base (164 to 203). |
| run-05/f2-m01 | 176 | [162, 190] | The dial is spread over all layers, so the middle third alone gives a partial dial between base 164 and the full 1.5x 203. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | 178 | [164, 193] | Theory: per-entry thresholding is the same as in the all-layer 1.5x edit, applied to a third of the layers, so about a third to half of the +39 gain (half-module splits gave 178-181). |
| run-03/f2-m02 | 172 | [158, 186] | Theory: the hazard is proportional to the size of the edit, so one third of the layers gives about a third of the 1.5x hazard, close to the size-0.5 cell (170 right, 50 cap hits). |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | 173 | [160, 187] | Same additive-hazard reading: a third of the layers at 1.5x is about a 0.5x dose (170/50); nothing in the theory makes the middle layers special. |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | 174 | [162, 186] | Same partial shift of the stopping point. |
| round-09/stopping-m03 | 173 | [161, 185] | Same 0.5x-equivalent push. |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 174 | [162, 186] | Same. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | 174 | [161, 188] | Same sub-threshold third of the shift. |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 176 | [163, 189] | A partial share of the dial from the middle layers' top directions. |
| round-09/weights-m02 | 172 | [159, 185] | Same share: about the 0.5x whole-edit cell. |
| round-09/weights-m03 | 171 | [159, 183] | The middle layers feed the readout weakly: a small share of the gain. |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | 177 | [163, 191] | A nominal partial share. |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | 179 | [166, 192] | The middle third covers layers 11-15 of the heavy band plus mid layers: about 38 % of the gain. |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 174 | [161, 188] | Same half-dose reading for the middle third. |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | 174 | [161, 188] | Middle third, partial finishing. |
| round-09/problems-m06 | 174 | [161, 188] | Same partial dose. |
| round-09/grader-m01 | 175 | [162, 188] | As t10; no seed reason to favour a third. |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | 174 | [161, 187] | Null 161 + about a third of 39. |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t12 (work-d80b27): Right answers of 328 on hard328, one sample with the cue, for the base plus the top 8 RL-Math directions at 1.5x added only in layers 22-31.

Unit: right answers of 328. Cell: {"model": "base + top 8 singular directions per matrix of (RL-Math - base) at 1.5x, layers 22-31 only", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> the 8 directions at 1.5x in layers 0-10, 11-21, 22-31 only

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 180 | [165, 195] | The late layers hold the finishing and 'Okay'/'Wait' readout directions, so a slightly larger share of the gain is expected there. |
| reader-2 | 180 | [163, 197] | Late layers carry the finishing/deliberation readouts, so a slightly larger share of the 164 -> 203 gain. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 175 | [161, 190] | Theory: input drive is similar across layer bands, so layers 22-31 alone carry about a third of the 1.5x edit's gain over the base (164 to 203). |
| run-05/f2-m01 | 175 | [162, 190] | The dial is spread over all layers, so the last third alone gives a partial dial between base 164 and the full 1.5x 203. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | 176 | [162, 192] | Theory: per-entry thresholding is the same as in the all-layer 1.5x edit, applied to a third of the layers, so about a third to half of the +39 gain over base 164. |
| run-03/f2-m02 | 172 | [158, 186] | Theory: the hazard is proportional to the size of the edit, so one third of the layers gives about a third of the 1.5x hazard, close to the size-0.5 cell (170 right, 50 cap hits). |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | 172 | [159, 186] | Same additive-hazard reading as the other layer thirds (about a 0.5x dose, 170/50); late layers hold the readable deliberation directions but get no extra weight under the theory. |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | 176 | [164, 188] | Same partial shift, slightly larger in late layers, which read out the stop words. |
| round-09/stopping-m03 | 175 | [163, 187] | Same push, slightly more where stop words are read out. |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 176 | [164, 188] | Same, slightly larger late-layer push. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | 176 | [163, 190] | Same, plus slightly more direct shift of the stop and hold-on logits from the last layers. |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 177 | [164, 190] | A partial share from the late layers' top directions. |
| round-09/weights-m02 | 172 | [159, 185] | Same share; no late-layer premium in a sum of pushes. |
| round-09/weights-m03 | 189 | [176, 202] | The late third holds most of the stop/hold-on readout, so it gives most of the 164 to 203 gain. |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | 179 | [165, 193] | A nominal partial share. |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | 172 | [159, 186] | The late third carries the least of RL's output change, and its cue-writing role is redundant with the prefilled cue: about 20 % of the gain. |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 176 | [162, 190] | Late layers write the finishing tokens, a little more cap-hit cut. |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | 176 | [162, 190] | Late-layer finishing at partial dose, no plans: part of 164 -> 203. |
| round-09/problems-m06 | 177 | [163, 191] | Late layers write the finishing readout, slightly more of the gain. |
| round-09/grader-m01 | 175 | [162, 188] | As t10. |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | 173 | [160, 186] | Null 161 + a third of 39; the edit's weight is flat across layers and module splits add linearly, so no third gets a bonus. |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t13 (work-22359d): Mean right answers of 500 per sample, over 4 samples (3 new plus the stored one), of the base plus 1x the top 8 RL-Math directions per matrix with the plain prompt on MATH-500 at T 1.0.

Unit: mean right answers of 500 per sample (4 samples). Cell: {"model": "base + 1x top 8 singular directions per matrix of (RL-Math - base)", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and cap not stated", "samples": 4, "grader": "not stated"}

> base + 1x top-8 RL-Math directions, plain, MATH-500, T 1.0, 3 new samples (4 with the stored one)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 425 | [418, 432] | Stored sample 427, shrunk slightly toward the mean. |
| reader-2 | 426 | [418, 434] | Stored sample is 427 of 500; new samples should scatter around it. |
| run-06/f2-m03 | 428 | [419, 437] | Theory: the top-8 directions carry RL's finishing form at 1x; the stored plain sample is 427, so the 4-sample mean stays near it. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 426 | [417, 435] | Theory: the edit works in full on MATH-500, which is in-domain, so new samples should repeat the stored 427 of 500 (plain prompt, 1x top-8). The interval allows sample-to-sample spread. |
| run-05/f2-m01 | 426 | [417, 435] | The 1x dial raises finishing and adds a little correctness; on MATH-500 the 4-sample mean stays near the stored 427 (sd about 7 per sample). |
| run-07/f2-m02 | 433 | [420, 446] | Theory: at 1x the top-8 edit carries about two thirds of RL's gain in its own domain; because the edit writes the deliberate-and-box habit, I measure that gain from the cued base, giving 410 + 2/3 x (463 - 410) = about 445, then pull toward the stored sample's 427, which is one of the four. |
| run-05/f2-m06 | 425 | [414, 435] | Theory: top-8 at nominal 1x is thresholded below RL's top-8 share, so it stays well under RL 463; the stored sample is 427 and the 4-sample mean regresses slightly. |
| run-03/f2-m02 | 425 | [417, 433] | Theory: at 1x the hazard converts unfinished answers while right-of-finished stays flat, so new samples repeat the stored 427 with slight regression. |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | 425 | [415, 435] | Theory: a 1x edit on short MATH-500 traces carries almost no degeneration hazard, so new samples repeat the stored 427. |
| run-04/f2-m03 | 426 | [416, 436] | Theory treats the edit's effect as a fixed shift in the stop hazard at T 1.0, so new samples land where the stored sample did (427, plain) and only sampling noise is added. |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | 425 | [419, 431] | Top-8 at 1x is far below collapse; 4-sample mean near the stored 427. |
| round-09/stopping-m04 | 425 | [419, 431] | Top-8 plain has mean tokens near the cued base's (3,962); seed scatter around the stored 427. |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 424 | [418, 430] | Top-8 plain leaves about 10-15 % of samples terse, which lose about half of their problems; 4-sample mean just under the stored 427. |
| round-09/sampling-m01 | 426 | [420, 432] | Stored 427 was not selected; the 4-sample mean sits near it with sd about 3.5. |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | 426 | [419, 433] | The top-8 edit writes the opening on its own (q about 0.86 at T 1.0), so plain gives a stable mixture near 427. |
| round-09/sampling-m04 | 426 | [420, 432] | 1x is below threshold; stays near the stored 427. |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 426 | [419, 433] | The finishing direction at 1x on the plain prompt: the stored 427 stands. |
| round-09/weights-m02 | 426 | [419, 433] | 1x of the push on the plain prompt: the stored 427 shrunk. |
| round-09/weights-m03 | 426 | [419, 433] | All layers at 1x: the stored 427. |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | 426 | [419, 433] | The final top-8 holds the register switch (430 of 500 open with 'Okay') plus finishing; on the plain prompt the stored 427 stands. |
| round-09/weights-m06 | 426 | [419, 433] | The same written edit as the stored run (add_norm equal), so new samples scatter around 427. |
| round-09/training-m01 | 425 | [418, 432] | The top-8 edit writes RL's boxed ending, which v3 reads, so no format loss; stored 427 shrunk to the mean. |
| round-09/training-m02 | 425 | [418, 432] | Few cuts on MATH-500; stored 427 shrunk to the mean. |
| round-09/training-m03 | 425 | [418, 432] | MATH-500 is mostly mid-difficulty problems that the RL directions move; stored 427. |
| round-09/training-m04 | 425 | [418, 432] | The plain prompt with the 8 directions mostly opens in the deliberative register (430 of 500 open 'Okay'); stored 427 shrunk. |
| round-09/training-m05 | 425 | [418, 432] | Top-8 writes the boxed ending on the plain prompt, which v3 reads; stored 427 shrunk. |
| round-09/training-m06 | 425 | [418, 432] | On the plain prompt the late layers' cue writing matters, and top-8 includes it; stored 427 shrunk. |
| round-09/problems-m01 | 424 | [417, 431] | Stored 427 shrinks toward the mean by about 3. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 424 | [417, 431] | Its losses are about 22 quick terse answers on easy problems per sample, which recur at a steady rate; stored 427 shrinks by about 3. |
| round-09/problems-m04 | 424 | [417, 431] | The top-8 edit carries the early part (opening, finishing) not the late long-derivation part; stored 427 shrinks. |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | 424 | [417, 431] | 1x on MATH-500 is on the flat top; stored 427 shrinks. |
| round-09/grader-m01 | 425 | [418, 432] | Stored 427 is an unselected planned cell; mild regression toward ~424. |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | 425 | [418, 432] | New samples of the same edit, already above its null; stored 427 regresses slightly. |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t14 (work-22359d): How many of the 2,000 samples (4 per MATH-500 problem) of the base plus 1x the top 8 RL-Math directions, plain prompt, T 1.0, are at most 1,000 tokens long.

Unit: samples of at most 1,000 tokens, of 2,000. Cell: {"model": "base + 1x top 8 singular directions per matrix of (RL-Math - base)", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and cap not stated", "samples": 4, "grader": "not stated"}

> readout of short samples (<=1,000 tokens) by cued-base solve bin

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 500 | [300, 720] | The plain and cued base often answer in under 1,000 tokens, while top-8 lengthens short answers toward RL (median right answer about 3,000 tokens), so about a quarter of samples. |
| reader-2 | 450 | [260, 690] | Rough length estimate: the cued base has a median of about 1,400 tokens and the edit lengthens short answers, so roughly 20-25 % of samples should be at most 1,000 tokens. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 320 | [160, 520] | Theory: most MATH-500 problems are solved in under 2,000 tokens. The cued base has 263 of 500 answers at or under 2,000 tokens, and the top-8 edit lengthens short answers toward RL, so about 16% of the 2,000 samples should be at or under 1,000 tokens. |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 300 | [170, 450] | The dial closes answers yet lengthens short ones (p10 rose 32-72% on hard328), so short samples fall below the cued base's share, to about 15% of 2,000. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | 430 | [270, 600] | Theory: 1x top-8 is realized only partway toward RL's share, so the short-answer share sits between the cued base (~33% at or under 1,000 tokens) and RL (~10%): ~21% of 2,000. |
| run-03/f2-m02 | 400 | [260, 560] | Theory: the directions lengthen premature short answers (p10 rose 32% at 1x on hard328), so far fewer samples stay at or under 1,000 tokens than for the cued base; about 20% of samples. |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | 450 | [320, 600] | A higher stop hazard means some samples stop early; the edited model opens like the cued base (median right answer ~1,400 tokens, most answers under 2,000), and lengthening of short answers keeps the share under 1,000 tokens at about 22% of 2,000. |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | 480 | [330, 640] | At 1x energy the stop shift lengthens the shortest answers only modestly (hard328 p10 +32 %), so short-sample counts stay near a quarter. |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 500 | [340, 660] | Short samples are the terse ones (about 12 % of 2,000, mostly under 1,000 tokens) plus deliberative answers to the easiest problems (about 13 %). |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | 430 | [310, 550] | About 14 % of samples open in the terse register, about 80 % of them under 1,000 tokens (225), plus about 12 % of the Okay-branch samples (205). |
| round-09/sampling-m04 | 460 | [330, 590] | A coherent 1x edit lengthens short answers (p10 +32 % on the 328) without making text decay, so the short share drops from the base's about 30 % to about 23 %. |
| round-09/sampling-m05 | 460 | [320, 600] | Short samples are the early end of the stop-time distribution; the edit makes stopping less likely before a check, removing about a quarter of the base's short answers. |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | - |  | no forecast |
| round-09/weights-m02 | 470 | [310, 640] | A partial push lengthens short answers part of the way toward RL's length (p10 up 32 % at 1x on hard328), so about a quarter stay at or under 1,000 tokens. |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | 490 | [320, 660] | The register part of top-8 puts most answers in the deliberative mode, but about 12 % stay in the short plain register, giving about a quarter of answers at or under 1,000 tokens. |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | - |  | no forecast |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | 460 | [300, 640] | About 14 % of answers stay in the terse plain register, mostly under 1,000 tokens (about 200), plus about 15 % of the lengthened deliberative answers (about 260). |
| round-09/training-m05 | 460 | [300, 640] | The boxed RL-style answers are longer; short answers come from the minority still in the plain register. |
| round-09/training-m06 | 460 | [300, 640] | Answers that the late layers fail to open in the deliberative register stay short. |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 450 | [300, 620] | About 27 % of MATH-500 is Levels 1-2; top8 lengthens those (p10 +32 % on hard328) but 10-15 % of answers stay in the terse plain register, so about 22 % of samples are at most 1,000 tokens. |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | 480 | [290, 680] | MATH-500 is easy-heavy: ~70 non-'Okay' plain-register answers per 500 mostly short plus ~18 % of the lengthened Okay answers, ~120 per 500. |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | - |  | no forecast |

## t15 (work-8b2ec9): Right answers of 328 on hard328 for Think-SFT prompted in its own ChatML chat format with <think>, one sample at T 1.0 with a 32,768-token cap, grader v3.

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 232 | [215, 248] | Think-SFT with the cue scores 230 at cap 32,768; its own chat template should be about as good. |
| reader-2 | 232 | [215, 248] | Think-SFT with the cue at cap 32,768 scored 230; its native template should be about as good. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 228 | [212, 244] | Theory: hard328 solutions need 6,000-14,000 tokens, which a long cap reaches. Starting from Think-SFT's cap-32k cue run (230), its native template should score about the same. |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | 228 | [213, 243] | A 32k cap makes Think-SFT finish its cut answers, so the single score rises as in the paired cue run (207 at 16k to 230 at 32k); the native template is assumed to be neutral. |
| run-03/f2-m05 | 224 | [206, 241] | Theory: the late part of long Think-SFT traces degenerates (median script switch near token 13,600), so going from 16k to 32k adds about 20 problems, not every cut answer (the cue run had 207 -> 230). |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 231 | [217, 245] | One sample at 32k: the abstentions now answer and about a quarter are right, as in the cue run (230). |
| round-09/stopping-m02 | 233 | [219, 247] | The native template asks for the same trace-length policy the model was trained on, so the 32k count matches the cue run (230), with slightly cleaner endings. |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 229 | [215, 243] | Drift comes from the weights' long-context behaviour, not the template: about 74 % of cut traces are undrifted and finish right about 32 % of the time, so 32k gives about +22 over about 207. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | 231 | [218, 244] | One draw of a model whose cue cell at 32k is 230; a template change of a few problems is inside one sample's spread. |
| round-09/sampling-m02 | 233 | [219, 247] | At 32k nearly every sample finishes; single = finished x precision, as in the cue run (230). |
| round-09/sampling-m03 | 232 | [218, 246] | <think> fixes the opening, like the cue, so the score is the cue run's (230) plus template noise. |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | 236 | [222, 250] | In its own template the end-of-thinking marker is in-distribution, so stops at completion points are more likely and fewer answers wander until 32k: a few above the cue run's 230. |
| round-09/sampling-m06 | 232 | [218, 246] | The template does not change which problems are out of reach; the same near-zero block gives the cue run's level. |
| round-09/weights-m01 | - |  | no forecast |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | 231 | [215, 247] | There is no delta, so finishing and precision are Think-SFT's own; the template does not change them; the cue run gave 230. |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | 235 | [221, 249] | Same reasoning length as the cue run (230 at 32k, mean single about 210 + 23 at 32k), plus 1-2 answers whose ending is now read. |
| round-09/training-m02 | 233 | [219, 247] | Mean single at 16k about 210, plus about 23 converted cuts at 32k as in the cue run. |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 231 | [216, 246] | In its native format Think-SFT still writes long real derivations; at 32k about 25 % of cut answers finish right, as with the cue (230). |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | 231 | [216, 246] | Plans come from the weights, not the template; native format equals the cue's 230. |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | 231 | [215, 247] | Cue run at 32k 230 had a 16k count of 207 against a 4-sample mean of 209, so a fresh draw is ~232 for the cue; the template is a minor change. |
| round-09/grader-m02 | 232 | [216, 248] | Single-sample count; abstention does not act without a vote. |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | 232 | [216, 248] | Same set and cap as the cue run (230); template change small. |
| round-09/grader-m05 | 232 | [216, 248] | Single count. |
| round-09/grader-m06 | 232 | [216, 248] | 16k level ~209 plus Think-SFT's yield of ~23 (one in four of ~93 cut answers). |

## t16 (work-8b2ec9): Right answers of 328 on hard328 for Think-SFT in its own ChatML format with <think>, one sample at T 1.0, counting only answers that finish within 16,384 tokens, grader v3.

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p not stated; generated at cap 32,768, scored at cap 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 205 | [188, 222] | The cue run scored 207 at cap 16,384; the native template may think longer, which could mean slightly more cap hits. |
| reader-2 | 205 | [186, 222] | The cue run counted at 16,384 scored 207 (23 below its 32k score); the native thinking format may run a bit longer. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 212 | [196, 228] | Theory: hard328 solutions sit at 6,000-14,000 tokens, so most right answers survive a 16,384 cutoff. Board pairing: 207 at 16k against 230 at 32k for the cue run, so I keep most of t15. |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | 206 | [192, 220] | Scored at 16k, unfinished answers abstain and count as wrong, so this sits at the cue run's 16k level (207; singles 201-212). |
| run-03/f2-m05 | 203 | [186, 220] | Theory: answers cut at 16,384 are lost and long traces carry the switch hazard; level with Think-SFT's stored 16k counts (203 plain, 207-219 cue). |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 206 | [192, 220] | Scored at 16k, the cut samples count as wrong; about 29 % capped, 88 % precise. |
| round-09/stopping-m02 | 205 | [190, 220] | The native traces may run a little longer, so a few more are cut at 16k than the cue run's 207. |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | 206 | [192, 220] | Counting at 16k reproduces a 16k cap: about 29 % cut, 88 % precise. |
| round-09/stopping-m05 | 206 | [191, 221] | Same as the cue run counted at 16k. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | 206 | [193, 219] | The same answers counted at 16,384, like the cue run's 207; one-sample sd 6-7. |
| round-09/sampling-m02 | 205 | [191, 219] | Counted at 16k the cut answers count as abstentions, as in the cue run's 207. |
| round-09/sampling-m03 | 206 | [192, 220] | Same fixed opening; counted at 16k as in the cue run (207). |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | 209 | [195, 223] | Fewer samples run past 16,384 than in the cue run (93), so the 16k count sits a little above 207. |
| round-09/sampling-m06 | 205 | [191, 219] | Same block structure, counted at 16k. |
| round-09/weights-m01 | - |  | no forecast |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | 206 | [190, 222] | The same finishing rate as the cue run at 16k (207). |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | 206 | [191, 221] | Cap behaviour is that of the cue run (207 at 16k), so the 16k count is unchanged apart from a point of format recovery. |
| round-09/training-m02 | 204 | [189, 219] | Native thinking is at least as long as the cued one, so slightly more cuts at 16k than the cue run's 207. |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 204 | [188, 220] | Same derivations, counted at 16k; native thinking plus a separate answer adds a few cut answers. |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | 204 | [188, 220] | Same plans counted at 16k, about 207 less a cut answer or two. |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | 207 | [191, 223] | Think-SFT 16k singles 201-212, mean 209; one draw. |
| round-09/grader-m02 | 207 | [191, 223] | Single count at 16k, as the cue run (207). |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | 207 | [191, 223] | 16k count of the same set. |
| round-09/grader-m05 | 207 | [191, 223] | Single count at 16k. |
| round-09/grader-m06 | 208 | [192, 224] | t15 minus the ~23-answer yield; the template does not change censoring. |

## t17 (work-8b2ec9): Right answers of 500 on MATH-500 for Think-SFT prompted in its own ChatML chat format with <think>, one sample at T 1.0 with a 32,768-token cap, grader v3.

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 463 | [450, 474] | Think-SFT cue singles are 454-462 at cap 16,384; the longer cap and the native format add a few. |
| reader-2 | 465 | [452, 476] | Think-SFT cue singles at 16k are 454-462 on MATH-500, plus a few answers that finish past 16k. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 460 | [448, 471] | Theory: MATH-500 is solved in under 2,000 tokens, so the cap does not matter. Value from Think-SFT single-sample base rates of 457-462. |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | 461 | [449, 472] | On MATH-500 few Think-SFT samples are capped (about 25), so finishing them at 32k adds only a few right answers over the cue singles of 454-462. |
| run-03/f2-m05 | 462 | [450, 472] | Theory: MATH-500 traces are short, so the extra cap adds little beyond the cue's 454-462 at 16k; few traces reach the degeneration zone. |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 463 | [454, 471] | On MATH-500 about 25 cut samples, a few of which finish right by 32k. |
| round-09/stopping-m02 | 465 | [456, 473] | Only about 25 MATH-500 traces outrun 16k; about a quarter finish right past it: 459 + 5. |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 463 | [454, 471] | Few MATH-500 traces pass 13k, so drift and late assertion barely matter: +4 over 16k. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | 463 | [453, 473] | Think-SFT singles are 454-462 at 16k, plus about 3 that finish past 16k. |
| round-09/sampling-m02 | 463 | [452, 474] | Few abstentions on MATH-500; 16k singles plus a few late finishes. |
| round-09/sampling-m03 | 463 | [452, 474] | Fixed opening; cue singles plus late finishes. |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | 465 | [455, 475] | Few MATH-500 answers reach 16k; those that finish later are mostly right for Think-SFT. |
| round-09/sampling-m06 | 463 | [452, 474] | Few MATH-500 problems are in Think-SFT's near-zero block; singles about 463. |
| round-09/weights-m01 | - |  | no forecast |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | 464 | [452, 475] | Precision is unchanged and the longer cap finishes a few more; the native layout may also fix the about 4 'Answer:'-line misses. |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | 468 | [459, 477] | Cue singles 457-462 at 16k, plus about 6 from finishing at 32k (25 cap hits, about a quarter right), plus about 3 of the 4 per sample v3 misses on the raw template. |
| round-09/training-m02 | 466 | [456, 475] | MATH-500 has about 25 cuts at 16k; about a quarter turn right at 32k, about +6 over the 16k singles. |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | 465 | [454, 475] | Think-SFT's 16k singles about 460 plus finishing at 32k. |
| round-09/training-m05 | 465 | [454, 475] | Think-SFT's native ending is its own format, not RL's box; 16k singles about 460 plus finishing at 32k. |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 465 | [453, 475] | MATH-500 cap hits (about 25 per sample) are mostly unfinished long derivations; 32k recovers about 6 of them over the 16k singles 454-462. |
| round-09/problems-m03 | 465 | [453, 475] | Native Think-SFT keeps its long register on easy problems; its few easy-side misses remain. |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | 465 | [453, 476] | Single count; Think-SFT cue singles 457-462 plus a few late finishes. |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | 465 | [453, 476] | MATH-500 has few long answers; 32k adds ~5. |
| round-09/grader-m05 | 465 | [453, 476] | Single count. |
| round-09/grader-m06 | 466 | [455, 477] | ~25 cut answers on MATH-500 at 16k, about a third finish right at 32k on these easier problems: 459 + 7. |

## t18 (work-8b2ec9): Right answers of 500 on MATH-500 for Think-SFT in its own ChatML format with <think>, one sample at T 1.0, counting only answers that finish within 16,384 tokens, grader v3.

Unit: right answers of 500. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p not stated; generated at cap 32,768, scored at cap 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 458 | [444, 470] | Think-SFT cue singles at cap 16,384 are 454-462. |
| reader-2 | 459 | [446, 470] | Matches the Think-SFT cue singles of 454-462 at cap 16,384. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 458 | [446, 469] | Theory: MATH-500 answers are short (under 2,000 tokens), so scoring at a 16,384 cap removes almost nothing from t17. |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | 456 | [443, 468] | At 16k the capped samples abstain, so this lands at the Think-SFT cue single level of 454-462, a few below the 32k count. |
| run-03/f2-m05 | 458 | [446, 469] | Theory: short MATH-500 traces mostly finish before the switch hazard, so 16k loses only a few answers compared with 32k. |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 459 | [449, 468] | Equal to the Think-SFT cue singles at 16k (454-462). |
| round-09/stopping-m02 | 459 | [449, 468] | At 16k the score equals the Think-SFT singles. |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | 459 | [449, 468] | Same for MATH-500 at 16k. |
| round-09/stopping-m05 | 459 | [449, 468] | Equal to the Think-SFT 16k singles. |
| round-09/stopping-m06 | 459 | [449, 468] | Think-SFT in its own template is never terse; same as its 16k singles. |
| round-09/sampling-m01 | 458 | [448, 468] | Mean of the Think-SFT cue singles at 16k. |
| round-09/sampling-m02 | 458 | [447, 469] | Cue singles at 16k. |
| round-09/sampling-m03 | 458 | [447, 469] | Fixed opening; cue singles at 16k. |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | 459 | [448, 470] | Cue singles at 16k, with the native stop structure. |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | - |  | no forecast |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | 459 | [446, 470] | Think-SFT cue singles at 16k are 454-462. |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | 463 | [453, 472] | Cue singles average about 460 at 16k; the trained ending recovers about 3 of the 16 in 74 wrong answers that had the gold on the next line. |
| round-09/training-m02 | 460 | [449, 470] | At 16k the cut answers count as wrong, as in the cue singles 457-462. |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | 460 | [448, 470] | Close to the cue singles 457-462 at 16k. |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 459 | [447, 470] | At 16k it equals the cue singles. |
| round-09/problems-m03 | 459 | [447, 470] | Same, counted at 16k. |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | 459 | [447, 470] | Single count at 16k. |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | 459 | [447, 470] | Think-SFT singles 457-462 at 16k. |
| round-09/grader-m05 | 459 | [447, 470] | Single count. |
| round-09/grader-m06 | 459 | [447, 470] | 16k count equals a 16k run: Think-SFT singles 457-462. |

## t19 (work-60f040): Right answers of 500 on MATH-500 for a majority vote over 9 samples of the untrained base with the opening cue at T 1.0, grader v3.

Unit: right answers of 500. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0 (same cell as the stored 4 samples); top-p and cap not stated", "samples": 9, "grader": "v3"}

> vote over 9 = 456 [449, 462] of 500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 453 | [446, 460] | Vote over 4 = 446, and the published majority curve adds about 2-3 points from 4 to 8 samples. |
| reader-2 | 452 | [446, 458] | Vote over 4 is 446 and pass@4 467; the vote curve flattens (Wang majority@8 about 91 %). |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 455 | [447, 462] | Theory: MATH-500 problems are short, so a vote over more samples keeps paying. From the base's vote over 4 = 446 and pass@4 = 467, a vote over 9 should reach about 455. |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 454 | [448, 460] | The cued base caps only about 5 % of MATH-500 samples, so extra samples add votes mostly on finished slips; the gain from 4 to 9 samples is about +8. |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | 454 | [448, 460] | More samples leave each sample's length distribution unchanged, so the base's roughly 33 never-solved problems and its cut answers stay lost; the vote rises a few problems above 446. |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 454 | [448, 460] | The cue removes terse stops; the cued base's early answers are right 95 % of the time (250 of 263), so votes can only work on its long answers: a few problems over 446. |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | 454 | [448, 460] | The cued base's misses at 4 are 4-way ties and 2-2 splits; 9 samples break most of them (about +6), and agreeing wrong values hold the rest. |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | 452 | [447, 457] | The 4-sample vote (446) misses 21 problems with a right sample: about 6 are ties that 9 samples settle; agreeing wrong groups and the 33 at 0 of 4 stay. |
| round-09/weights-m01 | - |  | no forecast |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | 452 | [446, 458] | The base lacks the later finishing and sharpening directions, so voting only removes scattered errors and plateaus. |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | 452 | [446, 458] | The base's cued 'Answer:' line is read correctly (121 of 132 right), so voting gains only from agreement, about +6 from 446. |
| round-09/training-m02 | 452 | [446, 458] | The base's cuts are few at T 1.0 (about 22 per sample), so its vote gain comes from agreement, not abstention: about +6 from 446. |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | 452 | [446, 458] | The vote over 4 (446) loses about 6-8 to ties; 9 odd samples resolve most of them toward the mode; pass@4 467 is not reachable. |
| round-09/training-m05 | 452 | [446, 458] | The base's 'Answer:' lines are read correctly; the vote gains from ties only. |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | 451 | [445, 457] | Vote 4 = 446, pass@4 467; 33 never-solved problems stay out and only the middle band (about 20 problems) converts, roughly a quarter of it from 4 to 9 samples. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 452 | [446, 458] | Easy-side quick errors are per-sample and are voted away by 4 samples already; more samples add little. |
| round-09/problems-m04 | 452 | [446, 458] | Voting the cued base recovers part of what step 100 adds on short problems, not the late part. |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | 453 | [446, 461] | The base abstains on ~5 % of MATH-500 samples, so extra votes convert only problems where the right answer is the plurality; pass@4 467 caps it, 0-of-4 excess (33) stays. |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | 454 | [447, 461] | MATH-500's easy majority is already won at k=4; extra votes act on ~40 mid-difficulty problems. |
| round-09/grader-m05 | 453 | [446, 460] | Odd k removes most of the 36 tie problems of k=4; random-equivalent resolution of those gives ~+5 over 446, plus a few plurality conversions. |
| round-09/grader-m06 | - |  | no forecast |

## t20 (work-60f040): Right answers of 500 on MATH-500 for a majority vote over 12 samples of the untrained base with the opening cue at T 1.0, grader v3.

Unit: right answers of 500. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0 (same cell as the stored 4 samples); top-p and cap not stated", "samples": 12, "grader": "v3"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 455 | [448, 462] | Vote over 4 = 446; the curve flattens above 9 samples. |
| reader-2 | 454 | [447, 460] | Small further gain over the vote over 9 as the curve plateaus. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 457 | [449, 464] | Theory: a vote over short samples scores well on MATH-500. Going from 9 to 12 samples adds about 2 more problems as the vote nears its plateau. |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 455 | [449, 461] | Few abstentions to fill in; 3 more samples add about 1 problem. |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | 455 | [449, 461] | Same ceiling; plateau. |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 455 | [449, 461] | Same; plateau. |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | 456 | [450, 462] | Three more samples resolve about 2 more ties; even counts bring back a few 2-way ties. |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | - |  | no forecast |
| round-09/sampling-m06 | 453 | [448, 458] | The plateau is reached: three more samples move about 1 problem. |
| round-09/weights-m01 | - |  | no forecast |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | - |  | no forecast |
| round-09/weights-m05 | 454 | [448, 460] | The plateau continues. |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | 454 | [448, 460] | Small further tie resolution beyond 9 samples; no format effect. |
| round-09/training-m02 | 454 | [448, 460] | Little left to gain beyond 9 samples. |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | 454 | [448, 460] | Plateau at the modal-right count; 12 adds about 2 over 9. |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | 452 | [446, 458] | From 9 to 12 samples the middle band is nearly exhausted; at most 1-2 more problems. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 453 | [447, 459] | Same plateau. |
| round-09/problems-m04 | 453 | [447, 459] | Plateau of the same. |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | 454 | [447, 461] | Small further gain over vote of 9 as plurality settles. |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | 455 | [448, 462] | Plateau on the easy-heavy set. |
| round-09/grader-m05 | 453 | [446, 460] | Even k=12 reopens 6-6 and 5-5 ties resolved by sample order, cancelling the small gain of three more samples. |
| round-09/grader-m06 | - |  | no forecast |

## t21 (work-8b4030): Right answers of 328 on hard328 for a majority vote over 4 samples of Think-SFT plus twice the RL-Math weight change.

Unit: right answers of 328. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 251 | [241, 260] | M(2) singles are 234 and 229; on fresh2026 the vote added about 8 points over singles, so expect about 7 points here. |
| reader-2 | 249 | [237, 260] | Singles are 234 and 229; the vote gain should be smaller than Think-SFT's +32 because M(2) abstains less, as on fresh2026 (+11 vs +15). |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 247 | [237, 257] | Theory: the RL change acts in full on in-domain math text, so the transplant's gain carries over to the vote. On fresh2026 the 2x transplant's vote led Think-SFT's by 8 (83 vs 75), and Think-SFT's hard328 vote is 241, giving about 247. |
| run-05/f2-m01 | 246 | [237, 255] | The RL change at 2x carries the dial: it cuts Think-SFT's cap hits (94.5 to 54), so the vote gains less than Think-SFT's +32 over a single sample; about +15 over singles of about 231. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | 249 | [239, 258] | Theory: at a=2 the bf16-merged delta is realized beyond nominal and makes Think-SFT finish (singles 229-234). The vote gain is smaller than Think-SFT's +32 because fewer samples abstain (fresh2026 vote gain 0.7x Think-SFT's). |
| run-03/f2-m02 | 246 | [236, 256] | Theory: the full RL delta on Think-SFT raises the hazard the same way, so Think-SFT stops abstaining and guesses more; the vote over its singles (about 231) gains less than Think-SFT's +32, closer to M(2)'s +11 on fresh2026. |
| run-02/f2-m04 | 246 | [236, 256] | The RL difference turns abstentions into scattered wrong answers: singles rise to about 232 (234, 229) but the vote gain shrinks from Think-SFT's +32 to roughly half (on fresh2026 the gain fell from +15 to +11). |
| run-03/f2-m05 | 247 | [237, 257] | Theory: the RL change shortens Think-SFT's traces (cap hits 94 -> 54) and so keeps answers from late degeneration; singles about 231, with a smaller vote gain than Think-SFT's (+32) because there are fewer abstentions (fresh2026: +11). |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 249 | [240, 258] | M(2) caps about 16 % on hard328 (Think-SFT 29 %) with 72 % precision, so its vote gain is about two thirds of Think-SFT's +32 relative to singles: 231.5 + about 18. |
| round-09/stopping-m02 | 250 | [241, 259] | With the earlier stopping point, M(2) has fewer cut samples to abstain, so its vote gain over 231.5 is smaller than Think-SFT's. |
| round-09/stopping-m03 | 250 | [241, 259] | 2x the full delta has top-subspace energy like top-8 at 2x: strong finishing, no collapse in the Think-SFT host (234 and 229 singles). |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 249 | [240, 259] | Long M(2) answers carry RL-like assertions, so its wrong values scatter and the vote still filters them; about +17 over singles. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | 250 | [240, 260] | M(2) abstains less than Think-SFT (about 50 against 89 cap hits), so its vote gain is about 0.7 of Think-SFT's +32: 231.5 + 19. |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | 251 | [241, 261] | a=2 is below threshold for Think-SFT (a=4 still 213, coherent), so its vote behaves like a finishing model's. |
| round-09/sampling-m05 | 251 | [241, 261] | M(2)'s stop draws finish more answers than Think-SFT's, so fewer abstentions feed the vote: gain about +19. |
| round-09/sampling-m06 | 250 | [240, 260] | M(2) singles 229-234; the vote converts mid-p problems, but the near-zero block (about 70 problems) caps pass@4 near 258. |
| round-09/weights-m01 | 248 | [237, 259] | 2x the full delta contains the top direction at 2x: Think-SFT finishes more, abstains less, so its vote gain is smaller than Think-SFT's +32. |
| round-09/weights-m02 | 249 | [238, 260] | 2x the whole delta adds a finishing push to Think-SFT; fewer abstentions shrink the vote gain to about 18 over the singles. |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | 248 | [237, 259] | Singles about 231.5. With cap hits cut from 94.5 to about 54, fewer samples abstain, so the vote gain is about 70 % of Think-SFT's +32 (fresh2026 ratio 10.75/15). |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | 249 | [238, 260] | The RL delta added to Think-SFT's weights is rounded onto them unbiased; the noise control (209) shows the residue is inert, so nominal a=2 gives its singles plus a reduced vote gain. |
| round-09/training-m01 | 249 | [239, 259] | M(2) runs on the raw template, so no format change; singles 234/229 plus a vote gain smaller than Think-SFT's because M(2) abstains less. |
| round-09/training-m02 | 248 | [238, 258] | M(2) has about 54 cuts per sample against Think-SFT's 94.5, so fewer abstentions: vote/single ratio about 0.92 of Think-SFT's 1.15, about 245-250 from singles near 232. |
| round-09/training-m03 | 249 | [239, 259] | Singles 234/229; the vote converts problems with intermediate solve rates. |
| round-09/training-m04 | 249 | [239, 259] | The RL delta concentrates answers, so fewer ties to resolve than for Think-SFT; about +17 over singles. |
| round-09/training-m05 | 249 | [239, 259] | Singles 234/229 plus a vote gain reduced by fewer abstentions. |
| round-09/training-m06 | 249 | [239, 259] | Singles 234/229 plus a reduced vote gain. |
| round-09/problems-m01 | 249 | [238, 259] | M(2) abstains about half as often as Think-SFT, so its vote gain is about 60 % of Think-SFT's +15 % on singles of 231.5, bounded by a pass@4 near 256. |
| round-09/problems-m02 | 249 | [238, 259] | Fewer cut answers than Think-SFT, so its vote gains less over singles of 231.5. |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | 249 | [238, 259] | M(2) keeps Think-SFT's plans and adds finishing; vote gain smaller than Think-SFT's because fewer abstentions. |
| round-09/problems-m06 | 248 | [237, 258] | a=2 turns some abstentions into guesses on hard328, so its vote gains less than Think-SFT's: about +7 % over 231.5. |
| round-09/grader-m01 | 248 | [237, 259] | Singles 234 and 229 (mean 231.5, a=2 picked on the 328, so ~230 for new seeds) plus a vote gain of ~18. |
| round-09/grader-m02 | 249 | [238, 260] | M(2) abstains on ~16 % (54 cap hits) with ~84 % finished precision: selection loss ~8 from a pass@4 near 257. |
| round-09/grader-m03 | 249 | [238, 260] | The transplant's null is Think-SFT itself (noise control 209 = Think-SFT mean), so the singles' +22 is real; vote adds ~18. |
| round-09/grader-m04 | 249 | [238, 260] | Vote over 4 on hard328 with ~70 problems no model solves. |
| round-09/grader-m05 | 248 | [237, 259] | M(2) finishes more than Think-SFT, so some ties return; vote ~ pass@4 minus ~9. |
| round-09/grader-m06 | 249 | [238, 260] | 16k vote of a model with ~16 % cap hits. |

## t22 (work-8b4030): Right answers of 500 on MATH-500 for one sample of Think-SFT plus twice the RL-Math weight change.

Unit: right answers of 500. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 468 | [458, 477] | a=1 scored 467 and Think-SFT cue singles are 454-462; a=2 peaked on hard328. |
| reader-2 | 466 | [455, 476] | a=1 scored 467 and Think-SFT singles are 457-462; a=2 should be similar. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 466 | [457, 474] | Theory: the edit works in full in-domain, so the transplant holds on MATH-500. The 1x transplant scored 467, Think-SFT singles score 457-462, and at 2x more answers finish. |
| run-05/f2-m01 | 465 | [456, 474] | The dial modestly raises correctness on finished problems, and MATH-500 has few unfinished ones, so 2x stays near a=1's 467 and Think-SFT's 457-462. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | 466 | [458, 474] | Theory: the a=2 merge is realized above nominal, but on MATH-500 finishing has little room: a=1 gave 467 and Think-SFT singles 457-462, so ~466. |
| run-03/f2-m02 | 466 | [455, 475] | Theory: right-of-finished stays flat and MATH-500 has few cap hits to convert, so a=2 sits near a=1's 467 and Think-SFT's 457-462 singles. |
| run-02/f2-m04 | 466 | [455, 475] | Finishing raises singles: a=1 gave 467 on MATH-500 against Think-SFT's 454-462; at a=2 finishing is near complete there, so it stays about level. |
| run-03/f2-m05 | 465 | [455, 474] | Theory: short MATH-500 traces carry little degeneration hazard, so a=2 stays near a=1's 467. |
| run-04/f2-m03 | 465 | [457, 473] | Twice the RL change multiplies the stop-hazard shift, so Think-SFT's few MATH-500 cap hits (about 25 of 500) convert at low precision; that adds little to its 457-462 single, near the a=1 467. |
| round-09/stopping-m01 | 465 | [456, 473] | One sample on MATH-500, where Think-SFT caps only about 5 %; the RL delta removes a few abstentions and costs a little precision. |
| round-09/stopping-m02 | 465 | [456, 473] | On MATH-500 few traces are long, so moving the stopping point earlier changes little; small precision cost against a=1's 467. |
| round-09/stopping-m03 | 465 | [456, 473] | Same edit on MATH-500, no degeneration. |
| round-09/stopping-m04 | 465 | [456, 473] | On MATH-500 Think-SFT cuts about 25 answers, so finishing more changes little; near a=1's 467. |
| round-09/stopping-m05 | 464 | [455, 472] | MATH-500 answers rarely pass 12k, so the long-answer precision loss costs about 1-2 problems against a=1. |
| round-09/stopping-m06 | 465 | [456, 473] | The Think-SFT host never writes terse answers; one MATH-500 sample near a=1's 467. |
| round-09/sampling-m01 | 466 | [457, 475] | a=1 gave 467 in one draw; a=2 is the same family, so one draw around 466. |
| round-09/sampling-m02 | 466 | [456, 476] | One sample on MATH-500 with few cap hits: finished x precision as at a=1 (467). |
| round-09/sampling-m03 | 466 | [456, 476] | Cued Think-SFT models open deterministically; no opening term, so it stays near a=1's 467. |
| round-09/sampling-m04 | 465 | [455, 475] | Below threshold on short MATH-500 answers: as at a=1 (467). |
| round-09/sampling-m05 | 466 | [456, 476] | On MATH-500 few answers reach the cap, so the change in stopping moves little. |
| round-09/sampling-m06 | 466 | [456, 476] | On MATH-500 the near-zero block is the same few problems for every strong arm; about a=1's 467. |
| round-09/weights-m01 | 465 | [455, 475] | On MATH-500 extra finishing changes little; a=1 gave 467. |
| round-09/weights-m02 | 466 | [456, 476] | On MATH-500 the push adds little to Think-SFT; a=1 gave 467. |
| round-09/weights-m03 | 466 | [456, 476] | The readout added to Think-SFT changes MATH-500 little; a=1 gave 467. |
| round-09/weights-m04 | 466 | [456, 476] | Think-SFT has few cap hits on MATH-500 (25), so the operator has little to finish; a=1 gave 467. |
| round-09/weights-m05 | 466 | [456, 476] | The full final delta on Think-SFT changes MATH-500 little. |
| round-09/weights-m06 | 466 | [456, 476] | Nominal a=2 on MATH-500: little change from a=1's 467. |
| round-09/training-m01 | 466 | [456, 475] | Raw template keeps the format undercount; a=1 gave 467, and a=2 adds finishing on few MATH-500 cap hits. |
| round-09/training-m02 | 466 | [456, 475] | MATH-500 has few cuts, so the added stopping changes little; near a=1's 467. |
| round-09/training-m03 | 466 | [456, 475] | MATH-500 is near saturation for Think-SFT; a=2 changes little over a=1's 467. |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | 466 | [456, 475] | The full delta on Think-SFT adds the boxed ending and stopping; MATH-500 has little to gain from either. |
| round-09/training-m06 | 466 | [456, 475] | Full delta on Think-SFT; MATH-500 near saturation. |
| round-09/problems-m01 | 465 | [456, 474] | MATH-500 has few never-solved problems; a=2 moves only the middle band, level with a=1's 467 within noise. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 465 | [456, 474] | Easy MATH-500 problems are already right in Think-SFT; a=2 changes only long ones. |
| round-09/problems-m04 | 465 | [456, 474] | MATH-500 short problems are already solved by Think-SFT; a=2 moves the long ones only. |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | 465 | [456, 474] | On MATH-500 a=2 is on the flat top, level with a=1's 467. |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | 466 | [456, 476] | Single count; a=1 467, finishing weight adds little where few answers are cut. |
| round-09/grader-m03 | 466 | [456, 476] | Null = Think-SFT singles ~459; a=1 adds +8 on MATH-500, a=2 no more because cap hits are few. |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | 466 | [456, 476] | Single count. |
| round-09/grader-m06 | 466 | [456, 476] | Few MATH-500 cap hits to remove, so a=2 = a=1 within noise. |

## t23 (work-8b4030): Right answers of 328 on hard328 for one sample of Think-SFT plus twice the RL-Math weight change with the token cap raised to 32,768.

Unit: right answers of 328. Cell: {"model": "Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "cap 32,768; T and top-p not stated; seed 3,000,000", "samples": 1, "grader": "not stated"}

> Added (amendment 3, no new box): M(2) at cap 32,768 on hard328, seed 3,000,000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 241 | [229, 252] | Same seed at cap 16,384 gave 234 with about 50 cap hits; the longer cap recovers roughly a quarter of those as right, as it did for Think-SFT. |
| reader-2 | 242 | [229, 255] | Seed 3,000,000 at 16k gave about 234; about 50 cap hits at a=2, and roughly a quarter of cut answers come right at 32k as for Think-SFT. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 240 | [228, 252] | Theory: hard328 needs long reasoning (6,000-14,000 tokens). Raising the cap lets M(2)'s roughly 40-54 cap hits finish; if they convert at Think-SFT's rate (23 right of 93), that adds about 8-10 to the 16k mean of 231.5. |
| run-05/f2-m03 | 243 | [231, 255] | Theory: full in-domain effect gives the 2x transplant about 234 at seed 3,000,000 at the 16,384 cap. Raising the cap to 32,768 should rescue about a quarter of its roughly 54 cut answers, as it did for Think-SFT (23 of 93 right). |
| run-05/f2-m01 | 239 | [229, 250] | With the dial at 2x, about 54 cap hits are left at 16k (singles 229-234); a larger cap lets some finish but fewer than Think-SFT's +23, because the dial already closed most of them. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | 245 | [232, 257] | Theory: the realized a=2 delta leaves ~54 cap hits of 328 (vs 94 for Think-SFT). At cap 32,768 about 25% of those finish right (Think-SFT's 23 of 93), so 231.5 + ~13. |
| run-03/f2-m02 | 238 | [226, 249] | Theory: the delta already closes many answers (about 54 cap hits at a=2), so doubling the cap adds fewer than Think-SFT's +23; about 231 plus 7. |
| run-02/f2-m04 | 242 | [231, 253] | Doubling the cap finishes most of M(2)'s ~54 cap hits; at Think-SFT's 25% right rate on late finishes (23 of 93), and lower precision under the RL difference, that adds about 10 to 232. |
| run-03/f2-m05 | 238 | [227, 249] | Theory: the extra 16k tokens recover only the cut traces that have not degenerated; M(2) has about 54 cap hits, roughly a quarter of them recoverable, giving about +7 on 231. |
| run-04/f2-m03 | 242 | [231, 253] | Survival view: M(2) scores ~234 at 16,384 tokens with ~54 cap hits; doubling the cap lets most of those finish, and at the ~25% precision of Think-SFT's late finishes that adds about 8-10. |
| round-09/stopping-m01 | 242 | [231, 253] | About 54 cap hits at 16k; most finish under 32k and about a fifth are right: about 232 + 10. |
| round-09/stopping-m02 | 243 | [232, 254] | 2x the RL delta moved the stopping point earlier (cap hits 54 at 16k); about 50 cut traces at 25 % recovery add about 11 to about 232. |
| round-09/stopping-m03 | 242 | [231, 253] | No degeneration even with a longer budget; cut answers finish. |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 240 | [229, 251] | The RL delta brings RL's habit of asserting at long lengths: late finishes of M(2) are right about 15-20 % of the time, so about 50 cut traces add about 8. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | 240 | [229, 251] | A same-seed rerun is a new draw: mean 16k single 231.5 plus about 9 from cut answers that finish. |
| round-09/sampling-m02 | 241 | [230, 252] | Doubling the cap finishes most of the ~50 cut answers, about 20 % right: 231.5 + 9. |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | 240 | [229, 251] | Answers past 16k take more draws, but a=2 is coherent; cut answers convert at about 20 %. |
| round-09/sampling-m05 | 241 | [230, 252] | About 50 cut answers finish at 32k at about 20 % (Think-SFT's 25 % scaled by right-of-finished 72/88): 231.5 + 10. |
| round-09/sampling-m06 | 241 | [230, 252] | A longer cap reaches only cut problems with p above 0; about 10 more right. |
| round-09/weights-m01 | 239 | [228, 250] | The 2x top direction leaves about 50 cap hits on the hardest problems; the extra 16k finishes some of them, at a low right rate. |
| round-09/weights-m02 | 241 | [230, 252] | The remaining cap hits finish with the extra tokens at about a quarter right. |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | 240 | [229, 251] | About 50 cap hits left. The operator has already closed the sound ones early, so the rest finish in the extra 16k at about 15 % right: about +6 over 234. |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | 241 | [229, 253] | Same written model as the 16k run; reruns with the same seed still differ (RL 193 against 206), so the interval is wider; the extra tokens add about 7. |
| round-09/training-m01 | 240 | [229, 251] | Raw template, about 50 cap hits at 16k; extra budget converts some; no format effect. |
| round-09/training-m02 | 239 | [228, 250] | About 50 cuts at 16k; the RL delta makes cut answers less like unfinished work (finished precision 88 to 72 %), so about 15 % convert, +7 on a 16k count near 232. |
| round-09/training-m03 | 240 | [229, 251] | More budget helps on problems the model solves sometimes; about +7 over the 16k count. |
| round-09/training-m04 | - |  | no forecast |
| round-09/training-m05 | 240 | [229, 251] | About 50 cuts left at 16k; some finish right at 32k. |
| round-09/training-m06 | 240 | [229, 251] | About 50 cuts at 16k, some convert at 32k. |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 240 | [228, 252] | M(2)'s remaining ~50 cap hits are Think-SFT-style unfinished work on the longest problems, about 18 % right when finished (+9) on a new-sample 16k base of about 231. |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | 240 | [228, 252] | Cut M(2) answers still hold plans, so 32k converts about a fifth of them to right. |
| round-09/problems-m06 | 240 | [228, 252] | At 32k the a=2 model's remaining cut answers are on hard problems; about a fifth finish right. |
| round-09/grader-m01 | 240 | [228, 252] | Same seed does not reproduce (RL 193 vs 206), so the 16k level is the a=2 mean ~231 plus ~9 late right answers. |
| round-09/grader-m02 | 240 | [228, 252] | Single count: ~231 at 16k plus ~9 late right answers. |
| round-09/grader-m03 | 240 | [228, 252] | a=2 mean ~231 at 16k plus late finishes. |
| round-09/grader-m04 | 240 | [228, 252] | hard328 late finishes for a model that already finishes more. |
| round-09/grader-m05 | 240 | [228, 252] | Single count. |
| round-09/grader-m06 | 240 | [228, 252] | M(2) has ~54 cut answers; the RL delta already finishes the easier ones, so yield ~15 %: 231 + 8. |

## t24 (work-290625): Right answers of 500 on MATH-500 for one sample of the base plus 2x the top 8 RL-Math directions per matrix, with the cue, at T 1.0, grader v3.

Unit: right answers of 500. Cell: {"model": "base + 2 x top 8 singular directions per matrix of (RL-Math - base)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and cap not stated; seed 3000000", "samples": 1, "grader": "v3"}

> Cell m29: base + top-8 RL-Math directions at 2x, cue, MATH-500 n 500, T 1.0, v3

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 448 | [436, 458] | 1.5x scored 456; on hard328, going from 1.5x to 2x cost 13 problems through over-eager finishing, and MATH-500 should be hurt less. |
| reader-2 | 450 | [438, 461] | 1.5x scored 456 on MATH-500; 2x slightly overshoots (190 vs 203 on hard328) but easy problems suffer less. |
| run-06/f2-m03 | 447 | [436, 457] | Theory: '2x commits too early', so this falls below the 1.5x cell's 456 on MATH-500; the cost is smaller than hard328's 13 points because MATH-500 has few long answers. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | 450 | [438, 461] | Theory: full in-domain effect on MATH-500 puts the 1.5x cue edit at 456. Going to 2x cost 13 problems on hard328 (190 vs 203), so expect a small drop. |
| run-05/f2-m01 | 450 | [438, 460] | Past 1.5x the dial closes unfinished hard solutions on guesses (hard328: 2x 190 vs 1.5x 203). MATH-500 has few cap hits, so it lands slightly below 1.5x's 456. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | 447 | [436, 457] | Theory: effective size grows faster than nominal, so 2x top-8 overshoots RL's share (hard328: 190 vs 203 at 1.5x, precision 0.59), costing a few points below the 456 of 1.5x on MATH-500. |
| run-03/f2-m02 | 450 | [438, 460] | Theory: past 1.5x the hazard closes hard problems with guesses (hard328 2x 190 vs 1.5x 203); on the easier MATH-500 the loss is small, a few points under 1.5x's 456. |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | 447 | [435, 458] | Theory: 2x is in the word-string zone, so it loses answers against 1.5x (456), as on hard328 (203 -> 190); losses are smaller on MATH-500 because hazard grows with tokens and the traces are short. |
| run-04/f2-m03 | 450 | [440, 460] | At 2x the dial leaves almost no cap hits, but precision falls (0.59 vs 0.65 on hard328, 190 vs 203); on MATH-500, which has few cap hits, that means a small drop from the 1.5x cell's 456. |
| round-09/stopping-m01 | - |  | no forecast |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | 451 | [442, 459] | Top-8 at 2x is below the collapse level (190 right and 5 cap hits on hard328, no word strings); MATH-500 has only about 27 base cap hits to turn into guesses, so the cost against 1.5x (456) is small. |
| round-09/stopping-m04 | 450 | [441, 458] | Few MATH-500 answers are cut, so the 2x edit's extra finishing has little to convert; a small precision cost against 456. |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 450 | [441, 458] | No terse stops under the cue; the 2x edit costs a little precision against 456. |
| round-09/sampling-m01 | 449 | [439, 459] | One draw near the 1.5x cell's 456, less a few for overshoot, sd 6. |
| round-09/sampling-m02 | 448 | [437, 459] | At 2x almost nothing abstains, and the precision loss seen on the 328 (0.65 to 0.59) is smaller on short answers. |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | 449 | [439, 459] | 2x is near the threshold (precision 0.59 on the 328), but MATH-500 answers are about 2.3x shorter, so the loss is a few problems from 456. |
| round-09/sampling-m05 | 449 | [439, 459] | 2x makes stopping very likely (5 cap hits on the 328); on MATH-500 few answers need the extra length, so the loss from early stops is small. |
| round-09/sampling-m06 | - |  | no forecast |
| round-09/weights-m01 | 446 | [434, 457] | 2x on the top direction over-commits on MATH-500's longest problems, giving back about 10 of the 1.5x cell's 456. |
| round-09/weights-m02 | 450 | [439, 460] | At 2x the summed push over-finishes; on MATH-500 few answers are long enough to be cut, so the loss from 456 is small. |
| round-09/weights-m03 | 449 | [438, 459] | A 2x late readout pushes stop early on MATH-500's few long problems: small loss from 456. |
| round-09/weights-m04 | 449 | [438, 459] | A 2x operator on the base finishes more but adds no correctness; MATH-500 has few cap hits, so a small loss from 456. |
| round-09/weights-m05 | 449 | [438, 459] | Late finishing directions at 2x over-finish slightly on MATH-500. |
| round-09/weights-m06 | 450 | [439, 461] | The written norm equals the hard328 2x edit (3.8596 vs 3.8597): nominal 2x behaviour, a small loss from 456 on MATH-500. |
| round-09/training-m01 | 449 | [438, 459] | 2x keeps the boxed ending; the small loss from 456 is overshoot, not format. |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | 449 | [438, 459] | MATH-500's movable problems are already moved at 1.5x (456); 2x adds overshoot cost only. |
| round-09/training-m04 | 449 | [438, 459] | A larger dose does not change the modal value on MATH-500; small overshoot cost from 456. |
| round-09/training-m05 | 449 | [438, 459] | On MATH-500 the boxed form is already written at 1.5x (456); 2x adds overshoot only. |
| round-09/training-m06 | 449 | [438, 459] | 2x over-drives the early features with little to gain on MATH-500; small loss from 456. |
| round-09/problems-m01 | - |  | no forecast |
| round-09/problems-m02 | 449 | [438, 459] | MATH-500 has few long derivations to cut short; 2x costs a few problems against 456 at 1.5x. |
| round-09/problems-m03 | 450 | [439, 460] | Short MATH-500 problems are untouched by a larger dose; only the longest lose a few. |
| round-09/problems-m04 | 449 | [438, 459] | MATH-500's long problems are the only ones a larger dose of early-RL directions can hurt. |
| round-09/problems-m05 | - |  | no forecast |
| round-09/problems-m06 | 450 | [439, 460] | MATH-500 is easy: few unsolvable cut answers, so 2x costs only a few against 456. |
| round-09/grader-m01 | 449 | [438, 459] | 1.5x scored 456 in one draw; 2x lost ~10 against the replicated 1.5x mean on hard328, less on MATH-500. |
| round-09/grader-m02 | - |  | no forecast |
| round-09/grader-m03 | 449 | [438, 459] | 2x lost ~10 vs the replicated 1.5x mean on hard328 through precision; on MATH-500 about 6. |
| round-09/grader-m04 | - |  | no forecast |
| round-09/grader-m05 | - |  | no forecast |
| round-09/grader-m06 | 450 | [439, 460] | 2x already removes almost all cap hits; on MATH-500 little is censored. |

## t25 (work-a68dfd): Right answers of 136 on the fresh 2026 contest problems for one sample of the untrained Olmo 3 base with the plain prompt (no cue) at T 1.0, cap 16,384, grader v3.

Unit: right answers of 136. Cell: {"model": "untrained base Olmo-3-1025-7B", "prompt": "plain (no cue)", "set": "fresh2026", "n": 136, "sampling": "T 1.0; top-p not stated; cap 16,384", "samples": 1, "grader": "v3"}

> Cell m20: untrained Olmo 3 base, plain prompt (no cue), fresh2026, 136 problems, 1 sample, T 1.0, v3, cap 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 13 | [7, 20] | The cued base single scores 29.5 on fresh2026, and the plain prompt keeps about 46-55% of the cued score on the other sets. |
| reader-2 | 13 | [6, 21] | The cued base single is 29.5 of 136; plain is about 0.45 of cue on hard328 (76 vs 164), and less on the hardest set. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | 14 | [8, 21] | The base fails on fresh contests by not stopping; without the cue the plain base stops early on short, low-precision answers, which gives about 0.46 of the cued single 29.5, the same ratio as hard328 (76 vs 164). |
| round-09/stopping-m01 | 13 | [7, 20] | Plain base answers rarely reach the cap: they end short and wrong, so no abstention effect; about 0.45 of the cued 29.5. |
| round-09/stopping-m02 | - |  | no forecast |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | 13 | [7, 20] | The plain base's short answers are rarely cut; its score is precision on finished answers, about 0.45 of the cued 29.5. |
| round-09/stopping-m05 | - |  | no forecast |
| round-09/stopping-m06 | 12 | [6, 19] | About 37 % of plain samples self-open and score like cued ones (0.37 x 29.5 = 11); the terse rest end early and get about 1-2 contest problems. |
| round-09/sampling-m01 | 13 | [7, 19] | Plain keeps about 0.45 of the cue's 29.5; at a mean of 13 the binomial sd is about 3.4. |
| round-09/sampling-m02 | - |  | no forecast |
| round-09/sampling-m03 | 11 | [5, 17] | At T 1.0 about 19 % of plain base answers self-open (cue rate 21.7 % -> 5.6); the terse 81 % solve about 5 % of 2026 contest problems (5.3). |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | 12 | [6, 18] | Plain base answers are short and almost never reach the cap, so the cap adds nothing; the plain/cue ratio sets the count. |
| round-09/sampling-m06 | 12 | [6, 18] | For the plain base most 2026 contest problems are in the near-zero block; the rest give about 0.4 of the cue's 29.5. |
| round-09/weights-m01 | - |  | no forecast |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | 13 | [7, 20] | No operator and no cue: the plain base keeps about 45 % of the cued score. |
| round-09/weights-m05 | 13 | [7, 20] | There is no register switch in the plain base; on the hardest set it keeps under half of the cued 29.5. |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | 12 | [6, 19] | Plain base answers rarely carry a readable final line on hard problems; about 0.4 of the cued 29.5. |
| round-09/training-m02 | - |  | no forecast |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | 11 | [6, 17] | Plain/cue ratio falls with difficulty: 0.55 at cued 82 %, 0.46 at cued 50 %; extrapolated to cued 21.7 % on fresh2026 it is about 0.38 of 29.5. |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | 12 | [6, 19] | Most fresh problems are in the cued base's never-solved block already; the plain prompt keeps about 0.42 of its 29.5. |
| round-09/problems-m02 | - |  | no forecast |
| round-09/problems-m03 | 12 | [6, 19] | Fresh problems have no short ones where the terse register would lose most, but the cued base is already low there; plain keeps about 0.42 of 29.5. |
| round-09/problems-m04 | 12 | [6, 19] | Without even the opening, the base's plain prompt keeps about 0.42 of the cued 29.5 on these long problems. |
| round-09/problems-m05 | 12 | [6, 19] | Plain base has the base's plans and loses its terse answers; about 0.42 of the cued 29.5. |
| round-09/problems-m06 | - |  | no forecast |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | 13 | [7, 20] | Single count of the plain base; no vote involved. |
| round-09/grader-m03 | 13 | [7, 20] | Unedited base; plain keeps ~0.45 of the cued count. |
| round-09/grader-m04 | 12 | [6, 19] | Plain = 20 % self-opened at cued accuracy + 80 % non-opened at ~0.33 of cued: 136 x (0.2 x 0.217 + 0.8 x 0.072) = 13.7, trimmed for the harder set. |
| round-09/grader-m05 | 13 | [7, 20] | Single count. |
| round-09/grader-m06 | 13 | [7, 20] | Plain base answers are short; censoring costs little. |

## t26 (work-dc9359): Right answers of 328 on hard328 for a majority vote over 4 samples of Think-SFT with the cue at a 32,768-token cap.

Unit: right answers of 328. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "cap 32,768; T and top-p not stated", "samples": 4, "grader": "not stated"}

> Think-SFT + cue vote over 4 at token cap 32,768 on hard328

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 246 | [236, 256] | At cap 16,384 the vote is 241 and sample 0 at cap 32,768 is 230; the offline simulation said 240 unless late answers disagree. |
| reader-2 | 245 | [235, 255] | Vote over 4 at 16k is 241 and the offline simulation says 240 [232, 248]; sample 0 at 32k scored 230 vs 207 at 16k. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 243 | [234, 252] | Theory: hard328 solutions need up to about 14,000 tokens, so a cap past 16k adds only a few votes. Starting from the 16k vote over 4 (241) and the offline simulation (240 [232, 248]). |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | 242 | [234, 251] | Core claim: at 32k, abstentions become scattered wrong answers that tie or outvote lone right samples, so even with singles at about 230 the vote stays near the 16k vote of 241 instead of climbing toward a higher pass@4. |
| run-03/f2-m05 | 246 | [237, 255] | Theory: late Think-SFT traces degenerate and degenerate traces end wrong, so the 32k cap adds wrong votes along with right ones; a small gain over the 16k vote's 241. |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 242 | [234, 250] | At 16k the vote (about 240 with the new sample 0, which scored 207 at 16k against the stored 212) is near pass@4 because the 29 % cut samples abstain; at 32k they vote, three quarters of them wrong, so the vote gains only about +2. |
| round-09/stopping-m02 | 247 | [238, 256] | Late finishes are real derivations whose values agree with sibling samples, so the vote gains about +6 over the 16k vote of about 241. |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 243 | [235, 251] | Late Think-SFT finishes include drifted guesses that add wrong votes; the net vote gain is a few problems. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | 242 | [233, 251] | At 16k the vote (241) is almost pass@4 because the other samples abstained; at 32k they finish, 75 % wrong, and turn about 9 single-right wins into ties, offsetting about 10 new right answers. |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | 245 | [236, 254] | Each 32k sample gains about 23 from finished cut answers, mostly on problems another sample already solves: pass@4 about 252, vote a few under it. |
| round-09/sampling-m06 | 245 | [236, 254] | The 16k vote (241) is almost at pass@4 (244); 32k lifts only the cut problems with p above 0 out of the near-zero block, about +4. |
| round-09/weights-m01 | - |  | no forecast |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | 245 | [236, 254] | Cut work that finishes past 16k is right about 25 % of the time; it adds right votes but also wrong votes, so the vote rises only a few above 241. |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | 245 | [236, 254] | Raw template with the cue; the vote at 32k moves only by finishing, not by format. |
| round-09/training-m02 | 246 | [237, 255] | At 16k the vote (241) is near pass@4 (244); at 32k all-cut problems get answers (about +8) and scattered late wrong answers cost a few ties (about -3). |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | 245 | [236, 254] | Late wrong finishes scatter over values, so they seldom form a wrong mode; the vote gains where all samples were cut. |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | 245 | [236, 254] | At 16k the vote (241) is already near pass@4 (244); at 32k late answers add new right samples on a few problems, but finished wrong ones now vote too. |
| round-09/problems-m02 | 246 | [237, 255] | Per sample about +7 points from finished long derivations, but the vote at 16k is already near pass@4, so the vote gains less than singles. |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | 246 | [237, 255] | Same on hard328, but its vote at 16k is already near pass@4. |
| round-09/problems-m06 | 245 | [236, 254] | A higher cap is a dose of finishing: on hard328 late answers to unsolvable problems vote too, so the vote gains less than singles. |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | 242 | [233, 251] | At 32k ~91 of 93 abstentions per sample finish, ~70 of them wrong; they now vote against lone right answers that won at 16k, offsetting the ~23 extra right per sample. |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | 243 | [234, 252] | hard328 late finishes give 23 right per sample but mostly on problems the vote already wins. |
| round-09/grader-m05 | 241 | [232, 250] | At 32k the cut samples finish, ~70 wrong, creating 1-1 ties with lone right answers that the lowest-index rule loses about half the time. |
| round-09/grader-m06 | 243 | [234, 252] | Per-sample yield of ~23 falls mostly on problems the vote already wins. |

## t27 (work-dc9359): Right answers of 136 on the fresh 2026 contest problems for a majority vote over 4 samples of Think-SFT with the cue at a 32,768-token cap.

Unit: right answers of 136. Cell: {"model": "allenai/Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "cap 32,768; T and top-p not stated", "samples": 4, "grader": "not stated"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 82 | [72, 91] | The vote at cap 16,384 was 75 with 46% cap hits; the longer cap finishes many of those, as on hard328 (+23 right per sample). |
| reader-2 | 82 | [72, 92] | Vote at 16k is 75 with 46 % cap hits; at 32k some cut answers finish right (+7 points per sample on hard328), though late wrong answers may dilute the vote. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-02/f2-m04 | 78 | [71, 85] | On fresh2026 (46% cap hits) the 32k cap lifts singles from 60 to about 66, but scattered late wrong answers cut the vote gain, so the vote rises only a little above the 16k vote of 75. |
| run-03/f2-m05 | 81 | [72, 90] | Theory: fresh2026 has 46% cap hits, many of which finish under 32k, but the switch hazard past about 13.6k tokens limits the recovered right answers; a modest gain over the 16k vote's 75. |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 79 | [72, 86] | 46 % of fresh samples abstain at 16k (vote 75); at 32k most of them answer, with low late precision on contest problems, so the vote gains about +4. |
| round-09/stopping-m02 | 83 | [75, 91] | 46 % of fresh samples are cut work; a longer cap finishes them at about 15-20 % right, lifting singles by about 10 and the vote by about 8. |
| round-09/stopping-m03 | - |  | no forecast |
| round-09/stopping-m04 | - |  | no forecast |
| round-09/stopping-m05 | 79 | [72, 86] | On contest problems more cut traces are drifted or unsolved, so late precision is about 12-15 %; the vote gains about +4. |
| round-09/stopping-m06 | - |  | no forecast |
| round-09/sampling-m01 | - |  | no forecast |
| round-09/sampling-m02 | 79 | [70, 88] | Singles rise about 10 when the 46 % cut answers finish, but on fresh problems the new finished answers are mostly wrong and break outright wins into ties: 75 + 4. |
| round-09/sampling-m03 | - |  | no forecast |
| round-09/sampling-m04 | - |  | no forecast |
| round-09/sampling-m05 | 82 | [73, 91] | On fresh2026, 46 % of samples are cut; at about 18 % right on finishing that is about +11 per sample and +7 to the vote. |
| round-09/sampling-m06 | 81 | [72, 90] | Fresh2026 has a large near-zero block for Think-SFT (pass@4 well under 136); 32k adds about 6 to the vote. |
| round-09/weights-m01 | - |  | no forecast |
| round-09/weights-m02 | - |  | no forecast |
| round-09/weights-m03 | - |  | no forecast |
| round-09/weights-m04 | 81 | [72, 90] | 46 % cap hits at 16k leave much sound work for the longer cap; the vote rises from 75. |
| round-09/weights-m05 | - |  | no forecast |
| round-09/weights-m06 | - |  | no forecast |
| round-09/training-m01 | 82 | [73, 91] | Raw template on fresh2026; the format effect is small on contest integers, so only the cap matters. |
| round-09/training-m02 | 81 | [72, 90] | 46 % cut on fresh2026 and late finishes right about 20 %: about +11 per single, about +6 to +8 under the vote from 75. |
| round-09/training-m03 | - |  | no forecast |
| round-09/training-m04 | 82 | [73, 91] | Same logic on fresh2026: new answers on all-cut problems, few wrong modes. |
| round-09/training-m05 | - |  | no forecast |
| round-09/training-m06 | - |  | no forecast |
| round-09/problems-m01 | 82 | [73, 91] | Fresh vote 75 is below its pass@4 because 46 % of samples abstain; finished late samples raise pass@4 and the vote follows it. |
| round-09/problems-m02 | 83 | [74, 92] | Fresh problems need the longest derivations: 46 % of samples are cut, about 20 % of them finish right at 32k, lifting pass@4 and the vote. |
| round-09/problems-m03 | - |  | no forecast |
| round-09/problems-m04 | - |  | no forecast |
| round-09/problems-m05 | 83 | [74, 92] | Think-SFT's cut fresh answers carry working plans; at 32k about 20 % finish right, lifting the vote by about 8. |
| round-09/problems-m06 | 82 | [73, 91] | Fresh problems have the most unsolvable cut answers, so the cap's vote gain is diluted: about +7. |
| round-09/grader-m01 | - |  | no forecast |
| round-09/grader-m02 | 78 | [70, 86] | 46 % abstentions at 16k become ~60 finished answers per sample with ~10 right; finished precision falls from 80 % to ~53 %, so the vote gain drops from +15 toward RL's +7 on a single of ~70. |
| round-09/grader-m03 | - |  | no forecast |
| round-09/grader-m04 | 78 | [70, 86] | Fresh is harder than hard328, so cut answers finish right less often (~15 % vs 25 %): ~9 per sample, and the vote loses part of its abstention lead. |
| round-09/grader-m05 | 78 | [70, 86] | 46 % of samples were abstentions at 16k; as they finish wrong, singleton ties replace lone winners. |
| round-09/grader-m06 | 80 | [71, 89] | ~62 cut answers per sample, yield ~18 % on harder problems: singles 60 -> 71, vote gain shrinks. |
