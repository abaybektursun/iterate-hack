# Notes: depth/rank paper data layer

`uv run --no-project --with numpy python studies/rlneurons/paper-depth-rank/build_facts.py` writes `facts.json` and `problem_table.json` from git files (158 + 79 readout checks pass). `prep_rows.py` and `prep_degenerate.py` froze `data/` from `runs/` and wrote `examples.json`. Degenerate answer: the most frequent word is more than 20 % of the words in an answer of 200 or more words.

## Pre-registration (`preregistration`, `normband`, `no_cue`, `review.10`)
- SPEC_depth3 came before its jobs. Its sample 0 was the source of the depth reading and is pooled into B1, B2, B4 and B5. All 7 predictions held.
- On Code, L1 and L2 were refuted and L3 held.
- SPEC_normband amendment 1 followed unscored smoke runs. P5 was committed after two band jobs had started. P2, P4 and P6 held, P3 was not held, P5's right-answer part and P7 were refuted.
- Samples: 1 for the no-cue cells, random cells, direction 1 at 1x/2x/3x and every Code cell. Same-seed reruns differ by up to 4 right.
- 745+ intervals: use 99 %.
- Board mismatches are listed in `board_checks` and the first report: 306787 references, 6f7ca3 "+7.3", 98de28 "0.83" at layer 24.

## Against the thesis
Claim: right answers come from the whole spectrum, finishing needs direction 1, and without the cue directions 2-8 open like the cue (+34 points) while direction 1 adds 8.

1. With the cue, direction 1 minus d2-8 is -2.0 [-4.9, 0.9] right and -8.7 cut-offs, so the two halves are not separated on right answers. Direction 1 gains 13.5 problems among finished answers. On top of direction 1, d2-8 cut cut-offs by -6.7 [-9.4, -4.1]. The parts sum to 1.33 [1.07, 1.59] of all 8.
2. **Without the cue the plain base barely reasons.** It opens with 'Okay' on 52 of 328, and 25 answers are under 20 words. 109 of d2-8's 112-problem gain falls on the 276 problems where the base did not reason. Where the base did reason (52), the gain is +5.8 [-5.8, 17.3]. So "+34" largely measures starting to reason.
3. Without the cue, d2-8 add cut-offs: +12.8 [7.9, 17.7], and +14.6 over RL plain (seed-matched). They do change finishing.
4. d2-8 plain equals d2-8 cued (-0.8) and RL plain (-0.9 seed-matched). The cue and d2-8 are substitutes: the plain-minus-cued difference in the d2-8 effect is +27.4 [21.0, 33.8].
5. Direction 1 plain gives +7.9 [2.7, 12.8] with +512 [18, 1014] tokens. Its gain sits on non-reasoning problems (+9.8 there, -1.9 where the base reasoned). It opens with 'Okay' on 79 vs 52. Its plain-minus-cued difference is +1.5 [-4.9, 7.6].
6. All no-cue cells have 1 sample. The two plain-base jobs (seeds 3.01M and 50M) differ by +0.3 [-4.9, 5.5].
7. L22-31 at 3.0x over 2 samples: -1.2 [-3.9, 1.5] right, -13.4 cut-offs. Right among finished drops to 51.4 %.
8. On Code, L0-10 cut cut-offs and L22-31 cuts none.

## Missing cell
A second plain-base sample and direction 1 + d2-8 together without the cue (all 8 plain).
