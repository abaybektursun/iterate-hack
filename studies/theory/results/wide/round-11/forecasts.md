# Forecasts, round-11

Board snapshot 2026-11-15T20:05:26 UTC, written 2026-11-15T20:19:32 UTC. 28 targets; forecasters reader-1, reader-2, run-06/f2-m03, run-05/f2-m01, run-05/f2-m03, run-02/f2-m01, run-05/f2-m06, run-07/f2-m02, run-03/f2-m02, round-09/training-m06, run-02/f2-m04, run-05/f2-m04, round-09/weights-m06, round-09/sampling-m03, round-09/training-m04, run-04/f2-m04, round-09/grader-m04, round-09/grader-m01, round-09/grader-m06, round-09/stopping-m01, round-09/training-m05, round-09/sampling-m06, run-08/f2-m01, round-09/sampling-m05, round-09/stopping-m04, round-09/grader-m02, round-09/training-m03, round-09/grader-m05, run-03/f2-m05, run-04/f2-m03, round-09/weights-m04, round-09/sampling-m01, round-09/training-m01, round-09/training-m02, round-11/s2-b, round-11/s4-b, round-11/s6-b.


- run-06/f2-m03 (training, carried): An outcome reward pays only for a gradable final answer, so its consistent gradient piles into a few singular directions that make the model complete the task in the rewarded form (boxed answer, final code block) before the cap; the rest of the update is diffuse. In-domain, the top-8 directions at 1.5x reproduce nearly all of RL's gain over the cued base. Another reward's directions give about half, random rank-8 gives nothing, and 2x commits too early.

- run-05/f2-m01 (weights, carried): The top-8 singular directions per matrix of the RL change act as a signed termination dial spread over all layers and both module families: adding them at size s raises, monotonically in s, the chance an answer closes with a boxed result before the cap (negative s lengthens and unboxes), and modestly raises correctness on problems already finished; past 1.5x it closes unfinished hard solutions on guesses. Random rank-8 edits and Think-SFT's directions carry no dial.

- run-05/f2-m03 (weights, carried): Each direction of an RL change acts only as far as the processed text drives its input (right) singular vectors: Math-RL's top-8 input subspaces are excited 8-11x above random by math-solution text and Code-RL's 6-9x, so an edit works in full on any problem set of its own domain and transfers to another domain in proportion to input-subspace overlap (Math with Code about 0.22-0.26, giving roughly half the in-domain effect).

- run-02/f2-m01 (run-02, carried): The autobench agent works under a fixed generation time per experiment, so it buys votes by shortening each sample (its best config: 10 samples at about 1,100 tokens each). Most MATH-500 problems are solved in under 2,000 tokens, so short samples plus a vote score well on dev100, but hard328 solutions need 6,000-14,000 tokens and short samples never reach them. For the base, each doubling of the token budget past 8,000 buys fewer problems.

- run-05/f2-m06 (weights, carried): Weight edits merged in bf16 are realized only where an entry's change exceeds half a unit in the last place of that weight, so small edits are thresholded onto small-magnitude weights and their effective size grows faster than nominal size (a=0.25 acts like about 0.12; top-8 at nominal 1.5 acts like RL's own top-8 share). Smaller deltas such as Code-RL's lose more at 1x and peak at a larger nominal size; trained checkpoints carry no such loss.

- run-07/f2-m02 (problems, carried): An RL run's top weight directions write a habit for its own domain's answers. For Math-RL that habit is to deliberate, check, and finish with one boxed answer; for Code-RL it is to reason, then finish with one final python block that passes the tests. In its own domain the top-8 edit carries about two thirds of RL's gain at 1x and nearly all of it at 1.5x. On another domain it carries about half as much.

- run-03/f2-m02 (stopping, carried): RL's top singular weight directions raise the model's per-token hazard of committing to an answer and ending, in proportion to their size. In-domain directions therefore turn unfinished answers into finished ones and lengthen premature short ones. Overall right-of-finished stays roughly flat, because fixes on problems already finished offset guesses on converted cap hits. Past about 1.5x the hazard closes hard problems with guesses. The full RL delta added to Think-SFT acts the same way.

- round-09/training-m06 (training, carried): The RL update is written onto features that pretraining placed in the early and middle layers: the input directions of RL-Math's top-8 change are the ones math text drives most, and most of RL's change in model output comes from layers 0-15. Adding the directions only in the first or middle third therefore gives more of the hard-problem gain than the last third, whose main distinct job, writing the opening cue, is redundant when the cue is prefilled.

- run-02/f2-m04 (run-02, carried): A capped sample gives no answer, so in a plurality vote it abstains instead of adding a wrong value. Think-SFT's vote sits near its pass@4 because its unsolved samples run to the cap rather than box a guess. Anything that makes it finish, a 32k cap or the RL difference, turns abstentions into mostly wrong, scattered answers that tie or outvote lone right samples: single scores rise, vote gains shrink.

- run-05/f2-m04 (weights, carried): RL writes its weight change in stages: the first 100 steps move weights along the reasoning-register directions that the cue's opening also drives (step-100 change about 0.03% of weight norm, activations nearly unchanged), giving the cue's gain plus a little precision; the finishing directions and the dense error-reducing remainder accumulate between steps 400 and 2,800. So a cue on an early checkpoint is redundant, and anything built from the final weights carries the late parts.

- round-09/weights-m06 (weights, carried): Edit entries smaller than half a bf16 ulp of the weight they modify are written by stochastic rounding (written/intended cosine 0.585). The written edit is unbiased: the intended direction comes through at full nominal size, and the rounding residue is a random edit, which is inert like the random rank-8 and noise controls. Scores therefore follow the nominal dose. The residue and GPU-dependent rounding draws add sample-to-sample spread, but they do not shift the mean.

- round-09/sampling-m03 (sampling, carried): Temperature sets how often a plain prompt opens in the deliberative 'Okay' register. At T 0.6 the first tokens collapse onto the modal opening (step 100: 478 of 500); at T 1.0 a share 1-q starts elsewhere (step 100: 117 of 500; base: about 400). A prefilled cue or fixed template removes that branch, so the cue's worth at T 1.0 is (1-q) times the gap between openings, which widens on harder problems.

- round-09/training-m04 (training, carried): Pretraining fixed, for each problem, the base's distribution over final values; the cue picks which register samples it but does not move its modal value. A vote converges to that mode, so its ceiling is the problems whose modal value is right, and samples beyond about eight only resolve ties. The plain prompt samples pretraining's terse solution register, whose accuracy falls faster with difficulty than the cued register's, so plain's share of the cued score shrinks on harder sets.

- run-04/f2-m04 (sampling, carried): A T 1.0 run is a set of independent per-problem Bernoulli draws: the run-to-run spread of a count is sqrt(sum p(1-p)), about 5-6 problems on MATH-500 and 6 on hard328 for these models, and the seed adds nothing systematic. A stored first sample is one such draw, so a 4-sample mean is 1/4 that draw plus 3/4 the model's mean, and adding one sample to a vote moves only the few problems it can flip.

- round-09/grader-m04 (grader, carried): A count's size depends on the set's difficulty mix: hard328's first 164 problems are much harder than its second half (cued base 65 vs 99), and fresh2026 is harder still. On hard items the opening (cue, step 100, self-opening) moves few problems, while answers past 16k tokens are mostly unfinished or guessed, so cap raises and votes yield less per abstention than on hard328, and plain prompts keep a falling share of the cued count.

- round-09/grader-m01 (grader, carried): Each posted single cell is one seeded draw: new seeds on the same weights scatter by 5-7 problems per 500 and up to 9-19 per 328, and cells picked as notable (best size, first run) sit above their model's mean. Multi-sample means regress to the pooled level of near-identical cells: step-100 plain pools with step-100 cue (same opening policy), and the 164-problem references come from draws above their own 4-sample means.

- round-09/grader-m06 (grader, carried): A count at a token cap scores every unfinished answer wrong, hiding whether it was unfinished work or a dead end. Raising the cap adds right answers in proportion to the model's share of unfinished-work cap hits: Think-SFT about one in four, RL one in ten, the base one in sixteen. Scoring the 32k text at 16,384 reproduces a 16k run, so the 32k-minus-16k difference is that yield alone.

- round-09/stopping-m01 (stopping, carried): A cut-off sample writes no answer marker, so it abstains from the plurality vote instead of voting wrong. A vote's gain over one sample therefore scales with the cap-hit share times the precision of finished answers: Think-SFT (29-46 % capped, 80-88 % precise) votes near pass@4, while RL and the 1.5x edit (5-15 % capped) gain less. A longer cap turns abstentions into mostly wrong late answers, so a vote gains far less from it than one sample does.

- round-09/training-m05 (training, carried): The largest singular direction per matrix of RL-Math's change carries the reward's most consistent signal: write the final answer in the boxed form the verifier reads, which also ends some answers. Deciding to stop deliberating on long problems is spread over the next directions. One direction therefore cuts cap hits only partly, and scaling it mostly changes answer form, not stopping: top-1 at 2x gains little over top-1 at 1x, while eight directions together act as the finishing dial.

- round-09/sampling-m06 (sampling, carried): Problems differ in solve rate far beyond binomial noise. Each arm has a block of problems it almost never samples right (base: 33 at 0 of 4 on MATH-500, against 0.5 expected) and a block where a wrong value is as likely as the right one. A vote wins only problems where the right answer is the most likely one, so it plateaus a few samples past 4, and the near-zero block caps votes on hard sets.

- run-08/f2-m01 (grader, carried): Each one-sample count is one seed's draw: the model branches at forks with fixed per-problem probabilities, so a cell has a sampling SD of about 5-6 problems on MATH-500, 7-9 on hard328 and 3 on fresh2026, plus small runner drift. A stored sample 0 is an unselected draw, so a 4-sample mean is that value shrunk slightly toward the cell's structural prior (neighbouring checkpoints, cue effect).

- round-09/sampling-m05 (sampling, carried): Ending is a sampled event: at T 1.0 the stop token is drawn at each point where an answer could close, so lengths have a long tail that the cap cuts off. Raising the cap finishes the cut samples, right at the rate of that model's long finished answers at the same difficulty: high for Think-SFT, whose cut answers are unfinished work, low for the base and RL, whose long answers mostly guess.

- round-09/stopping-m04 (stopping, carried): On a hard set part of every model's answers would end past 16,384 tokens, and a cut answer scores zero. A change that leaves the length distribution in place (100 RL steps, the cue on a checkpoint, a new seed or more samples) can move only the precision of finished answers. Step 100 writes cued-base lengths at T 1.0 (4,120 vs 4,008 tokens), so on hard problems it keeps the cued base's cap hits and adds a few right answers.

- round-09/grader-m02 (grader, carried): Under a plurality vote a cap hit or missing answer is an abstention, while a finished wrong answer is a vote against. A model's vote gain over its singles is set by how often it abstains instead of answering wrong: Think-SFT's vote nearly equals pass@4, while RL's and the edits' lose more. Raising the cap or adding finishing weight turns abstentions into mostly wrong finished answers, so singles rise while vote gains shrink.

- round-09/training-m03 (training, carried): RL-Zero's group-relative reward gives gradient only on prompts where some rollouts succeed and others fail, so early RL moves the policy on problems the base solves sometimes, mostly short and medium ones, and leaves problems the base rarely solves for late training. By step 100 the gain sits on MATH-500's mid-difficulty problems; on hard problems, where the cued base mostly fails or runs to the cap, step 100 plain is no better than the cued base.

- round-09/grader-m05 (grader, carried): Plurality votes break ties toward the lowest sample index, so at even k a 2-2 or 1-1-1-1 split is decided by sample order, not by the answers. Odd k dissolves 2-2 ties, and going from 9 to 12 samples brings them back, so the base's MATH-500 vote plateaus near 453. When abstentions become finished wrong singletons (32k cap), lone right answers end up tied and lose about half the time.

- run-03/f2-m05 (stopping, carried): A trace can degenerate before it ends, into word strings, a switch to Chinese script or repeated windows, and a degenerate trace almost never ends right. The hazard of this grows with edit size (word strings at 2-3x) and with tokens already generated (median first script switch near token 13,600). So oversized edits, and the late part of very long Think-SFT traces, lose answers. A smaller edit or a shorter trace keeps them. At T 1.0 classic loops are absent.

- run-04/f2-m03 (sampling, carried): Under T 1.0 stopping is a sampled event: at each position the model draws a commit/stop token with a small hazard, so the cap-hit share is a survival probability. RL's top-8 directions add a near-constant logit to that hazard (cap hits 96, 77, 46, 25, 5 along the dial); dose multiplies it. Where the base fails by not stopping (short code tasks, fresh contests) the dial converts unfinished samples, at precision below the base's finished answers.

- round-09/weights-m04 (weights, carried): Moved onto another model that shares the base, the RL-Math difference acts as a finishing operator on that model's own trajectories. It does not add correctness. On Think-SFT it closes long, unfinished but sound work earlier, so cap hits fall and right-of-finished drops toward RL's level. The gain is limited by how much of the recipient's cut work was sound. Prompt or template changes on Think-SFT alone (no delta) leave its finishing rate and precision unchanged.

- round-09/sampling-m01 (sampling, carried): Each sample is an independent draw: problem i is solved with a fixed probability p_i, so one cell's count varies by sqrt(sum p_i(1-p_i)), about 5-7 problems on MATH-500 and 6-9 on the 328, and same-seed reruns give new texts because vLLM is not batch-invariant. A stored single cell is one draw. New samples land around the arm's mean, not around the stored count, and a gap of a few problems between single cells is noise.

- round-09/training-m01 (training, carried): Think-SFT imitated teacher traces inside its ChatML template, opened by <think> and closed by a final answer after the thinking block. Where and how it states the answer is learned conditional on that template. On the raw template with the cue it reasons as well but sometimes misplaces the final answer (on the line after 'Answer:'), which v3 misses. Its own template restores the trained ending: more MATH-500 answers counted, unchanged reasoning length and cap behaviour on hard328.

- round-09/training-m02 (training, carried): Think-SFT copied teacher traces produced under long budgets, and imitation carries no pressure to stop, so its 16,384-token cuts are mid-derivation work, not loops or guesses. More budget turns cut answers right at the problem's difficulty rate (about a quarter on hard328, fewer on 2026 problems). Late finishes are mostly wrong but scattered, so in a vote they seldom beat an existing right answer and add less than to single samples. RL's delta adds stopping, leaving fewer cuts to convert.

- round-11/s2-b (s2): An RL run's task-specific policy lies almost entirely in the top-8 directions per matrix of that run's own delta, read through the inputs of its own task. So 1.5x of RL-Code's directions is a copy of RL-Code, and RL deltas for different tasks occupy nearly orthogonal subspaces that add without interference. Other rewards' directions transfer only a shared finishing part (cap hits, missing answer blocks), not task skill.

- round-11/s4-b (s4): Besides finishing, the top RL directions sharpen the base toward its own most likely correct solution on problems it already solves in some samples. HumanEval+ and MBPP+ consist almost entirely of such problems (high base pass@k), so at 1x most of the code gap closes through reliability on finished answers, not through cap hits. Gains from Math and Code directions add on code, and the effect needs base capability rather than a short answer length.

- round-11/s6-b (s6): Overdose costs accuracy only where the edit pushes a quantity that trades against correctness past its RL optimum. Math directions carry a math-specific stop-checking push whose optimum is near 1.5x on any math set, short or long; beyond it, checking that would catch errors is skipped. Code directions push code-block format and termination, which saturate (no-code and cap hits reach 0) and do not trade against a program's correctness, because tests, not self-checks, decide passing. So code plateaus at 2x.

## t01 (work-ef61c7): How many of the 500 MATH-500 problems does the base model plus 0.125 times the RL-Math 3.1 weight difference answer right with the plain prompt, one sample at T 1.0, grader v3 (both shards joined)?

