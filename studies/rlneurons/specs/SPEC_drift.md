# SPEC_drift: what a cut-off answer is doing. Language drift and other label-free signs in Think-SFT's cap hits

Board: idea-e37da1, work-76a232. Builds on result-818c20 (Think-SFT + cue, vote 241 of 328), result-5251c9 (fresh2026),
result-c8b994 (cap 32,768: 91 of 93 cut answers finish, 23 right), result-f3d708 and result-b30f15 (no early label-free
detector of a failing sample of the cued base). Laptop only, stored rows and stored texts, no GPU. Written 2026-11-15 UTC
after the instrument checks below and before any other number was computed: at this point the only numbers seen are the
printed lines of `analysis/drift.py` (per cell: cap hits, cap hits with more than 20 Chinese characters, cap hits with an
episode, the token-count check) and the planted tests of `analysis/drift_test.py`.

## Question

Think-SFT + cue hits the 16,384-token cap on 29 % of its samples on hard328 and 45.6 % on fresh2026; a cap hit casts no
vote. 86 of its 378 cap hits on hard328 and 66 of 248 on fresh2026 hold more than 20 Chinese characters (RL 1 of 114 and 3
of 84; base 2 of 286 and 0 of 219). Nobody has looked at this text. Q1: what is it, where does it start, and is it a
property of the problem or of the sample? Q2: does a switch predict that the sample ends not right, beyond marking a hard
problem? Q3: which label-free sign read at token 4,000 / 8,000 / 12,000 best predicts a sample that will not end right? Q4:
does "stop a sample at its first sign" save tokens under the sequential vote at no loss of right answers?

## Data (T 1.0 / top-p 1.0, grader v3 as stored, attempt 0 of each sample only)

| Cell | Rows | Texts (`runs/`, not in git) |
|---|---|---|
| hard328 Think-SFT + cue, 4 samples, cap 16,384 | `results/thinkvote/hard328_sft1_cue_s4-01` | `thinkvote_hard328_sft1_cue_s4` |
| hard328 RL plain | `results/day1_3/hard328_rl_plain_s4r2-01` | `abaybektursun-1114-200505-5ff2` |
| hard328 base + cue | `results/day1_3/hard328_base_cue_s4r2-01` | `abaybektursun-1114-200457-e8e6` |
| fresh2026 Think-SFT, RL, base, 4 samples | `results/fresh/{sft1_cue,rl_plain,base_cue}_s4-01` | `fresh_{sft1_cue,rl_plain,base_cue}_s4` |
| MATH-500 Think-SFT + cue, 4 samples | `results/thinkvote/math500_sft1_cue_s4-01` | `thinkvote_math500_sft1_cue_s4` |
| hard328 Think-SFT + cue, 1 sample, cap 32,768 | `results/cap32/rows-01/sft_cue.jsonl` | `cap32vote_handoff/abaybektursun-1115-005756-309b` (read only) |

## Definitions, fixed before computing

- Token position: the position in the text re-tokenized with the run's tokenizer (`allenai/Olmo-3.1-7B-RL-Zero-Math` @
  `364820b`, `tokenizer.json` from the local Hugging Face cache; no weights). A sign at token t uses the first t tokens only.
- Non-Latin letter: an alphabetic character whose Unicode name starts with one of the scripts of `drift.SCRIPTS` (CJK,
  Hiragana, Katakana, Hangul, Bopomofo, Cyrillic, Arabic, Hebrew, Thai, Devanagari and 13 more). Greek is excluded
  (mathematics), so a switch to Greek prose is not seen. Episode: at least 5 such letters, neighbours at most 200 characters
  apart. `switch`: the sample has an episode; its position is `detect_tok`, the token of the episode's 5th letter (the first
  moment a reader of the prefix can flag it); `start_tok` is the token of its first letter. Switched back: at least 10
  English function words (`drift.ENGLISH`) in the 1,000 characters after the episode's last letter; undetermined when fewer
  than 1,000 characters follow.
- `rep50`: of the 50-token windows inside the first t tokens (every start position), the share equal to an earlier window.
- `loopA`: the runner's rule A (`rln4_lib.onset_lines`, not rewritten). On a prefix it fires once its first verified window
  (8,000 characters, zlib ratio under 0.10) is complete; `loop_tok` is that token.
