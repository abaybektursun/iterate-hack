# Notes on the data layer of "Theories on trial"

Run: `uv run --no-project --with numpy python studies/theory/paper/build_facts.py` (worktree at de290fc+; no model, no network).
Outputs: `predictions.jsonl` (516 rows; 403 with flag `headline`), `facts.json`, `calibration.json`. Every stored gain (236 engine rows, 53 duel tests, forecast rows) is recomputed from the forecasts and must match to 0.002 or the script stops.

## How each headline is computed
- Rows: round 1 `predictions_measured.json`; rounds 2-3 `metrics_v{2,3}.json` rows; rounds 4-7 `metrics_v4.json` rows (not_scored rows skipped, as the engine does).
- 426 filed = 7 + 151 + 80 + 42 + 48 + 71 + 27. 403 computed = 426 - 23 with no number. 394 compared = 403 - 9 carried duel rows of round 6 (their "reader" is the theory they replaced). 236 = 394 - 158 of rounds 1-2, where readers filed points, no intervals: gain and reader coverage exist only on these (rounds 3-7).
- Nearer = |theory - measured| < |mean of the 2 reader centres - measured|, ties not nearer. This is the site page's rule; the engine never scored it. 190 of 394 = 0.482, cluster bootstrap 95 % [0.397, 0.551] (58 theories; 20 ties). Strictly nearer than each reader: 156 of 394.
- Coverage of nominal 90 % intervals, n = 236, 45 theories: theories 164 (0.695 [0.565, 0.797]), reader 1 197 (0.835 [0.771, 0.880]), reader 2 202 (0.856 [0.796, 0.902]); paired gap theory minus readers -0.150 [-0.276, -0.051]. All 403: theories 263 (0.653).
- Log gain (engine rule: normal, sd = width / 3.29, against the mixture of both readers, clipped to +-3): total -58.85 nats on 236; mean -0.249 per prediction [-0.685, +0.128]; total [-134.4, +39.8]. Without r6-account (+35.41 on 44): -94.27 on 192, mean -0.491 [-0.742, -0.236].
- Per round nearer / n; coverage t, r1, r2; gain: R1 6/7; R2 74/151 (theory coverage 0.570); R3 40/80, 0.750/0.863/0.925, -25.55; R4 10/29, 0.621/0.862/0.828, -17.32; R5 17/45, 0.489/0.733/0.756, -25.45; R6 35/58, 0.828/0.862/0.845, +22.41 (without the account 4/14, -13.01); R7 8/24, 0.667/0.833/0.875, -12.93.
- Fates (site rule, re-implemented): 63 ids; 23 ever refuted, 4 lost to a rival, 7 no gain, 1 survives (r5-m03-rival, not separated), 0 standing, 28 other (25 failed the round 1-3 score, r4-m01, r5-m10-rival, r6-m06).
- Calibration: the filed interval scaled about the forecast by z(level)/z(0.90) (keeps asymmetry), 11 levels, with cluster intervals; also |z| bins. At nominal 0.5 on n = 236: theories 0.356, readers 0.466 and 0.432. Readers are over-confident too, theories more.

## Scout / site / README against the recomputation
- Reproduced exactly: 63, 426, 403, 394, 190 (20 ties), 236, 69 / 83 / 86 %, -58.85, +35.41, 23 / 4 / 7 / 0, selfopen 375 [348, 400] vs 405 [386, 422] vs 411, 7 exposed targets. Site COUNTS literal: all equal.
- Duels "6 of 11 lost, 4 unseparated, 1 win" mixes rules. As printed by the version that ran each: 6 lost, 2 unseparated, 3 won. The scout's count is that with round 6's two wins re-scored under 7.1 (README correction). One rule (7.1) for all 11: 4 lost, 6 unseparated, 1 won (r4-m08 and r6-account had 0 separating tests). Summed over all 53 duel tests theory minus rival is -5.10 nats (-0.46 per duel): close to even. Rival intervals held 37 of 53, defenders' 27.
- Forecasts: "25 landed" is wrong. 12 distinct targets landed (17 target-run pairs of 37); 25 is the number of theory forecasts on them. Of the 25, 6 are an engine theory (r5-m03-rival, the same 3 targets in both runs: 6 of 6 inside, +3.54 nats) and 19 are mechanisms written for run-02 to disagree (6 of 19 inside, -18.39). "Nearer on 10" uses a stricter rule (nearer than both readers) than the engine page.
- "Planted reversed theory scored like real ones": planted min net +2 of 58, rank 2 of 7 (real: 3, 2, 2, -3, -7, -8), reader-vs-reader noise 3. But in round 2 the 5 reversals scored worse than their theories (nets -5, -5, -10, -2, -6 against +1 to +2; nearer 16 of 67 against 36 of 67); reversals exist only for the 5 candidates and were written by a different agent. No reversal control after round 3.
- Selfopen gain is in no engine file (`round-07/gpu_tests.json` is empty); computed here: -2.81 nats for the theory.
- README "Theories" table is stale ("Status after round 04"). README round counts all match.

