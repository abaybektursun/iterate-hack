# Self-distillation of the base model's own 4-sample vote (board work-9763ed)

Written 2026-11-15, before any GPU job. Changes after the first GPU job are dated at the end.

## Question

Can the base model's own 4-sample vote be put into its weights with a short supervised fine-tune on its own samples, with no
reward and no labels, and does that transfer to the 328 harder problems it never saw? Pair: base `allenai/Olmo-3-1025-7B`, RL
`allenai/Olmo-3.1-7B-RL-Zero-Math` (revisions in `data/rln4/frozen4.json`; RL tokenizer for all).

Known (grader v3, T 1.0 / top-p 1.0, one sample unless stated). MATH-500: base cue 405-410, its 4-sample vote 446 at 3.4 times the
tokens, RL plain 456-463, base pass@4 467. 328 harder: base plain 76, base cue 164 (77 cap hits), theta(0.5) cue 190, Code-RL cue 187,
RL plain 206, RL cue 205.

## Closest published experiments

- arXiv 2607.13643 (CANON), Table 1: LMSI, supervised fine-tuning on the model's own self-consistency-filtered solutions (hard
  targets), Qwen3-4B-Instruct-2507, 83 unlabeled AMC prompts: AMC (trained on) 66.0 -> 66.5, held-out AIME 2024 32.5 -> 32.5, AIME 2025
  30.1 -> 29.3 (avg@32). Gold-label RFT: 70.0 / 37.0 / 31.2; TTRL (vote reward RL): 70.3 / 36.7 / 31.3. Differs in: an instruct
  model (ours is a pretrained base whose plain prompt is 88 points under its cued prompt on the 328), 83 prompts (ours 455), no
  comparison with a released RL checkpoint of the same base or with partial RL weight differences, T 0.6 evaluation.
- arXiv 2609.18587, Table 2: majority-vote full fine-tuning (RL with vote reward) on Qwen2.5-7B, trained and tested on the same 500
  MATH problems: 45.9 -> 77.0, against 87.9 for gold-label RL. Differs in: RL, not supervised; transductive; no held-out set.
