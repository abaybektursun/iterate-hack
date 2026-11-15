# SPEC: direct tests of round-13/s3-a ("wrong answers split") and round-13/s3-b ("k=4 ties")

Board work-5d6316. Written before any number below was computed. Stored rows only: no GPU job, no forward pass.
Surprise (round 13, `surprises.md` row 3): cued untrained base, plurality vote over 12 samples on MATH-500, 466 of 500
(result-1c9e40); both no-theory readers about 454. Plans: `rivals-s3.json` in
`studies/theory/results/wide/round-13/jobs/` (iterate-hack-theory checkout).

## The two claims

- votesplit-01 (s3-a): most problems in G (right at k=12, wrong at k=4) have the right answer in under half of the 12
  samples, and win only because the wrong answers split over several values.
- votetie-01 (s3-b): most problems in G were ties at k=4 with the right answer in a tied top group, and have the right
  answer in at least half of the 12 samples.

Why each claim belongs to its own rival: a says the gain sits on p < 0.5 (right is the mode, not a majority); b says it
sits on p >= 0.5 tied at k=4. For the same number, a predicts S_b low (its gains have p < 0.5, so they cannot count for
b), b predicts S_a low. S_a counts p < 0.5 and S_b counts p >= 0.5 in the same set G, so S_a + S_b <= 1: at most one
claim can hold at its threshold (0.50 for a, 0.60 for b). Both can be refuted.

## Files

`studies/rlneurons/results/votek/math500_base_cue-01/rows.jsonl` (500 problems x 12 samples, one attempt each; jobs
abaybektursun-1114-153825-208b and the ih-1115-* shards listed in its metrics.json).

## Computation (one script, both tests)

1. One row per (problem_index, sample), samples 0-11.
2. The vote is the team's rule, not a new normaliser: `studies/rlneurons/analysis/votek.py` `agree_table` and `vote`
   (rln4_lib.agree on norm_v3; a row with no extracted answer casts no vote; largest group wins, ties to the group whose
   first member has the lowest sample index; the vote's score is the first member's score_v3). This is the code behind
   result-1c9e40.
   **Change from the plan:** the plan's answer-bearing rule (drop cap hits and finish_reason 'length') and its
   whitespace/'$'/\boxed normaliser are replaced by this rule, because it reproduces the posted counts. Check before any
   readout: k=4 over samples 0-3 must give 446 and k=12 must give 466 (metrics.json); else stop.
3. G = problems right at k=12 and wrong at k=4. p = (rows with score_v3 == 1) / 12 (a cap hit without a right
   extracted answer counts as not right).
4. a: S_a = |{g in G: p < 0.5}| / |G|. Null (single attractor): per problem, all answer-bearing rows with score 0 merged
   into one group W, all rows with score 1 into one group R; the k=12 null vote is right if |R| > |W|, or |R| == |W| and
   R's first sample index is lower. G_null = right in the null at k=12 and wrong at k=4 (the real k=4 vote).
   S_null = share of G_null with p < 0.5 (0 when every row has an answer). Report |G|, |G_null|,
   kept = |G ∩ G_null| / |G| and how many problems the merge removes from G.
5. b: T = 1 if, at k=4, two or more groups share the top size and one of them is a right group (first member
   score_v3 == 1). S_b = share of G with T = 1 and p >= 0.5. Null F = problems wrong at k=4 with at least one right sample
   in 0-3 that are not in G; S_null_b = share of F with T = 1 and p >= 0.5. Report S_b, S_null_b, S_b - S_null_b.
6. Intervals: 90 % percentile bootstrap, 10,000 resamples of the problems in G (and independently of F for the
   difference), numpy default_rng(0).

## Refuting observations (frozen, from the plans)

- a refuted if S_a < 0.50, or kept >= 0.80 (the merged-wrong null keeps at least 80 % of G: splitting not needed).
  Holds otherwise.
- b refuted if S_b < 0.60, or S_b - S_null_b < 0.20. Holds otherwise.
- Point estimates decide, as in the plans; the interval is reported. |G| is expected to be small (net gain 20), so its n
  is stated plainly.

## Instrument checks

- Reproduce 446 (k=4) and 466 (k=12) with the vote code; assert.
- Null of a: S_null is reported, not asserted. It is 0 when every row carries an answer (p < 0.5 then means |R| < |W|);
  it can exceed 0 only through rows with no extracted answer, and the count of such problems is reported.
- T is checked by hand on the 10 rows read in `reading.md`.

## What was seen before writing

The posted counts (410, 449.2, 456.6, 466; 446 for samples 0-3 in order), the result-1c9e40 comments (34 still wrong,
13 with no right sample) and round-13 fact 28 (43 % of k=4 failures with a right sample lost to a wrong group of two or
more). Nothing about G.

## Outputs

`studies/theory/analysis/direct_vote13.py` writes `studies/theory/results/direct/votesplit-01/` and
`studies/theory/results/direct/votetie-01/`: readout.json, examples.json, reading.md, run.json.
