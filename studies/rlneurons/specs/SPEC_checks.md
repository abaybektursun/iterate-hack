# SPEC checks: does RL check more, or err less per step? (idea-60d3e1, board work-768257)

Written 2026-11-15 before the analysis script existed. Offline, no GPU. Known when this was written: the gap anatomy
(result-afc423: the gain is a reliability shift; 35 % of the base's finished-wrong answers are slips), result-36e8cd and
result-ffebc2 (RL's weight difference and J-lens write hold-on words), result-96e819 (an appended review pass fixes no
mathematics), and a planner's unverified preview ("RL 9.7 hold-on words per 1k tokens, base 7.1; within a problem the
base's wrong samples minus right samples -0.47 per 1k, 137 problems"). To derive the marker list I counted the first one
to three words of every sentence in 10 base and 10 RL finished answers (random, seed 7): `wait` opens 132 sentences in
36,187 base tokens and 292 in 40,379 RL tokens. No rate by correctness was computed before this file was written.

## Question

RL plain is more reliable than the cued base on MATH-500. Is that because RL checks its work more (more checking text, and
checks that catch slips), or because each step is less often wrong? work-74703c will steer "Wait" into the base
(about 3.5 H100-hours); this study files a prediction for it first.

## Inputs

Attempt 0 of samples 0 to 3 of both Day-1 #3 jobs (T 1.0 / top-p 1.0, grader v3): text in
`runs/abaybektursun-1114-153825-208b/answers.jsonl` (base with cue) and `runs/abaybektursun-1114-183640-e828/answers.jsonl`
(RL), loaded with `analysis/anatomy.py:load`. Located first wrong steps: `results/anatomy/judge-01/labels.json` (pass A).
Problems: `data/rln4/math500.json`.

## Definitions (frozen)

- Token position. The laptop has no tokenizer, so character c of an answer is token c x n_new / len(text).
- Markers: case-insensitive regular expressions, three families. One match is one marker.
  - backtrack: `\b(wait|hold on|hmm+|actually|oops|scratch that|on second thought)\b`
  - check: `\b(double[- ]?check\w*|re-?check\w*|re-?examin\w*|re-?verif\w*|verif(?:y|ies|ied|ying)|check(?:s|ed|ing)?|confirm(?:s|ed|ing)?|sanity)\b`
  - error: `\b(mistake\w*|error|wrong|incorrect\w*|correction|miscalculat\w*|misread|messed up)\b|that can'?t be|doesn'?t make sense|not (?:right|correct)\b`
  - The primary measure is all three families together, per 1,000 tokens. Each family is also reported. `alternatively`,
    `perhaps`, `maybe` are a method choice, not a check: reported as a fourth family, outside the primary measure.
- Check event: a marker with no other marker in the 100 characters before it (a run of markers is one event).
- Rule for a revising event ("effective check", rule version): in the 200 tokens after the event's first marker there is
  both (1) a retraction cue `\b(should be|instead|mistake\w*|wrong|incorrect\w*|error|miscalculat\w*|forgot|missed|not \d|no,)`
  and (2) a number (`\d+(?:\.\d+)?`, 2 or more characters, or after `=`) that occurs nowhere before the event.
- Sample kinds as in the anatomy: right, finished-wrong, cap hit, no answer.
- Intervals: bootstrap over problems, 5,000 resamples, seed 0.

## Hypotheses, each with the observation that refutes it

- H1, per-step error, not checking: within one model and one problem, checking text does not separate right from wrong
  samples. Refuted if right samples have at least 1 more marker per 1k tokens than their wrong siblings (point estimate
  >= +1.0 and interval above 0), in the rate over the whole answer or over the first N tokens (N = the shorter sibling).
  If wrong samples have more markers than right ones, H1 stands (markers then follow trouble instead of preventing it).
- H2, RL checks more: on the same problems RL has more markers per 1k tokens than the base. Needs the paired difference
  RL - base above 0 with its interval; refuted if the interval includes 0 or is below it. Also by base k of 4 and in the
  cell (base 3, RL 4), and over right samples only (so that the base's long wrong samples do not drive it).
- H3, checks catch slips: in right samples a check event is followed by a revised value more often in RL than in the
  base. Tested by the rule on all events of right samples and by the judges on 40 events per model. Refuted if the
  judges' share of `fix` among RL events is not above the base's (interval of the difference includes 0).
- H4, the base does not notice its slips: after a located first wrong step the marker rate is no higher than at the same
  relative position of a right sibling and than at random positions of the same answer. Refuted if the rate in the 300
  tokens after the step is above both controls with intervals excluding 0.

## Analyses (`analysis/checks.py`, results in `results/checks/math500-01/`)

a. Markers per 1k tokens per problem (the 4 samples pooled), base against RL, paired; all samples, finished samples,
   right samples; by base k of 4 and in the (3, 4) cell; by family.
b. Within model and problem (problems with a right and a wrong sample): rate of the wrong samples minus rate of the right
   samples, wrong = any wrong and wrong = finished-wrong; whole answer; and first N tokens of every wrong x right pair
   (N = the shorter of the two), pairs averaged within the problem.
c. The located first wrong steps (pass A quote position, real items). Marker rate in the 300 tokens before the quote and
   in the 300 after its end, against (1) the same relative position of the right siblings and (2) 200 random positions of
   the same answer (seed 0). Share with a marker within 500 tokens after the step, against the same two controls.
   Every one of these samples ended wrong, so a slip that was caught is absent here by selection; d covers those.
d. Effective checks. Rule share over all events, by model and by sample kind. Rule validation: 20 flagged events (10 per
   model, seed 0) read by hand, precision reported. Judges: 40 events per model from right finished samples (seed 0, at
   most one per problem), shown with the problem, about 250 tokens before and after, the marker between `>>>` and `<<<`,
   no model name and no score. Labels: `fix` (a specific earlier statement was wrong and is corrected), `switch` (the
   method or the reading changes; no specific wrong statement is corrected), `confirm` (an earlier statement is tested or
   re-derived and kept), `filler` (nothing is re-examined). Controls: 10 planted fillers (`Wait, ` inserted before a
   sentence of a span with no marker; expected `filler`) and 10 planted corrections (a right `= value` line preceded by
   the same line with a wrong value and `Wait, that's not right.`; expected `fix`); pass at 8 of 10 each. Two passes over
   all 100 items in different batches and orders; agreement and Cohen's kappa. The judges are Claude Code subagents of the
   agent's own model: no hosted provider key works on this machine.
e. Per-step error proxy: uncaught slips per 1k tokens = finished-wrong samples x the judged slip share (21 of 60 base, 5
   of 30 RL) / generated tokens; the same for every first wrong step (finished-wrong / tokens). Caught errors per 1k
   tokens = events per 1k x the judges' `fix` share (right samples). Errors made per 1k = caught + uncaught; catch share =
   caught / made. Uncertainty: Wilson intervals of the two judged shares; the limits (40 events, one judge family, slips
   in cap hits unlabeled, a `fix` is judged from 500 tokens of context) are stated with the number.

## The prediction for work-74703c

Filed as a comment on work-74703c with the commit of the readout, before that work reports. If H1 stands and H3 is
refuted: steering Wait into the cued base raises its Wait rate and its tokens, and changes accuracy by less than the
interval of the run. If H1 is refuted: accuracy rises, by about (right minus wrong marker gap closed) points.
