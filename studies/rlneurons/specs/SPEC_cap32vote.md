# SPEC cap32vote: the vote over 4 of Think-SFT + cue at a cap of 32,768 tokens

Board idea-01fe11, work-dc9359. Written before any job was requested; the simulation below used stored rows only.

## Question

Think-SFT + cue votes 241 of 328 (hard328) and 75 of 136 (fresh2026) at a cap of 16,384 generated tokens. It hits that cap on
29 % and 46 % of its samples. One sample at a cap of 32,768 gains 23 problems on hard328 (207 to 230, +7.0 points [4.3, 9.8],
`results/cap32/readout.json`). What is the vote over 4 at 32,768 on both sets, and is doubling the cap a better use of tokens
than more samples at the old cap?

## Design

- Model, prompt, sampling, grader as in `SPEC_thinkvote.md` and `SPEC_fresh.md`: Think-SFT (`wsp_edit --recipe interp --other
  think_sft --alpha 1.0`), prompt `pair1` + cue, T 1.0 / top-p 1.0, grader v3, no restarts. Only `--max-tokens 32768` is new
  (`run_cell` sets the vLLM context to 2,048 + cap = 34,816; prompts are at most 2,048 tokens).
- hard328: samples 1 to 3, seeds 3010000, 3020000, 3030000 (the seeds of the stored 16,384 samples), each as 2 shards. Sample 0
  is the cap32 job `abaybektursun-1115-005756-309b` (seed 3000000), if its rows can be had; else it is run again here.
- fresh2026: samples 0 to 3, seeds 7000000 + 10000 s (the seeds of `SPEC_fresh.md`), `jobs/run_fresh.py`.
- Each answer is scored twice from the same text: at 32,768 as the runner wrote it, and at 16,384: an answer of more than
  16,384 tokens is cut after its 16,384th token (tokenizer of the run) and graded by grader v3 as a cap hit, exactly what a
  16,384 run stores (in the stored rows 55 of 378 cap hits still give an extracted answer, 14 of them right). All 16,384
  against 32,768 comparisons are paired on these identical answers. The stored 16,384 runs are a second, unpaired reference.
- Readout (`analysis/cap32vote.py`): singles, vote over 4, sequential votes, cap hits, precision of finished answers, tokens
  per problem, for both views; paired bootstrap of 32,768 minus 16,384 (single, vote) and against RL's stored vote; the 322
  problems outside Think-SFT's training prompts; fresh2026 split into 59 published and 77 transcribed.
- Limit, stated now: RL plain is not rerun at 32,768 with 4 samples. Its one-sample gain there is +0.6 points [0.0, 1.5]
  (2 problems). The comparison is against RL's stored 16,384 vote (221 of 328; 57 of 136), and against that vote plus 5
  problems (1.5 points, the upper end of its one-sample gain) on hard328.
- Jobs: `specs/cap32vote_jobs.txt`, run by the main session on vast.ai; smoke first (10 problems), rows read by hand.

## Offline simulation (run before the spec was committed)

`analysis/cap32vote_sim.py`, output `results/cap32vote/sim-01/readout.md`. Every stored cap hit is redrawn with the cap32 rates:
stays cut 2/93, finishes right 23/93 (uniform, or scaled by the problem's other three samples), else finishes wrong. The vote
then depends on one thing the one-sample run could not measure: whether the late wrong answers of a problem agree with each
other. Stored finished wrong samples of one problem agree in 63.8 % of 69 pairs (hard328) and 75.0 % of 36 (fresh2026).

| hard328, vote over 4 at 32,768 (241 at 16,384) | uniform rate | rate by problem |
|---|---|---|
| late wrong answers all distinct | 256.2 [248, 265] | 254.2 [246, 262] |
| late wrong answers agree at the stored rate (the prediction) | 238.9 [232, 247] | 240.1 [233, 248] |
| late wrong answers of a problem all agree | 232.6 [226, 240] | 234.3 [228, 241] |

fresh2026 (75 at 16,384): 90.1 / 87.4 distinct, 77.2 / 76.8 at the stored rate, 74.4 / 74.7 all agree.

## Hypotheses and predictions

Intervals are the 2.5 to 97.5 percentiles of the simulation's draws; they hold the redraw noise, not the model error.

- H1 (the hypothesis as given): the vote over 4 at 32,768 on hard328 is at least 250. Refuted if the paired interval of the
  32,768 vote minus the 16,384 vote (same answers) covers 0. Prediction: refuted. Vote 239.5 [232, 248], gain over the
  same-answer 16,384 vote -1.5 problems [-9, +7]. The late answers are right 25 % of the time, the 16,384 finished answers
  88 %: at the stored agreement rate the late wrong answers outvote as many right answers as the late right ones add.
- H2: the gain under the vote is smaller in points than the gain of one sample. Prediction: single (mean of 4) 229.0 [224.5,
  233.2], +6.1 points over the stored 209.0; vote gain -0.5 points. Refuted if the vote gain in points is at least the single
  gain.
- H3: on fresh2026 the one-sample gain is larger in points than on hard328. Prediction: single 74.5 [71.2, 78.0] of 136 against
  the stored 60.0: +10.7 points, against +6.1 on hard328. Refuted if the fresh2026 gain in points is at or below hard328's.
  Vote over 4 on fresh2026: 77.0 [71, 83] (75 at 16,384).
- H4, tokens. One sample at 32,768 beats the 16,384 rule that spends the same or more tokens on a second sample. Stored
  16,384 rules on hard328 (24 draw orders): one sample 209.0 at 10,137 tokens; one sample drawn again once after a cap hit
  (`restart1`) 222.0 at 14,330; vote over 2 221.8 at 20,301; `seq3` 233.2 at 26,269; `seq4` 238.9 at 30,904. Prediction: one
  32,768 sample 229 at 11,820 tokens. Refuted if its mean of 4 is at or below 222.0. On fresh2026: `restart1` 68.0 at 19,944,
  `seq4` 75.5 at 42,251; predicted one 32,768 sample 74.5 at 15,600; refuted if at or below 68.0. Second part, predicted from
  the simulation: above about 26,000 tokens per problem the higher cap buys nothing on hard328 (`seq4` at 32,768: 237 at
  30,500, against 238.9 at 30,904). Refuted if `seq4` at 32,768 beats `seq4` at 16,384 (same answers) with an interval above 0.
- P5, the unknown that decides H1: the share of agreeing pairs among late (more than 16,384 tokens) finished wrong answers of
  one problem. Assumed 64 % (hard328), 75 % (fresh2026). If it is below 30 %, the vote is near 254 and H1 holds.
- P6: cap hits at 32,768: 0.6 % of samples on hard328 (8 of 1,312), 1 % on fresh2026. Precision of finished answers falls from
  88.0 % to about 70 % on hard328 and from 80.4 % to about 55 % on fresh2026. Refuted outside 62 to 78 % and 47 to 63 %.
- P7: more than 20 Chinese characters in at least 20 % of the answers past 16,384 tokens (86 of 378 stored cap hits, 23 %).

## Literature

Searched with WebSearch (no Exa key in this session). Abstracts only, so no claim is taken from them: "Does Thinking More
Always Help?" (arXiv 2506.04210) reports that splitting a budget over several traces and voting beats one longer trace;
"Increasing the Thinking Budget is Not All You Need" reports the same direction. Neither has a table for a model whose
finished answers are 88 % right and whose cut answers cast no vote, which is the case here. Team memory (`tools/recall.py`):
result-c8b994 is the only 32,768 measurement; no vote at that cap.
