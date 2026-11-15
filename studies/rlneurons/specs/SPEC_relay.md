# SPEC_relay: Think-SFT writes, RL finishes. A two-model text relay on hard328

Board: idea-968e5b, work-1c43cf. Builds on result-a6ab7a (prefix hand-off: writer and finisher are separable roles),
result-bf6124 (Think-SFT and RL have different difficulty profiles), result-d9d6f3 (Think-SFT cue 219 of 328 in sameraslan's
workspace, 89 cap hits). Written 2026-11-15 UTC before any job of this study was submitted.

## Question

Does a relay in text (one model writes the first part of an answer, the other model finishes it) beat both single models on
the 328 harder problems at about the same generated tokens? Think-SFT with the cue solves more hard problems than RL-Zero-Math
but 89 of its 328 answers hit the 16,384 cap; RL finishes (20 cap hits). The weight-space combination of the same two models
(Think-SFT + (RL - base)) is work-0a00c2; this is the text-space one.

## Literature (WebSearch; the Exa key is invalid in this shell)

No published table answers it: no paper pairs an SFT writer with an RL finisher of the same base, with an own-prefix control
or token matching. Nearest, numbers read from the arXiv HTML bodies by a subagent: Reasoning Relay (2512.20647; prefixes cut at
25/50/75 % of cumulative log-probability on MATH; best relay Gemma-3-4B -> LLaMA-8B at 75 % 63.80 % against the writer's 68.06 %:
no relay beats its writer); Reasoning that Travels (2605.28913; AIME 24-26, relay 0.74 to 9.69 points below the provider);
RelayGen (2602.06454; AIME 2025 large 70.00, small 31.67, relay 68.33); R2R (2505.21600; AIME 12 %, 57 %, relay 55 %);
SpecReason (2504.07891; +1.0 % MATH500 and +3.1 % AIME over the large model, absolute numbers in figures only). All pair a strong
with a weak model; none pairs two models of about equal accuracy with different error types.

## Inputs (not regenerated)

- Writer `think`: Think-SFT (`allenai/Olmo-3-7B-Think-SFT`, revision `6ff857587e040d6d523a3d5f3a56e918f5401d66`, the `think_sft`
  entry of `jobs/wsp_delta_anatomy.MODELS`, written to `/tmp/theta` by `jobs/wsp_edit.py --recipe interp --other think_sft --alpha
  1.0 --rounding nearest`) with the cue, hard328, sample 0, seed 3000000, T 1.0 / top-p 1.0: job
  `abaybektursun-1115-000503-1e5f` (work-0a00c2). 212 of 328 right, 89 cap hits (4 of them scored right), 31 finished wrong,
  10,137 tokens per problem. The same request in sameraslan's workspace scored 219 (result-d9d6f3); same-seed reruns on another
  GPU differ by about 4 to 8 problems. The paired baseline of this study is the 212 sample, whose text is the prefix.
