# SPEC: direct test of run-03/f2-m04, "accuracy depends on how the answer ends"

Board work-8965b9. Stored rows only: no GPU job, no forward pass.

## The mechanism and the plan

`run-03/f2-m04` (`studies/theory/results/forecast/run-03/mechanisms.json`): graded accuracy depends on whether the last
thing an answer writes is the marker the grader reads (a boxed value, an Answer: line, the final python block). "Math
directions push a boxed ending that competes with the final code block." Its forecast t05 put Math's 8 directions at
1.5x on code below the readers for this reason.

Engine 12's plan (direct_tests.md on a copy of round 12, not committed): "on code, the RL-Math edit at 1x to 1.5x adds
at least 8 finished answers with no code block".

## Does the claim follow from this cause alone?

Yes. If Math directions install a boxed ending that displaces the final python block, then on code some answers that
finish (no cap hit) end without a fenced block, and the grader (last ```python block) scores them as failed. None of
the other top mechanisms predicts this: "autobench buys votes with short samples" is about voting; "directions act as
far as the text drives their inputs" predicts Math's directions act weakly on code text, not that they change its
ending format; "an added RL change depends on its host" is about sums of edits. The other mechanisms predict the
finishing effect seen on every edit (fewer cap hits), which removes no-block answers instead of adding them.

## Already decided by a posted count?

Mostly. result-a1bf75 (`studies/rlneurons/results/xreward/code_dial/readout.json`) posts "no code block" for the Math
edit at 1.5x as 6 of 538 (cued base 34, random rank-8 at 1.5x 45). That count includes cap hits; the split into
finished and cut-off answers was not posted. Since finished no-block <= 6 and the base's finished no-block >= 34 - 27
= 7, the claim cannot hold against the base. This test computes the split, the paired intervals, and reads the
answers. Disclosure: one count of finished no-block answers per cell was run on the downloaded rows before this spec
was written. The threshold below is the plan's (+8), unchanged.

1x: no cell with Math's directions alone at 1x on code exists (code_hosts `math1_code1` adds Code's directions too),
so only 1.5x is tested.

## Readout

Cells (HumanEval+ and MBPP+, 538 scored problems, Code cue, T 1.0 / top-p 1.0, seed 51000000, one sample each, rows
`answers.jsonl` on the Modal volume `iterate-runs`, copied by `gpu.py get` to `runs/<job>/`):

| Arm | Job |
|---|---|
| cued base | abaybektursun-1114-170304-c03c |
| random rank-8 at 1.5x (matched control) | abaybektursun-1115-101457-ef2c |
| RL-Math 8 directions at 1.5x | abaybektursun-1115-101508-33f0 |
| RL-Code 8 directions at 1x (reference) | abaybektursun-1115-101423-4a7d |
| RL-Code 8 directions at 1.5x (reference) | abaybektursun-1115-101434-4511 |

Finished no-block (FNB): `mode == "none"` and not `cap_hit`. Per arm: FNB, cap hits, no block, passed, answers holding
`\boxed`, answers whose text after the last ``` fence holds `\boxed`. Paired differences over problems (same uid,
same seed): FNB(Math) - FNB(random) [primary], FNB(Math) - FNB(base), FNB(random) - FNB(base). n and a 90 %
bootstrap interval over the 538 problems (10,000 resamples, seed 0) for every number.

## Verdict rule (fixed now)

- Holds: the 90 % interval of FNB(Math) - FNB(random) has its lower end >= +8.
- Refuted: its upper end < +8.
- Undecidable: anything else.
- Second reading, same rule, against the cued base. The cause also predicts boxed endings: refuted in addition if
  fewer than 4 Math-edit answers hold `\boxed` after their last fence or with no fence.

## Saved and read

`studies/theory/results/direct/ending-01/`: `readout.json`, `examples.json` (one Math-edit answer counted as FNB, one
finished with a block and failed), `run.json`. Read every Math-edit FNB answer and random-edit FNB answers to make 10
in all; notes in `readout.json` `reading`.
