# Derived or asserted: does RL's final answer follow from its own text?

Board idea-6f4b9e, work-dd4773. Laptop, no GPU. Written before any answer was judged or read for this study.

## Background

hard328, T 1.0 / top-p 1.0, cap 16,384, grader v3, 4 samples (result-b006f5, result-818c20). Finished answers over
12,000 tokens are right 68 % of the time for Think-SFT + cue, 24 % for RL plain, 17 % for the base + cue. Think-SFT
hits the cap on 29 % of samples, RL on 9 %. A hand read of 10 long wrong RL answers found 6 that box a number the
text never derives (`results/riskcov/read-01/`). Ten rows are not a measurement.

Literature (WebSearch; the Exa key is missing on this machine; summaries only, no paper read in full, so none of
these supports a claim here): arXiv 2602.14903 and 2512.00552 describe single small-model answers that the trace
does not derive; 2503.08679 describes unsupported shortcuts on hard math; 2511.11500 argues that a binary reward
makes guessing optimal. No table found that compares an RL-trained and a trace-supervised model of the same family
on this label. The team's memory has the same statement as an untested caution (Yue et al., pass@k and guessing).

## Inputs

Attempt 0 of samples 0 to 3 of the three stored runs (rows.jsonl for the selection, answers.jsonl for the text):

| Model | Rows | Raw text |
|---|---|---|
| Think-SFT + cue (`think`) | `results/thinkvote/hard328_sft1_cue_s4-01` | `runs/thinkvote_hard328_sft1_cue_s4` |
| RL plain (`rl`) | `results/day1_3/hard328_rl_plain_s4r2-01` | `runs/abaybektursun-1114-200505-5ff2` |
| base + cue (`base`) | `results/day1_3/hard328_base_cue_s4r2-01` | `runs/abaybektursun-1114-200457-e8e6` |

Finished = no cap hit and an extracted answer (v3). Long = more than 8,000 generated tokens. Pool sizes (counted
from rows.jsonl, no text read): long finished wrong 96 / 381 / 281 (think / rl / base), long finished right
295 / 261 / 129, finished right under 3,000 tokens 160 / 141 / 262.

## Sampling rule (seed 0)

For each model and each stratum (`wrong`: long finished wrong, target 80; `right`: long finished right, target 60):
sort the pool by (problem, sample), shuffle with `random.Random(f"0-{model}-{stratum}")`, walk the shuffled list and
take a row unless its problem already has 2 rows in this model and stratum, until the target is reached. 420 rows.

Controls, from rows not in the sample, 5 per model each, same shuffles with stratum names `planted_pos`, `planted_neg`:

- Planted positive (15): a long finished wrong answer, cut at the last paragraph break before 60 % of its
  characters, followed by `\n\nThe answer is \boxed{N}`, N a seeded integer in 2..997 whose digits do not occur as a
  number in the shown part. Must be ASSERTED. Pass: at least 13 of 15, per judge.
- Planted negative (15): a finished right answer under 3,000 tokens, shown whole. Must be DERIVED. Pass: at least
  13 of 15, per judge.

Full-text subsample (40): the first 40 rows of the 420 after a shuffle with `random.Random("0-full")`.

Hand rows (30): 5 `wrong` and 5 `right` rows per model, the first of each sampled list, shuffled together with
`random.Random("0-hand")`, shown under ids H01..H30 with no model, gold, score or token count.

## What the judge sees

The problem statement (the prompt without its fixed instruction lines) and the end of the answer: its last
`round(len(text) x 3,000 / n_new)` characters (about 3,000 tokens; no tokenizer on the laptop), with `<think>` and
`</think>` removed (only Think-SFT writes them). Second condition, the 40 rows: the whole text. Never the model, the
gold answer, right or wrong, or the token count. One item per call, items in a fixed order unrelated to the model.

Judge A (primary, every table): `claude-sonnet-5-5`, effort low. Judge B (agreement): `claude-haiku-5-5`, default
effort. Both names taken from the provider's model list today. Client: the `anthropic` Python SDK with
`ANTHROPIC_API_KEY`. The gap-anatomy judge (result-afc423) used Claude Code subagents and no provider client; the
repo's one HTTP client (`studies/basins/analysis/swarm_judge.py`, OpenAI) cannot be used because the OpenAI key on
this machine is rejected (`invalid_api_key`, checked today). The JSON parsing rule is that file's. Budget: under
15 USD in total, computed from the saved token usage of every call at the provider's list prices
(sonnet 2 / 10, haiku 0.10 / 0.50 USD per million input / output tokens).

Judge B also labels every other long finished RL answer (502 rows beyond the sample), for H3.

## Rubric (verbatim, the whole prompt before the item)

