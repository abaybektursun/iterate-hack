# RLN-3 — what the Olmo math RL run adds beyond an opening and a stop rule

Frozen 2026-11-13, before any RLN-3 generation exists. Inputs: `rln3/inputs/` (`frozen.json` holds every number below that
the job reads). Code: `infra/aws_pg/jobs/rln3_gen.py` (job), `rln3_prep.py` (inputs and laptop checks), `rln3_offline.py`
(offline gate), `rln3_analyze.py` (readout and verdict).

Question. The RL model (`Olmo-3.1-7B-RL-Zero-Math`, step 2,800) scores 92.0 on MATH-500 where the base scores 57.2 (n13, one
sample, cap 16,384). How much of that is reached by the base model when (F) its answer starts with the RL model's own
opening and (C) it is forced to state an answer after N tokens? Does the rest show on harder problems?

## 0. What is already published, and how this run differs

Wang et al., arXiv 2610.06851 ("Base Models Can Reason By Taking a Cue From Training Data"; HTML full text read 2026-11-13,
§3, App. B.1-B.2, Tables 3, 5, 7). Their setup: `Olmo-3-7B` base and the first-release `Olmo-3-7B-RL-Zero-Math`; plain-text
prompt with no chat template ("Solve the following math problem step by step. ..."); the cue ".\n\n" + "Okay" prefilled
after the prompt; 32 samples, temperature 0.6, top-p 0.95, 31,744-token budget, generation also stopped at a new
"Problem:" block; Math-Verify on the last "Answer:" line. Their numbers (pass@1, %): MATH-500 base 42, base + cue 78, RL 75;
AMC 23 / AIME 2024 / AIME 2025: base 30.9 / 12.0 / 11.8, base + cue 59.5 / 23.3 / 22.7, RL 66.2 / 35.2 / 30.0. So for the
first release, "the opening reaches RL on MATH-500 but not on AMC/AIME" is in their Table 7 already. Cap rate on MATH-500
with the cue: 0.16 (no cue 0.12); mean tokens 6,700 (no cue 4,779).

This run differs from Wang 2610.06851 in:
1. the 3.1 RL run (16k completion length in training) at steps 100, 400 and 2,800, plus the first release, with the base;
2. a forced-commit arm C (a stop rule at N tokens) on both P and F, which they do not test;
3. the prefill is the RL step-2,800 model's own opening under our prompt (" line!\n\nOkay"), not a searched cue;
4. our prompt is n13's (the 3.1 chat template: "Solve the following problem step by step. ..."; no "math"), our cap is
   16,384 (not 31,744), our extractor is n13's (last "Answer:" line, else last box) with n13's grader rule `dollar_both`;
5. a harder set of 400 (AIME 2022-2025, AMC 23, HMMT Feb 2025, OlympiadBench) instead of AMC 23 + AIME 2024/2025;
6. failure classes (non-attempt, cap hit with and without a loop, finished-wrong) and accuracy on problems both cells finish;
7. at most 4 samples on MATH-500 and 1 or more on the harder set (§4, §8: 1 each expected at the projected rate), not 32.

The reason for the fifth model (coordinator, 2026-11-13): AI2's report (arXiv 2512.13961v2, App. A.6.4) states that the 3.1
run differs from the first release mainly by a 16k instead of 12k completion length and by not masking truncated rollouts.
That paper was not read by this session; the claim is the coordinator's and is recorded as such.

## 1. Models (commits read from the Hugging Face refs API on 2026-11-13)

