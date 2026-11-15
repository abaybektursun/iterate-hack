# SPEC_thinkvote: Think-SFT with the cue under the vote rules, on the 328 and on MATH-500

Board: idea-1d9f26, work-0a00c2. Builds on result-d9d6f3 (Think-SFT cue 219 of 328, one sample, sameraslan), result-ad3c24
(454 of 500 on MATH-500), result-bf6124 (difficulty profiles), result-40ed3b (token frontier). Written 2026-11-15 UTC before
any job of this study was submitted.

## Question

Think-SFT (`allenai/Olmo-3-7B-Think-SFT`, revision `6ff857587e040d6d523a3d5f3a56e918f5401d66`, the `think_sft` entry of
`jobs/wsp_delta_anatomy.MODELS`) is trained by imitation on reasoning traces: no reward, but training. With the opening cue
it has 219 of 328 on the harder set in one sample (RL 205 to 206, cued base 164) and 454 of 500 on MATH-500 (RL 456 to 464).
What does it score under the test-time rules chosen on MATH-500 (vote over 4, sequential vote), at how many tokens, and is it
ahead of RL under the same rule on the 328? This is the candidate best reward-free row of the DIRECTION.md deliverable.

Caveats carried into every statement: (1) Think-SFT is trained, so the route is "no reward", not "no training". (2) The 328
are clean against the RL training prompts only; their overlap with the Think-SFT training traces is unchecked (result-d9d6f3,
check with its owner). (3) The 219 is a board post from another workspace; sample 0 here repeats it.

## Part A: cells

Think-SFT weights as in WSP-1: `jobs/wsp_edit.py --recipe interp --other think_sft --alpha 1.0 --rounding nearest --seed 0`
writes the stored Think-SFT tensors bit for bit (asserted in `wsp_edit.edit`: every tensor is the stored tensor, none goes
through rounding) with the RL-Math json files; `jobs/run_cell.py --model-path /tmp/theta --model-label sft1 --prompt cue
--temperature 1.0 --top-p 1.0`, cap 16,384, grader v3.

