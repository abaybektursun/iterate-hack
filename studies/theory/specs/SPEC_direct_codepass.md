# SPEC: direct test of round-13/s4-a, "Code's directions raise the pass rate of finished programs; Math's only finish"

Board work-ef2d53. Written before the readout was computed. Stored rows only: no GPU job, no forward pass.

## The claim

Rival `a` of pair s4 (`studies/theory/results/wide/round-13/jobs/rivals-s4.json` in the theory worktree): RL-Code's
top-8 directions at 1.5x raise the pass rate of finished programs, while RL-Math's top-8 directions at 1.5x help code
only by finishing more answers, which then pass at the random edit's rate. Consequence: among answers that finished
(no cap hit) and hold a code block, the pass rate under Code 1.5x is above the random rank-8 1.5x edit's rate, and the
rate under Math 1.5x is not.

Rival `b` (a shared commit-to-an-answer component in both rewards' directions) predicts that Math's directions also
raise this rate, by about Math's share of the total gain over random: dM / dC about 37/68 = 0.54. So the ratio
dM / dC separates the two rivals; rival `a` alone predicts dM < 0.5 dC with dC >= 3 points.

## Change from the plan

The plan sets F = 538 - cap hits - no-block. The two counts overlap (result-a1bf75 comment: 22 of the base's 27 cap
hits also have no block), so F is taken per problem from the rows instead: F = problems with `cap_hit` false and
`mode` != "none". Refuting observation and threshold are unchanged.

## Files

Per-problem rows (538 problems, one sample each, seed 51000000, T 1.0, Code cue), local copies of the job outputs
(`runs/<job>/answers.jsonl`, not committed; cell metrics in `studies/rlneurons/results/xreward/code_dial/`):

- random rank-8 1.5x: abaybektursun-1115-101457-ef2c
- Code top-8 1.5x: abaybektursun-1115-101434-4511
- Math top-8 1.5x: abaybektursun-1115-101508-33f0
- cued base (reference only): abaybektursun-1114-170304-c03c

## Computation

For each cell: r = passed among F / |F|. dC = r(Code) - r(random), dM = r(Math) - r(random), in points; ratio
dM / dC. 90 % paired bootstrap over the 538 problems (10,000 resamples, the same problem draw for all cells).
Secondary reading (not in the rule): the same rates on the problems in F for both the edit and random, which removes
the selection effect of finishing on harder problems.

## Verdict rule (frozen)

- Holds: dC >= 3.0 points and dM < 0.5 dC (point estimates).
- Refuted: dC < 3.0 points, or dM >= 0.5 dC.
- Reported with it: whether the 90 % interval of dC lies above 0, and of dM - 0.5 dC lies below 0. If the point rule
  holds but either interval does not, the verdict is "holds (point only)" and the caveat says so.

Null: the random 1.5x edit's own rate among its finished-with-block answers; rival b's dM/dC = 0.54 is the stronger
null for the Math cell.

## Instrument check

A planted control: replace the Math cell's pass column by the Code cell's on the same problems; the script must then
give dM = dC (ratio 1.0) and the rule must say refuted.

## Seen before writing

The posted totals of result-a1bf75 (passed 331 / 399 / 368, cap hits 27 / 4 / 1, no block 45 / 5 / 6) and the
overlap comment. Not the per-problem F or any rate.