Unit: right answers of 500. Cell: {"model": "base Olmo-3-1025-7B + 0.125 x (RL-Math 3.1 - base) (cell m18)", "prompt": "plain", "set": "MATH-500", "n": 500, "sampling": "T 1.0, top-p not stated, token cap not stated", "samples": 1, "grader": "v3"}

> (m18) base + 0.125x (RL-Math 3.1 - base), plain, MATH-500 n 500

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 310 | [297, 322] | Shard 0 scored 153/250 and the cut-off shard 1 had 156 at 247 rows; the full rerun of shard 1 is a new sample, so expect about 155 more. |
| reader-2 | 309 | [297, 321] | Shard 0 scored 153/250 and the cut-off shard 1 had 156 of 247 rows; a clean rerun of shard 1 should land near 150-158. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 309 | [297, 321] | The dial is monotone in size, so 0.125x of the RL change (which contains the top-8 directions) sits part way between plain base 224 and theta0.25 plain 405; shard 0's 153/250 plus about 156 on shard 1 fixes the level. |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 309 | [299, 319] | The theory says bf16 thresholding shrinks small edits: a=0.25 acts like about 0.12, so a=0.125 acts smaller still and lands well below a=0.25 plain (405) but far above plain base (224). This matches shard 0 (153/250) plus the rerun shard 1 (about 156). |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 310 | [298, 322] | Theory: a 0.125x full delta gives only a small rise in the hazard, so right-of-finished stays flat and the count follows the posted shards (153/250 + about 156/250 partial). |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | 309 | [296, 322] | Theory: anything built from the final weights carries the late parts, so even 0.125x of the RL difference lifts plain base well above 224 (theta0.25 plain 405 is the ceiling); the number comes from shard 0's 153/250 plus about 156 expected from the rerun of shard 1 (partial 156/247). |
| round-09/weights-m06 | 310 | [297, 323] | Theory: sub-ulp entries are stochastically rounded so the 0.125x edit acts at its full nominal 0.125 dose (not shrunk), placing it midway on the plain dose curve 224 -> 405 (a=0 -> 0.25), consistent with shard 0's 153/250 plus a rerun shard 1 near 156/250; rounding draws add only spread. |
| round-09/sampling-m03 | 310 | [299, 321] | Plain prompt at T 1.0 keeps the theory's non-'Okay' branch (share 1-q), so the score sits between base plain 224 and the cued/step-100 level (~410-418); the posted shards (153/250 even, 156 of 247 odd before rerun) place it near 310. |
| round-09/training-m04 | 310 | [299, 321] | Plain register part of the theory: a 0.125x edit leaves the pretrained plain (terse) register near base on the easy set, so the score follows the already-sampled plain shards (153/250 even half, about 156 on the odd half). |
| run-04/f2-m04 | 310 | [301, 319] | Theory: the shard-1 rerun is a fresh set of Bernoulli draws whose seed adds nothing systematic, so it centres on the cut run's rate (156/247, about 157 of 250); adding shard 0's 153 gives 310, and the spread is about 4 per 250-problem shard, applied once for the new draw and once for the uncertain mean. |
| round-09/grader-m04 | 310 | [298, 322] | Theory's plain-prompt clause: on the easiest set (MATH-500) a plain prompt keeps its largest share of the cued count, so the plain count stays high; anchored on shard 0 at 153/250 and the cut shard 1 at about 156/247. |
| round-09/grader-m01 | 310 | [299, 321] | Theory's seed scatter (5-7 per 500): shard 0 is already 153/250 and the cut shard 1 had 156 of 247, so the rerun of shard 1 lands near 157 +- a few, total about 310. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 310 | [302, 318] | Shard 0 is a fixed unselected draw (153/250); the theory treats the shard-1 rerun as a fresh seed draw centred on its cut-off partial (156 of 247, about 157/250), with an SD of about 4 for 250 problems. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | - |  | theory says nothing |
| round-09/training-m03 | 311 | [300, 321] | The theory says a small early RL move gains first on MATH-500's short and mid-difficulty problems that the base sometimes solves, so 0.125x of the RL-Math difference should lift plain MATH-500 well above the plain base; the size comes from shard 0's posted 153/250 plus the cut-off shard 1 (156 of 247 rows), about 311. |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 309 | [296, 322] | A 0.125x edit is far below the 2-3x size where the theory puts word strings, so no answers are lost to degeneration; the count is shard 0's 153 plus a rerun shard near its partial 156 of 247. |
| run-04/f2-m03 | 309 | [297, 321] | Dose multiplies the stopping hazard, so 0.125x shifts the stop logit by only an eighth of the 1x shift and cap hits stay near base (7 in shard 0); the count then follows the measured shard rate, 153/250 plus about 156/250 for the rerun shard. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | 310 | [298, 322] | Shard 0 is fixed at 153/250. The theory says a rerun lands around the arm's mean, not the stored count, so the rerun of shard 1 should land near the arm mean estimated from its cut-off draw (156/247, about 157/250). The spread is one new draw (sd about 5 on 250 problems) plus the error in that estimate. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t02 (work-441e5b): How many of the 328 hard problems does Think-SFT plus twice the RL-Math weight difference answer right with the cue, one sample with seed 3,100,000, scored at a 32,768-token cap?

Unit: right answers of 328. Cell: {"model": "M(2) = Think-SFT + 2 x (RL-Math - base)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T not stated, top-p not stated, token cap 32,768, seed 3,100,000 (sample-1 seed)", "samples": 1, "grader": "not stated"}

