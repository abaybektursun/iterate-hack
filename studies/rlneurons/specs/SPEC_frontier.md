# Token frontier: right answers against generated tokens per problem, base + cue and RL (board work-86ad1e, idea-aa7280)

Written 2026-11-15, before `analysis/frontier.py` scored any rule. Laptop only: the script replays rules on the stored rows of
Day-1 #3 (`results/day1_3/math500_base_cue-01/rows.jsonl`, `results/day1_3/math500_rl-01/rows.jsonl`; `run_cell --samples 4
--restarts 2`, T 1.0 / top-p 1.0, cap 16,384, grader v3).

## Question

DIRECTION.md asks for the cheapest reward-free route to the RL gain "at equal generated tokens and with RL given the same
procedure". Which test-time rule gives the base with the cue the most right answers at each token budget, does any reach one
RL sample (456 of 500 at 4,675 tokens for sample 0), at what multiple of its tokens, and what does RL get from the same rule?

## What is already known (so this spec is not blind)

- Committed: single 405 / 456, restart 413 / 458, vote over 4 446 / 474, vote after restart 450 / 475, `tie_short` 453 / 475
  (README "Day-1 #3", "Label-free selector"; base / RL). The 328: length rules negative (result-2c2cae).
- A planner's count on the same rows, given with the task and to be verified, not trusted: "draw 2, stop when two agree,
  else up to 4, plurality" base 452 at 11,314 tokens, RL 476 at 11,206; an earlier adaptive count 447 at 12,614.
  `specs/DAY1_hard328_vote_2026-11-14.md` amendment 1 has a parallel rule (stop all four when two finished answers agree):
  base 447 at 13,403, RL 473 at 16,553. The script must say which exact rule gives each of these numbers.
- So the MATH-500 numbers of the sequential rules are not a blind test; the blind test is the 328, scored once.

## Literature

Stopping a self-consistency vote early is published. Adaptive-Consistency (Aggarwal et al., arXiv 2305.11860) stops when a
Dirichlet / Beta posterior says the leading answer will stay the majority; its abstract reports up to 7.9 times fewer samples
with under 0.1 % average accuracy drop. Early-Stopping Self-Consistency (Li et al., arXiv 2401.10480) stops when all answers
in a window agree; its abstract reports 33.8 % fewer samples on MATH and 80.1 % on GSM8K at comparable accuracy. short-m@k
(Hassid et al., arXiv 2505.17813) stops k parallel samples when m finish. Only the abstracts of the first two were read (Exa
key missing; WebFetch of the arXiv pages), so the numbers are quoted, not checked in the tables. The stopping rule is not new.
New here: the frontier of a base model against its own RL-trained version at equal generated tokens, RL given the same rule.

## Input and blindness

Per problem, four sample chains (samples 0 to 3; a chain is attempt 0 and, after a cap hit, up to 2 restarts), checked complete
by `day1_vote.chains`. A rule receives only `n_new`, `cap_hit`, `extracted_v3` of each attempt and returns which attempt it
answers with and the tokens it spent. `score_v3` and `gold` are not in what a rule receives (reading them is a `KeyError`); the
scorer looks up `score_v3` of the returned attempt. "Agree" is `rln4_lib.agree` on `norm_v3` of both answers, grouped as in
`day1_vote.vote`; a sample without an extracted answer casts no vote. With no vote at all the rule has no answer and scores 0.

Tie rules: `low` = among the largest groups, the one whose first member was drawn first (`day1_vote.vote`); `short` = the group
holding the shortest finished sample (`selector.RULES["tie_short"]`).

Tokens of a problem = every generated token of every attempt the rule drew: `n_new` of a full attempt (16,384 for a cap hit),
every attempt of a restart chain, L for a sample abandoned at L. A sample the rule did not draw costs nothing.

## Rules (the whole family, fixed here)

Samples are drawn in the given order and never reused.

| Name | Rule |
|---|---|
| `single` | Sample 1, attempt 0. |
| `restart` | Sample 1; after a cap hit it is sampled again, up to twice (the stored chain). Answer: the last attempt. |
| `R8000`, `R12000` | Length-capped single: a sample longer than L is abandoned at L and the next is drawn; the fourth runs in full (`day1_length_rules.apply`, D off). |
| `vote2`, `vote3`, `vote4` | Plurality over attempt 0 of the first k samples, tie `low`. |
| `vote2_short`, `vote3_short`, `vote4_short` | The same, tie `short`. |
| `vote4_restart`, `vote4_restart_short` | Plurality over four restart chains (each chain's last attempt votes; all attempts cost). |
| `seq3`, `seq4` | Sequential vote: draw 2; stop if they agree; else draw a third; stop if any two agree; else (`seq4`) a fourth; then plurality, tie `low`. `seq3` never draws the fourth. |
| `seq4_short` | `seq4`, tie `short`. |
| `seq_2then4`, `seq_2then4_short` | Draw 2; if they agree stop; else draw the two remaining together; plurality over 4. |
| `seq4_restart`, `seq4_restart_short` | `seq4` over restart chains. |
| `seq4_stop1000`, `seq4_stop2000` | Draw one sample at a time. If the sample just drawn finished (no cap hit, has an answer) with at most N tokens, answer with it. Else continue as `seq4` (tie `low`). N in {1000, 2000}. |
| `seq4_L8000`, `seq4_L12000` | `seq4` (tie `low`) with a length cap: a sample longer than L is abandoned at L, costs L and casts no vote. The fourth stored sample runs in full. |
| `par4_m2` | Not sequential: four samples in parallel; all stop at the first moment two finished answers agree; tokens = each sample's tokens up to that moment; no agreement: `vote4`. Amendment 1 of the 328 spec; here for the reconciliation. |

Offline emulation limits. Abandoning at L is exact (a stopped sample would have generated the same first L tokens). The stored
rows end at four samples: `R(L)` and `seq4_L` run the fourth in full when it also exceeds L, and the script reports on how many
problems that happens ("ran out"). A real run would draw a fifth; on those problems the emulation overstates the tokens and may
understate or overstate the score.

Draw order. (a) Stored order 0, 1, 2, 3: the order the jobs drew. (b) The mean over all 24 orders of the four chains, to
remove order luck: right is then a mean and can be fractional. Both are reported. Choices use (b).

## Statistics

Right of n with the Wilson 95 % interval (stored order). Paired bootstrap over problems, 5,000 resamples, seed 0, on the
24-order means: (1) each base rule minus one RL sample (the mean of the four RL samples: 24-order `single`), with the token
multiple = base rule tokens / RL single tokens and its bootstrap interval; (2) RL minus base under the same rule.

"The base reaches one RL sample" has two readings, both reported: (strict) the point difference is at least 0; (not
separable) the 95 % interval of base minus RL single includes 0. The answer names the cheapest base rule under each reading.

## Selection protocol

Budgets, in generated tokens per problem: 5,000, 7,500, 10,000, 12,500, 15,000, 17,500, 20,000. Candidates: every rule above
except `par4_m2`. Per model and budget: five folds (problem position mod 5); on four folds, the rule with the most right
(24-order mean) among those whose tokens per problem on those folds fit the budget (a draw: fewer tokens, then the earlier
rule in the table); scored on the fifth fold. The held-out total is the honest MATH-500 number of "choose a rule at this
budget". The rule chosen on all 500 per model and budget is written to `chosen.json`.

The 328: `--fixed chosen.json` scores `single` and the chosen rules only, once, in stored order and 24-order mean, on rows of
`run_cell --set hard328 --samples 4 --restarts 2` (board work-1a972a). Nothing is chosen there.

## Other arms (context, not candidates)

Single-sample points of other weights from `results/rate/math500-01/table.json` (weight blends theta, Think-SFT, Code-RL, RL
3.0 checkpoints, controls), labelled with their training signal, so the table shows weight edits beside test-time compute.

## Hypotheses, each with what refutes it

- H1. `seq4` keeps the fixed vote's score at fewer tokens: base within 1.0 point of `vote4` at 25 % fewer tokens or better.
  Refuted if it loses more than 1.0 point (24-order mean) or saves less than 25 %.
- H2. No base rule reaches one RL sample at 2.0 times its tokens or less (strict reading). Refuted by one that does.
- H3. RL keeps a lead under every rule: RL minus base has its interval above 0 for every rule. Refuted by any rule whose
  interval includes 0.
- H4. The 24-order mean moves the base's `seq4` by less than 3 problems from the stored order. Refuted otherwise (then the
  planner's 452 is order luck).

## Planted tests (`analysis/frontier_test.py`)

A rule that reads `score_v3` or `gold` raises `KeyError`. `seq4` on four identical answers costs 2 samples; on four different
answers 4 samples. Two agreeing wrong answers first: `seq4` must stop at 2 and score 0 although samples 3 and 4 are right.
Tie rules, restart tokens, abandoned-sample tokens, `stop N`, `par4_m2` tokens, the budget choice refusing an over-budget rule.

## Outputs

`results/frontier/math500-01/`: `run.json`, `readout.json` (per rule and model: right, interval, tokens, both orders, samples
drawn, ran-out counts, comparisons, the fold choices, per-problem vectors), `frontier.md` and `frontier.json` (the table),
`chosen.json`, `examples.json` (a problem where `seq4` stops at 2 and is right, one where it stops at 2 and is wrong).