- hard328: seed 3000000 (sameraslan's cell and the Day-1 #1 rows), samples 0 to 3.
- MATH-500: seed 181000000 (the stored cell `results/wsp1/full500/sft1_cue-01/run.json`), samples 0 to 3.

One job per sample, so a dead job costs one sample: sample s is `run_cell --samples 1 --seed <seed + 10000 s>`, which gives
problem i the seed `seed + 10000 s + i`, exactly the seed of sample s under `--samples 4` (run_cell's rule; no change to
`run_cell.py`). `analysis/thinkvote_join.py` checks the seeds and writes the run folder that one `--samples 4` job would
have written; `analysis/day1_vote.py` and `analysis/frontier.py` read it unchanged.

Restarts: 0. A restart after a cap hit added 1.6 points on the base on MATH-500 at 27 % more tokens, and on the 328 the
base's cap hits are failures to solve, not loops that a new draw escapes (result-51fd20). Think-SFT hits the cap on 89 of 328
(result-d9d6f3), so two restarts would cost up to 2 x 89 x 16,384 tokens per sample for a gain that the vote already takes
(a cap hit casts no vote). The frontier's `restart` rules therefore equal their no-restart versions for Think-SFT; stated
in the table. The RL and base rows of work-1a972a have restarts.

Smoke before the full jobs: MATH-500, the first 10 problems, sample 0 seeds; rows read by hand (cue in the prompt, the
Think-SFT revision in the job log, worked solutions), compared with the stored cell's first 10 scores.

## Instrument checks (other GPU, so texts differ; same-seed rerun noise is about 4 problems, binomial sd 8)

- hard328 sample 0 within 12 of 219. Outside: the harness here and sameraslan's differ; stop and compare before any vote row.
- MATH-500 sample 0 within 12 of 454. Outside: same.
- Cap hits of hard328 sample 0 between 70 and 110 (89 stored).

## Readout

`day1_vote.py` (single, vote over 4, pass@4, tokens, `--minus` RL and base), `frontier.py --fixed
results/frontier/math500-01/chosen.json` with Think-SFT in the `--base` slot against RL for the 328 (single and the rules
chosen on MATH-500, both tie rules, 24 draw orders), and the full `frontier.py` on MATH-500 for the Think-SFT rows (nothing
chosen from them). RL and base + cue rows on the 328 under the same rules: jobs `abaybektursun-1114-200457-e8e6`, `-200505-5ff2`
(work-1a972a). Run folders `results/thinkvote/<set>_sft1_cue_s4-01/`, frontier folders `results/thinkvote/frontier_<set>-01/`.

## Hypotheses, each with the observation that refutes it

H1 (MATH-500 vote over 4, filed blind by others): 473.1 [466, 480] (Rasch, `results/rate/predict-0*`), 472.1 [464, 480]
(hazard, `results/hazard/predict-01`). Above 479 refutes the one-axis claim (result-bf6124); below 464 refutes both rules.

H2 (hard328 vote over 4, filed here before any job finished). Three rules and my number:

| Rule | Predicted right of 328 | Source |
|---|---|---|
| Rasch Lc, anchored at 219 | 243.8 | ability a with sum sigmoid(a + b_i) = 219 on the hard328 difficulties of `rate.py`, plus 0.873 x 0.964 logits (c of `results/rate`, the base's MATH-500 vote-over-4 shift) |
| Rasch Lc with RL's vote shift (0.763) | 238.6 | same |
| Point rule, MATH-500 gain | 245.9 | 219 + 328 x (446 - 405) / 500, the base's vote gain in points |
| Point rule, 328 gain | 234 | 219 + (179 - 164), the base's vote gain on the 328 itself (result-1dedfe) |
| Profile rule | no vote prediction | `results/profile` predicts single samples only (217.6 for this cell) |
| Mine | 238, 80 % interval [228, 250] | a cap hit casts no vote and 27 % of answers hit the cap, so the vote gains less than Rasch says |

Refuted (mine) outside [228, 250]. The rule nearest the observed count wins.

H3: Think-SFT cue is ahead of RL plain under the same rule on the 328: vote over 4 (no restart) Think-SFT minus RL at least
+2 points, as in one sample (+4.0). Refuted if RL's vote is at or above Think-SFT's. A paired interval that includes 0 is
reported as "not separated".

H4: on MATH-500 RL stays ahead under the vote (RL 474): Think-SFT vote over 4 below 474. Refuted at 474 or more.

H5 (tokens): the sequential vote (`seq4`) keeps Think-SFT's vote-over-4 score within 1.5 points at 25 % fewer tokens on
both sets (base: 29 % fewer on MATH-500). Refuted otherwise.

H6 (cap hits, read from raw rows): Think-SFT's cap hits on the 328 are long reasoning that does not finish, not loops
(rule A flags under 30 % of them; base at T 1.0: failures to solve). Refuted if rule A flags half or more.

## Part B: the stack Think-SFT + 1.0 x (RL-Math - base), cue, one sample (only if at most 4 H100 jobs are waiting)

Float32 target per tensor: sft + (rl - base); a tensor where rl equals base bit for bit is the stored Think-SFT tensor.
Rounding to BF16: stochastic (`merge_weights.to_bf16`, the rule of the wdiff study, generator seed 1), because most RL
changes are within one BF16 unit in the last place and nearest rounding would drop part of them. Weights check on the job:
effective scale of (written - sft) on (rl - base) within 0.02 of 1, and the unchanged tensors bit-identical to Think-SFT.
Predictions on file (result-bf6124): 467 of 500 on MATH-500 if the changes add (460 or less refutes); about 219 on the 328
(below 206: the RL change removes Think-SFT's lead). Controls that exist: Think-SFT cue alone (454, 219), base + 1.0 x diff
= RL cue (457, 205).

## Raw rows to read before any explanation

Think-SFT cap hits on the 328 (H6); 10 of the 328 that Think-SFT solves and all RL samples miss; its errors on MATH-500
levels 1 to 2 (wrong mathematics or format).
