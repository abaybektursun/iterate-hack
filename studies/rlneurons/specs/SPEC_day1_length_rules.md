# Day-1 length rules: double-check short answers, stop long answers and restart (board work-a992bd)

Written 2026-11-14, before any row exists. Code: `analysis/day1_length_rules.py`, `analysis/day1_length_rules_test.py`. No GPU,
no model, no sampling: the script reads the rows of the Day-1 #3 jobs (`specs/SPEC_day1_3.md`, `run_cell --samples 4
--restarts 2`) and scores two cheaper procedures from them, for both models.

## Question

At T 1.0 / top-p 1.0 the base with the opening cue scores 410 of 500 on MATH-500 and RL 463 (grader v3, one sample). Mean
generated tokens per problem: base 3,933, RL 4,694. The four-sample vote of SPEC_day1_3 costs four full samples per problem.
Can a rule that looks only at the length of an answer reach part of the vote's gain at no more generated tokens per problem
than one RL sample, and does the same rule help RL as much?

Counts given with the task, from the stored single samples (T1, T2), not re-derived here: the base has 263 answers of at most
2,000 tokens, 13 of them wrong; RL has 286 answers of at most 4,000 tokens, none wrong; above 12,000 tokens the base has 15
right and 40 wrong answers, RL 16 right and 22 wrong. The script prints the same counts for the new sample 0 (`sample_0` in
`metrics.json`), so they are checked on the rows it reads.

Closest published experiments (team notes, as cited in SPEC_day1_3): majority vote Maj@2 and Maj@4 in arXiv 2507.18122,
Table 1 (Maj@4 adds 0.8 points to a 73.6 % model on MATH500), and majority@k in arXiv 2610.06851, Fig. 21 (cued base and RL,
k = 1..32, T 0.6). Both vote over a fixed number of full samples. This spec differs in three ways: the extra sample is taken
only when the first answer is short, long answers are stopped at a cutoff, and the base's tokens are matched to one RL sample.

## Input

One finished `run_cell --samples 4 --restarts 2` run per model on the same problem set. Only attempt 0 of samples 0 to 3 is
read: four independent full samples per problem. Restart rows (attempt 1, 2) are not used. Row fields read: `problem_index`,
`sample`, `attempt`, `n_new` (generated tokens before the stop token), `cap_hit`, `extracted_v3`, `score_v3`; for the saved
examples also `seed`, `gold`, `prompt`, `text`. The gold answer enters only through `score_v3` of the sample that a rule
answers with. No decision of a rule reads `score_v3` or `gold`.

An unfinished run is refused as in `day1_vote.py`: `metrics.json` status not `done`, a missing problem or sample, a cap hit
without its restart, a duplicate row (`day1_vote.chains`). A run with fewer than 4 samples is refused.

## Rules (exact order)

Samples are taken in sample order, 0 to 3; a rule never takes a sample out of order and never uses one twice. "Agree" is
`rln4_lib.agree` on `norm_v3` of both extracted answers, through `day1_vote.vote` (the grouping rule of SPEC_day1_3).

**R(L), stop at a length cutoff and restart.** Take sample 0. While the current sample has `n_new > L` and is not sample 3, it
is stopped at L tokens, its answer is discarded, and the next sample is taken. The first sample with `n_new <= L` is the
answering sample. Sample 3 is the last allowed sample: it runs in full and is the answering sample whatever its length. A
sample that hit the cap has `n_new` = 16,384 > L, so it is stopped. With L off the answering sample is sample 0.

**D(S), double-check short answers.** Let j be the answering sample (sample 0 when R is off). The check runs when sample j
finished (no cap hit) with `n_new <= S`, and sample j+1 exists. Otherwise the answer is sample j.

1. Take sample j+1 in full, whatever its length. If j and j+1 agree, the answer is sample j.
2. If they do not agree (different answers, or one of them has no extracted answer) and sample j+2 exists, take sample j+2 in
   full. The answer is the plurality of the three under `day1_vote.vote`: a sample with no extracted answer casts no vote; the
   largest group wins; among equally large groups the one with the lowest sample number wins. So three different answers give
   sample j, and when sample j has no extracted answer and j+1, j+2 differ, the answer is sample j+1.
3. If j+2 does not exist (j = 2), the answer is the vote of the two: sample j, or sample j+1 when j has no extracted answer.
4. If no sample used has an extracted answer, the answer is sample j, scored wrong.

**D(S)+R(L).** First R(L) gives the answering sample j. Then D(S) is applied to sample j with the next unused samples j+1 and
j+2. Check samples are never stopped at L: they run in full. If j = 3 no sample is left and the answer is sample 3; if j = 2
only one check sample exists (case 3). The order is fixed: cutoff first, check second.

The score of a rule on a problem is `score_v3` of the sample it answers with (the first member of the winning group).

Grids: S in {off, 1000, 2000, 4000}, L in {off, 8000, 10000, 12000}; 16 settings; S off and L off is the single row (sample
0). Names: `single`, `D2000`, `R10000`, `D2000+R10000`.

## Tokens

Generated tokens of a problem under a rule = L for each stopped sample + `n_new` of the answering sample + `n_new` of each
check sample. Tokens per problem = the sum over problems / n. Samples that the rule did not take cost nothing. The stop at L
is exact on stored rows: a stopped sample would have generated the same first L tokens.

## Readout

Per model and setting: right of n, percent, Wilson 95 % interval, tokens per problem, the difference against that model's
single row in points with a paired bootstrap interval (5,000 resamples, `n13_score.paired_bootstrap`), the number of problems
the rule fixed (single wrong, rule right) and broke (single right, rule wrong), problems with a check, samples stopped.

With both runs given (`--base` and `--rl`): RL minus base per setting, paired bootstrap; and the equal-tokens block. The budget
is RL's single-row tokens per problem on the same problem set. For the base (and, for comparison, for RL): the setting with
the most right answers among those whose tokens per problem do not exceed the budget (ties: fewer tokens, then grid order),
with its difference against RL single (paired bootstrap).

Files in `--out` (a new run folder, `results/day1_length_rules/<set>-<nn>/`): `run.json` (analysis commit, command, each
run's job id, commit and config), `metrics.json`, `per_problem.tsv` (one line per model and problem: the four `n_new`, and per
setting `right tokens samples`; in `samples`, `x` after a sample number = stopped at L, `*` = the answering sample),
`examples.json` (per model, for `D2000`, that model's best R(L) and its equal-tokens setting: one problem the rule fixed and
one it broke, with every sample the rule touched: seed, `n_new`, extracted answer, score, last 2,000 characters), and with
`--choose` the file `chosen.json`.

## The choice and the test set

`--choose` (MATH-500 only) writes the base's equal-tokens setting (S, L) to `chosen.json`. `--fixed chosen.json` scores only
the single row, that setting and, when both parts are on, its two parts, on another problem set; it refuses a `chosen.json`
made on the same problem set. So S and L are never chosen on the 328. On the 328 the fixed setting can exceed that set's
budget; the readout states `within_budget`.

Choosing the best of 16 settings on MATH-500 biases its MATH-500 number upward. The MATH-500 intervals of a best-of row are
therefore read as optimistic; the 328 row with `--fixed` is the unbiased one.

## Hypotheses and what refutes them

- H0 (instrument): sample 0, attempt 0 repeats T1 and T2. Refuted, and nothing else is read, if the single row is outside
  410 +- 20 (base) or 463 +- 15 (RL), as in SPEC_day1_3.
- H1 (double-check): D(2000) adds at least 1.5 points to the base at fewer tokens per problem than RL single, and at most 0.5
  points to RL. Refuted if the base's paired interval (D2000 minus single) includes 0, or if fewer than 8 short wrong answers
  flip to right net of new errors (`fixed` minus `broke` < 8). Note: T1 has 13 short wrong answers, so 8 net needs most of
  them to flip, and a wrong answer that sample j+1 repeats stays wrong. The check sample's length is not bounded by S, so the
  token part can fail on its own; it is refuted if D2000's tokens per problem are at or above RL single's.
- H2 (cutoff): R(L) at the best L adds 1 to 3 points to the base at no more tokens per problem than its single row, and about
  as much to RL (RL's wrong answers are long too: 22 of its 38 answers above 12,000 tokens are wrong). Refuted if the base's
  paired interval (best R(L) minus single) includes 0. The best of three L is a choice on the same data; see above.
- H3 (the remaining gap): the best setting of the base at equal tokens stays below RL single (463). Refuted if its paired
  interval against RL single includes 0.

Nulls: each model's single row; RL under the same rule (`rl_minus_base`); the four-sample vote of SPEC_day1_3 as the upper
reference for what agreement between samples can add.

## What this does and does not show

- Each rule is a deterministic function of the stored samples, so its row is what an online run with the same seeds returns.
- Samples 1 to 3 serve as restart samples under R and as check samples under D. Within a problem no sample has two roles.
- A decision on `n_new` uses information available at generation time (the token count and whether the answer ended).
- Not covered: a cutoff applied to check samples, a restart with a changed prompt, more than four samples.

## Commands

Test (laptop, no model, no network):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules_test
```