## What would embarrass the claim
1. "Scripts fixed before any number was seen" holds only for rounds 4-7 (156 of 394). Rounds 1-3 score numbers a sonnet job read off board posts. In rounds 4-7 the recipe is fixed (sha256); the script is written afterwards by an opus job with Bash. Replication covers part (round 4: 7; round 6: 54 of 55 equal).
2. Three scoring rules: round 1 closer/farther on points, round 2 interval wins/losses, rounds 3-7 log gain. "Outside" changes in 6.2 (within noise is not outside: 9 rows), the duel rule in 7.1. Fates are not comparable across versions; "refuted" in rounds 2-3 is a review's word.
3. The total is not separated from 0 by the cluster bootstrap with the account in ([-134, +40]); one cluster (r6-account) carries +35.41. Its 44 predictions are shares of 7 cells that sum to 1 per cell, and its job read `incumbent_account.json` (earlier accounts' computed shares) that the readers were not given.
4. Predictions cluster: 394 comparisons on 228 distinct quantities (round 2: 151 claims on 38 targets; round 3: 80 on 29). r4-m10's +9.86 is one contrast three times (README). 6 of round 1's 7 hand-matched predictions are claimed again in round 2. Round 1's 7 were picked by hand after scoring.
5. Leak: all 151 round-2 claims come from agents with a commit subject holding result numbers in context (flag `leak_context`); only the 7 targets of that item were removed. Dropping round 2: 116 of 243; rounds 3-7 only: 110 of 236. The 11 exposed claims: 6 nearer.
6. The clip hides size: 27 gains at -3, 5 at +3.
7. Measured values revised or void: r6-m11 p1 differs from its replication (not scored); r5-m09 p1, p2 are 0 by data layout yet scored (-3.00, +0.87); r5-m06's pool was not base-only (README correction); forecast "measured" values are read from posts by a model.
8. One model family for all roles; run files record only the aliases `opus` and `sonnet`, no dated model id. The two readers are the same model and prompt run twice.
9. Whether forecasts were committed before results were posted is not recomputed here; the site literal says 10 of 25.

## Examples (`facts.json` key `examples`)
Confidently wrong:
- r4-m04 (base + a(RL - base) is a per-answer mixture of the two endpoint modes): 'Wait'-rate share at a = 0.25 plain, forecast 0.76 [0.60, 0.90], measured 0.327; readers 0.38 and 0.50; -3.00 nats, z -4.7.
- r5-m07 (by RL step 100 the policy differs from the base almost only in opening with the RL cue): share of step-100 plain answers opening with 'line', forecast 0.68 [0.40, 0.95], measured 0.034; readers 0.30 [0.02, 0.75] twice; -3.00.
Right where the readers were wrong:
- r4-m10 (early RL lowers entropy, so T 0.6 cap hits rise above the base's): step 400 minus base cap-hit rate, forecast +0.06 [0.015, 0.12], measured +0.066; readers -0.06 [-0.13, 0.01] and -0.07 [-0.13, 0.00]; +3.00. Its entropy mechanism later lost to a rival (-7.81).
- r5-m08 (Code 3.0 learned a runaway long-generation mode): share of Code 3.1's lead in the longest quartile, forecast 0.62 [0.45, 0.88], measured 0.795; readers 0.45 [0.20, 0.72] and [0.20, 0.70]; +1.75. Its stated cause was refuted by the review (5 cap hits of 500).
