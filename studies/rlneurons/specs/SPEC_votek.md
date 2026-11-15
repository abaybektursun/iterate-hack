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
