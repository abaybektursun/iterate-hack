# RLN-4 — does the base model loop because of the sampling temperature, or because it cannot continue a long solution?

Frozen 2026-11-14 ~06:45Z, before any RLN-4 generation exists. Inputs: `rln4/inputs/` (`frozen4.json` holds every number the job
reads; sha256 of `k.json`, `g.json`, `check.json`, `math500.json` in it). Code: `infra/aws_pg/jobs/rln4_gen.py` (job),
`infra/pg/rln4_lib.py` (loop detectors, grader v2, `agree`), `rln4_prep.py` (inputs and laptop checks), `rln4_offline.py`
(offline gate), `rln4_analyze.py` (the §7 readout; written after the spec froze and before any output, run on the stand-in
banks: identity pair T1 = base-01 F gives difference 0.0, interval [0, 0]). Checks: `rln4/offline/prep_checks.json`, `rln4/offline/offline_gate.json`. Decisions in this spec are the
coordinator's (2026-11-14) unless marked as this session's.

## 0. Facts this run starts from (all from saved artifacts, MATH-500, one sample, cap 16,384)

- Base `Olmo-3-1025-7B`, RLN-3 `base-01` (g7e.2xlarge, T 0.6, top-p 0.95, seeds 1,000,000 + index): plain (P) 302/500 = 60.4,
  65 cap hits; with the RL opening (F) 340/500 = 68.0, 119 cap hits, 92 of them with loop ratio < 0.10. (The coordinator's brief
  said 64 and 118; the bank says 65 and 119.)
- RL step 2,800 (n13 `s3gate-03`): 460/500 = 92.0, 16 cap hits.
- 86 problems: base F hit the cap and the RL answer is correct (this run's K pool, §2).
- Coordinator's numbers, not recomputed here: of 123 problems RL right and base F wrong, 85 are cap hits; base F cap rate by RL
  solution-length quartile 2 % to 66 %; base pass@3 at T 0.6 is 81 (by RL-length quartile 97 / 96 / 84 / 47); base right answers
  in the longest quartile have median 3,121 tokens against RL's 9,408.
- n13's base P and base-01's P used the same seeds; 176 of 500 texts are identical (one sample, not two). Cross-hardware
  agreement of those two runs (L40S vs RTX PRO 6000): scores equal on 43 of the first 50 problems and 436 of 500.

## 1. Published work, and how this run differs

**AI2's own sampling for RL-Zero** (Olmo 3 report, arXiv 2512.13961 HTML, read 2026-11-14). §6.1 "Reinforcement Learning From
Base with Dolci RL-Zero", RL algorithm paragraph: "we train with a response length of 16K tokens ... and (ii) we evaluate with a
response length of 32K tokens and temperature 1.0 to encourage diversity as we report pass@k." Top-p is not stated in §6.1.
Table 49 gives "Sampling temperature 1.0" for RL-Zero training. The offline filtering paragraph of the Think RL section says
"We sample with a temperature of 1.0 and top-p of 1.0, matching how we sample during RL training." So T1, T2, T3 and G use
**temperature 1.0, top-p 1.0**; the top-p is not stated for RL-Zero evaluation, and 1.0 is used as instructed and as AI2's RL
sampling. (The same report evaluates base models at temperature 0.6 and top-p 0.6, and Think models at 0.6 / 0.95.)

**Wang et al., arXiv 2610.06851** (as read by the RLN-3 session, SPEC3 §0; not re-read here): the first-release base and RL-Zero
model, the base continuing after a prefilled cue ".\n\n" + "Okay": MATH-500 77.7-78 with cap rate 0.16, 31,744-token budget,
T 0.6, 32 samples. This run differs: (a) the continuation test K hands the base a long prefix written by the RL model (or by
the base itself) up to the point where the base's own answer began to loop, not a two-token cue; (b) the 3.1 RL run's step
2,800 and the 3.1 base; (c) T 1.0 cells; (d) loop onset located per answer.

**Pipis, Garg et al., arXiv 2512.12895** ("Wait, Wait, Wait… Why Do Reasoning Models Loop?"; HTML read 2026-11-14, abstract and
§2 only): distilled and RL reasoning models (R1-distilled Qwen 1.5B-32B, OpenThinker3, QwQ-32B, Phi-4-reasoning), AIME 2024
and 2025, temperatures 0-1.0, 20 samples, a response loops when some 30-gram occurs at least 20 times. Finding: looping falls
as temperature rises, and responses stay longer than the teacher's. This run differs: a pretrained base model (no reasoning
post-training) with a prefilled RL opening, MATH-500, one sample, two temperatures, a cap-hit outcome, and a continuation test
that separates "cannot sustain a long solution" from "lacks the solution". Their loop rule (30-gram x 20) is not used; §4 gives
ours and the period rule the coordinator relayed from arXiv 2611.06095 (not read by this session).

