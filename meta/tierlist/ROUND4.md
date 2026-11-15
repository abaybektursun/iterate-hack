# Tier list, round 4 (2026-11-15, 18:25 UTC): the paper after "The First Hundred Steps"

Rounds 1 to 3 gave three papers: The finish dial, Theories on Trial, The First Hundred Steps. This round picks paper 4.

How it was made (board work-184476): 4 scouts, one slice each (the delta transplant, the newest dial results, Think-SFT
against RL, everything else), checked the headline numbers at the artifacts, searched the literature and scored
novelty, evidence and visual potential from 1 to 5. No judge panel this round: the scores separated the candidates.

| Rank | Candidate | Novelty | Evidence | Visual | State |
|---|---|---|---|---|---|
| 1 | No early warning: activations and text tell which problem is hard (AUROC 0.73 to 0.77), not which attempt at it will fail (best 0.57 [0.51, 0.63]); a perfect critic would match RL | 3.5 | 3.5 | 4 | Paper 4, written now. No GPU. One close paper (Knowing Before Saying) to read in full first. |
| 2 | Finishing and right answers sit in different ranks and depths of the RL update (result-306787, result-a1bf75) | 4 | 2 | 4 | Waits: one sample per cell, the depth reading was made after the run; needs work-b5f51c and 3 more samples. |
| 3 | Think-SFT with the cue against RL: 80 % against 43 % of finished answers right on 2026 problems; cap 32,768 gives +23 against +2 | 3 | 3 | 4 | Waits: the ordering is implicit in the Olmo 3 paper; cue and chat-format arms missing (work-8b2ec9 blocked). |
| 4 | Delta transplant: Think-SFT + 2 (RL - base), +9.0 points [5.3, 12.7] on fresh2026 | 2 | 3.5 | 4 | The sum of an SFT and an RL vector is published (2605.00610); The finish dial tells the hard328 half. |
| 5 | Agent reviewers cut planted waste but never see work already done (metaharness) | 3.5 | 2 | 3.5 | n = 3 per arm. |
| 6 | Doubt is not checking (signed self-training, wait steering) | 2.5 | 2.5 | 3.5 | Crowded literature; the instrument check failed. |

Scout reports are in the session transcript of work-184476.
