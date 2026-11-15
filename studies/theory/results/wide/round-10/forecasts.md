# Forecasts, round-10

Board snapshot 2026-11-15T18:58:29 UTC, written 2026-11-15T19:20:30 UTC. 33 targets; forecasters reader-1, reader-2, run-06/f2-m03, run-05/f2-m03, run-05/f2-m01, run-02/f2-m01, run-05/f2-m06, run-07/f2-m02, run-03/f2-m02, round-09/training-m06, run-05/f2-m04, run-02/f2-m04, round-09/sampling-m03, round-09/training-m04, run-04/f2-m04, run-08/f2-m01, round-09/grader-m04, round-09/grader-m03, run-04/f2-m03, round-09/grader-m06, round-09/training-m05, round-09/sampling-m05, run-03/f2-m05, round-09/training-m03, round-09/grader-m01, round-09/sampling-m06, round-09/weights-m01, round-09/sampling-m01, round-09/stopping-m04, round-09/weights-m04, round-09/weights-m06, round-09/problems-m05, round-10/stopping-m03, round-10/stopping-m04, round-10/weights-m01, round-10/weights-m03, round-10/weights-m05, round-10/weights-m06, round-10/training-m05, round-10/problems-m03, round-10/problems-m04, round-10/problems-m05, round-10/problems-m06, round-10/grader-m06.


- run-06/f2-m03 (training, carried): An outcome reward pays only for a gradable final answer, so its consistent gradient piles into a few singular directions that make the model complete the task in the rewarded form (boxed answer, final code block) before the cap; the rest of the update is diffuse. In-domain, the top-8 directions at 1.5x reproduce nearly all of RL's gain over the cued base. Another reward's directions give about half, random rank-8 gives nothing, and 2x commits too early.

- run-05/f2-m03 (weights, carried): Each direction of an RL change acts only as far as the processed text drives its input (right) singular vectors: Math-RL's top-8 input subspaces are excited 8-11x above random by math-solution text and Code-RL's 6-9x, so an edit works in full on any problem set of its own domain and transfers to another domain in proportion to input-subspace overlap (Math with Code about 0.22-0.26, giving roughly half the in-domain effect).

- run-05/f2-m01 (weights, carried): The top-8 singular directions per matrix of the RL change act as a signed termination dial spread over all layers and both module families: adding them at size s raises, monotonically in s, the chance an answer closes with a boxed result before the cap (negative s lengthens and unboxes), and modestly raises correctness on problems already finished; past 1.5x it closes unfinished hard solutions on guesses. Random rank-8 edits and Think-SFT's directions carry no dial.

- run-02/f2-m01 (run-02, carried): The autobench agent works under a fixed generation time per experiment, so it buys votes by shortening each sample (its best config: 10 samples at about 1,100 tokens each). Most MATH-500 problems are solved in under 2,000 tokens, so short samples plus a vote score well on dev100, but hard328 solutions need 6,000-14,000 tokens and short samples never reach them. For the base, each doubling of the token budget past 8,000 buys fewer problems.

- run-05/f2-m06 (weights, carried): Weight edits merged in bf16 are realized only where an entry's change exceeds half a unit in the last place of that weight, so small edits are thresholded onto small-magnitude weights and their effective size grows faster than nominal size (a=0.25 acts like about 0.12; top-8 at nominal 1.5 acts like RL's own top-8 share). Smaller deltas such as Code-RL's lose more at 1x and peak at a larger nominal size; trained checkpoints carry no such loss.

- run-07/f2-m02 (problems, carried): An RL run's top weight directions write a habit for its own domain's answers. For Math-RL that habit is to deliberate, check, and finish with one boxed answer; for Code-RL it is to reason, then finish with one final python block that passes the tests. In its own domain the top-8 edit carries about two thirds of RL's gain at 1x and nearly all of it at 1.5x. On another domain it carries about half as much.

- run-03/f2-m02 (stopping, carried): RL's top singular weight directions raise the model's per-token hazard of committing to an answer and ending, in proportion to their size. In-domain directions therefore turn unfinished answers into finished ones and lengthen premature short ones. Overall right-of-finished stays roughly flat, because fixes on problems already finished offset guesses on converted cap hits. Past about 1.5x the hazard closes hard problems with guesses. The full RL delta added to Think-SFT acts the same way.

- round-09/training-m06 (training, carried): The RL update is written onto features that pretraining placed in the early and middle layers: the input directions of RL-Math's top-8 change are the ones math text drives most, and most of RL's change in model output comes from layers 0-15. Adding the directions only in the first or middle third therefore gives more of the hard-problem gain than the last third, whose main distinct job, writing the opening cue, is redundant when the cue is prefilled.

- run-05/f2-m04 (weights, carried): RL writes its weight change in stages: the first 100 steps move weights along the reasoning-register directions that the cue's opening also drives (step-100 change about 0.03% of weight norm, activations nearly unchanged), giving the cue's gain plus a little precision; the finishing directions and the dense error-reducing remainder accumulate between steps 400 and 2,800. So a cue on an early checkpoint is redundant, and anything built from the final weights carries the late parts.

- run-02/f2-m04 (run-02, carried): A capped sample gives no answer, so in a plurality vote it abstains instead of adding a wrong value. Think-SFT's vote sits near its pass@4 because its unsolved samples run to the cap rather than box a guess. Anything that makes it finish, a 32k cap or the RL difference, turns abstentions into mostly wrong, scattered answers that tie or outvote lone right samples: single scores rise, vote gains shrink.

- round-09/sampling-m03 (sampling, carried): Temperature sets how often a plain prompt opens in the deliberative 'Okay' register. At T 0.6 the first tokens collapse onto the modal opening (step 100: 478 of 500); at T 1.0 a share 1-q starts elsewhere (step 100: 117 of 500; base: about 400). A prefilled cue or fixed template removes that branch, so the cue's worth at T 1.0 is (1-q) times the gap between openings, which widens on harder problems.

- round-09/training-m04 (training, carried): Pretraining fixed, for each problem, the base's distribution over final values; the cue picks which register samples it but does not move its modal value. A vote converges to that mode, so its ceiling is the problems whose modal value is right, and samples beyond about eight only resolve ties. The plain prompt samples pretraining's terse solution register, whose accuracy falls faster with difficulty than the cued register's, so plain's share of the cued score shrinks on harder sets.

- run-04/f2-m04 (sampling, carried): A T 1.0 run is a set of independent per-problem Bernoulli draws: the run-to-run spread of a count is sqrt(sum p(1-p)), about 5-6 problems on MATH-500 and 6 on hard328 for these models, and the seed adds nothing systematic. A stored first sample is one such draw, so a 4-sample mean is 1/4 that draw plus 3/4 the model's mean, and adding one sample to a vote moves only the few problems it can flip.

- run-08/f2-m01 (grader, carried): Each one-sample count is one seed's draw: the model branches at forks with fixed per-problem probabilities, so a cell has a sampling SD of about 5-6 problems on MATH-500, 7-9 on hard328 and 3 on fresh2026, plus small runner drift. A stored sample 0 is an unselected draw, so a 4-sample mean is that value shrunk slightly toward the cell's structural prior (neighbouring checkpoints, cue effect).

- round-09/grader-m04 (grader, carried): A count's size depends on the set's difficulty mix: hard328's first 164 problems are much harder than its second half (cued base 65 vs 99), and fresh2026 is harder still. On hard items the opening (cue, step 100, self-opening) moves few problems, while answers past 16k tokens are mostly unfinished or guessed, so cap raises and votes yield less per abstention than on hard328, and plain prompts keep a falling share of the cued count.

- round-09/grader-m03 (grader, carried): An edited model is not seed-paired with the stored base: BF16 rounding of any edit changes every text, so a functionless edit lands at the edit null (random rank-8 cells 158-167, mean about 161 on hard328 with the cue), not at the base's 164 draw. A partial edit's count is that null plus its share of the replicated full-edit gain (200.25, not the selected 203); halves of the edit add up to the whole.

- run-04/f2-m03 (sampling, carried): Under T 1.0 stopping is a sampled event: at each position the model draws a commit/stop token with a small hazard, so the cap-hit share is a survival probability. RL's top-8 directions add a near-constant logit to that hazard (cap hits 96, 77, 46, 25, 5 along the dial); dose multiplies it. Where the base fails by not stopping (short code tasks, fresh contests) the dial converts unfinished samples, at precision below the base's finished answers.

- round-09/grader-m06 (grader, carried): A count at a token cap scores every unfinished answer wrong, hiding whether it was unfinished work or a dead end. Raising the cap adds right answers in proportion to the model's share of unfinished-work cap hits: Think-SFT about one in four, RL one in ten, the base one in sixteen. Scoring the 32k text at 16,384 reproduces a 16k run, so the 32k-minus-16k difference is that yield alone.

- round-09/training-m05 (training, carried): The largest singular direction per matrix of RL-Math's change carries the reward's most consistent signal: write the final answer in the boxed form the verifier reads, which also ends some answers. Deciding to stop deliberating on long problems is spread over the next directions. One direction therefore cuts cap hits only partly, and scaling it mostly changes answer form, not stopping: top-1 at 2x gains little over top-1 at 1x, while eight directions together act as the finishing dial.

- round-09/sampling-m05 (sampling, carried): Ending is a sampled event: at T 1.0 the stop token is drawn at each point where an answer could close, so lengths have a long tail that the cap cuts off. Raising the cap finishes the cut samples, right at the rate of that model's long finished answers at the same difficulty: high for Think-SFT, whose cut answers are unfinished work, low for the base and RL, whose long answers mostly guess.

- run-03/f2-m05 (stopping, carried): A trace can degenerate before it ends, into word strings, a switch to Chinese script or repeated windows, and a degenerate trace almost never ends right. The hazard of this grows with edit size (word strings at 2-3x) and with tokens already generated (median first script switch near token 13,600). So oversized edits, and the late part of very long Think-SFT traces, lose answers. A smaller edit or a shorter trace keeps them. At T 1.0 classic loops are absent.

- round-09/training-m03 (training, carried): RL-Zero's group-relative reward gives gradient only on prompts where some rollouts succeed and others fail, so early RL moves the policy on problems the base solves sometimes, mostly short and medium ones, and leaves problems the base rarely solves for late training. By step 100 the gain sits on MATH-500's mid-difficulty problems; on hard problems, where the cued base mostly fails or runs to the cap, step 100 plain is no better than the cued base.

- round-09/grader-m01 (grader, carried): Each posted single cell is one seeded draw: new seeds on the same weights scatter by 5-7 problems per 500 and up to 9-19 per 328, and cells picked as notable (best size, first run) sit above their model's mean. Multi-sample means regress to the pooled level of near-identical cells: step-100 plain pools with step-100 cue (same opening policy), and the 164-problem references come from draws above their own 4-sample means.

- round-09/sampling-m06 (sampling, carried): Problems differ in solve rate far beyond binomial noise. Each arm has a block of problems it almost never samples right (base: 33 at 0 of 4 on MATH-500, against 0.5 expected) and a block where a wrong value is as likely as the right one. A vote wins only problems where the right answer is the most likely one, so it plateaus a few samples past 4, and the near-zero block caps votes on hard sets.

- round-09/weights-m01 (weights, carried): The commit-and-stop readout sits mainly in the top singular direction of each matrix of the RL-Math difference. The size of that one direction (its singular value times the scale) sets how often the model finishes. Breakdown into word strings also depends on that per-direction size, not on how many directions are added: about 2x over-commits on long problems, and about 3x on the top direction breaks generation, whether 1 direction or 8 are scaled.

- round-09/sampling-m01 (sampling, carried): Each sample is an independent draw: problem i is solved with a fixed probability p_i, so one cell's count varies by sqrt(sum p_i(1-p_i)), about 5-7 problems on MATH-500 and 6-9 on the 328, and same-seed reruns give new texts because vLLM is not batch-invariant. A stored single cell is one draw. New samples land around the arm's mean, not around the stored count, and a gap of a few problems between single cells is noise.

- round-09/stopping-m04 (stopping, carried): On a hard set part of every model's answers would end past 16,384 tokens, and a cut answer scores zero. A change that leaves the length distribution in place (100 RL steps, the cue on a checkpoint, a new seed or more samples) can move only the precision of finished answers. Step 100 writes cued-base lengths at T 1.0 (4,120 vs 4,008 tokens), so on hard problems it keeps the cued base's cap hits and adds a few right answers.

- round-09/weights-m04 (weights, carried): Moved onto another model that shares the base, the RL-Math difference acts as a finishing operator on that model's own trajectories. It does not add correctness. On Think-SFT it closes long, unfinished but sound work earlier, so cap hits fall and right-of-finished drops toward RL's level. The gain is limited by how much of the recipient's cut work was sound. Prompt or template changes on Think-SFT alone (no delta) leave its finishing rate and precision unchanged.

- round-09/weights-m06 (weights, carried): Edit entries smaller than half a bf16 ulp of the weight they modify are written by stochastic rounding (written/intended cosine 0.585). The written edit is unbiased: the intended direction comes through at full nominal size, and the rounding residue is a random edit, which is inert like the random rank-8 and noise controls. Scores therefore follow the nominal dose. The residue and GPU-dependent rounding draws add sample-to-sample spread, but they do not shift the mean.

- round-09/problems-m05 (problems, carried): Competition problems (AIME, HMMT; most of hard328, all of fresh2026) are limited by finding a working plan, not by executing steps: the base's errors on problems it never solves are wrong plans, and RL's finished wrong answers are 67 % wrong plans. RL weights and their top directions add finishing and fewer slips but no plans, so on contest sets they track RL; only imitation of long expert traces supplies plans, visible as high precision of finished long answers.

- round-10/stopping-m03 (stopping): Think-SFT was trained to end its reasoning at a </think> boundary and then write one short final answer and end-of-text. The raw template with the base's cue gives it no boundary, so after solving it keeps writing (re-checks, extra code blocks, new attempts) and stops late. In its own ChatML format it closes at the boundary: fewer answers reach 16k and output after the answer stops, with the same precision on finished answers.

- round-10/stopping-m04 (stopping): RL's top directions shift the lm_head readout toward commit tokens (the box, end-of-text, the 'Okay' cue). The shift raises the per-token chance of ending at points where an answer is ready, and it scales with the edit's projection on that readout, not with its energy. Directions from Math, Code or IF that share the readout add up; random or Think-SFT directions add nothing. Subtracting the directions turns boxed endings into unboxed ones more than into cap hits.

- round-10/weights-m01 (weights): The top RL-Math directions write stop and box logits additively: signed size s shifts the log-odds that an answer runs to the cap by a roughly fixed amount per unit, in either sign, on any set. Cap-hit counts therefore move with each set's base cap rate in log-odds, not by a fixed fraction. Overdose costs right answers only in proportion to a set's long unsolved answers, which it forces to finish as guesses.

- round-10/weights-m03 (weights): The effect of an added RL change depends on the host. Think-SFT's high-rank imitation change (3.7 % of weight norm, top 8 directions hold 2 %) already sets the long-reasoning features that RL's directions read, so RL's push has about a quarter of its effect on the base: a=1 cut Think-SFT's cap hits by 20 %, not 74 %. The response is weak but stable, no breakdown up to 4x. Its correctness covers every domain in its traces.

- round-10/weights-m05 (weights): Math-RL and Code-RL directions share part of their input subspace (overlap 0.22-0.26, random 0.002), and that part writes a reward-general readout: the deliberative opening, hold-on words and finishing. The rest of each change is domain-specific and nearly orthogonal (whole-change cosine under 0.03). Stacking the two edits counts the shared readout twice, which overdoses finishing, and adds each domain remainder once, so math gets Code's remainder only where it overlaps.

- round-10/weights-m06 (weights): Within the top-8 RL directions, the first singular direction of each matrix carries the format and stop part: it cuts cap hits, and at large size stops the model boxing its answer. Directions 2-8 carry the part that raises right answers on finished problems. So rank-1 edits finish without adding right answers, removing direction 1 keeps most of the correctness gain, and overdosing direction 1 produces unboxed answers that are graded wrong.

- round-10/training-m05 (training): Think-SFT's teacher traces cover competition problems (olympiad-style math and contest code) far more densely than the 3.1 RL prompts, which were filtered to problems the base fails. Imitation transfers whole solution routines for those problem types, not copies of items, so Think-SFT's lead over RL grows with competition difficulty (hard328, 2026 contests) and vanishes on MATH-500; adding the RL difference to it supplies closing, not routines.

- round-10/problems-m03 (problems): A code problem needs a short single-function artifact judged by hidden tests. The base's code deficit is mostly answers with no closed code block or cut off, not wrong logic, so any model or edit that writes a closed block recovers most of the gap; the ceiling is set by under-specified MBPP+ tests (about 405 of 538), which RL-Code (401) already nears. On math the matching lever is a terminal answer statement, which the plain base lacks.

- round-10/problems-m04 (problems): An edit's effect splits by problem stratum: it adds right answers on mid-difficulty problems (base right in some samples), which MATH-500 and hard328 both hold in similar numbers, while cap-hit changes live only in the long-derivation tail, which MATH-500 holds about a third as densely. So point gains transfer between sets, but a MATH-500 cap-hit change equals the hard328 change times the base's MATH-500/hard328 cap-hit ratio (about 22.5/77).

- round-10/problems-m05 (problems): Each set has problems that no reweighting of a host's own solution paths reaches (hard328: about 79 the base never solves even after restarts; MATH-500: about 15). Weight edits and their combinations only reweight paths the host already has, so scores saturate below that host's reach: stacking finishing directions adds little once most reachable problems finish, and votes stop near pass@k. Only a host with more reach (Think-SFT) raises the ceiling.

- round-10/problems-m06 (problems): An RL run's finishing habit is calibrated to the derivation lengths of its training domain. Code-RL learned to close at code-answer lengths (about 4k tokens), so its directions make math answers stop earlier: harmless on short MATH-500 problems, costly on long hard328 derivations (178 vs Math's 192, at fewer tokens). Math directions, calibrated to long derivations, have no room to act on short code tasks and give a partial gain there. Mixed edits inherit the shorter calibration on long problems.

- round-10/grader-m06 (grader): Each set holds items no model can be credited on: defective or unparseable golds, LLM-transcribed 2026 statements, and problems no arm ever solves (6 of MATH-500, about 80-90 of hard328). The count's ceiling is the set size minus these, so vote and long-cap gains compress as a model nears it: Think-SFT's vote already sits at pass@4, and extra samples or tokens add only on reachable unsolved items, never on the floor.

## t01 (work-ef61c7): How many of the first 250 MATH-500 problems does the base model plus 1.0x the top-8 directions of the RL-Code 3.1 weight change answer correctly with the plain prompt, one sample at T 1.0, grader v3?

Unit: right answers of 250. Cell: {"model": "Olmo-3-1025-7B base + 1.0x top-8 singular directions per matrix of (RL-Code 3.1 - base) (cell m21)", "prompt": "plain", "set": "MATH-500 first 250 problems", "n": 250, "sampling": "T 1.0; top-p and token cap not stated", "samples": 1, "grader": "v3"}

