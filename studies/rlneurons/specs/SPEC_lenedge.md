# SPEC_lenedge: does Think-SFT fall apart where its training traces end?

Board: idea-d82c84, work-63892a. Builds on result-997be4 (Drift), result-dd26fe (vote at a cap of 32,768), result-527fbb
(risk-coverage and its correction), result-818c20 (Think-SFT + cue under the vote rules), and the training-overlap scans
`results/wsp1/sft_overlap-03` and `results/fresh/sft_overlap-01`. Laptop only: one pass over the training rows, stored
readouts for the generated side. No GPU, no generation, no weights. Written 2026-11-15 (main frozen; branch `lenedge`)
before any training-side number was computed. Seen so far of the training data: its 16 `dataset_source` names with their
row counts (`results/wsp1/sft_overlap-03/metrics.json`), the message counts by role, and its size on disk (36.1 GB of
parquet). No turn length and no character count has been looked at.

## Facts to explain (generated side, T 1.0 / top-p 1.0, Think-SFT + 3-token cue, hard328)

- 156 of 1,312 samples (11.9 %) switch to a non-Latin script, 98 % of the letters Chinese; RL 12, base 9. First switch at
  token 10,733 / 13,589 / 15,048 (quartiles); English resumes after 85 % of first episodes; the switched text carries on
  the same derivation (`results/drift/describe-01`).
- Finished answers are right 97 to 99 % of the time under 8,000 tokens, 83 % at 8-12k, 68 % over 12,000
  (`results/riskcov/hard328-01`); of the 362 answers that finish after token 16,384 at a cap of 32,768, 99 are right
  (27 %), and 249 of the 368 answers past 16,384 hold more than 20 Chinese characters
  (`results/cap32vote/hard328_sft1_cue_s4-01/readout.json`, key `late_answers`).

## Question and hypotheses, each with the observation that refutes it

Training data: `allenai/Dolci-Think-SFT-7B` @ `83f618e2fe0aed29ee3440a3658a0326c175d09d` (name and revision as in
`analysis/wsp1_sft_overlap.py`), 2,268,178 rows, 2,368,984 assistant turns. A turn's length is the token count of the
assistant message's `content` (thinking and answer together), which is what `n_new` counts on the generated side.

- H1, length edge. The lengths at which the answers switch and lose precision lie beyond the bulk of the training turns:
  13,589 tokens is above the 99th percentile of training assistant-turn length. Refuted if more than 5 % of training
  assistant turns are longer than 12,000 tokens: then that length is inside the training distribution and something else
  causes the drop. Between 1 % and 5 %: undecided, reported as such. Stated as numbers: the share of training turns of at
  least 8,000, 12,000, 16,384 and 32,768 tokens.
- H1, functional comparison. Bins of generated length with edges 0, 2k, 4k, 6k, 8k, 10k, 12k, 14k, 16,384, 20k, 24k, 28k,
  32,768. Per bin: precision of finished answers (right / finished) and share of answers with more than 20 Chinese
  characters, from the committed `results/cap32vote/hard328_sft1_cue_s4-01/rows.jsonl` (1,312 samples, cap 32,768); and
  the training survival S = share of training assistant turns with at least the bin's lower edge of tokens. Spearman
  correlation over the 12 bins between S and precision, and between S and the Chinese share, with a permutation null
  (10,000 permutations of the bins, seed 0). Limit, stated now: every decreasing function of length has the same ranks as
  S, so this test can only refute (precision not monotone in length); it does not separate the training lengths from any
  other cause that grows with length. The comparison that carries information is where the fall starts: the training
  percentile of the first bin with precision under 90 % and of the first bin where over 10 % of answers hold Chinese.
- H1, switch hazard. From the per-sample signs on the laptop (`runs/drift_features/hard328_sft.jsonl`, cap 16,384, and
  `cap32_sft.jsonl`, cap 32,768): per bin, first switches in the bin over samples that entered the bin unswitched. H1
  needs the hazard low where S > 5 % and highest where S < 1 %. Refuted if the hazard reaches half of its largest value
  in a bin whose lower edge has S > 5 %.
- Matched control for the precision part. RL-Zero-Math and the cued base were not trained on these traces, and their
  precision also falls with length (finished answers over 12,000 tokens: RL 24.4 %, base 16.7 %, Think-SFT 68.2 %,
  `results/riskcov/hard328-01`). A fall of precision with length is therefore expected without any training-length edge
  (longer answers are answers to harder problems, see the correction of result-527fbb). The training lengths can explain
  only what is specific to Think-SFT: the switch of language (RL 1 %, base 1 %). The precision fall is reported, not
  attributed.
- H2, language source. Share of assistant turns with more than 20 Chinese characters (U+4E00 to U+9FFF, the count
  `drift.py` stores as `chinese_chars`), and share with a non-Latin episode (`drift.episodes`, the rule behind the 12 %),
  each overall, per `dataset_source`, and split by whether the user turn before it holds Chinese (more than 20 Chinese
  characters): a Chinese answer to a Chinese prompt is not a switch. (a) Chinese in at least 1 % of turns that answer a
  prompt without Chinese: the traces themselves switch, the model repeats a training mode. (b) under 0.1 % of such turns:
  the switch is produced by the model, not copied. Between: reported with the per-source table; the stronger statement
  is then the rate inside the math subset and inside long turns. Also measured: where in the turn the first Chinese
  character sits (share of the turn's characters before it; its token position; inside the thinking or after
  `</think>`), and the Chinese share by turn-length bin (the same bins), to compare with the generated side, where
  Chinese comes late.