MATH-500, all 16 settings and the choice (after `uv run tools/gpu.py get <job-id>` for both Day-1 #3 jobs):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules --base runs/<base math500 job> --rl runs/<rl math500 job> --out studies/rlneurons/results/day1_length_rules/math500-01 --choose
```

The 328, the chosen setting unchanged:

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_length_rules --base runs/<base hard328 job> --rl runs/<rl hard328 job> --out studies/rlneurons/results/day1_length_rules/hard328-01 --fixed studies/rlneurons/results/day1_length_rules/math500-01/chosen.json
```

One model alone (`--base` or `--rl` only) prints that model's rows without the RL-minus-base and equal-tokens blocks.

## Test record (laptop, 2026-11-14)

- `day1_length_rules_test`: all planted cases pass. D(2000): equal forms agree (no third sample); 2 of 3 fix a wrong short
  answer; a right short answer is broken when samples 1 and 2 share a wrong answer; three different answers keep sample 0; a
  repeated wrong answer stays; `n_new` = S is checked and S + 1 is not; a cap hit is never checked; a sample without an answer
  casts no vote; four samples without an answer score wrong; check samples cost their full length. R(8000): `n_new` = L is not
  stopped and L + 1 is; a right long answer is broken by a wrong restart; three stops then sample 3 in full (3 x 8,000 +
  16,384 tokens); four cap hits. D+R: stop, then check with the next two samples (11,700 tokens by hand); samples running out;
  no sample left; check samples not stopped. Readout: four planted problems per model, 10 settings checked against
  hand-computed right counts, tokens per problem, fixed, broke, checks and stops; `--choose` picks R8000 (3 right at 3,275
  against a budget of 4,200); `--fixed` scores only the fixed rows and reports a fixed setting above the budget as such.
- Refused, as planted: status `running`; a missing sample; a missing problem; a run of three samples; a cap hit without its
  restart; `--fixed` with a `chosen.json` from the same problem set; `--choose` on the 328, without the RL run, or with no
  setting within the budget; two problem sets; swapped models; an existing `--out`. The restart's answer (attempt 2) is not read.
- 14 mutations of the script each failed the test: `>=` at the cutoff; `<` at S; no cap-hit condition; stopped tokens not
  counted; check tokens not counted; never a third sample; the vote ignored; the last attempt read in place of attempt 0; no
  budget filter; no token tie-break; the same-set refusal off; the status check off; the four-sample check off; `fixed`
  counted with `>=`.
- End to end on `run_cell --dry-run` rows (10 problems, 4 samples, 2 restarts, both models, MATH-500 and hard328; the stand-in
  serves right, wrong, cap hit in turn): single 4, every D(S) 4, every R(L) 7, every D(S)+R(L) 7 of 10, as worked out by hand
  from the stand-in's order; `--choose` wrote R8000; `--fixed` on the hard328 rows scored `single` and `R8000` only. On these
  rows D(S) costs 16,406 tokens per problem against 4,926 single, because a check sample that hits the cap costs 16,384.
