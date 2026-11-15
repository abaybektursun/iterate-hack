# Vote over k samples of the untrained cued base, k = 1 to 12 (MATH-500)

Written before the jobs. The stored cell has 4 samples per problem (job `abaybektursun-1114-153825-208b`, base + cue, T 1.0 /
top-p 1.0, cap 16,384, seed 41000000): one sample 410.5 of 500, vote over 4 446, at least one of 4 right 467. RL-Zero-Math scores
456 to 463 with one sample. Theory round 06 (result-c637b2) predicted from the stored rows, and nobody ran: vote over 9 samples of
the cued base = 456 [449, 462].

Run: 8 more samples per problem of the same cell (`jobs/run_cell.py --model base --prompt cue --set math500 --temperature 1.0
--top-p 1.0 --seed 41040000 --samples 8`, no restarts, 4 shards). With the seed rule seed + 10000 x sample + index these are the
seeds of samples 4 to 11 of the stored cell. Grader v3. Vote: `rln4_lib` grouping (`agree`), largest group, ties to the group
whose first member has the lowest sample number; a sample with no answer does not vote (the rule of `analysis/day1_vote.py`).

Statistic: right of 500 for the vote over k samples, k = 1 to 12, mean over 200 random subsets of size k of the 12 samples (all 12
for k = 12), bootstrap over problems for the interval; at least one of k right as the upper bound; generated tokens per problem.
Control: the vote over the 4 stored samples must reproduce 446.

Predictions (each with what refutes it):
- V1 (theory round 06) vote over 9 is inside [449, 462]. Refuted outside.
- V2 (mine) the vote stops rising: vote over 12 minus vote over 6 is under 3 problems. Refuted if it is 3 or more. Reason: problems
  the base gets wrong with a stable wrong answer do not flip with more votes.
- V3 the vote over 12 stays below RL's one-sample score 456. Refuted if it reaches 456.

Decision: if V3 is refuted, the untrained base with no training reaches RL's one-sample MATH-500 score by voting, at about 12
times the tokens, and the same cell is run on the 328. If V2 and V3 hold, the vote's limit is measured and the remaining gap is
problems with a stable wrong answer.
Cost: about 16 million generated tokens, 4 vast.ai boxes for under an hour.

## The 328 (added 2026-11-15 19:35 UTC, before its jobs)

Trigger: with 3,989 of the 4,000 new MATH-500 rows read (11 rows of one AWS shard were cut by its time limit; a full copy of
that shard is still running and the MATH-500 numbers are posted only from complete rows), the vote over the available samples
is 446 at 4, 458 at 8 and 466 at 12. V3 is refuted unless the 11 missing rows remove 10 problems, which one missing sample of
12 per problem cannot do.

Run: 4 more samples per problem of the stored cell of the 328 (job `abaybektursun-1114-200457-e8e6`, base + cue, T 1.0 / top-p
1.0, cap 16,384, seed 3000000, 4 samples with restarts; attempt 0 of each sample is used, as on MATH-500):
`jobs/run_cell.py --model base --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3040000 --samples 4`, no
restarts, 6 shards on vast.ai. Deviation from "the same cell": 4 new samples, not 8, because the hackathon ends today; this
gives the vote over k = 1 to 8. Samples 8 to 11 (seed 3080000) follow only if time allows. Same readout (`analysis/votek.py`).

References on the 328, one sample: RL plain 200 to 206, Think-SFT + cue 209. Vote over 4 of attempt-0 rows: base + cue 179,
with restarts 195; RL plain vote over 4 with restarts 224.

Predictions:
- W1 the vote over 8 of the cued base stays below 200 (RL's lowest one-sample score): it lands in [185, 199]. Refuted outside.
  Reason: MATH-500 gained 12 problems of 500 from 4 to 8; from 179 a gain of that relative size gives about 190.
- W2 the vote over 8 minus the vote over 4 is at least 6 problems. Refuted under 6.
