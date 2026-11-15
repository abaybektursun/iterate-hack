# SPEC seen: is the RL gain practice on its training prompts?

Board idea-c1d00f, work-fec451. Written before any run. 2026-11-14.

## Question

72 of the 400 harder problems (`data/rln3/hard.json`) are in the RL training prompts of RL-Zero-Math
(`allenai/Dolci-RL-Zero-Math-7B`, 13,314 prompts): 43 exact, 29 near (`results/rln3/rln3_overlap.json`, rule in
`analysis/rln3_overlap.py`). Every harder-set score of ours uses the other 328. The 72 have no T 1.0 score. Is RL's
advantage larger on the problems it trained on than on matched unseen problems, and by how much?

## Sets

| Set | n | Sources |
|---|---|---|
| seen (`--set hard72`) | 72 | AIME 2022 24, AIME 2023 27, AIME 2024 1, AMC 23 12, OlympiadBench 8 |
| seen, exact | 43 | AIME 2022 20, AIME 2023 23 |
| seen, near | 29 | AIME 2022 4, AIME 2023 4, AIME 2024 1, AMC 23 12, OlympiadBench 8 |
| unseen (`--set hardmatch`) | 130 | every unseen AIME (2022 6, 2023 3, 2024 29, 2025 30), every unseen AMC 23 (28), every sixth unseen OlympiadBench problem by index (34 of 202) |

The match is by source family only: AIME, AMC 23, OlympiadBench. HMMT has no seen problem and is left out. Every unseen
number is the mean of the three family means weighted by the family shares of the seen set it is compared with (all 72:
52, 12, 8; exact: 43, 0, 0; near: 9, 12, 8). The year is not matched: 51 of the 52 seen AIME problems are 2022 or 2023,
59 of the 68 unseen ones are 2024 or 2025. Only 9 unseen AIME problems are 2022 or 2023, too few for a year-matched
set. The control arms carry this confound (below).

## Arms

T 1.0 / top-p 1.0, cap 16,384, 4 samples per problem, no restart, grader v3, seed 3,000,000 + 10,000 s + index (the
hard328 rule, so a problem keeps its seed), RL tokenizer.

| Arm | Model | Prompt |
|---|---|---|
| base | `allenai/Olmo-3-1025-7B` @ `a81bae42` (`data/rln4/frozen4.json`) | cue |
| RL | `allenai/Olmo-3.1-7B-RL-Zero-Math` @ `364820b0` (`frozen4.json`) | plain |
| Code-RL | `allenai/Olmo-3.1-7B-RL-Zero-Code` @ `1ca3bb30` (`jobs/merge_weights.py` `CODE`, alpha 1, nearest) | cue |
| Think-SFT | `allenai/Olmo-3-7B-Think-SFT` @ `6ff85758` (`jobs/wsp_delta_anatomy.py` `MODELS`, `wsp_edit --recipe interp --alpha 1.0`) | cue |

New runs: the 72 for all four arms; the 130 for Code-RL and Think-SFT. Base and RL on the 130 are reused from the
hard328 jobs of work-1a972a (`abaybektursun-1114-200457-e8e6`, `-200505-5ff2`: same seeds, `--samples 4 --restarts 2`;
attempt 0 of each sample is the row used here), once they are finished.

Controls. Code-RL is the matched control: RL-trained from the same base with a code reward. Checked before the run
(model and dataset cards on Hugging Face, Olmo 3 paper arXiv 2512.13961 section 6.1): the model card says "reinforcement
learning from verifiable rewards on the Dolci-RL-Zero-Code-7B dataset which consists of coding queries"; the dataset card
says "13.3k coding questions and answers"; neither names math prompts. So Code-RL did not train on these prompts in its
RL stage and is the control. Think-SFT is a second control with a caveat: its data (Dolci-Think-SFT-7B) has 753 k math
prompts from OpenThoughts3 and 105 k from SYNTHETIC-2, whose overlap with AIME or AMC is not checked. Literature
(WebSearch, four phrasings; the Exa tools had no key): no published accuracy of an RL-trained model on RL-seen against
matched unseen test problems was found; nearest are membership-inference papers (arXiv 2602.11792, 2511.14045), which
report detection scores, not accuracy. The base
with cue and Code-RL on the same problems measure how much easier the seen problems are for a model that did not train
on them (older problems, more copies on the web: pretraining exposure).

## Statistic (fixed here)

For a model m and a problem set, acc(m) = mean over problems of the mean score of its 4 samples (per sample), or the
score of the plurality vote over the 4 (`analysis/day1_vote.vote`).

- D(control) = [acc(RL) - acc(control)] on seen minus [acc(RL) - acc(control)] on unseen (family-weighted), in points.
  Primary: control = Code-RL, per sample. Also: control = base, control = Think-SFT; each for vote over 4; each for
  exact and near.
- Each arm's own seen minus unseen difference (base: pretraining exposure).
- Interval: bootstrap over problems, 5,000 resamples, seed 0, 95 % percentile; seen problems and each unseen family
  resampled separately; all arms resampled together (paired).
- Tokens per answer (mean `n_new`) per arm and set.

## Hypothesis and what refutes it

H: D(Code-RL, per sample) >= +15 points: RL solves the problems it practised on.
Refuted if D is inside +/-8 points.

## What n = 72 can resolve (computed before the run)

On the 246 unseen problems with 4-sample rows (sameraslan's partial RL rows), the per-problem difference RL minus base
has SD 0.37 (one sample) and 0.33 (vote); per family: AIME 0.28, AMC 23 0.49, OlympiadBench 0.39. With SD 0.33 on the
seen 72 the seen side has standard error 3.9 points; the family-weighted unseen side 2.9; D 4.8. Expected 95 %
interval: about +/-9.5 points. So: a true D of +15 is 3.1 standard errors from 0 (detected about 87 % of the time); a
true D of 0 gives an interval that excludes +15 only when the estimate is below about +5.5; the interval is wider than
the +/-8 band, so "inside +/-8" can be met by the point estimate but not by the whole interval. Exact (43) and near (29)
alone: about +/-12 and +/-16 points. The run goes ahead; a wide interval is reported as such.

## Checks

- `analysis/seen_test.py`: planted rows with D = +20 points must give an interval that excludes 0, and planted D = 0 an
  interval that includes 0.
- Smoke: 10 problems of one arm on `hard72`, rows read by hand, before the full jobs.
- Raw rows: for seen problems that RL solves (at least 3 of 4) and the base does not (at most 1 of 4), read RL's
  answers: recalled (short, states the answer without work, cites a known solution) or worked. Compare RL's tokens per
  answer on seen and unseen.
- A job that died with under 2 % of its rows missing is scored as is, and the count is stated.
