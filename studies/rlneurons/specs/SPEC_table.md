# SPEC_table: every full-set configuration on hard328 in one table (board work-44d747, idea-44d6e1)

Written before `analysis/config_table.py` computes anything. Laptop, no GPU, no model call.

## Question

DIRECTION.md asks how much of the RL-Zero-Math gain is reached without reward training, chosen on MATH-500 and scored once
on the 328 harder problems. The numbers are spread over about 20 README sections. This table rebuilds every full-set
configuration on hard328 from committed per-problem rows, with one definition of each column, and checks every cell that
has a posted number against that number.

Refuted if: a posted number does not reproduce from its committed rows. Such a row stays in the table marked "does not
reproduce" with both numbers.

## Sources (committed rows only)

| Key | Rows | Path |
|---|---|---|
| base | base + cue, 4 samples, up to 2 restarts | `results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl` |
| rl | RL plain, 4 samples, up to 2 restarts | `results/day1_3/hard328_rl_plain_s4r2-01/rows.jsonl` |
| think | Think-SFT + cue, 4 samples, no restart | `results/thinkvote/hard328_sft1_cue_s4-01/rows.jsonl` |
| relay | 8 writer x finisher x cut arms, 1 sample | `results/relay/{rl,think}_c{25,50}-01/rows.jsonl` |
| axis | 0/1 per problem, 1 sample: base plain, RL + cue, base + 0.25 / 0.5 (RL - base) + cue, Code-RL + cue, and the Day-1 #1 draws of base + cue and RL plain | `results/axis/hard328-01/vectors.json`; tokens and cap hits from `results/day1_wdiff328/readout.json` |
| sft_other | Think-SFT cue and plain, 1 sample, sameraslan | `results/wsp1/hard328/sft1_{cue,plain}-01/per_problem.json` at commit `bdba62b` of branch `claude/weight-space-programming-research-ddd44e` (read with `git show`; not on main) |
| MATH-500 | the same three 4-sample runs | `results/day1_3/math500_{base_cue,rl}-01/`, `results/thinkvote/math500_sft1_cue_s4-01/` |

A configuration with no committed per-problem rows is listed under "left out" with the reason. An open work item is left out
and its state is named.

## Rows

One sample (family "single"): base plain; base + cue; RL plain; RL + cue; Think-SFT + cue; Think-SFT plain; base + a (RL -
base) + cue; Code-RL + cue; the 8 relay arms; base + cue and RL with one restart chain; Think-SFT + cue with the answer
stopped at L tokens, L set so that its mean tokens equal one RL sample's (set from token counts only, no score).

Four or more samples (family "vote"): plurality vote over 4 (`day1_vote.vote`, attempt 0); vote over 4 after restart; vote
over 4 with ties to the shortest (`selector.RULES["tie_short"]`), with and without restart; the sequential votes that the
frontier chose on MATH-500 (`frontier.RULES`: `seq3`, `seq4_restart`, `seq4_restart_short`); mixed votes 2 + 2 and 4 + 4 of
two models (`mixvote.mix`).

For the three 4-sample runs the one-sample row is the mean of the four stored samples (attempt 0) per problem, a fraction
per problem; sample 0 alone is a reproduction check, not a row. A sequential rule's row is the mean over the 24 draw
orders, as in "Token frontier"; the stored order is a check.

## Columns

- n samples: samples the rule may draw per problem.
- right / wrong / abstained of 328. Abstained = the configuration gives no answer: no extracted answer (`extracted_v3` is
  null), for a vote no sample with an answer. Almost every cap hit is one; a cap hit with an extracted answer counts as
  answered. Rows without `extracted_v3` (axis: 0/1 only; sft_other: cap flag only) show cap hits in that column, marked.
- accuracy, percent, with a percentile bootstrap 95 % interval over problems.
- paired difference, points, to base + cue one sample (mean of 4) and to RL plain one sample (mean of 4).
- share of the base-to-RL gap closed, defined once:

  share(X) = (acc(X) - acc(B)) / (acc(R) - acc(B))

  Family single: B = base + cue, R = RL plain, each the mean of its four samples (posted 158.5 and 200.0 of 328).
  Family vote: B and R = the plain vote over 4, attempt 0 (posted 192 and 221). 0 % = the cued base, 100 % = RL, above 100 %
  = above RL. The interval is the percentile interval of the ratio itself over the resamples. The denominator's own interval
  is reported; the share is marked unstable when the lower end of the denominator's interval is under half of its point value
  or not above 0.
- one bootstrap for every column: 5,000 resamples of the 328 problems, `numpy.random.default_rng(0).integers(0, n, (5000, n))`
  (the matrix of `mixvote.paired` and `n13_score.paired_bootstrap`), the same resamples for every row, so differences and
  ratios are paired.
- tokens: mean generated tokens per problem over every sample and restart the configuration drew. Relay: generated tokens
  and, beside it, generated + prefix.
- clean 322: accuracy and share without the 6 problems flagged in `results/wsp1/sft_overlap-03/flags.json`.
- grader v4: accuracy under `grader/repair_v4.py` amended (v4a), a grader version for every model, votes recounted on the v4
  extraction. It needs the answer text, which is not committed. `--v4-from runs` reads the local raw answers once and writes
  `v4_rows.jsonl` (problem, sample, attempt, extraction, score; no text) into the run folder; the table reads that file. Rows
  whose text was not read have no v4 cell and are listed. v3 is the headline.
