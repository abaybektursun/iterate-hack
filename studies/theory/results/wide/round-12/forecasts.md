# Forecasts, round-12

Board snapshot 2026-11-15T20:38:56 UTC, written 2026-11-15T20:49:48 UTC. 20 targets; forecasters reader-1, reader-2, run-05/f2-m06, run-05/f2-m01, run-06/f2-m03, run-05/f2-m03, run-02/f2-m04, round-09/grader-m01, round-10/weights-m03, run-03/f2-m04, run-03/f2-m02, run-08/f2-m02, round-09/sampling-m05, run-04/f2-m05, run-08/f2-m06, round-09/training-m01, round-09/training-m06, round-09/grader-m06, round-10/weights-m06, round-10/problems-m04, round-09/stopping-m04, run-05/f2-m05, run-08/f2-m05, round-10/problems-m03, round-09/stopping-m01, run-07/f2-m01, round-09/training-m03, round-09/training-m04, run-03/f2-m03, round-10/grader-m06, round-10/weights-m01, run-06/f2-m04, run-03/f2-m01, round-09/training-m02, round-10/problems-m06, run-06/f2-m01, run-07/f2-m02, round-09/sampling-m01, round-09/weights-m04, round-09/grader-m04, round-10/training-m05, round-10/problems-m05, round-09/sampling-m02, round-10/weights-m05, round-12/s1-b, round-12/s6-b.


- run-05/f2-m06 (weights, carried): Weight edits merged in bf16 are realized only where an entry's change exceeds half a unit in the last place of that weight, so small edits are thresholded onto small-magnitude weights and their effective size grows faster than nominal size (a=0.25 acts like about 0.12; top-8 at nominal 1.5 acts like RL's own top-8 share). Smaller deltas such as Code-RL's lose more at 1x and peak at a larger nominal size; trained checkpoints carry no such loss.

- run-05/f2-m01 (weights, carried): The top-8 singular directions per matrix of the RL change act as a signed termination dial spread over all layers and both module families: adding them at size s raises, monotonically in s, the chance an answer closes with a boxed result before the cap (negative s lengthens and unboxes), and modestly raises correctness on problems already finished; past 1.5x it closes unfinished hard solutions on guesses. Random rank-8 edits and Think-SFT's directions carry no dial.

- run-06/f2-m03 (training, carried): An outcome reward pays only for a gradable final answer, so its consistent gradient piles into a few singular directions that make the model complete the task in the rewarded form (boxed answer, final code block) before the cap; the rest of the update is diffuse. In-domain, the top-8 directions at 1.5x reproduce nearly all of RL's gain over the cued base. Another reward's directions give about half, random rank-8 gives nothing, and 2x commits too early.

- run-05/f2-m03 (weights, carried): Each direction of an RL change acts only as far as the processed text drives its input (right) singular vectors: Math-RL's top-8 input subspaces are excited 8-11x above random by math-solution text and Code-RL's 6-9x, so an edit works in full on any problem set of its own domain and transfers to another domain in proportion to input-subspace overlap (Math with Code about 0.22-0.26, giving roughly half the in-domain effect).

- run-02/f2-m04 (run-02, carried): A capped sample gives no answer, so in a plurality vote it abstains instead of adding a wrong value. Think-SFT's vote sits near its pass@4 because its unsolved samples run to the cap rather than box a guess. Anything that makes it finish, a 32k cap or the RL difference, turns abstentions into mostly wrong, scattered answers that tie or outvote lone right samples: single scores rise, vote gains shrink.

- round-09/grader-m01 (grader, carried): Each posted single cell is one seeded draw: new seeds on the same weights scatter by 5-7 problems per 500 and up to 9-19 per 328, and cells picked as notable (best size, first run) sit above their model's mean. Multi-sample means regress to the pooled level of near-identical cells: step-100 plain pools with step-100 cue (same opening policy), and the 164-problem references come from draws above their own 4-sample means.

- round-10/weights-m03 (weights, carried): The effect of an added RL change depends on the host. Think-SFT's high-rank imitation change (3.7 % of weight norm, top 8 directions hold 2 %) already sets the long-reasoning features that RL's directions read, so RL's push has about a quarter of its effect on the base: a=1 cut Think-SFT's cap hits by 20 %, not 74 %. The response is weak but stable, no breakdown up to 4x. Its correctness covers every domain in its traces.

- run-03/f2-m04 (stopping, carried): Graded accuracy depends on how a model ends its answer: whether the last thing written is the gradable marker (a boxed value, an Answer: line, the final python block). Under the raw template Think-SFT sometimes ends with the gold on a line v3 does not read. RL directions install one terminal marker. The native Think-SFT format ends with a post-think summary that restates the answer. Math directions push a boxed ending that competes with the final code block.

- run-03/f2-m02 (stopping, carried): RL's top singular weight directions raise the model's per-token hazard of committing to an answer and ending, in proportion to their size. In-domain directions therefore turn unfinished answers into finished ones and lengthen premature short ones. Overall right-of-finished stays roughly flat, because fixes on problems already finished offset guesses on converted cap hits. Past about 1.5x the hazard closes hard problems with guesses. The full RL delta added to Think-SFT acts the same way.

- run-08/f2-m02 (grader, carried): A count 'at 16,384' rescored from a 32k run is a different measurement from a native 16k run: rows longer than 16,384 count wrong, while a native run lets grader v3 credit a box already written inside a truncated row (RL 69 % of capped rows, base 17 %, Think-SFT rarely). So 32k-minus-16k is extension finishes only, and models that box mid-reasoning lose a few problems when rescored.

- round-09/sampling-m05 (sampling, carried): Ending is a sampled event: at T 1.0 the stop token is drawn at each point where an answer could close, so lengths have a long tail that the cap cuts off. Raising the cap finishes the cut samples, right at the rate of that model's long finished answers at the same difficulty: high for Think-SFT, whose cut answers are unfinished work, low for the base and RL, whose long answers mostly guess.

- run-04/f2-m05 (sampling, carried): Long untruncated T 1.0 generations drift off-distribution (script switches into Chinese, restarted working) at a rate set by how far the prompt template is from the model's training format. Drifted continuations are almost never right (1 of 24 finish right). Think-SFT in its own ChatML <think> format samples a sharper, on-distribution next-token distribution, so fewer long answers drift, and its trained Answer line removes v3 undercounts; raw-template cue runs keep the drift.

- run-08/f2-m06 (grader, carried): A cap hit casts no vote: a model that runs out of tokens abstains instead of guessing, so its vote approaches pass@k (Think-SFT 241 against 244), while a model that finishes long and wrong spends votes on scattered wrong answers (RL 221 against 240). Turning abstentions into finishes (larger cap, RL directions, transplant) raises single-sample counts more than vote counts, because most converted rows are wrong and dilute the right minority.

- round-09/training-m01 (training, carried): Think-SFT imitated teacher traces inside its ChatML template, opened by <think> and closed by a final answer after the thinking block. Where and how it states the answer is learned conditional on that template. On the raw template with the cue it reasons as well but sometimes misplaces the final answer (on the line after 'Answer:'), which v3 misses. Its own template restores the trained ending: more MATH-500 answers counted, unchanged reasoning length and cap behaviour on hard328.

- round-09/training-m06 (training, carried): The RL update is written onto features that pretraining placed in the early and middle layers: the input directions of RL-Math's top-8 change are the ones math text drives most, and most of RL's change in model output comes from layers 0-15. Adding the directions only in the first or middle third therefore gives more of the hard-problem gain than the last third, whose main distinct job, writing the opening cue, is redundant when the cue is prefilled.

- round-09/grader-m06 (grader, carried): A count at a token cap scores every unfinished answer wrong, hiding whether it was unfinished work or a dead end. Raising the cap adds right answers in proportion to the model's share of unfinished-work cap hits: Think-SFT about one in four, RL one in ten, the base one in sixteen. Scoring the 32k text at 16,384 reproduces a 16k run, so the 32k-minus-16k difference is that yield alone.

- round-10/weights-m06 (weights, carried): Within the top-8 RL directions, the first singular direction of each matrix carries the format and stop part: it cuts cap hits, and at large size stops the model boxing its answer. Directions 2-8 carry the part that raises right answers on finished problems. So rank-1 edits finish without adding right answers, removing direction 1 keeps most of the correctness gain, and overdosing direction 1 produces unboxed answers that are graded wrong.

- round-10/problems-m04 (problems, carried): An edit's effect splits by problem stratum: it adds right answers on mid-difficulty problems (base right in some samples), which MATH-500 and hard328 both hold in similar numbers, while cap-hit changes live only in the long-derivation tail, which MATH-500 holds about a third as densely. So point gains transfer between sets, but a MATH-500 cap-hit change equals the hard328 change times the base's MATH-500/hard328 cap-hit ratio (about 22.5/77).

- round-09/stopping-m04 (stopping, carried): On a hard set part of every model's answers would end past 16,384 tokens, and a cut answer scores zero. A change that leaves the length distribution in place (100 RL steps, the cue on a checkpoint, a new seed or more samples) can move only the precision of finished answers. Step 100 writes cued-base lengths at T 1.0 (4,120 vs 4,008 tokens), so on hard problems it keeps the cued base's cap hits and adds a few right answers.

- run-05/f2-m05 (weights, carried): Imitation (Think-SFT) and RL weight changes are orthogonal (cosine -0.00001) and read different input subspaces, so their effects superpose: Think-SFT supplies high precision on finished answers but no termination drive and runs long; adding a(RL - base) adds RL's finishing push without disturbing SFT's precision, costing only on newly finished hard problems. Prompt format changes how the SFT part is engaged, not finishing, so Think-SFT's cap hits follow the token budget.

- run-08/f2-m05 (grader, carried): Majority vote counts answer strings: the base's wrong answers scatter (only about a quarter repeat), so the right answer is the plurality once per-sample success exceeds about 0.3, and even k leaves ties that a fixed rule breaks about half right. Vote over k therefore rises toward the number of problems whose right answer is the modal string, well below pass@k, with odd k gaining from fewer ties and returns shrinking fast after k = 4.

- round-10/problems-m03 (problems, carried): A code problem needs a short single-function artifact judged by hidden tests. The base's code deficit is mostly answers with no closed code block or cut off, not wrong logic, so any model or edit that writes a closed block recovers most of the gap; the ceiling is set by under-specified MBPP+ tests (about 405 of 538), which RL-Code (401) already nears. On math the matching lever is a terminal answer statement, which the plain base lacks.

- round-09/stopping-m01 (stopping, carried): A cut-off sample writes no answer marker, so it abstains from the plurality vote instead of voting wrong. A vote's gain over one sample therefore scales with the cap-hit share times the precision of finished answers: Think-SFT (29-46 % capped, 80-88 % precise) votes near pass@4, while RL and the 1.5x edit (5-15 % capped) gain less. A longer cap turns abstentions into mostly wrong late answers, so a vote gains far less from it than one sample does.

- run-07/f2-m01 (problems, carried): Each problem needs a derivation of a given length; past the 16,384 cap the answer is cut and scores zero. Extra budget or a finishing weight edit only converts cut answers into finished ones, and a converted answer is right at the rate the model reaches on problems that long and hard: about 25-30 % on hard328, about 45 % on MATH-500's long tail, under 20 % on fresh2026 contest problems. Finished short answers are untouched.

- round-09/training-m03 (training, carried): RL-Zero's group-relative reward gives gradient only on prompts where some rollouts succeed and others fail, so early RL moves the policy on problems the base solves sometimes, mostly short and medium ones, and leaves problems the base rarely solves for late training. By step 100 the gain sits on MATH-500's mid-difficulty problems; on hard problems, where the cued base mostly fails or runs to the cap, step 100 plain is no better than the cued base.

- round-09/training-m04 (training, carried): Pretraining fixed, for each problem, the base's distribution over final values; the cue picks which register samples it but does not move its modal value. A vote converges to that mode, so its ceiling is the problems whose modal value is right, and samples beyond about eight only resolve ties. The plain prompt samples pretraining's terse solution register, whose accuracy falls faster with difficulty than the cued register's, so plain's share of the cued score shrinks on harder sets.

- run-03/f2-m03 (stopping, carried): Whether tokens past a cap add right answers depends on whether a model's long answers are still deriving or already guessing. Think-SFT, trained by imitation, keeps deriving until it stops, so its capped answers are unfinished work that finishes right about a quarter of the time. The base and RL close long answers with asserted numbers, so a longer cap gains them little. In its native <think> format Think-SFT thinks longer, which moves more right answers past 16,384.

- round-10/grader-m06 (grader, carried): Each set holds items no model can be credited on: defective or unparseable golds, LLM-transcribed 2026 statements, and problems no arm ever solves (6 of MATH-500, about 80-90 of hard328). The count's ceiling is the set size minus these, so vote and long-cap gains compress as a model nears it: Think-SFT's vote already sits at pass@4, and extra samples or tokens add only on reachable unsolved items, never on the floor.

- round-10/weights-m01 (weights, carried): The top RL-Math directions write stop and box logits additively: signed size s shifts the log-odds that an answer runs to the cap by a roughly fixed amount per unit, in either sign, on any set. Cap-hit counts therefore move with each set's base cap rate in log-odds, not by a fixed fraction. Overdose costs right answers only in proportion to a set's long unsolved answers, which it forces to finish as guesses.

- run-06/f2-m04 (training, carried): On problems the base can solve, its errors are mostly per-sample slips, drawn by chance and independently at each step. Its remaining errors are misreadings and wrong plans that are set by what pretraining taught about each problem and recur across samples. Majority voting removes the slips by about 5-7 samples and then flattens at the number of problems where the base's modal answer is right, a few below pass@4, however many more samples are drawn.

- run-03/f2-m01 (stopping, carried): A sample that hits the token cap casts no vote, so the cap acts as a free precision filter that discards long, low-precision answers. A vote gains most over one sample when many wrong answers are cut this way (cued base, Think-SFT) and least when a change makes the model finish (top-8 edit, RL delta on Think-SFT, longer cap), because finished guesses then compete with right answers. An odd number of votes removes tie losses.

- round-09/training-m02 (training, carried): Think-SFT copied teacher traces produced under long budgets, and imitation carries no pressure to stop, so its 16,384-token cuts are mid-derivation work, not loops or guesses. More budget turns cut answers right at the problem's difficulty rate (about a quarter on hard328, fewer on 2026 problems). Late finishes are mostly wrong but scattered, so in a vote they seldom beat an existing right answer and add less than to single samples. RL's delta adds stopping, leaving fewer cuts to convert.

- round-10/problems-m06 (problems, carried): An RL run's finishing habit is calibrated to the derivation lengths of its training domain. Code-RL learned to close at code-answer lengths (about 4k tokens), so its directions make math answers stop earlier: harmless on short MATH-500 problems, costly on long hard328 derivations (178 vs Math's 192, at fewer tokens). Math directions, calibrated to long derivations, have no room to act on short code tasks and give a partial gain there. Mixed edits inherit the shorter calibration on long problems.

