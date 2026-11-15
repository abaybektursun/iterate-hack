# SPEC tieshort: does "vote ties go to the shortest finished answer" replicate on stored draws?

Board idea-2b2aa1, work-ccac62. Written before `analysis/tieshort.py` exists and before any new number is computed. Laptop
only, no model run: every input is a committed `rows.jsonl`.

## Question

result-dd26fe (section "Vote at a cap of 32,768") found post hoc that breaking vote ties to the shortest answer lifts the
vote over 4 of Think-SFT + cue from 244 to 252 of 328 (cap 32,768), from 238 to 246 (the same answers cut at 16,384), and
from 75 to 81 / 73 to 75 of 136 on fresh2026. The rule was applied after those rows were read. Does the gain appear on the
stored 16,384 draws of the same model (same seeds, but different text after a few hundred characters: an independent draw),
and on RL plain and the cued base?

## The rule

`studies/rlneurons/analysis/selector.py`, `RULES["tie_short"]`, unchanged (written in `SPEC_selector.md` on MATH-500 base
rows, result-cbe0bc): plurality over the groups of `day1_vote.vote`; among the largest groups, the group that holds the
shortest finished sample (`length` = `n_new`, a cap hit counts as infinite); then the lowest sample number. The plain vote is
`RULES["vote"]` = `day1_vote.vote`: among equally large groups, the group whose first member has the lowest sample number
(first seen in draw order; it reads no length and is not random).

The cap32vote post hoc rule is the same function: `cap32vote.RULES["vote4_short"]` = `frontier.RULES["vote4_short"]`
= `{"plan": [4], "tie": "short"}`, and `frontier.TIE["short"]` is `selector.RULES["tie_short"]`. In its 16,384 view a cut
answer is a cap hit, as in a stored row. So there is no variant to test as secondary; the README's "shortest answer" and the
selector's "shortest finished sample" are one rule.

## What is already known (stated so that nothing below reads as blind)

The task was written as if the stored draws had never been scored under this rule. They have, in committed tables, read
while preparing this spec:

- hard328, stored order (`results/table/hard328-02`, README "Configurations ... in one table"): Think-SFT + cue 241 plain,
  239 ties to the shortest; RL plain 221 and 222; base + cue 192 and 191 (after restart 195 and 199).
- MATH-500 (`results/thinkvote/frontier_math500-01`): Think-SFT 481 and 481; RL 474 and 475; base 446 and 453 (the rule's
  home set).
- fresh2026 (`results/fresh/frontier_sft_rl-01`, `frontier_base_rl-01`, rows `vote4_restart_short`; these runs have no
  restarts): Think-SFT 75 and 76; RL 57 and 60; base: 38 with the rule.

So the stored-order point values of H1 are known: -2 on hard328, +1 on fresh2026. Not known: any interval of rule minus
vote on these draws, the pooled interval, the 24-order means of the vote over 4 under both rules (only `seq4_restart`
238.9 against 239.5 is posted), the number of ties, what happens inside them, and the controls.

## Hypotheses

H1 (the lead's claim). On the stored 16,384 Think-SFT + cue draws the rule raises the vote over 4 on hard328 and on
fresh2026. Test: paired bootstrap over problems (5,000 resamples, seed 0, `n13_score.paired_bootstrap`) of rule minus plain
vote, pooled over the 328 + 136 = 464 problems, primary on the mean over the 24 draw orders, stored order next to it.
Refuted if the pooled 95 % interval covers 0.
- The lead's prediction from the cap32vote rows: +6 to +8 problems on hard328 (+1.8 to +2.4 points), +2 to +6 on fresh2026.
- My prediction, given the table above: refuted. Stored order -2 and +1, pooled -0.2 points with an interval covering 0.
  24 orders: the plain vote's mean over orders on hard328 will sit near 239 (241 is a favourable stored order), the rule's
  near 239 to 240, difference within +-1.5 problems; fresh2026 within +-1.5 problems.

H2. A gain exists for Think-SFT and not for RL or the cued base, because Think-SFT's short answers are its precise ones
(risk-coverage: precision falls with length). Refuted if Think-SFT's own interval covers 0 (then there is no gain to be
specific about), or if RL's or the base's pooled interval (hard328 + fresh2026) lies above 0, or if Think-SFT minus RL and
Think-SFT minus base (difference of the paired differences, bootstrap over problems) both cover 0. My prediction: refuted
by the first clause; RL's pooled difference will be the largest of the three (+1 and +3 in stored order).

