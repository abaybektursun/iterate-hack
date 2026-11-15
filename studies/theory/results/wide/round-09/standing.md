# Standing, round-09

From run-02, run-03, run-04, run-05, run-06, run-07, run-08, cells-01. Gain per number: log density of the forecast minus the equal mixture of the two readers, clipped to [-3, 3] nats, at most 0 when the measured value is outside the forecast's own 90 % interval. Carried: total above 0 on 3 or more scored numbers; graveyard: at or below -2 on 3 or more.

| mechanism | family | scored | inside | total gain | state | statement |
|---|---|---|---|---|---|---|
| run-06/f2-m03 | training | 5 | 5 | +5.56 | carried | An outcome reward pays only for a gradable final answer, so its consistent gradient piles into a few singular directions that make the model complete the task i |
| run-02/f2-m01 | run-02 | 6 | 4 | +5.10 | carried | The autobench agent works under a fixed generation time per experiment, so it buys votes by shortening each sample (its best config: 10 samples at about 1,100 t |
| run-05/f2-m03 | weights | 5 | 5 | +4.85 | carried | Each direction of an RL change acts only as far as the processed text drives its input (right) singular vectors: Math-RL's top-8 input subspaces are excited 8-1 |
| run-05/f2-m01 | weights | 5 | 5 | +4.40 | carried | The top-8 singular directions per matrix of the RL change act as a signed termination dial spread over all layers and both module families: adding them at size  |
| run-07/f2-m02 | problems | 5 | 2 | +3.29 | carried | An RL run's top weight directions write a habit for its own domain's answers. For Math-RL that habit is to deliberate, check, and finish with one boxed answer;  |
| run-05/f2-m06 | weights | 5 | 3 | +2.66 | carried | Weight edits merged in bf16 are realized only where an entry's change exceeds half a unit in the last place of that weight, so small edits are thresholded onto  |
| run-03/f2-m02 | stopping | 5 | 4 | +2.22 | carried | RL's top singular weight directions raise the model's per-token hazard of committing to an answer and ending, in proportion to their size. In-domain directions  |
| run-02/f2-m04 | run-02 | 3 | 2 | +1.43 | carried | A capped sample gives no answer, so in a plurality vote it abstains instead of adding a wrong value. Think-SFT's vote sits near its pass@4 because its unsolved  |
| run-03/f2-m05 | stopping | 5 | 2 | +0.49 | carried | A trace can degenerate before it ends, into word strings, a switch to Chinese script or repeated windows, and a degenerate trace almost never ends right. The ha |
| run-04/f2-m03 | sampling | 5 | 2 | +0.26 | carried | Under T 1.0 stopping is a sampled event: at each position the model draws a commit/stop token with a small hazard, so the cap-hit share is a survival probabilit |
| run-03/f2-m04 | stopping | 5 | 2 | -0.02 | not carried | Graded accuracy depends on how a model ends its answer: whether the last thing written is the gradable marker (a boxed value, an Answer: line, the final python  |
| run-08/f2-m01 | grader | 1 | 1 | -0.14 | not carried | Each one-sample count is one seed's draw: the model branches at forks with fixed per-problem probabilities, so a cell has a sampling SD of about 5-6 problems on |
| run-02/f2-m06 | run-02 | 4 | 2 | -0.20 | not carried | Think-SFT's difference from the base carries long derivation; the RL-Math difference carries a controller that stops once an answer is derived. The two are orth |
| run-06/f2-m05 | training | 2 | 0 | -0.26 | not carried | Imitation and reward write different things. Think-SFT's update, orthogonal to RL's (cosine about 0), supplies derivation quality. RL-Math's update, shaped by a |
| run-05/f2-m02 | weights | 5 | 1 | -0.29 | not carried | The RL change beyond its top-8 directions is a dense per-step error reducer: it lowers the base's chance of writing a slip or misreading at each step and makes  |
| run-04/f2-m04 | sampling | 1 | 1 | -0.31 | not carried | A T 1.0 run is a set of independent per-problem Bernoulli draws: the run-to-run spread of a count is sqrt(sum p(1-p)), about 5-6 problems on MATH-500 and 6 on h |
| run-06/f2-m02 | training | 5 | 1 | -0.41 | not carried | Olmo 3's pretraining and midtraining mix already contains long first-person reasoning traces, so the base holds a complete deliberative register. The cue, a sel |
| run-03/f2-m06 | stopping | 1 | 0 | -0.52 | not carried | Early RL (step 100) installs the deliberative 'Okay' opening on most answers but not all. Answers that miss it fall into the base's terse register and stop befo |
| run-07/f2-m05 | problems | 5 | 1 | -2.59 | graveyard | Too large a finishing dose makes the model stop before its derivation is complete. The cost grows with how long a derivation the problem needs: on hard328's lon |
| run-08/f2-m04 | grader | 5 | 1 | -4.23 | graveyard | Grader v3 and the code harness score only what they extract where they look: a final 'Answer:' line or box for math, a code block for code. A template or weight |
| run-04/f2-m06 | sampling | 5 | 1 | -4.60 | graveyard | Adding RL-direction weight to a model concentrates its answer-level distribution: samples of one problem agree more, right or wrong. Higher dose therefore raise |
| run-02/f2-m03 | run-02 | 5 | 2 | -5.45 | graveyard | The top singular directions of the RL-Math difference set when the base stops, not whether its reasoning is right: their dose sets the cap-hit rate, while right |
| run-02/f2-m05 | run-02 | 3 | 1 | -5.88 | graveyard | The RL-Math difference carries RL's habit of ending a long unsolved attempt with an asserted, underived number (per 1,312 hard328 samples RL finishes long and w |
| run-02/f2-m02 | run-02 | 4 | 1 | -8.62 | graveyard | The cued base's wrong answers on a problem rarely share a value: slips are per-sample chance events that land on scattered numbers, while right answers coincide |
| run-08/f2-m03 | grader | 5 | 0 | -12.27 | graveyard | The RL-direction edits add to a count mostly by converting cap hits into finished answers; the count hides the split: gain = cap hits removed x right rate on co |