> (m21) base + 1.0x top-8 dirs of (RL-Code 3.1 - base), plain, MATH-500 first 250

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 168 | [128, 205] | Math top-8 plain is 427/500 (85%) against RL-Math plain 463, and Code-RL plain is 390/500 (78%) on MATH-500; Code top-8 should give a smaller share, near 67% of 250, with a wide range in case the opening is not installed. |
| reader-2 | 185 | [150, 212] | Plain base is 44.8 %, Math top-8 1x plain 85.4 % and full Code-RL 3.1 plain 78 %; Code top-8 is weaker than Math top-8 on hard328 (178 vs 192) but also writes the opening, so about 74 % of 250. |
| run-06/f2-m03 | 163 | [142, 184] | Theory: another reward's directions give about half of the gain; half of the way from plain base 224/500 to Math top-8 1x plain 427/500 is ~325/500, i.e. ~163 of the first 250. |
| run-05/f2-m03 | 164 | [140, 190] | Cross-domain transfer at roughly half the in-domain effect: Math top-8 1x plain lifts MATH-500 from 44.8% to ~86% (mean of 4: 431.75/500), half of that gain gives ~65.6%, i.e. ~164 of 250. |
| run-05/f2-m01 | 180 | [145, 212] | Dial applies to the RL change's top-8 directions; Code's directions carry the finishing/opening dial at about half Math's strength (hard328 cue 178 vs 192 vs base 164), so plain MATH-500 lands between plain base 224/500 and Math top-8 plain ~432/500, scaled to 250. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 170 | [140, 200] | Theory: Code-RL's smaller delta loses more to bf16 thresholding at 1x, so its top-8 acts well below nominal; plain score sits below Math top-8 1x plain (~86%) and below Code-RL itself (390/500=78%), about 68% of 250. |
| run-07/f2-m02 | 150 | [122, 180] | Cross-domain clause: Code top-8 at 1x carries half of the own-domain two thirds, i.e. about 1/3 of RL-Math's plain gain; first-250 base plain ~110 and RL ~232 give 110 + 122/3 = 150. |
| run-03/f2-m02 | 185 | [155, 212] | Theory: RL top directions raise the hazard of committing and lengthen premature short answers, which is the plain base's failure; Code directions are a weaker, off-domain push than Math's (Math top-8 plain 427/500 = 85%, plain base 45%), so about 74% of 250. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 185 | [155, 212] | Theory: edits built from final RL weights carry the opening register plus the late finishing directions; Code 3.1's top-8 also writes the deliberation register (result-e2482e), but less strongly than Math's top-8 (427/500 plain = 85%); full Code-RL plain is 78% (390/500), so about 74% of 250. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | 186 | [160, 212] | Plain prompt at T 1.0: score = q*acc(Okay opening) + (1-q)*acc(other opening); Code-RL directions write the opening less reliably than Math top-8 (Code-RL full: plain 390 vs cue 450 implies 1-q about 0.3), so 0.7*0.88 + 0.3*0.43 of 250 = about 186. |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 183 | [152, 210] | Structural prior from neighbouring cells (Math top-8 plain 427-445/500, Code-RL plain 390/500, Code top-8 weaker than Math top-8 on hard328) puts the true rate near 73%; theory adds sampling SD ~4 on 250 plus wide structural uncertainty. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | 165 | [130, 200] | Theory: RL top-8 directions of any outcome reward add a stop-hazard logit (Code directions finish on the code dial, result-a1bf75), so at 1x Code directions take the plain base (44.8%) most of the way toward Code-RL plain (78%) but below Math top-8 plain (427/500), about 66% of 250. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 180 | [152, 204] | Theory: each reward's top direction writes the form its own verifier reads, so Code's 8 directions finish answers but give less math answer-form gain than Math's top-8 (427/500 plain = 213/250); placed near Code-RL plain's 78% (390/500) minus a little, as Code top-8 took about half of Math top-8's hard328 gain (178 vs 192). |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 190 | [170, 210] | Theory: a 1x edit is below the size where word strings appear (2-3x), so no answers are lost to degeneration; level set from base+Math top-8 1x plain (427-445/500) discounted toward Code-RL's weaker math transfer (Code-RL plain 390/500, Code top-8 178 vs Math 192 on hard328), about 76% of 250. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 185 | [163, 205] | Theory: the finish readout sits in each matrix's top direction and its size sets finishing. RL-Code's top-8 at 1x also carries the Okay/Wait readout but at smaller singular values than Math's (Code top-8 gave 178 vs Math's 192 on hard328). So the cell lands below Math top-8 plain (about 432/500 = 86%) at about 74%, i.e. 185 of 250. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 180 | [155, 205] | Scores follow the nominal dose: 1x Code top-8 should deliver the same share of its parent's plain-prompt gain as 1x Math top-8 did (427 of 463 over plain base 224, about 85%), applied to Code-RL plain 390, giving about 73% of 250. |
| round-09/problems-m05 | 178 | [155, 200] | Theory: RL top directions add finishing and fewer slips, which is what non-contest MATH-500 needs, so Code-RL's top-8 should get most of full Code-RL's plain level (390/500): about 72% of 250. |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 186 | [156, 211] | Code's late readouts carry the cue token about as often as Math's (15 vs 13 of 96), so the edit installs the opening and finishing on the plain prompt, but with less right-answer content than Math top-8 (85 %): about 74 %. |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | 180 | [155, 202] | Code's shared readout writes the opening on math prompts (Code-RL plain 78 % on MATH-500); top-8 holds most of it, about 72 % of 250. |
| round-10/weights-m06 | 178 | [150, 202] | Code's direction 1 writes format and opening; directions 2-8 add some math transfer. |
| round-10/training-m05 | 181 | [156, 205] | Code-RL's prompts contain no math, so its directions give math only the opening and closing, no math routines: below Math top-8's 85 %, near 72 %. |
| round-10/problems-m03 | 180 | [150, 205] | Plain base's math loss is mostly missing answer statements; Code directions write a terminal answer and deliberation, about 85 % of Code-RL's plain gain (390/500). |
| round-10/problems-m04 | 178 | [148, 204] | First 250 of MATH-500 have the full set's strata; Code directions recover most of the mid and easy stratum the plain base loses. |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | 183 | [155, 207] | MATH-500 problems are short (median about 3k), so code-length closing costs little; Code top-8 keeps most of Code-RL's plain 78 %. |
| round-10/grader-m06 | - |  | no forecast |

## t02 (work-ef61c7): How many of the 500 MATH-500 problems does the base model plus 0.125 times the full RL-Math 3.1 weight difference answer correctly with the plain prompt, one sample at T 1.0, grader v3?