- `zratio`: `rln4_lib.zratio` of the prefix (lower = more repetitive; used with its sign flipped).
- `wait`: occurrences of the word "wait" in the prefix. `restart`: occurrences of the phrases of `drift.RESTART` ("let me
  start over", "try a different approach", "let me reconsider", "I'm stuck", "this is getting too complicated", ...).
  Both as counts per 1,000 tokens of the prefix.
- `length`: min(n_new, t), i.e. whether the sample is still running at t. The baseline.
- Not right: `score_v3` = 0 at the end of the sample (a cap hit is not right unless its text already holds a right answer).
- Checkpoints t: 4,000, 8,000, 12,000 tokens. Running at t: n_new > t.
- Difficulty stratum of a problem: the cued base's right samples of 4 on it: 0, 1-2, 3-4 (as `riskcov_strat.STRATA`).
- Intervals: 95 %, bootstrap over problems (all samples of a problem move together), 5,000 resamples, seed 0.

## Instrument checks (done before this spec; they are the only numbers seen)

1. `analysis/drift_test.py`: 10 planted positives (Chinese long, short, inside mathematics, Japanese, Korean, Russian,
   Arabic, Hindi, Thai, mixed in an English sentence) each give one episode within 12 tokens of the planted position and
   are marked switched back; 10 negatives are not flagged (clean text, LaTeX, Greek letters in Unicode, names with
   diacritics, mathematical symbols incl. double-struck and mathematical-alphanumeric letters, full-width punctuation, four
   stray non-Latin letters, emoji and Latin-1 letters, code, five CJK letters more than 200 characters apart). A planted
   loop is found by `loopA` and `rep50`; a clean text has neither; a copy rewritten word by word is not a `rep50` repeat.
2. The published counts reproduce from the texts: cap hits with more than 20 Chinese characters, fresh2026 Think-SFT 66 of
   248, RL 3 of 84, base 0 of 219; hard328 Think-SFT 86 of 378, RL 1 of 114.
3. Re-tokenized length minus `n_new`: median 3 for cued cells (the 3 cue tokens), 0 for RL; largest absolute difference 53
   tokens over 8,300 samples. Token positions are therefore exact to about 50 tokens.
4. Still to pass, in `drift_read.py`: with `switch` flags shuffled within problems the within-problem difference of Q2 is
   inside its null interval; with a planted sign (a flag set on 80 % of not-right and 20 % of right samples) the
   within-problem AUROC is above 0.75; a stop rule that never fires reproduces `frontier.py`'s `seq4` and `vote4` rows
   exactly (241 at 30,904 and 241 at 40,410 tokens on hard328; fresh2026 75 at 42,251).

## Q1 Description

Per cell and model: samples with a switch, among all samples and among cap hits; scripts; `start_tok` (quartiles); share of
first episodes that switch back; share of the letters after the first switch that are non-Latin. The 32,768 sample: switches
before and after token 16,384. Hand read of 20 Think-SFT samples with a switch (drawn at random, seed 0: 8 hard328, 8
fresh2026, 4 from the 32,768 run), each with a short quote, my translation and what the text is doing at the switch; it is a
hand read by the agent, not a blind judge. Problem or sample: statistic S = number of pairs of samples of the same problem
that both switch. Null A: flags permuted over all samples. Null B: flags permuted over cap-hit samples only (does the switch
cluster in problems beyond what cap hits do?). 10,000 permutations, one-sided p.

Predictions. P1: by the episode definition 8 % of Think-SFT's hard328 samples switch (105 of 1,312) and 15 % on fresh2026
(82 of 544); RL and base under 1 %. P2: over 95 % of the episodes are Chinese. P3: median `start_tok` of the first switch is
past 8,000; under 10 % start before 4,000. P4: fewer than 40 % of first episodes switch back. P5: S is above null A
(p < 0.01: the switch sits in hard problems) and not above null B (p > 0.05: given a cap hit, it is a property of the
sample). Refuted by the opposite side of each number.

## Q2 Does a switch predict the outcome?

H1. Among Think-SFT samples still running at t, those that have switched by t (`detect_tok` <= t) end right less often than
those of the same problem that have not. Measure: per problem with both kinds at t, mean right of the switched minus mean
right of the others; the mean over those problems, with a problem bootstrap; t = 4,000 / 8,000 / 12,000, hard328 and
fresh2026 pooled and apart. Primary: t = 8,000, pooled. Also the unmatched difference inside each base stratum (0, 1-2, 3-4)
and their sample-weighted mean. Prediction: -10 points at t = 8,000 with an interval that excludes 0. Refuted if the
interval covers 0.

H1b (the 32,768 run). Of the answers longer than 16,384 tokens (93 by result-c8b994, 23 right), those with a switch before
token 16,384 end right less often than those without. Prediction: about 22 have a switch; 2 of 22 right against 21 of 71
(9 % against 30 %). Reported with a Fisher exact test and with the difference inside base strata (a switch may mark a hard
problem). Refuted if the stratified difference's interval covers 0.

## Q3 Which sign predicts best?

Signs, fixed: `switch` (0/1 by t), `rep50`, `loopA` (0/1 by t), `zratio` (flipped), `wait` per 1,000, `restart` per 1,000,
and `any` = `switch` or `loopA`. Outcome: not right. For each t and each set (hard328, fresh2026, pooled; Think-SFT; RL and
base as controls):

- (a) all samples, sign frozen at the sample's end when it finished before t: pooled AUROC of each sign and of `length`.
- (b) samples running at t (here `length` is constant, AUROC 0.5 by construction): pooled AUROC, and the within-problem
  AUROC: over pairs (a not-right and a right sample of the same problem, both running at t), the share where the not-right
  one has the higher sign, ties 0.5; this is the measure of result-f3d708 (0.531 [0.468, 0.589], 0.504 without the first 50
  tokens) and result-b30f15 (0.571 [0.509, 0.634]) on the cued base on MATH-500, which had answer length at the end at 0.68.

Prediction: no sign reaches 0.60 within problem at any t on the pooled set, and none has an interval above 0.55; `length`
in (a) is above 0.80 at t = 8,000 (most samples still running at 8,000 do not end right) and no sign beats it by 0.02 in
(a). `switch` has high precision and low recall: of samples switched by 12,000, under 10 % end right. Refuted by a sign with
a within-problem interval above 0.55.

## Q4 A use: stop at the first sign

Rule family. The sequential vote of "Token frontier" (`frontier.RULES["seq4"]`: draw 2, stop when two agree, at most 4), with
one change: a sample is stopped at the token where its sign fires, costs that many tokens and casts no vote (also when it is
the last stored sample). The sign of a sample is read from its own prefix only, at the checkpoints 4,000 / 8,000 / 12,000
for the counted signs and at the moment of detection for `switch` and `loopA`. Candidates (12):
`switch`; `loopA`; `any`; `rep50`, `zratio`, `wait`, `restart` each at two thresholds, the 75th and the 90th percentile of the
sign among MATH-500 Think-SFT samples running at that checkpoint; and as the length baseline the same rule with "stop every
sample at L", L = 12,000 (`len12000`). Also reported, not candidates: the frontier's own `seq4`, `seq3`, `vote4`,
`seq4_L8000`, `seq4_L12000` (which let the last sample run), and `vote4` with each stop.

Choice. MATH-500 Think-SFT has 159 not-right samples and 93 cap hits of 2,000 (known from the committed rows): enough to
choose on, as every configuration of this repository is. If no candidate fires on at least 30 MATH-500 samples, the choice
moves to a random half of the hard328 problems (seed 0) and the score to the other half plus fresh2026. Chosen: among the
candidates whose right count (mean over the 24 draw orders) on MATH-500 is at least `seq4`'s minus 0.5, the one with the
fewest tokens per problem. Scored once on hard328 and on fresh2026 (both held out from the choice): right (stored order),
right (24), tokens per problem, the paired difference to `seq4` in right (24) and the ratio of tokens with problem-bootstrap
intervals. All candidates are also listed on the held-out sets, marked as not chosen.

H2. The chosen rule saves at least 10 % of `seq4`'s tokens on hard328 and on fresh2026 with no loss of right answers (right
(24) not lower than `seq4`'s by more than 0.5 problem). Prediction: refuted. A switch is seen in about 8 % of samples and
late, so stopping there saves under 5 % of the tokens; the counted signs do not separate right from not-right samples, so a
threshold that saves 10 % loses problems. Expected for the chosen rule on hard328: 2 to 5 % fewer tokens, 0 to 2 problems
lost.

This is a replay on stored rows: a stopped sample is not continued and the "new sample" is the next stored one. It is exact
for rules that only stop samples and draw stored ones, so the chosen rule's held-out row may carry a `score: other` line
with that caveat; nothing else gets one.

## Literature (WebSearch, no Exa key; four papers read in full by a subagent, findings in `tools/paper.py`)

- 2507.15849 (The Impact of Language Mixing on Bilingual LLM Reasoning): on English MATH500 prompts 0.0 to 0.6 % of problems
  switch (Table 1); switch rate rises with length (Fig. 4); for R1-Distill-Qwen-1.5B switching responses score 0.438 against
  0.281 (App. A.3, Table 6, no counts): the opposite sign to H1, not matched by problem.
- 2505.14815 (Language Mixing in Reasoning Language Models): mixing rises with difficulty (Table 2); no table links mixing
  to a sample's correctness.
- 2505.17813 (Don't Overthink it): the shortest of 20 samples is right 57.8 %, the longest 22.2 % (R1-Distill-Qwen-7B, Table
  7); short-m@k stops on length only and never redraws.
- 2604.04930 (Early Stopping for Large Reasoning Models via Confidence Dynamics): a logit-based stop, 11,651 to 10,223 tokens
  for 33.6 to 31.2 % on AIME at a 16,384 cap (Table 2); no vote.
- No published table answers Q2, Q3 or Q4 for a model fine-tuned on traces. idea-6fb0de items 2, 3 and 6 (stop a problem at
  60 % agreement, half-vote guess for an unfinished sample, last-120-characters loop test) are different rules, not run here.

## Outputs

`analysis/drift.py` (signs; cache in `runs/drift_features/`, not committed), `analysis/drift_test.py`, `analysis/drift_read.py`
(Q1 to Q4). `results/drift/describe-01/`, `predict-01/`, `stop-01/`: `run.json`, `readout.json`, `table.md`, `examples.json`
(per sign one sample that ended right and one that did not, with short quotes).