- reward-trained weights: no / yes / partly (a weight blend or a mix of models, one of them reward-trained).
- chosen on 328: "no" only when the model, the prompt, the rule and its parameters were fixed before any 328 score of that
  configuration was read. A rule written on MATH-500 problems and then scored on the 328 is "no", with a note when it was
  chosen in-sample on MATH-500. Picking the best of several arms on the 328 is "yes" for the pick.
- MATH-500 column: the same configuration on MATH-500 (right of 500, tokens) where its rows are committed.

## Tokens matched to one RL sample

Method of "Token frontier": a configuration against one RL sample (mean of the four), with its token multiple and the
bootstrap interval of the multiple (`frontier.ratio_interval`). A configuration is at matched tokens when the multiple's
interval includes 1 or lies below it.

## Instrument checks

1. Every posted number of a row (README section or board result) is listed in `checks.json` with expected and got; counts
   and tokens must be equal after rounding to the posted digits, intervals are recomputed with the function its section used.
2. Planted test of the share: a configuration equal to RL gives exactly 100 % with interval [100, 100], equal to the base
   0 % [0, 0], and the mean of the two 50 %.
3. Planted failure: a row vector with one flipped problem must fail its check.

## Outputs

`results/table/hard328-01/`: `run.json`, `table.md`, `table.json`, `checks.json`, `v4_rows.jsonl`.

## Addendum 1: run hard328-02 (written before `config_table.py` is changed or any new cell is computed)

Reason: review of result-389164. "Every configuration" overstated: the top-8 dial and the self-distillation rows were absent.
Since hard328-01, per-problem rows of more closed hard328 configurations are on main. `results/table/hard328-02/` holds the
table of hard328-01 plus the rows below; hard328-01 is not touched. Same columns, same bootstrap, same check mechanism: every
posted number of a new row goes into `checks.json` with expected and got, and a row whose number does not reproduce stays in
the table marked "does not reproduce". The table is named "configurations with committed rows", and what is absent is listed.

New sources (committed on main):

| Key | Rows | Path |
|---|---|---|
| dial | 0/1, cap hit, tokens and extracted answer per problem, 1 sample: base + s x (top 8 directions of RL - base) + cue at s = -1, 0.5, 1, 1.5, 2, 3; 8 random directions at -1, 1, 2, 3; s = 0 and RL are the Day-1 #1 draws already in the table (used as a check against `axis/hard328-01/vectors.json`) | `PROBLEMS` in `tools/finding_the_finish_dial.py` (written from the jobs' answers; the run folders `results/xreward/edits/*-01/` hold metrics only); posted numbers in `results/xreward/edits/readout.json`, result-6f1bb7 |
| dial4 | the 1.5 size, 4 samples, no restart | `results/day1_3/hard328_top8x1.5_cue_s4-01/rows.jsonl` (the same file as `results/xreward/dial15_s4_vs_*-01/rows.jsonl`); MATH-500 one sample `results/xreward/dial15_math500-01/rows.jsonl`; result-95a4dc |
| transplant | Think-SFT + a (RL - base) + cue, a = 1, 2 (two samples), 3, 4, and Think-SFT + noise of the RL delta's norm, 1 sample each | `results/transplant/hard328-01/rows.jsonl`; MATH-500 a = 1 `results/transplant/math500-01/rows.jsonl`; result-3387ce |

New rows. Family single: each dial cell; the 1.5 size as the mean of its four samples; M(1), M(2) as the mean of its two
samples, M(3), M(4), the noise control. Family vote: the 1.5 size, plain vote over 4.

Flags, fixed here before the numbers are computed:
- dial, top-8 directions: reward-trained weights "partly (RL-derived directions)". Chosen on the 328: "yes" for size 1.5 (the
  best of 7 sizes scored on the 328), one sample and the four-sample rows alike; the four samples are new draws on the same
  problems, not a held-out set. The other sizes: "no (one size of the sweep, every size reported)".
- dial, random directions: reward-trained weights "no", chosen "no"; they are controls, not methods.
- transplant: reward-trained weights "partly"; chosen "yes" for a = 2 (best of 4 values of a on the 328; its second sample
  was pre-registered with the threshold 222); a = 1 "no" (prediction filed before the run); a = 3, 4 "no (one value of the
  sweep)". Noise control: "no", "no"; a control.

Included only if its rows are on main when the script runs, otherwise listed as left out with the reason: cap 32,768
(result-c8b994), self-distillation, signed self-training, the loop-neuron edit, solved examples, the other xreward edit cells.

Separate table, different benchmark, no share of the gap: fresh2026 (n = 136, result-5251c9), three models, one sample (mean
of 4) and vote over 4, with right / wrong / abstained, accuracy and its interval (the same bootstrap over the 136 problems),
tokens, and the paired differences as posted. Rows `results/fresh/{sft1_cue,rl_plain,base_cue}_s4-01/rows.jsonl`; posted
numbers `results/fresh/readout-01/readout.json`, checked the same way.

Summary sentences of the README section: changed only if a new row changes them. Sentence 1 changes if a row with
reward-trained weights "no" and chosen on the 328 "no" that is a method (not a control) is above Think-SFT + cue in its
family. The script prints the best such row per family.

Refuted if: a posted number of a new row does not reproduce from its committed rows.
