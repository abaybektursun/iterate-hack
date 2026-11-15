# Prefix hand-off at T 1.0: where inside an answer does the RL model's advantage enter? (board idea-17d5b7, work-b68a26)

Written 2026-11-15, before any GPU run. Code: `prep/handoff_plan.py`, `jobs/handoff_gen.py`, `analysis/handoff.py`,
`analysis/handoff_test.py`.

## Question

At T 1.0 / top-p 1.0 the base with the opening cue scores 405 of 500 on MATH-500 and RL 456 (Day-1 #3, sample 0). A stored
answer of one model (the writer) is cut after 25, 50 or 75 % of its tokens and the other model, or the same model (the
finisher), writes the rest. Which finisher gets the answer right, from which writer's prefix, at which cut?

Known before the run:
- Test K (SPEC4 section 2, board knowledge-1497e8): T 0.6 / top-p 0.95, 78 problems where the cued base hit the cap and RL was
  right, base finisher only, one cut (median 2,500 tokens): the base finishes 48 of 78 from RL's prefix against 23 from its own.
  At T 0.6 the base's cap hits are loops; at T 1.0 they are long answers (Day-1 #3), so K does not carry over.
- Wang et al. 2610.06851, App. D.3, Table 13 (team memory): swap of the opening only (a few tokens), their setting: base after
  an RL opening 77.7, RL alone 75.1, RL after a base opening 43.7, base alone 41.7. No cut inside the answer.
- No published table has mid-answer cuts in both directions on a base / RL-Zero pair (team memory, `tools/recall.py`). Exa was
  not searched: `EXA_API_KEY` is missing in this session and the MCP Exa tool returned 401.

## Design

- Writers: attempt 0 of sample 0 of the two Day-1 #3 jobs (rule fixed here, before the run): base + cue
  `abaybektursun-1114-153825-208b`, RL plain `abaybektursun-1114-183640-e828`; texts in `answers.jsonl` of each job in the
  Volume `iterate-runs` (the job reads `/runs/<job>/answers.jsonl`; the plan holds each text's sha256).
- Pool: the MATH-500 problems where the base is right in at most 3 of its 4 stored samples (attempt 0, grader v3), from
  `results/day1_3/math500_base_cue-01/rows.jsonl`: 183 problems. Computed by `prep/handoff_plan.py`;
  `results/anatomy/*/pool_k_le3.json` was not on main when the plan was written.
- Answer tokens: the stored records hold text, not ids. The answer text is tokenized with the RL tokenizer by
  `rln4_lib.encode_answer` (the cue's three sampled ids kept). A base answer includes its cue; an RL answer is what RL
  generated (RL writes `' line!\n\nOkay'` itself). Cuts are on token ids: L = round(cut x number of answer ids).
- Request: plain prompt ids + the first L answer ids, to the finisher, T 1.0 / top-p 1.0, max new tokens 16,384 - L (the cap
  counts the prefix, as in K). No cue is added: the prefix carries the writer's opening.
- Arms: writer {base, RL} x cut {25, 50, 75} x finisher {base, RL} = 12 arms x 183 problems = 2,196 requests, one sample
  each. One job per finisher (one model load, 6 arms, 1,098 requests).
- Seeds: 90,000,000 + 100,000 x (5 x writer + cut index) + problem index; writer base 0, RL 1; cut index in (0, 25, 50, 75,
  100). Both finishers use the same seed for the same prefix (different models). No earlier cell uses 90,000,000+.
- Check arms (smoke job only, 10 problems): cut 0 (the plain cell's prompt: ids must equal `n13_score.render_ids`) and cut
  100 (the whole answer; only answers that finished; the finisher must stop within a few tokens and the score must equal the
  writer's).
- Strata, by the writer sample's own outcome: right, wrong (finished, scored 0), cap (16,384 tokens, no stop token). A cut
  inside a cap-hit answer is reported apart. Counts in the pool: base 88 right / 70 wrong / 25 cap; RL 140 / 37 / 6.
- Flag per prefix: `prefix_has_right` = grader v3 applied to the prefix text alone scores 1 (the answer is already written
  before the cut). Every stratum table is also given without those prefixes.
- The job writes each finished request (ids, decoded text, finish reason) to `answers.jsonl` before anything else and does not
  score. `analysis/handoff.py` scores afterwards (grader v3 on prefix text + continuation). The loop detector
  `rln4_lib.onset_lines` raises IndexError on some degenerate answers (reported bug); the readout calls it per row, records the
  error text in the row and counts the errors. It is not fixed here (the lib file is frozen by posted numbers).
- Tokens: per arm, the finisher's generated tokens per problem, and the total including the prefix (L + generated).
- Intervals: Wilson 95 % for each count; paired bootstrap over problems (5,000 resamples, seed 0) for the differences.

## What is compared

1. Per writer, stratum and cut: right of n for each finisher; RL finisher minus base finisher on the same prefixes (paired).
2. Cross minus own, per finisher and cut, paired by problem: base finishing RL's prefix minus base finishing its own; RL
   finishing the base's prefix minus RL finishing its own.
3. Control, own prefix: the pool is selected with sample 0, so sample 0 of the base is wrong more often than a fresh sample
   (regression to the mean). The unbiased subset U is the pool problems that have a wrong answer among base samples 1 to 3
   (in the pool whatever sample 0 did). On U (base) and on the whole pool (RL: the pool rule never reads RL's samples), a
   model that finishes its own prefix must score, in expectation, what its stored sample 0 scores.
4. Fresh rate per stratum, the null for "recovery": the model's mean score over stored samples 1 to 3 on the same problems.

## Hypotheses and what refutes them

- H0 (instrument): own-prefix continuation reproduces the stored sample: on U, base finishing base prefixes minus stored
  base sample 0, and on the pool, RL finishing RL prefixes minus stored RL sample 0, have paired intervals that include 0 at
  every cut. Refuted otherwise; then re-tokenized prefixes change the model's behaviour and the cross rows are read against
  the own-prefix rows only. Also: smoke cut 100 of a right answer scores right with at most 5 new tokens in at least 9 of 10.
- H1 (late checking or finishing): RL is better at the end of an answer. Predicts: on WRONG base prefixes cut at 75 %, the RL
  finisher is right more often than the base finisher. Refuted if the paired interval of RL minus base finisher there
  includes 0 or is negative.
- H2 (the plan chosen early): what RL adds is in the first quarter. Predicts: on the pool, base finishing an RL prefix cut
  at 25 % recovers at least half of the gap between RL finishing its own prefix and base finishing its own prefix at 25 %.
  Refuted if it recovers less than half (point estimate), or if the interval of (base on RL prefix minus base on own prefix)
  includes 0.
- H3 (wrong base prefixes are poisoned): the error is fixed in the prefix. Predicts: on WRONG base prefixes cut at 50 % and
  75 %, neither finisher is right in more than 15 % of cases. Refuted if either finisher's Wilson lower bound exceeds 15 %
  at 50 %.
- H4 (RL prefixes are safe for the base): on RIGHT RL prefixes, the base finisher loses at most 5 points against the RL
  finisher at every cut. Refuted if the paired interval of RL minus base finisher lies above 5 points at some cut.
- A prediction that fails is reported as a result.

## Runs

- Laptop: `prep/handoff_plan.py` writes `data/handoff/plan_v1.json` (pool, strata, lengths, text sha256, id sha256 per
  prefix); `jobs/handoff_gen.py --dry-run` with a stand-in engine; `analysis/handoff_test.py` (planted checks: cut 100 of a
  right answer plus an immediate stop scores right with 0 new tokens; the same prefix plus a wrong answer line scores wrong;
  cut 0 gives the plain prompt ids; a degenerate answer that makes `onset_lines` raise is counted, not lost).
- Smoke: one H100, RL finisher, 10 problems, cuts 0, 25, 50, 75, 100, both writers. Rows read by hand: the continuation
  must continue the writer's text mid-thought.
- Main: two H100 jobs, one per finisher, cuts 25, 50, 75. Estimate from stored lengths: 3.9 M generated tokens per job if
  the finisher writes as much as the writer had left; about 1 h at 1,100 tokens/s; `--hours 4`.
- A job whose requests all started but that died near the end is scored as is, with the missing rows stated, when under 2 %
  of rows are missing.
- Results: `results/handoff/<finisher>-01/` (`run.json`, `metrics.json`, `rows.jsonl` without text, `examples.json`) and
  `results/handoff/readout-01/readout.json`.

## Deviations

- Smoke: the planned smoke `abaybektursun-1114-220435-7492` wrote no log past setup in 23 min and was killed. Its resubmission
  `abaybektursun-1114-222829-ce39` was killed while queued, ran anyway and finished (100 rows); it is the smoke that was read.
  While it ran, two pairs of main jobs died at runner start (`runs.reload()`: its log was open in the reused container).
- The main jobs were submitted before the smoke rows were read, to hold a queue place (coordinator's instruction).
- Added after the first readout was seen (post hoc, not hypotheses): the split of the wrong stratum by whether the writer
  sample had an extracted answer, and the counts of wrong answers that are cap hits or have no answer.
- `results/anatomy/math500-01/pool_k_le3.json` reached main during the run; its 183 problems equal the plan's pool.
- `rln4_lib.onset_lines` no longer raises on the degenerate inputs of `handoff_test` after the merge of main; the readout's
  per-row error record stays, and counted 0 errors in 2,196 rows.
