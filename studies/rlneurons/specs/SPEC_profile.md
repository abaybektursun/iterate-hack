# SPEC_profile: do supervised fine-tuning and RL have opposite difficulty profiles?

Board: idea-095c0d, work-d13a7f. Builds on result-e41d94 (RL's gain is largest on easy problems), result-5da8a9 (one axis),
result-17e25e (transfer rules), result-ad3c24 (Think-SFT cue 454, plain 440 of 500). Laptop only, numpy. Written before any
number of this study was computed. Known when written: the three earlier readings of Think-SFT below, and nothing of
work-9ecc56 (Think-SFT on hard328) beyond its title.

## Question

RL-Zero-Math removes 89 % of the cued base's errors on the 335 easiest MATH-500 problems and 25 % on the 46 hardest
(`results/hazard/math500-01/`). Three readings of Think-SFT with cue (one sample, 454 of 500) disagree: hazard ratio
0.33, 0.32, 0.55 for hardest, middle, easiest, called "constant" in the hazard section; 1.95 logits on the hardest group and
0.61 on the easiest, called "outside" in the same section; a planner's count of errors on the hardest 50 (base 43.2, RL
31.5, Think-SFT 26) and the easiest 200 (6.8, 0.2, 8). Step 0 reproduces each from the artifacts and says why they differ.

## Literature (subagent; WebSearch and WebFetch, because `tools/exa.py` has no key and the Exa MCP returned 401)

ReLIFT (arXiv 2506.07527, Section 2.1, Fig. 1a): Qwen2.5-Math-7B, SFT on DeepSeek-R1 traces against RL, 1,000 questions
binned by the base's accuracy over 8 samples: "RL outperforms SFT on Easy and Medium questions", "SFT achieves better results
than RL on the Hardest questions". A figure, no per-bin numbers, no noise floor, difficulty defined by the base. No paper
found with a per-level table for this contrast, a 2PL fit by training method, or the Olmo 3 pair. So the claim is published
in kind for another model; new here would be the size with a same-arm noise floor on this pair.

## Inputs

`results/axis/{math500,hard328}-01/vectors.json` (0/1 per arm, grader v3, T 1.0 / top-p 1.0), read with `rate.load`;
`results/wsp1/full500/sft1_{cue,plain}-01/per_problem.json` (cap hits, tokens); `data/profile/math500_meta_v1.json` (level 1
to 5 and subject per problem, from the Hugging Face dataset `HuggingFaceH4/MATH-500`, `test.jsonl`, joined on `unique_id`);
raw answers in `runs/<job id>/answers.jsonl` where the job is in this workspace. Fits: `axis.fit`, `rate.ability`,
`rate.boot`, `hazard.groups`, `hazard.group_shifts`, `hazard.folds`, `hazard.draw`.

## Difficulty, defined without the arms compared

A problem that an arm fails looks hard if that arm helps define "hard", so no bin uses the reference (the 4 base + cue
samples), the RL 3.1 arms (4 plain samples, cue), the Think-SFT arms, or any arm of the table.

- D-level (primary; uses no model output): MATH level, bins 1-2, 3, 4, 5.
- D-rest: `hazard.groups` (logit link, ridge 0.3) on the single-sample arms left after removing the above: three groups
  holding equal thirds of those arms' wrong cells. These arms are mostly RL-weight arms (theta 1.25, 1.5, the 3.0
  checkpoints, Code-RL plain), so D-rest is "hard for RL-like models".
- D-base: "hard for the base": number right among base + cue samples 2, 3, the random-difference control and the
  base-written-examples cell (0 to 4); bins 0-1, 2-3, 4; the reference is then base samples 0, 1. Repeated with the two
  halves of the base samples swapped, counts added.

## Measures