- Writer `rl`: RL-Zero-Math plain prompt, hard328, seed 3000000: job `abaybektursun-1114-151540-86ef` (Day-1 #1). 206 right, 20
  cap hits, 102 finished wrong, 9,315 tokens per problem.
- Both writers were sampled with the RL tokenizer (`frozen4.json`), so prefixes are cut on token ids with no re-encoding between
  models. Think-SFT's cue ids are `frozen4.json` `prefill_ids`; the stored text starts with the cue and `handoff_lib.answer_ids`
  keeps the three sampled ids. The RL answer text is re-tokenized (the count differs from the sampled count in 72 of 328
  answers by at most 49 ids; Think-SFT 54 of 328, at most 24).
- `data/handoff/plan_v2.json` (`prep/relay_plan.py`): all 328 problems, per (problem, writer) the stratum (right / wrong / cap),
  the source, and per cut the prefix length and the sha256 of the prefix ids. `plan_v1.json` is unchanged.

## Arms

Writer {think, rl} x finisher {think, rl} x cut {25 %, 50 %} of the writer's answer ids, all 328 problems, one sample each:
8 arms, 2,624 requests. Request = plain prompt ids + prefix ids (for the think writer the prefix starts with the cue ids);
T 1.0 / top-p 1.0; max new tokens = 16,384 - prefix length, so the cap counts the prefix. Seeds
`handoff_lib.seed(writer, cut, index, RELAY_WRITERS, 91000000)`. Grader v3 on prefix + continuation decoded in one piece.

- Own-prefix continuation (think -> think, rl -> rl) is the matched control for resampling the tail.
- A cap-hit answer has 16,384 ids, so its cut is a share of the cap: 4,096 ids at 25 %, 8,192 at 50 %. Cap-hit prefixes are a
  separate stratum in every table. The arm designed for them, "cut cap-hit Think-SFT answers at 25 % and let RL finish", is
  the cap stratum (n = 89) of think -> rl at 25 %; it is reported on its own line with think -> think at 25 % on the same 89
  as its control.
- Strata by the writer sample's outcome: right (think 208, rl 206), finished wrong (31, 102), cap hit (89, 20).
- Difficulty: by source, AIME (68) against the others (olympiad 202, HMMT 30, AMC 28).

Tokens per problem of a relay = prefix ids + finisher tokens. Compared with one sample of each model (10,137 and 9,315) and
with the vote rows of work-0a00c2 and work-1a972a at equal tokens when they are posted.

Size: if the finisher writes what the writer had left, 4.79 M tokens at 25 % and 3.19 M at 50 % per finisher (7.98 M per
finisher). At 1,050 to 1,400 tokens/s (the writer jobs) that is 1.6 to 2.1 h for one job per finisher, so each finisher is
split by cut: 4 jobs (about 1.2 h and 0.8 h each), one H100 each.

## Instrument checks (before the main jobs)

- Laptop: `analysis/handoff_test.py --plan plan_v2.json`: cut 0 = the plain prompt ids (the stored RL prompt, id for id); cut
  100 with an immediate stop scores what the writer scored, and with a wrong answer line appended scores 0; every request's
  prompt decodes to the writer's stored prompt and its prefix to the start of the stored text; the think prefix starts with the
  cue ids; a cap-hit answer's 25 % cut is a quarter of the cap.
- Smoke on the GPU: RL finisher, the first 10 problems, cuts 0, 25, 50, 100, both writers. Cut 100 must give 0 new tokens and
  the writer's score (failing input for the scorer: the laptop check above); rows read by hand: does the finisher continue
  mid-sentence, and does RL keep the Think-SFT plan or restart?
- H0 in the main run: a model finishing its own prefix scores what its stored sample scored. Refuted if the paired interval
  of own-prefix minus stored excludes 0 at either cut; then the cross arms are read against the own-prefix arm only.

## Hypotheses, each with the observation that refutes it

- H1 (the relay wins): think -> rl at 50 % scores at least 8 problems above the Think-SFT sample (212 here; 219 is the other
  workspace's draw of the same request). Refuted if the paired interval of think -> rl minus think -> think at 50 % includes 0
  or is negative, or if think -> rl at 50 % has fewer than 220 right.
- H2 (the gain comes from cap-hit answers): the difference RL finisher minus Think finisher on Think prefixes is larger, in
  problems, on the 89 cap-hit prefixes than on the 239 others. Refuted if the difference on the others is equal or larger, or if
  the paired interval on the cap stratum includes 0 at both cuts.
- H3 (direction matters): rl -> think is no better than rl -> rl. Refuted if the paired interval of rl -> think minus rl -> rl
  excludes 0 on the positive side at either cut.
- H4 (RL as finisher stops): think -> rl has fewer cap hits than think -> think at both cuts and fewer total tokens per problem
  than the Think-SFT sample (10,137). Refuted if either fails.

## Predictions (filed before any job; mine, from the MATH-500 hand-off rates)

A right prefix at 25 to 50 % is finished right about 85 to 94 % of the time by either model; a cap-hit prefix is a problem the
model does not solve, not a loop (result-51fd20 for the base), so a finisher rescues few. I expect H1 to be refuted.

| arm | right of 328, point [80 % range] | cap hits |
|---|---|---|
| think -> think 25 % | 205 [193, 217] | 85 |
| think -> think 50 % | 207 [197, 217] | 88 |
| think -> rl 25 % | 196 [182, 210] | 40 |
| think -> rl 50 % | 200 [188, 212] | 55 |
| rl -> rl 25 % | 205 [193, 217] | 22 |
| rl -> rl 50 % | 205 [195, 215] | 22 |
| rl -> think 25 % | 207 [193, 221] | 70 |
| rl -> think 50 % | 203 [191, 215] | 50 |

- think -> rl minus think -> think at 50 %: -7 problems [-20, +6]; no arm reaches 220.
- Cap stratum of Think-SFT (n = 89), right: think finisher 12 at 25 % and 8 at 50 %; RL finisher 16 at 25 % and 11 at 50 %.
- Think right prefixes (n = 208) at 50 %: think finisher 190, RL finisher 181.
- RL wrong prefixes (n = 102): Think finisher 28 at 25 %, 18 at 50 %; RL finisher 22 and 14.
- Tokens per problem, total: think -> rl 9,000 at 50 %, 8,500 at 25 %; think -> think 10,100.

## Readout

`analysis/relay.py` (imports `analysis/handoff.py`): per arm right of 328 with Wilson 95 %, cap hits, tokens per problem
(generated and total); paired bootstrap (5,000 resamples, seed 0) of each cross arm against the own-prefix control of the same
writer and of the same finisher, and of every arm against each writer's stored sample; the same by stratum and by source. Raw
rows read before any explanation: 10 relay wins over the Think-SFT sample, 10 losses, and what RL does with a Think-SFT cap-hit
prefix. Run folders `results/relay/<finisher>_c<cut>-01/`, readout `results/relay/readout-01/`.

## Limits known before the run

One sample per prefix, one prefix per problem. Think-SFT is trained (no reward, not no training); the overlap of the 328 with
its training traces is unchecked (result-d9d6f3). A relay needs both models loaded, which the token count does not price.