- arXiv 2604.01193, App. B.2: fine-tuning on a model's own unfiltered samples drawn at T 1 with no truncation has zero expected
  gradient. Our arm U is that case (up to the restriction to finished samples and to V's problems): the control should move the
  model little except through format (cue from the plain prompt) and the finished-only filter.
- arXiv 2603.08660: label-free RL sharpens the first answer and rarely corrects it.

Prior from LMSI: the vote-filtered fine-tune barely moves a model on held-out problems. We run it because the base-model setting,
the plain-prompt format effect and the comparison with RL-Zero of the same base are not in any table found (searches:
`tools/exa.py` with "self-distillation of majority-vote consistent samples into base model ... held-out ... RLVR", "fine-tuning
on its own self-consistent answers ... compared to RLVR", "rejection sampling fine-tuning with majority vote pseudo-labels ...
base model AIME transfer", "label-free SFT on self-generated majority voting samples versus TTRL versus RLVR", "SFT on
majority-vote agreeing self-generated solutions of a pretrained base model matches RL-Zero").

## Data arms (`jobs/distill_data.py`, laptop; `data/selfdistill/arms-v1.json`, sha256 `8048c4217ae82283b04902d47f2db2fdfa8203bede68c470b5cd914ae2314c63`)

Source: the base + cue rows of Day-1 #3 on MATH-500 (job `abaybektursun-1114-153825-208b`, `answers.jsonl` sha256 in the arms
file), attempt 0 of the 4 samples per problem, T 1.0 / top-p 1.0, seed rule `41000000 + 10000 s + i`. The builder keeps only
problem index, sample, attempt, cap hit, finish reason, extracted answer (v3 extraction), token count and text: no gold, score or
parsed-gold field reaches it (planted test: changing every gold changes no output).

- Plurality: the answers grouped as in `analysis/day1_vote.vote` (`rln4_lib.agree` on `norm_v3`); the largest group if it has at
  least 2 members and no other group is as large. 2-against-2 ties and all-different problems have no plurality and are dropped.
- V (vote): the shortest finished member (stop token, no cap hit) of the plurality group. 455 problems (45 dropped, all for no
  plurality; 0 for a plurality group with no finished member).
- U (random, control): on V's 455 problems, one finished sample drawn with `random.Random(0)` regardless of its answer.
- S (shortest, length control): on V's 455 problems, the shortest finished sample regardless of its answer.

| Arm | Examples | Mean tokens | Max tokens | Total tokens | Same sample as V |
|---|---|---|---|---|---|
| V | 455 | 1,970 | 15,070 | 896,257 | |
| U | 455 | 2,971 | 15,831 | 1,351,666 | 121 |
| S | 455 | 1,840 | 11,108 | 837,420 | 422 |

V is 34 % shorter than U, so arm S is added. V and S pick the same sample on 422 of 455 problems (93 %): on this data the vote
selection and the length selection are nearly the same choice, so V - U measures "selected by vote or by length" and cannot
separate the two; a model trained on S would differ from V by 33 examples. S is trained and scored (cue only) only if the budget
allows after the main cells (below).

## Training (`jobs/distill_train.py train`, one H100)

Example: prompt = the plain prompt (`data/rln4/prompt_ids.json`, the ids `run_cell --prompt plain` uses; the job asserts
`n13_score.render_ids` gives the same ids and that the stored prompt text decodes from them); target = the stored completion
re-encoded with `rln4_lib.encode_answer` (its first 3 ids are the cue `[1584, 2268, 33413]`) plus the stop id 100257. Loss on the
target only. So the plain prompt learns to write the cue.

Hyperparameters, fixed here, never tuned on the 328: LoRA on q, k, v, o, gate, up, down projections of all 32 layers, rank 16,
alpha 32 (scale 2), no dropout, A Kaiming-uniform and B = 0 in float32, base weights bf16 and frozen. AdamW, lr 1e-4 constant, no
warmup, betas (0.9, 0.999), weight decay 0, gradient clip 1.0. 2 epochs. Batch by target-token budget: examples in shuffled order
(`random.Random(epoch)`) are added to a batch until its target tokens reach 16,384; loss = summed token NLL over the batch's target
tokens. One sequence per forward, gradient checkpointing, sdpa attention. About 55 optimizer steps per epoch for V, 83 for U.

Merge: per adapted tensor M = bf16(W + 2 B A), stochastic rounding (`merge_weights.to_bf16`, generator seed 0, the order of
`merge_weights`); other tensors copied; RL json files (config identical to the base's apart from `use_cache` and the transformers
version). Stochastic rounding because, as in the weight-difference line, most entries of a small difference are under one bf16
unit and nearest rounding would drop them; the job reports the effective scale <M - W, D> / ||D||^2.

Report from each training job (`train.json`): examples, target and prompt tokens, loss per step, first and last step, mean per
epoch; per tensor group the relative norm ||D|| / ||W|| of the float32 difference and of the merged one, and their cosine with
RL - base; the merged-model sha256.

## Checks

1. Data builder planted cases (`jobs/distill_data_test.py`): a row whose answer disagrees with the plurality does not enter V; a
   cap-hit row enters no arm; a 2-2 tie is dropped; the gold field is unused. Passed on the laptop.
2. Zero adapter: the merge with the adapter scaled by 0 is tensor-identical to the base (asserted in the job, all 355 tensors
   pass through the same code).
3. The rebuilt model in each scoring job has the training job's sha256 (asserted).
4. Generations: 3 training prompts with the plain prompt, greedy, 80 tokens, before and after training; read by hand: after
   training they should start with the cue, before they should not.
5. Smoke: one training run on the 8 longest examples of U (worst-case memory), which must write `adapter.safetensors` and
   `train.json`, before the real runs.
6. Sanity cell (in-distribution; these problems were trained on, so a check that training worked, not a result): V plain on
   MATH-500 first 100, beside base plain (T3) and base cue (T1) on the same 100.

## Cells (`run_cell`, T 1.0 / top-p 1.0, cap 16,384, one sample, grader v3)

| Cell | Set | Seed base |
|---|---|---|
| sanity: V plain | MATH-500 first 100 | 80,000,000 |
| V plain | hard328 | 81,000,000 |
| V cue | hard328 | 82,000,000 |
| U plain | hard328 | 83,000,000 |
| U cue | hard328 | 84,000,000 |
| S cue (only if budget allows) | hard328 | 85,000,000 |

No seed base above has been used before in this repository. No comparison is made between cells with the same seed base.

## Predictions (each with the observation that refutes it)

Paired bootstrap over the 328 problems, 5,000 resamples, seed 0, 95 % percentile interval, in points.

- D1: V plain reaches the cued base: V plain >= 164 minus its paired interval. Refuted if the interval of V plain - base cue lies
  entirely under 0.
- D2 (main claim): V cue beats base cue (164): V cue - base cue > 0 with an interval excluding 0. Refuted otherwise. Prior from
  LMSI: likely refuted.
- D3: V beats U at the same prompt arm (the selection matters, not only training on own samples). Refuted if the paired interval
  includes 0; then any gain is from format or length and is reported as that. Because V and S share 93 % of their examples, a held
  D3 means "vote-or-length selection", not vote selection alone.
- D4: V does not reach RL plain (206). If V cue - RL plain has an interval including 0, that is the headline.
- D5: V has fewer cap hits than base cue's 77 (both prompt arms). Refuted if V cue or V plain has 77 or more.

## Analysis (`analysis/selfdistill.py`, `results/selfdistill/readout.json`)

Per cell: right (v3), cap hits, rule-A loops, mean tokens, seed base, job id, share of answers starting with the cue, right per
source. Paired differences for V cue - base cue, V plain - base cue, V - U per prompt arm, V cue - RL plain, V cue - theta(0.5) cue;
fixed and lost against base cue beside RL's 49 and 7; identical non-empty texts between any two compared cells (assert 0). The
share of each arm's training targets that are right under v3 (read from the source rows after the build, never by the builder).
Run folders `results/selfdistill/<arm>-01/` with `run.json`, `metrics.json`, `examples.json` (one right, one wrong) and the
training report. Hand reads: per 328 cell, 20 finished answers scored wrong (numpy seed 0), any that are right listed; 10 answers of
V plain read end to end for degenerate text (copied training solutions, empty answers, repeated lines), two tails quoted.

## Cost estimate (3.95 USD per H100-hour; limit 25 USD)

| Job | Minutes | USD |
|---|---|---|
| smoke (8 longest of U) | 12 | 0.8 |
| train V (1.8 M target tokens at about 3,000 tokens/s, plus setup, load, merge statistics) | 25 | 1.7 |
| train U (2.7 M target tokens) | 30 | 2.0 |
| sanity cell, 100 problems (with setup and merge) | 12 | 0.8 |
| four 328 cells (about 52 min each, plus merge) | 4 x 55 | 14.5 |
| total without S | | 19.8 |
| train S and S cue (only if the running total allows) | 25 + 55 | 5.3 |

Stop adding cells when the next would pass 25 USD.

## Changes after the first GPU job

- 2026-11-15, after the smoke job `abaybektursun-1114-193821-520c` (8 longest U examples, 115,780 target tokens, 3,101 target
  tokens/s, setup 36 s, wall 216 s; zero-adapter merge identical to the base; effective scale 1.000): the cost estimate drops (train V
  about 0.9 USD, U 1.2, S 0.9), so arm S is trained together with V and U and S cue is scored on the 328 (seed base 85,000,000) if the
  running total after the four main cells leaves room under 25 USD. Greedy generations of 3 training prompts with the plain prompt
  before training already begin `.\n\nOkay, so I need to ...` (the base's own plain opener), not the cue; the check after the real
  training reads whether they change to ` line!\n\nOkay`.
- 2026-11-15, before the 328 cells: spend after training and the sanity cell was 3.50 USD, so S cue was submitted with the four
  main cells (job `abaybektursun-1114-201132-3c04`). The readout's seed check was narrowed to compared pairs: the reference cells
  base cue and RL plain share seed base 3,000,000 and are not compared with each other here.