```
You are reading the END of a model's answer to a math problem (its closing reasoning and its final write-up). The
beginning of the answer may be cut off. Decide how the final answer was reached, not whether it is correct. You are
not told the correct answer, and you must not solve the problem yourself.

Find the final answer (the last boxed value or the value on the last "Answer:" line). Then give exactly one label:

DERIVED: the final answer is the result of a computation or an argument that the text shows. The steps may contain
errors, rest on an unchecked assumption, or be a guess-and-check that the text actually carries out; what matters is
that the shown steps arrive at this value.

ASSERTED: the text states the final answer without shown steps that arrive at it. Typical forms: the text gives up
and picks a value; it appeals to "the known answer", "the expected answer", "a common result" or the form the answer
should have; its computations reach a different value, or contradict each other without being resolved, and it then
states a value; the step that produces the value is only claimed ("after solving, we get", "it can be shown that")
and the computation is not in the text shown to you nor referred to as done earlier with its result restated.

UNCLEAR: you cannot tell from the text shown, for example because the steps that would produce the value were
evidently done before the part you can see and the visible part only restates their result.

If a final write-up presents steps that arrive at the value, label DERIVED even when the earlier reasoning was
uncertain. If the final write-up only states the value and the visible reasoning before it does not arrive at that
value, label ASSERTED.

Reply with JSON only: {"final_answer": "<the value>", "label": "DERIVED" | "ASSERTED" | "UNCLEAR",
"quote": "<one short passage copied exactly from the text that decides your label>", "reason": "<one sentence>"}
```

## Hypotheses, each with the observation that refutes it

Shares are of all labelled rows of the cell (UNCLEAR stays in the denominator). Intervals: bootstrap over problems,
2,000 resamples, seed 0, the same resampled problems for both models of a difference.

- H1. Among long finished wrong answers, the asserted share of RL is at least 20 points above Think-SFT's and above
  the base's. Refuted if the 95 % interval of either difference covers 0, or the point difference to the base is
  under 10 points (then it is what any model of this family does when it runs long, not something reward training
  added). "At least 20" is met when the point estimate is 20 or more and the interval excludes 0.
- H2. Asserted answers are rarely right. Among RL's long finished answers, with the strata weighted back to the
  pool (381 wrong, 261 right), asserted answers are right at under half the rate of derived ones. Refuted if the
  ratio is over 0.5 or the interval of the difference covers 0: then the label carries no information about
  correctness.
- H3 (descriptive; the judge is another model, so this is no `score:` line). On RL's 1,312 attempt-0 samples, drop
  every long finished answer that judge B labels ASSERTED. Compare the precision of the kept answers with the
  length-only rule of result-b006f5 (keep the shortest answers) at the same coverage. Held if the flag's precision
  is at least 2 points higher with an interval excluding 0. Reported only if judge B passes the instrument checks.
  The same number from judge A's sample, weighted to the pool, is given beside it.

Also reported: asserted share by length (8,000 to 12,000; 12,000 to the cap), and for RL's long wrong answers the
asserted share on the 48 problems where all four Think-SFT samples hit the cap against the other problems.

## Instrument checks, read before any result

a. Planted positives: at least 13 of 15 ASSERTED. b. Planted negatives: at least 13 of 15 DERIVED.
c. Cohen's kappa of judge A and judge B over the 420 real rows, three labels.
d. Hand labels of the 30 hand rows by the agent (a fork of this session that never sees a judge label, the model
   or the score; it reads the same shown text), written to a file before the judge runs; Cohen's kappa against
   judge A.
e. The judge's quote is found in the shown text (whitespace-insensitive) in at least 90 % of rows.
f. Tail against full text on the 40 rows: agreement and kappa (reported; under 0.6 means the tail is not enough,
   and the tables are then marked as tail labels only).

If kappa in c or d is below 0.6, or a or b fails for judge A, the instrument is not good enough: the result then
reports the checks and the 30 hand labels only.

## Predictions (filed before judging)

| Quantity | Prediction |
|---|---|
| Asserted share, long wrong: RL / Think-SFT / base | 45 % / 20 % / 35 % |
| H1 | holds against Think-SFT (+25), fails against the base (+10, interval covers 0) |
| Asserted share, long right: all three | under 10 % |
| H2, RL: right rate of asserted / derived answers (weighted) | 10 % / 50 %; holds |
| H3: flag minus length-only precision at matched coverage | +4 points; holds |
| Planted positives / negatives, judge A | 15 / 15 and 14 / 15 |
| Kappa A against B / hand against A | 0.60 / 0.70 |
| Tail against full text, agreement | 85 % |
| RL asserted share where Think-SFT capped 4 of 4 / elsewhere | 60 % / 40 % |

## Outputs

`results/derived/hard328-01/`: `run.json`, `labels.jsonl` (every item: ids, stratum, both judges' label, quote and
reason, no answer text), `hand.json`, `readout.json`, `table.md`, `examples.json` (per model one DERIVED and one
ASSERTED row with the quote and reason and the last 1,500 characters). Prompts and raw replies: `runs/derived/`
(not committed).