Per arm and bin: wrong cells per sample, error reduction 1 - wrong(arm) / wrong(reference) with a bootstrap over problems
(2,000 resamples, 95 %), and the logit shift in the bin (`hazard.group_shifts`).
Arms: RL plain (each of 4 samples and pooled), RL cue, Think-SFT cue, Think-SFT plain, Code-RL cue, theta 0.25, 0.5, 0.75 cue,
top-8 plain, Math 3.0 cue.

Profile contrast of arm A against arm B: C = log(wrong_A / wrong_B) in the hardest bin minus the same in the easiest bin
(0.5 added to each count per sample). C < 0: A is relatively better on hard problems. It does not use the base.

## Hypotheses, each with the observation that refutes it

H1. Think-SFT's gain over base + cue is concentrated in hard problems, RL's in easy ones: C(Think-SFT cue, RL plain pooled) < 0.
Refuted if, on D-level, C is inside either noise floor: (a) same-arm: one sample against the pooled other three, 4 values
for RL and 4 for the base (refuted if |C| does not exceed all 8); (b) one axis: the central 95 % of C on 200 matrices
simulated from the fitted Rasch model, bins recomputed where they depend on arms. Also refuted if the sign of C differs
on D-rest or D-base, or if Think-SFT's errors on easy problems are cap hits or answer-format failures rather than wrong
mathematics (cap-hit share of its easy errors above twice that of its other errors, or the raw rows show it).
Prediction: holds on D-rest (it is the hazard section's own split), about half as large on D-level; I give it 50 %.

H2. A per-arm discrimination (2PL: logit p = a_j + (1 + g_j) b_i, ridge on g) improves the held-out log-likelihood over
Rasch on the folds of `axis.heldout`. Refuted if the gain is at or below the 95th percentile of the gain on 20
Rasch-simulated matrices. If it holds, H1 predicts g(RL arms) > g(Think-SFT). Planted check first: a 2PL matrix with g of
sd 0.3 must be detected and a Rasch matrix must not.

H3. The pair (Think-SFT cue, RL) is complementary beyond noise. Test with power for a difficulty-dependent effect: C above,
and the practical quantity, the union of Think-SFT cue with one RL sample against the union of two RL samples (6 pairs).
Refuted if H1 is refuted or the union gain over two RL samples is below 5 problems. Power stated by planting the observed
per-bin logit shifts of Think-SFT on a simulated arm: the share of 200 simulations in which C falls outside the one-axis
95 % range, with 1, 2, 4 and 8 samples of the arm; this also answers how many Think-SFT samples decide H1.

## Predictions for work-9ecc56 (Think-SFT cue and plain on hard328, one sample, of 328), filed before its numbers are opened

(i) `rate` rules with Think-SFT held out: Lc (logit shift times the calibration slope of the 5 arms on both sets), L1, P
(same point gain). (ii) Profile rule: the arm's logit shift per D-rest group on MATH-500, applied to each hard328 problem
by the group its reference probability falls in (group edges as reference probabilities on MATH-500; hard328 difficulties
from its 7 arms and the rerun). 80 % interval: bootstrap of the group shifts plus binomial draws. The profile rule is first
checked on the 5 arms measured on both sets against Lc and P. If H1 holds, Think-SFT should beat its Lc and P predictions.
Filed in `results/profile/predict-01/predictions.json`, committed and pushed, hash commented on work-d13a7f, then scored.

## Verdict rule

Second axis (SFT against RL) = H1 not refuted and H2 or H3 holds. Then name the stack (Think-SFT weights plus an RL part)
with its job and cost; do not submit it. A GPU job (3 more Think-SFT cue samples on the 150 hardest and 150 easiest) only if
the power calculation says one sample cannot decide H1 and no other session has more samples.

## Outputs

`results/profile/math500-01/`: `run.json`, `readout.json`, `table.md`, `examples.json`; `results/profile/predict-01/`;
`results/profile/scored-01/`. Code `analysis/profile.py`, planted checks `analysis/profile_test.py`.
