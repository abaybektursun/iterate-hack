# SPEC xreward: what do RL runs with different rewards write into the same base? (idea-ac4e14, work-4fa42e)

Written 2026-11-15 before the run. Weights only in Part 1; generation in Part 2.

## Question

Seven released RL-Zero models share the base `allenai/Olmo-3-1025-7B`: Math 3.1, Code 3.1, Math 3.0, Code 3.0, IF, General, Mix.
With the cue on MATH-500 (n 500, T 1.0, v3; result-edceef, result-4b0d5f) they score Math 3.1 457, Code 3.1 450, Math 3.0 448,
Mix 440, General 429, Code 3.0 411, IF 377, against base 410. WSP-1 (result-e2482e) found the top-8 subspaces of the Math 3.1 and
Code 3.1 differences overlap far above a random subspace, and also overlap with Think-SFT's on the input side.

Do the RL differences share a low-rank subspace per matrix, and does that subspace separate the models that gain on math from
those that do not?

## Part 1: overlap table (jobs/xreward_overlap.py, one job, about 10 minutes)

Per layer matrix (q, k, v, o, gate, up, down; 224 matrices) and per difference d = model - base, the top 8 left (output) and right
(input) singular vectors, by `wsp_delta_anatomy.spectrum`. Differences: the seven RL models, Think-SFT, and the base matrix itself
(`base_w`, as a reference for "the difference follows the base's own largest directions").

For every pair (a, b): cos; overlap_left = ||Ua^T Ub||_F^2 / 8, overlap_right the same with V; and for the ordered pair, the share
of a's squared norm inside b's subspace: cap_left = ||Ub^T da||^2 / ||da||^2, cap_right, cap_both = ||Ub^T da Vb||^2 / ||da||^2.

References: random 8-dimensional subspace, overlap 8 / dimension (0.002 for 4,096), stated analytically and checked in the selftest;
Think-SFT (fine-tuning without RL); `base_w`; ceiling Math 3.0 against Math 3.1 (same reward, two releases).

Hypotheses, each with the observation that refutes it:

- X1. RL differences share a subspace beyond what any fine-tune shares: mean overlap (left and right) of RL-RL pairs is above the
  mean of RL-Think-SFT pairs. Refuted if the RL-RL mean is at or below the RL-SFT mean on both sides.
- X2. The shared subspace is not the base's own largest directions: RL-RL overlap is above RL-`base_w` overlap. Refuted otherwise.
- X3. Overlap follows the math gain: among the six other RL models, overlap with Math 3.1 ranks them as their cue score does
  (Code 3.1, Math 3.0, Mix, General, Code 3.0, IF). Refuted if the Spearman correlation of overlap with the cue score is below 0.5.
  If X1 holds and X3 is refuted, the shared subspace is what RL writes whatever it rewards, and it does not carry the math gain.

## Part 2: edits (after Part 1, spec amended here before running)

Chosen from the Part 1 table. Scored with the cue on hard328 (base 164, RL 206) and MATH-500, never on plain rows alone (Think-SFT
scores 91 of 100 plain with a difference orthogonal to RL). Controls: matched random rank-8, Think-SFT top-8, effective scale after
BF16 rounding.

## Amendment 1 (2026-11-15, after Part 1, before any Part 2 cell): first four cells

Part 1 (job abaybektursun-1114-220151-daaa) refuted "one subspace for every reward": input-side overlap is 0.48 for Math 3.0 with
Math 3.1, 0.22 to 0.26 for Math with Code, and 0.03 to 0.05 for Math with IF or General (Think-SFT 0.11). Part 2 therefore asks
first what the 8 directions carry beyond the cue. result-36e8cd has them on plain rows only (427 of 500, against the cued base 410).

Cells: hard328, cue, T 1.0 / top-p 1.0, seed 3000000, one sample (paired with base cue 164, RL plain 206, RL cue 205, theta(0.25)
182), by `wsp_edit` then `run_cell`:

