# lenvote: a vote weighted by agreement-calibrated answer length

Written 2026-11-16. Board: the work item names this file. Offline, stored rows only, no GPU.

## What was looked at before this was written (stated so the reader can discount it)

1. `results/cap32/`: at cap 32,768 a Think-SFT answer longer than 16,384 tokens is right 23 times of 93; shorter ones about 9 of 10.
2. A trial of the rule below on the MATH-500 rows (`results/thinkvote/math500_sft1_cue_s4-01/rows.jsonl`, cap 16,384) with 3, 5
   and 8 length bins: plain vote 481, weighted 481, 482, 482. 5 bins was fixed there.
3. Then the fixed rule was run once on the 328 at both caps and on fresh2026: the numbers in the README. Another session had
   already seen that ties to the shortest answer help at 32,768 and gave it no score as post hoc (board result-dd26fe).

So the rule's form and its one free number were fixed on MATH-500, where it changes nothing; the 328 and fresh2026 numbers are
one scoring each. The motive came from the 328 (item 1), so fresh2026 is the cleaner test.

## Rule (label-free; sees n_new, cap_hit and extracted_v3 of each sample, never the score)

1. Group a problem's finished samples by equal answer (`rln4_lib.agree` on `norm_v3`).
2. Calibration without labels, on the same set: split all finished samples of the set into 5 bins of equal count by generated
   tokens. For each bin, a = (samples whose answer another sample of the problem shares + 1) / (samples + 2).
3. A sample's weight is log(a / (1 - a)) of its bin. A group's score is the sum of its samples' weights. Answer with the
   group of the highest score; ties to the group holding the shortest sample.

Compared with: plain plurality (ties to the lowest sample), plurality with ties to the shortest, and the shortest finished
sample alone. Paired bootstrap over problems, 10,000 resamples, seed 0.

## Hypotheses and what refutes each

- H1: at cap 32,768 the weighted vote beats the plain vote on fresh2026 (4 samples, 136 problems) with a paired 95 % interval
  above 0. Refuted if the interval includes 0.
- H2: the gain needs the long answers that the larger cap lets finish: at cap 16,384 on the 328 the gain is within the interval
  of 0. Refuted if it gains there too.
- Control for "any length rule does it": ties to the shortest and shortest-alone are reported beside it. If the weighted vote
  does not beat ties-to-shortest, the result is "prefer short answers at a large cap", and the calibration adds nothing.
