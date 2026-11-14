# SPEC5 map: where the RL model still disagrees with the cued base

Idea `idea-d204a7`, work item `work-e0effe`. Written 2026-11-14, before the first GPU job. Inference only: forward passes with
teacher forcing over stored answers, no sampling.

## 1. Question

The base `allenai/Olmo-3-1025-7B` with the three-token opening cue scores 410 of 500 on MATH-500 at T 1.0; the RL model
`allenai/Olmo-3.1-7B-RL-Zero-Math` scores 463 of 500 with the plain prompt (`results/rln4/grader_v3/readout.json`). Once the
cue is given, at which positions of an answer do the two models' next-token distributions still differ, and is the token where
the base starts a wrong final answer one of them?

## 2. Hypothesis H and what refutes it

Observation behind H (`results/rln4/t1_t2_items-01/metrics.json`): RL has 0 wrong answers among its 286 answers of at most
4,000 tokens, and its right answers are about twice as long as the base's (median 3,014 against 1,432 tokens).

H: on the base's wrong answers of under 4,000 generated tokens among the 65 problems that RL solved and the base did not
(group i, n = 23), RL gives much lower probability than the base to the token where the base starts its final answer.

Answer-start token: grader v3 (`rln4_lib.extract_v3`) picks the final `\boxed{` run or the final answer marker
(`MARK_V3`: "Answer:", "Final Answer:", "**Answer**:" and the like). The answer-start token is the token that holds the first
non-space character of that span. Statistic per answer: D = ln P_RL(token) - ln P_base(token), both models reading the base's
own text up to that token.

H is refuted if any of these holds:

1. Median D over group i is above -ln 2 (RL's probability is within a factor 2 of the base's).
2. The control shows the same shift: on right base answers of at most 2,000 tokens (group ii, n = 250) median D is at or
   below -ln 2, or a permutation test of the difference in medians between groups i and ii (10,000 permutations, two-sided)
   gives p > 0.05.
3. Disagreement is spread evenly over position: in the median group-i answer, KL(base||RL) at the answer-start token is below
   the 90th percentile of that answer's positions.

Readings declared in advance, reported next to the main statistic and not used for the verdict: (s1) D summed over the tokens
from the answer-start token through the token that holds the `{` of `\boxed{` or the end of the marker; (s2) the header
variant: when the 60 characters before the span contain "Final Answer", the first token of that header; (s3) each model's
stop-token probability at the true end of each answer.

## 3. Closest published experiments

From the team memory (`tools/recall.py`, papers read in full by teammates):

- arXiv 2605.06241, Table 2: on base greedy rollouts on MATH-500, the RL teacher's top-1 token differs from the base's at
  1.03 to 3.96 % of positions (4 pairs); base entropy is 7.6 to 12.6 times higher at those positions.
- arXiv 2610.24663, Appendix E Table 12: base confidence locates the top-10 % KL positions with AUROC 0.94 to 0.98 (AIME24/25).
- arXiv 2510.07364, Tables 2 and 5: base and RL model disagree at 5 to 12 % of generated tokens (Qwen2.5-7B / ORZ-7B: 5.9 % on
  MATH500).
- arXiv 2610.06851 (the cue paper): the base continuing an RL-generated opening reaches pass@1 0.777 (Table 13).

Found by an Exa search on 2026-11-14 and not read (title and highlights only, so they support no claim here): arXiv 2603.22446
"Sparse but Critical: A Token-Level Analysis of Distributional Shifts in RLVR Fine-Tuning of LLMs"; arXiv 2507.00432 §4 "Token
Distribution Shifts: Insights from KL Divergence and Rank Analyses".