1. `top8 --other rl_math`: base + the 8 directions of Math 3.1.
2. `rand8 --other rl_math`: the matched random control.
3. `top8 --other rl_code`: base + the 8 directions of Code 3.1.
4. `bulk --other rl_math`: Math 3.1 minus its 8 directions.

P1. If the 8 directions carry the gain on hard problems, cell 1 is at least 182 (theta(0.25)) and cell 2 is within 164 +- 12.
    Refuted if cell 1 is within 12 of cell 2: then the 8 directions write the cue and the hard-problem gain is in the rest.
P2. If the gain is in the rest, cell 4 stays within 12 of 205.
A paired difference on 328 problems resolves about 5 points (16 problems).

## Amendment 2 (2026-11-15, before the job): the same table at RL step 100

Part 1 found two groups by input-side overlap: {Math, Code} and {IF, General}, with Mix overlapping both, and each release pair
(Math 3.0/3.1, Code 3.0/3.1) nearest to each other. `xreward_overlap --steps` adds the step-100 checkpoint of each of the seven runs
(revisions pinned in `STEP100`).

- S1. The reward is readable from the weights after 100 RL steps: for each step-100 checkpoint, the final model of another run with
  the highest input-side overlap is the other release of the same reward (Math, Code), or Mix for IF and General, and IF for Mix
  (the Part 1 neighbours). Refuted if fewer than 5 of 7 match.
- S2. The rewards do not share an early phase: mean input-side overlap between step-100 checkpoints of different reward groups
  (Math or Code against IF or General) is no higher than between their final models (0.03 to 0.10). Refuted if it is above 0.2.

## Amendment 3 (2026-11-15, after the first four cells, before the next eight)

First four cells (hard328, cue, of 328): base 164, rand8 158, Math top-8 192, Code 3.1 top-8 178, Math 3.1 minus its top-8 190, RL 206.
P1 held (192 against 158: +10.4 points [5.8, 14.9]). P2 refuted (190, not within 12 of 205): each half alone gives about two thirds of
the gain. Cap hits: 77, 67, 46, 41, 90, 20. Step 100: S1 held (6 of 7; Mix is nearest to General, not IF), S2 held (0.076).

Next cells, same settings, `wsp_edit` with the new flags `--mods`, `--scale`, `--donor` (selftest checks 7 to 9), `--other math31`:

1. `top8 --k 1`. One direction per matrix. Predicted 170 to 180; "one direction is enough" is refuted if within 12 of rand8 (158).
2. `top8 --k 64`. Predicted 192 to 200.
3. `top8 --mods q,k,v,o` and 4. `top8 --mods gate,up,down`. Predicted: the MLP half is higher. Refuted as "one module family carries
   it" if the two differ by fewer than 12 problems.
5. `top8 --scale 2`. Predicted 195 to 206 with fewer than 46 cap hits. Refuted if below 192.
6. `proj --donor code30` and 7. `projc --donor code30`: the Math top-8 edit split into the part that reads from Code 3.0's top-8 input
   subspace (Part 1: overlap 0.218; Code 3.0 itself gains nothing on MATH-500) and the rest, at their natural norms. Hypothesis
   "the input directions that reasoning rewards share carry the gain": 6 is at least 180 and above 7. Refuted if 6 is within 12 of
   rand8; if 7 is then near 192, the gain is in what the math reward adds beyond the shared input directions.
8. `top8 --other code30`. Code 3.0's own 8 directions; its whole model gains nothing on MATH-500 with the cue (411 against 410).

## Amendment 4 (2026-11-15, after the audit of the first four cells): control for the minus-top-8 cell

The audit found that the cap hits are not repetition loops (rules A and B: 0 in every cell) and that the minus-top-8 cell (190 right,
90 cap hits) has no control for the BF16 rounding noise it carries. Cell 9: `rbulk --other math31` = Math 3.1 minus a matched random
rank-8 addition (rand8's P diag(s) Q^T), same rounding. If removing the 8 directions is what costs 15 problems and adds cap hits,
cell 9 stays within 8 of RL cue (205) with fewer than 45 cap hits. If cell 9 is near 190 with about 90 cap hits, the loss is the
perturbation of the RL weights, not the 8 directions.

## Amendment 5 (2026-11-15, after the second batch, before the next eleven cells; work-e02ba4): the finish dial

Second batch: cap hits follow the size of Math 3.1's 8 directions (RL minus them 90, base 77, one direction 51, eight 46, twice
the size 5) while right answers per finished answer stay near 0.65 (0.59 at twice the size). Same settings as before.