| name | repo | branch | commit |
|---|---|---|---|
| base | allenai/Olmo-3-1025-7B | main | a81bae42db3975be1671e27b9c9a56da1a9f980f |
| s0100 | allenai/Olmo-3.1-7B-RL-Zero-Math | step_0100 | 0a45720ccbf23c0aa255a28119787538a48dd56b |
| s0400 | allenai/Olmo-3.1-7B-RL-Zero-Math | step_0400 | 897c0ce4b2e39f6802515f3c1a4e1cf53995af78 |
| s2800 | allenai/Olmo-3.1-7B-RL-Zero-Math | main | 364820b002fc8e81d11a81c7fc9dd6b49c83cd05 |
| fr | allenai/Olmo-3-7B-RL-Zero-Math | main | dee26a4074b88215cd1326472e1ab14d0259d892 |

- `main` of the 3.1 repo and its `step_2800` branch (966de016…) carry the same three shard LFS oids: main is step 2,800.
- The first release's `main` shards differ from its last step branch listed (`step_1900`); `main` is used as its final checkpoint.
- Every shard's sha256 is checked on the instance against the LFS oid of that commit (G-WEIGHTS).
- Prompt and detokenizer for every model: the 3.1 tokenizer at 364820b0 (as n13 did for the base). The first release's
  tokenizer assigns 11 added-token ids (100256, 100266-100275) other names (`<think>`, `<|assistant|>`, …); every other id is
  the same. The job counts generated ids in that range per answer (`n_special_ids`).
- Confound recorded: the first release's own chat template says "Solve the following **math** problem step by step"; this run
  gives it n13's prompt (without "math"), the same bytes as every other model.

## 2. Data

- **MATH-500**: n13's 500 rows (`HuggingFaceH4/MATH-500` @ 6e4ed1a2, banked in n13's `problems.json`); the MATH-500 prompt
  ids must equal n13's banked `prompt_ids.json` (checked in the job).
- **Harder set, 400 problems** (`rln3/inputs/hard.json`, sha256 in `frozen.json`):

| source | HF repo @ commit | rows | kept |
|---|---|---|---|
| AIME 2022, 2023, 2024 | project-numina/aimo-validation-aime @ 13f9e12f | 90 | 30 + 30 + 30 |
| AIME 2025 (I and II) | MathArena/aime_2025 @ c94da77e | 30 | 30 |
| AMC 23 | math-ai/amc23 @ 80815d37 | 40 | 40 (gold 27.0 written as 27) |
| HMMT Feb 2025 | MathArena/hmmt_feb_2025 @ 6fdc4277 | 30 | 30 |
| OlympiadBench OE_TO_maths_en_COMP | Hothan/OlympiadBench @ 91184b52 | 674 | 210 drawn (seed 0) from 573 eligible |

  OlympiadBench drops: 93 with more than one final answer, 8 with a unit (1 more carries an error tolerance and also a unit);
  all 674 are text-only English. Every kept gold grades equal to itself under n13's grader (0 dropped for that); G-GRADER on
  the 400 golds passes (planted pairs, self-equality, derangement rate).

## 3. Arms