Differs in: the Olmo 3 / Olmo 3.1 RL-Zero-Math pair; the cue is in the prefix, so the opening that RL learned is already
given; sampled T 1.0 answers of each model (the published maps use greedy base rollouts); both directions (the base's text and
RL's own text); the answer-start test with a matched control; the stop-token probability at the end of each answer.

## 4. Inputs

- Stored answers, 500 rows each, frozen in `data/rln5/map_inputs.json` (sha256, size): `T1.jsonl` (base with cue, T 1.0) and
  `T2.jsonl` (RL, plain prompt, T 1.0). Not committed. Uploaded to the Modal Volume `iterate-runs` under `inputs/rln5/`; the
  job reads `/runs/inputs/rln5/` and asserts sha256 and size.
- Models, revisions, tokenizer, cue ids, prompt template: `data/rln4/frozen4.json` (both models with the RL tokenizer).
  Problems: `data/rln4/math500.json`; prompt ids checked against `data/rln4/prompt_ids.json`.
- Per-problem table `results/rln4/t1_t2_items-01/per_problem.json` (right and wrong under grader v3, token counts, cap hits,
  hand label `failure_type`), read by the analysis only.

The rows hold text and no token ids. The answer is re-tokenized with `rln4_lib.encode_answer` (keeps the cue's three sampled
ids). The job compares the count with the row's `n_new`; a row that differs by more than 1 % is listed in
`tokenize_check.json` and left out of the map; more than 25 such rows in a cell fail the job. Stored `mean_logprob` of each row
(the sampler's own log-probs) is the reference for control 3.

## 5. The job (`jobs/rln5_map.py`) and its controls

Sequence per row: rendered prompt, the cue (T1 rows), the generated tokens, and the stop token `100257` for rows that are not
cap hits. Both models run over the same sequence in bf16 on one H100 (`transformers`, `torch`, the runner image). The pass is
chunked (1,024 positions) with the key-value cache, so the vocabulary projection of a 16,384-token answer never exists at once.
Per position after the prompt, stored as float16 / int32 / uint8 in compressed shards (`<cell>_map_<kkk>.npz`): written token,
position kind (cue, generated, stop), log-prob of the written token under each model, each model's entropy, KL(base||RL),
KL(RL||base), each model's top-1 token and its log-prob, rank of the written token (cap 100), each model's log-prob of the
other's top-1, of the stop token, and of the set of vocabulary tokens whose string contains "boxed" or "Answer".

Controls. The smoke run (per cell: the 10 shortest answers, the answer nearest 6,000 tokens, the longest answer) must pass all
of them before the full run; the full run repeats them and fails at its end if one fails, after writing every file.

1. Identity: 2 answers scored base against base give max |KL| <= 1e-6, equal log-probs and equal top-1 at every position.
2. Positive control: at the three cue positions of T1 rows, the median over answers of RL's probability of the cue (product of
   the three) is at least 2 times the base's. If it is not, stop and find out why.
3. Calibration: (a) for each cell, mean log-prob of the written generated tokens under the generating model plus that model's
   mean entropy is within 0.05 nats of 0; (b) the median over rows of |mean log-prob of the generated tokens from this job
   minus the row's stored `mean_logprob`| is at most 0.02 nats. (b) is the sharper test that the sequence is what the model
   saw.
4. Files: every output file is written and `analysis/rln5_map_analyze.py` reads them. Instrument check added here because the
   models use a 4,096-token sliding window in 24 of 32 layers: on the answer nearest 6,000 tokens the chunked cached pass and
   one pass without cache give the written tokens' log-probs with mean |difference| <= 0.02 nats and at most 0.1 % of positions
   over 0.25 nats. If it fails, the full run uses `--forward oneshot`.

## 6. Analysis (`analysis/rln5_map_analyze.py`, full run)

a. Share of generated positions where the two top-1 tokens differ, for T1 and T2 answers; share of the summed KL carried by
   the top 1 % and top 4 % of positions (both directions).
b. KL by position: the first 10 generated tokens after the cue, deciles of the answer, the last 50 tokens.
c. The test of H: D at the answer-start token for (i) the 23, (ii) right base answers of at most 2,000 tokens, (iii) all other
   wrong finished base answers. Medians, quartiles, n, a bootstrap interval of each median, and RL's top-1 token at those
   positions (10 most frequent, decoded).
d. The 16 cap-hit base answers that RL solved: positions of the largest log-prob gaps and what RL preferred there; where the
   base text states the gold answer, RL's probability of the stop token or of an answer marker in the 50 tokens after, against
   random 50-token windows of the same answers.
e. On T2: the 30 tokens with the largest summed KL(RL||base), decoded; each model's stop-token probability at the true end.

At least 15 raw positions are read in context before any number is explained. Absolute numbers with n. A result that refutes H
is reported as such. Examples saved next to the numbers: real input, output and score of items for and against H.

## 7. Runs, limits, cost

One folder per GPU run: `results/rln5/map-01/` (smoke runs are named in its `run.json`). At most 2 smoke and 2 full jobs,
`--hours 1` each, at most 1.5 H100-hours in total. Estimate: 4.31 M generated tokens in the two files, two models, so 8.6 M
token forward passes; at 8,000 to 15,000 tokens per second and model that is 10 to 18 minutes, plus about 5 minutes of weight
download and load. Smoke: about 60,000 positions, under 2 minutes after load. The per-position shards (about 200 MB) stay in
the Volume `iterate-runs` under `<job-id>/` and in `runs/<job-id>/` on the laptop; small readouts are committed.

## 8. Deviations

2026-11-14, after the full run `sameraslan-1114-135831-c3ec`:

1. Group i has n = 21 at the answer-start test: 2 of the 23 answers have no extracted answer under grader v3. Group iii has 39
   of 40 for the same reason.
2. The shards store natural-log probabilities in float16 where §5 says probabilities, ranks in uint8, and two arrays more
   than listed: each model's log-prob of its own top-1 token.
3. Added after reading the positions and not used for the verdict: the split of D by the format of the base's final answer
   ("Answer:" line or `\boxed{}`), `metrics.json` `c.by_format`; and group iv (right base answers over 2,000 tokens).
4. Part d, "where the base text states the gold answer": the pattern found the gold in 3 of the 16 cap-hit texts, and on
   reading 2 of the 3 are intermediate numbers. The comparison has one real case and supports no claim.
5. Re-tokenization: 41 T1 rows and 34 T2 rows differ from the stored count by 1 to 5 tokens (all within 1 %); they are in the
   map. No row was left out.
6. The smoke run had 12 answers per cell. One smoke job and one full job were used.