## 2. Cells (priority order; the job runs them in this order except where one queue holds several)

All: MATH-500 (n13's 500 rows), n13's prompt (3.1 chat template, `pair1`), cap 16,384 generated tokens, the RLN-3 engine
build (vLLM 0.32.0, bf16, `max_model_len` 18,432, `gpu_memory_utilization` 0.90, prefix caching, FLASH_ATTN, FlashInfer
sampler off; transformers 5.19.0 and tokenizers 0.23.3 pinned as in base-01's `pip_freeze_n13.txt`), one sample, stop id 100257.
"Opening" = the RLN-3 prefill ids [1584, 2268, 33413] (" line!\n\nOkay"); in F cells it does not count toward the 16,384.

| cell | model | prompt + prefix | temperature / top-p / repetition penalty | seed base | requests |
|---|---|---|---|---|---|
| check | base | opening | 0.6 / 0.95 / 1.0 | 1,000,000 (base-01's) | problems 0-49 |
| T1 | base | opening | 1.0 / 1.0 / 1.0 | 41,000,000 | 500 |
| K_rl | base | first L tokens of the saved RL answer | 0.6 / 0.95 / 1.0 | 42,000,000 | 78 |
| K_own | base | first L tokens of base-01's own F answer | 0.6 / 0.95 / 1.0 | 43,000,000 | 78 |
| K_fresh | base | opening (restart) | 0.6 / 0.95 / 1.0 | 44,000,000 | 119 (every base-01 F cap hit) |
| K_fresh2 | base | opening (second restart) | 0.6 / 0.95 / 1.0 | 44,500,000 | one per K_fresh cap hit |
| T2 | RL step 2,800 | none (plain) | 1.0 / 1.0 / 1.0 | 45,000,000 | 500 |
| G | base | Dolci prompt + opening | 1.0 / 1.0 / 1.0 | 48,000,000 + 100,000 s | 4 per prompt, cap 4,096 |
| R1 | base | opening | 0.6 / 0.95 / 1.1 | 46,000,000 | 500 |
| T3 | base | none (plain) | 1.0 / 1.0 / 1.0 | 47,000,000 | 500 |

Seed = base + problem index (G: + Dolci row). Earlier runs used 1,000,000-1,030,499 (n13 set A, RLN-3 MATH-500), 2,000,000+
(n13 set B) and 3,000,000-3,070,399 (RLN-3 harder set); every RLN-4 cell except the check is above 41,000,000, and no
(model, problem, seed) repeats across cells (`prep_checks.json` → `seeds`; failing inputs: T1 at the check's base, R1 at T1's
base, both detected).

**K (continuation test).** Pool: base-01 F hit the cap and n13's RL answer is correct: 86 problems. L = min(tokens of base-01's
F answer before its loop onset (rule A, §4), 2,500, tokens of the RL answer before the line holding its extracted answer). The
third term (this session's addition) keeps the RL prefix from containing the RL model's final answer line; it binds on 2 problems.
Answers with no loop onset (18) take the onset at the end of the text, so L = 2,500. Dropped for L < 300: 8 problems
(indices 4, 17, 67, 91, 326, 462, 476, 491; L 278, 2, 259, 163, 58, 61, 186, 265). **78 problems in K.** L over the 78:
min 399, 10 % 986, 25 % 2,031, median 2,500, max 2,500; 52 at 2,500, 24 set by the onset. Both prefixes count the 3 opening
tokens; the total cap 16,384 includes the prefix (max new tokens = 16,384 − L; K_fresh: 16,384 − 3). The saved records hold text,
not token ids, so prefixes are re-tokenized saved text (opening ids kept as sampled; re-tokenization of the rest is canonical BPE,
which may differ from the sampled ids at a few places).

**Restart row (coordinator's addition).** Per problem, attempts in order: base-01 F (saved, T 0.6), K_fresh, K_fresh2; the
answer is the first attempt that finished (no cap hit), else the last attempt; tokens = the sum of generated tokens over the
attempts used. K_fresh runs on all 119 base-01 F cap hits (not only the 78) so that the row covers all 500 problems.
Compared with the RL model's single answer (n13: 92.0, its mean tokens) — reported, no verdict.

**G (bank only, coordinator's change).** `allenai/Dolci-RL-Zero-Math-7B` @ 93b5e498, train split, 13,314 prompts; excluded by
`rln3_overlap`'s rule applied against MATH-500 and the 400-problem harder set (exact normalized text, or at least half of a test
problem's word 8-grams inside the prompt): 44 exact + 45 near = 89; 13,225 kept; order = `numpy.random.default_rng(0).permutation`;
the first 1,000 in `g.json`. Submitted prompt by prompt (512 requests kept in flight) until 1,000 prompts or 12:58Z; an answer
that reaches 4,096 tokens is recorded as cut (`cap_hit`), no continuation. Target 1,000, minimum 400; R1 and T3 run only after
G reaches 1,000 (if fewer than 400 fit, R1 and T3 are dropped first). Per-row grader fields only.

**R1.** repetition_penalty 1.1 (vLLM `SamplingParams.repetition_penalty`; fixed now).

## 3. Engine-concurrency finding (base-01, before launch)

base-01's vLLM log: KV cache 247,034 tokens (70.4 GiB at `gpu_memory_utilization` 0.90), `max_num_seqs` 128. Over the run the
KV cache was 96-100 % full with 20-35 sequences running and hundreds waiting; 128 running only in short bursts after long answers
ended. `nvidia-smi dmon`: SM 93 % and memory bandwidth 85 % on average. So concurrency was limited by KV memory, not by
`max_num_seqs`, and the GPU was busy. Raising `gpu_memory_utilization` to 0.95 would add about 6.6 % KV; not done, to keep the
check (§5) on the same engine settings as base-01 (this session's decision).

## 4. Loop-onset detectors (instrument check on saved files, `prep_checks.json` → `detector`)

Rule A (this study): a loop is verified by an 8,000-character window starting at a line start with zlib ratio < 0.10 (SPEC3's
loop-ratio constants). Onset = the first line of the repeated block: from the first verified window, walk back over lines that
recur in that window (digits as '#', stripped, at least 8 characters; blank lines pass), then forward to the first recurring
line. Rule B (arXiv 2611.06095 as relayed): the longest suffix with period ≤ 64 characters, at least 2,000 characters and 3
cycles; onset = its start. Crude rule: any line over 20 characters occurring three times.

| file | finished | A fires | B fires | crude fires | cap hits with ratio < 0.10 | A fires | B fires | crude fires |
|---|---|---|---|---|---|---|---|---|
| n13 RL | 484 | 0 | 0 | 60 | 7 | 7 | 2 | 4 |
| n13 base P | 431 | 1 | 0 | 35 | 60 | 59 | 8 | 43 |
| base-01 P | 435 | 0 | 0 | 39 | 48 | 46 | 6 | 36 |
| base-01 F | 381 | 0 | 0 | 11 | 92 | 90 | 11 | 64 |

Rule A passes (finished < 2 % everywhere; most low-ratio cap hits); rule B passes the false-positive limit but fires on 6-17 %
of the low-ratio cap hits (the base's loops have periods of hundreds of characters); the crude rule fails (60 of 484 RL finished,
reproducing the coordinator's count). **Rule A is used** for L and for the loop outcome; B is recorded per answer. Failing input:
an RL finished answer with 300 repeated lines appended fires A. Caveat: on cap hits with loop ratio < 0.10 the last 8,000
characters already satisfy A's verification, so A's hit rate on that set is nearly guaranteed; what the table tests is the
false-positive side and where the onset falls. The onset position was checked by eye on 4 answers only.

## 5. Grader v2 (`rln4_lib.extract_v2`; v1 = `n13_score.extract`, unchanged)

v2 = v1; when v1 finds nothing, the last line starting with `**Answer**:` or `**Answer:**`, one `\( \)` or `\[ \]` pair removed.
Same rule for every model. On the saved files (correct of 500): n13 base v1 286 (registered: 286, pass), v2 287; n13 RL v1 460
(registered: 460, pass), v2 460; base-01 P v1 302, v2 303; base-01 F v1 340, v2 344. No answer right under v1 is wrong under v2.
Headline numbers use v1; v2 is reported beside them. Answer agreement between attempts uses `rln4_lib.agree` (the grader's
equivalence test, never string equality; tests: "5.5" = "\dfrac{11}{2}", "$x = 2$" = "2", "5.5" ≠ "\frac{11}{3}").

## 6. Checks (each with an input that fails it)

| check | passes if | failing input |
|---|---|---|
| reproduction (GPU, first stage) | base F, T 0.6, problems 0-49, base-01's seeds: scores equal to base-01's on ≥ 45 of 50 on base-01's GPU (RTX PRO 6000, g7e), ≥ 38 of 50 on another GPU → pass; < 30 → job stops (exit 3); in between → the job continues, `check.json` verdict `continue_does_not_count`, and every comparison with a base-01 cell (T1 vs base F) does not count until the cause is found; K arms among themselves are unaffected | offline: empty answers (13 of 50 equal) → verdict stop, exit 3 |
| G-TEMPLATE | rendered MATH-500 prompt ids = n13's banked ids | (RLN-3's) |
| G-WEIGHTS | every shard sha256 = the HF LFS oid at the frozen commit | the other model's oids |
| requests (offline) | every request's ids, sampling, seed and max_tokens as §2 | wrong seed, prefix, max_tokens each raise |
| hard stop | at 13:18Z unfinished requests are aborted and listed, files closed, exit 0 | offline run started 2 minutes before the stop |

Upper bound of the check: 50 of 50 (base-01 against itself). Reference for a non-bug difference: 43 of 50 across hardware (§0).
The check is run alone (50 requests), so batch composition differs from base-01's; vLLM is not batch-invariant, so a score
difference under 45 can come from numerics. Other-GPU threshold (this session's decision, before launch): the measured
cross-hardware agreement is 43 of 50 (436 of 500 = 87 %); a binomial 95 % lower end at 87 % on 50 problems is about 38, so 38.
The stop threshold 30 lies far above the agreement a broken engine gives (empty answers: 13 of 50) and below any run that
samples the same model from the same prompt.

## 7. Frozen readout (computed after the run, v1 grader; v2 beside it)

**T1 vs base-01 F (T 0.6).** Cap-hit count of 500 and accuracy, each with a paired bootstrap interval over problems (2,000
resamples, seed 0, 95 % percentile; `n13_score.paired_bootstrap`), T1 minus F. Label: "temperature explains the loops" if T1's
cap hits < 40 of 500; "temperature does not explain the loops" if > 90; "undecided" for 40-90. If T1 is incomplete at the
stop, the label is computed only if ≥ 450 problems finished, on those problems with the thresholds scaled by n/500; otherwise
"not counted".

**K.** Per arm on the 78 problems: finished (no cap hit), loop (rule A) or not, correct (v1), tokens (prefix + new). Label:
"the base can finish from a sound prefix" if K_rl finishes on ≥ 60 % (≥ 47 of 78) and K_own on ≤ 30 % (≤ 23 of 78); "the base
loops regardless of prefix" if K_rl finishes on ≤ 30 %; otherwise "undecided". K_fresh is the restart row (no label). Each
proportion is reported with a Wilson 95 % interval; K_rl − K_own finish rate with a paired bootstrap interval. If an arm has
fewer than 70 of 78 records at the stop, K is "not counted".

**Restart row**, T2 (RL at T 1.0 vs n13's RL at T 0.6: accuracy, cap hits, paired interval), R1 and T3 (vs base-01 F and P):
reported with intervals, no labels. G: banked; per-row grader fields only.

Refutation, stated before the data: "temperature explains the loops" is refuted by T1 cap hits > 90; "the base can finish from a
sound prefix" is refuted by K_rl finishing on ≤ 30 %. A threshold found wrong after unblinding gets a dated exploratory note; these
rules still decide the headline.

## 8. Hardware, time, cost

Type: first of `g7e.2xlarge` (base-01's type; the G-family quota frees when base-01 ends, its allowance ends about 08:52Z) or
`p5.4xlarge` (P-family quota, 128 vCPU, free now); `g6e.2xlarge` only if nothing launches by 09:30Z. Launch attempts every 10
minutes from about 06:50Z. Prefix `results/rlneurons/r4/<name>-01/`. Everything saved by 13:30Z: the job's hard stop is 13:18Z
(abort and list), the G submission stop 12:58Z, `pg run --budget-min` = minutes from launch to 13:30Z, reaper 10 minutes later.

Projection (assumption, not a measurement), at base-01's measured 550-590 tokens/s on g7e: setup about 12 min (venv, two
snapshots, the RL one during base1); check about 15 min (tail-bound); T1 + K about 5.9 M tokens (T1 2.5 M assumed as base-01 F;
K_rl 0.5 M, K_own 0.9 M, K_fresh 1.3 M, K_fresh2 0.7 M) = about 3.0 h; T2 about 2.3 M = 1.1 h; G about 10 k tokens per prompt.
On g7e launched at 09:00Z, T2 would be cut at the stop and G would not start. On p5.4xlarge (3.35 TB/s against 1.6, 80 GB) the
rate is unknown; at 1.5 × the g7e rate and a 07:00Z start, T1 + K end about 09:15Z, T2 about 10:05Z, G about 700-900 prompts by
12:58Z, R1 and T3 not reached. GPU-hours: at most (13:40Z − launch) on one GPU, ≤ 7 GPU-h.

## 9. Offline gate (laptop, stand-in engine, no model forward), 2026-11-14 06:30Z: green

`rln4_offline.py` → `rln4/offline/offline_gate.json`: base1 on base-01 texts gives check 50/50 (pass), T1 500, K_rl 78, K_own 78,
K_fresh 119, K_fresh2 one per K_fresh cap hit; rl gives T2 500 (460 correct on n13's RL texts); base2 gives G 1,000 x 4 then R1 500
and T3 500; base2 started 20 minutes before the G stop banks 318 prompts and drops R1 and T3; base1 started 2 minutes before the hard
stop aborts 375 requests and exits normally; empty answers stop the job at the check (exit 3); a wrong seed, prefix or max_tokens
raises. Laptop tokenizer note: without the repo's `config.json` the RL tokenizer loads as a different class and splits ".\n\n";
with it, the rendered ids equal n13's on 500 of 500.

## 10. Launch record

Launch attempts about every 12 minutes from 06:34Z: `g7e.2xlarge` (G-family quota until base-01 ended at about 08:13Z, then
no capacity) and `p5.4xlarge` returned no capacity on all 16 attempts from 06:34Z through 09:24Z. At 09:37Z
`g6e.2xlarge` (L40S, n13's hardware) joined the list as §8 allows and launched: `i-0384fdbf215c8b604`, prefix
`results/rlneurons/r4/base_rl-01/`, `--budget-min 232`, reaper 13:41:42Z, heartbeat at 09:40:25Z, setup.json at 09:40:41Z.
Attempt 01 failed in setup at 09:44Z (`STATUS exit=1`: huggingface_hub was imported before `hf_setup`, so the hub stayed in offline mode and the base snapshot could not download; no generation ran). Fixed (commit after 2693027a0) and relaunched as attempt 02: `i-09b23d20f2b7a2192`, g6e.2xlarge, prefix `results/rlneurons/r4/base_rl-02/`, `--budget-min 219`, reaper 13:42:26Z. At 10:00Z: G-WEIGHTS pass, tokenizer pins 5.19.0 / 0.23.3, G-TEMPLATE pass, engine loaded in 85 s with 12,817 KV blocks (n13's L40S count), stage `check` running, heartbeat current. The check therefore uses the other-GPU threshold (38 of 50). At n13's L40S rate (about 240 tokens/s for the base) the job has
about 3.0 M tokens before the 13:18Z stop: the check, then T1 (about 2.5 M) is expected to finish or nearly finish; K, T2, G, R1
and T3 are expected to be cut or not reached. Per-cell files are written per request, so every finished request is usable.

## Deviations

**2026-11-14 ~10:25Z, K cell on Modal (`infra/modal_rln4_k.py`, prefix `results/rlneurons/r4/modal_k-01/`).** The AWS job
`base_rl-02` (L40S) is not expected to reach K before the stop (§10), so K runs separately on Modal. Definitions unchanged: same
inputs (sha256 against `frozen4.json`), same prompts, prefixes, seeds, sampling, caps, grader v2 and the job's own `run()` code.
What differs from §2 and §6:
1. Hardware: one H100 80GB per container (not g7e or g6e). The check uses the other-GPU threshold (38 of 50), which was set from
   the L40S vs RTX PRO 6000 agreement.
2. Queues: the check runs alone on its own engine (as §6 says), then K runs in two parallel engines: `K_rl` + `K_own` on one
   GPU, `K_fresh` (+ `K_fresh2`) on another. T1 is not in the queue. Seeds are per request, but vLLM is not batch-invariant, so
   batch composition differs from the one-queue plan.
3. K runs only if the check verdict is "pass" (the coordinator's rule for this run; §6 would also continue at 30-37).
4. Stop: 12:05Z instead of 13:18Z, so that the worst-case Modal spend stays under 15 USD (2 H100 x 1.7 h at 3.95 USD/h). It matters
   only if a request is still running at 12:05Z; the readout reports whether any were aborted.
   Outcome: it did not bind. `k_a` ended 10:54:41Z and `k_b` 11:02:18Z with 0 requests aborted (`metrics.json` stages).
5. The job code gained two phases (`check`, `k` with `--arms`); phase `base1` is unchanged (offline gate rerun: identical except
   timestamps).

**2026-11-14 ~13:30Z, T2 and T3 on Modal (`infra/modal_rln4_k.py` steps `t2`, `t3`; prefixes `results/rlneurons/r4/modal_t2-01/`,
`results/rlneurons/r4/modal_t3-01/`).** The AWS job reached neither cell. Cell definitions unchanged (§2: prompts, seed bases
45,000,000 and 47,000,000, T 1.0 / top-p 1.0, cap 16,384, grader v1 with v2 beside it). What differs:
1. Hardware: one H100 80GB per run, as the K deviation.
2. RL check (new; the coordinator's rule for this run): before T2, on the same engine, the RL model on problems 0-49, plain prompt,
   n13's sampling (`n13_gen.SAMPLING`: T 0.6, top-p 0.95) and seeds (1,000,000 + index), scores compared with n13 `s3gate-03`'s RL
   answers (`inputs/check_rl.json`, written by `rln4_prep.write_check_rl`, sha256 in `rln4_gen.CHECK_RL_SHA256`, uploaded to
   `r4/inputs/`). Thresholds are §6's (pass at ≥ 38 of 50 on a GPU other than the reference's, stop below 30, in between continue
   and comparisons with n13 RL do not count). They were set for the base model (§6) and are reused for the RL model unchanged.
   Reference: problems 0-49 of n13 RL have 46 right and 1 cap hit.
3. T3 runs alone (§2 had it after G and R1); it runs only if the base check of `modal_k-01` passed (42 of 50).
4. Stop: the frozen stop (13:18Z) had passed. Each run's stop is set at launch from the spend limit for this task (8 USD of
   Modal usage, at most 15 USD for the day) and must fall at least 10 minutes inside the 2-hour function timeout. Unfinished
   requests at the stop are aborted and listed in `metrics.json`.
5. Phases `rl_check` and `t3` added to `rln4_gen`; the base check code moved into a shared `check()` (offline gate rerun:
   sections 1-6 identical except timestamps; new sections 7-9 pass, including empty answers stopping `rl_check` with exit 3).
   Outcome (artifacts `rln4/modal_t2-01/`, `rln4/modal_t3-01/`): RL check 48 of 50 scores equal (pass) on an NVIDIA H200 (Modal
   placed the `H100` request on an H200; KV cache 56,679 blocks against 28,749 on H100); T2 500 of 500 on the same H200, 0 aborted,
   container 13:32:03Z-14:00:45Z; T3 500 of 500 on an H100 80GB, 0 aborted, 14:01:13Z-14:15:29Z. Billed (Modal report, rln4-k):
   2.44 USD (T2 run) + 1.16 USD (T3 run). Readouts: `rln4_analyze` (`readout.json`) and `rln4_temp` (quartiles, examples).
   Caveat seen in the rows: the v1/v2 graders miss lines such as "Final answer: 42" (T3's saved wrong example); 166 of 500 T3
   answers and 127 of 500 base-01 P answers have no extracted answer.

## Grader v3 (2026-11-14; `rln4_lib.extract_v3`, `norm_v3`, `grade_v3`; v1 and v2 unchanged)

Why: two hand audits of saved answers found correct answers scored wrong by v1 and v2 (an earlier "Answer:" line run together
with later text taken instead of the final box; "Answer:" in the middle of a line or inside `**Answer: N**`; "Final answer: N" and
"The final answer is N"; Unicode exponents, `∞`, `√`; tuple against a pmatrix column vector; several roots in separate boxes;
trailing words such as "gallons" or a glued "Answer").

**Extraction (never reads the gold).**
1. Candidates: every balanced `\boxed{...}`, and every answer marker anywhere in a line: `Answer` or `Final answer` (either
   case of `F`/`a`), optionally followed by `**`, `*` or `__`, then `:` or the word `is`. A marker's candidate is the rest of
   its line, with `\( \) \[ \]` removed and `*`/`_` stripped from both ends; an empty rest is skipped.
2. The candidate that starts last in the text is the answer (a box inside a marker line starts after the marker, so the box wins).
3. When the answer is a box, the boxes before it that are separated from it only by spaces, newlines, commas, semicolons, `$`,
   brackets, backslashes and one "and"/"or" are joined to it with ", " in text order (exact duplicates dropped).
4. No candidate: nothing extracted, scored wrong.

**Normalization (`norm_v3`, applied to the gold and to the extracted string alike).** Unicode superscript digits and `⁻` to
`^{...}`; `∞` to `\infty`; `−` (U+2212) to `-`; `√` followed by a number, one letter or a parenthesised group to `\sqrt{...}`,
other `√` to `\sqrt`; a `pmatrix` without `&` (a column vector) to a tuple `(a, b, c)`; a whole string `[a, b, c]` with three or
more items to `(a, b, c)`; trailing words of three or more letters (and one final period) after a digit or closing bracket are
removed when the part before them contains a digit and no word of three or more letters (so "16/27 gallons." becomes "16/27" and
"72Answer" becomes "72", while "The radius is 3 units." is left whole).

**Equivalence.** `n13_score.grade(norm_v3(gold), norm_v3(extracted))` (math-verify 0.9.0, rule `dollar_both`), the same test
as v1. On the 500 golds: 500 equal to themselves; 3 equal after a fixed derangement (seed 0); planted pairs 24/24 equal, 16/16
unequal.

**Checks.** `studies/rlneurons/rln4_grader_v3_test.py`: every audited row (22 saved answers) is wrong under v2 and must be right
under v3; negative cases that must stay wrong (a wrong number with units; a correct intermediate value followed by a different
final answer; an answer that contains the gold as a substring, 112 for 12; "x = 2" for gold "x = 2, 3"; boxes separated by words
are not joined; "2xy" is not cut to "2"). A test fails when any one part of the fix is removed (v2 extraction,
normalization, pmatrix rule, trailing-word rule, mid-line markers).

**Direction-of-error review** (frozen before the table was computed): list every v1-to-v3 flip per cell; read every
right-to-wrong flip and 40 wrong-to-right flips drawn with `random.Random(0)` from all cells; if more than 2 of the 40 are judged
incorrect, tighten the rule and repeat.

Exploratory deviation, 2026-11-14 (before the readout, after the first flip listing): the first draft stripped trailing `.,;`
from every answer and removed `\( \)` only as an enclosing pair. That made three right answers wrong (math-verify reads the last
number of a sentence only when the sentence ends with a period: "The radius of the sphere is 3 units."; and "\[Answer:\mathrm{6}\]").
The general punctuation strip was dropped, the trailing-word rule got the "no word in the part before" condition, and the
delimiters are now removed anywhere in a marker's text. The rule above is the one after this change; it was then frozen.

Known limit: a marker in the middle of a line also matches when the model goes on to invent and answer a new problem
(T3 row 146: right under v1, wrong under v3). A tail of three or more letters glued to a number is cut even when it is a product of
variables ("2xyz" becomes "2").