- run-06/f2-m01 (training, carried): Think-SFT imitates teacher traces in which every stated value is derived and the answer comes only after the work, so it rarely asserts a guess: a sample cut at the cap is unfinished work, not a stall. More budget turns about a quarter of cut samples into right answers on hard sets and more on easy ones; late wrong answers scatter, so the vote keeps gaining. The habit sits in the weights, so the template changes little.

- run-07/f2-m02 (problems, carried): An RL run's top weight directions write a habit for its own domain's answers. For Math-RL that habit is to deliberate, check, and finish with one boxed answer; for Code-RL it is to reason, then finish with one final python block that passes the tests. In its own domain the top-8 edit carries about two thirds of RL's gain at 1x and nearly all of it at 1.5x. On another domain it carries about half as much.

- round-09/sampling-m01 (sampling, carried): Each sample is an independent draw: problem i is solved with a fixed probability p_i, so one cell's count varies by sqrt(sum p_i(1-p_i)), about 5-7 problems on MATH-500 and 6-9 on the 328, and same-seed reruns give new texts because vLLM is not batch-invariant. A stored single cell is one draw. New samples land around the arm's mean, not around the stored count, and a gap of a few problems between single cells is noise.

- round-09/weights-m04 (weights, carried): Moved onto another model that shares the base, the RL-Math difference acts as a finishing operator on that model's own trajectories. It does not add correctness. On Think-SFT it closes long, unfinished but sound work earlier, so cap hits fall and right-of-finished drops toward RL's level. The gain is limited by how much of the recipient's cut work was sound. Prompt or template changes on Think-SFT alone (no delta) leave its finishing rate and precision unchanged.

- round-09/grader-m04 (grader, carried): A count's size depends on the set's difficulty mix: hard328's first 164 problems are much harder than its second half (cued base 65 vs 99), and fresh2026 is harder still. On hard items the opening (cue, step 100, self-opening) moves few problems, while answers past 16k tokens are mostly unfinished or guessed, so cap raises and votes yield less per abstention than on hard328, and plain prompts keep a falling share of the cued count.

- round-10/training-m05 (training, carried): Think-SFT's teacher traces cover competition problems (olympiad-style math and contest code) far more densely than the 3.1 RL prompts, which were filtered to problems the base fails. Imitation transfers whole solution routines for those problem types, not copies of items, so Think-SFT's lead over RL grows with competition difficulty (hard328, 2026 contests) and vanishes on MATH-500; adding the RL difference to it supplies closing, not routines.

- round-10/problems-m05 (problems, carried): Each set has problems that no reweighting of a host's own solution paths reaches (hard328: about 79 the base never solves even after restarts; MATH-500: about 15). Weight edits and their combinations only reweight paths the host already has, so scores saturate below that host's reach: stacking finishing directions adds little once most reachable problems finish, and votes stop near pass@k. Only a host with more reach (Think-SFT) raises the ceiling.

- round-09/sampling-m02 (sampling, carried): A plurality vote counts only committed answers: a cap hit or a missing answer casts no vote, so a right answer facing abstentions wins outright, while one facing scattered wrong values wins only through the tie rule. A model that abstains instead of guessing (Think-SFT) votes close to pass@4. Anything that turns abstentions into finished answers (a longer cap, finishing weights) raises single samples but adds wrong votes, so the vote gains less than the singles.

- round-10/weights-m05 (weights, carried): Math-RL and Code-RL directions share part of their input subspace (overlap 0.22-0.26, random 0.002), and that part writes a reward-general readout: the deliberative opening, hold-on words and finishing. The rest of each change is domain-specific and nearly orthogonal (whole-change cosine under 0.03). Stacking the two edits counts the shared readout twice, which overdoses finishing, and adds each domain remainder once, so math gets Code's remainder only where it overlaps.

- round-12/s1-b (s1): Without the cue, the base at T 0.6 meets hard problems with quick, confident, finished wrong answers. These repeat across samples of the same context, so a plurality vote locks onto them. On easy MATH-500 problems the shared answer is the right one, so the vote ties the cue there. On hard328 it fixes the wrong attractor. The 4,096 cap is secondary: most of these samples finish early (mean about 1,700 tokens per sample).

- round-12/s6-b (s6): RL-Code's top-8 directions hold two separable parts. A low-dose format part (close the code block, stop before the cap) saturates by about 0.5x and fixes about 44 unformatted answers. A dose-graded correctness part raises the pass rate of programs that were already finished. It grows roughly linearly to about 1.5x and adds to the correctness part in Math's directions. About 40 of the 69 problems gained at 1x come from the correctness part.

## t01 (work-3d4e90): How many of the 328 hard problems does Think-SFT answer right in its own chat format at its released sampling setting (T 0.6, top-p 0.95, cap 32,768), one sample, grader v3?

