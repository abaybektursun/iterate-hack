# Direct test of round-10/weights-m03: does Think-SFT's own change lie in RL-Math's input directions?

Written 2026-11-15 before any number below except those marked "seen" was computed. Board work-ae598b. Offline, stored
per-matrix rows only, no GPU, no forward pass.

## The mechanism

round-10/weights-m03 (`results/wide/round-10/mechanisms.json`): "The effect of an added RL change depends on the host.
Think-SFT's high-rank imitation change ... already sets the long-reasoning features that RL's directions read, so RL's push
has about a quarter of its effect on the base: a=1 cut Think-SFT's cap hits by 20 %, not 74 %."

Engine 12's plan (`direct_tests.md` on a copy of round 12, not committed): "Think-SFT's own weight change lies along RL-Math's
top-8 input directions at least 2x more than chance."

## Does the plan's claim follow from this cause, and from no other top mechanism?

- From the cause: if Think-SFT already changed how each matrix responds to the inputs that RL-Math's change reads (its top-8
  right singular vectors V), Think-SFT's change must have weight in that input subspace. A Think-SFT change at chance in every
  matrix leaves the cause no route inside the same matrices. So the overlap is a necessary condition of the cause.
- Other top mechanisms: "autobench buys votes with short samples" and "accuracy depends on how the answer ends" say nothing
  about weights. "Directions act as far as the text drives their inputs" (run-05/f2-m03) also predicts the overlap if
  Think-SFT trained on text that drives the same inputs (reasoning traces). So the overlap does not separate the host cause
  from run-05/f2-m03; it can refute both, not one against the other.
- The plan's chance level is weak. Every fine-tune's weight change has the form sum of (output error) x (input activation)^T,
  so its input side follows the anisotropic input activations; any two changes share input directions above random. Seen
  before this spec (result-9d979a): top-8 vs top-8 input-subspace overlap of Math 3.1 with Think-SFT 0.109, with the base
  matrix's own top-8 0.042, with General 0.045, with IF 0.026-0.034, random 0.002. So "2x random" is close to certain. Seen:
  the share of Think-SFT's change inside Math 3.1's top-8 input subspace, mean over 224 matrices, 0.0088
  (`overlap-01/readout.json`, `cap_right`, think_sft>math31). Not seen: the same share for any other subspace.
- Sharpened claim (the one that tests "the features RL-Math reads", not generic input anisotropy): Think-SFT's change lies
  more in Math 3.1's top-8 input subspace than in the top-8 input subspace of the same rank in the same matrix taken from a
  change that is not math reasoning: IF-RL 3.0, General-RL 3.0 (LM-judge chat), and the base matrix itself (a proxy for the
  input directions every change loads).

## Readout (`analysis/direct_host.py`, numpy)

Input: `data/direct_host/cap_v1.json`, extracted from `runs/abaybektursun-1114-221259-0871/metrics.json` (job of
`studies/rlneurons/jobs/xreward_overlap.py --steps`, commit f89a394, selftest passed: planted rank-8 subspace overlap 1.000,
planted vs independent Gaussian near 8/dimension). Per layer matrix m (32 layers x q, k, v, o, gate, up, down = 224) and
subspace X: `cap_right(a>X)_m = ||d_a V_X||^2 / ||d_a||^2`, d_a = model a minus base, V_X = top-8 right singular vectors of X.
Same for `cap_left` (U_X) and `cap_both`.

- Random matched null: for a uniformly random rank-8 subspace of the input space of dimension n_in, the expected share is
  exactly 8 / n_in for any fixed d (4096 for q, k, v, o, gate, up; 11008 for down). Same rank, same matrix.
- Primary T (the plan's claim): mean over matrices of cap_right(think_sft>math31)_m / (8 / n_in,m).
- Sharpened S_X: mean_m cap_right(think_sft>math31)_m / mean_m cap_right(think_sft>X)_m, X in {if30, general30, base_w}.
- 90 % percentile bootstrap over the 224 matrices (10,000 resamples, seed 0, matrices resampled jointly for numerator and
  denominator). Sensitivity: the same over the 32 layers (matrices of one layer resampled together).
- Reported, not deciding: S for code31, math30 (positive control: another Math RL run must sit far above every non-math
  subspace) and the step-100 subspaces; T and S by module; cap_left, cap_both; how many of 224 matrices have
  cap_right(think_sft>math31) above each X's.

## Verdict rule, fixed now

- Refuted: T upper bound below 2, or for some X the upper bound of S_X below 1 (Think-SFT's change lies less in Math's input
  directions than in a non-math subspace of the same rank).
- Holds: T lower bound 2 or more, and every S_X lower bound 1.5 or more. Row in `results/direct_tested.json`, with the caveat
  that run-05/f2-m03 predicts the same overlap.
- Holds, not distinctive: T lower bound 2 or more, every S_X interval reaching 1 or more, some S_X lower bound below 1.5. Row in
  `results/direct_tested.json` with verdict holds and the result saying the overlap is no larger than generic input
  anisotropy gives.
- Otherwise undecided.

What the test cannot decide: whether the overlap causes the smaller effect of RL on Think-SFT (that needs a forward pass:
Think-SFT + RL with the overlapping part of RL's change projected out, against the base). Not run here.

## Outputs

`results/direct/host-01/`: `readout.json` (every number with n and interval), `examples.json` (the matrix with the largest
and the smallest S against base_w, with their per-subspace values), `run.json` (commit, command, input job).