Unit: right answers of 500. Cell: {"model": "Olmo-3-1025-7B base + 0.125 x (RL-Math 3.1 - base) (cell m18)", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0; top-p and token cap not stated", "samples": 1, "grader": "v3"}

> (m18) base + 0.125x (RL-Math 3.1 - base), plain, MATH-500 n 500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 325 | [235, 410] | Plain dose row is 224/405/443/463 at a=0/0.25/0.5/1; a=0.125 sits between plain base and a=0.25, and bf16 rounding of small deltas may weaken it further. |
| reader-2 | 365 | [265, 425] | Plain dose curve 224 (a=0), 405 (a=0.25, acting as about 0.12 after bf16 rounding), 443 (a=0.5); a=0.125 sits between, with wide uncertainty because rounding may remove much of so small a delta. |
| run-06/f2-m03 | 320 | [272, 368] | Theory: the finishing/rewarded-form effect grows with the dose along the concentrated directions; 1/8 of the delta gives roughly half of the plain-prompt format gain seen at 0.25x (224 -> 405). |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 330 | [260, 395] | Monotonic dial in size s: 0.125x of the full delta carries the top-8 at small s, so the score sits between plain base 224 and theta 0.25 plain 405, discounted for bf16 rounding of tiny changes. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 290 | [230, 360] | Theory: a=0.25 acts like ~0.12 and effective size shrinks faster than nominal, so a=0.125 acts like ~0.04; interpolating in logit between plain base 224 and a=0.25 plain 405 gives ~290. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 300 | [240, 370] | Theory: the effect is in proportion to size; 0.125x is half of theta 0.25 (plain 405/500 vs base 224), and bf16 rounding shrinks it further, so it lands partway between base and theta 0.25. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 370 | [290, 425] | Theory: a change of about 0.03% of weight norm along the register directions gives the cue's gain (step 100 plain 418); 0.125x of the final delta is about that size but not purely register, and bf16 rounding may shrink it (theta 0.25 plain 405, base plain 224). |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | 322 | [255, 390] | Plain at T 1.0 is a mix of openings: base has 1-q = 0.8 (plain 224), 0.25x has q about 0.83 (plain 405 vs cue 441); at 0.125x (further shrunk by bf16 rounding) q is about 0.5, giving 0.5*0.85 + 0.5*0.44 of 500 = about 322. |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 330 | [265, 395] | Prior interpolated on the theta dose curve (plain 224 at 0, 405 at 0.25, nonlinear and bf16-shrunk), with MATH-500 sampling SD 5-6 on top of a wide structural spread. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 254 | [222, 295] | Partial edit = edit null (plain base level 224, null sits at the base mean) plus its share (0.125) of the full RL-Math gain to 463: 224 + 0.125*239 = 254. |
| run-04/f2-m03 | 330 | [255, 395] | Theory: dose multiplies the hazard shift, so 0.125x of the full difference gives about half of theta 0.25's plain jump (224 -> 405), shrunk further by BF16 rounding at small doses. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 320 | [235, 410] | Theory: finishing is set by the size of the top direction. At 0.125x of the full difference that size is small, so the model stays nearer plain base (224) than theta 0.25 (405, which bf16 rounding may already shrink to about 0.12); wide interval because rounding is uncertain. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 320 | [270, 375] | Stochastic rounding writes the sub-ulp 0.125x edit at its full nominal size, so it acts as a true eighth dose, about halfway up the plain dose curve between a=0 (224) and a=0.25 (405). |
| round-09/problems-m05 | 330 | [250, 400] | Theory: RL weights add finishing and the opening on execution-limited MATH-500, so a small dose sits between plain base 224 and theta 0.25 plain 405; the theory gives no dose curve, hence the wide interval. |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 330 | [250, 405] | An eighth of the full difference, much of it lost to bf16 rounding, gives a small readout shift; the plain dose curve 224/405 puts it about two thirds of the way up. |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | 350 | [265, 415] | The shared opening readout is installed at small doses of the full change; a=0.125 sits between plain 224 and a=0.25's 405. |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 365 | [275, 425] | Answer-statement losses go first at any small dose; bf16 rounding keeps the effective dose weak. |
| round-10/problems-m04 | 365 | [275, 425] | Plain-base losses sit on easy and mid problems that a small dose recovers first. |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | - |  | no forecast |

## t03 (work-3baa2c): On the 328 harder problems with the cue at T 1.0, what is the mean number of right answers over 4 samples (the stored 184 plus 3 new) for the base plus 1.5x the top-8 RL-Math 3.1 directions applied in layers 0-10 only?

Unit: mean right answers of 328 over 4 samples. Cell: {"model": "Olmo-3-1025-7B base + RL-Math 3.1 top-8 directions at 1.5x in layers 0-10 only", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p and token cap not stated", "samples": 4, "grader": "not stated"}

> base + Math 3.1 top-8 at 1.5x in L0-10 (+3 samples)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 181 | [172, 190] | Stored 184 plus 3 new samples; single samples vary by about 8, and the 1.5x all-layer cell fell back from 203 to a mean of 200. |
| reader-2 | 182 | [175, 190] | Stored 184 plus 3 new samples regressing slightly toward about 181 (the all-layer 203 single fell to a 200.25 mean); seed sd about 6. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 181 | [173, 189] | Dial is spread over all layers, so L0-10 alone gives only part of the all-layer gain; the stored 184 regresses slightly toward the band level over 3 new samples. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 181 | [174, 188] | Theory: the 1.5x top-8 edit is realized at RL's own top-8 share (no thresholding loss), so the stored L0-10 cell (184) is the cell's level, with 3 new samples regressing slightly as the full 1.5x cell did (203 -> 197-199). |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 181 | [174, 189] | Theory: a layer band carries only part of the edit's size, so the effect is partial; anchored on the stored 184, with 3 new samples regressing slightly toward the size-proportional ~178. |
| round-09/training-m06 | 182 | [175, 189] | Theory: RL's change and its output effect sit in layers 0-15, so the first third keeps most of the hard-problem gain; the stored 184 (result-306787) holds with slight regression, as the all-layer 1.5x edit went 203 -> 200.25 over 4 samples. |
| run-05/f2-m04 | 181 | [173, 189] | Edit from final weights carries the late error-reducing part in early layers (stored 184, L0-10 minus random +7.9); 3 new samples regress toward about 180 (sample sd about 7). |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | 183 | [175, 191] | Theory: a 4-sample mean is 1/4 the stored draw (184) plus 3/4 the model mean, and that one draw is the only estimate of the mean; spread comes from the per-draw sd of about 6 (3/4 x 6 for the mean estimate, combined with 3 new draws). |
| run-08/f2-m01 | 182.5 | [173, 192] | Theory: stored 184 is an unselected draw, so the 4-sample mean is 184 shrunk slightly toward the neighbouring-band prior (~182); 3 new draws with hard328 SD 7-9. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 180 | [172, 189] | Halves add up: band excesses over the 161 null (23, 22, 5) rescaled to sum to the replicated 39.25 gain give L0-10 about 179 per new sample; mean with the stored 184 = 180. |
| run-04/f2-m03 | 180 | [172, 189] | A partial-layer dose gives a partial hazard shift and conversion at lower precision, so the 4-sample mean regresses from the stored 184 toward the band level, between base 164 and all layers 200. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 180 | [172, 189] | Theory: 1.5x is under the word-string hazard, so the cell's level is its stored 184 regressed toward the band means (~178) for 3 new samples; mean of 4. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 181.5 | [174, 189] | Regression clause: the stored 184 is a first draw, so the 3 new seeds should average slightly lower (about 181, with single draws scattering 9-19 per 328); mean of 4 = (184 + 3 x 180.7) / 4. |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 181 | [172, 190] | Theory: 1.5x per direction is below the 2x over-commit point, so no breakdown and the stored 184 should hold. Expect regression toward the mean over 4 samples (seed spread about ±9). |
| round-09/sampling-m01 | 183 | [173, 193] | Theory: the stored 184 is one draw and new samples land around the arm mean, best estimated by 184; the 4-sample mean carries the arm-mean uncertainty (sd about 7 per cell on the 328) plus the averaged noise of 3 new draws. |
| round-09/stopping-m04 | 182.5 | [175, 190] | New seeds leave the length distribution in place and can move only precision of finished answers (theory), so the 4-sample mean stays near the stored L0-10 cell's 184 (result-306787), slightly regressed. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 181 | [175, 188] | Rounding draws add spread but do not shift the mean, so the 3 new samples should average near the cell's nominal level (about 180) and the stored 184 regresses slightly, as the first 207 did in result-95a4dc. |
| round-09/problems-m05 | - |  | theory says nothing |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 181 | [173, 189] | The L0-10 band adds right answers without the commit shift (98 cap hits); three new samples regress the stored 184 toward about 180. |
| round-10/weights-m01 | 181 | [173, 189] | A band edit carries only part of the stop readout; the right-answer gain of the stored 184 regresses by a few. |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | 181 | [173, 189] | The early band's correctness lives in directions 2-8 and is real; the stored 184 regresses a little. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | 182 | [176, 189] | L0-10's gain is on finished mid problems (precision 0.80); stable across seeds. |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | 182 | [176, 189] | Math-calibrated early band: long answers kept (98 cap hits), precision high; seed noise only. |
| round-10/grader-m06 | - |  | no forecast |

## t04 (work-3baa2c): On the 328 harder problems with the cue at T 1.0, what is the mean number of right answers over 2 samples (the stored 183 plus 1 new) for the base plus 1.5x the top-8 RL-Math 3.1 directions applied in layers 11-21 only?

Unit: mean right answers of 328 over 2 samples. Cell: {"model": "Olmo-3-1025-7B base + RL-Math 3.1 top-8 directions at 1.5x in layers 11-21 only", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p and token cap not stated", "samples": 2, "grader": "not stated"}

> L11-21, L22-31 (+1 each)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 181.5 | [174, 189] | Stored 183 averaged with one new sample expected near 180. |
| reader-2 | 182 | [175, 189] | Stored 183 plus one new sample near 181; per-sample sd about 6 on the 328. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 181 | [173, 190] | Spread-over-layers dial: middle band gives a partial gain like the stored 183 (cap hits 49), one new sample with seed noise. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 181.5 | [175, 188] | Theory: 1.5x edit realized at full share, so stored L11-21 183 is the level; one new sample regressing slightly gives ~181.5 mean. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 181 | [172, 190] | Theory: partial-size hazard rise from one band (stored 183, 49 cap hits); one new sample regresses slightly toward ~179. |
| round-09/training-m06 | 182 | [174, 190] | Theory: the middle third (inside layers 0-15 KL share) carries gain like the first third, so the stored 183 holds with slight regression over one more sample. |
| run-05/f2-m04 | 181 | [173, 189] | Final-weight edit in middle layers carries part of the late directions (stored 183 with 49 cap hits); one new sample near 180. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | 183 | [176, 190] | Theory: a 2-sample mean is half the stored Bernoulli draw (183) plus one new draw around the same mean (seed adds nothing systematic), so sd is about 0.5 x sqrt(6^2+6^2), roughly 4. |
| run-08/f2-m01 | 181.5 | [173, 190] | Stored 183 plus one new draw (SD 8) centred on a prior ~180 from the L0-10 band and the all-layer edit; mean of 2 shrunk slightly. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 181 | [171, 190] | Same rescaled band share: L11-21 = 161 + 17.3 = 178 for the new sample, averaged with stored 183 gives about 181. |
| run-04/f2-m03 | 181 | [172, 190] | The L11-21 band cut cap hits (77 -> 49), so per the theory it converts unfinished samples at lower precision; the 2-sample mean stays near the stored 183 with slight regression. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 181 | [172, 190] | Theory: 1.5x edit in mid layers causes no degeneration; stored 183 plus one new sample regressed toward ~179. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 181 | [174, 188] | Seed-scatter clause: the new seed lands within about 7 of the cell's mean, which sits a little under the first-run 183; (183 + ~179) / 2. |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 181 | [171, 191] | Theory: 1.5x per direction is below 2x, so no over-commit or breakdown and the band keeps its stored level (183). Mean of 2 samples, slight regression. |
| round-09/sampling-m01 | 183 | [175, 191] | Theory: the new sample lands around the arm mean, estimated by the stored 183, with per-cell sd about 7 on the 328; averaging over 2 samples gives about +/-8. |
| round-09/stopping-m04 | 182 | [174, 190] | One new seed leaves the length distribution in place (theory), so the 2-sample mean stays at the stored 183 of the L11-21 cell within seed noise. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 181.5 | [175, 188] | Same mean as the nominal dose with extra rounding spread: the stored 183 plus one new draw near 180. |
| round-09/problems-m05 | - |  | theory says nothing |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 181 | [173, 189] | The middle band partly carries the commit shift (49 cap hits); stored 183 plus one sample near 180. |
| round-10/weights-m01 | 181 | [174, 189] | Middle band cut cap hits to 49; one more sample near 180. |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | 181.5 | [174, 189] | The middle band holds part of directions 2-8. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | 181.5 | [175, 188.5] | Middle band adds on the mid stratum; one more draw. |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | 181.5 | [175, 188.5] | Same domain calibration; one more draw. |
| round-10/grader-m06 | - |  | no forecast |

## t05 (work-3baa2c): On the 328 harder problems with the cue at T 1.0, what is the mean number of right answers over 2 samples (the stored 166 plus 1 new) for the base plus 1.5x the top-8 RL-Math 3.1 directions applied in layers 22-31 only?

Unit: mean right answers of 328 over 2 samples. Cell: {"model": "Olmo-3-1025-7B base + RL-Math 3.1 top-8 directions at 1.5x in layers 22-31 only", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p and token cap not stated", "samples": 2, "grader": "not stated"}

> L11-21, L22-31 (+1 each)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 167 | [159, 175] | Stored 166 averaged with one new sample near the base and random level (159-168). |
| reader-2 | 166.5 | [160, 173] | Stored 166 plus one new sample near the random/base level of 159-167 (late layers add no right answers on either pair). |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 167 | [158, 176] | Spread dial gives late band only a small part; stored 166 plus one sample near base-to-random level. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 167 | [160, 174] | Theory: 1.5x edit realized at full share, so stored L22-31 166 (near random/base level) is the level; mean of 2 ~167. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 167 | [158, 176] | Theory: partial-size band edit; the stored 166 sits near base and random, and one new sample keeps the mean near there. |
| round-09/training-m06 | 166 | [158, 174] | Theory: the last third's distinct job (writing the cue) is redundant with the cue prefilled, so it stays near base/random (164/159), consistent with the stored 166. |
| run-05/f2-m04 | 168 | [159, 177] | Late layers add no right answers on either pair (math +2.4 and code +2.0 over random), so mean of stored 166 and one new sample is near base/random (159-164). |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | 166 | [159, 173] | Theory: half the stored draw (166) plus one new independent draw around the same mean, sd about 4 from the run-to-run spread of 6 on hard328. |
| run-08/f2-m01 | 165.5 | [157, 174] | Stored 166 plus one new draw centred on the late-band prior (~165, between base 164 and random 159; late layers add no right answers on both pairs), SD 8 halved. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 166 | [157, 175] | Same rescaled band share: L22-31 = 161 + 3.9 = 165 for the new sample, averaged with stored 166 gives about 166. |
| run-04/f2-m03 | 167 | [158, 177] | The late band gives little hazard shift that converts to right answers (166, random 159); the 2-sample mean stays near base level. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 168 | [159, 178] | Theory: no degeneration at 1.5x, and late layers add no right answers (math and code); stored 166 plus one new sample near 170. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 166 | [159, 173] | Seed-scatter clause: 166 was not a cell picked for being notable (it was low), so no downward regression; the new draw scatters around about 166, between random (159) and the base (164). |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 167 | [157, 177] | Theory: 1.5x per direction is below 2x, so the late band keeps its stored 166, which is near base and random (late layers add no right answers). Mean of 2 samples. |
| round-09/sampling-m01 | 166 | [158, 174] | Theory: the new sample lands around the arm mean, estimated by the stored 166, with per-cell sd about 7 on the 328; averaging over 2 samples gives about +/-8. |
| round-09/stopping-m04 | 167 | [159, 175] | One new seed leaves the length distribution in place (theory), so the 2-sample mean stays at the stored 166 of the L22-31 cell within seed noise. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 165.5 | [159, 172] | Nominal dose in L22-31 adds about nothing over random (166 stored); a new draw near 165 with rounding spread leaves the mean unchanged. |
| round-09/problems-m05 | - |  | theory says nothing |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 166 | [159, 173] | The late band alone does not fire the commit at answer-ready points (57 cap hits, no right answers added); near the base level. |
| round-10/weights-m01 | 165 | [158, 172] | The late band moved cap hits only 77->57 and added no right answers; the new sample sits near the random level. |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | 166 | [159, 173] | The late band holds little of directions 2-8. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 166 | [160, 172.5] | The late band writes no closing format on code and adds no right answers on math either. |
| round-10/problems-m04 | 166 | [160, 172.5] | Late band adds nothing on any stratum. |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | 166 | [160, 172.5] | Late band adds no right answers on either domain. |
| round-10/grader-m06 | - |  | no forecast |

## t06 (work-3baa2c): On the 328 harder problems with the cue at T 1.0, one sample, how many right answers does the base get when only RL-Math 3.1 singular directions 2-8 (not the first) are added at 1.5x, in layers 0-10?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + RL-Math 3.1 directions 2-8 only (first direction dropped) at 1.5x, layers 0-10 as grouped in the item", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p and token cap not stated", "samples": 1, "grader": "not stated"}

> new cells directions 2-8 only

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 175 | [161, 190] | L0-10 with all 8 directions gives 184; dropping the first direction (top-1 alone 181 in all layers) should cost some, leaving it between that and base 164. |
| reader-2 | 175 | [160, 190] | L0-10 with all 8 directions gave 184 against random 159 and base 164; dropping the first direction should keep part of that early-layer gain. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 177 | [164, 190] | The dial lives in the top-8 directions as a group; dropping direction 1 in L0-10 removes some of the finishing push, slightly below the L0-10 cell's 184. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 177 | [165, 190] | Theory: dropping the first direction leaves a smaller edit that loses more to bf16 thresholding, so it falls below the L0-10 full-top-8 cell (184) toward base/random (159-164). |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 176 | [163, 189] | Theory: dropping the first direction removes a large share of the edit's size and so of the hazard rise, giving less than the full L0-10 band (184) and a little above base 164. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 176 | [162, 190] | Directions 2-8 still carry part of the late error-reducing change in L0-10 (all 8 there gave 184), minus the first direction's contribution; between random (about 160) and 184. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 178 | [162, 194] | One draw (hard328 SD 7-9) around a structural prior just under the all-8 L0-10 cell (184), because the first direction mostly sets finishing. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 169 | [156, 182] | Halves add up: directions 2-8 carry the full 39.25 gain minus the first direction's ~21.5, and L0-10 holds ~0.46 of that, so 161 + 8 = 169. |
| run-04/f2-m03 | 177 | [164, 190] | Dropping the first direction lowers the dose of the summed edit, so the hazard shift is a bit smaller than the full L0-10 edit (184): slightly fewer right answers. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 176 | [161, 191] | Theory: stopping is spread over directions 2-8 and the first direction mostly carries the boxed form, so dropping it keeps most of the L0-10 band's effect (184/328) but loses a few format-ended answers. |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 176 | [163, 189] | Theory: a smaller edit (first direction dropped) keeps answers without degeneration; between the L0-10 full-band level (~180) and random (~160), nearer the band. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 172 | [160, 184] | Theory: commit-and-stop sits mainly in the top direction. Dropping it from the L0-10 edit (184 right, 98 cap hits) removes its finishing share, so right answers fall toward base and random (159-164) and cap hits stay high. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 180 | [168, 192] | Nominal-dose reading: directions 2-8 carry most of the top-8 dose (one direction alone adds little to right answers), so this lands near the full L0-10 edit's 184. |
| round-09/problems-m05 | - |  | theory says nothing |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 177 | [163, 191] | Directions 2-8 in L0-10 keep that band's right-answer content; the band carried no finishing to lose, so a little under 184. |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | 181 | [170, 192] | In layers 0-10 the 8 directions gave 184 at 0.80 precision on finished answers; dropping direction 1 removes stop push, not correctness, so precision holds and right answers stay near 180. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 176 | [162, 190] | Early-layer directions 2-8 keep part of the band's gain. |
| round-10/problems-m04 | 175 | [162, 189] | Directions 2-8 keep most of the early band's mid-stratum gain. |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | 175 | [162, 189] | Math-domain directions 2-8 in early layers keep part of the gain. |
| round-10/grader-m06 | - |  | no forecast |

## t07 (work-3baa2c): On the 328 harder problems with the cue at T 1.0, one sample, how many right answers does the base get with a random rank-8 weight edit applied only in layers 0-10?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + random rank-8 edit in layers 0-10 (control; scale not stated, matched to the 1.5x cells)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0; top-p and token cap not stated", "samples": 1, "grader": "not stated"}

> random rank-8 in L0-10

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 160 | [149, 171] | Random rank-8 edits are flat at 158-167 with base cue 164 on hard328. |
| reader-2 | 161 | [150, 172] | Random rank-8 edits are flat at 158-167 at every size on the 328, base 164. |
| run-06/f2-m03 | 161 | [148, 174] | Theory: random rank-8 gives nothing, so it stays at the cued base on hard328 (164/161, random edits 158-167). |
| run-05/f2-m03 | 160 | [147, 174] | A random rank-8 subspace is not driven by math text (top-8 subspaces are excited 8-11x above random), so the edit acts like nothing: cued-base level, matching the random rank-8 cells at 158-167 on hard328. |
| run-05/f2-m01 | 161 | [150, 172] | Random rank-8 edits carry no dial, so it equals base/random cells (158-167 on hard328 with the cue). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 161 | [150, 172] | Theory: a random rank-8 edit carries no RL-specific realized change, so it sits at the random-edit level seen at every size (158-167) and base 164. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 161 | [148, 174] | Theory: only RL's top directions raise the stopping hazard; a random rank-8 edit leaves the base unchanged (random edits at all sizes 158-167). |
| round-09/training-m06 | 161 | [152, 170] | Theory: the gain comes from RL writing onto the input directions math text drives most; a random rank-8 edit in layers 0-10 hits no such features, so it stays at base/random level (164, 158-167). |
| run-05/f2-m04 | 161 | [149, 173] | A random rank-8 edit carries none of RL's staged directions, so it stays at the base level (random edits 158-167, base cue 160-164). |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 162 | [149, 175] | Random rank-8 edits are flat at base level (158-167 vs base 164), so one hard328 draw with SD ~8 around ~162. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 161 | [151, 171] | A functionless edit lands at the edit null (random rank-8 cells 158-167, mean 161), not at the base's 164 draw. |
| run-04/f2-m03 | 162 | [151, 173] | Theory: only RL directions shift the stop hazard and random rank-8 edits are flat (158-167), so the cell stays at the cued base's 164. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 161 | [150, 172] | Theory ties loss to edit size along RL directions; random rank-8 edits stay flat on the board (158-167 right, 67-79 cap hits), so base level ~161. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 160 | [149, 171] | Pooling clause: a random rank-8 edit is a near-identical cell to a fresh cued-base draw (random edits 158-167, base singles 160/161/164, 4-sample mean 158.5), so one seed lands near the pooled ~160 with about +-10 scatter. |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 162 | [151, 173] | Theory: only the RL top direction's size moves finishing, so a random rank-8 edit does nothing. Expect base and random levels (158-167 across sizes). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 161 | [151, 171] | A random rank-8 edit leaves cap hits where the base has them (67-79 on the board), so by the theory only precision moves and the score stays at the cued base / random level of 158-164. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 162 | [152, 172] | A random edit is inert in the theory, so this scores at the cued base's level (base 160-164; random cells 158-167). |
| round-09/problems-m05 | 160 | [148, 172] | Theory: only RL directions carry finishing, so a random rank-8 edit adds neither finishing nor plans and stays at the cued base's hard328 level (158-167 for random edits). |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 161 | [150, 172] | A random rank-8 edit has no readout projection, so it stays flat at 158-167. |
| round-10/weights-m01 | 161 | [151, 171] | A random rank-8 edit writes no stop logit at any size. |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | 160.5 | [150, 171] | Random directions carry neither part. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 161 | [151, 171] | Random edit writes no format. |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | 161 | [151, 171] | Random edit has no domain calibration. |
| round-10/grader-m06 | - |  | no forecast |

## t08 (work-739554): On the 500 MATH-500 problems with the cue, how many answers hit the token cap for the base model with the top-8 RL-Math directions subtracted (size -1.0)?

Unit: cap hits of 500. Cell: {"model": "Olmo-3-1025-7B base - 1.0 x top-8 RL-Math directions (cell m11)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> m11 base - 1.0 x top-8 RL-Math directions, cue, MATH-500 n 500, readout cap hits

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 40 | [22, 65] | Base cue has 22-27 cap hits on MATH-500; size -1 raised hard328 cap hits from 77 to 96 and stopped boxing, so a larger relative rise on easier problems. |
| reader-2 | 36 | [24, 55] | Cued base has 22-27 cap hits of 500 on MATH-500; on hard328 size -1 raised cap hits 77 to 96 (and RL minus its top-8 went 20 to 90), so expect a moderate rise. |
| run-06/f2-m03 | 40 | [27, 58] | Theory: the top-8 directions make the model finish before the cap, so subtracting them raises cap hits; scaling hard328's 77 -> 96 to MATH-500's base 27 plus lost boxing gives ~40. |
| run-05/f2-m03 | 37 | [25, 52] | An in-domain edit acts in full on any math set, so the hard328 size -1 effect (cap hits 77 -> 96, x1.25) carries over to MATH-500's cued-base cap hits (~22-27), plus extra from lost finishing. |
| run-05/f2-m01 | 38 | [25, 55] | Negative s lengthens answers: base cue MATH-500 has 22-27 cap hits, and size -1 raised hard328 cap hits 77 to 96, so MATH-500 cap hits rise by roughly half. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 38 | [25, 55] | Theory: -1x top-8 is realized like +1x (same magnitude, partly thresholded), so cap hits rise as on hard328 (77 -> 96, x1.25) plus unboxing; scaling cued-base MATH-500's ~27 cap hits gives ~38. |
| run-07/f2-m02 | 36 | [22, 52] | The top-8 directions write the Math-RL habit of finishing with one boxed answer, so subtracting them removes that habit and raises cap hits above the cued base's ~23-27 on MATH-500, scaled like the hard328 rise from 77 to 96. |
| run-03/f2-m02 | 38 | [26, 52] | Theory: hazard scales with signed size; at -1 the hard328 survival past the cap rose 77->96 (hazard factor ~0.85), and applying that to MATH-500's ~25 base cap hits (S^0.85) gives ~38. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 38 | [24, 55] | Theory: the finishing directions sit in the final weights, so subtracting the top-8 raises cap hits (hard328: 77 to 96 at -1); cued base MATH-500 has 22-27 cap hits, so about 1.5x that. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 34 | [22, 48] | Base cue MATH-500 cap hits 22-27 per sample, scaled by the hard328 dial ratio at size -1 (96/77), plus count noise. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | 38 | [26, 54] | Survival model: on hard328, size -1 multiplies the hazard by about 0.85 (cap share 0.235 -> 0.293); applied to MATH-500's cued-base cap share (22-27 of 500), that gives about 38 cap hits. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 34 | [22, 49] | Theory: the 8 directions together are the finishing dial, so at -1 finishing reverses; on hard328, -1 raised cap hits 77->96 (+25%) and boxing fell, so MATH-500's cued-base 22-27 cap hits rise to about 34. |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 36 | [24, 52] | Stopping lens: removing the finishing directions raises cap hits (hard328 77 -> 96 at -1, +25%, plus unboxed answers); applied to the cued base's MATH-500 22-27 cap hits with some extra rise. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 38 | [24, 56] | Theory: a negative top-direction size lowers finishing. On hard328, -1x raised cap hits from 77 to 96 (x1.25), so the cued base's 22-27 MATH-500 cap hits rise to about 35-40. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 35 | [24, 50] | The -1x edit acts at full nominal dose, raising cap hits by the same ratio as on hard328 (77 to 96), applied to the cued base's 22-27 MATH-500 cap hits, plus the loss of boxing. |
| round-09/problems-m05 | 42 | [27, 65] | Theory: the top RL directions carry finishing, so subtracting them removes it and raises cap hits above the cued base's 22-27 on MATH-500, scaled from hard328 (77 to 96 at size -1). |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 31 | [21, 43] | At size -1 on hard328 cap hits rose only 77 to 96 (x1.25) while unboxed answers rose 23 to 61: the lost commit mostly ends answers unboxed. x1.25 on MATH-500's 22-27 gives about 31. |
| round-10/weights-m01 | 30 | [20, 42] | hard328 size -1 moved cap hits 77->96, +0.30 in log-odds; the same shift on MATH-500's 4.5 % base cap rate gives about 6 %, so 30 of 500. |
| round-10/weights-m03 | 37 | [25, 52] | On the base host the negated push lengthens answers fully. |
| round-10/weights-m05 | 37 | [25, 52] | Negating removes the shared readout; the cue still supplies the opening, so only the finishing loss shows. |
| round-10/weights-m06 | 36 | [24, 50] | Negating direction 1 removes boxing (61 unboxed on hard328), and unboxed answers run on; a moderate cap-hit rise. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 35 | [23, 52] | Subtracting the directions removes boxing (61 unboxed on hard328) and closing; on MATH-500 a modest rise over 22-27. |
| round-10/problems-m04 | 30 | [20, 43] | On hard328 the -1 edit took cap hits 77 -> 96 (x1.25, +19); MATH-500's tail is 22.5 cap hits, so 22.5 x 1.25 plus a little breakage gives about 30. |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | 34 | [22, 50] | Removing Math's long-derivation closing only matters on long MATH-500 problems: a modest rise over 22-27. |
| round-10/grader-m06 | - |  | no forecast |

## t09 (work-8ea654): How many of the 538 HumanEval+ and MBPP+ problems does Think-SFT pass with the Code cue, one sample at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-7B-Think-SFT (no reward)", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0, seed 51000000; top-p and token cap not stated", "samples": 1, "grader": "not stated (tests passed)"}

> HumanEval+ and MBPP+ (538), Code cue and Math cue, T 1.0, 1 sample, seed 51000000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 375 | [330, 415] | Think-SFT beats RL on math under the cue; RL-Code is 401 and base+Code cue 317, and Think-SFT's long answers and cap hits may cost some code passes. |
| reader-2 | 385 | [330, 428] | Think-SFT matches or beats RL on math and MMLU/BBH (342 vs RL 332); on code RL-Code has 401 and the cued base 317, minus some loss to Think-SFT cap hits. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 385 | [355, 415] | Structural prior: Think-SFT is level with or above RL on the other sets (MATH-500, hard328, OOD), so it should land near RL-Code 401 on code; one-draw SD ~9 on 538 plus structural spread. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 390 | [355, 420] | Theory: shorter traces keep answers; code answers are short (~4k tokens), so Think-SFT loses little to late degeneration and lands near RL-Code (401) and its edge elsewhere (MMLU/BBH 342 vs RL 332). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | - |  | theory says nothing |
| round-10/stopping-m03 | 383 | [352, 410] | In the raw code template there is no </think> boundary, so Think-SFT sometimes writes test or alternative code after its solution, and the last code block is then not the solution; a few passes are lost below the native level. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | 398 | [360, 428] | Think-SFT's correctness covers code traces, and short code answers rarely hit the cap, so its missing finishing push costs little: about RL-Code's 401. |
| round-10/weights-m05 | 390 | [350, 425] | Think-SFT has its own code correctness but no RL finishing readout; it lands near RL-Code minus a little. |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 392 | [358, 422] | The Think-SFT data carry many contest-code traces, so it brings code routines RL-Code learned only from reward; at short code lengths the cap barely binds, putting it level with RL-Code's 401. |
| round-10/problems-m03 | 390 | [364, 412] | Think-SFT writes closed code blocks and code needs short derivations, so it lands near the test ceiling of about 400, minus a few cap hits. |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 390 | [364, 412] | Think-SFT's code reach is near the test ceiling that RL-Code (401) already approaches. |
| round-10/problems-m06 | 390 | [364, 412] | Think-SFT's teacher traces include code; short code derivations end well under the cap. |
| round-10/grader-m06 | 380 | [342, 410] | Code items with defective tests cap all models near 400. |

## t10 (work-8ea654): How many of the 538 HumanEval+ and MBPP+ problems does Think-SFT pass with the Math cue, one sample at T 1.0?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-7B-Think-SFT (no reward)", "prompt": "Math cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0, seed 51000000; top-p and token cap not stated", "samples": 1, "grader": "not stated (tests passed)"}

> HumanEval+ and MBPP+ (538), Code cue and Math cue, T 1.0, 1 sample, seed 51000000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 372 | [325, 412] | On the base the Math cue equals the Code cue (326 vs 317), so expect about the same as the Code-cue cell. |
| reader-2 | 380 | [325, 425] | The Math cue works about as well as the Code cue on the base (326 vs 317); same reasoning as the Code-cue cell. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 388 | [357, 418] | Same prior as the Code-cue cell; on the base the Math cue scored at or slightly above the Code cue (326 vs 317). |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 390 | [355, 420] | Same as t09: short code traces avoid late degeneration; the Math cue worked as well as the Code cue on the base (326 vs 317). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | - |  | theory says nothing |
| round-10/stopping-m03 | 381 | [350, 409] | The Math cue sets no boundary either; same loss as t09. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | 395 | [355, 427] | The prompt opening matters little once the imitation change sets the register (base Math cue = Code cue). |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 389 | [354, 420] | The routines come from the weights, not the cue: Math cue about equal to Code cue. |
| round-10/problems-m03 | 386 | [360, 410] | For a model that already deliberates, the Math cue does what the Code cue does. |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | 386 | [360, 410] | A cue does not recalibrate Think-SFT's closing; Math cue about equals Code cue. |
| round-10/grader-m06 | 376 | [338, 408] | Same ceiling. |

## t11 (work-8b2ec9): How many of the 328 harder problems does Think-SFT answer correctly in its own ChatML chat format, one sample at T 1.0 with a 32,768-token cap, grader v3?

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0, token cap 32,768; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 232 | [216, 247] | Think-SFT with raw template plus cue scores 230 at cap 32,768; its own chat format should be about equal or slightly better. |
| reader-2 | 232 | [215, 248] | Think-SFT with the cue in the raw template has 230 at cap 32,768 (207-212 at 16,384); its own chat format should be similar or slightly better. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | 226 | [210, 242] | Theory: hard328 solutions need 6,000-14,000 tokens, so a 32,768 cap holds every solution; level taken from Think-SFT's cue run at cap 32,768 (230, result-c8b994), a little lower for the untested native format. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | 228 | [214, 242] | Theory part 'a 32k cap makes it finish, single scores rise': Think-SFT's capped answers finish at 32k as in the cue run (207 -> 230, result-c8b994); the native template is assumed to change little. |
| round-09/sampling-m03 | 229 | [215, 243] | A fixed template removes the opening branch just as the cue does, so the native ChatML run should match Think-SFT with the cue at cap 32,768 (230 of 328, result-c8b994), with seed spread of about 10. |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 228 | [212, 244] | Neighbouring cell: Think-SFT with the raw template and cue at cap 32,768 scored 230; the native template should be about equal, with hard328 SD 7-9. |
| round-09/grader-m04 | 228 | [214, 242] | Theory: on hard items an opening change (own ChatML template instead of the cue) moves few problems, so the count stays near Think-SFT with the cue at cap 32,768 (230, result-c8b994). |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | 231 | [215, 246] | Theory: 32k = 16k count plus one in four of Think-SFT's unfinished-work cap hits; Think-SFT 16k single about 208 with about 93 cap hits gives 208 + 23 (as in result-c8b994, 207 -> 230), widened for the untested native template. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | 228 | [214, 242] | Theory: raising the cap finishes Think-SFT's ~85-90 cut answers at its matched-difficulty long-answer rate (~25-30 %, as 23 of 93 in result-c8b994), so about +22 on top of the ~206 at cap 16,384. |
| run-03/f2-m05 | 227 | [212, 242] | Theory: tokens past ~13,600 often degenerate and rarely end right, so cap 32,768 gains only part of the cut answers; anchored on the cue run's 230 at cap 32,768. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 228 | [215, 241] | A prompt change on the checkpoint keeps Think-SFT's length distribution (theory), so at cap 32,768 it lands near the paired cue cell's 230 (result-c8b994). |
| round-09/weights-m04 | 230 | [218, 242] | Theory: a template change on Think-SFT alone leaves its finishing rate and precision unchanged, so the native template matches the cue run at cap 32,768 (230 of 328, result-c8b994) within one-sample noise. |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | 228 | [212, 243] | Theory: imitating long expert traces supplies the plans hard328 needs, and the extra budget lets them finish, so the native format should match Think-SFT's cue cap-32k sample (230). |
| round-10/stopping-m03 | 233 | [219, 247] | At 32k nearly every answer ends in either format; the boundary moves the stop earlier, not the precision, so about the raw-template 230 plus 3. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | 234 | [219, 248] | Think-SFT's own template matches the change that sets its behaviour; at 32k it reaches the cue run's 230 or a little more. |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 233 | [219, 247] | Routines are in the weights; template does not change them; 32k lets competition-length routines finish. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 232 | [218, 246] | Same host, same reach: native format equals the cue run's 230. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 232 | [218, 246] | Same reachable set as the cue run at 32k. |

## t12 (work-8b2ec9): How many of the 328 harder problems does Think-SFT in its own ChatML format answer correctly when its cap-32,768 answers are scored at a 16,384-token cap, one sample at T 1.0, grader v3?

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0, generated at cap 32,768, scored at cap 16,384; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 206 | [188, 222] | Cue version scored at 16,384 is 207 (single samples 201-219); the native format may think longer. |
| reader-2 | 210 | [193, 225] | The cue runs scored at 16,384 have 201-212 (mean 209); about 23 fewer than at the 32k cap. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | 214 | [198, 230] | Theory: hard328 solutions need 6,000-14,000 tokens, so cutting at 16,384 loses only a few right answers versus t11 (the cue run lost 23, so I sit between the theory and that rate). |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | 206 | [192, 220] | Same answers cut at 16,384 bring back the abstaining caps, so the score falls back to Think-SFT's 16k single level (207-212, result-c8b994/818c20). |
| round-09/sampling-m03 | 208 | [196, 220] | The fixed template acts like the cue, so the score at 16,384 should equal the cued Think-SFT score there (207 in the cap-32k run; 4-sample singles 201-219, mean 209). |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 206 | [190, 222] | Same answers counted at 16,384, where the cue run scored 207 (vs 230 at 32k); single-draw SD ~8. |
| round-09/grader-m04 | 206 | [192, 220] | Opening moves few hard problems, and the answers past 16k are the ones lost when scored at 16,384, so it stays near the cue run's 207 at 16k (result-c8b994). |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | 208 | [193, 223] | Theory: scoring the 32k text at 16,384 reproduces a 16k run, so this is Think-SFT's 16k single-sample rate (209.0 mean cue, 207 in the cap32 run), widened for the native template. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | 206 | [192, 220] | Same answers cut at 16,384: the theory's cut tail stays wrong, so the level is Think-SFT's 16k rate on the 328 (207 in the cap-32k cue run, 209 mean of 4). |
| run-03/f2-m05 | 203 | [186, 218] | Long Think-SFT traces lose answers at the cap; scoring at 16,384 removes the late finishes, as in the cue run (207 at 16,384); the native <think> format may run somewhat longer. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 206 | [193, 219] | Answers that run past 16,384 tokens score zero (theory): Think-SFT loses the ~23 right answers that finish between 16k and 32k, as in the cue cell (230 -> 207). |
| round-09/weights-m04 | 208 | [196, 220] | Same clause (template leaves finishing and precision unchanged): equals the cue run scored at 16,384, 207 there and 209 for the stored 4-sample mean. |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | 205 | [188, 221] | Theory: Think-SFT's plans are long, so cutting at 16k drops the unfinished ones; same as the cue run scored at 16k (207). |
| round-10/stopping-m03 | 213 | [199, 227] | At 16k the boundary closes some answers that would run past the cap in the raw template (89 cap hits there); about 15 fewer cut, about a quarter right, so +4 over the raw 16k level of 209. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | 206 | [190, 221] | Answers are as long as in the cue runs; scored at 16k, about the 207-209 level. |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 207 | [193, 221] | At 16k long competition routines are cut as in the raw run. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 207 | [193, 221] | At 16k the cap limits reach to the cue cell's 201-212. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 208 | [192, 222] | Same reachable set at 16k. |

## t13 (work-8b2ec9): How many of the 500 MATH-500 problems does Think-SFT answer correctly in its own ChatML chat format, one sample at T 1.0 with a 32,768-token cap, grader v3?

Unit: right answers of 500. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0, token cap 32,768; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 465 | [452, 476] | Think-SFT cue singles are 454-462 at 16k; cap 32k adds a few, and its own format should be no worse. |
| reader-2 | 465 | [452, 476] | Think-SFT cue singles are 457-462 at 16k with about 25 cap hits; the 32k cap and native format add a few. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | 456 | [444, 468] | Theory: most MATH-500 problems are solved in under 2,000 tokens, so the cap does not bind; level from Think-SFT cue single samples 457-462 (result-818c20). |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | 466 | [456, 476] | A 32k cap turns part of Think-SFT's ~25 MATH-500 cap hits per sample into finished answers, so the single score rises a few points above its 16k level of 457-462 (result-818c20). |
| round-09/sampling-m03 | 462 | [451, 472] | The fixed template acts like the cue: cued Think-SFT on MATH-500 scores 454-462 at cap 16,384, plus a few right answers past 16,384 at cap 32,768. |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 465 | [453, 476] | Think-SFT cue singles on MATH-500 were 454-462; a 32k cap recovers a few of its ~24 cap hits; SD 5-6. |
| round-09/grader-m04 | 464 | [455, 473] | Opening moves few problems, so it sits near the cued Think-SFT singles (454-462); on the easier MATH-500 mix the few cap hits gain a little from the 32k cap (+~5). |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | 464 | [453, 474] | Theory: 16k MATH-500 count (about 459, singles 457-462) plus one in four of about 21 cap hits per sample gives about +5. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | 466 | [456, 475] | Theory: Think-SFT's ~25 MATH-500 cap hits finish at its high long-answer rate (~30-40 % at that difficulty), adding ~8 to the ~458 seen at 16,384. |
| run-03/f2-m05 | 463 | [451, 474] | MATH-500 traces are mostly short, so few reach the late degeneration region; Think-SFT single 454-462 plus a small 32k gain. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 463 | [452, 473] | Same length distribution as Think-SFT with the cue (single samples 454-462 at 16k, ~24 cap hits); the 32k cap lets a few of those cut answers finish right. |
| round-09/weights-m04 | 463 | [452, 473] | Template leaves finishing and precision unchanged, so it matches cued Think-SFT on MATH-500 (singles 457-462) plus a few of its about 25 cap hits that finish under the 32,768 cap. |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | 465 | [452, 477] | Theory: imitation supplies plans and MATH-500 needs few long ones, so Think-SFT stays near its cue level (457-462), plus a few right answers from cut ones finishing at 32k. |
| round-10/stopping-m03 | 467 | [457, 476] | The 16k level plus the few cut answers that finish by 32k; the boundary removes run-on text after answers on easy problems. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | 466 | [455, 476] | MATH-500 singles 457-462 plus a few cut answers finished at 32k. |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 465 | [455, 474] | MATH-500 needs no competition routines; Think-SFT sits at RL's level plus a few from 32k. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | 466 | [457, 475] | The 32k cap reaches only MATH-500's thin tail: a few extra right. |
| round-10/problems-m05 | 466 | [457, 475] | MATH-500 reach for Think-SFT is about 485; 32k moves a single sample a few points toward it. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 465 | [455, 474] | MATH-500 ceiling near 494 leaves little room above 465. |

## t14 (work-8b2ec9): How many of the 500 MATH-500 problems does Think-SFT in its own ChatML format answer correctly when its cap-32,768 answers are scored at a 16,384-token cap, one sample at T 1.0, grader v3?

Unit: right answers of 500. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "Think-SFT's own ChatML template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0, generated at cap 32,768, scored at cap 16,384; top-p not stated", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 460 | [446, 472] | Think-SFT cue single samples at cap 16k are 454-462 on MATH-500. |
| reader-2 | 459 | [446, 470] | Equals the 16k-cap level of Think-SFT singles (454-462). |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | 454 | [442, 466] | Theory: MATH-500 solutions are under 2,000 tokens, so scoring at 16,384 drops only about 2 answers from t13. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | 460 | [450, 470] | Scored at 16k the capped samples abstain again, giving Think-SFT's 16k single level of 457-462 (result-818c20). |
| round-09/sampling-m03 | 459 | [448, 469] | The fixed template acts like the cue: cued Think-SFT singles on MATH-500 at cap 16,384 are 454-462 (mean about 459). |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 459 | [447, 470] | At 16,384 it matches the stored Think-SFT singles (454-462 of 500), SD 5-6. |
| round-09/grader-m04 | 459 | [450, 468] | Same answers cut at 16,384 lose that cap-raise gain, which leaves the cued Think-SFT single level (~459) because the opening moves few problems. |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | 459 | [448, 469] | Theory: the 16k score from 32k text equals a 16k run, Think-SFT's MATH-500 single rate 457-462. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | 458 | [449, 467] | Scored at 16,384 the cut tail counts wrong, so the score is Think-SFT's 16k single-sample level (457-462 with the cue). |
| run-03/f2-m05 | 458 | [445, 470] | Shorter traces keep answers: at 16,384 MATH-500 loses only the few long ones; near Think-SFT single 454-462. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 458 | [447, 468] | Cut answers score zero at 16,384 (theory), so this matches Think-SFT cue singles at the 16k cap (454-462). |
| round-09/weights-m04 | 460 | [449, 470] | Template leaves finishing and precision unchanged, so it matches cued Think-SFT singles at 16,384 on MATH-500 (457-462, result-818c20). |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | 459 | [445, 471] | Theory: MATH-500 is limited by execution, not plans, so at 16k Think-SFT matches its stored cue singles (454-462). |
| round-10/stopping-m03 | 463 | [452, 473] | With fewer of the about 25 MATH-500 cap hits at 16k, a few more answers are scored than in raw-template singles (454-462). |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | 460 | [448, 471] | The 16k level of Think-SFT singles. |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 460 | [449, 470] | Equal to its 16k raw singles, RL-level on MATH-500. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | 459 | [449, 468] | Mid and easy strata unchanged by format; 16k level. |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 459 | [448, 469] | Same ceiling at 16k. |

## t15 (work-60f040): How many of the 500 MATH-500 problems does the untrained base with the cue get right under a majority vote over 9 samples at T 1.0, grader v3?

Unit: right answers of 500. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0 (same cell as the stored 4 samples); top-p and token cap not stated", "samples": 9, "grader": "v3, majority vote over 9 samples"}

> V1 vote over 9 in [449, 462]

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 452 | [445, 459] | Vote over 4 is 446 and pass@4 467; Wang's majority@8 runs about 2.5 points above majority@4, so expect a modest gain for 9. |
| reader-2 | 452 | [444, 460] | Vote over 4 is 446 (tie-short 453, pass@4 467); Wang's majority curve suggests +1-2 points from 4 to 8-9 votes, damped by the extra 0-of-k problems. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | 453 | [446, 460] | Theory: the vote converges to the pretrained mode, and going from 4 to 9 samples only resolves ties (57% of the 54 vote-over-4 failures), worth a few problems; so the stored vote over 4 (446) plus about 7 resolved ties. |
| run-04/f2-m04 | 450 | [444, 456] | Theory: adding samples to a vote moves only the few problems it can flip, so the vote over 9 stays near the stored vote over 4 (446), plus a few problems; spread of about 5-6 on MATH-500. |
| run-08/f2-m01 | 453 | [445, 460] | Stored vote over 4 is 446 and pass@4 is 467; going from 4 to 9 samples adds about 1.5 points, as in Wang Fig. 21's maj4-to-maj8 step; new draws add runner drift. |
| round-09/grader-m04 | 452 | [445, 459] | Theory: votes yield little on hard items, and the ~54 problems still missed after the vote over 4 (446) are MATH-500's hard tail, so going to 9 samples adds only a few. |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | 451 | [445, 457] | Theory's holds_against on fact 28: 57% of the base's vote-over-4 failures are ties that more samples settle, worth about 5 problems by k = 9, so 446 (stored vote over 4) + 5 = 451; the 33-problem near-zero block (0 of 4) caps it well below pass@4 467. |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | 454 | [446, 461] | Theory: samples are independent draws with fixed p_i, so a 9-sample vote pushes problems with p_i above the wrong-answer plurality toward right. Scaled from the stored vote of 4 (446, single mean 410.5, pass@4 467), with a few problems of sd. |
| round-09/stopping-m04 | 454 | [447, 461] | More samples leave the base's ~27 cap hits per sample in place and move only precision of finished answers (theory), so the vote rises a little above the 4-vote's 446, capped below pass@4 467. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | 452 | [445, 460] | Theory: the base's errors on problems it never solves are wrong plans that more votes cannot fix, so the vote plateaus just above the vote over 4 (446) and below pass@4 (467). |
| round-10/stopping-m03 | 452 | [446, 458] | The cued base ends on its own 'Answer:' line at a stable point; the boundary question does not apply and the vote plateaus just above 446. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | 453 | [447, 459] | Vote gains come from the mid stratum (sharpening share 0.45 of the gap), about 30 problems, of which a few more convert at k 9. |
| round-10/problems-m05 | 453 | [447, 459] | Vote approaches the base's pass@k ceiling (467 at k 4) only partly. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 453 | [447, 459] | Base pass@4 467 and the floor bound vote-9 gains to a few points. |

## t16 (work-60f040): How many of the 500 MATH-500 problems does the untrained base with the cue get right under a majority vote over all 12 samples at T 1.0, grader v3?

Unit: right answers of 500. Cell: {"model": "Olmo-3-1025-7B base (untrained)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0 (same cell as the stored 4 samples); top-p and token cap not stated", "samples": 12, "grader": "v3, majority vote over 12 samples"}

> Vote over k = 1..12 samples of the untrained cued base on MATH-500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 453.5 | [446, 461] | Small further gain over the vote of 9; plateau expected. |
| reader-2 | 454 | [446, 462] | Slightly above vote over 9 as the vote plateaus below pass@4. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | 454 | [447, 461] | Theory: beyond about 8 samples the vote plateaus at the modal value, so 12 samples add at most a tie or two over the vote over 9 (~453). |
| run-04/f2-m04 | 451 | [445, 457] | Theory: 3 more samples after 9 flip only a problem or two, so the vote is near the stored 4-vote 446 plus a few; MATH-500 spread of about 5-6. |
| run-08/f2-m01 | 455 | [447, 462] | Vote curve flattens past 9 samples; slightly above the 9-sample vote, bounded by pass@k. |
| round-09/grader-m04 | 453 | [446, 460] | Same difficulty-mix argument: the remaining misses are hard items where more votes yield little, so 12 samples stay about 1 above the vote over 9. |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | 452 | [445, 458] | Theory says the vote plateaus a few samples past 4 and the near-zero block holds after k = 9, so 12 samples add at most about 1 over the k = 9 value of about 451. |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | 457 | [449, 464] | Theory: same independent fixed-p_i vote as t15 with 3 more draws; it rises a little over 9 samples, toward the pass@k ceiling. |
| round-09/stopping-m04 | 455 | [448, 462] | As for the 9-vote: extra samples add only precision on finished answers, and the problems the base cuts at the cap stay lost, so the vote is near its plateau. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | 453 | [446, 461] | Theory: same plan-limited plateau; going from 9 to 12 votes adds at most a point or two over vote-9. |
| round-10/stopping-m03 | 453 | [447, 459] | As t15, one more on the plateau. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | 454 | [448, 460] | Mid stratum nearly exhausted by k 9. |
| round-10/problems-m05 | 454 | [448, 460] | Saturates under pass@4. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 455 | [449, 461] | Ceiling compresses gains past 9 votes. |

## t17 (work-30f0ed): How many of the 328 harder problems does Think-SFT plus 1.5x RL-Math's 8 strongest weight-change directions answer correctly?

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT + RL-Math's top-8 directions at 1.5x", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> Think-SFT + RL-Math's 8 directions at 1.5x, 3x, random 3x on hard328

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 217 | [200, 233] | On the base, top-8 at 1.5x matches full RL (200 vs 200); on Think-SFT the full a=1 transplant gives 220 against Think-SFT's 209. |
| reader-2 | 217 | [200, 232] | Think-SFT single is about 209 and the full transplant at a=1 gives 220; the 8 finishing directions should cut cap hits for a modest gain. |
| run-06/f2-m03 | 222 | [207, 237] | Theory: the top-8 directions at 1.5x carry the finishing part of RL's update, so on Think-SFT (209, ~90 cap hits) they act like the full transplant at about 1x-1.5x (220-232). |
| run-05/f2-m03 | 222 | [207, 237] | The Math edit works in full on math text regardless of host, so on Think-SFT (209) it cuts cap hits as the full RL transplant does (a=1 220, a=2 231.5); 1.5x top-8 sits near a=1-1.5. |
| run-05/f2-m01 | 220 | [207, 233] | The 1.5x dial makes Think-SFT close many of its ~90 cap hits and modestly raises right-of-finished, about like the full transplant M(1) 220 from Think-SFT's 209. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 215 | [200, 230] | Theory: top-8 at nominal 1.5 acts like RL's own top-8 share, which on the base carried nearly the full RL effect; on Think-SFT the full delta at a=1 gave 220 vs 209, so ~215. |
| run-07/f2-m02 | 220 | [206, 233] | Own-domain clause: top-8 at 1.5x carries nearly all of RL's gain, so on Think-SFT it should match the full 1x RL-Math transplant (220 of 328) over Think-SFT alone (~209). |
| run-03/f2-m02 | 221 | [208, 234] | Theory: RL directions on Think-SFT act like the full delta, turning its unfinished cap hits into finished answers; top-8 at 1.5x roughly matches 1x of the full delta (M(1) 220, Think-SFT alone 209). |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 222 | [205, 238] | The top-8 from final weights carries the finishing directions, which cut Think-SFT's about 90 cap hits; full transplant gives 220 at a=1 and 231.5 at a=2, against Think-SFT 209. |
| run-02/f2-m04 | 220 | [206, 234] | Theory: the RL difference makes Think-SFT finish and single scores rise; RL's top-8 directions carry the finishing part, so expect a rise from 209 toward the full M(2) transplant's 231.5 (result-3387ce). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 222 | [207, 237] | On the base, top-8 at 1.5x matched the full RL change, so on Think-SFT the expected count sits between transplant a=1 (220) and a=2 (231.5); hard328 SD ~8. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 220 | [205, 235] | Edit null on the Think-SFT host is its mean (~209, noise control 209) plus the top-8 1.5x share, which on the base equals the full RL gain; full a=1 on Think-SFT adds ~11, so ~220. |
| run-04/f2-m03 | 218 | [205, 231] | Think-SFT fails by not stopping (about 90 cap hits); the 1.5x hazard shift converts roughly half of them at low precision (about 25-35%), as the full a=1 transplant did (220). |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 222 | [206, 237] | Theory: the 8 directions are the finishing dial, so on Think-SFT (whose losses are cap hits with 88% of finished answers right) 1.5x converts a share of its ~90 cap hits, as the full transplant did (a=1: 220, a=2: 231.5, base 209). |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 218 | [205, 231] | Theory: a 1.5x edit is below the degeneration size and cuts Think-SFT's cap losses; between Think-SFT 209 and the full transplant a=1 220 / a=2 231.5. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 222 | [210, 234] | Theory: the top direction's size sets finishing, so top-8 at 1.5x acts on Think-SFT like a full transplant at a=1.5 in finishing terms. That is between a=1 (220) and a=2 (232), with fewer cap hits than Think-SFT's 209. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | 222 | [208, 234] | The RL-Math finishing part (top-8 directions at 1.5x finish about as much as full RL on the base) moved onto Think-SFT closes sound cut work like the full a=1 transplant (220), and the gain is capped by Think-SFT's sound cut work (230 at cap 32k). |
| round-09/weights-m06 | 218 | [205, 231] | Nominal dose: on the base, top-8 at 1.5x matches the full RL change at 1x (200 vs 200), so on Think-SFT it should match Think-SFT + 1x(RL - base), which scored 220. |
| round-09/problems-m05 | 218 | [204, 233] | Theory: Think-SFT supplies plans and RL directions add finishing, so the edit should finish some cut plans, like Think-SFT + 1x RL delta (220), above Think-SFT's 209. |
| round-10/stopping-m03 | 215 | [202, 228] | RL's directions add a stop push to a raw-template Think-SFT that lacks its boundary; cap hits fall as with the a=1 transplant (220), a little less. |
| round-10/stopping-m04 | 216 | [203, 229] | The commit shift lands on Think-SFT through the same lm_head, so cap hits fall from about 90 toward 50 at a small cost in precision, like the a=1 transplant (220). |
| round-10/weights-m01 | 219 | [205, 232] | The stop push turns part of Think-SFT's 94 cap hits into answers, about a quarter of them right (as at cap 32,768), less a small precision loss. |
| round-10/weights-m03 | 216 | [204, 228] | 1.5x top-8 on Think-SFT acts like about a=1 of the full change on finishing (94 -> about 78 cap hits); a=1 gave 220, but without the remainder's correctness, so about 216. |
| round-10/weights-m05 | 218 | [204, 231] | Think-SFT lacks RL's shared readout (its top 8 directions do not finish), so adding it brings finishing. |
| round-10/weights-m06 | 218 | [204, 231] | Direction 1 finishes Think-SFT's cut answers; directions 2-8 add little to a host that is already precise. |
| round-10/training-m05 | 220 | [205, 235] | The edit adds closing to Think-SFT's routines, like the a=1 transplant. |
| round-10/problems-m03 | 219 | [205, 232] | Think-SFT already states answers; the gain comes from closing cut answers. |
| round-10/problems-m04 | 219 | [205, 232] | Think-SFT's misses sit in the long tail; finishing converts some. |
| round-10/problems-m05 | 219 | [205, 232] | Directions reweight Think-SFT's paths; stays below the full transplant's 231.5. |
| round-10/problems-m06 | 219 | [205, 232] | Math-calibrated closing suits Think-SFT's long math derivations: modest gain. |
| round-10/grader-m06 | 217 | [202, 231] | Single sample far from the ceiling. |

## t18 (work-30f0ed): How many of the 328 harder problems does Think-SFT plus 3x RL-Math's 8 strongest weight-change directions answer correctly?

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT + RL-Math's top-8 directions at 3x", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> Think-SFT + RL-Math's 8 directions at 1.5x, 3x, random 3x on hard328

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 170 | [110, 225] | At 3x the base edit decays into word strings (117), but Think-SFT tolerates a=3 full transplant (227), so wide. |
| reader-2 | 185 | [120, 232] | At 3x on the base the 8 directions break the model (117); on Think-SFT the damage may be smaller, so wide interval below the single-sample level. |
| run-06/f2-m03 | 178 | [135, 218] | Theory: overdosing the finishing directions makes the model commit too early (base at 3x falls 164 -> 117), so Think-SFT drops well below its 209. |
| run-05/f2-m03 | 170 | [120, 225] | The in-domain edit acts in full, so 3x top-8 should overshoot on Think-SFT as it does on the base (3x: 117 vs base 164, word strings); Think-SFT's higher start and the a=3 full transplant (227) give a wide interval. |
| run-05/f2-m01 | 195 | [150, 228] | Past 1.5x the dial closes unfinished hard solutions on guesses (base: 203 at 1.5x, 190 at 2x, 117 at 3x), so 3x falls below the 1.5x cell, possibly sharply. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 190 | [150, 225] | Theory: effective size grows faster than nominal, so 3x top-8 overshoots well past RL's share (on the base 2x 190, 3x 117); Think-SFT's finishing deficit absorbs some, giving ~190. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 185 | [140, 225] | Theory: past about 1.5x the hazard closes hard problems with guesses (base at 3x fell to 117), so Think-SFT at 3x falls below its 1.5x value, softened by Think-SFT's high right-of-finished. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 185 | [130, 230] | At 3x the finishing push overshoots (base + top-8 at 3x decays to 117, at 2x 190); Think-SFT is more robust (a=4 full transplant 213), so expect a drop from 209 with a wide range. |
| run-02/f2-m04 | 212 | [185, 236] | Theory says the finishing push raises single scores, but at 3x the turned abstentions are mostly wrong (as right-of-finished fell 88 to 72 % with a, result-3387ce), so the score sits near Think-SFT's 209 with a wide interval. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 170 | [110, 228] | At 3x the top-8 edit broke the base (117 vs 203 at 1.5x) while transplant a=3 on Think-SFT held at 227; wide prior between those, plus sampling SD. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | 180 | [125, 225] | At 3x the hazard shift drives cap hits near zero, but precision collapses as on the base at 3x (117), so most converted answers are wrong and some finished ones break. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 188 | [138, 228] | Theory: at 3x the dial over-finishes and decays (base at 3x: 117, 3x top-1 boxes less); Think-SFT handles larger full transplants (a=4: 213), so the forecast sits between, with a wide interval. |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 170 | [120, 215] | Theory: hazard grows with edit size, with word strings at 2-3x (base + top-8 at 3x fell 164 -> 117), so the 3x edit loses answers on Think-SFT too, maybe less. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 160 | [110, 215] | Theory: about 3x on the top direction breaks generation into word strings whether 1 or 8 directions are scaled (base top-8 at 3x: 117), so Think-SFT drops well below its 209. Wide because the full a=3 transplant kept 227. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | 190 | [150, 230] | A finishing operator in overdose: cap hits fall to near 0 and right-of-finished drops below RL's level; on the base the same 3x size already breaks the model (117), so the forecast is lower than 1.5x and wide. |
| round-09/weights-m06 | 195 | [150, 235] | A nominal 3x top-8 dose broke the base (117), while Think-SFT tolerated a 3-4x full delta (227, 213), so this sits between the two with wide spread. |
| round-09/problems-m05 | 190 | [145, 228] | Theory: finishing beyond the plan's length makes the model box guesses on cut work, and 3x top-8 already broke the base (117), so expect a fall below Think-SFT's level, with high uncertainty. |
| round-10/stopping-m03 | 160 | [108, 212] | At 3x the stop push overwhelms the missing boundary and ends text or makes it degenerate, as on the base (117); Think-SFT tolerates it somewhat better. |
| round-10/stopping-m04 | 150 | [100, 205] | At 3x the commit shift fires at points where no answer is ready, so text ends or becomes word strings (base 3x: 117 right, 9 cap hits); the readout is the same on the Think-SFT host. |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | 212 | [185, 234] | Think-SFT + 3x and 4x the full change, which contain 3x and 4x top-8, did not break (227, 213), so 3x top-8 gives a finishing gain minus a precision loss, near 210. |
| round-10/weights-m05 | 190 | [135, 230] | 3x of the shared readout overdoses; the damage is uncertain. |
| round-10/weights-m06 | 200 | [160, 232] | Direction 1 at 3x unboxes some answers, but Think-SFT + 3x the full change (which contains it) kept 227, so the loss is moderate. |
| round-10/training-m05 | 208 | [182, 231] | Routines survive in the host (it took 4x the whole difference at 213); strong closing trades cap hits for precision. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 165 | [108, 220] | At 3x the top-8 edit breaks paths rather than reweighting them (base 117). |
| round-10/problems-m06 | 165 | [108, 220] | At 3x the closing push overrides any calibration and breaks text (base 117). |
| round-10/grader-m06 | - |  | no forecast |

## t19 (work-30f0ed): How many of the 328 harder problems does Think-SFT plus a random rank-8 weight edit at 3x size answer correctly?

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT + random rank-8 edit at 3x (control)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> Think-SFT + RL-Math's 8 directions at 1.5x, 3x, random 3x on hard328

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 208 | [196, 220] | Random edits do nothing at any size on the base, and noise does nothing on Think-SFT (209); Think-SFT singles are 201-219. |
| reader-2 | 208 | [194, 222] | Random edits change nothing on either host (Think-SFT noise control 209); Think-SFT single about 209. |
| run-06/f2-m03 | 209 | [196, 222] | Theory: random rank-8 gives nothing, so Think-SFT stays at one-sample level (201-212; noise control 209). |
| run-05/f2-m03 | 209 | [196, 222] | Random rank-8 directions are not driven by math text, so the edit has no effect: Think-SFT baseline (~209, as with the 209 noise control). |
| run-05/f2-m01 | 208 | [197, 219] | Random rank-8 edits carry no dial, so it stays at Think-SFT's level (209; noise control 209). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 207 | [195, 220] | Theory: a random rank-8 edit realizes no RL-specific change, so Think-SFT stays at its level (209; noise control 209). |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 208 | [197, 219] | Theory: a random edit does not change the stopping hazard, so Think-SFT stays at its own level (209; noise control 209). |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 208 | [195, 222] | A random rank-8 edit carries none of RL's directions (random 3x on base 163 = base), so Think-SFT stays at its single-sample level of about 209. |
| run-02/f2-m04 | 209 | [198, 220] | A random rank-8 edit does not make Think-SFT finish (the noise control gave 209 with 97 cap hits, result-3387ce), so by the theory its single score stays at Think-SFT's 209. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 209 | [195, 223] | Random edits change nothing on either host (Think-SFT noise control 209, base random flat), so one draw around Think-SFT's 209 mean. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 209 | [198, 220] | A functionless random edit lands at the host's edit null: Think-SFT's mean of about 209 (noise control 209). |
| run-04/f2-m03 | 208 | [196, 220] | Random rank-8 adds no hazard logit (flat on the base, noise control on Think-SFT 209), so the score stays at Think-SFT's 209. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 208 | [197, 220] | Random edits do not produce degeneration (flat at all sizes on the base; noise control on Think-SFT 209), so Think-SFT level. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 209 | [197, 221] | Pooling clause: a random edit on Think-SFT is a near-identical cell to a fresh Think-SFT cue draw (noise control 209, singles 212/212/211/201, mean 209.0), and one seed scatters up to about 12 per 328. |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 208 | [196, 220] | Theory: a random rank-8 edit has no RL top-direction size, so it does not change finishing and Think-SFT stays at its single-sample level (about 209; noise control 209). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | 209 | [199, 219] | A random edit leaves Think-SFT's lengths and cap hits in place (its noise control gave 209 with 97 cap hits), so by the theory the score stays at Think-SFT's 209. |
| round-09/weights-m04 | 209 | [196, 222] | Only the RL difference finishes; a random edit adds neither finishing nor correctness, so Think-SFT stays at its own level (209; same-norm noise control 209, result-3387ce). |
| round-09/weights-m06 | 210 | [200, 221] | Random edits are inert, so this stays at Think-SFT's own hard328 level (single samples 201-219, mean 209; noise control 209). |
| round-09/problems-m05 | 209 | [197, 221] | Theory: a random edit adds neither finishing nor plans, so Think-SFT stays at its level (209; its noise control scored 209). |
| round-10/stopping-m03 | 209 | [197, 221] | Random edits do not move the stopping point; the 209 level. |
| round-10/stopping-m04 | 209 | [197, 221] | A random rank-8 edit has no projection on the commit readout; Think-SFT stays at 209. |
| round-10/weights-m01 | 209 | [197, 221] | Random rank-8 adds no stop push; the noise control was 209. |
| round-10/weights-m03 | 209 | [197, 221] | Noise of the full change's norm already gave 209 on this host. |
| round-10/weights-m05 | 208.5 | [196, 221] | Random has no shared readout. |
| round-10/weights-m06 | 208.5 | [196, 221] | Random carries neither part. |
| round-10/training-m05 | 208 | [196, 220] | Random edit leaves routines and score unchanged. |
| round-10/problems-m03 | 208 | [196, 220] | Random edit changes no format. |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 208 | [196, 220] | Random edit leaves reach and weights of paths. |
| round-10/problems-m06 | 208 | [196, 220] | Random edit carries no closing habit. |
| round-10/grader-m06 | - |  | no forecast |

## t20 (work-30f0ed): How many of the 328 harder problems does the base answer correctly with both RL-Math's and RL-Code's top-8 directions added, each at 1.5x?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + RL-Math top-8 directions at 1.5x + RL-Code top-8 directions at 1.5x", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 188 | [165, 206] | Two 1.5x finishing edits combined act like an overdose (2x gave 190, 3x 117), with partial overlap of Math and Code directions. |
| reader-2 | 190 | [165, 208] | Math 1.5x alone averages 200 and Code 1x adds finishing; the combined dose likely overshoots like the 2x cell (190). |
| run-06/f2-m03 | 190 | [175, 205] | Theory: Code directions add about half again of finishing, so Math 1.5 + Code 1.5 overshoots like ~2x, where commitment comes too early (190 vs 200 at 1.5x). |
| run-05/f2-m03 | 185 | [165, 205] | Math 1.5x acts in full and Code 1.5x transfers about half (Code top-8 1x 178 vs Math 192 on hard328), so the dose is like Math ~2.25x, past the dial's peak (1.5x 203, 2x 190). |
| run-05/f2-m01 | 188 | [172, 203] | Math and Code directions both turn the finishing dial, so (1.5,1.5) acts past 1.5x and closes hard problems on guesses, like the 2x cell (190). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 195 | [180, 208] | Theory: Math 1.5x is at RL's top-8 share (~200) and Code 1.5x adds a further realized finishing push, overshooting like Math 2x (190), so ~195. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 190 | [177, 203] | Theory: hazards add with size; Math 1.5x plus Code 1.5x pushes past the 1.5x optimum, like Math at about 2x (190), where guesses close hard problems. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 192 | [175, 208] | Both edits carry finishing directions, which add up into an overshoot like Math at 2x (190, 5 cap hits); Math 1.5x alone averages 200. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 190 | [172, 207] | Combined norm is like a ~2x dial, where the base scored 190 (finishing saturated, precision falls); single-draw SD ~8 plus structural spread. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 210 | [190, 228] | Parts add up: null 161 + Math top-8 1.5x gain 39.25 + Code top-8 1.5x gain on hard328 (~18, scaled from Code 3.0's +12 at 1x) = ~218, shaded down. |
| run-04/f2-m03 | 192 | [178, 206] | Math and Code hazard shifts add, so the combined dose is past 1.5x Math alone (cap hits near 0), where precision falls as at 2x (190). |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 186 | [160, 205] | Theory: Math and Code top-8 both write finishing (Code top-8 alone: 41 cap hits), so 1.5+1.5 acts like an overdosed dial (Math 2x: 190 right, 5 cap hits; precision falls). |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 188 | [172, 203] | Theory: the summed Math+Code edit at 1.5x each is effectively oversized (like >=2x, where Math alone gave 190), so it gives up some of the 1.5x Math edit's ~200. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 197 | [184, 210] | Theory: per-direction size, not the number of directions, sets finishing and breakdown. Math+Code at 1.5x each (nearly orthogonal) acts like the 1.5x Math edit (about 200), with no over-commit. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 192 | [178, 206] | Nominal doses add: Math 1.5x (200) plus a near-orthogonal Code 1.5x finishing push overshoots like the Math 2x cell (190). |
| round-09/problems-m05 | 192 | [176, 208] | Theory: both sets of directions add finishing but no plans, so on contest-heavy hard328 the score is capped near RL (200-206); the doubled finishing dose overshoots like 2x (190). |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 187 | [168, 204] | Two 1.5x readout shifts add to about a 2.5x Math commit: nearly no cap hits, precision as at 2x (190) or a little lower; no word-string collapse, because the norm is split over two subspaces. |
| round-10/weights-m01 | 181 | [160, 202] | Code's 8 directions cut cap hits about as much per unit as Math's (41 vs 46 at 1x), so 1.5 + 1.5 adds up to roughly a 3x finishing push: past the 2x point (190), right answers fall further. |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | 187 | [168, 204] | The shared part is counted twice, overdosing finishing like Math 2x (190), and Code's math remainder adds little. |
| round-10/weights-m06 | 189 | [168, 206] | The two first directions add their stop pushes into an overdose; directions 2-8 add some right answers. |
| round-10/training-m05 | 191 | [173, 206] | On the base neither edit adds competition routines; both add closing, over-dosed like the 2x cell. |
| round-10/problems-m03 | 189 | [170, 205] | Format is saturated by Math 1.5x alone; Code adds over-dose, not format. |
| round-10/problems-m04 | 189 | [170, 205] | Mid-stratum gain saturated at Math 1.5x; extra dose acts on the tail with low precision. |
| round-10/problems-m05 | 189 | [170, 205] | Base reach caps the combination near RL's 200-206; over-dose loses some. |
| round-10/problems-m06 | 186 | [168, 202] | Code's short-length closing at 1.5x cuts long hard328 derivations on top of Math 1.5x: below Math 1.5x (200), near 2x (190). |
| round-10/grader-m06 | - |  | no forecast |

## t21 (work-30f0ed): How many of the 328 harder problems does the base answer correctly with both RL-Math's and RL-Code's top-8 directions added, each at 1x?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + RL-Math top-8 directions at 1x + RL-Code top-8 directions at 1x", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 197 | [184, 210] | Math 1x gives 192 and Code 1x 178; together they should act like about 1.5x Math (200). |
| reader-2 | 197 | [182, 211] | Math top-8 at 1x is 192 and Code top-8 at 1x is 178; together a dose near 1.5x Math, around 195-200. |
| run-06/f2-m03 | 199 | [186, 212] | Theory: Math 1x (192) plus half-strength Code finishing acts like ~1.5x Math, which reproduces nearly all of RL's gain (~200). |
| run-05/f2-m03 | 200 | [186, 214] | Math 1x in full (192) plus Code 1x at about half (~Math 0.5x) is a dose like Math 1.5x (203; 4-sample mean 200.25). |
| run-05/f2-m01 | 197 | [185, 210] | (1,1) adds up to about a 1.5x dial setting, near the 1.5x peak (200 mean) and above Math 1x alone (192). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 197 | [185, 209] | Theory: Math top-8 at 1x is partly thresholded (192) and Code at 1x loses more, so it adds only a little: ~197. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 198 | [186, 210] | Theory: Math 1x plus Code 1x sums to about the 1.5x-equivalent hazard, near the dial's optimum (Math 1.5x 200-203). |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 198 | [183, 212] | Math top-8 at 1x (192) plus Code's nearly orthogonal finishing and error-reducing directions at 1x (Code alone 178) give a combined push near Math 1.5x (200). |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 198 | [184, 212] | Math 1x (192) plus near-orthogonal Code 1x acts like about a 1.5x dial (200-203); SD ~8. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 200 | [186, 214] | Parts add up: null 161 + Math top-8 1x gain (~31) + Code top-8 1x gain (~12) = ~204, shaded down. |
| run-04/f2-m03 | 197 | [184, 210] | The summed 1x+1x hazard shift is about a 1.5x Math dose, near the dial's peak (about 200), with a small precision cost from the Code part. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 196 | [181, 210] | Theory: two finishing dials at 1x add up to about Math at 1.5x (203; 200.25 over 4 samples) without overdose, slightly below because Code's directions add less right-answer content (Code top-8 178 vs Math 192). |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 197 | [184, 210] | The 1x+1x sum is close to a single 1.5x-size edit, below the hazard; near Math 1x 192 to 1.5x 200. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 192 | [180, 204] | Theory: per-direction size 1x sets finishing as in the 1x Math edit (192/328). Adding Code's directions does not raise the per-direction size. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 198 | [185, 210] | Math 1x (192) plus Code 1x's extra finishing dose lands near the Math 1.5x level (200-203). |
| round-09/problems-m05 | 198 | [185, 211] | Theory: finishing without plans tracks RL on hard328; the combined 1x+1x dose is about Math 1.5x (200.25 mean). |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 199 | [187, 211] | 1x plus 1x adds to about a 1.6x Math commit, close to the best dial point (200 mean at 1.5x). |
| round-10/weights-m01 | 191 | [178, 204] | 1 + 1 adds up to about a 2x Math finishing push with Math-1x correctness, the cell that scored 190. |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | 200 | [188, 212] | At 1+1 the twice-counted shared part is about 1.5x (192 -> 200), and Code's remainder adds its overlapping math share (Code 1x 178 vs random 158, about half of it not shared), so about 200. |
| round-10/weights-m06 | 197 | [184, 210] | Like 1.5x Math. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 197 | [185, 209] | Two 1x format edits give about Math 1.5x. |
| round-10/problems-m04 | 197 | [185, 209] | Combined 1x edits reach about Math 1.5x's mid-stratum gain. |
| round-10/problems-m05 | 197 | [185, 209] | Two 1x edits saturate toward the base-host ceiling near 200. |
| round-10/problems-m06 | 195 | [183, 207] | Code 1x adds closing with a short calibration; little gain over Math 1x (192). |
| round-10/grader-m06 | - |  | no forecast |

## t22 (work-30f0ed): How many of the 328 harder problems does the base answer correctly with RL-Math's top-8 directions plus a random rank-8 edit in place of the Code directions?

Unit: right answers of 328. Cell: {"model": "Olmo-3-1025-7B base + RL-Math top-8 directions + random rank-8 edit (control; scales not stated)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 197 | [184, 209] | The random part adds nothing, so expect Math top-8 alone: 192 at 1x, about 200 at 1.5x. |
| reader-2 | 198 | [185, 211] | The random edit adds nothing, so this equals Math top-8 alone (192 at 1x, 200 mean at 1.5x). |
| run-06/f2-m03 | 199 | [186, 211] | Theory: random rank-8 adds nothing, so this equals Math top-8 at 1.5x alone (mean 200.25). |
| run-05/f2-m03 | 197 | [183, 211] | The random rank-8 part is not driven by math text, so this cell equals the Math edit alone (1x 192, 1.5x mean 200.25). |
| run-05/f2-m01 | 196 | [184, 209] | Random edits carry no dial, so it equals Math top-8 alone at 1-1.5x (192-200). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 198 | [187, 210] | Theory: the random edit realizes nothing RL-specific, so the cell equals Math top-8 alone (192 at 1x, ~200 at 1.5x). |
| run-07/f2-m02 | 198 | [185, 211] | Own-domain clause: Math top-8 at 1.5x carries nearly all of RL's hard328 gain (RL ~200-206 vs cued base 164); a random edit writes no habit, so it adds nothing. |
| run-03/f2-m02 | 197 | [185, 209] | Theory: the random part adds no hazard, so this equals Math top-8 alone at 1x to 1.5x (192-203). |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 197 | [183, 211] | The random part adds nothing, so this is Math top-8 alone (192 at 1x, mean 200 at 1.5x). |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 197 | [182, 211] | Random rank-8 adds nothing, so this is the Math top-8 cell alone (192 at 1x, 200 at 1.5x); SD ~8. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 200 | [190, 211] | The random part adds nothing beyond the null, so the cell equals the Math top-8 edit's replicated 200.25. |
| run-04/f2-m03 | 197 | [184, 210] | The random part adds no hazard logit, so the cell equals the Math top-8 edit alone at 1-1.5x (192-200). |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 195 | [181, 209] | Theory: only the RL directions carry the dial (random rank-8 stays flat at 158-167), so this matches Math top-8 alone at 1x-1.5x (192-203). |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 199 | [187, 211] | A random part adds no degeneration hazard (flat), so near the Math top-8 edit alone (~200 at 1.5x). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 199 | [187, 210] | Pooling clause: Math top-8 plus a random edit pools with the Math top-8 1.5x cell (random edits add nothing), so it regresses to that cell's 4-sample mean of 200.25, not the notable first 203; wide because the scale is not stated (1x = 192). |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 198 | [185, 211] | Theory: the random rank-8 adds no RL top-direction size, so the cell equals Math top-8 alone (192 at 1x, about 200 at 1.5x). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 198 | [185, 210] | The random part is inert, so the score is the Math top-8 edit alone: 200.25 at 1.5x, 192 at 1x. |
| round-09/problems-m05 | 199 | [186, 212] | Theory: a random edit adds nothing, so this equals the Math directions alone, which track RL (192 at 1x, 200 at 1.5x). |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 196 | [185, 208] | The random part adds no commit shift, so this is Math top-8 alone at an unstated size (192 at 1x, 200 at 1.5x). |
| round-10/weights-m01 | 197 | [185, 210] | The random rank-8 edit writes no stop logit (cap hits flat at 67-79 for every size), so this is Math top-8 alone, 192-200. |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | 197.5 | [185, 210] | Random shares no subspace with Math (overlap 0.002), so this is Math alone. |
| round-10/weights-m06 | 197.5 | [185, 210] | The random part adds nothing. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 197 | [185, 209] | Random adds nothing; Math directions alone. |
| round-10/problems-m04 | 197 | [185, 209] | Random adds nothing in any stratum. |
| round-10/problems-m05 | 197 | [185, 209] | Random adds no paths. |
| round-10/problems-m06 | 197 | [185, 209] | No code calibration added; Math directions alone. |
| round-10/grader-m06 | - |  | no forecast |

## t23 (work-30f0ed): How many of the 538 HumanEval+ and MBPP+ problems does the base pass with both RL-Math's and RL-Code's top-8 directions added, each at 1.5x?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + RL-Math top-8 directions at 1.5x + RL-Code top-8 directions at 1.5x", "prompt": "not stated", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "not stated", "samples": "not stated", "grader": "not stated (tests passed)"}

> base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 388 | [364, 405] | On code, Code top-8 gives 399 at 1.5x and 394 at 2x; adding Math 1.5x may overdose slightly. |
| reader-2 | 390 | [365, 410] | Code top-8 at 1.5x passes 399 and Math 1.5x 368; adding both risks overshoot, so a little under 399. |
| run-06/f2-m03 | 390 | [373, 406] | Theory: in-domain Code 1.5x gives ~RL (399); adding Math's half-strength finishing overshoots toward 2x (394), slightly lower. |
| run-05/f2-m03 | 390 | [372, 405] | On code, Code 1.5x acts in full (399) and Math 1.5x transfers roughly half (368 vs random 331), so the dose is like Code ~2.3x, near the 2x cell's 394. |
| run-05/f2-m01 | 390 | [370, 405] | On code the combined dial overshoots 1.5x (Code 1.5x 399, 2x 394), so the score sits slightly below the Code peak. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 393 | [375, 408] | Theory: Code's delta peaks at a larger nominal size, so Code 1.5x (399) is near its peak and adding Math 1.5x adds a little finishing but risks overshoot: ~393. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 388 | [372, 402] | Theory: on code the Code directions are in-domain, and adding Math's at 1.5x puts the total above the 1.5x optimum (Code 1.5x 399, 2x 394), with a small loss to guesses. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 395 | [375, 411] | Code top-8 at 1.5x gives 399 and at 2x 394; adding Math's directions pushes finishing further, near the plateau. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 392 | [373, 410] | Code top-8 at 1.5x scored 399, and adding Math directions gives little more on code (Math 1.5x alone 368); SD ~9 on 538. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 415 | [390, 440] | Parts add up on code: random null 331 + Code 1.5x gain 68 + Math 1.5x gain 37 = 436, shaded toward the ceiling near RL-Code 401. |
| run-04/f2-m03 | 393 | [378, 407] | On code, Code top-8 at 1.5x already removes almost all cap hits (399); extra Math dose adds little finishing and costs some precision, like Code 2x (394). |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 386 | [362, 403] | Theory: summed finishing dials over-finish on code like Code top-8 at 2x (394) or more, a little below Code 1.5x (399). |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 390 | [370, 406] | Theory: a larger summed edit adds hazard; Code 1.5x alone 399, 2x 394, so the combined edit sits slightly below. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 392 | [375, 408] | Theory: per-direction size 1.5x is below breakdown and code answers are short, so the pair acts like Code top-8 at 1.5x (399) and does not add up; slight cost from the extra Math perturbation. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 392 | [375, 405] | Code 1.5x alone passes 399 and Code 2x 394; adding Math 1.5x's dose overshoots slightly, as larger code doses do. |
| round-09/problems-m05 | 395 | [380, 410] | Theory: easy code needs finishing, not plans, so the directions reach RL-Code's level (401; Code 1.5x 399), with slight overshoot from the extra Math dose. |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 392 | [374, 406] | On code the combined shifts act like Code's directions at 2x (394): every answer finishes and precision is a little lower. |
| round-10/weights-m01 | 393 | [378, 407] | Code answers are short, so an overdosed stop push finishes them at little cost (Code 2x 394 vs 1.5x 399). |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | 391 | [370, 408] | On code the shared readout is doubled (little cost on short answers; Code 2x 394) plus Code's code remainder. |
| round-10/weights-m06 | 390 | [368, 408] | Code directions 2-8 carry code correctness; the extra stop push costs little. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 391 | [372, 406] | Code 1.5x already has 4 cap hits and 5 missing blocks; extra Math dose cannot pass the test ceiling and slightly overshoots. |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 390 | [370, 406] | Code 1.5x (399) is at the base host's code ceiling; more dose cannot add. |
| round-10/problems-m06 | 392 | [374, 407] | On short code tasks Math's long calibration has no room to act; near Code 1.5x/2x (394-399). |
| round-10/grader-m06 | 389 | [368, 405] | Near the code ceiling. |

## t24 (work-30f0ed): How many of the 538 HumanEval+ and MBPP+ problems does the base pass with both RL-Math's and RL-Code's top-8 directions added, each at 1x?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + RL-Math top-8 directions at 1x + RL-Code top-8 directions at 1x", "prompt": "not stated", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "not stated", "samples": "not stated", "grader": "not stated (tests passed)"}

> base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 392 | [375, 406] | Code 1x gives 386 and Math 1.5x alone gives 368 on code; combined should be near the Code 1.5x level of 399. |
| reader-2 | 391 | [370, 408] | Code top-8 at 1x passes 386; adding Math directions at 1x brings the total dose near 1.5x (399). |
| run-06/f2-m03 | 396 | [382, 410] | Theory: Code 1x (386) plus half-strength Math finishing acts like ~1.5x Code, about RL-Code's level (399-401). |
| run-05/f2-m03 | 395 | [380, 408] | Code 1x in full on code (386) plus Math 1x at about half is a dose like Code 1.5x (399). |
| run-05/f2-m01 | 394 | [378, 408] | Code 1x (386) plus Math's finishing directions acts near the 1.5x peak of the code dial (399). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 390 | [372, 405] | Theory: Code 1x loses more to thresholding (386), and Math 1x adds a little realized finishing push: ~390. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 395 | [380, 408] | Theory: Code 1x (386) plus Math 1x sums to roughly a Code-1.5x hazard (399). |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 392 | [372, 408] | Code top-8 at 1x (386) plus Math's 1x finishing directions (Math 1.5x alone on code 368 vs random 331). |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 391 | [372, 408] | Code 1x scored 386; adding Math 1x adds some finishing, near the 1.5x level of 399; SD ~9. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 400 | [380, 420] | Parts add up on code: null 331 + Code 1x gain 55 + Math 1x gain (~25) = ~411, shaded down. |
| run-04/f2-m03 | 390 | [375, 404] | Code 1x (386) plus Math 1x adds hazard toward the 1.5x level (399), so the score lands between them. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 392 | [375, 406] | Theory: Code top-8 at 1x (386) plus Math's finishing directions (Math 1.5x alone on code: 368) push toward the 1.5x code dial level (399). |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 392 | [375, 406] | A moderate summed size keeps answers; Code 1x 386 plus some Math help, under 1.5x Code's 399. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 385 | [368, 400] | Theory: per-direction size 1x sets finishing as in Code top-8 at 1x (386/538). The Math directions add no size. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 393 | [378, 405] | Code 1x passes 386; adding Math 1x's finishing dose moves it toward the 1.5x level (399). |
| round-09/problems-m05 | 392 | [377, 406] | Theory: finishing directions from both rewards approach RL-Code (401); Code 1x alone gave 386, plus Math's finishing. |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 396 | [381, 409] | Code 1x (386) plus Math 1x commit is about Code at 1.6x, near 399. |
| round-10/weights-m01 | 392 | [376, 407] | Adding the two pushes is like Code 1.5-2x, which is flat at 394-399 on code. |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | 395 | [381, 408] | Code 1x 386 plus Math's shared readout, which raises finishing to Code's 1.5x level (399). |
| round-10/weights-m06 | 391.5 | [373, 407] | Same at 1x. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 393 | [377, 406] | Code 1x (9 cap, 8 no block) plus Math 1x closes the rest of the format gap, near 1.5x's 399. |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 392 | [376, 406] | Saturates near the 399-401 ceiling. |
| round-10/problems-m06 | 393 | [377, 407] | Code 1x (386) plus Math 1x's partial gain on short tasks. |
| round-10/grader-m06 | - |  | no forecast |

## t25 (work-30f0ed): How many of the 538 HumanEval+ and MBPP+ problems does the base pass with RL-Math's top-8 directions plus a random rank-8 edit in place of the Code directions?

Unit: problems passed of 538. Cell: {"model": "Olmo-3-1025-7B base + RL-Math top-8 directions + random rank-8 edit (control; scales not stated)", "prompt": "not stated", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "not stated", "samples": "not stated", "grader": "not stated (tests passed)"}

> base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 362 | [343, 381] | Math top-8 at 1.5x on code gives 368 and random adds nothing; somewhat lower if the scale is 1x. |
| reader-2 | 366 | [345, 385] | Math top-8 at 1.5x on code passes 368 and a random edit adds nothing (random 331 vs base 317). |
| run-06/f2-m03 | 368 | [352, 384] | Theory: another reward's directions give about half (Math 1.5x on code 368) and random adds nothing. |
| run-05/f2-m03 | 364 | [345, 382] | The random part is not driven, so this equals the Math edit on code, which transfers at about half the in-domain effect (Math 1.5x on code 368). |
| run-05/f2-m01 | 362 | [345, 380] | Random carries no dial, so it equals Math's directions alone on code (368 at 1.5x, a bit lower at 1x). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 366 | [345, 385] | Theory: random edit adds no realized RL-specific change, so the cell equals Math top-8 on code (368 at 1.5x). |
| run-07/f2-m02 | 360 | [343, 377] | Cross-domain clause: Math top-8 on code carries about half of what own-domain 1.5x carries (all of RL-Code's 84-point gain over the cued base 317), so 317 + 42 = ~360; the random part adds no habit. |
| run-03/f2-m02 | 364 | [345, 382] | Theory: random adds nothing, so this is Math directions alone on code (368 at 1.5x; random 331). |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 366 | [348, 384] | The random part adds nothing, so this is Math top-8 on code (368 at 1.5x, random 331). |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 368 | [350, 386] | Equals the Math top-8 on code cell (368), since the random edit adds little; SD ~9. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | 368 | [355, 381] | The random part adds nothing beyond the null, so the cell equals Math's top-8 1.5x on code, 368. |
| run-04/f2-m03 | 366 | [350, 382] | The random part adds no hazard, so this matches Math top-8 alone on code (368 at 1.5x). |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 364 | [343, 383] | Theory: only Math's directions finish (random adds nothing: 331 vs cue 317), so this matches Math top-8 at 1.5x on code (368), or slightly less at 1x. |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 366 | [348, 383] | A random part adds no hazard; level of Math directions at 1.5x on code (368). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 366 | [354, 378] | Pooling clause: Math top-8 plus random pools with the stored Math-directions-on-code cell (368 of 538, one draw); a new seed scatters about +-7 per 500, slightly more per 538. |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 365 | [349, 381] | Theory: random rank-8 adds nothing, so the cell equals Math top-8 on code (368 at 1.5x). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 368 | [352, 384] | The random part is inert, so this equals Math top-8 at 1.5x on code: 368 of 538. |
| round-09/problems-m05 | 366 | [350, 382] | Theory: only the finishing in the Math directions acts and random adds nothing, so this equals Math 1.5x on code (368). |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 365 | [347, 382] | Math's commit shift on code gives 368 at 1.5x; the random edit adds no shift. |
| round-10/weights-m01 | 364 | [345, 382] | Math 1.5x on code 368; the random part adds no stop push. |
| round-10/weights-m03 | - |  | no forecast |
| round-10/weights-m05 | 362 | [343, 381] | Math's shared readout alone on code (368 at 1.5x); random adds nothing. |
| round-10/weights-m06 | 364 | [345, 383] | Math's directions on code finish answers but add little code correctness. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 364 | [346, 381] | Math directions fix part of the missing blocks (368 at 1.5x); random adds none. |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | 363 | [346, 380] | Math directions give a partial code gain (368 at 1.5x); random adds none. |
| round-10/grader-m06 | - |  | no forecast |

## t26 (work-8b4030): How many of the 328 harder problems does Think-SFT plus twice the RL-Math weight change get right under a majority vote over 4 samples (the stored 234 and 229 samples plus 2 new)?

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT + 2 x (RL-Math - base), M(2)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated (seeds of samples 3-4: 3,200,000 and 3,300,000)", "samples": 4, "grader": "not stated, majority vote over 4 samples"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 249 | [238, 259] | Singles are about 231; Think-SFT's vote adds 32, RL's 21 and the 1.5x edit's 14; M(2) has fewer cap hits, so expect about +18. |
| reader-2 | 249 | [239, 258] | M(2) singles 234/229; on fresh2026 its vote gain was about 0.7 of Think-SFT's, and Think-SFT gains 32 on the 328, so about +20 over the single mean. |
| run-06/f2-m03 | 243 | [233, 253] | Theory: RL's update makes Think-SFT finish (singles 234/229), so fewer abstentions and less voting headroom than Think-SFT's +32; the vote adds ~10 to the 232 mean. |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 245 | [236, 254] | The RL change (including its dial) makes M(2) finish more, so its vote gains less over singles (231.5) than abstaining Think-SFT does, giving modestly above Think-SFT's 241. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 248 | [237, 258] | Theory: the full delta makes Think-SFT finish (44 cap hits, single mean 231.5), so the vote gains less than Think-SFT's +32 abstention vote; I scaled by the fresh2026 vote-gain ratio (~0.7) to get about +17. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 245 | [235, 254] | The full final delta carries the late finishing and error-reducing parts, so M(2) singles are about 231 with fewer cap hits than Think-SFT; the vote gain falls between RL's (+21) and Think-SFT's (+32), less because of lower precision. |
| run-02/f2-m04 | 245 | [237, 253] | Theory: the RL difference turns abstentions into scattered wrong answers, so M(2)'s vote gain shrinks from Think-SFT's +32 to about RL's/edit's +14 over the single mean of 231.5 (fresh: M(2) vote +10.75 vs Think-SFT +15). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | 249 | [240, 258] | Theory: the samples are independent per-problem Bernoulli draws around M(2)'s mean of 231.5, so the 4-vote adds only the problems with intermediate p; vote gain set like M(2)'s fresh2026 gain (+10.75 over the mean, about 0.7 of Think-SFT's), giving about +17 on hard328. |
| run-08/f2-m01 | 248 | [238, 258] | Stored singles 234 and 229 plus two new draws; the vote gain is smaller than Think-SFT's +32, scaled by the fresh2026 ratio (M(2) +10.75 vs Think-SFT +15), and capped near pass@4. |
| round-09/grader-m04 | 248 | [238, 258] | Theory: the vote's gain scales with abstentions. M(2) abstains less than Think-SFT (about 54 vs 94 cap hits), so its gain over its ~231 singles falls between RL's +21 and Think-SFT's +32 on hard328. |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 250 | [239, 261] | A 2x full delta on Think-SFT is not oversized (227 even at 3x); singles 231.5, and the vote gain sits between RL's (+21) and Think-SFT's (+32), scaled as on fresh2026 (+10.75 vs +15). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 250 | [240, 260] | Regression clause: the stored 234/229 sit above M(2)'s mean, so the two new draws come in near 228; adding the board's vote gain for a model that finishes more than Think-SFT (fresh2026 M(2) +10.75 of 136, scaled to the 328) gives about 250. |
| round-09/sampling-m06 | 245 | [236, 254] | A vote wins only the problems where the right answer is the most likely value. M(2) finishes more often than Think-SFT (54 against 94 cap hits) but writes more wrong values, so its gain over the single-sample mean of 231.5 is set between RL's +21 and the 1.5x edit's +14 and is capped by the near-zero block on hard328: about +14. |
| round-09/weights-m01 | 245 | [235, 254] | Theory: 2x over-commits on long problems, so M(2) finishes more wrong answers and its vote gain over its single mean (231.5) is smaller than Think-SFT's 32. Expect about +14, like RL's vote and M(2)'s fresh2026 vote gain. |
| round-09/sampling-m01 | 248 | [239, 257] | Theory: the two new samples land around the M(2) arm mean of 231.5. The vote's gain over the single mean comes from the independent-draw p_i spread; it is scaled between Think-SFT (+32 on the 328) and RL (+21), as M(2)'s fresh2026 vote gain is about 0.7 of Think-SFT's. |
| round-09/stopping-m04 | 249 | [239, 258] | New seeds keep M(2)'s length distribution (theory), so the vote gains only by selecting among finished answers: the singles average 231.5, with a vote gain between RL's (+21) and Think-SFT's (+32) that is scaled by M(2)'s fewer cap hits. |
| round-09/weights-m04 | 245 | [236, 253] | The delta adds no correctness, so M(2)'s pass@4 is about Think-SFT's (244) plus a few sound cut answers it now finishes; its lower precision (about 72 % right of finished) costs a few votes, and singles average about 231. |
| round-09/weights-m06 | 245 | [234, 256] | Rounding spread around a nominal single-sample mean of about 231.5; the vote gain is smaller than Think-SFT's +32 because the delta makes it finish more (fresh2026 vote gain about 0.7 of Think-SFT's). |
| round-09/problems-m05 | 247 | [237, 257] | Theory: Think-SFT's plans plus RL's finishing give singles near 231.5; the vote gains less than Think-SFT's +32 because precision drops, so above Think-SFT's 241 vote, as on fresh2026 (83 vs 75). |
| round-10/stopping-m03 | 249 | [240, 258] | M(2) stops earlier through RL's push, standing in for the boundary; the vote adds about +18 over the singles. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | 249 | [239, 258] | M(2) finishes more answers at lower precision, so its vote gains less than Think-SFT's +32; about +18 over 231. |
| round-10/weights-m03 | 249 | [239, 258] | M(2) singles 234/229; its vote gain is about 0.7 of Think-SFT's, as on fresh2026. |
| round-10/weights-m05 | 249 | [239, 258] | The full change carries the readout; the vote adds about +18. |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 250 | [240, 260] | M(2) keeps Think-SFT's routines with more finishing; vote near its pass@4 minus some selection loss. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 248 | [239, 257] | Vote bounded by M(2)'s pass@4, a little above Think-SFT's 244. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 249 | [241, 256] | Vote bounded by M(2)'s pass@4 well below the floor-limited ceiling. |

## t27 (work-8b4030): How many of the 500 MATH-500 problems does Think-SFT plus twice the RL-Math weight change answer correctly in one sample?

Unit: right answers of 500. Cell: {"model": "Olmo-3-7B-Think-SFT + 2 x (RL-Math - base), M(2)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 467 | [457, 477] | a=1 transplant gives 467 on MATH-500 and Think-SFT singles are 454-462. |
| reader-2 | 468 | [458, 477] | Think-SFT + 1x delta gives 467 and Think-SFT alone 457-462; a=2 is level or slightly higher. |
| run-06/f2-m03 | 468 | [458, 477] | Theory: the finishing directions turn Think-SFT's MATH-500 cap hits into answers; a=1 gave 467 and 2x adds little on short problems. |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 466 | [458, 474] | Dial plus modest correctness gain on finished answers: like M(1) 467 and above Think-SFT's 457-462; MATH-500 problems are mostly already finished. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 465 | [455, 474] | Theory: on MATH-500 few Think-SFT answers are unfinished, so doubling the delta changes little from M(1) 467 and Think-SFT 457-462. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 466 | [457, 474] | Transplanting the final delta adds the late parts to Think-SFT (a=1 gives 467 on MATH-500, Think-SFT 457-462); a=2 is about equal. |
| run-02/f2-m04 | 468 | [459, 477] | Theory: the RL difference makes Think-SFT finish and single scores rise: at or slightly above a=1's 467 and above Think-SFT's 457-462 (result-3387ce). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 466 | [455, 476] | Neighbouring transplant a=1 scored 467 on MATH-500; a=2 should be about the same, SD 5-6. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | 464 | [454, 474] | MATH-500 has few cap hits, so the larger a=2 hazard dose converts little; precision below finished answers trims a bit off a=1's 467. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 466 | [455, 476] | At 2x the transplant does not degenerate and MATH-500 traces are short; near a=1's 467. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 465 | [455, 474] | Pooling clause: one MATH-500 seed of M(2) lands near the pooled level of the near-identical transplant and Think-SFT/RL cells (a=1 467, Think-SFT 457-462, RL 456-463), with about 7 per 500 of scatter. |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 468 | [458, 477] | Theory: 2x over-commit costs only on long problems, and MATH-500 answers are short. So M(2) sits at or slightly above a=1 (467) and Think-SFT singles (457-462). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | 466 | [457, 474] | Finishing gain is capped by Think-SFT's few cut answers on MATH-500 (about 25), so a=2 sits near a=1's 467, with precision drifting toward RL's. |
| round-09/weights-m06 | 466 | [455, 476] | The full delta acts at its nominal 2x on Think-SFT; on MATH-500 a=1 gave 467 and Think-SFT alone 454-462, so 2x stays near that ceiling. |
| round-09/problems-m05 | 466 | [455, 476] | Theory: on execution-limited MATH-500, Think-SFT plus RL finishing sits at the a=1 transplant (467) and Think-SFT singles (457-462). |
| round-10/stopping-m03 | 467 | [458, 476] | Few MATH-500 answers run on; a=2 is at the a=1 level. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | 468 | [458, 477] | MATH-500 has few cap hits left to convert at a=2; level with a=1's 467. |
| round-10/weights-m03 | 468 | [458, 477] | The weak push on this host leaves MATH-500 near a=1's 467. |
| round-10/weights-m05 | 467.5 | [458, 477] | MATH-500 saturates. |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 466 | [457, 475] | On MATH-500 routines do not matter: RL/Think-SFT level. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | 467 | [458, 476] | MATH-500's thin tail limits what a=2 can add over a=1's 467. |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 467 | [459, 475] | Near the MATH-500 ceiling. |

## t28 (work-8b4030): How many of the 328 harder problems does Think-SFT plus twice the RL-Math weight change answer correctly in one sample with the token cap raised to 32,768?

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT + 2 x (RL-Math - base), M(2)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "token cap 32,768, seed 3,000,000; temperature and top-p not stated", "samples": 1, "grader": "not stated"}

> Added (amendment 3, no new box): M(2) at cap 32,768 on hard328, seed 3,000,000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 240 | [227, 252] | M(2) is about 231 at 16k with about 54 cap hits; a 32k cap finishes most of them and about a quarter are right, as for Think-SFT. |
| reader-2 | 243 | [230, 256] | M(2) about 232 at 16k with about 54 cap hits; Think-SFT turned 25 % of its cut answers right at the 32k cap, so about +11. |
| run-06/f2-m03 | 240 | [228, 252] | Theory: the RL update already makes M(2) finish before 16k (cap hits ~54 vs Think-SFT 94), so the 32k cap rescues only a quarter of those (+~6 over 234). |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 238 | [228, 248] | The dial already closes most answers before 16,384, so a 32,768 cap adds less than for Think-SFT (+23): a few points over 231.5. |
| run-02/f2-m01 | 236 | [224, 248] | Theory: hard328 solutions fit in 6,000-14,000 tokens, so raising M(2)'s cap from 16,384 to 32,768 adds only a few answers over its 234/229 at 16,384 (result-3387ce). |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 238 | [228, 248] | Theory: the delta already finished most answers (44 cap hits left vs Think-SFT's 93), so the 32k cap rescues only about a quarter of the remaining cap hits, roughly +7 over 231.5. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 240 | [229, 251] | M(2) has about 54 cap hits at 16,384 (single 231.5); with a 32,768 cap about a fifth of the cut answers finish right, as with Think-SFT (+23 from 93), so +8 to +10. |
| run-02/f2-m04 | 239 | [230, 248] | M(2) already finishes most answers (33 cap hits at 16k), so a 32k cap turns only a few remaining abstentions into answers, about a quarter right: a small rise above its 234 at the same seed. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 241 | [228, 254] | 16k singles average 231.5 with ~54 cap hits; about a quarter of cut answers come out right at 32k, as for Think-SFT (+23 from 93); one-draw SD ~8. |
| round-09/grader-m04 | 238 | [226, 250] | Theory: answers past 16k are mostly unfinished or guessed, so the cap raise turns only ~15-20% of M(2)'s ~54 cap hits into right answers, about +7 over its ~231 singles. |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | 241 | [230, 252] | Under the survival model, doubling the cap leaves about S^2 of the 54 cap hits; the roughly 45 converted answers are right at a late-answer precision of about 25%, giving about 231.5 + 10. |
| round-09/grader-m06 | 241 | [228, 253] | Theory's yield rule: M(2)'s 16k count 231.5 plus its 54 cap hits times a yield between Think-SFT's 1/4 and RL's 1/10 (about 0.18) gives about +10. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | 241 | [229, 253] | Theory: M(2)'s ~54 cut answers finish at a rate between Think-SFT's unfinished-work rate and RL's guessing rate (~15-20 %), adding ~9-10 to its ~232 at cap 16,384. |
| run-03/f2-m05 | 240 | [228, 252] | Theory: answers extended past 16k mostly degenerate and rarely end right, so the 32k cap recovers only ~20% of M(2)'s ~54 cap hits on top of ~232. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 242 | [230, 254] | Seed clause: the 16k mean regresses to about 230 (234 was the high first draw), and the larger cap recovers about a quarter of M(2)'s ~75 cap hits (Think-SFT recovered 23 of 93); one draw scatters 9-19. |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 240 | [229, 251] | Theory: at 2x, M(2) over-commits, so fewer of its answers are cut. The roughly 50 remaining cap hits finish at 32k with about a quarter right, which adds about 10 to the 231.5 seen at 16k. |
| round-09/sampling-m01 | 238 | [227, 249] | Theory: a same-seed rerun is a new draw around the arm mean of 231.5, not the stored 234 (sd about 7). The cap raised to 32,768 adds a few right answers from M(2)'s roughly 54 cap hits, at the 25% finish-right rate the board reports for Think-SFT. |
| round-09/stopping-m04 | 240 | [229, 250] | Cut answers score zero at 16k (theory); raising the cap lets M(2)'s ~33 cut answers finish, about a quarter of them right (Think-SFT 23 of 93), added to the same-seed 16k level of about 232. |
| round-09/weights-m04 | 234 | [224, 244] | The delta only shortens Think-SFT's own sound work, so at cap 32,768 M(2) reaches about Think-SFT's own cap-32k ceiling (230) or its 16k level (231.5), not 240 or more. |
| round-09/weights-m06 | 243 | [232, 254] | M(2) at 16k (the seed-3,000,000 sample scored 234, with about 54 cap hits); a 32k cap lets about 20% of those cut answers finish right, as Think-SFT's did (23 of 93). |
| round-09/problems-m05 | 242 | [230, 254] | Theory: imitation's plans are long and unfinished at 16k; M(2)'s about 54 cut answers convert at Think-SFT's 25% rate when given 32k, adding about 10 to 234. |
| round-10/stopping-m03 | 241 | [229, 253] | M(2)'s remaining cut answers finish at 32k with about 20 % right. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | 242 | [230, 254] | M(2)'s remaining ~54 cut answers finish under the doubled cap, about a fifth of them right. |
| round-10/weights-m03 | 242 | [230, 254] | On this host M(2) still leaves about 54 cut answers that are unfinished work; about a fifth of them finish right at 32k. |
| round-10/weights-m05 | 241.5 | [229, 254] | Doubling the cap finishes a fifth of the remaining cut answers right. |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 242 | [230, 254] | Cut M(2) traces on competition problems are routine work; 32k finishes some right. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 241 | [229, 253] | 32k extends reach on cut problems; about +10. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 241 | [230, 251] | Late finishes only on reachable items. |

## t29 (work-290625): How many of the 500 MATH-500 problems does the base plus 2x the top-8 RL-Math weight-change directions answer correctly with the cue, one sample at T 1.0, grader v3?

Unit: right answers of 500. Cell: {"model": "Olmo-3-1025-7B base + top-8 RL-Math directions at 2x (cell m29)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, seed 3000000; top-p and token cap not stated", "samples": 1, "grader": "v3"}

> Cell m29: base + top-8 RL-Math directions at 2x, cue, MATH-500 n 500, T 1.0, v3

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 447 | [434, 459] | 1.5x gives 456 on MATH-500; on hard328, 2x fell from 203 to 190 as precision dropped, and the effect is smaller on easy problems. |
| reader-2 | 448 | [435, 460] | 1.5x gives 456 on MATH-500; on hard328 2x was 13 below 1.5x but MATH-500 has few long problems, so a few points lower. |
| run-06/f2-m03 | 446 | [435, 457] | Theory: 2x commits too early, so it falls a little below 1.5x's 456 on MATH-500 (hard328: 190 vs 203). |
| run-05/f2-m03 | 449 | [437, 461] | An in-domain edit works in full on any math set, so MATH-500 follows the hard328 dial shape (2x a little below 1.5x: 190 vs 203) applied to MATH-500's 1.5x cell of 456. |
| run-05/f2-m01 | 452 | [442, 461] | Past 1.5x the dial closes unfinished answers on guesses, but MATH-500 has few unfinished, so 2x stays near the 1.5x cell's 456, slightly lower. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 447 | [434, 460] | Theory: 1.5x top-8 already matches RL's own share (456), and since effective size grows faster than nominal, 2x overshoots (hard328 203 -> 190); MATH-500 is easier, so the drop is smaller, giving ~447. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 448 | [436, 460] | Theory: past about 1.5x the hazard closes hard problems with guesses; on MATH-500, with few cap hits, 2x falls slightly below the 1.5x cell's 456. |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | 448 | [435, 460] | A larger finishing push beyond 1.5x cuts derivations short (hard328 203 to 190 from 1.5x to 2x); MATH-500 is easier, so a smaller drop from 1.5x's 456. |
| run-02/f2-m04 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 449 | [438, 459] | Paired with the 1.5x cell (456); on hard328 the 2x size lost ~4 points against 1.5x; MATH-500 SD 5-6. |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | 448 | [436, 460] | At 2x the dose pushes MATH-500's few cap hits to near zero while precision falls (right of finished 0.65 -> 0.59 on hard328), so it lands slightly below the 1.5x cell's 456. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/training-m05 | 447 | [434, 458] | Theory: eight directions are the finishing dial; at 2x cap hits are nearly gone and precision drops (hard328 2x 190 vs 1.5x 203), but MATH-500 has few cap hits, so 2x lands a little under the 1.5x cell's 456. |
| round-09/sampling-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 447 | [435, 458] | Theory: hazard grows with edit size; 2x loses some answers relative to 1.5x (hard328 203 -> 190, code 399 -> 394), applied to the 1.5x MATH-500 456. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 450 | [440, 459] | Pooling clause: the 2x cell sits near the 1.5x MATH-500 level (456, one draw) and slightly lower, as 2x was below 1.5x on the 328 (190 vs a pooled 200); about +-7 per 500 of seed scatter. |
| round-09/sampling-m06 | - |  | theory says nothing |
| round-09/weights-m01 | 448 | [438, 458] | Theory: 2x over-commits on long problems (on hard328, 2x gave 190 vs 203 at 1.5x). MATH-500 is mostly short, so the cost against the 1.5x cell's 456 is small. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | 450 | [438, 462] | The 2x edit acts as a true 2x (same written norm as the stored hard328 edit): on hard328 2x fell 13 below 1.5x, and on easier MATH-500 a smaller drop from 1.5x's 456 is expected. |
| round-09/problems-m05 | 450 | [438, 461] | Theory: the directions add finishing, so on MATH-500 they track RL (1.5x: 456); a larger dose adds no plans and turns into guessed boxes (hard328 2x: 203 to 190). |
| round-10/stopping-m03 | - |  | no forecast |
| round-10/stopping-m04 | 449 | [437, 459] | At 2x every MATH-500 answer commits (about 22 base cap hits to convert), and the commit at points that are not quite ready costs a few points against 1.5x's 456. |
| round-10/weights-m01 | 452 | [442, 461] | At 2x MATH-500's roughly 20 cap hits all finish; the precision loss grows with the wrong share (44 of 500 at 1.5x, +12 % as on hard328's finished problems), so about 451. |
| round-10/weights-m03 | 448 | [436, 459] | On the base host the push has its full effect, so 2x overshoots a little. |
| round-10/weights-m05 | 448 | [436, 459] | 2x of the shared readout overdoses finishing a little. |
| round-10/weights-m06 | 446 | [434, 457] | At 2x direction 1 begins to unbox a few answers, and finishing at 2x costs a little precision. |
| round-10/training-m05 | - |  | no forecast |
| round-10/problems-m03 | 449 | [438, 459] | Answer statement already saturated at 1.5x on MATH-500; 2x adds only over-dose cost. |
| round-10/problems-m04 | 450 | [440, 459] | 2x vs 1.5x on hard328 lost 13, part in the tail that MATH-500 lacks: about -6 from 456. |
| round-10/problems-m05 | - |  | no forecast |
| round-10/problems-m06 | 449 | [438, 459] | Math-calibrated 2x closes long MATH-500 problems early; few such problems. |
| round-10/grader-m06 | - |  | no forecast |

## t30 (work-dc9359): How many of the 328 harder problems does Think-SFT with the cue get right under a majority vote over 4 samples generated with a 32,768-token cap and scored at that cap?

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "token cap 32,768; temperature and top-p not stated", "samples": 4, "grader": "not stated, majority vote over 4 samples"}

> Think-SFT + cue vote over 4 at token cap 32,768 on hard328

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 246 | [236, 257] | Vote at 16k is 241 and a single sample at 32k is 230; the owner's simulation says 240 [232, 248] unless late wrong answers disagree. |
| reader-2 | 247 | [237, 258] | The offline simulation says 240 [232, 248] or 254 if late wrong answers disagree; the 16k vote is 241 and the 32k singles are about 230. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | 246 | [236, 256] | Theory: hard328 solutions need at most about 14,000 tokens, so the 32,768 cap adds only a little to Think-SFT's 16,384 vote over 4 of 241 (result-818c20). |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | 244 | [236, 252] | At 32k singles rise to about 230, but the finished former abstentions are mostly wrong and scattered and tie or outvote lone right samples, so the vote gain shrinks and the vote stays near the 16k vote of 241. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 247 | [237, 257] | The 16k vote is 241 and its pass@4 244; at 32k the cut answers finish, about a quarter of them right, so the vote rises toward a higher pass@4; between the job's simulation (240) and its 254 case. |
| round-09/grader-m04 | 246 | [236, 256] | With the 32k cap the singles rise to ~230 and few samples abstain, so the vote gains less per sample than at 16k; the count stays a little above the 16k vote's 241. |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | 244 | [234, 254] | Survival: at 32,768 tokens nearly all of Think-SFT's 29% cap hits finish, about 25% of them right (+7 points per sample, result-c8b994), so the vote rises a little above 241. |
| round-09/grader-m06 | 244 | [233, 254] | Theory: each Think-SFT sample gains about 23 at 32k, but only a quarter of late finishes are right, so the vote, already near pass@4 at 16k (241 of 244), adds little: about +3. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | 248 | [238, 258] | Theory: each Think-SFT sample gains ~7 points from finished cut answers at ~25 % right; the vote over 4 (241 at 16k, already near pass@4) gains less, about +7, mainly where all 4 samples were cut. |
| run-03/f2-m05 | 245 | [235, 256] | Late degeneration limits what the 32k cap adds (switched cut answers 1 of 24 right); 16k vote 241 plus a modest gain, near the simulation's 240. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 244 | [235, 253] | Pooling clause: the vote regresses to the level of the near-identical 16k vote (241) plus a small gain, since the cap-32k singles (sample 0 = 230, the others regressing lower) now finish the answers that were cut. |
| round-09/sampling-m06 | 247 | [238, 256] | At cap 32,768 Think-SFT's cut answers finish, 23 of 93 right and the rest wrong values that now take part in the vote, so the vote sits only a little above the 16k vote's near-pass@4 241; the near-zero block on hard328 caps it near the larger pass@4. |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | 246 | [237, 255] | Theory: samples 1-3 land around the cap-32k arm mean (about 230, matching sample 0). The vote adds less over the singles than at 16k (241 vs 209) because cap hits no longer abstain, so the result sits a little above the 16k vote. |
| round-09/stopping-m04 | 246 | [237, 254] | At 32k Think-SFT's cut answers finish (23 of 93 right per sample, theory: cut answers are the only loss), which adds problems the 16k vote (241) never reached, partly offset by wrong long votes. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | 250 | [240, 260] | Theory: Think-SFT's cut answers hold real plans (high precision when finished), so the 32k budget lifts the vote over the 16k vote of 241, which was near pass@4. |
| round-10/stopping-m03 | 245 | [236, 254] | Raw template with the cue: no boundary, so the cap-32k effect is the one measured on single samples, partly passed through the vote. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | 247 | [237, 257] | Think-SFT lacks the stop push, so its cut answers are unfinished work that the 32k cap completes, a few more votes. |
| round-10/weights-m03 | 247 | [237, 257] | Think-SFT has no finishing push, so its cut answers are unfinished; 32k adds a few votes. |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 248 | [238, 258] | Long competition routines finished at 32k add right answers that join the vote. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 245 | [236, 255] | Think-SFT's pass@4 rises about 8 at 32k; the vote follows part of it. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 246 | [238, 253] | Vote sits at pass@4; 32k raises pass@4 only on reachable cut items, about +5. |

## t31 (work-dc9359): How many of the 328 harder problems does Think-SFT with the cue get right under a majority vote over 4 samples generated at a 32,768-token cap but scored as if cut at 16,384 tokens?

Unit: right answers of 328. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "generated at token cap 32,768, scored at 16,384 from the same text; temperature and top-p not stated", "samples": 4, "grader": "not stated, majority vote over 4 samples"}

> each answer scored at 16,384 and 32,768 from the same text

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 240 | [232, 248] | Should reproduce the stored 16k vote of 241 with fresh samples. |
| reader-2 | 240 | [231, 249] | The same as the stored 16k vote over 4 (241) on new samples. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | 240 | [231, 249] | Theory: scored at 16,384 the vote matches the stored cap-16,384 vote over 4 (241), because hard328 solutions take 6,000-14,000 tokens. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | 240 | [233, 247] | Cut at 16k the capped samples abstain, so the vote is again near pass@4, which reproduces the stored 16k vote of 241 (result-818c20); the 207 single in this run puts it slightly lower. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | 241 | [233, 249] | Theory: seed adds nothing systematic, and answers cut at 16,384 are equivalent to a cap-16,384 run, so the new 4-vote equals the stored Think-SFT cue 4-vote (241) within a run-to-run spread of about 5. |
| run-08/f2-m01 | 241 | [232, 250] | Scoring at 16,384 reproduces the stored 16k vote cell (241), with new-seed draw noise. |
| round-09/grader-m04 | 240 | [231, 249] | Scored at 16,384, the answers past 16k count as abstentions again, which reproduces the stored 16k vote over 4 (241) within sample noise. |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | 240 | [230, 249] | Theory: scoring at 16,384 reproduces a 16k run, so this is the stored 16k vote over 4 (241), allowing for a seed draw. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | 240 | [231, 249] | Scored at 16,384 the cut tail is not counted, so this is the stored 16k vote over 4 (241) for new seeds. |
| run-03/f2-m05 | 239 | [229, 249] | Scoring at 16,384 cuts the late part; equals the stored 16k vote level (241) with fresh samples. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 239 | [231, 247] | Pooling clause: scored at 16,384 this is a near-identical cell to the stored vote over 4 (241), and new seeds regress to it; sample 0 at 16k was 207, against the stored mean of 209. |
| round-09/sampling-m06 | 240 | [233, 247] | Scored at 16,384 this is the stored Think-SFT vote setting (241 of 328, near its pass@4 of 244 because cap hits abstain); the near-zero block caps it, and new seeds move it by a few problems. |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | 241 | [233, 249] | Theory: answers scored at 16,384 are new draws from the same Think-SFT cue arm whose stored 16k vote over 4 is 241, so the vote lands around 241 with a few problems of noise. |
| round-09/stopping-m04 | 239 | [231, 247] | Scored at 16k, cut answers score zero, and new seeds move only precision (theory), so the vote equals the stored 16k vote of 241, a bit lower because sample 0 scores 207 at 16k. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | 239 | [230, 248] | Theory: scored at 16k, the plans that need length are cut again, so the vote matches the stored 16k vote (241) with new-sample noise. |
| round-10/stopping-m03 | 239 | [230, 248] | The 16k vote level on new raw-template samples. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | 240 | [232, 248] | New samples reproduce the stored 16k vote. |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 240 | [231, 249] | Reproduction of the stored 16k vote. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | - |  | no forecast |
| round-10/problems-m05 | 240 | [232, 248] | Same reach, same cap: 241. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 240 | [233, 247] | 16k vote at the same pass@4 ceiling. |

## t32 (work-dc9359): How many of the 136 fresh 2026 contest problems does Think-SFT with the cue get right under a majority vote over 4 samples generated with a 32,768-token cap and scored at that cap?

Unit: right answers of 136. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "token cap 32,768; temperature and top-p not stated", "samples": 4, "grader": "not stated, majority vote over 4 samples"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768 from the same text

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 82 | [73, 91] | 16k vote is 75 with 46% cap hits; 32k finishes many of them and some are right, as with Think-SFT's +23 on hard328. |
| reader-2 | 82 | [72, 92] | 16k vote 75 with 46 % cap hits; the 32k cap finishes many of them at about 20 % right, a few more votes. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | 78 | [70, 86] | At 32k many of the ~46 % capped fresh samples finish, so singles rise from 60, but the theory says the new answers are mostly wrong and dilute the vote, so it gains only a little over the 16k vote of 75 (result-5251c9). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| run-08/f2-m01 | 80 | [73, 87] | The stored 16k vote is 75 of 136, with 46% cap hits; the 32k cap finishes part of them, adding ~5 under the vote; fresh2026 SD ~3. |
| round-09/grader-m04 | 80 | [72, 88] | Theory: fresh2026 is harder, so long answers there are more often guessed. The 32k cap and the vote yield less per abstention than on hard328, adding only ~5 to the 16k vote's 75. |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | 80 | [72, 88] | Survival: Think-SFT's 46% cap hits on fresh2026 mostly finish by 32,768 tokens, converting at low precision (about 20%), so per-sample right rises by about 10 and the vote rises from 75 to about 80. |
| round-09/grader-m06 | 81 | [72, 90] | Theory: fresh2026 Think-SFT hits the cap on about 62 of 136 per sample, so a quarter of those (about +15 per sample) finish right; the vote adds about 6 over its 16k 75. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | 85 | [76, 94] | Theory: Think-SFT cuts ~46 % of fresh2026 samples (~62 per sample); finishing them at ~25 % right adds ~15 per sample, so the vote rises from 75 to about 85. |
| run-03/f2-m05 | 80 | [72, 88] | Fresh2026 has many cap hits (46%) but late traces often switch script and fail, so the 32k gain over the 16k vote (75) is modest. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 80 | [72, 88] | Pooling clause: anchored on the near-identical 16k fresh vote (75), plus the cap-32k gain from finishing cut answers, since cap hits are 46 % here. |
| round-09/sampling-m06 | 81 | [74, 88] | fresh2026 vote at 16k is 75 from a single-sample mean of 60. The longer cap finishes many of the 46% of samples that hit it, but the theory's near-zero block on a hard set and the wrong values that are as likely as the right one limit the vote to about +6. |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | 82 | [73, 91] | Theory: new draws around the arm mean (fresh 16k singles 60, vote 75). Raising the cap converts some of the roughly 45% cap-hit samples to answers (about a quarter right, per the board's cap32 rate), lifting the vote by about 7. |
| round-09/stopping-m04 | 82 | [73, 90] | Think-SFT cuts 46% of fresh2026 samples at 16k; at 32k those finish and roughly a fifth are right, so the vote rises above the 16k vote of 75. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | 87 | [77, 97] | Theory: fresh2026 contest problems are plan-limited and Think-SFT's 46% cap hits are unfinished plans with about 80% precision when finished; 32k converts about 25% of them, lifting the vote from 75. |
| round-10/stopping-m03 | 81 | [72, 90] | Raw template on fresh2026: cut answers are run-on work that finishes at 32k; the vote rises a few points. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | 82 | [73, 91] | Same logic on fresh2026 with 46 % cap hits. |
| round-10/weights-m03 | 82 | [73, 91] | The same on fresh2026. |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 84 | [75, 93] | 2026 contests are exactly the covered problem type, and 46 % of samples are cut routines; at 32k they finish and the vote gains about 9. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | 82 | [74, 91] | fresh2026 is mostly tail stratum, so a cap change moves it more per problem than hard328. |
| round-10/problems-m05 | 82 | [74, 91] | 32k raises Think-SFT's fresh reach; vote follows. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 81 | [74, 87] | Fresh ceiling is limited by transcription defects; +6 from finished cuts. |

## t33 (work-dc9359): How many of the 136 fresh 2026 contest problems does Think-SFT with the cue get right under a majority vote over 4 samples generated at a 32,768-token cap but scored as if cut at 16,384 tokens?

Unit: right answers of 136. Cell: {"model": "Olmo-3-7B-Think-SFT", "prompt": "cue", "set": "fresh2026", "n": 136, "sampling": "generated at token cap 32,768, scored at 16,384 from the same text; temperature and top-p not stated", "samples": 4, "grader": "not stated, majority vote over 4 samples"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768 from the same text

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 75 | [68, 82] | Should reproduce the stored 16k vote of 75 of 136 with new samples. |
| reader-2 | 74 | [66, 82] | Should reproduce the stored 16k vote over 4 of 75 on new samples. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| run-02/f2-m04 | 75 | [69, 81] | Scored at 16k the caps abstain again, reproducing the stored 16k Think-SFT vote over 4 of 75 of 136 (result-5251c9). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | 75 | [69, 81] | Theory: new seeds scored at the 16,384 cut are fresh Bernoulli draws of the same cell, so the 4-vote reproduces the stored fresh2026 Think-SFT cue vote of 75, with a spread of about 4 on 136 problems. |
| run-08/f2-m01 | 75 | [69, 81] | Same text scored at 16,384 reproduces the stored vote of 75, with fresh2026 draw SD ~3. |
| round-09/grader-m04 | 75 | [68, 82] | Scoring at 16,384 removes the cap-raise gain, which leaves the stored Think-SFT fresh2026 16k vote over 4 (75, result-5251c9). |
| round-09/grader-m03 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/grader-m06 | 75 | [68, 82] | Theory: the 16k score from 32k text equals a 16k run, the stored fresh2026 Think-SFT vote over 4 at 16,384 (75). |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m05 | 75 | [68, 82] | At 16,384 the cut tail stays unfinished, so this is the stored Think-SFT cue vote over 4 on fresh2026 (75 of 136). |
| run-03/f2-m05 | 74 | [67, 81] | Scored at 16,384 it matches the stored 16k vote of 75 with new samples. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m01 | 75 | [68, 82] | Pooling clause: scored at 16,384 this is a near-identical cell to the stored fresh2026 Think-SFT vote over 4 (75), and new seeds regress to it, with scatter of about 5 per 136. |
| round-09/sampling-m06 | 75 | [69, 81] | Scored at 16,384 this repeats the stored fresh2026 Think-SFT vote cell (75 of 136); the vote is capped by the near-zero block, and only sampling noise moves it. |
| round-09/weights-m01 | - |  | theory says nothing |
| round-09/sampling-m01 | 75 | [68, 82] | Theory: scored at 16,384 these are new draws from the same fresh2026 Think-SFT cue arm whose stored vote over 4 is 75, so the count lands around 75 with sd about 4 on 136. |
| round-09/stopping-m04 | 74 | [67, 81] | Scored at 16k with cut answers zero, and new seeds move only precision (theory), so this reproduces the stored 16k fresh2026 vote of 75. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/problems-m05 | 74 | [66, 82] | Theory: at 16k the long plans are cut again, so the vote equals the stored fresh2026 16k vote (75). |
| round-10/stopping-m03 | 75 | [67, 83] | The 16k vote is reproduced. |
| round-10/stopping-m04 | - |  | no forecast |
| round-10/weights-m01 | - |  | no forecast |
| round-10/weights-m03 | 75 | [67, 82] | Reproduces the 16k vote of 75. |
| round-10/weights-m05 | - |  | no forecast |
| round-10/weights-m06 | - |  | no forecast |
| round-10/training-m05 | 74 | [66, 82] | Reproduction of the stored 75. |
| round-10/problems-m03 | - |  | no forecast |
| round-10/problems-m04 | 75 | [68, 82] | Same strata, same cap: stored vote. |
| round-10/problems-m05 | 75 | [68, 82] | Unchanged reach at 16k. |
| round-10/problems-m06 | - |  | no forecast |
| round-10/grader-m06 | 74.5 | [68, 81] | Same fresh ceiling at 16k. |
