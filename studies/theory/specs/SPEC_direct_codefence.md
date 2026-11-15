# Direct test codefence-01 (theory round 14, engine 14)

Shared test of two rival pairs that state the same statistic on the same rows: round-14/s1 (a vs b) and round-14/s2
(a vs b). Plans: `studies/theory/results/wide/round-14/jobs/rivals-s1.json` and `rivals-s2.json`, field `test`.

## Claim

Which problems carry Think-SFT's Code-cue answers that have no fenced code block. Rival a (both pairs): they are a
layout habit on easy problems, so the cued base passes those problems far more often than a random problem. Rival b
(both pairs): they are failed solves on hard problems, so the cued base passes them far less often. A random 106-problem
subset gives the base's overall rate, 317/538 = 0.589.

## Statistic

r_U = (problems among the 106 Think-SFT Code-cue rows with `mode == "none"` whose cued-base Code-cue row has
`passed == true`) / 106. Unit: problem.

## Files and rows

- Think-SFT + Code cue: job `ih-1115-185836-e7ef/codecue`, raw rows `runs/ih-1115-185836-e7ef/codecue/answers.jsonl`
  (538 rows, one per problem).
- base + Code cue: job `abaybektursun-1114-170304-c03c`, raw rows
  `runs/abaybektursun-1114-170304-c03c/answers.jsonl` (538 rows, one per problem).
- Committed summaries of the same runs: `studies/rlneurons/results/code_think/sft1_codecue-01/` and
  `studies/rlneurons/results/code1/base_cue-01/`.

Rows: the 106 Think-SFT rows with `mode == "none"` (the stored grader found no fenced block; result-9d38d9), each
joined on `uid` to its one base row. n = 106.

## Computation

1. Load both answers.jsonl files; check 538 unique uids each, Think-SFT 301 passed and 106 `mode == "none"`, base 317
   passed and 34 `mode == "none"` (the posted counts of result-9d38d9 and result-59ed1a). Stop if any differs.
2. Select the 106 Think-SFT `none` rows; for each, take the base row with the same uid; a missing row counts as not
   passed (none expected).
3. r_U = passes / 106. 90 % percentile bootstrap over the 106 problems, 10,000 resamples, `numpy.random.default_rng(0)`.
   Also report the Wilson 90 % interval (z = 1.645).
4. Also report: r_U on the 97 unopened-block rows alone, the 9 others, the same base share on the 432 fenced Think-SFT
   rows, and the base's 538-problem rate 0.589.

## Null

Random 106-problem subset of the 538, drawn without replacement: expected 0.589, 90 % sampling range s1 [0.52, 0.66],
s2 [0.51, 0.67].

## Frozen ranges (copied from the plans)

- s1: a [0.72, 1.0], b [0.0, 0.46], null [0.52, 0.66]
- s2: a [0.72, 1.0], b [0.0, 0.45], null [0.51, 0.67]

## Verdict rule (engine 14, rival pair shared test), applied to each pair separately

Interval = the 90 % percentile bootstrap interval. An interval wholly inside one rival's range holds that rival and
refutes the other. An interval in neither rival's range (wholly outside both) refutes both. An interval that straddles a
rival's boundary is undecided for the rival(s) it touches. n >= 50 is required to hold.

## Changes from the plans, noted before computing

- The plans list the committed folders `sft1_codecue-01` and `base_cue-01`, which hold only two example rows each. The
  per-problem rows are the raw `answers.jsonl` files of the same jobs, fetched to the laptop with `ih get` into
  `runs/` (not committed, not in a Modal Volume). Their `metrics.json` files are byte-identical (sha1) to the committed
  ones. The script takes their two paths as arguments.
- s2 names Wilson as the primary interval and bootstrap as the check; s1 names the reverse. Per the brief, the verdict
  uses the 90 % percentile bootstrap for both pairs; Wilson is reported beside it, and any case where the two intervals
  would give different verdicts is stated.
- "First row per problem" (s2): each file has exactly one row per uid, so this changes nothing.