Dial, `--other math31`: `top8 --scale S` for S = -1, 0.5, 1.5, 3 (0, 1, 2 exist: 77, 46, 5 cap hits) and the control
`rand8 --scale S` for S = -1, 2, 3 (1 exists: 67).

- D1. Cap hits fall monotonically with S: above 100 at -1, 55 to 70 at 0.5, 10 to 30 at 1.5, at most 2 at 3. Refuted if S = -1
  gives 77 or fewer, or if two neighbouring sizes are out of order by more than 15.
- D2. It is the directions, not the size of a perturbation: the random edit stays within 55 to 85 cap hits at every size. Refuted
  if the random edit at size 3 has fewer than 30 cap hits; then any large rank-8 perturbation makes the model finish.
- D3. Right answers peak between sizes 1 and 1.5 and are below the base (164) at -1 and at 3.

Which reward writes the finishing directions: `top8 --other X` for X = math30, if30, general30, think_sft (Code 3.1: 41 cap hits,
Code 3.0: 23, Math 3.1: 46). The edit's share of the weight norm (`add_rel`) is reported beside each cell.

- R1. The reward family of Part 1 predicts it: math30 at most 55 cap hits; if30 and general30 within 62 to 85; think_sft at least 60.
  Refuted if if30 or general30 has 45 or fewer, or math30 65 or more. If every difference cuts cap hits, finishing is what any
  fine-tune writes.

## Amendment 6 (2026-11-15, after the dial and its replication, before two control cells; work-e1b23a)

The dial has no random cell at its best size, and the Think-SFT cell of amendment 5 was 50 times too large (3.68 % of the weight
norm against 0.074 %) and broke the model. Same settings.

1. `rand8 --scale 1.5 --other math31`. Predicted 155 to 170 right and 60 to 80 cap hits, as the random edit at sizes 1, 2 and 3.
   Refuted if it has fewer than 45 cap hits or more than 180 right.
2. `top8 --scale 0.02 --other think_sft`: Think-SFT's 8 directions at Math's edit norm (3.68 % x 0.02 = 0.074 %). If finishing
   needs a reward, cap hits stay within 62 to 85 and right answers within 164 +- 12. Refuted if cap hits are 50 or fewer: then
   fine-tuning on reasoning traces writes the finishing directions too.

## Amendment 7 (2026-11-15, before the cells; work-df5e0a): the dial on a second model pair and benchmark

The dial is shown for one pair (base, Math 3.1) on math. Code pair (README "Code pair", `jobs/run_code_cell.py`, which gains
`--model-path` / `--model-label`): HumanEval+ and MBPP+, 538 scored problems, Code cue (12 tokens), T 1.0 / top-p 1.0, seed
51000000, one sample. References: base plain 222, base + Code cue 317 (27 cap hits, 34 answers with no code block), RL-Code plain
401 (8, 8).

Cells: `wsp_edit --recipe top8 --other code31 --scale S` for S = 1, 1.5, 2; `rand8 --other code31 --scale 1.5`;
`top8 --other math31 --scale 1.5` (Math's directions on code).

- C1. The dial exists for the Code pair: Code's directions at 1 pass at least 345, at 1.5 at least 360, and the random edit stays
  within 317 +- 15. Refuted if the best of the three sizes is below 340 or the random edit is within 15 of it.
- C2. Cap hits and answers with no code block fall with size (27 and 34 for the base; at most 15 and 15 at 1.5).
- C3. Math's directions at 1.5 on code pass at least 335 (the Math cue works on code: 326). Refuted if within 317 +- 15.
