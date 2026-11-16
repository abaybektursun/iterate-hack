# Stored rows, explore half only

Split rule (studies/theory/data/split_v1.json): For each set, sort its problem ids by the sha256 hex digest of '<set>:<id>' (id as a decimal string, or the code uid such as 'HumanEval/0'); the first floor(n / 2) ids are explore, the rest test. dev100 uses MATH-500's assignment (its ids are MATH-500 indices, key 'math500:<id>'). No seed. Never changed after its first commit.

Problems per set in this half: hard328 164, math500 250, fresh2026 68, code 269, dev100 54.

Each file holds one cell's rows of this half, one JSON object per line, with `pid` added (the problem id). Cells with the same set share problem ids. `cell` is the name a test loads with rows.py.

| file | cell | set | rows | source path |
|---|---|---|---|---|
| math500/cleanneurons__gen__vote_attr1000r2_t06-01.jsonl | cleanneurons/gen/vote_attr1000r2_t06-01 | math500 | 1045 | studies/cleanneurons/results/gen/vote_attr1000r2_t06-01/rows.jsonl |
| fresh2026/rlneurons__cap32vote__fresh2026_sft1_cue_s4-01.jsonl | rlneurons/cap32vote/fresh2026_sft1_cue_s4-01 | fresh2026 | 272 | studies/rlneurons/results/cap32vote/fresh2026_sft1_cue_s4-01/rows.jsonl |
| hard328/rlneurons__cap32vote__hard328_sft1_cue_s4-01.jsonl | rlneurons/cap32vote/hard328_sft1_cue_s4-01 | hard328 | 656 | studies/rlneurons/results/cap32vote/hard328_sft1_cue_s4-01/rows.jsonl |
| math500/rlneurons__ckptcue__s0100_cue-01.jsonl | rlneurons/ckptcue/s0100_cue-01 | math500 | 250 | studies/rlneurons/results/ckptcue/s0100_cue-01/per_problem.json |
| math500/rlneurons__ckptcue__s0100_cue_s123-01.jsonl | rlneurons/ckptcue/s0100_cue_s123-01 | math500 | 750 | studies/rlneurons/results/ckptcue/s0100_cue_s123-01/rows.jsonl |
| math500/rlneurons__ckptcue__s0100_plain-01.jsonl | rlneurons/ckptcue/s0100_plain-01 | math500 | 250 | studies/rlneurons/results/ckptcue/s0100_plain-01/per_problem.json |
| math500/rlneurons__ckptcue__s0100_plain_s123-01.jsonl | rlneurons/ckptcue/s0100_plain_s123-01 | math500 | 750 | studies/rlneurons/results/ckptcue/s0100_plain_s123-01/rows.jsonl |
| math500/rlneurons__ckptcue__s0400_cue-01.jsonl | rlneurons/ckptcue/s0400_cue-01 | math500 | 250 | studies/rlneurons/results/ckptcue/s0400_cue-01/per_problem.json |
| math500/rlneurons__ckptcue__s0400_plain-01.jsonl | rlneurons/ckptcue/s0400_plain-01 | math500 | 250 | studies/rlneurons/results/ckptcue/s0400_plain-01/per_problem.json |
| math500/rlneurons__ckptcue__s0400_plain_s123-01.jsonl | rlneurons/ckptcue/s0400_plain_s123-01 | math500 | 750 | studies/rlneurons/results/ckptcue/s0400_plain_s123-01/rows.jsonl |
| hard328/rlneurons__day1_3__hard328_base_cue_s4r2-01.jsonl | rlneurons/day1_3/hard328_base_cue_s4r2-01 | hard328 | 851 | studies/rlneurons/results/day1_3/hard328_base_cue_s4r2-01/rows.jsonl |
| hard328/rlneurons__day1_3__hard328_rl_plain_s4r2-01.jsonl | rlneurons/day1_3/hard328_rl_plain_s4r2-01 | hard328 | 718 | studies/rlneurons/results/day1_3/hard328_rl_plain_s4r2-01/rows.jsonl |
| hard328/rlneurons__day1_3__hard328_top8x1.5_cue_s4-01.jsonl | rlneurons/day1_3/hard328_top8x1.5_cue_s4-01 | hard328 | 656 | studies/rlneurons/results/day1_3/hard328_top8x1.5_cue_s4-01/rows.jsonl |
| math500/rlneurons__day1_3__math500_base_cue-01.jsonl | rlneurons/day1_3/math500_base_cue-01 | math500 | 1057 | studies/rlneurons/results/day1_3/math500_base_cue-01/rows.jsonl |
| math500/rlneurons__day1_3__math500_rl-01.jsonl | rlneurons/day1_3/math500_rl-01 | math500 | 1020 | studies/rlneurons/results/day1_3/math500_rl-01/rows.jsonl |
| math500/rlneurons__egate__math500_esc3k-01.jsonl | rlneurons/egate/math500_esc3k-01 | math500 | 250 | studies/rlneurons/results/egate/math500_esc3k-01/rows.jsonl |
| math500/rlneurons__egate__math500_hi6-01.jsonl | rlneurons/egate/math500_hi6-01 | math500 | 500 | studies/rlneurons/results/egate/math500_hi6-01/rows.jsonl |
| math500/rlneurons__egate__math500_lo6-01.jsonl | rlneurons/egate/math500_lo6-01 | math500 | 1000 | studies/rlneurons/results/egate/math500_lo6-01/rows.jsonl |
| fresh2026/rlneurons__fresh__base_cue_s4-01.jsonl | rlneurons/fresh/base_cue_s4-01 | fresh2026 | 272 | studies/rlneurons/results/fresh/base_cue_s4-01/rows.jsonl |
| fresh2026/rlneurons__fresh__rl_plain_s4-01.jsonl | rlneurons/fresh/rl_plain_s4-01 | fresh2026 | 272 | studies/rlneurons/results/fresh/rl_plain_s4-01/rows.jsonl |
| fresh2026/rlneurons__fresh__sft1_cue_s4-01.jsonl | rlneurons/fresh/sft1_cue_s4-01 | fresh2026 | 272 | studies/rlneurons/results/fresh/sft1_cue_s4-01/rows.jsonl |
| hard328/rlneurons__relay__rl_c25-01.jsonl | rlneurons/relay/rl_c25-01 | hard328 | 328 | studies/rlneurons/results/relay/rl_c25-01/rows.jsonl |
| hard328/rlneurons__relay__rl_c50-01.jsonl | rlneurons/relay/rl_c50-01 | hard328 | 328 | studies/rlneurons/results/relay/rl_c50-01/rows.jsonl |
| hard328/rlneurons__relay__think_c25-01.jsonl | rlneurons/relay/think_c25-01 | hard328 | 328 | studies/rlneurons/results/relay/think_c25-01/rows.jsonl |
| hard328/rlneurons__relay__think_c50-01.jsonl | rlneurons/relay/think_c50-01 | hard328 | 328 | studies/rlneurons/results/relay/think_c50-01/rows.jsonl |
| math500/rlneurons__repair__offline-01.jsonl | rlneurons/repair/offline-01 | math500 | 2000 | studies/rlneurons/results/repair/offline-01/rows.jsonl |
| math500/rlneurons__rln4__t1_t2_items-01.jsonl | rlneurons/rln4/t1_t2_items-01 | math500 | 250 | studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json |
| math500/rlneurons__rln4__t1_t3_items-01.jsonl | rlneurons/rln4/t1_t3_items-01 | math500 | 250 | studies/rlneurons/results/rln4/t1_t3_items-01/per_problem.json |
| hard328/rlneurons__seen__base_hardmatch-01.jsonl | rlneurons/seen/base_hardmatch-01 | hard328 | 240 | studies/rlneurons/results/seen/base_hardmatch-01/rows.jsonl |
| hard328/rlneurons__seen__rl_hardmatch-01.jsonl | rlneurons/seen/rl_hardmatch-01 | hard328 | 240 | studies/rlneurons/results/seen/rl_hardmatch-01/rows.jsonl |
| hard328/rlneurons__thinkvote__hard328_sft1_cue_s4-01.jsonl | rlneurons/thinkvote/hard328_sft1_cue_s4-01 | hard328 | 656 | studies/rlneurons/results/thinkvote/hard328_sft1_cue_s4-01/rows.jsonl |
| math500/rlneurons__thinkvote__math500_sft1_cue_s4-01.jsonl | rlneurons/thinkvote/math500_sft1_cue_s4-01 | math500 | 1000 | studies/rlneurons/results/thinkvote/math500_sft1_cue_s4-01/rows.jsonl |
| hard328/rlneurons__transplant__cap32_m2_s1-01.jsonl | rlneurons/transplant/cap32_m2_s1-01 | hard328 | 164 | studies/rlneurons/results/transplant/cap32_m2_s1-01/rows.jsonl |
| fresh2026/rlneurons__transplant__fresh2026-01.jsonl | rlneurons/transplant/fresh2026-01 | fresh2026 | 612 | studies/rlneurons/results/transplant/fresh2026-01/rows.jsonl |
| fresh2026/rlneurons__transplant__fresh2026-02.jsonl | rlneurons/transplant/fresh2026-02 | fresh2026 | 816 | studies/rlneurons/results/transplant/fresh2026-02/rows.jsonl |
| hard328/rlneurons__transplant__hard328-01.jsonl | rlneurons/transplant/hard328-01 | hard328 | 2296 | studies/rlneurons/results/transplant/hard328-01/rows.jsonl |
| hard328/rlneurons__transplant__hard328-02.jsonl | rlneurons/transplant/hard328-02 | hard328 | 1804 | studies/rlneurons/results/transplant/hard328-02/rows.jsonl |
| hard328/rlneurons__transplant__hard328_cap32-01.jsonl | rlneurons/transplant/hard328_cap32-01 | hard328 | 164 | studies/rlneurons/results/transplant/hard328_cap32-01/rows.jsonl |
| math500/rlneurons__transplant__math500-01.jsonl | rlneurons/transplant/math500-01 | math500 | 2250 | studies/rlneurons/results/transplant/math500-01/rows.jsonl |
| math500/rlneurons__votek__math500_base_cue-01.jsonl | rlneurons/votek/math500_base_cue-01 | math500 | 3000 | studies/rlneurons/results/votek/math500_base_cue-01/rows.jsonl |
| math500/rlneurons__wsp1__full500__rand8_plain-01.jsonl | rlneurons/wsp1/full500/rand8_plain-01 | math500 | 250 | studies/rlneurons/results/wsp1/full500/rand8_plain-01/per_problem.json |
| math500/rlneurons__wsp1__full500__sft1_cue-01.jsonl | rlneurons/wsp1/full500/sft1_cue-01 | math500 | 250 | studies/rlneurons/results/wsp1/full500/sft1_cue-01/per_problem.json |
| math500/rlneurons__wsp1__full500__sft1_plain-01.jsonl | rlneurons/wsp1/full500/sft1_plain-01 | math500 | 250 | studies/rlneurons/results/wsp1/full500/sft1_plain-01/per_problem.json |
| math500/rlneurons__wsp1__full500__top8_plain-01.jsonl | rlneurons/wsp1/full500/top8_plain-01 | math500 | 250 | studies/rlneurons/results/wsp1/full500/top8_plain-01/per_problem.json |
| hard328/rlneurons__wsp1__hard328__sft1_cue-01.jsonl | rlneurons/wsp1/hard328/sft1_cue-01 | hard328 | 164 | studies/rlneurons/results/wsp1/hard328/sft1_cue-01/per_problem.json |
| hard328/rlneurons__wsp1__hard328__sft1_plain-01.jsonl | rlneurons/wsp1/hard328/sft1_plain-01 | hard328 | 164 | studies/rlneurons/results/wsp1/hard328/sft1_plain-01/per_problem.json |
| math500/rlneurons__wsp2__full500__cueprog_plain-01.jsonl | rlneurons/wsp2/full500/cueprog_plain-01 | math500 | 250 | studies/rlneurons/results/wsp2/full500/cueprog_plain-01/per_problem.json |
| math500/rlneurons__wsp2__full500__cueprog_rand_plain-01.jsonl | rlneurons/wsp2/full500/cueprog_rand_plain-01 | math500 | 250 | studies/rlneurons/results/wsp2/full500/cueprog_rand_plain-01/per_problem.json |
| hard328/rlneurons__xreward__depth3__rand8x1.5_L0-10_math31_s1-01.jsonl | rlneurons/xreward/depth3/rand8x1.5_L0-10_math31_s1-01 | hard328 | 164 | studies/rlneurons/results/xreward/depth3/rand8x1.5_L0-10_math31_s1-01/rows.jsonl |
| hard328/rlneurons__xreward__depth3__top8x1.5_L0-10_math31_s1-01.jsonl | rlneurons/xreward/depth3/top8x1.5_L0-10_math31_s1-01 | hard328 | 164 | studies/rlneurons/results/xreward/depth3/top8x1.5_L0-10_math31_s1-01/rows.jsonl |
| hard328/rlneurons__xreward__depth3__top8x1.5_L0-10_math31_s2-01.jsonl | rlneurons/xreward/depth3/top8x1.5_L0-10_math31_s2-01 | hard328 | 164 | studies/rlneurons/results/xreward/depth3/top8x1.5_L0-10_math31_s2-01/rows.jsonl |
| hard328/rlneurons__xreward__depth3__top8x1.5_L0-10_math31_s3-01.jsonl | rlneurons/xreward/depth3/top8x1.5_L0-10_math31_s3-01 | hard328 | 164 | studies/rlneurons/results/xreward/depth3/top8x1.5_L0-10_math31_s3-01/rows.jsonl |
| hard328/rlneurons__xreward__depth3__top8x1.5_L11-21_math31_s1-01.jsonl | rlneurons/xreward/depth3/top8x1.5_L11-21_math31_s1-01 | hard328 | 164 | studies/rlneurons/results/xreward/depth3/top8x1.5_L11-21_math31_s1-01/rows.jsonl |
| hard328/rlneurons__xreward__depth3__top8x1.5_L22-31_math31_s1-01.jsonl | rlneurons/xreward/depth3/top8x1.5_L22-31_math31_s1-01 | hard328 | 164 | studies/rlneurons/results/xreward/depth3/top8x1.5_L22-31_math31_s1-01/rows.jsonl |
| hard328/rlneurons__xreward__depth3__top8x1.5_d2-8_math31_s1-01.jsonl | rlneurons/xreward/depth3/top8x1.5_d2-8_math31_s1-01 | hard328 | 164 | studies/rlneurons/results/xreward/depth3/top8x1.5_d2-8_math31_s1-01/rows.jsonl |
| math500/rlneurons__xreward__dial15_math500-01.jsonl | rlneurons/xreward/dial15_math500-01 | math500 | 250 | studies/rlneurons/results/xreward/dial15_math500-01/rows.jsonl |
| hard328/rlneurons__xreward__dial15_s4_vs_base_cue-01.jsonl | rlneurons/xreward/dial15_s4_vs_base_cue-01 | hard328 | 656 | studies/rlneurons/results/xreward/dial15_s4_vs_base_cue-01/rows.jsonl |
| hard328/rlneurons__xreward__dial15_s4_vs_rl_plain-01.jsonl | rlneurons/xreward/dial15_s4_vs_rl_plain-01 | hard328 | 656 | studies/rlneurons/results/xreward/dial15_s4_vs_rl_plain-01/rows.jsonl |
| hard328/rlneurons__xreward__normband__top1x1.5_math31_s0-01.jsonl | rlneurons/xreward/normband/top1x1.5_math31_s0-01 | hard328 | 164 | studies/rlneurons/results/xreward/normband/top1x1.5_math31_s0-01/rows.jsonl |
| hard328/rlneurons__xreward__normband__top1x1.5_math31_s1-01.jsonl | rlneurons/xreward/normband/top1x1.5_math31_s1-01 | hard328 | 164 | studies/rlneurons/results/xreward/normband/top1x1.5_math31_s1-01/rows.jsonl |
| hard328/rlneurons__xreward__normband__top8x0.2_L0-10_math31_s1-01.jsonl | rlneurons/xreward/normband/top8x0.2_L0-10_math31_s1-01 | hard328 | 164 | studies/rlneurons/results/xreward/normband/top8x0.2_L0-10_math31_s1-01/rows.jsonl |
| hard328/rlneurons__xreward__normband__top8x1.5_d2-8_math31_s0-01.jsonl | rlneurons/xreward/normband/top8x1.5_d2-8_math31_s0-01 | hard328 | 164 | studies/rlneurons/results/xreward/normband/top8x1.5_d2-8_math31_s0-01/rows.jsonl |
| hard328/rlneurons__xreward__normband__top8x3_L22-31_math31_s1-01.jsonl | rlneurons/xreward/normband/top8x3_L22-31_math31_s1-01 | hard328 | 164 | studies/rlneurons/results/xreward/normband/top8x3_L22-31_math31_s1-01/rows.jsonl |
| hard328/rlneurons__xreward__normband__top8x4.5_L22-31_math31_s1-01.jsonl | rlneurons/xreward/normband/top8x4.5_L22-31_math31_s1-01 | hard328 | 164 | studies/rlneurons/results/xreward/normband/top8x4.5_L22-31_math31_s1-01/rows.jsonl |
| hard328/theory__direct__template-01.jsonl | theory/direct/template-01 | hard328 | 984 | studies/theory/results/direct/template-01/rows.jsonl |
| fresh2026/theory__experiments__cell-m20-01.jsonl | theory/experiments/cell-m20-01 | fresh2026 | 68 | studies/theory/results/experiments/cell-m20-01/per_problem.json |
| math500/theory__experiments__cell-m29-01.jsonl | theory/experiments/cell-m29-01 | math500 | 250 | studies/theory/results/experiments/cell-m29-01/per_problem.json |
| math500/theory__experiments__cell-r9-m18-01.jsonl | theory/experiments/cell-r9-m18-01 | math500 | 250 | studies/theory/results/experiments/cell-r9-m18-01/per_problem.json |
| math500/theory__experiments__selfopen-01.jsonl | theory/experiments/selfopen-01 | math500 | 250 | studies/theory/results/experiments/selfopen-01/per_problem.json |
| math500/theory__experiments__top8x4-01.jsonl | theory/experiments/top8x4-01 | math500 | 250 | studies/theory/results/experiments/top8x4-01/per_problem.json |
| hard328/autobench__math500-loop__finals-01__hard328-karpathy-000.jsonl | autobench/math500-loop/finals-01/hard328-karpathy-000 | hard328 | 164 | studies/autobench/results/math500-loop/finals-01/hard328-karpathy-000.json |
| hard328/autobench__math500-loop__finals-01__hard328-swarm-cue-004.jsonl | autobench/math500-loop/finals-01/hard328-swarm-cue-004 | hard328 | 164 | studies/autobench/results/math500-loop/finals-01/hard328-swarm-cue-004.json |
| hard328/autobench__math500-loop__finals-01__hard328-swarm-vote4-003.jsonl | autobench/math500-loop/finals-01/hard328-swarm-vote4-003 | hard328 | 164 | studies/autobench/results/math500-loop/finals-01/hard328-swarm-vote4-003.json |
| math500/autobench__math500-loop__finals-01__math400-karpathy-000.jsonl | autobench/math500-loop/finals-01/math400-karpathy-000 | math500 | 196 | studies/autobench/results/math500-loop/finals-01/math400-karpathy-000.json |
| math500/autobench__math500-loop__finals-01__math400-swarm-cue-004.jsonl | autobench/math500-loop/finals-01/math400-swarm-cue-004 | math500 | 196 | studies/autobench/results/math500-loop/finals-01/math400-swarm-cue-004.json |
| math500/autobench__math500-loop__finals-01__math400-swarm-vote4-003.jsonl | autobench/math500-loop/finals-01/math400-swarm-vote4-003 | math500 | 196 | studies/autobench/results/math500-loop/finals-01/math400-swarm-vote4-003.json |
| code/rlneurons__code1__rl_plain.jsonl | rlneurons/code1/rl_plain | code | 269 | runs/abaybektursun-1114-170253-f661/answers.jsonl |
| code/rlneurons__code1__base_plain.jsonl | rlneurons/code1/base_plain | code | 269 | runs/abaybektursun-1114-170258-388e/answers.jsonl |
| code/rlneurons__code1__base_cue.jsonl | rlneurons/code1/base_cue | code | 269 | runs/abaybektursun-1114-170304-c03c/answers.jsonl |
| code/rlneurons__code1__base_mathcue.jsonl | rlneurons/code1/base_mathcue | code | 269 | runs/abaybektursun-1114-170309-b137/answers.jsonl |
| (not here: S3, not cached) | rlneurons/code_think/sft1_codecue | code | - | runs/ih-1115-185836-e7ef/codecue/answers.jsonl |
| (not here: S3, not cached) | rlneurons/code_think/sft1_mathcue | code | - | runs/ih-1115-185836-e7ef/mathcue/answers.jsonl |
| code/rlneurons__xreward__code_depth__code_rand8x1.5_code31.jsonl | rlneurons/xreward/code_depth/code_rand8x1.5_code31 | code | 269 | runs/abaybektursun-1115-101457-ef2c/answers.jsonl |
| code/rlneurons__xreward__code_depth__code_top8x1.5_code31.jsonl | rlneurons/xreward/code_depth/code_top8x1.5_code31 | code | 269 | runs/abaybektursun-1115-101434-4511/answers.jsonl |
| (not here: S3, not cached) | rlneurons/xreward/code_depth/code_top8x1.5_L0-10_code31 | code | - | runs/abaybektursun-1115-120127-70c3/answers.jsonl |
| (not here: S3, not cached) | rlneurons/xreward/code_depth/code_top8x1.5_L11-21_code31 | code | - | runs/abaybektursun-1115-120138-c4be/answers.jsonl |
| (not here: S3, not cached) | rlneurons/xreward/code_depth/code_top8x1.5_L22-31_code31 | code | - | runs/abaybektursun-1115-120151-bee2/answers.jsonl |
| code/rlneurons__xreward__code_dial__code_top8_code31.jsonl | rlneurons/xreward/code_dial/code_top8_code31 | code | 269 | runs/abaybektursun-1115-101423-4a7d/answers.jsonl |
| code/rlneurons__xreward__code_dial__code_top8x2_code31.jsonl | rlneurons/xreward/code_dial/code_top8x2_code31 | code | 269 | runs/abaybektursun-1115-101445-e35e/answers.jsonl |
| code/rlneurons__xreward__code_dial__code_top8x1.5_math31.jsonl | rlneurons/xreward/code_dial/code_top8x1.5_math31 | code | 269 | runs/abaybektursun-1115-101508-33f0/answers.jsonl |
| (not here: S3, not cached) | rlneurons/xreward/code_hosts/math1.5_code1.5 | code | - | runs/abaybektursun-1115-130332-eba9/answers.jsonl |
| (not here: S3, not cached) | rlneurons/xreward/code_hosts/math1_code1 | code | - | runs/abaybektursun-1115-130400-064d/answers.jsonl |
| (not here: S3, not cached) | rlneurons/xreward/code_hosts/math1.5_rand1.5 | code | - | runs/abaybektursun-1115-130426-5898/answers.jsonl |
| (not here: S3, not cached) | rlneurons/xreward/code_hosts_s52/math1_code1 | code | - | runs/abaybektursun-1115-143215-6942/answers.jsonl |
| code/rlneurons__xreward__code_hosts_s52__code_top8_code31.jsonl | rlneurons/xreward/code_hosts_s52/code_top8_code31 | code | 269 | runs/abaybektursun-1115-143231-15bb/answers.jsonl |
| code/rlneurons__xreward__code_hosts_s52__rl_plain.jsonl | rlneurons/xreward/code_hosts_s52/rl_plain | code | 269 | runs/abaybektursun-1115-143247-929d/answers.jsonl |
| (not here: S3, not cached) | rlneurons/xreward/code_hosts_s53/math1_code1 | code | - | runs/abaybektursun-1115-143301-ec55/answers.jsonl |
| code/rlneurons__xreward__code_hosts_s53__code_top8_code31.jsonl | rlneurons/xreward/code_hosts_s53/code_top8_code31 | code | 269 | runs/abaybektursun-1115-143316-628e/answers.jsonl |
| code/rlneurons__xreward__code_hosts_s53__rl_plain.jsonl | rlneurons/xreward/code_hosts_s53/rl_plain | code | 269 | runs/abaybektursun-1115-143331-10da/answers.jsonl |
