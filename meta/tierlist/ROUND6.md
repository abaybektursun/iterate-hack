# Tier list, round 6 (2026-11-15, 20:50 UTC): the paper after "Two Token Limits"

Rounds 1 to 5 gave five papers: The finish dial, Theories on Trial, The First Hundred Steps, No Early Warning,
Two Token Limits. This round picks paper 6.

How it was made (board work-184476): one scout read the board items posted since round 5, checked the headline
numbers at the artifacts, read the closest papers before scoring (the lesson of round 4) and scored novelty,
evidence and visual potential from 1 to 5. A second agent then read the closest 12 papers in full
(`studies/rlneurons/paper-depth-rank/LITERATURE.md`).

| Rank | Candidate | Novelty | Evidence | Visual | State |
|---|---|---|---|---|---|
| 1 | Where the RL update acts, by rank and by depth: directions 2 to 8 add the right answers (+7.5 points [4.4, 10.7], hard328) and leave cut-off answers at base level; layers 22 to 31 remove cut-offs (-4.7 [-7.2, -2.1]) without adding right answers; the depth split failed on the Code pair (result-6f7ca3, result-51ccc6) | 4 | 3.5 | 4.5 | Paper 6, written now. 7 of 7 predictions were filed before the run. Four papers put the RL gain in direction 1; none scores finishing apart from correctness. A norm-matched band control is running. |
| 2 | RL's directions carried to other models and domains: Code directions at 1.5x reach 399 of 538 against RL-Code's 401; Math + Code directions summed 411 (result-a1bf75, result-6776d8) | 2.5 | 2.5 | 3 | Waits on the replication work-f58d89 (one sample per cell). Transfer of an RL vector across domains is published (2509.01363). |
| 3 | A vote over 6 samples of the cued base matches one RL sample (result-1c9e40) | 1.5 | 3.5 | 4 | Published: the cue paper (2610.06851, App. E.2, Fig. 21) has the same curve on the same model. Only the early stop is new, and it is a standard idea. |

Dropped: theory rounds 10 and 11 (their surprises are the numbers of result-a1bf75), Think-SFT on the Code pair
(work-8ea654, no result yet).

The scout report is in the session transcript of work-184476.
