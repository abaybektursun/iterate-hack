# Tier list, round 5 (2026-11-15, 19:25 UTC): the paper after "No Early Warning"

How it was made (board work-184476): one scout read the board items posted since round 4 and tested one idea on the
stored rows: are the project's gains only gains in finishing under the 16,384-token limit? The broad form failed (RL's
gain over the base is 42 to 69 % on problems with no cut-off answer, and survives a limit of 32,768). A narrower form
held and became the pick. The literature was searched before the draft (no paper compares fine-tunes of one family at
two limits).

| Rank | Candidate | Novelty | Evidence | Visual | State |
|---|---|---|---|---|---|
| 1 | The same answers at two token limits: RL - base holds, Think-SFT - RL grows by 6.4 points [3.7, 9.5], the weight sum's gain over Think-SFT shrinks (suggestive on one sample) | 3.5 | 3.5 | 4.5 | Paper 5, Two Token Limits. Waited for one run of the weight sum at 32,768 (result-42cc6c). |
| 2 | Think-SFT beats RL from the same base | 3 | 3.5 | 4 | Folded into 1. The ordering is implicit in the Olmo 3 paper. |
| 3 | Where the RL update sits by depth and rank (result-6f7ca3: 7 of 7 predictions hold on math; result-51ccc6: the depth split fails on code) | 4 | 3 | 4 | Candidate for paper 6: a math result with a failed replication on code stated up front. |

Scout report and reviews are in the session transcript of work-184476.