- **P** (plain): n13's prompt, generation from the prompt.
- **F** (prefill): the prompt followed by the token ids [1584, 2268, 33413] = " line" "!\n\n" "Okay". Rule: the most common
  opening of the RL step-2,800 answers in n13's saved MATH-500 generations (`s3://pg-lineage-769063704696/results/next_n13/
  s3gate-03/out/rl/rl/math500/generations.jsonl`), re-tokenized: 494 of 500 share the first four tokens " line", "!\n\n",
  "Okay", ","; the other 6 open " tag", ".". The literal first two tokens (" line!\n\n") only close the prompt's last sentence
  ("…on its own line after "Answer:"" → " line!"); they carry no reasoning start. Wang's cue is the sentence close ".\n\n"
  plus "Okay". So the prefill is the RL opening through its first reasoning word: three tokens, not two. The base itself opens
  ".\n\n" in most answers (".\n\n" "Okay" 168 of 500). The 3 prefill tokens do not count toward the 16,384 new tokens.
- **C** (forced commit), on P and on F: an answer whose stop token is not among its first N generated tokens is cut at N
  tokens; the commit string "\n\nFinal answer: \\boxed{" (ids [271, 19918, 4320, 25, 1144, 80175, 90]) is appended, and the
  model continues for at most 100 tokens (same seed as the parent, same sampling). The C answer is the content of the box the
  commit opened (the last balanced box of commit + continuation); no closed box = no answer. Answers that finished within N
  keep their P (or F) record. C is computed from the P and F generations, so it needs only the short continuations.
- **N = 11,911**: the ceiling of the 95th percentile (numpy linear, 11,910.5) of the generated length of the 484 finished RL
  step-2,800 answers in n13's saved MATH-500 generations. Fixed before any RLN-3 output; no accuracy enters it. (N is close to
  the first release's 12k training length; that was not the reason for the rule.)

## 4. Engine, sampling, samples

- n13 unchanged: vLLM 0.32.0 in the n13 venv (`n13_setup.venv_n13`), bf16, `max_model_len` 18,432, `gpu_memory_utilization`
  0.90, prefix caching, `generation_config="vllm"`, engine seed 0, FLASH_ATTN, FlashInfer sampler off; sampling
  `n13_gen.SAMPLING` (temperature 0.6, top-p 0.95, stop id 100257, logprobs 0); cap 16,384 new tokens; extractor
  `n13_score.extract`, grader `n13_score.grade` (`dollar_both`, math-verify 0.9.0).
- Seeds: MATH-500 1,000,000 + 10,000·sample + index (sample 0 = n13's seed set A); harder set 3,000,000 + 10,000·sample +
  index. P and F share seeds; a C continuation takes its parent's seed.
- **Samples, decided before launch: MATH-500 up to 4, harder set 1 (1 and 1 expected on the hardware used, §8).** Rule in the job: after sample 0 of every cell, MATH-500
  samples 1-3 run only if they fit the job's allowance at the measured seconds per sample; then extra harder-set samples run
  under the same rule (at most 8 in all). The readout uses, per set, the largest k such that samples 0..k-1 are complete in all
  five models.
- Hardware: AWS `g7e.2xlarge` (1 × RTX PRO 6000 Blackwell Server, 96 GB) for all five models; the same type for every model.
  n13 ran on L40S; the first GPU check (§5) decides whether this engine reproduces n13. (Dated change before any output,
  2026-11-13 ~01:30Z: the spec first named `p5.4xlarge`; two launch attempts returned InsufficientInstanceCapacity in every
  AZ. Vast.ai credit is $20.65, below the cost of this run on any GPU there. `g7e.2xlarge` is the remaining single-GPU AWS type
  with more memory bandwidth than the L40S.) Second dated change, ~01:45Z, still before any output of the other models: the
  base job launched on `g7e.2xlarge` at 01:24Z; `g7e` then had no capacity for the next three launches, so the other models
  take the first of `g7e.2xlarge`, `g7e.4xlarge` (same GPU) or `p5.4xlarge` (H100) that launches. Each model's GPU is recorded
  (`metrics.json` → `memory.gpu`). Across models the texts differ anyway (different weights), so the GPU affects a comparison
  only through numerical noise and through how many extra samples fit; the readout uses the common sample count. The G-family quota is 32 vCPU = four `g7e.2xlarge`, so s0100 and s0400 run in
  sequence on one instance (`jobs/pipeline.py`, s0400 second: the coordinator's first model to drop).

## 5. Checks (each has an input that fails it)

| check | passes if | failing input (must fail) |
|---|---|---|
| grader reproduction (laptop) | n13's extractor + grader on the saved texts give 286/500 (base) and 460/500 (RL), every record's mode, extraction and score equal to the banked ones | the golds deranged (seed 1) |
| G-GRADER, both sets | planted 24 equal / 16 unequal pairs, every gold equal to itself, derangement rate ≤ identical rate + 0.01 | the derangement scored as identity |
| G-TEMPLATE | every prompt equals the pair1 bytes; MATH-500 ids equal n13's banked ids | the render without the generation suffix |
| G-PREFILL | every F request = prompt ids + the 3 prefill ids; every P request = prompt ids | an F request without the prefill (offline) |
| G-COMMIT | each C request = parent request + parent's first N generated ids + commit ids, max 100 tokens, sent only for a parent not finished within N | a request cut at N + 1 (offline) |
| G-WEIGHTS | every shard sha256 = the LFS oid at the frozen commit | another model's oids |
| G-CHECK (GPU, first stage of the base and s2800 jobs) | sample 0 of P on MATH-500 lies in n13's Wilson 95 % interval: base [52.8, 61.5], s2800 [89.3, 94.1]; else the job stops (exit 3) | offline: the RL texts served to the base job |
| G-COMPLETE | per set, at least one sample complete in every model, every cell | one record removed (offline) |
| G-SEEDS | every record's seed is the registered one | — (recomputed from the record) |
| instrument | identity pair (base P vs itself): difference 0, interval [0, 0]; planted pair (60 problems set right): interval above 0 | — |
| loop ratio | on n13's saved answers: base 60 of 69 cap hits < 0.10, RL 7 of 16; 0 of the finished answers of 8,000+ characters (53 base, 249 RL) < 0.10 | the finished answers |

Offline gate (laptop, no model forward): `rln3_offline.py` → `rln3/offline/offline_gate.json`; prep checks →
`rln3/offline/prep_checks.json`. Result in §10.

## 6. Readout per cell (model × arm × set)

- Accuracy: mean score over problems and the common samples, in points.
- Failure classes for P and F: right; non-attempt (finished, wrong, fewer than 64 generated tokens); cap hit with a loop (zlib
  compression ratio of the last 8,000 characters < 0.10); cap hit without a loop; finished-wrong (with and without an
  extracted answer). For C: the same for answers finished within N; for cut answers: right, commit-wrong, commit not closed.
- Cap-hit share; mean generated tokens (C: N + 7 + continuation for cut answers).
- Paired differences between cells: per-problem means over samples, bootstrap over problems (2,000 resamples, seed 0,
  95 % percentile interval; `n13_score.paired_bootstrap`), in points. Also restricted to (problem, sample) pairs where both
  cells finished (P/F: no cap hit; C: committed box closed or finished within N).
- Raw generations banked for every cell; the report quotes one right and one wrong sample-0 instance per cell (for C, a cut
  answer when one exists) with problem, gold, extraction and answer probability.

## 7. Frozen outcomes (absolute points)

Let D(set) = accuracy(s2800 best arm) − accuracy(base F+C), the best arm being the highest of P, F, P+C, F+C on that set
(chosen on the same data; recorded). Label per set: MATCHES if the 95 % interval contains 0 and its upper end ≤ 6 points;
FALLS SHORT if its lower end > 0; EXCEEDS if its upper end < 0; UNDECIDED if it contains 0 with upper end > 6 (no power).

- **(a)** MATCHES on both sets.
- **(b)** MATCHES on MATH-500 and FALLS SHORT on the harder set.
- **(c)** On the harder set, the P cap-hit share falls by at least 5 points from base to s2800, and C does not recover it for
  the base: base F+C − base F < 2 points with its interval's upper end < 5 points. The cap-hit share at base, 100, 400, 2,800 is
  reported. (c) can hold together with (a) or (b).
- **First release (coordinator's frozen prediction)**: the s2800 − fr accuracy difference (P) lies on problems the first
  release does not finish, and forced commit on the first release closes it. Per set: UNDECIDED if the s2800 P − fr P interval
  contains 0 (no difference to locate); REFUTED if the difference restricted to pairs both finish has its interval above 0;
  SUPPORTED if that restricted interval contains 0 and s2800 P − fr P+C contains 0; otherwise PARTLY. The restriction to
  finished pairs selects on difficulty; it is reported with its pair count.

A threshold found wrong after unblinding gets a dated exploratory note; these rules still decide the headline.

## 8. Cost (GPU-hours)

n13's measured throughput (L40S, `s3gate-03`): base MATH-500 one sample 1,675,605 output tokens at 238.7 tokens/s = 1.95 h;
RL 2,250,092 at 333.4 = 1.87 h. Harder set (no measurement; assumption): 8,000 tokens per answer at 240 tokens/s = 3.7 h per
arm and sample. Per model, sample 0 of P and F on both sets: 11.2 h on L40S; five models 56 h, four 45 h. That exceeds the
40 GPU-hour cap at one sample before any cut is possible, so L40S is not used.

Projection on the hardware used: decode in n13 was bound by KV-cache reads (14-20 sequences at 3.4-5.6k context, n13 journal
A22). `g7e.2xlarge`'s GPU has 1.6 TB/s against the L40S's 0.864 (1.85 ×) and 96 GB against 48 GB, so the projection is
1.85 × n13's rate (an assumption, not a measurement). Per model: setup 0.3 h, sample 0 of all cells 6.05 h; MATH-500 samples
1-3 (2.05 h each) do not fit the allowance at that rate. **So the expected realized plan is 1 sample per problem on both
sets**; the job adds MATH-500 samples first, then harder-set samples, only when its measured rate leaves room. Projected total
5 × 6.35 = 31.8 GPU-h. Enforced: in-job allowance 440 min per model from that model's start (15 min reserve) and `pg run
--budget-min` 470 per model (940 for the s0100 + s0400 instance), with the reaper 10 min later: at most 5 × 8.0 = 40.0 GPU-h.
If the GPU runs below about 1.6 × n13's rate, a model's harder-set stage (B2) may not finish inside its 8 h; the first
stage's rate is in that model's `metrics.json` (`stages[0].tokens_per_s`) about an hour after launch.
(First projection, for `p5.4xlarge` before the capacity failure: 3.9 × n13's rate, 4 MATH-500 samples, 30.5 GPU-h.)

**Dated change, coordinator's decision at 2026-11-14 03:50Z** (no output of s2800, fr, s0400 or s0100 exists; only base
runs): s2800, fr, s0400 and s0100 waited over two hours (11 rounds, 01:28Z-03:48Z) for `g7e` or `p5.4xlarge` capacity.
`g6e.2xlarge` and `g6e.4xlarge` (L40S, n13's hardware) join the fallback list (order: g7e.2xlarge, p5.4xlarge, g7e.4xlarge,
g6e.2xlarge, g6e.4xlarge). The study cap rises from 40 to 70 GPU-hours. Sample 0 of every cell comes before any extra
sample (the job's stage order already does this). These four models get an in-job allowance of 750 min and `--budget-min`
770 (reaper at 780 min), enough for sample 0 of all cells on an L40S (11.2 h + setup by §8's numbers); the base job keeps
440/470. Launch order by value: s2800, fr, then s0400 followed by s0100 on one instance (`jobs/pipeline.py`, budget 1,540 min).
Worst case: 8.0 + 2 × 13.0 + 26.0 = 60.0 GPU-h ≤ 70.

## 9. Facts measured before launch from n13's saved generations

- Base: 69 cap hits of 500, 60 with loop ratio < 0.10; RL: 16 cap hits, 7 < 0.10 (coordinator's numbers reproduced).
- Finished generated length, RL step 2,800: median 2,856, p90 9,136, p95 11,910.5, p99 15,513; base: median 609, p95 4,876.
- Base finished answers under 64 tokens: 23 (7 empty).

## 10. Offline gate and launch record

Offline gate, 2026-11-13, green (`rln3/offline/prep_checks.json`, `rln3/offline/offline_gate.json`; scratch venv with
math-verify 0.9.0 and transformers, no torch):
- grader reproduction: base 286/500 = 57.2, RL 460/500 = 92.0, all 1,000 banked scores equal; deranged golds fail.
- the job's child (`rln3_gen.run`) on a stand-in engine serving n13's saved texts, five models: G-CHECK base 57.2 and s2800
  92.0 pass; RL texts served to the base job stop it with exit 3 (check 92.0, outside [52.8, 61.5]); every P, F and C request
  matched its rule (1,160 commit requests in the base run); an F request without the prefill and a commit cut at N + 1 raise;
  a small allowance gives 1 MATH-500 and 1 harder-set sample.
- `rln3_analyze` on the stand-in banks: COMPLETE, every gate passes, identity and planted checks pass; one record removed →
  G-COMPLETE fails.

Inputs uploaded to `s3://pg-lineage-769063704696/results/rlneurons/r3/inputs/` (frozen.json sha256 6d732e53…, math500.json
69b71821…, hard.json 1c1f9eac…, n13 prompt_ids.json 3c2e95d9…).

