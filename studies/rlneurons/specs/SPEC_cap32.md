# cap32: the token cap doubled to 32,768 on the 328

Written 2026-11-15 before any run. Board: work-ceccc0.

## Question

Think-SFT with the cue scores 219 (job sameraslan-1114-204845-1055) and 212 (job abaybektursun-1115-000503-1e5f) of 328 at the
cap of 16,384 generated tokens, with 89 answers cut at the cap in both runs. So at most about 20 of its finished answers are
wrong, and most of its misses are unfinished answers. For the cued base, a forced commit at the cap is right on 0 to 2 of 77
(`results/commit1/`): its cap hits are failures to solve. Are Think-SFT's cap hits unfinished work that more tokens complete?

## Measurement

`run_cell --set hard328 --max-tokens 32768`, T 1.0 / top-p 1.0, grader v3, one sample, seed 3000000, on vast.ai:

- Think-SFT cue (`wsp_edit --recipe interp --other think_sft --alpha 1.0`, as job 1e5f),
- RL plain (the same change for the RL model; 20 cap hits at 16,384),
- base cue (77 cap hits at 16,384).

Each cell gives two scores from the same answers: right at 32,768, and right with at most 16,384 generated tokens (the score
the same run would have had at the old cap, up to answers that were right before being cut: 3 of 77 for the base). The
difference is paired inside one run. Tokens per problem are reported at both caps.

## Hypotheses and what refutes each

- H1: Think-SFT gains at least 15 problems from the second 16,384 tokens (above 234 if the run's 16,384 score is 219).
  Refuted if it gains fewer than 8: then its cap hits are failures to solve, like the base's.
- H2: the base gains fewer than 8 (its cap hits are failures). Refuted if it gains 15 or more.
- H3: RL gains at most 5 (it has 20 cap hits). Refuted otherwise.
- Instrument: each cell's score at 16,384 must lie within 12 problems of the stored cell at that cap (two SD of identical
  requests is about 11): Think-SFT 212 to 219, RL plain 206, base cue 164. Outside that, the box's cell is not comparable and
  is rerun.

## Order

Smoke on each box: `--n 8 --max-tokens 32768`, check answers.jsonl and that an answer longer than 16,384 tokens exists or all
finished. Then the three full cells, one box each. Readout `analysis/cap32.py` to `results/cap32/`.