> M(2) = Think-SFT + 2x(RL-Math - base), cue, hard328, cap 32,768, ONE sample with sample-1 seed

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 241 | [229, 252] | M(2) scores about 229-237 at 16k with about 50 cap hits; Think-SFT's cut answers come out right about 25% of the time when given up to 32k, so add about 10. |
| reader-2 | 238 | [227, 249] | M(2) scores 233 on average at 16k with about 33-46 cap hits; Think-SFT gains about 22 at 32k, but M(2) already finishes most of those problems, so a smaller gain of about 5. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 240 | [228, 252] | The 2x dial carried in M(2) already closes most answers (cap hits about 50 at 16k), so the 32k cap adds fewer answers than it adds for Think-SFT (230-235), and the dial's modest gain on finished problems keeps M(2) a little above it. |
| run-05/f2-m03 | 241 | [230, 252] | Theory: the RL-Math change works in full on its own domain, so M(2) keeps its 16k effect (229 at this seed, cap hits ~75) and at 32k turns about a fifth of its remaining cap hits into right answers, as Think-SFT did (+23 of 93). |
| run-02/f2-m01 | 238 | [227, 249] | Theory: hard328 solutions need 6,000-14,000 tokens, so doubling the cap past 16,384 buys few problems for M(2), which already finishes most answers (about 44 cap hits); its 16k samples are 229-237, so add a few late finishes. |
| run-05/f2-m06 | 241 | [230, 252] | The theory says a large merge (a=2) is realized at its nominal size, so M(2) keeps its measured 16k level (about 233). The 32k cap adds roughly a quarter of its about 40 cap hits as right answers (Think-SFT converted 23 of 93). |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 236 | [227, 246] | Full delta on Think-SFT acts like the hazard: about 33-54 cap hits are left to finish past 16k, a few of them right, added to this seed's 16k score of 229. |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | 240 | [229, 251] | Theory: a 32k cap turns M(2)'s remaining capped samples into answers, so its single score rises above its 16k level (229-237, mean 233.3, ~54 cap hits). Most late answers are wrong, so the gain is about +7, well below Think-SFT's +22. |
| run-05/f2-m04 | 239 | [228, 250] | Theory: M(2) is built from the final weights and already carries the finishing directions (cap hits about 54 vs Think-SFT's 94), so the 32k cap adds less than Think-SFT's +23; that gives about 229 for this seed at 16k plus about 10. |
| round-09/weights-m06 | 239 | [228, 250] | Theory: the a=2 transplant keeps its nominal-dose mean regardless of GPU rounding draws (M(2) 16k mean 233.3, 234/229/237), plus a smaller cap-32k gain than Think-SFT's +23 because M(2) has ~54 rather than ~94 cap hits; different-GPU rounding draws widen the interval. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 241 | [229, 253] | Cap-raise clause: answers past 16k are mostly unfinished or guessed, so M(2)'s roughly 54 cap hits gain at a modest rate (about 15 %, below Think-SFT's 23 of 93), giving the 16k mean of 233 plus about 8. |
| round-09/grader-m01 | 243 | [231, 255] | Single seeded draws regress to the pooled level: M(2)'s 16k samples pool at 233.3 (229 for this seed was a low draw), plus the roughly 10 extra problems its 54 cap hits gain at 32k (Think-SFT turned about a quarter of its cut answers into right ones), with the theory's scatter of up to 9-19 per 328. |
| round-09/grader-m06 | 240 | [228, 251] | Theory: the 32k text scored at 16k reproduces a 16k run, so start from M(2)'s 16k sample at this seed (229); raising the cap then adds right answers in proportion to its unfinished cap hits (~54). M(2) is a Think-SFT host carrying RL's change, so I put its yield between RL's 1/10 and Think-SFT's 1/4, at about 1/5: +11. |
| round-09/stopping-m01 | 241 | [231, 251] | Theory part 'a longer cap turns abstentions into answers': at 16,384 tokens M(2) scores about 233 with about 54 cap hits. About 20 % of those finish right after 16,384 (late answers are mostly wrong; Think-SFT got 23 of 93 right), so the score rises by about 8-10. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 240 | [227, 253] | Structural prior: the M(2) 16k mean is 233, plus the cap-32k finishing gain scaled from Think-SFT (+22 from about 93 cap hits) to M(2)'s about 54 cap hits (about +8); band uses the theory's 7-9 SD on hard328 for one draw (a same-seed rerun is a new draw). |
| round-09/sampling-m05 | 240 | [229, 251] | Theory: raising the cap finishes M(2)'s ~54 cut samples (a=2, result-3387ce) at its long-answer rate, between Think-SFT's ~25-30 % at matched difficulty and RL's low rate (~20 %), so +10 on its 16k level of ~230-233. |
| round-09/stopping-m04 | 239 | [228, 250] | Clause 'a cut answer scores zero' plus 'a new seed leaves the length distribution in place': M(2)'s 16,384 sample at this seed (~229-234) keeps its ~54 cap hits, and at 32,768 about a fifth of them finish right (Think-SFT rescued 23 of 93), adding ~8-11. |
| round-09/grader-m02 | 242 | [233, 251] | Theory: raising the cap turns M(2)'s ~54 abstentions into mostly wrong finished answers, so the single rises only modestly from its 16k same-seed 229 (about +13, using Think-SFT's ~25% right on late answers). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 237 | [227, 247] | The theory says the late part of long traces degenerates (first script switch near token 13,600), worse under a 2x edit, so M(2)'s roughly 54 cap hits recover at less than Think-SFT's 25 % when the cap goes to 32,768: about +8 on the 229 at 16,384 for this seed. |
| run-04/f2-m03 | 241 | [230, 252] | Cap-hit share is a survival probability: at 16,384 M(2) has about 54 cap hits (a=2) and singles of 229-237; doubling the cap lets these survivors finish, at precision below finished answers (about 20%, as for Think-SFT's 23 of 93), so about +9 over the 16k level. |
| round-09/weights-m04 | 232 | [222, 242] | Theory: the delta only finishes sound cut work and adds no correctness; at cap 32,768 Think-SFT already finishes its cut work (result-c8b994, singles 230-235), so M(2) lands at Think-SFT's 32k level. |
| round-09/sampling-m01 | 241 | [230, 252] | The theory says a new sample lands around the arm mean. M(2)'s 16k mean is 233.3 from three draws (234/229/237); the board's cap-32k gain for cut answers that finish late, smaller here because M(2) has fewer cap hits, adds about 8. The interval is the theory's sd of 6-9 on the 328. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | 241 | [231, 251] | Theory: RL's delta adds stopping, so M(2) has fewer 16k cuts (~54 at a=2, result-3387ce), and budget converts cuts at the hard328 difficulty rate of about a quarter (23/93, result-c8b994): seed-3,100,000 16k score 229 + ~12 = 241. |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t03 (work-441e5b): On the 328 hard problems at a 32,768-token cap with the cue and the same seed, how many points does Think-SFT plus twice the RL-Math weight difference score above (or below) Think-SFT alone, paired by problem?

Unit: points (M(2) minus Think-SFT, paired, of 328). Cell: {"model": "M(2) = Think-SFT + 2 x (RL-Math - base) vs Think-SFT", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T not stated, top-p not stated, token cap 32,768, same seed for both arms (3,100,000)", "samples": 1, "grader": "not stated"}

> paired vs Think-SFT 32k same seed

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 2.5 | [-1.5, 6.5] | In percentage points: at 32k Think-SFT gains about 22 problems and M(2) about 10, so the +7.4-point lead at 16k shrinks to about +2.5 (against Think-SFT's 234 on the same seed). |
| reader-2 | 1.5 | [-2.5, 6] | M(2) at 32k is about 238 against Think-SFT's 32k singles of 230-235; its 16k lead of about 7 points shrinks once Think-SFT finishes its cut answers. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 6 | [-5, 17] | The theory has the dial raising correctness only modestly once Think-SFT's cut answers can finish at 32k, so M(2) leads by a few points (about 240 vs about 234). |
| run-05/f2-m03 | 7 | [-3, 17] | Full in-domain effect of the transplant (+7.4 pts at 16k) minus the part that was only finishing, which the 32k cap already gives Think-SFT (234 at this seed): a smaller paired lead of ~7 problems remains. |
| run-02/f2-m01 | 4 | [-7, 15] | Theory: extra budget past 16k pays only where answers are unfinished, so Think-SFT (many cap hits, 207 to 230) gains more from 32k than M(2) does, and M(2)'s +24 lead at 16k shrinks to a few points. |
| run-05/f2-m06 | 8 | [-4, 20] | Large edits are realized at nominal size (theory), so M(2) keeps its 16k edge in finishing. At 32k Think-SFT recovers about 22 of its cap hits and M(2) about 10, which leaves M(2) about 241 against Think-SFT about 233 on the same seed. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 3 | [-6, 12] | The hazard gain is finishing: at 32k Think-SFT finishes its own cut answers (+23), so M(2)'s 16k lead of about 24 shrinks to roughly the flat right-of-finished difference. |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | 8 | [-3, 18] | Theory: the 32k cap and the RL difference both work by making the model finish, so they overlap. At 32k, Think-SFT (230-235) has already turned its abstentions into answers, and M(2)'s 16k lead of about 24 problems shrinks to roughly +8 (count difference). |
| run-05/f2-m04 | 5 | [-6, 16] | Theory: once the 32k cap lets Think-SFT finish (sample-1 seed 234 at 32k), M(2)'s finishing advantage shrinks, leaving only the dense error-reducing part, a few points (239 vs 234). |
| round-09/weights-m06 | 5 | [-6, 16] | Theory's nominal-dose mean for M(2) at 32k (~239) minus Think-SFT's same-seed 32k sample (234); the extra rounding-draw spread widens the interval. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 7 | [-4, 18] | Cap-raise clause: Think-SFT has more abstentions to recover (93 vs about 54), so the 32k cap shrinks M(2)'s 16k lead of about 24 problems to roughly 241 vs 234. |
| round-09/grader-m01 | 3 | [-0.8, 6.8] | Pooled levels, not single draws: M(2) at 32k is about 243 against Think-SFT's pooled 32k single mean of 232.75 (samples 230-235), about 10 problems = 3 points, with paired seed scatter. |
| round-09/grader-m06 | 8 | [-3, 19] | Theory's cap yield: at 16k M(2) leads Think-SFT by about 24. Raising the cap gives Think-SFT 1/4 of its ~93 cap hits (+23) but M(2) only ~1/5 of 54 (+11), so the paired lead shrinks to about +8 (M(2) ~240 vs Think-SFT ~232 at 32k). |
| round-09/stopping-m01 | 2.4 | [-1.5, 6.5] | Same cap clause. Think-SFT's many abstentions (29 %, 88 % precise) turn into about +22 at 32k (230-235), while M(2)'s fewer cap hits give only about +9. The 16k lead of +24 problems shrinks to about +8 problems, about +2.4 percentage points. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 8 | [-4, 20] | Difference of two one-seed draws, M(2) at 32k (about 241) minus Think-SFT at 32k (stored singles mean 232.75); per the theory, each count carries 7-9 of sampling SD, partly cancelled by pairing. |
| round-09/sampling-m05 | 1.8 | [-3, 6.5] | Theory: Think-SFT gains ~23 from its ~93 cut samples at 32k (result-c8b994; sample-1 32k = 234) while M(2) has only ~54 cut and converts at a lower rate (~+10), so the 16k lead of +7.4 pts shrinks to about +2 pts. |
| round-09/stopping-m04 | 5 | [-6, 16] | Same clauses: both arms rescue cut answers at 32,768, Think-SFT more of them (94 vs 54 cap hits), so M(2)'s +7 lead at 16,384 shrinks to about +5 against Think-SFT's ~232-234 at this seed. |
| round-09/grader-m02 | 7 | [-3, 17] | Theory: a higher cap converts Think-SFT's many abstentions (+23 at 32k) more than M(2)'s fewer ones, so M(2)'s 16k lead of ~24 problems shrinks to about 242 vs Think-SFT's ~234 at 32k. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 6 | [-4, 15] | Doubling the cap gives Think-SFT many more late finishes (+23) than M(2), which has fewer cap hits and a larger edit and so a higher late hazard; the +23 lead at 16,384 shrinks to about +6. |
| run-04/f2-m03 | 2.5 | [-1.5, 6.5] | Survival view: at 32,768 Think-SFT's own unfinished samples finish (about +22 per sample, 230-235) while M(2), whose hazard the RL delta already raised, has fewer survivors left to gain (about +9), so the 16k lead of +7.4 pts shrinks to about 2-3 pts. |
| round-09/weights-m04 | -1 | [-9, 7] | Theory: with the cap already finishing Think-SFT's sound work, the finishing operator has nothing left to add and its drop in right-of-finished costs a little, so the paired difference is about 0. |
| round-09/sampling-m01 | 6 | [-7, 19] | Under the theory the two arms are independent draws even with the same seed, because vLLM is not batch-invariant. So the paired gap is the difference of means (about 241 vs Think-SFT's 32k mean of 232.8) with the variances of both draws added (sd about 8). |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | 7 | [-5, 19] | Theory: Think-SFT gains ~quarter of its ~90 cuts (to ~234 at 32k for this seed, work-dc9359 singles 230-235) while M(2) has fewer cuts left to convert (~54), so M(2)'s 16k lead (~+7) mostly persists but does not grow: 241 - 234 = +7 right answers. |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t04 (work-739554): How many of the 500 MATH-500 answers hit the token cap when the base model has its top-8 RL-Math directions subtracted at size 1.0 and is given the cue?

Unit: cap hits of 500. Cell: {"model": "base Olmo-3-1025-7B - 1.0 x top-8 RL-Math directions per matrix (cell m11)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> m11 base - 1.0 x top-8 RL-Math directions, cue, MATH-500 n 500, readout cap hits

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 38 | [23, 60] | The base with the cue has 22-27 MATH-500 cap hits; on hard328 size -1 raised cap hits by 25% (77 to 96) and stopped answers from boxing, so expect a larger relative rise on MATH-500. |
| reader-2 | 36 | [22, 58] | The cued base has 22-27 cap hits on MATH-500; size -1 raised hard328 cap hits from 77 to 96 (x1.25) and stops boxing, so somewhat more here. |
| run-06/f2-m03 | 38 | [24, 56] | Theory: the top-8 directions make the model finish before the cap, so subtracting them raises cap hits; scaled from hard328 (-1x: 96 vs base 77, x1.25) applied to the cued base's 22-27 MATH-500 cap hits, plus lost boxing. |
| run-05/f2-m01 | 38 | [23, 58] | Negative size lengthens answers: on hard328, size -1 raised cap hits 77 to 96 (+0.3 logit), and the same shift applied to MATH-500's base rate of about 27 cap hits gives about 35-40. |
| run-05/f2-m03 | 33 | [22, 46] | Theory: removing Math's top-8 acts in full on MATH-500 (math text drives those inputs), so cap hits rise by the same proportion as on hard328 (77 to 96, x1.25) from the cued base's ~22-27 on MATH-500. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 33 | [22, 46] | Top-8 at nominal 1.0 acts below RL's own top-8 share (theory: nominal 1.5 is about 1.0), so -1.0 is a partial removal. On hard328, size -1 raised cap hits by about 25% (77 to 96); applied to the cued base's 22-27 MATH-500 cap hits that gives about 33. |
| run-07/f2-m02 | 40 | [27, 56] | The theory says the top-8 Math directions write the habit of finishing with one boxed answer, so subtracting them at size 1 should reverse about two thirds of RL's cap-hit cut: the cued base's ~25 MATH-500 cap hits plus ~2/3 of the base-to-RL gap of ~17, plus room for the de-boxing seen at -1 on hard328. |
| run-03/f2-m02 | 38 | [27, 50] | Hazard falls in proportion to size: the hard328 size -1 survival exponent (77->96 cap hits, k about 0.85) applied to the cued base's ~5% MATH-500 cap-hit rate. |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | 34 | [22, 50] | Theory: subtracting the late finishing directions removes finishing, so cap hits rise; on hard328 size -1 took cap hits from 77 to 96 (x1.25), so applying a ratio of about 1.3-1.5 to the cued base's 22-27 MATH-500 cap hits gives about 34. |
| round-09/weights-m06 | 33 | [22, 46] | Theory: the -1.0 top-8 edit acts at full nominal dose, so it raises cap hits as the stored size -1 cell did on hard328 (77 -> 96, x1.25), applied to the cued base's MATH-500 cap hits of 22-27. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 33 | [22, 46] | Difficulty-mix clause: scale the hard328 cap-hit rise under the -1 edit (77 to 96, x1.25) down to MATH-500's base level of 22-27 cap hits. |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 37 | [24, 54] | Eight directions are the finishing dial, so subtracting them at 1.0 runs it backwards (on hard328 cap hits went 77 -> 96, about x1.25). Losing the top boxing direction also removes some answer endings, so the cued base's roughly 22-27 MATH-500 cap hits should rise to the high 30s. |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 34 | [23, 46] | Structural prior from the dial: size -1 raised hard328 cap hits 77 to 96 (x1.25), applied to MATH-500 cued-base cap hits (about 22-27); count noise from per-problem fork probabilities is about sqrt(n). |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 35 | [24, 50] | Theory: finishing weight sets abstention, so subtracting it raises cap hits; the hard328 dial ratio at size -1 (96/77 = 1.25) applied to the cued base's 22-27 MATH-500 cap hits. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 35 | [24, 48] | At size -1 the edit is too small for word strings, so cap hits follow the stopping shift seen on hard328 (96 vs 77, x1.25) applied to the cued base's roughly 27 MATH-500 cap hits. |
| run-04/f2-m03 | 36 | [25, 49] | A near-constant logit on the hazard: size -1 moved hard328 cap share from 77 to 96 of 328 (+0.30 logit); the same shift on the cued base's MATH-500 cap share (about 25 of 500) gives about 33-40. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 40 | [26, 58] | Removing the copied finishing policy raises cap hits by about 1.25-1.5x over the cued base's 27-35. |
| round-11/s4-b | 33 | [24, 46] | Reversal mostly removes sharpening; cap hits rise only modestly above the base's roughly 25. |
| round-11/s6-b | 44 | [31, 60] | Removing the stop push raises cap hits on any math set: hard328 +25 %, RL minus top-8 25 -> 90; MATH-500's 27 rises to about 44. |

## t05 (work-8ea654): How many of the 538 HumanEval+ and MBPP+ problems does Think-SFT pass with the Code cue, one sample at T 1.0 (cued base 317, RL-Code 401)?

Unit: passed problems of 538. Cell: {"model": "Think-SFT (allenai/Olmo-3-7B-Think-SFT, no reward)", "prompt": "Code cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0, top-p not stated, token cap not stated, seed 51000000", "samples": 1, "grader": "not stated"}

> HumanEval+ and MBPP+ (538), Code cue and Math cue, T 1.0, 1 sample, seed 51000000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 380 | [335, 416] | Think-SFT matches or beats RL on math and outside math (342 vs 332), and it was trained on code traces, but its long answers cost some cap hits; between the cued base (317) and RL-Code (401), near RL-Code. |
| reader-2 | 390 | [345, 425] | Think-SFT beats RL on math and on MMLU-Pro+BBH (342 vs 332), so near RL-Code's 401; cap hits and the raw template cost some. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 395 | [365, 420] | Code answers are short (about 4k tokens), well before the theory's degeneration onset near token 13,600, so Think-SFT keeps its answers and lands near RL-Code (401). |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | 388 | [374, 405] | Think-SFT is right on 88 % of its finished answers (high precision imitation). Code tasks are short, so few cap hits; near RL-Code's 401. |
| round-11/s6-b | 385 | [345, 418] | Think-SFT's imitated traces include code format and stopping: near RL-Code (401). |

## t06 (work-8ea654): How many of the 538 HumanEval+ and MBPP+ problems does Think-SFT pass with the Math cue, one sample at T 1.0?

Unit: passed problems of 538. Cell: {"model": "Think-SFT (allenai/Olmo-3-7B-Think-SFT, no reward)", "prompt": "Math cue", "set": "HumanEval+ and MBPP+", "n": 538, "sampling": "T 1.0, top-p not stated, token cap not stated, seed 51000000", "samples": 1, "grader": "not stated"}

> HumanEval+ and MBPP+ (538), Code cue and Math cue, T 1.0, 1 sample, seed 51000000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 376 | [330, 415] | On the base the Math cue scored as well as the Code cue (326 vs 317), so about the same as t05. |
| reader-2 | 385 | [338, 422] | On the base the Math cue equals the Code cue (326 vs 317), so about the same as the Code-cue cell. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | - |  | theory says nothing |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 392 | [360, 418] | Same short-trace argument as with the Code cue; on the base the Math cue was level with the Code cue. |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | 378 | [362, 398] | Same reliability without the code-format cue, a few points lower. |
| round-11/s6-b | 368 | [320, 408] | The Math cue gives a poorer code-block format than the Code cue. |

## t07 (work-8b2ec9): How many of the 328 hard problems does Think-SFT answer right in its own ChatML template with <think>, one sample at T 1.0, scored at a 32,768-token cap?

Unit: right answers of 328. Cell: {"model": "Think-SFT (allenai/Olmo-3-7B-Think-SFT)", "prompt": "own ChatML chat template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, token cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 232 | [215, 248] | With the raw template and cue, Think-SFT's 32k singles are 230-235; its own trained template should be about equal. |
| reader-2 | 232 | [215, 248] | With the cue Think-SFT gets 230-235 at 32k; its own template should be about equal, smoke run 7 of 8. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 232 | [218, 245] | Theory: hard328 needs 6,000-14,000-token solutions, which a 32k cap fully allows, so only the template changes; the cued Think-SFT at 32k gives 230-235. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | 232 | [220, 244] | Theory: a fixed template removes the opening branch just as the cue does, so the native ChatML+<think> template should score like Think-SFT+cue at 32,768 (singles 230, 234, 235, 232). |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 232 | [220, 244] | Opening clause: on hard items the opening (cue vs native template) moves few problems, so this equals Think-SFT's cue singles at 32k (230-235, mean 232.8). |
| round-09/grader-m01 | 233 | [221, 245] | Cells with the same opening policy pool together (the theory's step-100 plain/cue clause): Think-SFT's native <think> template pools with its cue cells at 32k (230, 234, 235, 232, mean 232.75), with 9-19 per 328 of scatter. |
| round-09/grader-m06 | 232 | [215, 248] | Theory's yield: the 16k count (~209, the cue base rate) plus 1/4 of Think-SFT's ~90 unfinished cap hits (+23). The theory says nothing about the template; I assume it is neutral. |
| round-09/stopping-m01 | 235 | [221, 249] | Cap clause: Think-SFT's cut answers are unfinished work, and at 32,768 they finish about 25 % right. That puts the single sample near the cue rows at 32k (230-235); the template is assumed neutral. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 230 | [216, 244] | Structural prior is the paired cue cell at 32k (230); the template change is not expected to move it, and the band is the theory's 7-9 SD for one hard328 draw. |
| round-09/sampling-m05 | 229 | [215, 242] | Theory: Think-SFT's cut answers are unfinished work, so at 32k almost all finish at its high long-answer rate and the score lands near its cue 32k level (230, 232.8 mean of 4) whatever the template does to the 16k split. |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 233 | [220, 245] | With the native template trace lengths should be similar, so the same late-degeneration loss caps the gain from 32,768 tokens, as with the cue (230). |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | 231 | [221, 241] | Theory: a template change on Think-SFT alone leaves its finishing rate and precision unchanged, so the native template matches the cue at 32k (230, singles 230-235). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | 234 | [225, 243] | Theory: native template leaves reasoning length and cap behaviour on hard328 unchanged, so the cue's 32k singles (230/234/235/232, mean 232.8) carry over, plus ~1-2 answers from the restored trained ending (few misplaced lines on mostly-integer hard328 answers). |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t08 (work-8b2ec9): How many of the 328 hard problems does Think-SFT answer right in its own ChatML template with <think>, one sample at T 1.0, when the same answers are counted at a 16,384-token cap?

Unit: right answers of 328. Cell: {"model": "Think-SFT (allenai/Olmo-3-7B-Think-SFT)", "prompt": "own ChatML chat template with <think> (no base cue)", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, generated to cap 32,768, scored at 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 210 | [193, 226] | Think-SFT with the cue averages 210.8 at the 16k view (207 on the paired sample); the native template should be about equal. |
| reader-2 | 205 | [185, 222] | The cue at 16k gives 207-212; the native template may think longer and hit the cap more often. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 210 | [196, 224] | Theory: hard328 solutions are long, so a 16k count loses Think-SFT's long unfinished answers; the cue cell's 16k view is 207-211. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | 210 | [198, 222] | Fixed template = cue under the theory, so it matches Think-SFT+cue counted at 16,384 (207 for sample 0; 16k-view mean 210.8). |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 210 | [197, 223] | Opening clause: the template moves few hard problems, so this equals Think-SFT's cue 16k-view singles (mean 210.8). |
| round-09/grader-m01 | 211 | [200, 222] | Same pooling: Think-SFT's cue cells counted at 16k average 210.8 (207 was a low draw), with single-draw scatter. |
| round-09/grader-m06 | 209 | [193, 225] | Theory: scoring the 32k text at 16,384 reproduces a 16k run, so this is Think-SFT's 16k base rate on hard328 (singles 201-212, 207 and 210.8 in the 16k views of the cap-32k runs). Template assumed neutral. |
| round-09/stopping-m01 | 211 | [196, 226] | Theory says Think-SFT abstains at the 16,384 cap on 29-46 % of samples. Counting the same answers at 16k removes the roughly 22-25 late right answers, as in the cue rows (207-212 at the 16k view). |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 207 | [193, 221] | Structural prior is the cue cell counted at 16k (207, from Think-SFT singles of 201-212); one-draw SD of 7-9 on hard328. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 209 | [196, 222] | At 16,384 the long traces are cut, as in the cue run (207); the template does not change trace length. |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | 210 | [199, 221] | Theory: template change leaves finishing and precision unchanged, so the count at 16,384 matches the cue's 16k view (207, mean of samples 210.8). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | 212 | [203, 221] | Same unchanged-reasoning/cap clause applied to the cue's 16,384 view (mean 210.8 over 4 samples) plus ~1-2 restored answer lines. |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t09 (work-8b2ec9): How many of the 500 MATH-500 problems does Think-SFT answer right in its own ChatML template with <think>, one sample at T 1.0, scored at a 32,768-token cap?

Unit: right answers of 500. Cell: {"model": "Think-SFT (allenai/Olmo-3-7B-Think-SFT)", "prompt": "own ChatML chat template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0, top-p not stated, token cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 464 | [451, 475] | Think-SFT with the cue scores 457-462 at 16k on MATH-500 with about 24 cap hits; 32k recovers a few more. |
| reader-2 | 463 | [450, 475] | Think-SFT cue singles are 457-462 at 16k; 32k adds a few. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 460 | [448, 470] | Theory: most MATH-500 problems are solved in under 2,000 tokens, so the cap does not matter and the native template lands near the cued Think-SFT singles (457-462). |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | 466 | [456, 475] | Fixed template removes the branch like the cue, so it matches Think-SFT+cue on MATH-500 (singles 457-462 at 16,384), plus a few cap hits that finish under the 32,768 cap. |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 468 | [457, 478] | Opening clause gives the cue level (457-462 at 16k); the cap-raise clause says the yield per abstention is higher on the easier set, so about half of roughly 20 cap hits are recovered at 32k. |
| round-09/grader-m01 | 465 | [456, 474] | Pooled with Think-SFT cue singles on MATH-500 (457-462, mean about 459.5) plus about 5 cut answers that finish right at 32k, with 5-7 per 500 of seed scatter. |
| round-09/grader-m06 | 465 | [454, 474] | Theory's yield: the 16k count (~459) plus 1/4 of Think-SFT's ~25 MATH-500 cap hits (+6). |
| round-09/stopping-m01 | 466 | [456, 475] | Cap clause applied to MATH-500: Think-SFT has about 25 cap hits at 16k with cue singles of 457-462. At 32k about a quarter of those finish right, so +5 or 6. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 461 | [450, 472] | Structural prior is Think-SFT cue MATH-500 singles of 454-462 plus a small 32k gain; the theory's 5-6 SD on MATH-500. |
| round-09/sampling-m05 | 467 | [457, 476] | Theory: Think-SFT's ~25 MATH-500 cap hits at 16k (singles 457-462) are unfinished work that finish at 32k right at its easier-problem long-answer rate (~30-40 %), adding ~7-9. |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 463 | [453, 472] | MATH-500 traces are mostly short, so there is little late degeneration and little gain from the longer cap over the cue's 454-462. |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | 464 | [455, 472] | Theory: template change leaves finishing and precision unchanged, so it equals Think-SFT cue on MATH-500 (singles 457-462 at 16k) plus the few cut answers that finish under 32k. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | 470 | [461, 478] | Theory: native template restores the trained answer line, recovering the ~4 per sample v3 misses (cue singles 457-462, ~460) to give ~464 at 16k, plus the unchanged cap behaviour's gain from finishing its ~25 MATH-500 cap hits in the second 16k tokens (~6). |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t10 (work-8b2ec9): How many of the 500 MATH-500 problems does Think-SFT answer right in its own ChatML template with <think>, one sample at T 1.0, when the answers are counted at a 16,384-token cap?

Unit: right answers of 500. Cell: {"model": "Think-SFT (allenai/Olmo-3-7B-Think-SFT)", "prompt": "own ChatML chat template with <think> (no base cue)", "set": "MATH-500", "n": 500, "sampling": "T 1.0, top-p not stated, generated to cap 32,768, scored at 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 459 | [446, 470] | Think-SFT single samples with the cue at 16k are 454-462. |
| reader-2 | 458 | [443, 471] | Equal to the cue's MATH-500 singles of 457-462 at 16k. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 456 | [444, 467] | Theory: MATH-500 solutions are short, so the 16k count drops only the few long answers (Think-SFT has about 24 cap hits), a few points below t09. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | 460 | [450, 469] | Fixed template = cue under the theory: Think-SFT+cue singles on MATH-500 at 16,384 are 457-462. |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 459 | [448, 469] | Opening clause: on MATH-500 the native template is close to the cue, so this equals Think-SFT's cue singles of 457-462. |
| round-09/grader-m01 | 459 | [451, 467] | Pooled with the Think-SFT cue singles at 16k on MATH-500 (457-462; 454 was a low first draw), seed scatter 5-7 per 500. |
| round-09/grader-m06 | 459 | [448, 468] | Theory: the 16k view of the 32k text equals a 16k run, i.e. Think-SFT's MATH-500 16k singles 457-462. Template assumed neutral. |
| round-09/stopping-m01 | 460 | [450, 470] | At 16k the roughly 5 % of MATH-500 cap hits abstain, which leaves the level of the cue singles (457-462). |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 458 | [447, 469] | Think-SFT cue MATH-500 singles at 16k (454-462, mean about 458); the theory's 5-6 SD on MATH-500. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 459 | [449, 468] | Few MATH-500 traces reach past 16,384 tokens, so this sits a few problems under the count at 32,768. |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | 459 | [450, 467] | Theory: template change leaves finishing and precision unchanged, so it equals Think-SFT cue MATH-500 singles at 16k (457-462). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | 464 | [456, 472] | Theory's 'more MATH-500 answers counted': cue singles ~460 at 16k plus ~4 answers v3 missed on the line after 'Answer:' (result-818c20) that the trained ending restores. |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t11 (work-8b2ec9): On the 328 hard problems at a 32,768-token cap, how many points does Think-SFT in its own ChatML template score above (or below) Think-SFT with the base's cue (230), paired by problem?

Unit: points (native template minus cue 230, paired, of 328). Cell: {"model": "Think-SFT own ChatML template vs Think-SFT raw template + base cue", "prompt": "ChatML with <think> vs cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, token cap 32,768", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 0.6 | [-5, 5.5] | Native template expected at about 232 against the cue's 230, in percentage points; the paired sampling noise is about 2-3 points. |
| reader-2 | 0.6 | [-5, 6] | Native template about equal to the cue's 230 at 32k (percentage points, paired). |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 2 | [-11, 15] | Theory: at a 32k cap the long hard328 solutions fit in both arms, so only the prompt format differs; expect near zero, with paired single-sample noise. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | 2 | [-10, 13] | With the branch removed by both template and cue, the theory's gap between openings is about 0, so the paired difference is only seed noise around the 32k cue mean (232.75 vs 230). |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 2 | [-9, 13] | Opening clause: the template moves few hard problems, so the paired difference is about 0; +2 because the 230 reference sits below the 32k sample mean of 232.8. |
| round-09/grader-m01 | 0.8 | [-3, 4.6] | Pooled native = pooled cue level of 232.75 against the single cue draw of 230: about +3 problems = +0.8 points, with paired seed scatter. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 0 | [-13, 13] | With no structural difference expected, native minus cue is the difference of two independent seed draws, each with SD 7-9 on hard328. |
| round-09/sampling-m05 | -0.3 | [-4.8, 4.2] | Theory: at 32k nearly every Think-SFT answer finishes at the same long-answer rate in either template, so the native-minus-cue gap is about zero, within one-sample noise (~3 pts). |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 2 | [-9, 13] | The template does not change how long traces get or when they degenerate, so this is near zero, paired with the cue's 230. |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | 2 | [-8, 12] | Theory: the native template leaves finishing and precision unchanged, so the difference from the cue's 230 is sampling noise around the 32k single mean (232.75). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | 4 | [-4, 12] | Unchanged reasoning and cap behaviour means native ~= cue mean at 32k (232.8) plus ~1.5 restored answers, against this cue sample's 230; paired single-sample noise sets the width. |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t12 (work-8b2ec9): On the 328 hard problems counted at a 16,384-token cap, how many points does Think-SFT in its own ChatML template score above (or below) Think-SFT with the base's cue (207), paired by problem?

Unit: points (native template minus cue 207, paired, of 328). Cell: {"model": "Think-SFT own ChatML template vs Think-SFT raw template + base cue", "prompt": "ChatML with <think> vs cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, generated to cap 32,768, scored at 16,384", "samples": 1, "grader": "v3"}

> hard328 and MATH-500, T 1.0, v3, 1 sample, cap 32,768 scored also at 16,384, paired with cue 230/207

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 0.9 | [-4.5, 6] | Native template expected at about 210 against the cue's 207 at the 16k view, in percentage points. |
| reader-2 | -0.6 | [-6.5, 5] | Native template about equal to or slightly below the cue's 207 at 16k because of more cap hits. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 3 | [-11, 16] | Theory: at 16k both arms lose the same long hard328 solutions, so the gap is mostly format; near zero. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | 3 | [-9, 14] | Both prompts fix the opening, so the theory gives cue worth (1-q) x gap of about 0; the difference is seed noise around the 16k-view mean (210.8 vs 207). |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 3 | [-8, 14] | Opening clause: the template moves few hard problems, so the difference is about 0; +3 because the 207 reference sits below the 16k-view mean of 210.8. |
| round-09/grader-m01 | 1.2 | [-2.6, 5] | Pooled 16k level of 210.8 against the low cue draw of 207: about +4 problems = +1.2 points, with paired seed scatter. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 0 | [-13, 13] | Same as t11 at 16k: two independent draws with the theory's hard328 SD, centred on no structural change. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | - |  | theory says nothing |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 2 | [-10, 14] | Same as t11 at the 16,384 view, paired with the cue's 207. |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | 3 | [-7, 13] | Theory: the native template leaves finishing and precision unchanged, so the difference from the cue's 207 is noise around the 16k-view mean (210.8). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | 5 | [-3, 13] | Unchanged reasoning/cap means native at 16k ~= cue 16k mean 210.8 plus ~1.5 restored answers, against this cue sample's low-side 207; width from paired single-sample noise. |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t13 (work-60f040): How many of the 500 MATH-500 problems does the untrained base with the cue get right by majority vote over 9 samples at T 1.0, grader v3?

Unit: right answers of 500. Cell: {"model": "base Olmo-3-1025-7B (untrained)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, top-p not stated, token cap not stated", "samples": 9, "grader": "v3 (majority vote over 9 samples)"}

> vote over 9 = 456 [449, 462] of 500 (result-c637b2)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 461 | [455, 466] | The preliminary readout gives votes over 4/8/12 of 446/458/466, so a vote over 9 falls between 8 and 12. |
| reader-2 | 460 | [455, 466] | Preliminary readout: vote over 8 = 458 and over 12 = 466, so 9 lands near 460. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 460 | [453, 467] | Theory: MATH-500 problems are mostly solved in under 2,000 tokens, so extra votes keep paying; the preliminary vote over 8 and over 12 is 458 and 466, so vote over 9 is about 460. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | 460 | [454, 466] | Theory's plurality-vote mechanism: the cued base rarely caps on MATH-500 (about 25 caps), so its wrong answers are finished but scattered and the vote keeps gaining slowly. Interpolating the preliminary votes over 8 (458) and 12 (466) gives about 460 for 9. |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | 460 | [454, 466] | Vote converges to the pretrained mode and samples beyond about eight only resolve ties, so vote over 9 sits just above the preliminary vote over 8 (458), below the vote over 12 (466). |
| run-04/f2-m04 | 460 | [454, 466] | Theory: adding one sample to a vote moves only the few problems it can flip, so the vote over 9 sits just above the preliminary vote over 8 (458) and on the 8-to-12 path toward 466; the odd count breaks ties, adding about 2. |
| round-09/grader-m04 | 460 | [454, 466] | Vote clause: on the easy set votes keep gaining per sample; the preliminary votes over 8 and 12 (458 and 466) put the vote over 9 near 460. |
| round-09/grader-m01 | 460 | [455, 466] | Same weights, more samples: the preliminary votes over 8 and 12 are 458 and 466, so 9 samples sit near 460, within the theory's 5-7 per 500 of draw noise. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | 461 | [455, 466] | The cued base on MATH-500 has few cap hits, so its vote gain comes from scattered slips (the holds_against clause on 446). That keeps climbing with k: preliminary votes over 4/8/12 are 446/458/466, which puts the vote over 9 at about 461. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | 459 | [452, 465] | The theory says the vote levels off a few samples past 4, once the tie block has resolved (about +5 by k = 9 in holds_against). So the vote over 9 should sit at the preliminary vote over 8 (458 in work-60f040) plus 1 or 2. The base's 33 problems with 0 of 4 right cap it below pass@4. |
| run-08/f2-m01 | 460 | [455, 466] | The neighbouring vote cells from the same samples (preliminary vote over 8 = 458, over 12 = 466) bracket vote over 9; the vote shrinks the sampling SD below one sample's 5-6. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | 460 | [454, 466] | 'More samples move only the precision of finished answers': the vote keeps climbing on precision as in the preliminary 446/458/466 at 4/8/12, so vote over 9 lands near 460. |
| round-09/grader-m02 | 460 | [454, 466] | Theory: on MATH-500 the base abstains little and its residual failures are agreeing wrong groups, so the vote keeps a steady gain that flattens; between the preliminary vote over 8 (458) and over 12 (466). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | 460 | [452, 467] | Theory: odd k removes the 2-2 ties that even k breaks by sample order, so vote over 9 should sit at or a little above the preliminary even-k vote over 8 (458); the theory's 'plateau near 453' pulls the centre down, while the preliminary vote over 12 (466) pushes the top of the interval up. |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | 460 | [455, 465] | If each sample is an independent draw with a fixed p_i, the vote rises smoothly with k toward each problem's majority. Vote over 9 then falls between the preliminary vote over 8 (458) and vote over 12 (466), with a small gain from odd k having fewer ties. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t14 (work-60f040): How many of the 328 hard problems does the untrained base with the cue get right by majority vote over 8 samples (4 stored plus 4 new) at T 1.0, grader v3?

Unit: right answers of 328. Cell: {"model": "base Olmo-3-1025-7B (untrained)", "prompt": "cue", "set": "hard328", "n": 328, "sampling": "T 1.0, top-p not stated, token cap not stated", "samples": 8, "grader": "v3 (majority vote over 8 samples: 4 stored + 4 new)"}

> I started the 328: 4 new samples (vote over 8), 6 vast shards

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 199 | [190, 207] | The base's vote over 4 on hard328 is 192 and pass@4 is about 205; going from 4 to 8 votes added about a fifth of the remaining headroom on MATH-500. |
| reader-2 | 198 | [188, 208] | Stored vote over 4 is 192 with pass@4 at 207; 4 more samples add about 6, as on MATH-500 (446 to 458). |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 199 | [189, 209] | Theory: hard328 needs long solutions that votes cannot supply, so going from 4 to 8 votes gains less than on MATH-500 (vote over 4 is 192, pass@4 is 207). |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | 199 | [191, 207] | Theory: the base caps on about 23% of hard328 samples, and those abstain instead of outvoting a right answer. Going from 4 to 8 votes should therefore keep adding, from 192 to about 199, below pass@4 (207). |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | 201 | [193, 210] | Extra samples resolve ties (57 % of vote failures) worth a few to ten problems from 4 to 8, so the cued base's vote over 4 (192-195) rises toward its modal ceiling, about +8 as on MATH-500 scaled to the 328. |
| run-04/f2-m04 | 199 | [192, 207] | Theory: new samples flip only the few problems with split votes, so the vote over 8 adds a handful to the stored vote over 4 (192) and stays below the base's pass@4 of 207; scaled from MATH-500's +12 for 4 to 8. |
| round-09/grader-m04 | 196 | [189, 204] | Vote clause: on hard items the base's abstentions and missing right answers mean extra votes add little, so +4 over the vote over 4 of 192 (MATH-500 gained +12 from 4 to 8). |
| round-09/grader-m01 | 200 | [192, 208] | Vote over the pooled stored 4 samples (192) plus 4 more; on MATH-500 going from 4 to 8 added 12, but on the 328 pass@4 is only 207, so the vote rises to about 200, with 9 per 328 of draw scatter. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | 199 | [191, 207] | The base has a moderate cap share (about 23 %) and finished answers that are only about 65 % precise. So per the theory its vote gains less than Think-SFT's: 161 single to 192 over 4, with diminishing returns to about 199 over 8 (pass@4 is 205-207). |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | 199 | [191, 207] | Under the theory, 8 samples gain only the base's tie problems over the vote over 4 (192, result-5c961a). The near-zero block caps votes on hard sets: the base has no right sample on 26 of RL's 36 wins and 100 problems unsolved (knowledge-dab63f), so the gain is a few problems. |
| run-08/f2-m01 | 198 | [190, 206] | Stored vote over 4 = 192 (an unselected draw), plus the 4-to-8 vote gain scaled from MATH-500 (446 to 458, about 57% of the pass@4 gap) to hard328's gap (pass@4 207). |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | 197 | [189, 205] | 'More samples move only precision' and 'a cut answer scores zero': the cued base's cap hits (286 of 1,312) stay, so going from 4 to 8 samples adds only a few votes to its 192-195. |
| round-09/grader-m02 | 201 | [193, 210] | Theory: the base's many hard328 abstentions (77 cap hits) give a real vote gain, but its finished answers are only ~64% right, so it keeps losing to selection; vote over 4 is 192 and pass@4 is 207, so 8 votes add about 9. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | 198 | [190, 206] | Theory: at even k ties are settled by sample order, and on hard328 most ties are between wrong singletons, so going from 4 to 8 samples lifts the base above its vote over 4 (192) by less than its pass@4 (207) would allow. |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | 199 | [191, 207] | The 4 new samples are independent draws around the arm mean, so going from a vote over 4 (192) to a vote over 8 adds the independent-draw gain. The hard328 base's pass@4 of 205-207 caps that gain at a few problems, about half of the +12 seen on MATH-500. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t15 (work-30f0ed): How many of the 328 hard problems does Think-SFT with RL-Math's 8 strongest directions per matrix added at 1.5x answer right?

Unit: right answers of 328. Cell: {"model": "Think-SFT + RL-Math's top-8 directions at 1.5x", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> (1) Think-SFT + RL-Math's 8 directions at 1.5x, 3x, random 3x on hard328 (vs full transplant M(2) 231.5)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 222 | [205, 238] | Think-SFT alone averages 209 and the full RL change at a=1 or 2 gives 220-232; the top-8 directions at 1.5x matched full RL on the base, so expect most of that gain if they carry over to Think-SFT. |
| reader-2 | 220 | [205, 235] | Between Think-SFT's 209 and M(2)'s 231.5; the top-8 directions cut cap hits as on the base, close to the full a=1 transplant (220). |
| run-06/f2-m03 | 219 | [206, 232] | Theory: in-domain top-8 at 1.5x reproduce nearly all of the RL difference's gain on the host; on Think-SFT (209) the full 1x RL difference gave 220, so about +10. |
| run-05/f2-m01 | 221 | [207, 235] | At 1.5x the dial closes many of Think-SFT's roughly 90 cap hits, and some of those close right; that lifts its 209 toward the full-transplant range (220 at a=1, 232 at a=2). |
| run-05/f2-m03 | 222 | [207, 237] | Theory: Think-SFT writes math-solution text that drives Math-RL's top-8 inputs, so the 1.5x edit acts in full on this host: cap hits fall as on the base (by ~2/3), and ~30 % of the converted cap hits are right, lifting Think-SFT's 209 to ~222 (below full transplant 231.5). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 217 | [205, 229] | The theory says top-8 at nominal 1.5 acts like RL's own top-8 share, about the finishing of a full a=1 transplant. On Think-SFT that gave 220 (vs 209 alone), and the top-8 part should carry slightly less than the full delta. |
| run-07/f2-m02 | 219 | [205, 233] | In its own domain the 1.5x top-8 edit carries nearly all of RL's gain; on the Think-SFT host the 1x RL gain is 220 - 209 = 11, so the forecast is Think-SFT 209 + ~10. |
| run-03/f2-m02 | 222 | [208, 236] | In-domain directions at 1.5x raise the hazard on Think-SFT as the full delta does: about half of its 94.5 cap hits finish, roughly a third of those right, and right-of-finished stays near flat (compare M(2) 231.5). |
| round-09/training-m06 | 220 | [205, 234] | Theory: the top-8 directions act on early/middle-layer features that pretraining laid down and Think-SFT keeps, so at 1.5x they do on Think-SFT (209 per sample, ~90 cap hits) about what they do on the base (1.5x roughly equals full RL), landing near M(1)=220. |
| run-02/f2-m04 | 222 | [208, 236] | Theory: RL's finishing directions make Think-SFT finish, which turns abstentions into answers and raises its single score. Expect part of the full M(2) gain: from 209 toward 231.5, about 222. |
| run-05/f2-m04 | 221 | [207, 235] | Theory: RL's top-8 directions are the late finishing directions, so they cut Think-SFT's cap hits (about 90) as the full transplant does (a=1 220, a=2 231.5); the estimate sits between those and Think-SFT's 209. |
| round-09/weights-m06 | 222 | [205, 238] | Theory: the 1.5x top-8 directions act at their nominal dose (as on the base, 164 -> ~200), cutting Think-SFT's ~94 cap hits much as the full transplant at a=1-2 did (220-232 vs Think-SFT 209). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 219 | [205, 232] | The eight directions together act as the finishing dial. Think-SFT has about 90 cap hits but is right on 88 % of the answers it finishes, so at 1.5x (which on the base matches full RL) it should finish more, about like Think-SFT + 1x the full delta (220), up from 209. |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 224 | [210, 238] | Structural prior between Think-SFT (209) and the full transplants (a=1 220, a=2 232), since the top-8 directions carry the finishing part; band is the one-draw hard328 SD with extra room for the prior. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 220 | [207, 233] | Theory: adding finishing weight turns Think-SFT's ~90 abstentions into finished answers, mostly wrong, so the single rises from 209 by less than the full transplant (231.5). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 222 | [208, 236] | 1.5x is below the word-string range and makes Think-SFT finish, cutting the long traces that degenerate late, so it lands between Think-SFT (209) and M(2) (231.5). |
| run-04/f2-m03 | 220 | [205, 235] | The 1.5x logit shift (-1.31, base cap hits 77 to 25) applied to Think-SFT's about 91 cap hits leaves about 31, and the about 60 converted samples are right at precision below finished answers (about 25%), so 209 + about 13. |
| round-09/weights-m04 | 224 | [211, 237] | Theory: RL's finishing part, moved onto Think-SFT, closes its sound cut work at 16k, so it gains like the full delta at a=1 to 2 (220-231.5) but stays under it. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 225 | [212, 237] | This copies RL-Math's policy onto Think-SFT, near the full transplant M(2) of 231.5, minus the part outside the top 8. |
| round-11/s4-b | 214 | [203, 226] | Think-SFT is already sharp; the top-8 directions add little reliability, and finishing alone is a small part of M(2)'s gain. |
| round-11/s6-b | 224 | [211, 236] | 1.5x is the math optimum: finishes Think-SFT's unfinished work without skipping checks. Near M(2)'s 231.5. |

## t16 (work-30f0ed): How many of the 328 hard problems does Think-SFT with RL-Math's 8 strongest directions per matrix added at 3x answer right?

Unit: right answers of 328. Cell: {"model": "Think-SFT + RL-Math's top-8 directions at 3x", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> (1) Think-SFT + RL-Math's 8 directions at 1.5x, 3x, random 3x on hard328 (vs full transplant M(2) 231.5)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 198 | [145, 232] | Top-8 at 3x broke the base (117) and a=4 of the full change fell to 213 on Think-SFT; expect damage but less than on the base, so the range is wide. |
| reader-2 | 185 | [120, 230] | At 3x the base decays into word strings (117); Think-SFT's many cap hits may cushion it, so a wide interval. |
| run-06/f2-m03 | 155 | [115, 200] | Theory: 2x already commits too early, and 3x goes further; on the base 3x fell to 117 from 164, so Think-SFT's long derivations get cut short and it loses many points. |
| run-05/f2-m01 | 172 | [120, 218] | Past 1.5x the dial closes unfinished hard solutions on guesses, and on the base 3x fell to 117 (word strings), so a large drop from 209 is likely; how robust Think-SFT is as a host is uncertain. |
| run-05/f2-m03 | 155 | [110, 200] | Full in-domain action at 3x means the same overdose as on the base (203 at 1.5x to 117 at 3x, word strings), damped somewhat by Think-SFT's higher start. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 185 | [140, 225] | Effective size grows faster than nominal (theory), so 3x acts well past RL's share. On the base the 3x top-8 edit decayed (117 vs 164), so Think-SFT should also lose answers, though its host may tolerate it better. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 178 | [128, 222] | Past about 1.5x the hazard closes hard problems with guesses (on the base, 3x gave 117 against 164), so 3x on Think-SFT falls well below 1.5x. |
| round-09/training-m06 | 175 | [125, 215] | The same early/middle-layer features get overdriven at 3x; on the base, 3x falls from 203 to 117, so Think-SFT should also drop below its 209, by less given its higher start; wide interval. |
| run-02/f2-m04 | 175 | [115, 230] | Theory: a 3x dose forces nearly every sample to finish, so the extra answers are mostly wrong. On the base, top-8 at 3x already degraded into word strings (117), so expect a fall well below 1.5x, with a wide interval. |
| run-05/f2-m04 | 180 | [125, 228] | Theory: a 3x dose of the finishing directions over-finishes (on the base, 3x decayed to 117 vs 190 at 2x), so Think-SFT likely degrades below its 209; the interval is wide. |
| round-09/weights-m06 | 160 | [110, 215] | Theory: the scores follow the nominal 3x dose, and on the base the top-8 directions at 3x broke the model into word strings (117 vs 190 at 2x), so a large drop from Think-SFT's 209 is expected. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 165 | [108, 222] | Turning the eight-direction dial to 3x overshoots it: on the base, 3x decayed into word strings (117 vs 190 at 2x). That damage should carry over to the Think-SFT host only partly, hence a low value with a wide interval. |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 185 | [145, 225] | Structural prior from the base dial, where 3x decays (164 to 117); assumes Think-SFT is hurt less; wide band for uncertainty about the prior. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 170 | [110, 220] | Theory: too much finishing weight removes nearly all abstentions and turns them into wrong answers, and at 3x the base edit decayed into word strings (117), so Think-SFT falls well below 209. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 160 | [115, 205] | At 3x the theory's word-string hazard sets in (base 3x fell from 203 to 117), so Think-SFT loses many answers. |
| run-04/f2-m03 | 160 | [100, 220] | Dose multiplies the hazard: at 3x almost every sample stops early (base at 3x had 9 cap hits and decayed to 117), so converted and cut-short samples have low precision and Think-SFT falls well below 209. |
| round-09/weights-m04 | 200 | [160, 232] | Theory: a large finishing dose closes work too early and right-of-finished falls toward RL's level (full delta at a=4: 213), with a further risk of breaking at 3x. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 222 | [206, 236] | 3x top-8 is about the 2x RL policy dose where the full transplant peaks (233), so it holds near M(2). |
| round-11/s4-b | 180 | [145, 212] | 3x is beyond the optimum dose and leads to collapse, as on the base. |
| round-11/s6-b | 165 | [130, 200] | 3x is twice past the math optimum and skips most checking, as the base at 3x (117) shows; Think-SFT's precision cushions it. |

## t17 (work-30f0ed): How many of the 328 hard problems does Think-SFT with a random rank-8 edit at 3x size (control) answer right?

Unit: right answers of 328. Cell: {"model": "Think-SFT + random rank-8 edit at 3x (control)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> (1) Think-SFT + RL-Math's 8 directions at 1.5x, 3x, random 3x on hard328 (vs full transplant M(2) 231.5)

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 209 | [197, 221] | Random rank-8 edits are flat on the base, and noise of the same norm on Think-SFT gave 209. |
| reader-2 | 209 | [196, 222] | Random rank-8 edits are flat on every host; Think-SFT single mean is 209, noise control 209. |
| run-06/f2-m03 | 209 | [197, 221] | Theory: a random rank-8 edit gives nothing, so Think-SFT's cue score (209 mean of 4) is unchanged, give or take one-sample noise. |
| run-05/f2-m01 | 208 | [197, 219] | Random rank-8 edits carry no dial (flat at 158-167 on the base at every size), so Think-SFT stays at its one-sample level of about 209. |
| run-05/f2-m03 | 208 | [196, 220] | A random rank-8 subspace is not driven by math text (8-11x less), so it acts on nothing: Think-SFT stays at its one-sample level ~209 (random edits on the base flat at 158-167). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 208 | [196, 220] | A random rank-8 edit gets the same bf16 thresholding but has no finishing direction. Random edits were flat on the base at every size, so Think-SFT should stay at its single-sample level of about 201-212. |
| run-07/f2-m02 | 209 | [195, 223] | The theory credits the gain only to RL's top directions, which write the habit, so a random rank-8 edit leaves the Think-SFT host at its single-sample level of ~209. |
| run-03/f2-m02 | 208 | [196, 220] | Random directions carry no hazard (flat at every size on the base), so Think-SFT stays near its 209. |
| round-09/training-m06 | 209 | [197, 221] | Theory: random directions do not sit on the features math text drives (8-11x less drive), so a random rank-8 edit at 3x leaves Think-SFT at its 209 baseline (random edits on the base are flat at 158-167; the noise control on Think-SFT gave 209). |
| run-02/f2-m04 | 209 | [198, 220] | Theory: only edits that make Think-SFT finish change its score. A random rank-8 edit does not change finishing (random edits stay flat on the base, noise on Think-SFT gives 209), so it stays at Think-SFT's single-sample mean of 209. |
| run-05/f2-m04 | 209 | [196, 222] | Theory: a random rank-8 edit carries none of RL's late parts, so the score stays at Think-SFT's 16k level (209 mean; random edits on the base were flat at 158-167). |
| round-09/weights-m06 | 209 | [197, 221] | Theory: a random rank-8 edit is inert at any size (base random 158-167 flat across sizes; Think-SFT noise control 209), so the score stays at Think-SFT's one-sample level (201-219). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 209 | [197, 221] | A random rank-8 edit acts like a new seed on the same weights (flat on the base at every size), so it regresses to Think-SFT's pooled single-sample level of 209.0 on the 328, with 9-19 of scatter. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 209 | [197, 221] | Only the RL directions act as the finishing dial. A random rank-8 edit was flat at every size on the base, so Think-SFT should stay at its single-sample mean of 209. |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 209 | [196, 222] | Random edits are flat on the base dial and the noise control on Think-SFT scored 209, so the prior is Think-SFT's 209 with the hard328 one-draw SD of 7-9. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 208 | [197, 219] | Theory: a random edit adds no finishing weight, so abstentions and the score stay at Think-SFT's single (201-212, mean 209). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 209 | [197, 221] | A random edit leaves stopping alone (it was flat at every size on the base), so the count stays at Think-SFT's 209. |
| run-04/f2-m03 | 209 | [196, 222] | Only RL's directions carry the hazard logit; random rank-8 edits leave cap hits flat at every size (base 158-167), so Think-SFT stays at its 209 mean. |
| round-09/weights-m04 | 209 | [197, 221] | Theory: only the RL difference finishes, so a random edit leaves Think-SFT at its own level (209; noise control 209). |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 209 | [196, 221] | Random is inert, so this is Think-SFT one sample at 16k. |
| round-11/s4-b | 209 | [198, 220] | A random edit does not sharpen. |
| round-11/s6-b | 209 | [197, 221] | Random rank-8 at 3x is flat on the base: Think-SFT's 209. |

## t18 (work-30f0ed): How many of the 328 hard problems does the base model with both the Math and the Code RL directions added at 1.5x each answer right?

Unit: right answers of 328. Cell: {"model": "base + RL-Math top-8 directions at 1.5x + RL-Code top-8 directions at 1.5x", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> (2) one edit for two skills: base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 192 | [172, 209] | Math at 1.5x alone gives about 200; adding the Code finishing directions overshoots the dose the way the 2x edit did (190, 5 cap hits). |
| reader-2 | 190 | [170, 206] | Math at 1.5x alone gives 200 and the 2x Math edit drops to 190; adding Code at 1.5x overdoses finishing. |
| run-06/f2-m03 | 195 | [181, 209] | Theory: Math top-8 at 1.5x gives about RL's level (200.25), and Code's directions add finishing that pushes the total dose toward the too-early 2x regime (190), so slightly below 200. |
| run-05/f2-m01 | 188 | [171, 203] | Math and Code directions both write finishing, so 1.5+1.5 acts as a dose past 1.5x that closes hard solutions on guesses, like the 2x Math cell (190, 5 cap hits). |
| run-05/f2-m03 | 193 | [179, 207] | Math directions act in full on hard328 (1.5x alone ~200), Code directions add about half their in-domain effect via 0.22-0.26 overlap, so the sum behaves like Math at ~2x, where the base scored 190 (over-finishing). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 196 | [183, 209] | Math top-8 at 1.5 acts like RL's share (about 200 on hard328). Code's smaller delta needs a larger nominal size to act (theory), so at 1.5 it adds some extra finishing that pushes toward the over-finished 2x regime (190). |
| run-07/f2-m02 | 206 | [188, 224] | Math top-8 at 1.5x carries nearly all of the hard328 gain (164 -> ~204), and Code's directions on math carry about half as much on top. Both write finishing, so the total is capped near RL's 206 instead of the additive ~227. |
| run-03/f2-m02 | 188 | [172, 203] | Math and Code directions at 1.5x each add up to a hazard past the 1.5x Math point, so guesses close hard problems as at Math 2x (190, 5 cap hits). |
| round-09/training-m06 | 192 | [175, 207] | Math and Code top-8 directions overlap on shared early-layer input features, so adding both at 1.5x acts like a Math dose near 2x, which overshoots (190 on the base at 2x) rather than reaching 1.5x's ~200. |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | 193 | [180, 206] | Theory: Math and Code top-8 directions both carry finishing, so 1.5x+1.5x behaves like an overdose similar to Math at 2x (190, 5 cap hits) rather than Math 1.5x (200). |
| round-09/weights-m06 | 192 | [175, 208] | Theory: the edits add at their nominal doses, so Math 1.5x (~200) plus Code finishing directions overshoot toward the 2x regime (190, few cap hits); the result lands near the Math-alone level. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 192 | [177, 207] | The finishing dial adds up across both rewards' eight directions. Math at 1.5x (about 200) plus Code's finishing dose pushes past the optimum, like the 2x cell (190), and Code's top direction writes code form rather than boxes. |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 194 | [180, 208] | Structural prior: Math 1.5x (200.25 mean) plus orthogonal Code directions overshoots finishing, like Math 2x (190); one-draw SD of 7-9 plus prior uncertainty. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 195 | [182, 208] | Theory: Math plus Code finishing directions at 1.5x each overshoot like the 2x Math edit (190, 5 cap hits); the abstentions they remove become mostly wrong answers, so the score sits just under the 1.5x Math edit's 200. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 192 | [178, 206] | Two finishing edits at 1.5x add up to an oversized dose (about 2x), so word-string losses resemble the 2x cell (190). |
| run-04/f2-m03 | 188 | [172, 202] | Hazard logits add: Math 1.5x (-1.31) plus Code 1.5x (about -1.15) is like Math at 2x (5 cap hits, 190 right); the extra converted samples are right at low precision, with some early-stop loss. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 205 | [197, 216] | Math copy (200) plus Code's subspace, orthogonal to it, which adds Code-RL's small math transfer and no interference: about 205. |
| round-11/s4-b | 200 | [190, 211] | Math and Code reliability add on math only weakly; Math 1.5x level (200.25). |
| round-11/s6-b | 205 | [198, 215] | Code directions add no math stop-checking push, so the math dose stays at its 1.5x optimum (4-sample mean 200.25), plus a little from format. |

## t19 (work-30f0ed): How many of the 328 hard problems does the base model with both the Math and the Code RL directions added at 1x each answer right?

Unit: right answers of 328. Cell: {"model": "base + RL-Math top-8 directions at 1x + RL-Code top-8 directions at 1x", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> (2) one edit for two skills: base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 197 | [183, 210] | Math at 1x gives 192 and Code at 1x gives 178 on hard328; the two are nearly orthogonal and both push toward finishing, so a small gain over Math alone. |
| reader-2 | 196 | [182, 210] | Math at 1x gives 192 and Code at 1x about 178; combined acts like about a 1.5x Math edit. |
| run-06/f2-m03 | 196 | [183, 209] | Theory: Math top-8 at 1x scores 192 and the Code directions, worth about half the in-domain gain, add a little more finishing. |
| run-05/f2-m01 | 198 | [186, 210] | 1x Math (192) plus 1x Code finishing adds up to an effective dose near 1.5x, where the dial peaks (Math 1.5x averaged 200). |
| run-05/f2-m03 | 197 | [184, 210] | Math at 1x (192) plus Code at 1x transferring about half its effect, roughly Math at ~1.4x, near the 1.5x level of ~200. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 195 | [183, 207] | Math top-8 at 1x scored 192. The theory says Code's smaller delta loses more at 1x, so adding Code at 1x gives only a small extra gain. |
| run-07/f2-m02 | 201 | [187, 215] | Math top-8 at 1x carries two thirds of the 42-point gain (+28), and Code at 1x on math carries about half that (+14). Adding them gives ~206, shaded down for overlap: ~201. |
| run-03/f2-m02 | 198 | [185, 210] | Math and Code at 1x each sum to a hazard near Math 1.5x (about 200), so the count sits near the dial's peak. |
| round-09/training-m06 | 198 | [186, 210] | Math at 1x (192) plus partly overlapping Code directions (Code alone 178) sums to an effective dose between 1x and 1.5x on the shared features, so between 192 and 200. |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | 198 | [186, 210] | Theory: Math 1x (192) plus Code 1x adds more finishing, roughly like the Math 1.5x level (200 mean). |
| round-09/weights-m06 | 198 | [183, 212] | Theory: the nominal doses add, so Math 1x (192) plus Code 1x (178 alone) gives roughly a 1.5x-equivalent finishing dose (~200). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 197 | [183, 210] | Math top-8 at 1x (192) plus Code top-8 at 1x (Code alone 178) adds finishing dose to a total of about 1.5x Math, near the dial's optimum of about 200, with a small cost from Code's own answer form. |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 197 | [184, 210] | Structural prior between Math top-8 at 1x (192) and 1.5x (200), since the added Code directions push finishing further; hard328 one-draw SD. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 198 | [186, 210] | Theory: two 1x finishing edits add about the finishing weight of the 1.5x Math edit (200.25), so cap hits fall to ~25 and the score lands near it. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 196 | [183, 209] | The combined 1x+1x dose is near Math 1.5x, below the hazard range, so it lands near 200. |
| run-04/f2-m03 | 196 | [183, 209] | Math 1x (-0.55) plus Code 1x (-0.77) sums to about the Math 1.5x shift (about 25 cap hits), which scored a mean of 200; Code's directions add less correctness per finish, so a little below that. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 194 | [182, 206] | Math 1x (about 190) plus a small additive Code contribution. |
| round-11/s4-b | 198 | [188, 208] | Math 1x (192) plus a few points from Code's sharpening on math (Code 1x gave 178 vs base 164). |
| round-11/s6-b | 195 | [183, 206] | Math 1x (192) is below its optimum; Code 1x adds only format. |

## t20 (work-30f0ed): How many of the 328 hard problems does the control edit (base plus the Math RL directions plus random directions) answer right?

Unit: right answers of 328. Cell: {"model": "base + RL-Math directions + random directions (control)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> (2) one edit for two skills: base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 197 | [183, 210] | Random directions add nothing, so this should score like Math's directions alone (192 at 1x, 200 at 1.5x). |
| reader-2 | 198 | [185, 211] | Random directions add nothing, so equal to the Math directions alone (192-200 depending on size). |
| run-06/f2-m03 | 198 | [185, 211] | Theory: random directions add nothing, so the cell is about the Math top-8 edit alone (1x 192, 1.5x 200.25). |
| run-05/f2-m01 | 197 | [184, 209] | The random part carries no dial, so the cell equals the Math directions alone: 192 at 1x, 200 at 1.5x. |
| run-05/f2-m03 | 199 | [187, 211] | Random directions are not excited by math text and add nothing, so the cell equals the Math 1.5x edit alone (4-sample mean 200.25 on hard328). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 199 | [186, 210] | Random directions carry no finishing (flat dial), so the control should score like Math top-8 alone, about 192-203. |
| run-07/f2-m02 | 198 | [183, 213] | Random directions carry no habit, so the cell is the Math top-8 edit alone: 192 at 1x, ~204 at 1.5x. The scale is not stated, so the forecast sits between the two. |
| run-03/f2-m02 | 200 | [188, 212] | Random directions add no hazard, so the cell equals the Math 1.5x edit (mean of 4 samples 200.25). |
| round-09/training-m06 | 199 | [187, 211] | Random directions add nothing because they are off the features math text drives, so the control scores about the same as the Math top-8 edit alone (1.5x, mean of 4 samples 200). |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | 197 | [184, 210] | Theory: only the Math directions carry the late parts and random directions add nothing (flat), so this equals Math alone at 1x-1.5x (192-200). |
| round-09/weights-m06 | 199 | [186, 212] | Theory: the random part is inert, so the score equals the Math top-8 edit alone at nominal 1.5x (four-sample mean 200.25). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 199 | [187, 211] | Math directions plus a random (seed-like) edit pool with the 1.5x Math edit's 4-sample mean of 200.25, not the notable first draw of 203, minus a little for the extra perturbation. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 199 | [187, 211] | Random directions carry no finishing signal, so the control should score like Math's eight directions alone (about 200 at 1.5x). |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 199 | [186, 212] | Random directions are flat on the dial, so the prior is the Math-directions cell alone (192-200); hard328 one-draw SD. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 196 | [184, 208] | Theory: the random part adds no finishing weight, so the score follows the Math directions alone (192 at 1x, 200 at 1.5x). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 200 | [188, 212] | Random directions do not change stopping, so this equals the Math 1.5x edit (mean 200.25). |
| run-04/f2-m03 | 198 | [185, 211] | Random directions add no hazard logit, so the control equals Math's directions alone (1.5x: mean 200.25; 1x: 192). |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 199 | [188, 210] | Random is inert, so this is Math 1.5x, 200. |
| round-11/s4-b | 199 | [189, 209] | Random adds nothing; Math 1.5x. |
| round-11/s6-b | 197 | [185, 209] | Random adds nothing: the Math edit alone, 192-200. |

## t21 (work-30f0ed): How many HumanEval+ and MBPP+ problems does the base model with both the Math and the Code RL directions added at 1.5x each pass?

Unit: passed problems of HumanEval+/MBPP+. Cell: {"model": "base + RL-Math top-8 directions at 1.5x + RL-Code top-8 directions at 1.5x", "prompt": "not stated", "set": "HumanEval+/MBPP+", "n": "not stated", "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> (2) one edit for two skills: base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 393 | [374, 408] | Code at 1.5x alone passes 399 and at 2x 394; adding Math's directions pushes the finishing dose past the peak. |
| reader-2 | 392 | [370, 410] | Code at 1.5x alone gives 399 and Math at 1.5x gives 368; the combined edit stays near the Code edit, slightly overdosed. |
| run-06/f2-m03 | 391 | [374, 407] | Theory: Code top-8 at 1.5x reproduces RL-Code (399 of 538); the added Math finishing directions push toward the over-committed 2x regime (394), so slightly lower. |
| run-05/f2-m01 | 391 | [374, 405] | On code the dial is saturated near 1.5x-2x (Code 1.5x 399, 2x 394), so the combined overdose sits just below the peak. |
| run-05/f2-m03 | 391 | [376, 405] | Code directions act in full on code (399 at 1.5x) and Math adds about half its effect (Math alone on code +37 over random vs Code +68), so the sum acts like Code at ~2x+ (394), saturated near RL-Code 401. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 395 | [380, 408] | Code top-8 at 1.5 is near its peak (theory: Code peaks at a larger nominal size); it scored 399 alone, and the Math directions add little on top of an already-finishing model. |
| run-07/f2-m02 | 398 | [382, 414] | On code, Code top-8 at 1.5x carries nearly all of RL-Code's gain (317 -> ~399), and Math's half share would push past RL, so the forecast is capped at about RL-Code's 401. |
| run-03/f2-m02 | 390 | [375, 405] | Code is in-domain: the summed hazard is past saturation (Code 2x 394, 0 cap hits), so a few guesses come in just under Code 1.5x's 399. |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | 392 | [377, 406] | Theory: both edits carry finishing, so on code the result is near the Code-directions overdose level (2x 394, 1.5x 399; RL-Code 401). |
| round-09/weights-m06 | 395 | [378, 410] | Theory: the nominal doses add, so Code top-8 1.5x (399) plus Math's directions acts like a larger finishing dose (Code 2x 394). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 391 | [374, 406] | Code's eight directions are the finishing dial on code (399 at 1.5x, 394 at 2x). Adding Math's eight adds more finishing past the optimum, so slightly below 399. |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 395 | [378, 412] | Structural prior from the code dial: Code top-8 at 1.5x 399 (Math directions add little on code), with sampling noise on 538 problems. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 390 | [372, 405] | Theory: code cap hits and missing blocks are already gone at Code 1.5x (399), and the extra Math finishing weight only overshoots, like Code 2x (394). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 392 | [375, 408] | The combined oversized dose overshoots like Code 2x (394) rather than Code 1.5x (399). |
| run-04/f2-m03 | 392 | [375, 405] | On code the base fails by not stopping; Code 1.5x already brings cap hits to about 0 (399), and the added Math logit overshoots as at Code 2x (394), so no further gain. |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 402 | [393, 413] | Code copy (399) plus orthogonal Math directions, whose shared finishing part is already saturated (0 cap hits): about RL-Code level, 401-403. |
| round-11/s4-b | 403 | [393, 416] | Code (399) and Math (368, +37 over random on code) sharpening add on code's solvable problems, reaching RL-Code or above. |
| round-11/s6-b | 397 | [385, 409] | Code format channel saturated, and the Math checking push is idle on code: plateau at 394-399. |

## t22 (work-30f0ed): How many HumanEval+ and MBPP+ problems does the base model with both the Math and the Code RL directions added at 1x each pass?

Unit: passed problems of HumanEval+/MBPP+. Cell: {"model": "base + RL-Math top-8 directions at 1x + RL-Code top-8 directions at 1x", "prompt": "not stated", "set": "HumanEval+/MBPP+", "n": "not stated", "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> (2) one edit for two skills: base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 390 | [372, 405] | Code at 1x passes 386 and Math's directions add a little finishing on code (368 vs 331 at 1.5x). |
| reader-2 | 392 | [372, 408] | Code at 1x gives 386; Math directions add a little finishing. |
| run-06/f2-m03 | 390 | [373, 406] | Theory: Code top-8 at 1x gives 386, and the Math directions (about half the gain off-domain) add a few problems. |
| run-05/f2-m01 | 392 | [377, 405] | Code 1x (386) plus Math's finishing directions takes the dose to near the code peak of about 399. |
| run-05/f2-m03 | 394 | [380, 407] | Code at 1x (386) plus Math's half-strength transfer, roughly Code at ~1.4-1.5x (399). |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 388 | [374, 401] | Code top-8 at 1x lost more to thresholding (theory) and scored 386. Math at 1x adds a little finishing. |
| run-07/f2-m02 | 394 | [378, 410] | On code, Code top-8 at 1x carries two thirds of the 84-point gain (+56), and Math at 1x carries about half that (+28). Additive is ~401; shaded for overlap: ~394. |
| run-03/f2-m02 | 395 | [380, 408] | Code 1x (386) plus Math 1x adds hazard toward the Code 1.5x point (399). |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | 391 | [376, 405] | Theory: Code top-8 at 1x (386) plus Math's finishing directions (Math 1.5x alone gives 368 on code) push toward the Code 1.5x level of 399. |
| round-09/weights-m06 | 392 | [375, 407] | Theory: the nominal doses add, so Code 1x (386) plus Math 1x (Math 1.5x alone gives 368 on code) lands near Code 1.5x (399). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 391 | [375, 405] | Code's eight at 1x (386) plus Math's eight (which alone add +6.9 over random on code) adds finishing dose toward Code's 1.5x level (399). |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 390 | [373, 407] | Structural prior: Code top-8 at 1x 386, plus a small Math-direction contribution; sampling noise on 538 problems. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 389 | [373, 404] | Theory: summed 1x finishing weights are about Code 1x to 1.5x, so passed problems land near 386-399. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 390 | [374, 405] | A moderate combined dose with no degeneration lands near Code 1x (386) plus a little from the Math directions. |
| run-04/f2-m03 | 395 | [380, 408] | Summed logits of Code 1x (386, 9 cap hits) and Math 1x convert the remaining unfinished code answers, landing near Code 1.5x (399). |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 391 | [379, 403] | Code 1x (386) plus a few points of Math's finishing part on code. |
| round-11/s4-b | 397 | [386, 408] | Code 1x (386) plus part of Math's code gain. |
| round-11/s6-b | 390 | [377, 403] | Code 1x 386, plus Math's shared format part. |

## t23 (work-30f0ed): How many HumanEval+ and MBPP+ problems does the control edit (base plus the Math RL directions plus random directions) pass?

Unit: passed problems of HumanEval+/MBPP+. Cell: {"model": "base + RL-Math directions + random directions (control)", "prompt": "not stated", "set": "HumanEval+/MBPP+", "n": "not stated", "sampling": "not stated", "samples": "not stated", "grader": "not stated"}

> (2) one edit for two skills: base + Math + Code directions at (1.5,1.5), (1,1), control Math + random, on hard328 and HumanEval+/MBPP+

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 362 | [344, 380] | Math's directions at 1.5x pass 368 on code against random's 331; random directions add nothing, and the size here may be 1x. |
| reader-2 | 366 | [345, 385] | Math at 1.5x on code gives 368; random adds nothing. |
| run-06/f2-m03 | 367 | [350, 384] | Theory: another reward's directions give about half the gain (Math on code measured 368 vs base 317 and RL-Code 401), and random adds nothing. |
| run-05/f2-m01 | 364 | [344, 382] | The random part adds nothing, so this is Math's directions on code alone: 368 at 1.5x, a little lower if the size is 1x. |
| run-05/f2-m03 | 368 | [353, 383] | Random adds nothing, Math directions transfer to code at about half the in-domain effect: the measured Math 1.5x on code, 368 of 538. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 366 | [350, 382] | Math directions alone on code scored 368 at 1.5x, and random directions add nothing. |
| run-07/f2-m02 | 357 | [339, 375] | Random directions add nothing. Math directions on code carry about half of their own-domain share: +28 at 1x, +42 at 1.5x over the cued base's 317. The scale is not stated, so the forecast is ~357. |
| run-03/f2-m02 | 368 | [352, 384] | Random adds no hazard, so this equals Math 1.5x on code (368). |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | 366 | [350, 382] | Theory: only Math's finishing directions act on code (Math 1.5x on code 368; random edits flat at 331 vs base 317). |
| round-09/weights-m06 | 368 | [352, 384] | Theory: the random directions are inert, so the score equals Math's 8 directions on code at 1.5x (368). |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 368 | [356, 380] | Pools with the near-identical cell, base + Math directions at 1.5x on code (368 of 538), since the random part acts as a seed-like perturbation; single-draw scatter about 7. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 366 | [350, 382] | Random directions do nothing, so the control should score like Math's eight directions alone on code (368 of 538). |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 368 | [350, 386] | Random directions are flat (random 1.5x 331), so the prior is Math top-8 at 1.5x on code (368); sampling noise on 538 problems. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 362 | [340, 380] | Theory: only the Math directions add finishing weight on code (368 at 1.5x) and the random part adds none. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 366 | [350, 382] | The random part does nothing, so this equals Math 1.5x on code (368). |
| run-04/f2-m03 | 365 | [348, 382] | Random directions add no hazard, so the control equals Math's directions alone on code (1.5x: 368). |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 366 | [350, 382] | Math 1.5x on code (368); random is inert. |
| round-11/s4-b | 368 | [353, 383] | Math 1.5x on code scored 368; random adds nothing. |
| round-11/s6-b | 366 | [350, 381] | Math directions on code 368; random adds nothing. |

## t24 (work-8b4030): How many of the 328 hard problems does Think-SFT plus twice the RL-Math weight difference get right by majority vote over its 4 samples (Think-SFT's vote over 4 is 241)?

Unit: right answers of 328. Cell: {"model": "M(2) = Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "not stated (seeds 3,000,000 / 3,100,000 / 3,200,000 / 3,300,000)", "samples": 4, "grader": "not stated (majority vote over 4)"}

> hard328 samples 3-4 for the vote over 4

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 246 | [239, 253] | M(2)'s vote over its 3 samples (234/229/237) is 246; a 4th sample adds ties and moves it little. |
| reader-2 | 247 | [239, 255] | M(2) vote over 3 is already 246 and Think-SFT's vote over 4 is 241; a fourth sample adds about 0-3. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 245 | [237, 253] | The 2x dial in M(2) raises right answers per sample (234/229/237), so the vote over 4 lands near its vote over 3 (246), above Think-SFT's 241. |
| run-05/f2-m03 | 247 | [239, 255] | Full in-domain effect of the transplant persists across samples (234/229/237, vote over 3 = 246), so the vote over 4 lands near 246-248, above Think-SFT's 241. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 247 | [240, 254] | A large merge is realized at its nominal size (theory), so M(2) reproduces its samples (234/229/237, vote over 3 = 246). A fourth sample moves the vote little. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 247 | [239, 255] | The higher hazard turns abstentions into finished answers, some of them wrong, which dilutes the vote: the vote over 3 was 246 and a fourth sample adds about 0-2. |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | 246 | [239, 253] | Theory: the RL difference makes Think-SFT finish, so vote gains shrink. M(2)'s singles average about 233 and its vote over 3 is 246, so a fourth sample adds about 0. The vote gain is about +13, against Think-SFT's +32. |
| run-05/f2-m04 | 247 | [239, 255] | Theory: M(2) carries RL's late finishing plus error-reducing parts on top of Think-SFT, so its vote beats Think-SFT's 241; samples 234/229/237 give a vote over 3 of 246, plus a fourth sample. |
| round-09/weights-m06 | 247 | [240, 254] | Theory: M(2)'s samples share one nominal-dose mean (234/229/237, vote over 3 = 246); a 4th sample barely moves the vote. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | 247 | [241, 253] | Theory: a fourth sample, an independent draw near M(2)'s mean of about 233, flips only the few split problems, so the vote over 4 stays near the vote over 3 (246), about +1 as for Think-SFT (votes over 3 of 231-241, vote over 4 of 241). |
| round-09/grader-m04 | 247 | [240, 254] | Vote clause: M(2) abstains less than Think-SFT, so its vote gains little over single samples; a 4th sample adds about 1 to the vote over 3 of 246. |
| round-09/grader-m01 | 247 | [240, 254] | Vote over the pooled samples (234/229/237 plus a fourth near the pooled 233): its vote over 3 is already 246, and a fourth sample moves the vote only a few problems. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | 247 | [240, 253] | Vote gain scales with cap share times precision. M(2) caps less (about 16 %) and is less precise (about 72 %) than Think-SFT, so its vote gains less over its single mean of about 233. The vote over 3 is already 246, so the fourth sample adds about 1. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | 246 | [239, 252] | The theory says the vote has mostly levelled off by 3 or 4 samples: a 4th sample settles only the ties. So M(2)'s vote over 4 should stay near its vote over 3 (246, singles 234/229/237), above Think-SFT's 241. |
| run-08/f2-m01 | 247 | [239, 255] | The vote over the three stored M(2) samples (234/229/237) is 246; a fourth unselected draw adds little, and Think-SFT's 3-to-4 vote moved 0-10. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | 247 | [240, 254] | 'More samples move only precision of finished answers': a 4th sample with M(2)'s unchanged length distribution adds about one vote to its vote over 3 (246). |
| round-09/grader-m02 | 247 | [240, 254] | Theory: M(2)'s finishing weight cuts abstentions, so its vote gains less over its singles (233) than Think-SFT's near-pass@4 vote; the vote over 3 is 246, so a 4th sample adds about 1. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | 243 | [236, 250] | Theory: M(2) has few cap hits, so lone right answers face finished wrong singletons; at even k=4 the 2-2 and 1-1-1-1 ties that k=3 avoided come back and are lost about half the time, so the vote stays at or just below its vote over 3 (246) rather than climbing toward pass@4. |
| run-03/f2-m05 | - |  | theory says nothing |
| run-04/f2-m03 | - |  | theory says nothing |
| round-09/weights-m04 | 246 | [238, 253] | Theory: the delta finishes sound work but lowers precision, so the vote gains less over singles than Think-SFT's abstaining vote does; vote over 3 is already 246 (singles 234/229/237). |
| round-09/sampling-m01 | 247 | [239, 255] | The 4th sample is a new independent draw around M(2)'s mean of about 233. Adding it to the vote over 3 (246) changes the vote by roughly 0 to +2, as Think-SFT's votes over 3 (231-241) did against its vote over 4 (241). |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t25 (work-8b4030): How many of the 500 MATH-500 problems does Think-SFT plus twice the RL-Math weight difference answer right in one sample?

Unit: right answers of 500. Cell: {"model": "M(2) = Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "MATH-500", "n": 500, "sampling": "not stated", "samples": 1, "grader": "not stated"}

> MATH-500 1 sample

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 466 | [456, 475] | Think-SFT plus the RL change at a=1 scores 467 on MATH-500 and Think-SFT alone 457-462; a=2 should be about the same. |
| reader-2 | 466 | [456, 475] | Think-SFT + 1x scored 467 on MATH-500 and Think-SFT singles are 457-462; 2x is about the same. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 466 | [457, 474] | MATH-500 has few unfinished answers, so the extra closing at 2x changes little from a=1's 467 (Think-SFT 457-462). |
| run-05/f2-m03 | 468 | [458, 477] | The RL-Math change acts in full on MATH-500 too: M(1) scored 467 and Think-SFT 457-462, so M(2) one sample ~468 near the ceiling. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 466 | [457, 474] | Large merges act at their nominal size (theory). M(1) scored 467 and Think-SFT 454-462 on MATH-500, so M(2) should sit near the a=1 level. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 466 | [457, 474] | MATH-500 has few cap hits to convert and right-of-finished stays roughly flat, so a=2 sits near a=1's 467 and Think-SFT's 454-462. |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | 466 | [458, 474] | Theory: making Think-SFT finish raises its single score, but on MATH-500 it caps only about 24 times, so there is little room. Expect M(2) near the a=1 result (467), slightly above Think-SFT's single-sample range (457-462). |
| run-05/f2-m04 | 466 | [457, 474] | Theory: the transplant from final weights carries the late parts; Think-SFT + 1x gave 467 and Think-SFT cue singles give 457-462, so a=2 lands near 466. |
| round-09/weights-m06 | 467 | [457, 477] | Theory: the transplant behaves at its nominal dose, so M(2) on MATH-500 sits near M(1)'s 467 and above Think-SFT's 457-462. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | - |  | theory says nothing |
| round-09/grader-m01 | 467 | [459, 475] | Near-ceiling MATH-500 cells pool: the transplant at a=1 scored 467, and Think-SFT's singles are 457-462; with 5-7 per 500 of seed scatter. |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 466 | [456, 476] | Structural prior from the neighbouring transplant a=1 (467) and Think-SFT cue singles (454-462); the theory's 5-6 SD on MATH-500. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 466 | [458, 474] | Theory: finishing weight turns some of Think-SFT's ~24 MATH-500 cap hits into answers, so the single rises a little above Think-SFT's 457-462 (a=1 scored 467). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 465 | [455, 474] | A 2x edit's late-degeneration hazard barely touches short MATH-500 traces, so this stays near a=1's 467. |
| run-04/f2-m03 | 466 | [457, 474] | On MATH-500 Think-SFT has about 24 cap hits; the RL delta at 2x raises the hazard and converts most of them at low precision, adding a few problems to Think-SFT's 457-462 (a=1 scored 467). |
| round-09/weights-m04 | 466 | [458, 474] | Theory: the delta finishes part of Think-SFT's roughly 24 MATH-500 cap hits per sample (singles 457-462; a=1 gave 467), limited by how much of that cut work was sound. |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t26 (work-8b4030): How many of the 328 hard problems does Think-SFT plus twice the RL-Math weight difference answer right at a 32,768-token cap, one sample with seed 3,000,000 (Think-SFT alone gets 230 there)?

Unit: right answers of 328. Cell: {"model": "M(2) = Think-SFT + 2 x (RL-Math - base)", "prompt": "not stated", "set": "hard328", "n": 328, "sampling": "T not stated, top-p not stated, token cap 32,768, seed 3,000,000", "samples": 1, "grader": "not stated"}

> M(2) at cap 32,768 on hard328, seed 3,000,000

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 243 | [231, 254] | This seed scored 234 at 16k; about 50 cap hits at roughly a 20-25% late-finish rate add about 10. |
| reader-2 | 239 | [228, 250] | This seed scored 234 at 16k; 32k finishes some of its about 35 cap hits, against Think-SFT's 230 at this seed. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | 241 | [229, 252] | Same reasoning as t02: from this seed's 234 at 16k, the dial-closed M(2) gains less from 32k than Think-SFT (230 here) and keeps a modest correctness edge. |
| run-05/f2-m03 | 245 | [234, 256] | M(2) at this seed scored 234 at 16k; the full in-domain effect is kept and the 32k cap finishes ~a fifth of its ~75 cap hits, against Think-SFT's 230 at the same seed. |
| run-02/f2-m01 | 236 | [225, 247] | Theory: long hard328 solutions mostly fit in 16k for a model that finishes, so M(2) at 32k gains only a few late finishes over its 16k level (229-237). |
| run-05/f2-m06 | 242 | [231, 253] | Same reasoning as t02: M(2) is realized at nominal size, about 233 at 16k, and the 32k cap adds about 10 right answers from its roughly 40 cap hits. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 240 | [231, 249] | This seed's 16k score was 234; the remaining cap hits finish past 16k, a few right, so the delta mostly saves tokens with a small gain over Think-SFT's 230. |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | 241 | [230, 252] | Theory: the 32k cap turns M(2)'s capped samples into answers that are mostly wrong. Expect a modest rise over its 16k score for this seed (234) and mean (233.3), about +7, less than Think-SFT's +22 (230 at 32k). |
| run-05/f2-m04 | 243 | [232, 254] | Theory: M(2) already finishes because it carries the finishing directions, so the 32k cap adds about 9 to this seed's 234 at 16k, versus Think-SFT going from 207 to 230. |
| round-09/weights-m06 | 240 | [229, 251] | Theory: same nominal-dose mean as the 16k seed-3,000,000 sample (234), plus a cap-32k gain smaller than Think-SFT's (+23) because M(2) has fewer cap hits. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 241 | [229, 253] | Cap-raise clause: M(2)'s roughly 54 cap hits yield about 15 % right when extended (mostly unfinished or guessed), so the 16k level of about 233 plus about 8. |
| round-09/grader-m01 | 244 | [232, 256] | This seed drew 234 at 16k, near the pooled 233.3; adding about 10 right answers from finishing the cut answers at 32k, with 9-19 of draw scatter. |
| round-09/grader-m06 | 245 | [234, 256] | Theory: the 16k run at seed 3,000,000 scored 234; raising the cap to 32k adds about 1/5 of M(2)'s ~54 unfinished cap hits (between Think-SFT's 1/4 and RL's 1/10), so +11. |
| round-09/stopping-m01 | 243 | [233, 252] | Cap clause: one sample gains from the longer cap. M(2) at 16k is about 233 with about 54 cap hits, and roughly 20 % of the late answers are right, so +9 or 10. That is just above the owner's 240 threshold. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 242 | [229, 255] | M(2) 16k mean (233; this seed's stored draw 234) plus a cap-32k finishing gain of about +8 scaled from Think-SFT's cap-hit conversion; hard328 one-draw SD of 7-9. |
| round-09/sampling-m05 | 243 | [232, 254] | Theory: same as t02 for seed 3,000,000 (16k sample 234): ~54 cut samples finish at M(2)'s long-answer rate (~20 %), adding ~+9-10. |
| round-09/stopping-m04 | 243 | [232, 254] | 'A cut answer scores zero': M(2)'s 234 at 16,384 for this seed plus about a fifth of its ~54 cut answers finishing right at 32,768 gives ~243 (Think-SFT 230). |
| round-09/grader-m02 | 246 | [237, 255] | Theory: a higher cap turns M(2)'s remaining abstentions into mostly wrong answers, so it adds about 12 to the same seed's 16k score of 234, a smaller gain than Think-SFT's +23. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 241 | [231, 250] | As in t02, the 32,768 cap recovers only part of M(2)'s cap hits because late traces degenerate: about +7 on 234 at this seed. |
| run-04/f2-m03 | 243 | [231, 254] | Survival at the doubled cap: this seed scored 234 at 16,384 with about 54 cap hits; letting them run to 32,768 converts about 20% of them, so about +9. |
| round-09/weights-m04 | 231 | [221, 241] | Theory: no added correctness, and at 32k Think-SFT's sound cut work is already finished, so M(2) is about Think-SFT's 230 at this seed. |
| round-09/sampling-m01 | 241 | [230, 252] | This is a new draw of the same arm as t02, so by the theory it lands around the arm mean (16k mean 233.3 plus about 8 from the longer cap), not near Think-SFT's stored 230. The interval is the theory's sd of 6-9 on the 328. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | 246 | [236, 256] | Theory: RL's delta leaves ~54 cuts at 16k (result-3387ce) and extra budget converts about a quarter of them on hard328 (result-c8b994), so seed 3,000,000's 16k score 234 + ~12 = 246, above Think-SFT's 230. |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |

## t27 (work-290625): How many of the 500 MATH-500 problems does the base model with its top-8 RL-Math directions added at 2x answer right with the cue at T 1.0, grader v3 (the 1.5x edit scored 456)?

Unit: right answers of 500. Cell: {"model": "base Olmo-3-1025-7B + top-8 RL-Math directions per matrix at 2x (cell m29)", "prompt": "cue", "set": "MATH-500", "n": 500, "sampling": "T 1.0, top-p not stated, token cap not stated, seed 3000000", "samples": "not stated", "grader": "v3"}

> Cell m29: base + top-8 RL-Math directions at 2x, cue, MATH-500 n 500, T 1.0, v3

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 449 | [437, 459] | 1.5x scored 456; at 2x hard328 fell from 203 to 190 and code from 399 to 394, so expect a small drop on easier MATH-500. |
| reader-2 | 448 | [435, 460] | The 1.5x edit gave 456; on hard328 2x lost 13 against 1.5x as right-of-finished fell, and MATH-500 has few cap hits left to gain. |
| run-06/f2-m03 | 446 | [433, 458] | Theory: 2x commits too early; on hard328 2x lost about 13 against 1.5x (190 vs 203), and on easier MATH-500 the 1.5x edit's 456 drops by fewer points. |
| run-05/f2-m01 | 447 | [435, 458] | Past 1.5x the dial closes unfinished solutions on guesses (on hard328, 203 at 1.5x fell to 190 at 2x); on the easier MATH-500 the loss from 1.5x's 456 is smaller. |
| run-05/f2-m03 | 450 | [438, 460] | In-domain the top-8 edit acts in full, so 2x overshoots on MATH-500 as on hard328 (203 to 190 from 1.5x to 2x), but less on easy problems: slightly below the 1.5x cell's 456. |
| run-02/f2-m01 | - |  | theory says nothing |
| run-05/f2-m06 | 448 | [436, 459] | Effective size grows faster than nominal (theory), so 2x overshoots RL's top-8 share; on hard328 it fell from 203 to 190 by over-finishing. MATH-500's shorter problems lose less, so slightly below the 1.5x score of 456. |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | 448 | [436, 460] | Past about 1.5x the hazard closes hard problems with guesses (hard328: 203 -> 190), but MATH-500 has fewer long problems, so 2x sits a little below 1.5x's 456. |
| round-09/training-m06 | 448 | [435, 460] | With the cue prefilled, the top-8 directions add only through the early/middle-layer features; at 2x they overshoot (on hard328, 190 vs 203 at 1.5x), but the short MATH-500 problems lose less, so a little below the 1.5x edit's 456. |
| run-02/f2-m04 | - |  | theory says nothing |
| run-05/f2-m04 | 449 | [437, 460] | Theory: the top-8 are finishing directions, and past about 1.5x they over-finish (hard328 went from 203 at 1.5x to 190 at 2x), so 2x sits a little below the 1.5x MATH-500 score of 456. |
| round-09/weights-m06 | 448 | [436, 459] | Theory: the 2x edit acts at nominal 2x (stored hard328 2x edit: right 190 vs 203 at 1.5x, precision falling), so MATH-500 drops a few problems from the 1.5x edit's 456. |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 451 | [440, 461] | Difficulty-mix clause: on MATH-500 few answers pass 16k, so the 2x edit's switch from abstaining to guessing (which cost 13 on hard328) costs only a few problems against the 1.5x cell's 456. |
| round-09/grader-m01 | - |  | theory says nothing |
| round-09/grader-m06 | - |  | theory says nothing |
| round-09/stopping-m01 | - |  | theory says nothing |
| round-09/training-m05 | 448 | [436, 459] | At 2x the eight-direction dial has removed nearly all cap hits (5 on hard328) while precision drops (190 vs 203 on hard328). MATH-500 has few cap hits left to convert, so the edit should land a little under the 1.5x score of 456. |
| round-09/sampling-m06 | - |  | theory says nothing |
| run-08/f2-m01 | 448 | [436, 460] | Structural prior from the 1.5x cell (456) and the hard328 dial, where 2x falls below 1.5x as right-of-finished drops; the theory's MATH-500 SD of 5-6. |
| round-09/sampling-m05 | - |  | theory says nothing |
| round-09/stopping-m04 | - |  | theory says nothing |
| round-09/grader-m02 | 450 | [440, 460] | Theory: the base abstains little on MATH-500, so going from 1.5x (456) to 2x finishing weight only forces wrong finished answers (hard328 fell from 203 to 190 at 2x). |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | - |  | theory says nothing |
| run-03/f2-m05 | 445 | [432, 456] | 2x enters the theory's word-string range, losing answers against 1.5x's 456 (hard328 lost 13 at 2x); short MATH-500 traces limit the loss. |
| run-04/f2-m03 | 448 | [436, 459] | Dose multiplies the hazard: at 2x cap hits go to about 0, but MATH-500 has few unfinished samples left after 1.5x (456), so the main effect is early stops cutting precision, as on hard328 (203 to 190). |
| round-09/weights-m04 | - |  | theory says nothing |
| round-09/sampling-m01 | - |  | theory says nothing |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | - |  | theory says nothing |
| round-11/s2-b | 455 | [445, 464] | A 2x copy of RL's policy stays at the RL level (457-463), like the 1.5x edit's 456. |
| round-11/s4-b | 452 | [442, 461] | Just past the optimum dose at 1.5x (456); a small loss. |
| round-11/s6-b | 438 | [424, 446] | The math overshoot is not length-specific: hard328 lost 6.4 % from 1.5x to 2x (203 -> 190), and the same skipped checking on MATH-500 takes 456 down by about 4 %. |

## t28 (work-dc9359): How many fresh2026 problems (2026 contest problems) does Think-SFT with the cue get right by majority vote over 4 samples at a 32,768-token cap (75 of 136 at the 16,384 cap)?

Unit: right answers on fresh2026 (vote over 4). Cell: {"model": "Think-SFT (allenai/Olmo-3-7B-Think-SFT)", "prompt": "cue", "set": "fresh2026", "n": "not stated", "sampling": "T not stated, top-p not stated, token cap 32,768", "samples": 4, "grader": "not stated (majority vote over 4)"}

> fresh2026 (4 samples), each answer scored at 16,384 and 32,768 from the same text

| forecaster | value | 90 % interval | reason |
|---|---|---|---|
| reader-1 | 81 | [73, 89] | Think-SFT's fresh2026 vote is 75 at 16k with about 46% cap hits per sample; on hard328 32k lifted the vote by 6 of 328, and fresh2026 has more cut answers. |
| reader-2 | 79 | [72, 86] | 75 at 16k; Think-SFT has 46% cap hits on fresh2026, more than on hard328 where 32k moved the vote from 238 to 244. |
| run-06/f2-m03 | - |  | theory says nothing |
| run-05/f2-m01 | - |  | theory says nothing |
| run-05/f2-m03 | - |  | theory says nothing |
| run-02/f2-m01 | 81 | [73, 89] | Theory: hard contest problems need long solutions, so doubling the cap finishes some of Think-SFT's many cut answers (46% cap hits); hard328's vote rose 238 to 244, so add about 6 to the 75 at 16k. |
| run-05/f2-m06 | - |  | theory says nothing |
| run-07/f2-m02 | - |  | theory says nothing |
| run-03/f2-m02 | - |  | theory says nothing |
| round-09/training-m06 | - |  | theory says nothing |
| run-02/f2-m04 | 78 | [71, 85] | Theory: the 32k cap turns Think-SFT's many fresh2026 abstentions (46% capped) into mostly wrong, scattered answers that tie with or outvote lone right samples. Single scores rise, but the vote gains little: on hard328 the 32k cap added +6 to the vote against +22 per sample, so expect 75 to about 78. |
| run-05/f2-m04 | - |  | theory says nothing |
| round-09/weights-m06 | - |  | theory says nothing |
| round-09/sampling-m03 | - |  | theory says nothing |
| round-09/training-m04 | - |  | theory says nothing |
| run-04/f2-m04 | - |  | theory says nothing |
| round-09/grader-m04 | 78 | [73, 83] | Theory directly: on fresh2026, which is harder, a cap raise and a vote yield less per abstention than on hard328 (+6 vote there), so about +3 over the 75 at 16k. |
| round-09/grader-m01 | 80 | [73, 87] | Pooled from the near-identical hard328 cap-32k vote cell, where rescoring the same text raised the vote 238 to 244 (about a quarter of the singles' gain); fresh2026 has more cap hits, so 75 rises by about 5, with the vote's scatter on 136 problems. |
| round-09/grader-m06 | 81 | [74, 88] | Theory's yield: 1/4 of Think-SFT's ~62 fresh2026 cap hits per sample gives about +15 right per sample. The vote passes on only part of that; on hard328 about 0.27 got through (+22 per sample became +6 in the vote), so 75 + ~6. |
| round-09/stopping-m01 | 78 | [72, 85] | Last clause: a vote gains far less from a longer cap than one sample does (hard328 vote +6 against single +22). On fresh2026 the cap share is high (46 %) but late answers are mostly wrong, so the vote moves only about +3 from 75. |
| round-09/training-m05 | - |  | theory says nothing |
| round-09/sampling-m06 | 80 | [73, 87] | The theory says the near-zero block caps votes on hard sets. On hard328, the 32k cap lifted single samples by about 22 but the vote over 4 by only about 6 (238 to 244). Applied to fresh2026's 75 at 16k, that gives a small gain of about 5. |
| run-08/f2-m01 | 80 | [73, 87] | Vote over 4 at 16k is 75; the 32k gain is scaled from hard328's vote (+6) and the higher fresh2026 cap-hit share; the theory's fresh2026 SD of about 3, partly cancelled by the vote. |
| round-09/sampling-m05 | 81 | [74, 88] | Theory: Think-SFT's 45.6 % cut samples on fresh2026 finish at 32k at its long-answer rate on hard problems (~20 %, ~+12 per sample), and as on hard328 (vote 238->244) about a third of that reaches the vote, more here because many problems had no finished vote. |
| round-09/stopping-m04 | 81 | [74, 88] | 'A cut answer scores zero': Think-SFT cuts ~46 % of fresh2026 samples at 16,384, and at 32,768 some finish right; under the vote this adds about 6 to its 75, as on hard328 (vote 238 -> 244). |
| round-09/grader-m02 | 79 | [72, 86] | Theory: at 32k Think-SFT's 46% abstentions become finished answers, mostly wrong, so singles rise but the vote gains less; on hard328 the vote rose only +6 against singles' +22, so 75 rises about 4. |
| round-09/training-m03 | - |  | theory says nothing |
| round-09/grader-m05 | 77 | [71, 83] | Theory: at the 32k cap, answers that abstained at 16k become finished wrong singletons, and tied lone right answers lose about half the time, so most of the single-sample gain from finishing is lost in the vote: only a small rise over 75, as on hard328 (238 to 244). |
| run-03/f2-m05 | 80 | [74, 87] | A higher cap lets many of fresh2026's frequent cap hits finish, but script-switched late traces rarely end right, so the vote gains only about 5 over 75. |
| run-04/f2-m03 | 81 | [74, 88] | Fresh contests fail by not stopping (46% cap hits at 16,384): doubling the cap lets these survivors finish at low precision (about 20%), and the vote gains roughly a quarter of the single-sample gain (hard328 vote 238 to 244), so 75 + about 6. |
| round-09/weights-m04 | 80 | [74, 87] | Theory's premise that Think-SFT's cut work is sound (result-c8b994): finishing it at 32k recovers about what the finishing delta gave on fresh2026 (vote 75 to 83), shrunk as the hard328 vote shrank (+6). |
| round-09/sampling-m01 | 82 | [74, 90] | These are the same 4 independent draws, rescored. Each sample's 62 or so cap hits partly finish right past 16k, so the vote moves up from 75; the gain is larger than hard328's +6 because the share of cap hits is higher. The spread is that of a vote over 4 draws on 136 problems. |
| round-09/training-m01 | - |  | theory says nothing |
| round-09/training-m02 | 78 | [73, 83] | Theory: on 2026 problems fewer than a quarter of Think-SFT's ~62 cuts per sample convert, and late finishes are scattered so in a vote they seldom beat an existing right answer (hard328 vote gained 6 vs 22 for singles), so the vote over 4 rises only ~3 from 75. |
| round-11/s2-b | - |  | no forecast |
| round-11/s4-b | - |  | no forecast |
| round-11/s6-b | - |  | no forecast |
