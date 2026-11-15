# SPEC: direct test of the judge's disagreement round-15/d1 (editreach-01)

Board work-85bec7 (idea work-4948a7). Written before the statistic was computed. Stored rows only: no GPU job, no
forward pass. Plan: `studies/theory/results/wide/round-15/synthesis_tests.md`, section `round-15/d1` (entry
`round-15/d1` in `synthesis_tests.json`).

## The claim (copied from the plan)

On hard328 problems where the cued base has 0 right among its 4 attempt-0 samples, the 1.5x top-8 edit's per-sample
lift over a fresh cued-base sample, as a fraction of RL plain's lift over the same fresh base sample, is 0.6 or more if
account-2 holds and 0.10-0.45 if account-1 holds.

- account-1 (`round-15/account-1/d1`): the edit carries one shared graded shift that makes the base's scattered slips
  rarer on problems it can already solve, not RL's problem-specific solves. On problems outside the base's 4-sample
  reach the edit lifts the base only a little and captures a minority of RL's advantage there.
- account-2 (`round-15/account-2/d1`): the edit lowers the per-step slip rate the way RL does; the lower rate compounds
  over long chains, so it wins the base-0-of-4 problems about as often as RL plain and captures most or all of RL's
  advantage there.

## Statistic

S = (E - B) / (R - B): the share of RL plain's per-sample advantage over a fresh cued-base sample that the edit captures
on base-0-of-4 problems (unitless ratio of mean per-sample right rates).

## Rows

Problems of hard328 with 0 of 4 right (grader v3, `score_v3`) among the cued base's attempt-0 samples 0-3 in
`studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01` (restarts, attempt > 0, excluded). On these:

- the edit's 4 samples: `day1_3/hard328_top8x1.5_cue_s4-01` (job abaybektursun-1115-055641-b417);
- RL plain's 4 attempt-0 samples: `day1_3/hard328_rl_plain_s4r2-01` (job abaybektursun-1114-200505-5ff2);
- the independent cued-base sample of `cap32/base_cue-01` (job cap32_base_cue_joined, max 32,768 tokens), scored at a
  16,384-token cut: right only if `score_v3` is 1, `n_new` <= 16,384 and not `cap_hit`.

Per-sample scores are read from the committed `rows.jsonl` of the three day1_3 cells and from
`studies/rlneurons/results/cap32/rows-02/base_cue.jsonl`. Freshness needs full texts: `runs/<job>/answers.jsonl` of the
cued-base s4r2 job (abaybektursun-1114-200457-e8e6) and of cap32
(`../iterate-hack-shots/runs/cap32_base_cue_joined/answers.jsonl`), not in git. Drop a problem if any of its 9 rows is
missing, or if the cap32 text's sha256 equals that of one of its s4r2 base samples 0-3 (the sample would not be fresh).
The cap32 seed (3,000,000 + index, sample 0, attempt 0) is the same seed as s4r2 sample 0, so this check matters.
The plan expects n of about 108 problems.

Instrument checks before the readout: each committed rows.jsonl reproduces its metrics.json right count per sample;
the cap32 rows reproduce the readout's 152 right at the 16,384 cut; the same count check fed the wrong cell's rows
must fail.

## Computation (as the plan)

1. Select the problems with 0 right among the cued base's attempt-0 samples 0-3.
2. Per problem: e = right edit samples / 4, r = right RL samples / 4, b = 1 if the fresh cap32 base sample, cut at
   16,384, is right.
3. E, R, B = means of e, r, b over the selected problems.
4. S = (E - B) / (R - B).
5. 90 % interval: resample the selected problems with replacement 10,000 times (numpy default_rng(0)), recompute S each
   time with the same draw for E, R and B; 5th and 95th percentiles. Report R - B with its own interval. If that interval
   includes 0 the test does not count (not decided).

Secondary numbers (not in the rule): E - R with interval; E, R, B separately; the same S with the cap32 sample scored
at its full 32,768 tokens.

## Null

The edit as a base resample: on these problems the edit's rate equals a fresh cued-base sample's (E = B, as a random
rank-8 1.5x edit does), so S is about 0.

## Frozen ranges (copied from the plan)

- account-1: [0.10, 0.45]
- account-2: [0.60, 1.40]
- null: [-0.15, 0.08]

## Verdict rule (engine 14)

Per account: holds only if the 90 % interval lies wholly inside that account's range and n >= 50; refuted if the 90 %
interval lies wholly outside that account's range; otherwise undecided (state the n that would decide). Also report
where the value falls relative to the null range.

## Outputs

`studies/theory/results/direct/editreach-01/`: `metrics.json`, `examples.json` (one row scored right and one wrong,
real input and output), `rows.json` (one row per account for the coordinator). Script:
`studies/theory/analysis/direct_editreach.py`.

## Why editreach-02 exists (added after editreach-01)

editreach-01 (commit d52d13d, result-fe30d5) looped over problem ids `range(328)`, but hard328 ids run 0-399, so it
selected only 102 of the 121 base-0-of-4 problems. The bug was found after -01 by the edit0of4 test (result-378eef).
editreach-02 is the same plan, ranges and verdict rule, iterating over the problem ids in the stored rows. -01 is kept
unchanged and does not count; -02 supersedes it.
