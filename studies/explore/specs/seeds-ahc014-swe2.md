# Seeds test: single vs parallel vs fnf on ahc014 with SWE-2 (written before the runs, 2026-11-15 03:05 UTC)

Question: with a strong agent model, does Fork-and-Flush beat one long chat, and does it beat 4 parallel chats
at the same 40 submissions?

- Arms: single, parallel (best of 4), fnf (forks at 0/33/66 %, 4 branches x 2 submissions). Code as in
  ahc014/swe2-01 (commit 78b1352; later commits only add flag-gated arms and backends).
- Model devin:swe-2-medium (Devin Pro, free). Task ahc014, validation cases 1-5, budget 40.
- Seeds 1-5 per arm, new runs in runs/explore/ahc014/swe2-seeds-01; seed 0 from ahc014/swe2-01 is pooled in
  (6 runs per arm). Seed only changes the run label: the model's sampling is not seeded, so seeds are repeats.
- Measure: final best validation score per run. Test: one-sided Mann-Whitney rank-sum (exact, 6 vs 6),
  fnf > single and fnf > parallel; also report mean, spread and the held-out test score (cases 6-10) of each
  run's best program.
- Prediction (from seed 0: fnf 0.625, parallel 0.595, single 0.561): fnf > single at p < 0.05.
  Refuted if p >= 0.05 or the fnf mean is not above the single mean. fnf vs parallel is reported either way;
  a 0.03 gap may need more seeds than this.
- Cost: 0 USD (free model); about 15 runs x 40 calls on 6 concurrent Devin calls.