H3 (mechanism, descriptive). Per model and set: the number of problems with a tie for first in the plain vote; in those,
right answers under the lowest-sample rule, under the rule, under the longest-sample control (`selector.CONTROLS`), and
the expectation of a uniform random choice (`selector.tie_random`); the precision of the tied group that holds the
shortest finished sample against the precision of the other tied groups; the number of ties in which no tied group has a
finished sample (the rule then falls back to the lowest sample). Prediction: hard328 Think-SFT has 25 to 45 ties; the
shortest group is right more often than the other tied groups (by 10 to 25 points of precision), but not more often than
the lowest-sample pick by more than 2 problems on these draws. If the shortest group's precision is not above the other
tied groups' in the pooled Think-SFT ties, the mechanism behind the lead is refuted, not only its size.

## Order robustness

The plain vote's tie-break depends on draw order; the rule's does only when lengths are equal or no tied group finished.
Both rules are replayed over all 24 orders of the four samples (`frontier.replay`, columns `s`), and the difference is
bootstrapped on the per-problem 24-order means. The stored order is reported next to it.

## Controls and checks (run before reading the result)

1. Reproduce from the committed rows: plain vote 241 (hard328), 75 (fresh2026), 481 (MATH-500) for Think-SFT; RL 221, 57,
   474; base 192, 446. Reproduce from `results/cap32vote/*/rows.jsonl` the post hoc numbers: 244 and 252 at 32,768, 238
   and 246 cut at 16,384 (hard328); 75 and 81, 73 and 75 (fresh2026). The script stops if one differs.
2. Planted test (`analysis/tieshort_test.py`): a set of 2-against-2 ties where the group with the shortest sample is always
   right and the lowest sample is wrong must gain exactly the number of ties; with the lengths of each problem shuffled
   the mean gain over shuffles must be about 0; a set where the shortest tied group is always wrong must lose exactly the
   number of ties the vote had right.
3. Null on the real rows: the rule with `n_new` permuted among the finished samples of each problem (200 permutations):
   the gain a length-blind tie-break gets. The rule's gain is compared with this, not only with the stored-order vote.

## Frontier point

`seq4_short` (sequential vote, stop when two agree, at most 4, ties to the shortest) against `seq4`: right (24 orders) and
generated tokens per problem, three models, three sets.

## Outputs

`results/tieshort/{hard328,fresh2026,math500}-01/`: `run.json`, `readout.json`, `table.md`, `examples.json` (one problem
the rule fixes and one it breaks, with the four answers, lengths and scores). Script `analysis/tieshort.py`; it imports
`day1_vote`, `selector`, `frontier`, `n13_score` and copies none of them.

## Posting rule

If H1 holds: `score: other` lines for the stored draws with the caveat that the rule was first seen on other draws of the
same model and problems. If it does not: the null is posted without a score line; the plain votes stay the scores.

## Literature

No Exa key in this environment; one WebSearch. Hassid et al., arXiv 2505.17813 ("Don't Overthink It"), is in the team's
paper memory (Sec 4.3, Fig 3-4: short-m@k breaks ties to the shortest chain and beats a random tie-break); it reports no
replication on a second draw of the same problems and no model trained on traces. Abstracts of arXiv 2505.10772 (ranked
voting) and 2502.06233 (CISC) were seen only as search snippets and support no claim here.
