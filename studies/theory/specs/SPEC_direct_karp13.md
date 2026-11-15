# SPEC: direct tests karpcap-01 (round-13/s1-a) and karpagree-01 (round-13/s1-b)

Board work-f5966a. Written before any number below was computed. Stored rows only: no GPU job, no forward pass.

## The surprise and the two rivals

The autobench Karpathy arm's kept method (plain prompt, T 0.6, 12 samples, first pass 1,536 tokens, continuation to
4,096, plurality vote; `studies/autobench/results/math500-loop/karpathy-01/solve.py`) got 139 of 328 on hard328
(result-6e7b64); both readers forecast about 190-197. Rivals in
`studies/theory/results/wide/round-13/jobs/rivals-s1.json`:

- a (karpcap): the lost votes on problems the cued base solves come from 4,096-token cap hits; the right routes are
  long. b predicts for a's number: lost problems are no longer-only than difficulty-matched won problems (gap < 0.20).
- b (karpagree): the lost votes come from agreeing short finished wrong answers (shared attractor values); the cap
  rarely binds. a predicts for b's numbers: cap-bound share high, wrong-answer agreement not above the base's own.

The two are near-complements; both numbers are reported whatever the verdicts.

## What was changed from the plans, and why

The plans need per-sample rows of the Karpathy final (finish reason, generated tokens, extracted answer of each of
the 12 samples). Only per-problem grades are committed (`finals-01/hard328-karpathy-000.json`: index, right,
extracted winning answer). The per-sample texts are in frustea's Modal Volume `autobench-runs`
(`final/hard328-karpathy-000/`), not reachable from this workspace (asked frustea at 21:57 UTC). So L, N, C and A_K
cannot be computed. The closest computable readouts, with the plans' thresholds kept:

- Sets (as planned). k = right samples (score_v3 == 1, no cap hit) among attempt 0 of samples 0-3 of the cued base
  (`studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl`, T 1.0, cap 16,384). Lost = Karpathy wrong
  and k >= 2. Null = Karpathy right and k >= 2 (difficulty-matched).
- a, L' and N': share of problems in the lost (null) set where every right cued-base sample is longer than 4,096
  generated tokens (n_new > 4,096), so a 4,096 cap removes every right route the base wrote. This is plan a's own
  step 5, given its null. Holds iff L' >= 0.45 and L' - N' >= 0.20.
- b, C': the same L' (the share of lost problems whose right routes the cap removes). Refuted if C' > 0.35.
- b, A_K' - A_B: A_K' = pooled share of pairs (Karpathy winning wrong answer, cued-base finished wrong answer of the
  same problem) that agree under `rln4_lib.agree`, over the lost set. A_B = pooled share of unordered pairs of
  cued-base finished wrong answers of the same problem that agree, on the same lost problems. Cued-base wrong answers
  are taken from all attempts of samples 0-3 (attempt 0 alone leaves at most 2 wrong per lost problem and almost no
  pairs). Holds iff C' <= 0.35 and A_K' - A_B >= 0.10.
- Bias stated in advance: the Karpathy answer is a plurality winner, a mode, so it matches other draws more often than
  two random draws match. That favours b; a refutation of b by A is therefore strong, a hold is weaker.

90 % intervals: bootstrap over problems of each set, 10,000 resamples, seed 0.

## Checks that the instruments can fail

- finals-01 must reproduce 139 of 328.
- agree(Karpathy extracted, gold) must be true on (nearly) every problem graded right and false on (nearly) every
  problem graded wrong.
- L' at threshold 16,384 must be 0 (right samples are finished), at threshold 0 must be 1.

## Context reported, not used for a verdict

Aggregate finish counts of the final (`karpathy-01/metrics.json`): 7,961 requests, stop 3,331, length 3,910,
time 720. The second call is |cut| + |continued| = 4,025 requests with |continued| <= |cut|, so at least 2,013 of
the 3,936 first-pass samples (51 %) reached the 1,536-token first limit.

## Seen before writing

The finals' per-problem file layout, the cued-base rows' fields, the aggregate finish counts above. No readout.

## Files

- Script: `studies/theory/analysis/direct_karp13.py`
- Outputs: `studies/theory/results/direct/karpcap-01/`, `studies/theory/results/direct/karpagree-01/`