Launch record (2026-11-14 UTC):
- base: `i-0dac5b629337007f3`, g7e.2xlarge, launched 01:24:53Z, prefix `results/rlneurons/r3/base-01/`, reaper 09:24:53Z.
  Engine up 01:34Z (vLLM 0.32.0, 36,066 KV blocks against n13's 12,817). **G-CHECK base passed**: sample 0 of P on MATH-500
  302/500 = 60.4, inside [52.8, 61.5]; 65 cap hits (n13: 69). Measured rate in that stage: 1,618,048 tokens in 2,742 s =
  590 tokens/s, 2.47 × n13's base rate (projection was 1.85 ×). At that rate a model's sample 0 of every cell takes about
  4.7 h with setup, and the rule adds about one MATH-500 sample.
- After the 03:50Z decision (§8), each on its first try, all `g6e.2xlarge` (L40S; g7e and p5 still had no capacity):
  s2800 `i-0a27f920f3438d518`, prefix `r3/s2800-01/`, reaper 16:56:01Z; fr `i-022a77a3b88f0b7c3`, prefix `r3/fr-01/`, reaper
  16:59:30Z; s0400 then s0100 `i-0a4552047765bf1ea` (pipeline), prefix `r3/s0400_s0100-01/`, reaper 2026-11-15 05:52:08Z.
  Heartbeats and metrics.json present for all four instances at 04:03Z. Base at 04:03Z: stage B2 (harder set, P and F), with
  stage B1 (F, MATH-500) measured at 553 tokens/s over 4,613 s.

## 11. Dated change 2026-11-14 04:20Z: training-set overlap (found after launch, before any RL accuracy was read)

`rln3_overlap.py` compares each test problem with the 13,314 prompts of `allenai/Dolci-RL-Zero-Math-7B` (train split), the RL
training set. Result (`results/rln3_overlap.json`, per-problem flags):

| set | exact | near (≥ half of word 8-grams in one training prompt) | none |
|---|---|---|---|
| MATH-500 | 1 | 8 | 491 |
| AIME 2022 | 20 | 4 | 6 |
| AIME 2023 | 23 | 4 | 3 |
| AIME 2024 | 0 | 1 | 29 |
| AIME 2025 | 0 | 0 | 30 |
| AMC 23 | 0 | 12 | 28 |
| HMMT Feb 2025 | 0 | 0 | 30 |
| OlympiadBench | 0 | 8 | 202 |

72 of the 400 harder problems are flagged, 43 of them exact. The RL models were trained on those problems with the gold
answer as reward. Consequence for the readout, fixed now: every harder-set number is reported on the 328 unflagged problems;
the 72 flagged problems are reported apart and carry no claim about what RL added. The frozen outcome rules of §1 are
applied to the 328. MATH-500 is reported on all 500 and on the 491 unflagged. The near flags on MATH-500 that were read
(3 of 8) are the same problem template with different numbers, not the same problem.