Unit: right answers of 328. Cell: {"model": "Think-SFT (Olmo-3-7B-Think-SFT)", "prompt": "own chat format", "set": "hard328", "n": 328, "sampling": "T 0.6 / top-p 0.95, cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, v3, 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 229 | [213, 244] | Own format at T 1.0 cap 32,768 gave 232/328 (cue 230-235 across seeds); T 0.6 with top-p 0.95 is the released setting, so roughly the same, with some extra risk of loops. |
| reader-2 | 228 | [213, 242] | Think-SFT own format at T 1.0 cap 32,768 scored 232 (cue singles 230-235); T 0.6 is its released setting, but it may loop or cut off a little more, so slightly lower and wider. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 232 | [218, 246] | Theory: a single cell is one seeded draw that regresses to the pooled level of near-identical cells; Think-SFT at cap 32,768 pools at about 232 (own format 232, cue 230/234/235/232), with seed scatter of up to 9-19 per 328. |
| round-10/weights-m03 | - |  | theory says nothing |
| run-03/f2-m04 | 228 | [213, 242] | Theory: the native Think-SFT format ends with a post-think summary that restates the answer, so nothing is lost to the grader; anchored on the paired T 1.0 native cell (232/328) with a small allowance for T 0.6. |
| run-03/f2-m02 | - |  | theory says nothing |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | 237 | [225, 249] | Theory: Think-SFT in its own ChatML format is on-distribution, and a lower temperature sharpens the distribution further, so fewer long answers drift (drifted ones are almost never right); start from the own-format T 1.0 cell at 232/328 and add a few rescued long answers. |
| run-08/f2-m06 | - |  | theory says nothing |
| round-09/training-m01 | 231 | [219, 242] | Theory: in its own (trained) template Think-SFT keeps the trained ending with reasoning length and cap behaviour on hard328 unchanged, so the count stays at the native-format cap-32,768 level (232 at T 1.0, result-dd9239; cue 230-235 per seed), with only seed noise from the released T 0.6 setting. |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | 229 | [215, 243] | Theory: count at 32k = 16k count plus one in four of Think-SFT's unfinished cap hits; the paired T 1.0 own-format run gives about 205 at 16k with about 95 cap hits, so about 205 + 24, and the theory adds nothing about temperature. |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 222 | [205, 238] | Theory's holds_against clause says T 0.6 adds opening-dependent loops and cap hits, so Think-SFT own format drops below its T 1.0 / cap 32,768 count of 232 (result-dd9239). |
| run-05/f2-m05 | 235 | [222, 248] | Theory: prompt format and sampling engage SFT's precision, not finishing, and Think-SFT's cap hits follow the token budget, so at cap 32,768 (about 1 cap hit) it scores like the paired T 1.0 own-format cell (232), give or take seed noise. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | 230 | [216, 243] | Theory: at cap 32,768 almost no derivation is cut, so the score is set by problem length and difficulty, not by sampling; I take the paired T 1.0 own-format cell at 32,768 (232/328) and the cue cells at 32,768 (230-235), widened because the theory says nothing about temperature. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | 231 | [217, 245] | Theory's last clause: in its native <think> format Think-SFT thinks longer and its right answers move past 16,384, so a 32,768 cap captures them; anchored on the native-format T 1.0 cap-32,768 cell (232; 204 at 16,384), theory silent on temperature so the T 1.0 anchor is kept. |
| round-10/grader-m06 | 228 | [214, 241] | Theory's hard328 ceiling (328 minus 80-90 never-solved items, about 238-248) caps the paired T 1.0 own-format 232; the lower temperature only moves reachable items, so the value stays just below 232 and under the ceiling. |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | 229 | [216, 242] | Theory: Think-SFT's 16,384 cuts are unfinished work and the 32,768 cap converts about a quarter of them on hard328, so ~205 at 16k plus ~1/4 of ~90 cuts gives ~229, as in the T 1.0 own-format cell (232); wider because the theory says nothing about T 0.6. |
| round-10/problems-m06 | - |  | theory says nothing |
| run-06/f2-m01 | 231 | [218, 244] | Theory: Think-SFT's derive-then-answer habit sits in the weights and its cut samples are unfinished work, not stalls, so the format and the lower-temperature released setting change little from the paired T 1.0 own-format cell (232/328, result-dd9239). |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 230 | [214, 244] | New samples land around the arm's mean: Think-SFT at cap 32,768 sits at 230-235 at T 1.0 (own format 232, cue 230/234/235/232); the theory's T 0.6 clause (loops put problems near p=0.5) widens the spread beyond the usual 6-9 on the 328. |
| round-09/weights-m04 | 229 | [215, 243] | Theory: template changes on Think-SFT alone leave its finishing and precision unchanged, so the own-format cell sits at Think-SFT's cap-32,768 level (232 own format, 230 cue at T 1.0); the released T 0.6 setting is taken as neutral for a model trained there. |
| round-09/grader-m04 | 228 | [214, 242] | Theory: the opening (prompt format) moves few problems on hard items, and at cap 32,768 Think-SFT's late answers finish, so the count stays near the paired T 1.0 own-format cell (232) with a small allowance for the T 0.6 change, which the theory does not cover. |
| round-10/training-m05 | 230 | [217, 243] | Theory: Think-SFT's hard328 level comes from imitated solution routines, not sampling, so the released T 0.6 setting should land near its own-format T 1.0 cap-32,768 cell (232/328; cue at 32k 230-235). |
| round-10/problems-m05 | 232 | [221, 243] | A sampling setting only reweights Think-SFT's own paths, so the score stays near its reach (pass@4 244); I centre on the paired T 1.0 own-format cell, 232 (result-dd9239). |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | - |  | theory says nothing |
| round-12/s1-b | 231 | [219, 243] | Think-SFT's own format already removes the plain-prompt failure, and T 0.6 changes little: about 232. |
| round-12/s6-b | - |  | no forecast |

## t02 (work-3d4e90): How many of the 500 MATH-500 problems does Think-SFT answer right in its own chat format at its released sampling setting (T 0.6, top-p 0.95, cap 32,768), one sample, grader v3?

Unit: right answers of 500. Cell: {"model": "Think-SFT (Olmo-3-7B-Think-SFT)", "prompt": "own chat format", "set": "MATH-500", "n": 500, "sampling": "T 0.6 / top-p 0.95, cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, v3, 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 472 | [462, 481] | Own format at T 1.0 cap 32,768 gave 474/500 and the cue singles are 457-462 at 16k; T 0.6 should be close to this. |
| reader-2 | 472 | [462, 481] | Own format at T 1.0 cap 32,768 scored 474 on MATH-500; RL barely moves between T 0.6 and T 1.0, so the forecast is near 474 with a small loop risk. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 470 | [460, 479] | Theory: regress toward the pooled level; cue singles at 16k are 457-462 and the larger cap adds about 10, so the pool is about 470 rather than the single 474 draw, with scatter of 5-7 per 500. |
| round-10/weights-m03 | - |  | theory says nothing |
| run-03/f2-m04 | 472 | [462, 481] | Native-format clause (the summary restates the answer, so v3 reads it); anchored on the paired T 1.0 native MATH-500 cell, 474/500 at cap 32,768. |
| run-03/f2-m02 | - |  | theory says nothing |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | 476 | [467, 484] | Theory: in its own format the trained Answer line removes v3 undercounts and a sharper T 0.6 distribution drifts less, so slightly above the own-format T 1.0 474/500, near the ceiling. |
| run-08/f2-m06 | - |  | theory says nothing |
| round-09/training-m01 | 474 | [465, 482] | Theory: the native template restores the trained answer line so v3 counts more MATH-500 answers than under the raw cue, so the count matches the native cap-32,768 cell (474, result-0a0a5a) and sits above the cue singles (457-462). |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | 472 | [462, 481] | Theory: 16k count (~463, as the T 1.0 own-format 464) plus a quarter-to-full yield on Think-SFT's ~25 long answers (+10 at T 1.0), so about 472. |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 466 | [452, 478] | Same T 0.6 loop clause: a few more unfinished answers than the T 1.0 own-format 474/500 (result-0a0a5a), smaller loss on easy MATH-500. |
| run-05/f2-m05 | 474 | [465, 483] | Theory: with the budget fixed at 32,768, cap hits and SFT precision do not change, so this matches the paired own-format T 1.0 cell (474/500). |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | 472 | [462, 481] | Theory: at 32,768 the cut answers in MATH-500's long tail finish (right at about 45 %) and finished short answers are untouched, so the result should match the paired T 1.0 own-format 32,768 cell (474/500), minus a little for the temperature change, which the theory does not cover. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | 473 | [463, 482] | Same native-format clause: at cap 32,768 the long native answers finish (native T 1.0: 464 at 16,384 -> 474 at 32,768), so the forecast stays at the cap-32,768 native level. |
| round-10/grader-m06 | 474 | [464, 482] | Theory's MATH-500 ceiling of 494 (500 minus 6 never-solved items) compresses changes near the paired T 1.0 own-format 474, so the sampling change moves only a few reachable items. |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | 472 | [462, 481] | Theory: few MATH-500 answers are cut at 16k (~25), and the 32,768 cap finishes them at a high rate on easy problems, so ~462 + ~10 ≈ 472, matching the T 1.0 own-format 474. |
| round-10/problems-m06 | - |  | theory says nothing |
| run-06/f2-m01 | 472 | [463, 481] | Theory: the habit is in the weights, so the released setting changes little from the T 1.0 own-format MATH-500 cell at cap 32,768 (474/500, result-0a0a5a). |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 472 | [462, 481] | Arm mean from the paired T 1.0 own-format cap-32,768 cell (474) and the 457-464 cue/16k cells; one draw varies by about 5-7 on MATH-500, widened slightly for the T 0.6 clause. |
| round-09/weights-m04 | 472 | [462, 481] | Same template-invariance clause: Think-SFT's own format at cap 32,768 matches its cue rows (474 at T 1.0), assuming T 0.6 does not change finishing. |
| round-09/grader-m04 | 472 | [463, 481] | Theory: changing the opening and format moves few problems, so the count stays near the paired own-format T 1.0 cap-32,768 cell (474 of 500) on the easy MATH-500 mix. |
| round-10/training-m05 | 473 | [464, 481] | Theory: imitation's routines set the level and MATH-500 shows no competition edge, so T 0.6 should land near the own-format T 1.0 cap-32,768 cell (474/500). |
| round-10/problems-m05 | 473 | [465, 481] | Reweighting by temperature cannot pass Think-SFT's reach on MATH-500 (about 485 given the ~15 problems nothing solves), so I centre near the paired T 1.0 cell, 474 (result-0a0a5a). |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | - |  | theory says nothing |
| round-12/s1-b | 473 | [465, 481] | Own-format MATH-500 is 474 at T 1.0, and T 0.6 changes little. |
| round-12/s6-b | - |  | no forecast |

## t03 (work-f58d89): How many of the 538 HumanEval+/MBPP+ problems does the base model plus RL-Math's and RL-Code's top-8 weight directions (each at 1x) pass, one sample at the first of two new seeds?

Unit: problems passed of 538. Cell: {"model": "base Olmo-3-1025-7B + Math top-8 directions 1x + Code top-8 directions 1x", "prompt": "not stated", "set": "HumanEval+/MBPP+", "n": 538, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> base + Math 1x + Code 1x on HumanEval+/MBPP+ at 2 new seeds

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 403 | [389, 417] | The first seed gave 411, but Code-alone 1.5x gives 399 and RL-Code 401, so expect some regression toward about 400; per-seed spread is about 7. |
| reader-2 | 403 | [388, 418] | 411 at the first seed regresses toward the Code-direction family (386-399) and RL-Code 401; seed noise is about 7-10 of 538. |
| run-05/f2-m06 | 405 | [390, 420] | Theory: summing Math and Code directions gives a larger per-entry change, so less of it is thresholded away in bf16 than with Code alone at 1x; the combined edit stays near its measured 411, with seed noise pulling slightly toward the 399 peak. |
| run-05/f2-m01 | 402 | [387, 417] | Dial part: Math and Code top-8 directions each push termination, so the summed 1x edit sits at the top of the code dial plateau (Code 1x 386, 1.5x 399, 2x 394, sum 411 at the first seed); at a new seed I expect it to fall back toward about 400. |
| run-06/f2-m03 | 403 | [388, 418] | Theory: in-domain Code directions near 1.5x reproduce nearly all of RL-Code's gain (~399-401) and Math's directions add about half on top of an almost saturated 1x Code edit, so the sum sits near RL-Code; the first seed's 411 regresses toward ~403. |
| run-05/f2-m03 | 404 | [389, 419] | Theory: Code directions act in full on code (Code alone 1x 386, 1.5x 399) and Math's directions add about half their in-domain effect through the 0.22-0.26 input-subspace overlap (Math 1.5x on code 368 vs random 331), so roughly 386 + 15-20; the 411 seen at one seed is pulled back toward that. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 401 | [388, 413] | Theory: the 411 was a first-run headline cell and sits above its model's mean; new seeds regress toward the pooled level of nearby code-direction cells (386-399, 1.5+1.5 at 387, RL-Code 401). |
| round-10/weights-m03 | 401 | [386, 416] | Theory: on the base (no imitation change of its own) RL directions act at full strength, so Math+Code 1x keeps Code's full effect near RL-Code; the first seed's 411 is pulled back toward 401/386-399 code-dial values. |
| run-03/f2-m04 | 400 | [386, 414] | Theory: Math directions push a boxed ending that competes with the final code block, so the one-sample 411 should fall back toward the Code-direction level (386-399; 1.5x+1.5x gave 387). |
| run-03/f2-m02 | 401 | [385, 417] | Hazard rises with total direction size: Math 1x + Code 1x already finishes nearly everything on code (cap hits near 0), so with right-of-finished flat the score sits at the finished ceiling seen for 1x-2x Code edits and RL-Code (386-411); the 411 headline is pulled toward that band at a new seed. |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | - |  | theory says nothing |
| run-08/f2-m06 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | 402 | [389, 415] | Theory: the top-8 directions write RL's update onto features pretraining placed in the weights, so the Math+Code 1x+1x gain is a property of the weights and should replicate across seeds. The value pulls the first seed's 411 back toward Code 1.5x at 399 and RL-Code at 401 (result-6776d8, result-a1bf75), with about 7 problems of seed noise. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | 403 | [388, 418] | Theory: directions 2-8 of each reward add right answers on finished problems, and at 1x+1x direction 1 is not overdosed (unlike 1.5x+1.5x: 387, 0 cap hits), so the sum stays near the first-seed 411, shrunk toward Code 1.5x/RL-Code (~400) for a new seed. |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 405 | [391, 419] | A new seed leaves the length distribution in place and moves only precision, so base+Math 1x+Code 1x stays near its 411/538, shrunk slightly for headline selection. |
| run-05/f2-m05 | 402 | [386, 418] | Superposition part: Math's and Code's finishing directions add, which put the earlier seed at 411; on a new seed I expect a regression toward Code-alone 1x (386) and RL-Code (401), since finishing is near saturation. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | 405 | [391, 418] | Theory: Math+Code directions write closed code blocks, so the score sits at the under-specified-MBPP+ ceiling of about 405 of 538 (first seed measured 411, reseeding noise about 8). |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | - |  | theory says nothing |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-10/problems-m06 | 405 | [389, 421] | Theory: on short code tasks Code directions act fully and Math directions add only a partial gain, so the sum sits a little above Code alone at 1x (386); this matches the 411 already measured, pulled slightly toward the mean for a new seed. |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | 401 | [384, 418] | Own-domain top-8 at 1x carries ~2/3 of RL-Code's 84-point gain over cued base 317 (+56) and Math's directions on the other domain carry about half that (+28), summed: 317+56+28 = 401. |
| round-09/sampling-m01 | 406 | [393, 419] | The stored 411 is one draw; new seeds land around the arm's mean, which I shrink a little toward the neighbouring code-direction cells (386-399), with about 7-8 problems of per-draw sd on 538. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | - |  | theory says nothing |
| round-10/problems-m05 | 402 | [387, 417] | Stacking finishing directions adds little once most reachable problems finish, so Math+Code should fall back toward the Code-direction and RL-Code level (~395-401), not hold the one-seed 411. |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | 398 | [383, 413] | Theory: stacking adds the shared readout twice (an extra finishing dose, which the code dial shows is harmless: 1.5x 399, 2x 394) plus Math's code remainder only where the two overlap, so the sum lands about at Code's 1.5x level; the 411 single sample regresses toward that. |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | 407 | [395, 419] | The correctness parts add: Code 1x about 381, plus Math's own correctness (+37 at 1.5x over random) scaled to 1x, minus overlap, about +26, giving about 407; the measured 411 replicates. |

## t04 (work-f58d89): How many of the 538 HumanEval+/MBPP+ problems does the base model plus RL-Math's and RL-Code's top-8 weight directions (each at 1x) pass, one sample at the second of two new seeds?

Unit: problems passed of 538. Cell: {"model": "base Olmo-3-1025-7B + Math top-8 directions 1x + Code top-8 directions 1x", "prompt": "not stated", "set": "HumanEval+/MBPP+", "n": 538, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> base + Math 1x + Code 1x on HumanEval+/MBPP+ at 2 new seeds

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 403 | [389, 417] | Same cell as t03 at another seed: 411 so far, regressed toward the ~400 level of the comparable cells. |
| reader-2 | 403 | [388, 418] | Same cell at another seed: 411 so far, shrunk toward about 400. |
| run-05/f2-m06 | 405 | [390, 420] | Same theory part as t03 (the joint edit loses less to bf16 thresholding than Code alone at 1x), new seed around 411 with regression. |
| run-05/f2-m01 | 402 | [387, 417] | Same dial reasoning as t03 for the second new seed: the summed edit finishes nearly every code answer, so the score sits on the plateau near 400. |
| run-06/f2-m03 | 403 | [388, 418] | Same derivation as t03: Code 1x plus half-strength Math directions reaches about the 1.5x in-domain level, so it lands near RL-Code's 401, with seed noise. |
| run-05/f2-m03 | 404 | [389, 419] | Same theory reading as t03 (Code in full plus about half of Math's effect), at a second fresh seed, so one-sample noise of about 9 on 538. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 401 | [388, 413] | Same as t03: new seed of a notable first cell regresses to its pooled level, about 400, with scatter of about 7 per 538. |
| round-10/weights-m03 | 401 | [386, 416] | Same as t03: full-strength RL directions on the base host, second seed, centred between 411 and the code-dial cells. |
| run-03/f2-m04 | 400 | [386, 414] | Same clause as t03 (the boxed ending competes with the code block); a second seed regresses from 411 toward the Code-alone range. |
| run-03/f2-m02 | 401 | [385, 417] | Same as t03 at the second seed: combined in-domain plus Math directions saturate finishing, right-of-finished flat, so about 400 of 538 with one-sample seed noise. |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | - |  | theory says nothing |
| run-08/f2-m06 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | 402 | [389, 415] | Same theory part as t03, which says the effect lives in the weights and replicates. A second new seed regresses from 411 toward the 399-401 level of the code dial. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | 403 | [388, 418] | Same as t03: combined directions 2-8 keep correctness while direction 1 at 1x+1x only finishes; second new seed, centred between the measured 411 and the ~400 dial plateau. |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 405 | [391, 419] | New seed leaves lengths in place (theory), so near the first seed's 411/538 with seed noise. |
| run-05/f2-m05 | 402 | [386, 418] | Same superposition reading as t03 for the second new seed: about 402, regressed from the 411 first draw. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | 405 | [391, 418] | Theory: closed blocks recover the format gap and the ceiling is about 405 of 538; a new seed regresses from 411 toward that ceiling. |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | - |  | theory says nothing |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-10/problems-m06 | 405 | [389, 421] | Same as t03: Code-calibrated directions plus a partial Math gain on short code answers, 386 plus about 20, with the 411 seen at one seed. |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | 401 | [384, 418] | Same theory arithmetic as t03 at the second seed: 317 + 2/3*84 (Code, own domain) + 1/3*84 (Math, cross-domain at half) = 401. |
| round-09/sampling-m01 | 406 | [393, 419] | Same arm as t03: an independent draw around the arm's mean (about 406), not around the stored 411. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | - |  | theory says nothing |
| round-10/problems-m05 | 402 | [387, 417] | Same stacking-saturation clause as t03: the combination sits near the saturated Code-direction level, about 400. |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | 398 | [383, 413] | Same as t03: a double shared readout plus Code's remainder, with little code-specific remainder from Math, gives about Code at 1.5x (399), with one-sample seed noise. |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | 407 | [395, 419] | Same, second seed. |

## t05 (work-f58d89): How many of the 538 HumanEval+/MBPP+ problems does RL-Zero-Code pass, one sample at the first of the two new seeds?

Unit: problems passed of 538. Cell: {"model": "Olmo-3.1 RL-Zero-Code", "prompt": "not stated", "set": "HumanEval+/MBPP+", "n": 538, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> with RL-Code and Code-alone 1x at the same seeds (411 vs 401 vs 386 so far)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 400 | [387, 413] | RL-Code scored 401/538 at seed 51000000; a new seed adds only sampling noise. |
| reader-2 | 400 | [387, 413] | RL-Code scored 401 of 538 at seed 51000000; a new seed should land near that with about 7-8 points of noise. |
| run-05/f2-m06 | 401 | [387, 415] | Theory: trained checkpoints carry no rounding loss, so RL-Code reproduces its full level of 401 up to seed noise. |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 398 | [387, 409] | Theory: reference draws sit slightly above their own multi-sample mean, so RL-Code's 401 regresses a little on a new seed, with scatter of 5-7 per 500. |
| round-10/weights-m03 | - |  | theory says nothing |
| run-03/f2-m04 | 401 | [389, 413] | Theory: RL installs one terminal marker (the final python block), so RL-Code's 401/538 should hold at a new seed, give or take seed noise. |
| run-03/f2-m02 | - |  | theory says nothing |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | - |  | theory says nothing |
| run-08/f2-m06 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 401 | [389, 413] | New seed changes only precision of finished answers, so RL-Code repeats its 401/538. |
| run-05/f2-m05 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | 401 | [389, 413] | Theory: RL-Code already writes closed blocks and nears the ~405 ceiling, so a new seed stays at its measured 401 within sampling noise. |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | - |  | theory says nothing |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-10/problems-m06 | - |  | theory says nothing |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 401 | [389, 413] | The best estimate of RL-Code's arm mean is its stored single draw (401); a new seed is a fresh draw with an sd of about 7 on 538. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | - |  | theory says nothing |
| round-10/problems-m05 | - |  | theory says nothing |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | - |  | theory says nothing |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | 400 | [388, 412] | RL-Code measured 401; binomial noise only. |

## t06 (work-f58d89): How many of the 538 HumanEval+/MBPP+ problems does RL-Zero-Code pass, one sample at the second of the two new seeds?

Unit: problems passed of 538. Cell: {"model": "Olmo-3.1 RL-Zero-Code", "prompt": "not stated", "set": "HumanEval+/MBPP+", "n": 538, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> with RL-Code and Code-alone 1x at the same seeds (411 vs 401 vs 386 so far)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 400 | [387, 413] | RL-Code scored 401/538 at seed 51000000; a new seed adds only sampling noise. |
| reader-2 | 400 | [387, 413] | RL-Code 401 baseline, new seed. |
| run-05/f2-m06 | 401 | [387, 415] | Trained checkpoints carry no thresholding loss (theory), so RL-Code stays at 401 up to seed noise. |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 398 | [387, 409] | Same as t05: one new seeded draw of RL-Code, centred slightly under the posted 401. |
| round-10/weights-m03 | - |  | theory says nothing |
| run-03/f2-m04 | 401 | [389, 413] | Same as t05: RL-Code's single terminal marker keeps it near 401. |
| run-03/f2-m02 | - |  | theory says nothing |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | - |  | theory says nothing |
| run-08/f2-m06 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 401 | [389, 413] | New seed changes only precision, so RL-Code repeats its 401/538. |
| run-05/f2-m05 | - |  | theory says nothing |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | 401 | [389, 413] | Theory: RL-Code sits just under the ~405 test-set ceiling; second seed repeats 401 within sampling noise. |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | - |  | theory says nothing |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-10/problems-m06 | - |  | theory says nothing |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 401 | [389, 413] | Same arm as t05, an independent draw around 401. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | - |  | theory says nothing |
| round-10/problems-m05 | - |  | theory says nothing |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | - |  | theory says nothing |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | 400 | [388, 412] | Same, second seed. |

## t07 (work-f58d89): How many of the 538 HumanEval+/MBPP+ problems does the base model plus RL-Code's top-8 weight directions alone at 1x pass, one sample at the first of the two new seeds?

Unit: problems passed of 538. Cell: {"model": "base Olmo-3-1025-7B + Code top-8 directions 1x", "prompt": "not stated", "set": "HumanEval+/MBPP+", "n": 538, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> with RL-Code and Code-alone 1x at the same seeds (411 vs 401 vs 386 so far)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 388 | [374, 402] | Code top-8 at 1x scored 386 (1.5x 399, 2x 394); a new seed adds noise around about 388. |
| reader-2 | 389 | [375, 403] | Code top-8 at 1x scored 386; 1.5x scored 399 and 2x scored 394, which puts the true 1x level near 388-390. |
| run-05/f2-m06 | 388 | [373, 403] | Theory: Code-RL's small delta loses more at 1x to bf16 thresholding and peaks at a larger nominal size, so Code-alone 1x stays below RL-Code and the 1.5x 399, near its measured 386. |
| run-05/f2-m01 | 390 | [376, 404] | Dial at size 1 on code: the measured dial is 386, 399 and 394 at 1x, 1.5x and 2x, so 1x at a new seed lands near the plateau, at about 390. |
| run-06/f2-m03 | 386 | [371, 401] | Theory's dial: in-domain top-8 at 1x gives most but not all of RL-Code's gain (1.5x gives nearly all), which matches the measured 386 of 538 (base+cue 317, 1.5x 399); a new seed should land near 386. |
| run-05/f2-m03 | 390 | [375, 405] | Theory: an edit acts in full in its own domain, so Code top-8 at 1x sits on the code dial (386 at 1x, 399 at 1.5x, 394 at 2x); centre is the dial's level near 1x, plus one-sample noise. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 390 | [378, 402] | Theory: one draw that pools with the near-identical code-direction cells (1x 386, 1.5x 399, 2x 394), so a new seed sits near 390 with a scatter of about 7. |
| round-10/weights-m03 | 389 | [374, 404] | Theory: the base takes RL directions at full effect, so Code top-8 1x stays near its measured 386 (1.5x 399, 2x 394). |
| run-03/f2-m04 | 390 | [376, 404] | RL-Code's directions install the code-block ending (no-block answers 34 to 8 at 1x); the level is the 1x/1.5x/2x cells, 386-399. |
| run-03/f2-m02 | 388 | [372, 404] | In-domain Code directions at 1x convert most of the cued base's 27 cap hits / 34 no-code answers into finished ones with flat right-of-finished, which gave 386 at seed 51000000; a new seed gives the same level plus one-sample noise. |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | - |  | theory says nothing |
| run-08/f2-m06 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | 390 | [377, 403] | Theory: the RL-Code top-8 directions carry the update in all layers, so their gain replicates across seeds. The value is near the code dial's 1x 386, 1.5x 399 and 2x 394 (result-a1bf75), with seed noise of about 7. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | 389 | [374, 404] | Theory: top-8 Code directions at 1x finish (direction 1, cap hits 27 -> 9) and add correctness (directions 2-8), giving the measured 386 at 1x, between the cued base 317 and the 1.5x plateau 399; new seed, same level. |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 386 | [373, 399] | New seed leaves the length distribution in place, so Code top-8 1x repeats its 386/538. |
| run-05/f2-m05 | 387 | [371, 403] | Theory: adding RL's directions adds its finishing push, so Code top-8 at 1x lands near its earlier 386, between the cued base (317) and RL-Code (401). |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | 389 | [375, 403] | Theory: Code 1x still leaves about 17 cut-off or no-block answers (9 cap hits, 8 no block), so it stays a little below the ~405 ceiling, near its measured 386. |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | - |  | theory says nothing |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-10/problems-m06 | 388 | [372, 404] | Theory: Code directions are calibrated to code-answer lengths, so on code they act in full, as the code dial showed (1x 386, 1.5x 399); a new seed gives about 386-390. |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | 375 | [358, 392] | Own-domain top-8 edit at 1x carries about two thirds of RL-Code's gain: 317 + 2/3*(401-317) = 373, nudged toward the measured 386 at the old seed. |
| round-09/sampling-m01 | 389 | [376, 402] | The stored 386 is one draw; the arm mean is shrunk slightly toward the 1.5x/2x cells (399, 394), since a gap of a few problems between single cells is noise, with an sd of about 7-8. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | - |  | theory says nothing |
| round-10/problems-m05 | 390 | [375, 405] | Edits saturate below the host's reach: Code directions at 1x/1.5x/2x already sit at 386-399 (result-a1bf75), so 1x lands near that plateau, about 390. |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | 389 | [374, 404] | Theory: Code's top-8 at 1x is one dose of the shared finishing readout plus Code's own remainder, which reproduces the dial's 1x cell (386, between 1x and 1.5x at 399) at a new seed. |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | 380 | [366, 394] | Format part full (+29), correctness part about 2/3 of its 1.5x size (+53 at 1.5x), so about 317 + 29 + 35 = 381; 386 was a slightly high draw. |

## t08 (work-f58d89): How many of the 538 HumanEval+/MBPP+ problems does the base model plus RL-Code's top-8 weight directions alone at 1x pass, one sample at the second of the two new seeds?

Unit: problems passed of 538. Cell: {"model": "base Olmo-3-1025-7B + Code top-8 directions 1x", "prompt": "not stated", "set": "HumanEval+/MBPP+", "n": 538, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> with RL-Code and Code-alone 1x at the same seeds (411 vs 401 vs 386 so far)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 388 | [374, 402] | Code top-8 at 1x scored 386 (1.5x 399, 2x 394); a new seed adds noise around about 388. |
| reader-2 | 389 | [375, 403] | Same as t07, at the second seed. |
| run-05/f2-m06 | 388 | [373, 403] | Same thresholding loss for Code's small delta at 1x (theory), so it stays near 386 at the second seed. |
| run-05/f2-m01 | 390 | [376, 404] | Same dial-at-size-1 reasoning as t07 for the second seed. |
| run-06/f2-m03 | 386 | [371, 401] | Same dial position as t07: Code top-8 at 1x is below the 1.5x full-gain point, so about 386 of 538 at a new seed. |
| run-05/f2-m03 | 390 | [375, 405] | Same in-domain full-effect reading as t07, second seed. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 390 | [378, 402] | Same as t07: a second new seed of Code 1x, regressing toward the pooled code-dial level. |
| round-10/weights-m03 | 389 | [374, 404] | As t07, second seed of the full-strength base response to Code top-8 at 1x. |
| run-03/f2-m04 | 390 | [376, 404] | Same as t07 at the second seed. |
| run-03/f2-m02 | 388 | [372, 404] | Same as t07 at the second new seed. |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | - |  | theory says nothing |
| run-08/f2-m06 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | 390 | [377, 403] | Same as t07: the Code-alone 1x edit at a second seed sits near the dial's 1x to 2x level of 386-399. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | 389 | [374, 404] | Same as t07: Code top-8 at 1x, direction 1 finishing plus directions 2-8 correctness, ~386-399 on the code dial; second new seed. |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 386 | [373, 399] | New seed leaves the length distribution in place, so Code top-8 1x repeats its 386/538. |
| run-05/f2-m05 | 387 | [371, 403] | Same as t07 for the second seed. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | 389 | [375, 403] | Theory: the remaining format misses at 1x keep Code-alone a few points under the ~405 ceiling; second seed near 386-392. |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | - |  | theory says nothing |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-10/problems-m06 | 388 | [372, 404] | Same as t07: Code-calibrated directions on their own domain at 1x, about 386 plus seed noise. |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | 375 | [358, 392] | Same as t07 at the second seed: two thirds of RL-Code's 84-point gain over the cued base 317. |
| round-09/sampling-m01 | 389 | [376, 402] | Same arm as t07, an independent draw around about 389. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | - |  | theory says nothing |
| round-10/problems-m05 | 390 | [375, 405] | Same saturation clause as t07: the Code-direction plateau is about 390. |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | 389 | [374, 404] | Same as t07: a single shared readout plus Code's remainder, around the dial's 386 to 399. |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | 380 | [366, 394] | Same cell, second seed. |

## t09 (work-f58d89): How many of the 328 hard problems does Think-SFT plus RL-Math's top-8 weight directions at 3x answer right, one sample at seed 3,100,000?

Unit: right answers of 328. Cell: {"model": "Think-SFT + RL-Math top-8 directions at 3x", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated (seed 3100000)", "samples": 1, "grader": "not stated"}

> Think-SFT + Math top-8 3x on hard328 at seed 3100000 (232 so far)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 226 | [213, 239] | 232 at seed 3000000, chosen as a headline, so expect regression toward Think-SFT + Math 1.5x (220) and M(2) (~233). |
| reader-2 | 223 | [210, 237] | 232 at the first seed sits above the Think-SFT + Math 1.5x (220) and random 3x (213) cells, so it regresses toward about 222 on a new seed. |
| run-05/f2-m06 | 227 | [214, 240] | Theory: at 3x nominal the top-8 Math edit is mostly realized above the half-ulp threshold, so it acts as a full large edit on Think-SFT, as measured (232); regressed toward 1.5x (220) and full-transplant levels for seed noise. |
| run-05/f2-m01 | 226 | [214, 238] | Dial part: the RL directions make Think-SFT finish answers it would otherwise leave unfinished (209 base, 220 at 1.5x, 232 at 3x, random 213); the first seed's 232 is a single high draw, so I expect it to fall back to about 226. |
| run-06/f2-m03 | 224 | [209, 239] | Theory says sizes past 1.5x commit too early, so 3x should not beat Think-SFT + 1.5x (220) by much; the single 232 regresses toward ~224 (Think-SFT alone 209, random 3x 213). |
| run-05/f2-m03 | 226 | [214, 238] | Theory: Math directions act in full on hard math on any host, so the edit keeps its gain over Think-SFT (232 vs random 3x 213 at seed 3,000,000; Think-SFT mean 209); at a new seed the 232 regresses toward about 209 + 17. |
| run-02/f2-m04 | 228 | [216, 240] | The theory says the RL difference makes Think-SFT finish, which raises single scores above Think-SFT's 209 (16k), so the replication should land near the 232 already measured, allowing for seed noise. |
| round-09/grader-m01 | 225 | [211, 238] | Theory: 232 was the best size picked from a sweep, so it sits above its mean; a new seed regresses toward the pooled Think-SFT+edit level (1.5x 220, random 213, M(2) 233), with scatter of up to 9-19 per 328. |
| round-10/weights-m03 | 226 | [214, 238] | Theory: on Think-SFT the RL push has about a quarter of its effect and is weak but stable to 4x, so 3x top-8 sits a few points above Think-SFT's 209 (random 213, 1.5x 220), with the 232 pulled back by regression. |
| run-03/f2-m04 | 226 | [213, 239] | Math directions install a boxed terminal marker that makes Think-SFT finish (cap hits 82 to 60); the seed-3,000,000 value was 232, regressed slightly toward 220 at 1.5x, with Think-SFT seed spread of about 10. |
| run-03/f2-m02 | 226 | [213, 239] | Math directions at 3x on Think-SFT convert many of its ~94 cap hits (60 left at 3x) but past 1.5x the hazard closes hard problems with guesses, so right stays near the transplant plateau (220 at 1.5x, 232 at 3x, 231.5 for M(2)); the selected 232 regresses a little at a new seed. |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | - |  | theory says nothing |
| run-08/f2-m06 | 227 | [216, 238] | Theory: RL directions turn Think-SFT's cap-hit abstentions into finishes, which raises single-sample counts above Think-SFT's 209 (random 213). I centre a little below the first seed's 232 for regression. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | 226 | [213, 239] | Theory: RL-Math's top-8 directions add right answers through early and middle-layer features on any host. On Think-SFT, 1.5x gave 220 and 3x gave 232 (result-6776d8), against a random edit's 213. A new seed regresses toward about 226, with hard328 seed spread of about 8. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | 227 | [215, 239] | Theory: at 3x direction 1 makes Think-SFT finish (cap 82 -> 60) while overdose starts to cost boxed answers, so directions 2-8 lift it only to about the 232 measured at seed 3000000, minus some regression for a new seed (Think-SFT seeds span 201-219). |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 229 | [218, 240] | New seed moves only precision, so Think-SFT + Math top-8 3x stays near its 232/328 (60 cap hits kept), slight regression. |
| run-05/f2-m05 | 227 | [215, 239] | Theory: RL's finishing push adds to Think-SFT's precision (Think-SFT 209 at T 1.0, 16k; the 2x transplant averages 233); I regress the 232 one-sample draw toward that for a new seed. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | 222 | [209, 235] | Theory: a finishing edit only turns cut answers into finished ones, at 25-30 % right on hard328; Think-SFT is at 209 with 94.5 cap hits and the 3x edit leaves 60, so 209 + 0.27 x 35 = about 218, blended with the 232 measured at the other seed. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | 227 | [215, 238] | Theory's hard328 ceiling of about 238-248 compresses one-sample highs, so a new seed falls back from 232 toward the Think-SFT-plus-edit range of about 225-233 and stays under the ceiling. |
| round-10/weights-m01 | 228 | [216, 240] | The theory's 'overdose costs right answers only in proportion to long unsolved answers' applies: Think-SFT's long answers are mostly unfinished work, not loops, so 3x mainly cuts cap hits (82 to 60) at little cost. That keeps the new seed near the first 232, minus some regression toward the 1.5x (220) and random-3x (213) cells. |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | 227 | [215, 239] | Theory: RL's delta adds stopping, so Think-SFT's unfinished 16k cuts (94.5 -> 60) finish and some are right; the first sample gave 232, and a new seed should fall back a little toward the 1.5x/transplant level (~220-232). |
| round-10/problems-m06 | 226 | [212, 240] | Theory: Math directions are calibrated to long derivations, so on hard328 they keep adding to Think-SFT (209; 1.5x 220, 3x 232 at one seed); a new seed pulls back toward about 226. |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 226 | [214, 238] | The stored 232 is one draw at seed 3,000,000; the new seed lands around the arm mean, shrunk toward the 1.5x (220) and M(2) (233) cells, with an sd of 6-9 on the 328. |
| round-09/weights-m04 | 226 | [212, 240] | The RL-Math directions on Think-SFT act only as a finishing operator, so the gain is capped by Think-SFT's sound cut work (~209 at 16k plus ~20 recoverable, as in the full transplant at ~232); the first 232 is expected to regress slightly on a new seed. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | 229 | [216, 242] | Theory: adding the RL difference to Think-SFT supplies closing, not routines, so the 3x top-8 edit should sit at the closing-saturated level of its first seed (232) and of M(2) (229-237), above Think-SFT's 209. |
| round-10/problems-m05 | 229 | [218, 240] | The edit only reweights Think-SFT's paths, so it stays below Think-SFT's pass@4 of 244; I expect a new seed to sit near the saturated transplant level (M(2) mean 233, edit 232), slightly regressed. |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | 226 | [214, 238] | Theory: Math's directions carry the reward-general finishing readout, and that helps Think-SFT, whose losses are unfinished answers (random 3x 213, Math 1.5x 220); the 232 single sample regresses toward the middle of those. |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | 229 | [215, 243] | Math correctness part at 3x adds to Think-SFT (213 random 3x); 232 replicates within noise. |

## t10 (work-739554): How many of the 500 MATH-500 answers hit the token cap when the base model has RL-Math's top-8 weight directions subtracted (size -1) and is prompted with the cue, one sample?

Unit: cap hits of 500. Cell: {"model": "base Olmo-3-1025-7B - 1.0 x top-8 RL-Math directions (cell m11)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "v3"}

> m11 base - 1.0 x top-8 RL-Math directions, cue, MATH-500 n 500, readout cap hits

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 40 | [31, 50] | The odd shard had 20 cap hits of 250; the even shard should be similar, giving about 40 of 500. |
| reader-2 | 40 | [29, 52] | The odd-problem shard had 20 cap hits of 250, so doubling gives about 40, plus binomial noise. |
| run-05/f2-m06 | 40 | [28, 54] | Theory: the -1 edit is partly thresholded, so it acts smaller than nominal and cap hits rise only modestly; scaled from the finished odd shard's 20 of 250. |
| run-05/f2-m01 | 41 | [29, 53] | Negative s lengthens answers: cap hits rise above the cued base's 27 of 500. The finished half had 20 of 250, so doubling gives about 40. |
| run-06/f2-m03 | 41 | [30, 53] | Theory: subtracting the finishing directions removes completion before the cap, so cap hits rise above the cued base's ~27 per 500; the odd-problem shard already shows 20 of 250, so about 40 for all 500. |
| run-05/f2-m03 | 41 | [31, 52] | Theory: the subtracted Math edit acts in full on MATH-500 (in-domain), as size -1 raised cap hits on hard328; the measured odd shard has 20 of 250, so about twice that over 500. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 40 | [30, 51] | Theory: shards are seeded draws of the same weights; shard 1 gave 20 of 250 cap hits, so the full 500 pools at about 40, plus shard scatter. |
| round-10/weights-m03 | 41 | [30, 53] | Theory: the base responds fully to RL directions, so subtracting them raises cap hits (hard328 96 vs 77); the odd half already shows 20 of 250, and the even half should be similar. |
| run-03/f2-m04 | 40 | [29, 52] | Removing RL's terminal-marker directions leaves the base's mixed endings; shard 1/2 had 20 cap hits of 250, doubled for 500. |
| run-03/f2-m02 | 41 | [30, 53] | Size -1 lowers the stop hazard, raising cap hits above the cued base's 27; the measured odd half has 20 of 250, so doubling gives about 41 with Poisson noise on the even half. |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | 40 | [31, 50] | The theory treats stopping as a sampled event, so cap hits are a per-sample tail rate; the odd half's 20 of 250 (8 %) should repeat on the even half, giving about 40 of 500. |
| run-04/f2-m05 | 40 | [28, 54] | Theory: raw-template cue runs keep their drift rate, so the unmeasured shard drifts and caps at the same rate as the measured shard (20 of 250), which doubles to about 40 of 500. |
| run-08/f2-m06 | 41 | [31, 53] | Theory read in reverse: removing the RL directions turns finishes back into abstentions. The odd shard measured 20 of 250 cap hits, so I double it for the full set. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | 40 | [29, 52] | Theory: subtracting the directions removes the early and middle-layer features, while the late-layer job (writing the cue) does not matter because the cue is prefilled. The value doubles the finished shard's 20 cap hits out of 250 (work-739554) to the full 500. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | 40 | [31, 51] | Theory: subtracting direction 1 removes the stop part, raising cap hits above the cued base's 27 on MATH-500; the odd shard already shows 20 of 250, so about twice that over 500. |
| round-10/problems-m04 | 34 | [27, 42] | Theory's cap-hit rule: the hard328 change at size -1 (77 -> 96, +19) times the MATH-500/hard328 ratio 22.5/77 gives +5.6, so about 28 per 500 (14 per 250) for the unfinished shard, added to the 20 already counted on the odd shard. |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-05/f2-m05 | 41 | [30, 54] | Theory: subtracting RL's finishing directions removes the termination drive, so cap hits rise above the cued base's 27; the odd shard already shows 20/250, so I double it to about 41 of 500. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | 41 | [30, 53] | Theory: removing the finishing directions (size -1) turns finished answers back into cut ones (on hard328 cap hits went 77 to 96), and the odd shard already shows 20 of 250, so I double it to about 40. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | - |  | theory says nothing |
| round-10/weights-m01 | 39 | [31, 48] | Fixed log-odds shift per unit of size: on hard328, size -1 moves cap hits 77 to 96 (+0.30 logit). Applied to the cued base's 27/500 on MATH-500, that gives about 36/500, or about 18 on the unrun shard 0, added to the 20 measured on shard 1. |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | 40 | [30, 52] | The theory says the top-8 edit makes the model finish, so the reversed edit (size -1) should stop it finishing (hard328: 96 cap hits against the base's 77). The odd shard already shows 20 cap hits of 250, so I doubled that for 500. |
| round-09/training-m02 | 41 | [30, 53] | Theory: RL's delta adds stopping, so subtracting it removes stopping and raises cap hits; the odd shard has 20 of 250, so about 41 of 500. |
| round-10/problems-m06 | 40 | [30, 52] | Theory: removing the Math finishing calibration lets fewer answers close, but most MATH-500 derivations are short, so the cap-hit rate stays near the measured half (20 of 250), doubled. |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 40 | [32, 48] | Shard 1/2 gave 20 cap hits of 250; the rerun shard 0/2 is an independent draw at the same rate, so the total is about 40, with binomial plus problem-split spread. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 41 | [30, 53] | Set-composition part of the theory: the interleaved MATH-500 shards have the same difficulty mix, so the full count is about twice shard 1/2's 20 cap hits of 250. |
| round-10/training-m05 | - |  | theory says nothing |
| round-10/problems-m05 | - |  | theory says nothing |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | 41 | [30, 53] | Theory: subtracting the directions removes the shared finishing readout, so cap hits rise above the cued base's 27 (hard328 at size -1: 96 against 77); the done shard's 20 of 250 doubles to about 40. |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | - |  | no forecast |

## t11 (work-739554): How many of the 500 MATH-500 problems does the base model with RL-Math's top-8 weight directions subtracted (size -1), prompted with the cue, answer right under grader v3, one sample?

Unit: right answers of 500. Cell: {"model": "base Olmo-3-1025-7B - 1.0 x top-8 RL-Math directions (cell m11)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "v3"}

> 188/250 right v3

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 376 | [362, 389] | The odd shard got 188/250 right v3; doubling gives about 376, with binomial noise of about 7 on the other half. |
| reader-2 | 376 | [363, 389] | The odd shard had 188/250 right under v3; the even shard should match, giving about 376 of 500. |
| run-05/f2-m06 | 375 | [358, 391] | Same partial realization of the -1 edit (theory); scaled from the finished shard's 188 of 250, below cued base 410. |
| run-05/f2-m01 | 376 | [363, 389] | Negative s lengthens answers, unboxes them and lowers correctness below the cued base's 410. The finished half had 188 of 250, so doubling gives about 376, plus binomial noise from the half still running. |
| run-06/f2-m03 | 376 | [361, 391] | Theory: removing the finishing directions loses answers in the rewarded form (fewer boxed answers, more cap hits) and drops the score below the cued base's 410; the odd-problem shard shows 188 of 250, so about 376 of 500. |
| run-05/f2-m03 | 376 | [362, 390] | Theory: the size -1 Math edit acts in full in domain, lowering right answers from the cued base's 410; the odd shard measured 188/250, so the total is about 2 x 188 with noise from the even shard. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 376 | [364, 388] | Theory: the other half is a fresh draw at the same pooled rate as 188/250, so about 376 of 500, with scatter of 5-7 per 500 (wider for the half-set). |
| round-10/weights-m03 | 375 | [360, 390] | Full base response to the subtracted directions; the odd half gave 188/250, so about twice that over 500. |
| run-03/f2-m04 | 376 | [362, 390] | With the RL marker removed, endings become plain 'Answer: X' lines, which v3 reads; shard 1/2 scored 188/250, doubled. |
| run-03/f2-m02 | 376 | [360, 392] | Lower hazard at size -1 leaves more answers unfinished (below the cued base's 410); the odd half scored 188/250, doubled to 376 with binomial and half-difficulty noise on the other 250. |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | 375 | [358, 391] | Theory: same drift rate in both shards of this raw-template cue run (drifted answers are wrong), so double the measured shard's 188/250 right. |
| run-08/f2-m06 | 375 | [359, 391] | The extra abstentions from removing the directions lower single-sample right answers; the odd shard's 188/250 doubles to about 376. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | 376 | [360, 392] | Same theory part as t10: losing the early and middle features costs right answers with the cue prefilled. The value doubles the finished shard's 188 of 250 right under v3 (work-739554), with binomial and shard noise. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | 376 | [362, 390] | Theory: removing the top-8 subtracts the stop/format part (141 of 250 answers unboxed, but v3 reads 'Answer: X') and the correctness part, so the score falls below the cued base's 410; the odd shard's 188/250 doubles to about 376. |
| round-10/problems-m04 | 360 | [342, 378] | Theory says point changes transfer between sets: hard328 at size -1 loses 14.0 points (164 -> 118), so MATH-500 gets 410 - 70 = 340 (170 per 250) for the unfinished shard, added to the 188/250 already measured on the other shard. |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-05/f2-m05 | 376 | [361, 391] | Removing the finishing push costs answers (hard328 at -1 fell from 164 to 118); the odd shard has 188/250, so I double it to about 376. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | 376 | [360, 392] | Theory: on math the lever is a terminal answer statement; m11 keeps one (141 of 250 plain 'Answer: X') so it stays near the cued-base level, and the odd shard's 188/250 doubles to about 376. |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | 378 | [362, 394] | Theory: only the extra cut answers (about 13 more than the cued base's 27) are lost, at the 45 % long-tail rate, which would give about 404; the odd shard's measured 188/250 shows a larger loss, so I double that half. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | 374 | [358, 390] | Under the theory, the uncreditable items (6 never-solved ones on MATH-500, plus unparseable answers) fall about equally in each half, so the even half should mirror shard 1/2's 188/250: about twice 188, a little lower. |
| round-10/weights-m01 | 377 | [363, 391] | Measured 188/250 on shard 1. For shard 0, the theory's log-odds shift gives about 19 cap hits (scored wrong); the other ~231 finished answers are taken at shard 1's 81.7 % right, giving about 189. |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | 376 | [361, 391] | The theory says the reversed edit cuts finishing, which costs right answers relative to the cued base's 410. The odd shard's 188/250 doubled gives 376, with half-to-half sampling noise added. |
| round-09/training-m02 | 376 | [358, 392] | Theory: the base's cut answers are failed solves (not unfinished right work), so the cap hits gained by removing the stopping delta count as wrong; doubling the odd shard's 188/250 gives ~376. |
| round-10/problems-m06 | 376 | [360, 392] | Theory: short MATH-500 problems leave little room for the finishing calibration, so accuracy follows the measured shard (188/250) doubled. |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 376 | [364, 388] | Shard 1/2 gave 188/250; the other half is an independent draw around the same per-problem rates, about 188, so the total is about 376 with an sd of about 6-7. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 375 | [360, 390] | Set-composition part of the theory: the interleaved shards share a difficulty mix, so the full count is about twice shard 1/2's 188/250 right under v3. |
| round-10/training-m05 | - |  | theory says nothing |
| round-10/problems-m05 | 375 | [361, 389] | Removing directions only reweights the base's own paths (score bounded by its reach); doubling the measured odd-problem shard of 188/250 gives about 375. |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | 376 | [360, 392] | Removing the finishing readout costs answers against the cued base's 410 (more cap hits and unboxed answers); the done shard's 188 of 250 doubles to about 376. |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | - |  | no forecast |

## t12 (work-8ea654): How many of the 538 HumanEval+ and MBPP+ problems does Think-SFT (no reward) pass with the Code cue at T 1.0, one sample?

Unit: problems passed of 538. Cell: {"model": "Think-SFT (Olmo-3-7B-Think-SFT)", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0, top-p not stated, cap not stated (seed 51000000)", "samples": 1, "grader": "not stated"}

> HumanEval+ and MBPP+ (538), Code cue and Math cue, T 1.0, 1 sample, seed 51000000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 372 | [330, 410] | Between the cued base (317) and RL-Code (401): Think-SFT is trained on code traces but at T 1.0 and a 16k cap it hits the cap often, so the interval is wide. |
| reader-2 | 392 | [345, 430] | No Think-SFT code row exists yet; imitation was level with RL on math (and on MMLU-Pro+BBH), so near RL-Code 401, but cap hits and code-block format risk widen the low side. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-10/weights-m03 | 398 | [368, 425] | Theory: Think-SFT's correctness covers every domain in its traces (code included), so it should reach about RL-Code's 401, well above the cued base's 317. |
| run-03/f2-m04 | 368 | [338, 398] | Theory: under the raw template Think-SFT sometimes does not end on the gradable marker (here the final python block) and runs long, so it scores below RL-Code's 401. |
| run-03/f2-m02 | - |  | theory says nothing |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | 372 | [338, 405] | Theory: a raw-template cue keeps Think-SFT off its trained format, so some long answers drift, but code answers are short; between the cued base (317) and RL-Code (401), closer to RL as Think-SFT's sharper distribution was on MMLU/BBH. |
| run-08/f2-m06 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-05/f2-m05 | 385 | [355, 412] | Theory: Think-SFT brings high precision on finished answers, and short code answers rarely reach the cap, so it scores near RL-Code's 401 and well above the cued base's 317. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | 390 | [366, 410] | Theory: Think-SFT writes closed final code blocks, so it recovers most of the base's format gap (317) and lands just under the ~405 MBPP+ ceiling, minus a few long answers cut off at T 1.0. |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | - |  | theory says nothing |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-10/problems-m06 | - |  | theory says nothing |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/weights-m04 | 385 | [345, 425] | Theory says prompt changes on Think-SFT alone leave finishing and precision unchanged, so the Code-cue and Math-cue cells should be equal; the level comes from Think-SFT matching RL on other domains (RL-Code 401). |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | 392 | [362, 418] | Theory: Think-SFT's lead over RL vanishes on problems below competition difficulty, and HumanEval+/MBPP+ are easy, non-contest code, so Think-SFT should land near RL-Code's 401, not above it. |
| round-10/problems-m05 | 400 | [365, 432] | Only a host with more reach (Think-SFT) raises the ceiling, so Think-SFT should reach about RL-Code's 401 or more on code, with format and cap risk widening the interval. |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | - |  | theory says nothing |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | 375 | [335, 415] | Think-SFT has the format part from imitation but only part of the reward-driven correctness gain. |

## t13 (work-8ea654): How many of the 538 HumanEval+ and MBPP+ problems does Think-SFT (no reward) pass with the Math cue at T 1.0, one sample?

Unit: problems passed of 538. Cell: {"model": "Think-SFT (Olmo-3-7B-Think-SFT)", "prompt": "Math cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0, top-p not stated, cap not stated (seed 51000000)", "samples": 1, "grader": "not stated"}

> HumanEval+ and MBPP+ (538), Code cue and Math cue, T 1.0, 1 sample, seed 51000000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 362 | [318, 403] | The math cue did about as well as the code cue on the base for code (326 vs 317); Think-SFT may drift more toward math-style output, so slightly below t12. |
| reader-2 | 385 | [335, 425] | The Math cue matched the Code cue on the base (326 vs 317), so similar to t12, a bit lower and wider because of format risk. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-10/weights-m03 | 375 | [330, 415] | Same coverage claim: Think-SFT is right on code even under the Math cue, minus some format and code-block loss from the math-style prompt. |
| run-03/f2-m04 | 345 | [310, 380] | A math framing pushes a boxed or prose ending that competes with the final code block, so the Math cue loses more answers to format than the Code cue does (t12). |
| run-03/f2-m02 | - |  | theory says nothing |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | 355 | [315, 392] | Theory: drift rises with distance from the training format; the Math cue sits further from the code task than the Code cue, so more drift and a lower pass count than t12. |
| run-08/f2-m06 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-05/f2-m05 | 380 | [350, 408] | Theory: the prompt changes how the SFT part is engaged, not finishing, so with the Math cue Think-SFT stays close to its Code-cue score (own format tied the cue on math). |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | 382 | [354, 406] | Theory: the score depends on writing a closed block, not on the cue's domain; Think-SFT mostly still writes one under the Math cue, but a few more answers lose the block, so it lands a little below the Code-cue cell and under the ~405 ceiling. |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | - |  | theory says nothing |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-10/problems-m06 | - |  | theory says nothing |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/weights-m04 | 385 | [345, 425] | Same prompt-invariance clause: the Math cue gives Think-SFT the same pass count as the Code cue. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | 386 | [352, 415] | Same as t12 (on easy code the theory gives Think-SFT no lead over RL-Code's 401); Think-SFT already opens with 'Okay', so the Math cue should change little, with a slightly lower centre for the off-domain cue. |
| round-10/problems-m05 | 385 | [345, 422] | Same host-reach clause as t12, a little lower because the Math cue does not fit code problems. |
| round-09/sampling-m02 | - |  | theory says nothing |
| round-10/weights-m05 | - |  | theory says nothing |
| round-12/s1-b | - |  | no forecast |
| round-12/s6-b | - |  | no forecast |

## t14 (work-f33794): How many of the 328 hard problems does the untrained base model with the cue get right under a plurality vote over 6 samples per problem?

Unit: right answers of 328 (vote over 6). Cell: {"model": "base Olmo-3-1025-7B", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 6, "grader": "not stated"}

> cued base, 2 new samples per problem first (vote over 6)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 196 | [188, 205] | Cued base vote over 4 is 192 (195 after restart); on MATH-500 going from 4 to 6 samples added about 7, and less is expected on hard328, where the base has no right sample on many problems. |
| reader-2 | 197 | [188, 207] | The cued base's vote over 4 is 192 (pass@4 207); on MATH-500, going from 4 to 6 samples added about 1.5 points, so about +4-5 here. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m04 | 199 | [189, 209] | Capped samples abstain instead of adding wrong values (the cued base caps about 77 of 328), so votes keep gaining as more samples finish: about +5 over the vote-over-4 count of 192-195, like MATH-500's rise from 449 to 457 between 4 and 6 samples. |
| round-09/grader-m01 | 196 | [188, 204] | Theory: multi-sample statistics regress to the pooled level; the cued base's vote over 4 pools at 192-195 on the 328, and two more samples add a few problems at most (pass@4 is 207). |
| round-10/weights-m03 | - |  | theory says nothing |
| run-03/f2-m04 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | - |  | theory says nothing |
| run-08/f2-m06 | 198 | [189, 207] | Theory: the cued base abstains at the cap often, so more votes move it toward pass@k. It also finishes long and wrong, so the gain is modest: about +6 over the vote over 4 (192), like MATH-500's 449 -> 457 from 4 to 6 samples. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 197 | [187, 207] | More samples keep the cued base's cap hits and only sharpen finished-answer precision, so the vote over 6 rises a little above the vote over 4 of 192-195 (as MATH-500 449->457). |
| run-05/f2-m05 | - |  | theory says nothing |
| run-08/f2-m05 | 198 | [190, 206] | The theory says the vote climbs toward the count of problems whose right answer is the modal string, stays well below pass@k, and returns shrink fast after k=4 (even k=6 still leaves ties). So from the cued base's vote-4 of 192 (pass@4 205) it adds only about 6, scaled from MATH-500's vote 4 to vote 6 step of 449 to 457. |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 198 | [189, 207] | Vote gain = cap-hit share x finished precision plus the scattered-slip gain (holds_against 5d032f): the cued base (~23 % capped, ~64 % precise) got 192-195 from 4 votes against pass@4 207, so 2 more abstaining-or-scattered samples add about 4-6, as 4->6 added ~7 on MATH-500. |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | 198 | [190, 206] | The theory says a vote converges to the base's pretrained modal value and that samples beyond 4 only break ties ('a few problems from 4 to 9', with 57% of vote failures being ties), so the cued base's vote over 4 on hard328 (192) gains a few problems at 6, like MATH-500's +7.4 from 4 to 6. |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | 197 | [189, 205] | Theory: extra samples add only on reachable unsolved items, never the floor (79-100 items the base never solves); the base's vote over 4 is 192 against pass@4 of 207, so two more samples add only a few of those 15. |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | 199 | [191, 207] | The theory says that by about 5-7 samples majority voting has removed the base's per-sample slips and levels off a few below pass@4 (base cue hard328 pass@4 205-207, vote over 4 192, result-5c961a/knowledge-dab63f), so a vote over 6 lands near that plateau at about 199-203; I put it slightly below because on MATH-500 the vote kept climbing from 6 to 12 samples (result-1c9e40). |
| run-03/f2-m01 | 198 | [189, 207] | The theory says the vote gains most for the cued base, because its many cap hits (about 70 per sample) cast no vote and so drop long wrong answers. Starting from its hard328 vote over 4 (192), I added the 4-to-6 gain seen on MATH-500 (449.2 to 456.6); 6 is even, so tie losses remain. |
| round-09/training-m02 | - |  | theory says nothing |
| round-10/problems-m06 | - |  | theory says nothing |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 197 | [189, 205] | With independent draws at fixed p_i, adding 2 samples to the 4-sample vote (192) raises the plurality modestly; pass@4 of 207 caps the gain on the 328. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 196 | [188, 204] | Theory: on hard items votes yield little per abstention, so going from 4 to 6 samples adds only a few problems over the cued base's vote over 4 (192, 195 after restart), staying under its pass@4 of 207. |
| round-10/training-m05 | - |  | theory says nothing |
| round-10/problems-m05 | 196 | [188, 205] | Votes stop near pass@k: base vote over 4 is 192 (195 after restart) against pass@4 207, so 6 samples add only a few problems. |
| round-09/sampling-m02 | 197 | [189, 205] | Cap hits cast no vote, so the cued base's right answers keep winning against its abstentions as k grows: vote over 4 is 192 (pass@4 207), and two more samples add about 5, like 449 to 457 from k=4 to k=6 on MATH-500. |
| round-10/weights-m05 | - |  | theory says nothing |
| round-12/s1-b | 195 | [187, 203] | The cue context still has some agreeing wrong answers on hard problems, so the vote saturates: 192-195 at 4, about the same at 6. |
| round-12/s6-b | - |  | no forecast |

## t15 (work-8b4030): How many of the 500 MATH-500 problems does Think-SFT plus twice the RL-Math weight change (RL-Math minus base) answer right, one sample?

Unit: right answers of 500. Cell: {"model": "M(2): Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 466 | [456, 476] | Think-SFT cue singles score 457-462 and M(1) 467; M(2) finishes more but is slightly less precise, so about 466. |
| reader-2 | 468 | [458, 477] | Think-SFT cue singles score 457-462 and a=1 scored 467; a=2 adds finishing, which matters less on MATH-500, so about 468. |
| run-05/f2-m06 | 469 | [459, 479] | Theory: a full-delta merge at a=2 sits far above the half-ulp threshold, so it acts at nominal size; MATH-500 lands just above a=1 (467) and Think-SFT's 457-462. |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | 468 | [459, 476] | Theory: the RL-Math change acts in full on its own domain on the Think-SFT host, so 2x lands at or slightly above a=1's 467 and Think-SFT's 457-462 on MATH-500, close to the ceiling. |
| run-02/f2-m04 | 467 | [457, 476] | The RL difference turns Think-SFT's capped samples into finished answers, so the single score rises a few points above Think-SFT's 457-464 at 16k. |
| round-09/grader-m01 | 468 | [459, 477] | Theory: one seeded draw around the pooled level of near-identical Think-SFT+delta cells (a=1 467, Think-SFT singles 457-462), with scatter of 5-7 per 500. |
| round-10/weights-m03 | 468 | [458, 477] | Theory: a weak but stable response on Think-SFT, no breakdown at a=2, so M(2) on MATH-500 stays near a=1's 467 and Think-SFT's 457-462. |
| run-03/f2-m04 | 466 | [456, 476] | The RL delta installs one boxed terminal marker, removing Think-SFT's raw-template ending on an unread line (about 4 per sample); from Think-SFT cue singles of 457-462, plus 4 (a=1 gave 467). |
| run-03/f2-m02 | 466 | [456, 476] | The full RL delta on Think-SFT acts like the dial: on MATH-500 Think-SFT has few cap hits, so finishing gains are small and at 2x (past 1.5x) some are guesses; right stays near a=1's 467 and above Think-SFT's 457-462. |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | 465 | [456, 474] | Theory: the raw-template cue keeps Think-SFT's v3 undercount (about 4 per sample, Answer line not boxed) and its drift, so M(2) lands near Think-SFT + cue (457-462) plus the finishing gain seen at a=1 (467). |
| run-08/f2-m06 | 468 | [458, 477] | Theory: the transplant turns abstentions into finishes, which raises single counts over Think-SFT's 457-462 at cap 16,384 (a=1 scored 467). |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | 478 | [466, 490] | Theory says the edit's gain sits in the mid-difficulty stratum and transfers between sets: M(2) adds about 22.5 problems (+6.9 points) over Think-SFT on hard328, so Think-SFT's MATH-500 single 459.5 plus a similar gain, held down by the near-ceiling on MATH-500. |
| round-09/stopping-m04 | - |  | theory says nothing |
| run-05/f2-m05 | 468 | [458, 477] | Superposition: 2(RL-base) finishes Think-SFT's roughly 25 MATH-500 cap hits without lowering its precision (singles 457-462, a=1 467), losing only a little on newly finished hard problems. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | 465 | [456, 474] | Theory: twice the RL change mostly converts Think-SFT's roughly 25 MATH-500 cap hits (single samples 457-462) into finished answers, right at about 45 %; halving the cap hits gives about +6, so about 465 (a=1 gave 467). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | 468 | [459, 477] | Near the MATH-500 ceiling of 494 the theory says gains compress, so M(2)'s +7-point hard328 gain shrinks to a few items over Think-SFT's 457-462 (467 at a=1). |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | 466 | [456, 475] | Theory: RL's delta adds stopping, so the few MATH-500 Think-SFT cuts (~25 at 16k) finish under the cap at the easy-problem rate, moving ~461 up to the a=1 level (~467). |
| round-10/problems-m06 | 463 | [452, 474] | Theory: the Math delta's long-derivation calibration has no room to act on short MATH-500 problems, so M(2) stays near Think-SFT's level at a 16k cap (457-464). |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 469 | [460, 477] | Arm mean from neighbouring cells (Think-SFT + 1x delta 467, Think-SFT 457-462), with M(2)'s hard328 lead mostly saturated on MATH-500; one draw varies by about 5-7. |
| round-09/weights-m04 | 468 | [459, 477] | The delta closes Think-SFT's unfinished sound work (cue singles 457-462 at 16k, ~474 when it is let finish at 32k), minus a small precision drop toward RL; a=1 scored 467. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | 466 | [456, 475] | Theory: no Think-SFT lead on MATH-500, and the RL difference only adds closing, so M(2) should sit just above Think-SFT's singles (457-462) and near the a=1 cell (467). |
| round-10/problems-m05 | 468 | [459, 477] | The edit reweights Think-SFT's paths, so the score saturates below its MATH-500 reach (~485); M(1) is 467 and Think-SFT singles 457-462, so M(2) lands at about 468. |
| round-09/sampling-m02 | 468 | [459, 477] | Finishing weights turn abstentions into answers and so raise single samples: M(2) should sit above Think-SFT's 457-462 and near a=1's 467 on MATH-500. |
| round-10/weights-m05 | 468 | [457, 479] | Theory: the RL change's shared readout makes Think-SFT finish (cap hits fall), but MATH-500 has few cut-off answers to recover, so it lands near a=1's 467, above Think-SFT's 457 to 462. |
| round-12/s1-b | 469 | [460, 477] | Think-SFT cue 457-462, plus a few finished answers from M(2). |
| round-12/s6-b | - |  | no forecast |

## t16 (work-8b4030): How many of the 328 hard problems does Think-SFT plus twice the RL-Math weight change answer right in its fourth sample (seed 3,300,000)?

Unit: right answers of 328. Cell: {"model": "M(2): Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated (seed 3,300,000)", "samples": 1, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 233 | [222, 244] | The first three M(2) hard328 samples scored 234, 229 and 237 (mean 233.3). |
| reader-2 | 233 | [221, 245] | M(2) hard328 samples so far are 234, 229 and 237 (mean 233.3), with single-sample seed noise of about 7. |
| run-05/f2-m06 | 233 | [221, 245] | The a=2 merge is realized at nominal size (theory), so a fourth sample matches the earlier M(2) hard328 samples 234/229/237. |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | 233 | [222, 244] | Theory: the in-domain RL-Math change acts in full on hard328, so the fourth sample matches the first three (234, 229, 237; mean 233.3). |
| run-02/f2-m04 | 233 | [222, 244] | The RL difference raises single scores (finishing): the fourth sample should match M(2)'s earlier singles 234/229/237, against Think-SFT's 209. |
| round-09/grader-m01 | 233 | [222, 244] | Theory: a new seed of the same weights regresses to the pooled mean of M(2)'s samples (234/229/237, mean 233.3), with scatter of up to 9-19 per 328. |
| round-10/weights-m03 | 233 | [222, 244] | Stable dose response with no breakdown at 2x: the fourth sample matches samples 1-3 (234, 229, 237). |
| run-03/f2-m04 | 233 | [222, 244] | The terminal marker from the RL delta keeps M(2) finishing; its earlier hard328 samples were 234/229/237. |
| run-03/f2-m02 | 233 | [222, 244] | M(2) converts Think-SFT's cap hits at flat-ish right-of-finished, giving 234/229/237 on its first three seeds; the fourth sample is drawn from the same level (mean 233.3) with one-sample noise. |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | 233 | [223, 243] | Theory: a raw-template cue run at a fixed cap and temperature keeps the same drift, so a fourth sample repeats M(2)'s single-sample rate (234, 229, 237). |
| run-08/f2-m06 | 233 | [224, 242] | M(2)'s single-sample counts after its abstentions are converted are 234, 229 and 237 (mean 233.3), so the fourth sample should land near that mean. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 233 | [222, 244] | A new seed leaves M(2)'s length distribution in place, so sample 4 matches samples 1-3 (234/229/237). |
| run-05/f2-m05 | 233 | [222, 244] | Superposition gain: the three M(2) samples so far are 234/229/237 (mean 233.3, +7.4 over Think-SFT), so the fourth seed should land near their mean. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| run-07/f2-m01 | 231 | [219, 243] | Theory: M(2) converts about 40 of Think-SFT's 94.5 cut answers at 25-30 % right (209 to about 220); I blend that with the three measured M(2) samples at the same setting (234, 229, 237). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | 233 | [223, 242] | One more sample of M(2) under the theory's ceiling of about 238-248 should sit at the mean of its first three samples (234, 229, 237). |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | - |  | theory says nothing |
| round-09/training-m02 | 233 | [222, 244] | Theory: the RL delta turns Think-SFT cuts into finishes at the same rate on every seed, so the fourth sample should match the first three (234, 229, 237; mean 233.3). |
| round-10/problems-m06 | 233 | [222, 244] | Theory: the Math delta is calibrated to long derivations, so it keeps its gain on hard328; the fourth sample should match samples 1-3 (234, 229, 237). |
| run-06/f2-m01 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 233 | [221, 245] | Samples 234/229/237 give an arm mean of 233.3; the 4th sample is an independent draw around it with an sd of about 7 on the 328. |
| round-09/weights-m04 | 233 | [222, 244] | The finishing operator gives a steady per-sample level, bounded by Think-SFT's sound cut work; M(2) samples so far are 234, 229 and 237. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-10/training-m05 | 233 | [221, 245] | Theory: the RL difference adds closing on top of Think-SFT's routines, which is stable across seeds, so take the mean of M(2)'s three hard328 samples (234/229/237). |
| round-10/problems-m05 | 233 | [222, 243] | The edit saturates below Think-SFT's reach: M(2) samples so far are 234/229/237, mean 233, below pass@4 244. |
| round-09/sampling-m02 | 233 | [224, 242] | Finishing weights raise single samples: M(2)'s singles are 234/229/237 (mean 233.3, about 7 points over Think-SFT), and a fourth seed should land at the same level. |
| round-10/weights-m05 | 233 | [222, 244] | The doubled finishing readout gives Think-SFT a steady gain; samples 1 to 3 of M(2) were 234, 229 and 237, so the fourth falls around their mean of 233. |
| round-12/s1-b | 233 | [223, 243] | Mean of three samples is 233.3. |
| round-12/s6-b | - |  | no forecast |

## t17 (work-8b4030): How many of the 328 hard problems does Think-SFT plus twice the RL-Math weight change get right under a plurality vote over 4 samples per problem?

Unit: right answers of 328 (vote over 4). Cell: {"model": "M(2): Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": 4, "grader": "not stated"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 246 | [239, 253] | M(2) vote over 3 was 246 and Think-SFT's vote over 4 is 241; the 4th sample changes little. |
| reader-2 | 247 | [239, 255] | M(2)'s vote over 3 is 246; Think-SFT's vote over 4 (241) sits at or above its votes over 3 (231-241), so a fourth sample adds about 0-3. |
| run-05/f2-m06 | 246 | [238, 254] | The a=2 merge is realized at nominal size (theory); the vote over 4 tracks the measured vote over 3 (246). |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | 246 | [239, 253] | Theory: the in-domain full effect gives the same per-sample level, so the vote over 4 stays near the vote over 3 (246), above Think-SFT's 241. |
| run-02/f2-m04 | 247 | [240, 254] | Vote gains shrink once samples finish: M(2)'s vote over 3 is only +13 over its singles (246) while Think-SFT's is +32, so a fourth sample adds about 1. |
| round-09/grader-m01 | 247 | [239, 254] | Theory: the vote over 4 regresses to the pooled level of the vote over 3 (246) and of Think-SFT's votes (231-241); a fourth sample moves it by only a few problems. |
| round-10/weights-m03 | 246 | [238, 254] | Stable M(2) samples (mean 233) with a vote over 3 of 246; a fourth sample barely moves the vote. |
| run-03/f2-m04 | 247 | [239, 255] | Consistent boxed endings make votes agree; M(2)'s vote over 3 was 246 (Think-SFT's vote over 4 is 241), plus one more sample. |
| run-03/f2-m02 | 247 | [239, 254] | With most answers finished by the raised hazard, the vote over 3 was 246; adding a fourth sample of the same model moves the plurality by only a few problems. |
| run-08/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-04/f2-m05 | 246 | [239, 253] | Theory: drifted cut answers are almost never right and abstain rather than vote wrong, so the vote over 4 is close to pass@k; the vote over 3 is 246, and a fourth sample adds little. |
| run-08/f2-m06 | 247 | [240, 254] | Theory: converted abstentions are mostly wrong and dilute the vote. The vote gain over Think-SFT (241) is therefore much smaller than the single-sample gain (+24); the vote over 3 is 246, so a fourth sample adds about 1. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 246 | [238, 254] | One more sample only adds precision on finished answers, so the vote over 4 stays near the vote over 3 of 246. |
| run-05/f2-m05 | 246 | [238, 254] | High precision plus finishing makes the vote close to pass@k; the vote over 3 is 246 and Think-SFT's vote over 4 is 241, so I expect about 246. |
| run-08/f2-m05 | 248 | [241, 255] | Going from odd k=3 (vote 246) to even k=4 adds ties that a fixed rule breaks only about half right, so per the theory's diminishing returns past k=4 the vote over 4 gains just a few problems over 246. That matches Think-SFT's vote-4 of 241 against its vote-3 range of 231 to 241. |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 248 | [241, 255] | M(2) is capped less than Think-SFT (~17 % vs 29 %) with lower precision (~72 %), so by cap share x precision its vote gains less than Think-SFT's +32; the vote over 3 is already 246 from singles near 233, and a 4th sample adds a few more. |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | - |  | theory says nothing |
| round-10/grader-m06 | 247 | [242, 252] | Theory: the vote of a Think-SFT-like model already sits near pass@k and near the about 238-248 ceiling, so a fourth sample adds at most a few items to the vote-over-3 count of 246. |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | 247 | [240, 254] | The theory says the RL delta on Think-SFT makes it finish, so the vote gains little: vote over 3 was 246 against a single-sample mean of 233, far less than Think-SFT's +32. Going to an even 4 votes brings back tie losses, so I put it at about the vote over 3. |
| round-09/training-m02 | 247 | [240, 254] | Theory: late finishes are scattered and seldom beat a right answer that is already there, so a fourth sample adds little to the vote over 3 (246). |
| round-10/problems-m06 | 247 | [239, 255] | Theory: Math calibration keeps M(2)'s hard328 gain (vote over 3 = 246); adding a fourth sample moves the vote by only a few answers. |
| run-06/f2-m01 | 249 | [242, 256] | Theory: late wrong answers scatter, so the vote keeps gaining; adding a fourth sample to M(2)'s vote over 3 (246) adds a few more right answers. |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 247 | [240, 254] | The vote over 3 is 246; one more independent draw changes the plurality on only a few near-tie problems (Think-SFT's vote over 4 sat at the top of its vote-over-3 range). |
| round-09/weights-m04 | 246 | [239, 254] | Precision drops toward RL, so votes gain less than Think-SFT's do; the vote over 3 is 246, and a fourth sample adds little. |
| round-09/grader-m04 | 246 | [239, 253] | Theory: a vote's yield per abstention on hard328 is modest, so the fourth sample adds about nothing to M(2)'s vote over 3 (246). |
| round-10/training-m05 | 246 | [238, 254] | Theory: closing on top of routines; M(2)'s vote over 3 is 246 against Think-SFT's 241 vote over 4, and a fourth sample adds little. |
| round-10/problems-m05 | 246 | [239, 252] | Votes stop near the host's pass@k: M(2)'s vote over 3 is 246, near Think-SFT's pass@4 of 244 and the ~249 reach, so a 4th sample adds about nothing. |
| round-09/sampling-m02 | 248 | [241, 255] | M(2)'s finished extra answers add wrong votes, so its vote gains less over its singles (233 to about 248) than Think-SFT's +32; the vote over 3 is 246 and a fourth sample adds about 2. |
| round-10/weights-m05 | 247 | [239, 255] | The finishing readout turns Think-SFT's cap hits into answers, so the vote nears pass@k; the vote over 3 was 246, and a fourth sample adds about 0 to 2. |
| round-12/s1-b | 246 | [239, 253] | Vote over 3 is 246. Agreeing wrong answers keep the fourth sample from adding. |
| round-12/s6-b | - |  | no forecast |

## t18 (work-8b4030): How many of the 328 hard problems does Think-SFT plus twice the RL-Math weight change answer right with the token cap at 32,768, one sample at seed 3,000,000?

Unit: right answers of 328. Cell: {"model": "M(2): Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "T not stated, top-p not stated, cap 32,768 (seed 3,000,000)", "samples": 1, "grader": "not stated"}

> M(2) at cap 32,768 on hard328, seed 3,000,000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 243 | [233, 253] | M(2) at 32k on seed 3,010,000 scored 245; on seed 3,000,000 Think-SFT at 32k scored 230 vs 234, so slightly lower. |
| reader-2 | 244 | [234, 254] | M(2) at cap 32,768 scored 245 at seed 3,010,000 (232 at 16k); seed 3,000,000 scored 234 at 16k, and the larger cap adds about 10-13. |
| run-05/f2-m06 | 243 | [233, 253] | The a=2 merge is realized at nominal size (theory); at cap 32,768 the other seed gave 245, against Think-SFT's 230-235. |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | 243 | [233, 252] | Theory: the in-domain change acts in full, and the larger cap adds the late finishes; seed 3,010,000 gave 245 at 32,768 (232 at 16,384), and this seed gave 234 at 16,384, so about 243. |
| run-02/f2-m04 | 242 | [232, 252] | The 32k cap and the RL difference both make samples finish, raising the single score: 245 at the other seed, adjusted down because Think-SFT itself scores 230 at this seed against 234 there. |
| round-09/grader-m01 | 244 | [234, 254] | Theory: one seeded draw; seed 3,000,000 gave 234 at 16k, the cap adds about 12 (as 232->245 on the other seed), and 245 was a first draw that may sit high, so about 244 with scatter of 9-19 per 328. |
| round-10/weights-m03 | 241 | [231, 251] | Theory: the RL change cuts Think-SFT's cap hits by only about 20 % and mostly makes it finish, so at 32,768 M(2) lands a few points above Think-SFT's 230 on this seed (other seed 245 vs 234). |
| run-03/f2-m04 | 243 | [233, 253] | With RL's marker, almost every answer reaches a gradable end by 32,768 tokens (0 cap hits at seed 3,010,000: 245); Think-SFT at this seed and cap is 230. |
| run-03/f2-m02 | 243 | [233, 252] | At cap 32,768 the delta's raised hazard lets M(2) finish nearly every answer (0 cap hits, 245 at seed 3,010,000, +11-13 over its 16k view); at seed 3,000,000, where Think-SFT scored 230 vs 234, expect a similar or slightly lower count. |
| run-08/f2-m02 | 243 | [234, 252] | Theory: 32k = native-16k count (M(2) 16k samples 229-237, about 233) plus extension finishes only; the other seed's 32k run added 13 over its 16k view (232 -> 245), and Think-SFT is weaker at seed 3,000,000 (230 vs 234), so about 233 + 12 - 2. |
| round-09/sampling-m05 | 246 | [236, 255] | Raising the cap finishes M(2)'s cut samples at Think-SFT's matched-difficulty long-answer rate (~25 %): 234 at 16,384 on this seed plus about 0.25 x ~50 cap hits gives ~246, in line with the other seed going from 232 to 245. |
| run-04/f2-m05 | 242 | [232, 252] | Theory: answers that drift past 16,384 tokens (raw-template cue) rarely finish right, so a cap of 32,768 adds only the undrifted unfinished answers; the other seed gave 245. |
| run-08/f2-m06 | 244 | [236, 252] | Theory: a larger cap converts M(2)'s ~50 cap hits into finishes and raises the single count. At 16,384 this seed gives 234; the other seed rose 232 -> 245 at 32,768 with 0 cap hits. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | 245 | [235, 255] | Theory: 16k view reproduces a 16k run (M(2) ~233 mean, ~54 cap hits), and the 32k-minus-16k difference is the Think-SFT-like yield of one in four of those cap hits (+13, as at seed 3,010,000: 232 -> 245). |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 242 | [232, 252] | New seed at the same cap changes only precision, so near the other cap-32,768 seed's 245 (0 cap hits). |
| run-05/f2-m05 | 242 | [231, 252] | At cap 32,768 the delta still adds right answers beyond finishing (other seed: 245 vs Think-SFT 234); Think-SFT at this seed scores 230, so about 242. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 245 | [237, 253] | A longer cap turns M(2)'s ~56 cut-offs into late answers, which helps one sample: the seed-3,010,000 run went 232 -> 245, and seed 3,000,000 reads 234 at 16,384, so about +11-13. |
| run-07/f2-m01 | 247 | [237, 257] | Theory: the 32,768 budget finishes M(2)'s roughly 55 cut answers at 16,384, and about 25-30 % of them are right on hard328: about 233 + 14 = 247 (the other seed went 232 to 245). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | 246 | [236, 256] | Think-SFT-derived capped answers are unfinished derivations that finish right about a quarter of the time: M(2) at 16,384 on this seed is ~234 with ~54 cap hits, +1/4 of those gives ~247 (the 3,010,000 seed went 232 -> 245 with 56 cap hits). |
| round-10/grader-m06 | 241 | [233, 249] | Theory: the longer cap adds only reachable items that were cut at 16k, and the gain compresses at the about 238-248 ceiling, so this seed lands near the other seed's 245 and slightly lower. |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | 244 | [234, 254] | The theory says a longer cap makes the model finish; M(2) at 32,768 finishes almost every answer. I took its 16,384-cap mean of about 233 plus the +13 that seed 3,010,000 gained at 32,768 (232 to 245). |
| round-09/training-m02 | 245 | [235, 255] | Theory: at 32,768 a quarter of M(2)'s ~50 16k cuts convert (fewer cuts than Think-SFT's because the RL delta stops early), so the seed's 16k score of ~234 + ~12 ≈ 245, as on seed 3,010,000 (232 -> 245). |
| round-10/problems-m06 | 242 | [232, 252] | Theory: long-derivation calibration means extra tokens finish M(2)'s long hard328 answers; the other seed at cap 32,768 gave 245 (Think-SFT 230 at this seed). |
| run-06/f2-m01 | 247 | [237, 257] | Theory: a larger budget turns about a quarter of cut samples into right answers on hard sets; M(2) at 16,384 is about 233 with about 56 cap hits, plus about 14 gives about 247 (the other seed went 232 to 245). |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 245 | [233, 257] | The first cap-32,768 M(2) sample gave 245, and its 16k view (232) matched the arm's 16k mean, so 245 is the arm mean; the same seed still gives new text, with an sd of about 7. |
| round-09/weights-m04 | 234 | [222, 246] | At cap 32,768 Think-SFT already finishes its sound work (230 at this seed, 2 cap hits), so a delta that only shortens adds about nothing; the other seed's 245 sets the upper end. |
| round-09/grader-m04 | 244 | [235, 252] | Theory: on hard328 a cap raise turns Think-SFT-type unfinished answers into some right ones, as M(2) went 232 to 245 at seed 3,010,000; apply the same gain to the 16k mean of about 233. |
| round-10/training-m05 | 244 | [233, 254] | Theory: at cap 32,768 Think-SFT's unfinished routines finish anyway, so the closing the delta adds gains less; the other seed gave 245 (232 at 16k), and this seed's M(2) at 16k was about 234. |
| round-10/problems-m05 | 242 | [233, 250] | A longer cap lets Think-SFT's reach show, but the edit cannot pass the ~249 reach ceiling; the other seed at 32k gave 245. |
| round-09/sampling-m02 | 244 | [235, 252] | A longer cap turns cut-off answers into finished ones and raises single samples: at seed 3,010,000 the 32,768 cap gave 245 against 232 at 16,384, and this seed's 16,384 sample is about 234. |
| round-10/weights-m05 | 242 | [232, 252] | With the readout doubled almost no answer is cut off at 32,768, so the larger cap adds the right answers past 16,384 (other seed: 245 against Think-SFT's 234); this seed's Think-SFT is 230, about 4 lower, so about 242. |
| round-12/s1-b | 243 | [235, 251] | The other seed at 32k gave 245. Allow for seed noise. |
| round-12/s6-b | - |  | no forecast |

## t19 (work-dc9359): How many of the 136 contest problems published in 2026 does Think-SFT with the cue get right under a plurality vote over 4 samples with the token cap at 32,768?

Unit: right answers of 136 (vote over 4). Cell: {"model": "Think-SFT (Olmo-3-7B-Think-SFT)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "T not stated, top-p not stated, cap 32,768", "samples": 4, "grader": "not stated"}

> Think-SFT + cue vote over 4 at token cap 32,768

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 82 | [74, 90] | The 16k vote is 75/136 with 46% cap hits; at 32k about a quarter of the cut answers finish right (as on hard328), raising singles by about 10, so the vote rises by about 7. |
| reader-2 | 81 | [73, 89] | Think-SFT's fresh2026 vote at 16k is 75 with 46% cap hits; the larger cap lifted the hard328 vote by 6 (238 to 244), and fresh has more cut answers left to finish. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m04 | 79 | [72, 86] | At 32k the abstaining capped samples (about 62 per sample at 16k) become mostly wrong scattered answers, so the vote gains only a little over its 75 at 16k while singles rise (as on hard328: vote 238 to 244). |
| round-09/grader-m01 | - |  | theory says nothing |
| round-10/weights-m03 | - |  | theory says nothing |
| run-03/f2-m04 | 82 | [74, 90] | Accuracy follows whether an answer reaches its marker: Think-SFT's fresh2026 cap hits (46%) are unfinished work that a 32,768 cap lets end with an answer; from the 16,384 vote of 75, plus a hard328-like gain scaled up for the higher cap-hit rate. |
| run-03/f2-m02 | - |  | theory says nothing |
| run-08/f2-m02 | 80 | [73, 87] | Theory: the 32k-minus-16k difference is only extension finishes, and Think-SFT rarely boxes mid-reasoning, so its 16k vote over 4 (75) gains only from late finishes; that gain is damped under the vote as on hard328 (238 -> 244), so about +5. |
| round-09/sampling-m05 | 80 | [72, 88] | The extra tokens finish Think-SFT's ~62 cut samples per run at ~20-25 %, so singles gain ~13; because three in four late answers are wrong, the vote gains only about a third of that (as on hard328: 238 to 244), so 75 + ~5. |
| run-04/f2-m05 | 79 | [72, 86] | Theory: under the raw-template cue many of Think-SFT's cut fresh2026 answers drift (104 of 544 switch script) and drifted continuations almost never finish right, so the cap of 32,768 adds only a few votes to the 75 at cap 16,384. |
| run-08/f2-m06 | 77 | [70, 84] | Theory: Think-SFT's cap hits abstain, so its vote at 16,384 (75) is already near pass@k. Answers converted by the 32,768 cap are mostly wrong, so the vote rises only slightly (hard328 vote: 238 -> 244, while singles rose about 22). |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | 82 | [75, 89] | Theory's yield of one in four of Think-SFT's ~62 cap hits per sample lifts singles by ~15; under the vote the gain is smaller, as on hard328 (+6 vote for +22 singles), so the 16k vote of 75 becomes about 82. |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 80 | [73, 87] | Cut answers score zero, so lifting the cap to 32,768 finishes some of Think-SFT's ~62 cap hits per sample; the vote gains about a quarter of the single-sample gain over its 16k vote of 75, as on hard328 (238->244). |
| run-05/f2-m05 | 80 | [72, 88] | Theory: Think-SFT's cap hits follow the budget; doubling it finishes most of its 46% cut samples, some of them right (on hard328 the vote went 238 to 244), so the 16k vote of 75 rises to about 80. |
| run-08/f2-m05 | 78 | [71, 85] | The vote is capped by the count of problems with a modal right answer and already sits near pass@4 (75 at 16,384). Longer answers turn abstentions into answers, but many are wrong and split the vote, so it rises only about 3, scaled from hard328 where the cap-32,768 vote gained 6 against 22 for single samples. |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 78 | [72, 84] | A longer cap turns abstentions into mostly wrong late answers, so the vote gains far less than single samples do (hard328: vote +6 vs singles +22); starting from the 16,384 vote of 75, that gives about +3. |
| run-07/f2-m01 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | 81 | [73, 89] | Quarter-of-capped-answers-finish-right rule raises each fresh2026 sample from ~60 by ~15 (about 62 cap hits per sample at 16,384); the vote, already near pass@4 through abstention at 75, gains less, as on hard328 (238 -> 244), giving ~81. |
| round-10/grader-m06 | 82 | [75, 89] | Theory: the 32k cap adds reachable items cut at 16k (Think-SFT hits the cap on 46 % of fresh samples), while LLM-transcribed statements stay a floor, and the vote stays near pass@4; this lifts the 16k vote of 75 by about 7, like hard328's 238 to 244. |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | 79 | [72, 86] | The theory says a longer cap makes Think-SFT finish, so finished guesses compete and the vote gains less than single samples do. On hard328 the 32k vote rose only 6 while single samples rose 22, so I moved the fresh2026 vote at 16,384 (75) up by only a few. |
| round-09/training-m02 | 78 | [72, 85] | Theory: on 2026 problems fewer than a quarter of cuts convert, and late finishes add less to a vote than to single samples, so the 16k vote of 75 rises by only ~3. |
| round-10/problems-m06 | - |  | theory says nothing |
| run-06/f2-m01 | 84 | [77, 91] | Theory: cap-cut answers are unfinished and late wrong answers scatter, so the vote keeps gaining over the 16,384 vote of 75 as each sample gains about 15. |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 80 | [73, 87] | The 16k vote is 75; by the hard328 base rate the late finishes add about a quarter of the single-sample gain to the vote, about +5. |
| round-09/weights-m04 | 80 | [73, 87] | Think-SFT's cut work is long but sound, so a 32k cap converts some of its ~62 cap hits per sample to right answers; the 16k vote of 75 rises by about as much as hard328's did (238 to 244). |
| round-09/grader-m04 | 79 | [72, 86] | Theory: on fresh2026 (harder than hard328) cap raises and votes yield less per abstention, so the vote over 4 rises only a few problems above its cap-16,384 value of 75. |
| round-10/training-m05 | 81 | [72, 90] | Theory: Think-SFT's lead grows on 2026 contests because its long routines are unfinished at 16k (cap hits 46%); the 16k vote is 75, and the extra tokens should finish some of them, as on hard328 (vote 238 to 244). |
| round-10/problems-m05 | 80 | [73, 87] | Think-SFT is the host with more reach; at 32k its unfinished answers finish, and the vote, which stops near pass@k, rises a little over the 16k vote of 75. |
| round-09/sampling-m02 | 78 | [71, 85] | Think-SFT abstains rather than guessing, so its vote at 16,384 (75) is already near pass@4; the 32,768 cap adds wrong votes along with right ones, so the vote gains only about 3 (hard328: +1.8 points against +6.7 for singles). |
| round-10/weights-m05 | - |  | theory says nothing |
| round-12/s1-b | 78 | [71, 85] | Late answers at 32k often share wrong values (hard328 vote gained only +6), so the vote gains little over 75. |
| round-12/s6-b | - |  | no forecast |

## t20 (work-dc9359): Averaged over 4 single samples, how many of the 136 contest problems published in 2026 does Think-SFT with the cue answer right with the token cap at 32,768?

Unit: right answers of 136, mean of 4 single samples. Cell: {"model": "Think-SFT (Olmo-3-7B-Think-SFT)", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "T not stated, top-p not stated, cap 32,768", "samples": 4, "grader": "not stated"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768 from the same text

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 70 | [63, 77] | The 16k single mean is 60.0 with about 62 cap hits per sample; if about 25% of those finish right at 32k, as on hard328, the mean rises to about 70. |
| reader-2 | 70 | [63, 77] | Singles average 60 of 136 at 16k with about 62 cap hits; if about 20% of the cut answers finish right at 32,768 (hard328: 23 of 93), that adds about 10. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m04 | 70 | [64, 77] | A 32k cap makes capped samples finish and raises single scores: about a quarter of fresh2026's roughly 55 long answers come out right (23 of 93 on hard328), taking the 16k mean of 60 to about 70. |
| round-09/grader-m01 | - |  | theory says nothing |
| round-10/weights-m03 | - |  | theory says nothing |
| run-03/f2-m04 | 71 | [64, 78] | Same clause: from the 16,384 single mean of 60, about a quarter of roughly 60 cut answers per sample finish right at 32,768 (hard328: 23 of 93). |
| run-03/f2-m02 | - |  | theory says nothing |
| run-08/f2-m02 | 71 | [64, 78] | Theory: Think-SFT rarely boxes inside truncated rows, so the rescored 16k equals native 16k (mean 60 of 136) and 32k adds only extension finishes: about 63 capped rows per sample at roughly 18 % finishing right (hard328: 23 of 93) gives about +11. |
| round-09/sampling-m05 | 72 | [65, 79] | At 16,384 Think-SFT averages 60 of 136 with ~62 cap hits per sample; the theory says those finish right at its matched-difficulty long-answer rate (~20 %, since the fresh tail is hard), which adds about 12. |
| run-04/f2-m05 | 66 | [60, 72] | Theory: of about 62 cut answers per sample, the drifted ones stay wrong (1 of 24) and only undrifted unfinished work finishes right, so about +6 over the mean of 60 at cap 16,384. |
| run-08/f2-m06 | 69 | [63, 76] | Theory: a larger cap raises single counts more than votes. Think-SFT abstains on about 62 of 136 per sample at 16,384 (mean 60 right); I assume about 15 % of those convert to right answers, which adds about 9. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| round-09/grader-m06 | 75.5 | [69, 82] | Theory: 16k single mean 60.0 (cap hits 45.6 %, ~62 per sample) plus one in four of those cap hits finishing right at 32k (+15.5). |
| round-10/weights-m06 | - |  | theory says nothing |
| round-10/problems-m04 | - |  | theory says nothing |
| round-09/stopping-m04 | 73 | [66, 80] | Cut answers score zero: of ~62 cap hits per sample at 16k about a fifth to a quarter finish right at 32,768 (hard328: 23 of 93), lifting the 16k mean of 60. |
| run-05/f2-m05 | 70 | [63, 77] | Budget part: about 62 cut samples per run finish at 32k, and roughly 1 in 6 of them is right (hard328 single samples went +22), so the 16k mean of 60 rises to about 70. |
| run-08/f2-m05 | - |  | theory says nothing |
| round-10/problems-m03 | - |  | theory says nothing |
| round-09/stopping-m01 | 69 | [63, 75] | Think-SFT is ~46 % capped on fresh2026 at 16,384 (single ~60); the longer cap finishes those answers and a minority (~15-20 %) come out right, which lifts single samples by about 9, as on hard328 (+22 from 93 cut-offs). |
| run-07/f2-m01 | 70 | [64, 76] | Theory: on fresh2026 the cut answers converted by the 32,768 budget are right under 20 % of the time; Think-SFT's 16,384 single samples average 60 with about 62 cap hits each, so 60 + 0.17 x 62 = about 70. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-03/f2-m03 | 75 | [68, 82] | Think-SFT keeps deriving, so about a quarter of its ~62 cap hits per sample at 16,384 finish right at 32,768: 60.0 + ~15 = ~75 per sample mean. |
| round-10/grader-m06 | 70 | [63, 77] | Theory: long-cap gains come only from reachable cut items; at about a quarter of roughly 62 cut answers per sample finishing right (the hard328 rate, 23 of 93), the 16k single mean of 60 rises by about 10. |
| round-10/weights-m01 | - |  | theory says nothing |
| run-06/f2-m04 | - |  | theory says nothing |
| run-03/f2-m01 | 70 | [63, 77] | The theory says a longer cap turns Think-SFT's cap hits (46% of fresh2026 samples) into finished answers. On hard328 about a quarter of those cut answers come out right, so I added about 10 to the 16,384-cap single-sample mean of 60. |
| round-09/training-m02 | 69 | [63, 75] | Theory: ~62 cuts per sample at 16k (45.6 %) convert at a rate below hard328's quarter (~15 %), so the 16k single mean of ~60 rises by ~9. |
| round-10/problems-m06 | - |  | theory says nothing |
| run-06/f2-m01 | 75 | [69, 81] | Theory: a quarter of the about 62 cut samples per sample at 16,384 turn right with more budget (or more), so about +15 on Think-SFT's 16,384 mean of about 60 of 136. |
| run-07/f2-m02 | - |  | theory says nothing |
| round-09/sampling-m01 | 71 | [64, 78] | The arm mean at 16k is about 60 of 136 with about 62 cap hits per sample; by the board's rate for late finishes (about 20-25% right on hard328) that adds about 11, and averaging 4 draws shrinks the sampling noise. |
| round-09/weights-m04 | 71 | [65, 78] | Sound-cut-work clause: the 16k mean of 60.0 with ~62 cap hits gains about 20 % of those as right answers once let finish (hard328: 23 of 93), in line with M(2)'s +12 from finishing at 16k. |
| round-09/grader-m04 | 67 | [62, 73] | Theory: fresh2026's ~62 cap hits per sample finish at 32,768 but convert at a lower rate than hard328's (~24 %), about +7 on the 16k single-sample mean of 60. |
| round-10/training-m05 | 71 | [63, 79] | Theory: Think-SFT's cut answers on contest problems are unfinished routines, so cap 32,768 recovers about a fifth of its ~62 cap hits per sample, on top of the 16k single mean of 60 (hard328: +22 from 93 cut answers). |
| round-10/problems-m05 | 69 | [63, 75] | Think-SFT's cap hits are reachable unfinished work: at 32k about 15-20 % of its ~62 cap hits per sample should come right, on top of 60.0 at 16k (on hard328 the same change was +22). |
| round-09/sampling-m02 | 68.5 | [63, 74] | A longer cap turns Think-SFT's many fresh2026 cap hits (about 46 % of samples) into finished answers, about 20-25 % of them right, so the single-sample mean rises from about 60 to about 68. |
| round-10/weights-m05 | - |  | theory says nothing |
| round-12/s1-b | 70 | [64, 76] | About 62 cap hits per sample at 16k; roughly 16 % finish right at 32k: 60 plus about 10. |
| round-12/s6-b | - |  | no forecast |