- H3, math against the rest. Math turns by subset: `dataset_source` contains "math" (OpenThoughts3 math, 752,997 rows).
  Keyword rule for the other subsets, fixed here: the user turn before the assistant turn matches both
  `\\boxed|\\frac|\\sqrt|\$[^$\n]{1,200}\$` and
  `\b(find|compute|evaluate|determine|prove|solve|how many|what is|calculate)\b` (case-insensitive). H1 and H2 repeated on
  the subset and on subset plus keyword turns. Expected: math turns are longer than the rest.
- H4, controls. RL-Zero-Math switches in 12 of 1,312 samples, the cued base in 9. To be confirmed from the model cards
  (quoted): RL-Zero-Math was trained with RL from the base, not from Think-SFT. If so, the two models that never saw
  these traces rarely switch. What cannot be tested: the base's pretraining text is not available, so whether Chinese
  text in pretraining is the source of the switched text, and whether the base at the same lengths and the same state
  would switch, stays open; the base and RL also rarely reach long coherent derivations (their long answers are mostly
  loops or cap hits), so their low rate is not a matched control for length.

## Predictions, written before the pass

My expectation is against H1 as stated. Reason: 36.1 GB of parquet for 2.37 M assistant turns is on the order of 25,000
characters per turn, and a third of the rows are OpenThoughts3 math, whose traces are long.

| Quantity | Prediction |
|---|---|
| Assistant-turn tokens, 50th percentile | 3,500 |
| 90th percentile | 14,000 |
| 99th percentile | 24,000 |
| 99.9th percentile | 32,000 |
| Share of turns of at least 12,000 tokens | 13 % (so H1 is refuted: over 5 %) |
| Math subset, 50th percentile | 9,000 (longer than the rest) |
| Turns with more than 20 Chinese characters, all | 1.0 % |
| the same, prompt without Chinese | 0.3 % |
| the same, math subset | 0.5 % |
| First Chinese character, median share of the turn before it (prompt without Chinese) | 0.5 |
| Spearman of S with precision over the 12 bins | above +0.9 (uninformative, see the limit above) |

What each hypothesis needs: H1 needs S(12,000) under 1 % (refuted over 5 %). H2a needs at least 1 % of turns after a
prompt without Chinese to hold Chinese; H2b under 0.1 %. H3 needs the math 50th percentile above the overall one. A
prediction that turns out wrong is reported as a result.

## Method

`analysis/lenedge.py`: one pass, 156 shards, each downloaded to `--tmp`, read and deleted (the shard loop of
`wsp1_sft_overlap`: `dataset_files`, `all_turns`, `DATASET`, `REVISION` imported, not copied). Per assistant turn:
shard, row, turn, source, characters, tokens, tokens of the row's earlier messages, Chinese characters, first Chinese
character (character and token), first episode of `drift.episodes` (character and token of its 5th letter), number of
episodes, position of `</think>`, Chinese characters of the user turn before it, the keyword flag. Tokens: the
`tokenizer.json` of `allenai/Olmo-3-7B-Think-SFT` @ `6ff8575` (tokenizer file only), `add_special_tokens=False`, every
turn. If the full tokenization is too slow, a fixed 5 % of rows chosen by a hash of the row id is tokenized and the rest
is estimated from characters with the ratio fitted on that sample; the readout then says so and gives the error. The
per-turn table goes to `runs/lenedge/train-01/` (not committed). Also kept per shard for the hand read: the 15 flagged
turns (more than 20 Chinese characters) with the lowest SHA-1 of the row id, apart for prompts with and without Chinese,
and the 15 longest turns, each as short excerpts.

`analysis/lenedge_read.py`: the aggregates and the comparison; writes `results/lenedge/train-01/` (`run.json`,
`readout.json`, `table.md`, `examples.json`, `hand_read.md`).

## Instrument checks

1. `python -m studies.rlneurons.analysis.lenedge --selftest`: the 10 planted positives and 10 negatives of
   `analysis/drift_test.py` (imported), written as assistant turns of a parquet file with the dataset's schema and read by
   the pass: every positive must come out with an episode and, when it holds more than 20 Chinese characters, with the
   Chinese flag; no negative (LaTeX, Greek, diacritics, mathematical letters, full-width punctuation, four stray letters,
   emoji, code) may be flagged. A planted turn of known token count must come out with that count; a planted Chinese
   passage at a known character must be found there.
2. The pass must read 2,268,178 rows and 2,368,984 assistant turns, or it stops.
3. Generated side: the bins must reproduce the posted `late_answers` (368 answers past 16,384 tokens, 362 finished, 99
   right, 249 with Chinese) from `rows.jsonl`.
4. Hand read by the agent (one reader, not a blind judge): 15 flagged turns after a prompt without Chinese (lowest hash),
   and the 15 longest turns, with short quotes and translations.

## Not done

No new generation. No statement about the base's pretraining data. No causal test: a model trained on the same traces
cut at another length would be the experiment that separates length from content.
