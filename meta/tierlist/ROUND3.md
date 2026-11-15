# Tier list, round 3 (2026-11-15, 16:30 UTC): the next papers

Round 1 and 2 (`TIERLIST.md`) put the finish dial in tier S; it is a paper. This round picks what to write next.

How it was made (board work-184476): 8 scouts each read one slice (board items since the last list, basins / jspace /
cleanneurons, autobench / metaharness / gpuprice, the theory engine, the swarm itself, the 144 dossiers of round 1,
the imitation-against-reward line, four mid-tier findings head to head) and checked the headline numbers at the
artifacts. Their 9 candidates went to 5 judges with one view each: frontier scientist, newcomer, founder,
methodologist, interpretability and automated-science researcher. Score: mean of the five tiers (S = 5 ... D = 1,
a minus is -0.3).

| Rank | Candidate | Tiers (sci, new, founder, method, interp) | Mean | Picks | State |
|---|---|---|---|---|---|
| 1 | A. Three tokens match the first 100 RL steps (F08, result-fad48d, F14; with I as a section) | A S S A- A | 4.3 | 3 | Paper 3. Waits on 3 more samples of the step-100 cells (running). |
| 2 | B. Theories on trial: 63 agent-written theories predict no better than readers with no theory (F30) | A- A A S S | 4.3 | 2 | Paper 2, written now: all data committed, no GPU. |
| 3 | C. Imitation beats reward by knowing when not to answer (F01, F02, F12) | B A A C A- | 3.3 | 0 | Waits on the 32,768 vote and the native chat format (work-dc9359, work-8b2ec9). |
| 4 | D. What removing 100 loop neurons buys (F15 and its generation follow-up) | C B B B- B | 2.7 | 0 | Ready. The neurons are published (2606.13705); no repetition-penalty baseline. |
| 5 | E. Forecast the listings, not the median (gpuprice) | B C C B C | 2.4 | 0 | Ready. Off the Olmo mission. |
| 6 | I. The base already writes the cue (F06, code, general questions) | C A B C B- | 2.7 | 0 | Folded into A. |
| 7 | F. Audits reproduce the numbers but narrow the claims | C C B C B+ | 2.5 | 0 | Needs a board export and blind coding (1 h, no GPU). |
| 8 | G. The reliability split is reproduced by noise (F10) | B- D C C B- | 2.0 | 0 | A failure to reject at low power. |
| 9 | H. A Karpathy autoresearch loop against the swarm | D B C D C | 1.8 | 0 | One loop run. |

What the judges agreed on:

- A must claim a bound, not an equality: step 100 plain minus the cued base is +1.6 points [-2.0, 5.2] on one sample,
  and step 100 with the cue beats the cued base by +3.4 [0.2, 6.6].
- B must state up front: both readers are the same model, the scoring rule changed between engine versions, commit
  subjects leaked 7 results in round 2, and predictions cluster inside theories, so intervals resample theories.
- C is the largest practical claim and the least ready: Think-SFT has the cue and RL is plain in every comparison.

Scout reports and judge texts are in the session transcript of work-184476.
