# Direct tests codecontract-01 (round-13/s6-a) and codereliab-01 (round-13/s6-b)

Both rivals of round-13 pair 6 explain one surprise: base + Code-RL 3.1's top-8 weight directions at 1x passed 386 of 538
HumanEval+/MBPP+ problems (result-a1bf75); both readers forecast 350. The two tests read the same rows, so one script runs both.

## Claims

- a (codecontract): the base failures that Code top-8 1x fixes are enriched for answer-contract failures (cap hit, no closed
  code block, a block that does not parse, a block that defines no function the tests call) beyond what the random rank-8 1.5x
  edit's fixes show.
- b (codereliab): those fixes are mostly problems the base passes in its other stored base-like samples, clearly more than base
  failures in general.

What the other rival predicts. Rival b treats cap hits and missing blocks as per-sample finishing events, so it predicts the
contract share of top-8 fixes is about the contract share of random fixes (S_top8 - S_rand near 0), which refutes a. Rival a
says the fix is a deterministic contract repair independent of whether the base can solve the problem in other samples, so it
predicts Q_top8 near Q_base (the contract-failure problems are not more base-solvable than others), which refutes b. The two
claims can both hold (contract failures that the base avoids in other samples); the tests are separate.

## Files (stored per-problem rows, one sample per problem, seed 51000000, T 1.0)

`runs/<job>/answers.jsonl` (gpu.py get copies, not committed), fields uid, passed, cap_hit, mode (block/none), code, prompt.

| cell | job | passed |
|---|---|---|
| base + Code cue (code1/base_cue-01) | abaybektursun-1114-170304-c03c | 317 |
| base + Math cue (code1/base_mathcue-01) | abaybektursun-1114-170309-b137 | 326 |
| random rank-8 1.5x (code_dial code_rand8x1.5_code31-01) | abaybektursun-1115-101457-ef2c | 331 |
| Code top-8 1x (code_dial code_top8_code31-01) | abaybektursun-1115-101423-4a7d | 386 |
| RL-Code plain (code1/rl_plain-01) | abaybektursun-1114-170253-f661 | from file |

The Code top-8 1x job id is read from code_top8_code31-01/run.json at run time and asserted to give 386.

## Computation

Join on uid (538). B = problems the Code-cue base fails (221).

a. A base failure is a contract failure if: cap_hit; or mode == "none" (no closed fenced block, the grader's own BLOCK regex
from `rlneurons/lib/code_lib.py`, the same rule ending-01 used); or ast.parse(code) fails; or no `def <entry>` in the parsed
block, where entry is the name in "Write the complete Python function `<entry>`" (HumanEval+) or, for MBPP+, any non-builtin
name called in the prompt's test line (the block must define at least one of them). There are no stdio tasks in this set (all
538 are function tasks), so the stdin rule does not apply. Otherwise logic failure.
F_top8 = B and top8 passes; F_rand = B and random passes. S = contract share of F. r_c = |F_top8 ∩ contract| / |contract|,
r_l = the same for logic. 90 % bootstrap over the 538 problems, 10,000 draws, for S_top8, S_top8 - S_rand, r_c / r_l.

b. k2 = passes in the base + Math cue cell and the random 1.5x cell (0-2). Q_top8 = share of F_top8 with k2 >= 1; Q_base = share
of B with k2 >= 1; Q_RL = share of RL-Code's fixes (B and RL passes) with k2 >= 1. Fix rate of top8 within B∩k2=0 and B∩k2>=1.
90 % bootstrap for Q_top8 and Q_top8 - Q_base.

Change to plan b: the random cell is both in k2 and is the source of no fixes here, so no overlap issue; but random's own passes
on B are by construction F_rand, which shares the seed and prompt with top8. To check that this does not drive Q_top8, a
secondary Q_top8 with k2 from the Math-cue cell alone (k1) is also reported (not deciding).

## Frozen rules (from the plans)

- a holds iff S_top8 >= 0.50 and the 90 % lower bound of S_top8 - S_rand > 0 and r_c / r_l >= 2.0; else refuted.
- b holds iff Q_top8 >= 0.60 and the 90 % lower bound of Q_top8 - Q_base > 0.10; else refuted.

## Nulls

a: the random rank-8 1.5x edit's fixes (S_rand), and the contract share among all base failures. b: Q_base (fixes drawn
without regard to base solvability), and Q_RL as the reference for the full RL change.

## Instrument checks

- Classifier: the planted program `def wrong(): pass` against a HumanEval entry must classify as contract (no entry def); a
  copy of a passing answer's code must classify as logic. Every passing base answer must have an entry def and parse (count
  reported; a passing answer flagged contract means the entry rule is wrong).
- Planted controls: replacing top8's pass column by random's must give S_top8 - S_rand = 0 (refutes a). For b, replacing
  top8's pass column by a draw that fixes a random subset of B of the same size must give Q_top8 near Q_base and refute b.

## Seen before writing

Cell totals (passed, cap hits, no-block counts) from metrics.json and the first row's fields. No per-problem joins were computed.
