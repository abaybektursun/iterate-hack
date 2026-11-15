# Answer-statement repair: how much of the base-to-RL gap is a failure to state the answer? (board idea-ae6eba, work-655434)

Written 2026-11-15, before any count below was computed. Code: `grader/repair_v4.py` (the rules), `grader/repair_v4_test.py`
(planted cases), `analysis/repair.py` (upper bound, rule table, vote), `prep/repair_plan.py` and `jobs/` for Part B.

## Question

On MATH-500 at T 1.0 / top-p 1.0 the base with the opening cue has 405 to 418 right of 500 per sample and RL 456 to 464
(Day-1 #3, grader v3): about 10 points. The judge study (`results/anatomy/judge-01/`) extrapolates that about 52 of the base's
358 wrong samples (36 to 79) fail in stating the answer: a placeholder `$Answer$`, a form v3 rejects, or no answer line. RL has
none. How many of the 10 points does a label-free step recover that only makes the base state its answer, when RL gets the
same step?

## Known before this study (not repeated)

- result-e78dfe, result-60d899: grader v3 gives the cued base +21 and RL +5 of 500 over v1; 96 v1/v3 disagreements read, 0
  wrong answers accepted. A literal reading of Wang et al.'s rule gives the base 336 to 355.
- idea-884e91 (sameraslan): 5 of 65 RL-right / base-wrong items have the gold in the base's final line (T1 cell: 135, 165,
  338, 354, 447).
- knowledge-499152: v3's two known errors (a mid-line marker of an invented problem; `2xyz` cut to `2`).
- Team memory (`tools/recall.py`): no item measures a repair of the statement of the answer. Exa was not searched:
  `EXA_API_KEY` is not set in this session (AGENTS.md forbids the MCP Exa tools).

## Data

Attempt 0 of samples 0 to 3 of the two Day-1 #3 jobs: base + cue `abaybektursun-1114-153825-208b`, RL plain
`abaybektursun-1114-183640-e828`; 2,000 samples each; text in `runs/<job>/answers.jsonl` (not committed), scores as stored
(`score_v3`). Sample types as in `analysis/anatomy.py`: right, cap hit, no answer (finished, nothing extracted), finished-wrong.

## Two kinds of change (kept apart in every table)

- A rule that changes EXTRACTION or NORMALIZATION is a grader change. It applies to both models and corrects the measured
  gap. It is not a method and not a route to RL. It is a new grader version in a new file (`grader/repair_v4.py`);
  `rln4_lib.grade_v3` is not edited.
- A step that changes GENERATION (Part B: a forced suffix and at most 64 new tokens from the same model) is a method. Its
  gain is counted on top of the same grader, with its tokens.

## Part A (a): upper bound that reads the gold (analysis only, not a grader)

For every wrong sample: a value in the text is "gold-equal" when `S.grade(norm_v3(gold), norm_v3(value)) == 1`. Values: every
balanced `\boxed{}`; the rest of every v3 marker line; every math span (`$$..$$`, `$..$`, `\(..\)`, `\[..\]`, at most 200
characters, on one line); for a span that contains `=`, also the part after its last `=`. Reported per model and sample type
(finished-wrong, no answer, cap hit): samples with a gold-equal value (i) in the last non-empty line, (ii) in the last 5
non-empty lines, (iii) anywhere. (iii) is loose: a short gold (`2`) equals intermediate values. 20 samples of (ii) are read by
hand (base first, random with seed 0) and the failure is named.

## Part A (b): label-free rules (never read the gold), fixed here

"Unusable" extracted string: None, or, after removing every character of `` $*_.:\()[]{}<>`` and spaces and lower-casing,
empty or one of `answer`, `youranswer`, `finalanswer`, `theanswer`, `textanswer`, `boxedanswer`.

- R1, placeholder: when the v3 answer is unusable and not None, cut the text at that candidate's start and extract with v3
  again; repeat until the answer is usable or nothing is left. The new candidate is accepted only when it starts within the
  5 non-empty lines that end at the placeholder's line; otherwise nothing is extracted.
- R2, lower-case marker: when nothing is extracted (v3 alone, or after R1), candidates are the rests of lines after
  `answer`, any case, optional `**`, `*`, `__`, then `:` or the word `is` (v3's marker with any case); delimiters and
  emphasis removed as in v3; the last usable one is the answer.
- R3, last-line math: when nothing is extracted and the answer ended with the stop token (`finish_reason == "stop"`; never on
  a cap hit): take the last line that holds a letter or digit. Its last math span (`$$..$$`, `$..$`, `\(..\)`, `\[..\]`) is the
  answer. With no span in that line, the line itself, stripped of `*`, `_`, `#`, spaces and one final period, is the answer
  when it has at most 30 characters and holds a digit. Otherwise nothing.
- R4, trailing brace: when the extracted string has more unescaped `}` than `{`, remove `}` from its end (with spaces) until
  balanced or no `}` is at the end.
- R5, form (written from the 4 judged `format` items 379 and 227, so optimistic on these two problems): an extracted string
  `(X) words` or `X) words` with X in A to E becomes `X`; a string `<digits><st|nd|rd|th> words` with no other digit becomes
  the digits.
- v4 = v3, then R1, then R2, then R3 on the extraction, then R4 and R5 on the string; equivalence as in v3 (`norm_v3`,
  math-verify 0.9.0, `dollar_both`).

Each rule is scored alone (v3 + the rule) and v4 as a whole, on both models, on the 2,000 samples and per sample (500):
right, gain over v3 in points with a paired bootstrap interval (5,000 resamples over problems, seed 0), samples changed
wrong to right and right to wrong (both counts shown, neither hidden), and RL minus base under v3 and under v4 on the same
samples. Vote over 4 (the rule of `analysis/day1_vote.py`: plurality, `agree`, ties to the lowest sample) under v4
extraction, with problems fixed and broken. Every wrong-to-right sample of v4 is read by hand (the model's own final
statement must be the gold value); a sample judged wrongly accepted is listed.

## Planted tests (`grader/repair_v4_test.py`)

- The 17 planted wrong answers of the audit and the negative cases of `rln4_grader_v3_test.py` must stay wrong under every
  rule alone and under v4; the 22 audited rows of `grader/cases.json` must stay right.
- New planted wrong cases, which must stay wrong: placeholder after a boxed wrong value; placeholder with the only box more
  than 5 lines above (nothing extracted); a finished answer whose last line holds an intermediate value different from the
  gold; a cap-hit text whose last line holds the gold (R3 must not fire); `112}` for gold 12; `(B) Line` for gold `(C)`;
  `21st` for gold 12; a last line of 31 or more characters without math.
- New planted right cases (each rule must fire): one per rule, and each must be wrong under v3 (the rule is the cause).
- Known limit, asserted so that it is visible: a gold-equal intermediate value inside R1's window or in R3's last line,
  followed by a different final answer that no rule extracts, is scored right.

## Part B: generation-side repair (method; GPU)

Eligible sample: attempt 0, `finish_reason == "stop"`, and v3 extraction unusable (None or placeholder). Eligibility never
reads the gold; both models, same rule. Request: plain prompt ids + the stored answer's ids (`rln4_lib.encode_answer`) + the
suffix ids, same model, T 1.0 / top-p 1.0, at most 64 new tokens, one sample, seed 95,000,000 + 10,000 x sample + problem
index. The suffix is chosen from how the two models' right answers end (counted in Part A, stated in the README before the
run). Score: grader v3 and v4 on stored text + suffix + continuation. Control: the same suffix on a random 100 samples that
are right under v3 (the score must not drop: a suffix that makes a model change a right answer is not a repair).
Tokens: the repair's generated tokens per problem, added to the row's tokens.

## Hypotheses and what refutes them

- H1: at least 2 points of the single-sample gap are answer-statement failures of the base that a label-free rule recovers.
  Refuted if v4 gains under 1 point on the base (mean over the 4 samples), or if the base's gain minus RL's gain is under 1
  point (the gap does not close).
- H2: RL has no answer-statement failures: v4 changes at most 2 of RL's 2,000 samples. Refuted by 3 or more.
- H3: the rules accept no wrong answer: 0 right-to-wrong samples and 0 wrong-to-right samples judged wrongly accepted on
  hand reading. Refuted by 1.
- H4: the judge's extrapolation (52 of 358, range 36 to 79) is an overestimate of what extraction can recover: the upper bound
  (ii), last 5 lines, on finished-wrong and no-answer base samples is under 36. Refuted if it is 36 or more.
- H5 (Part B): the forced suffix recovers at least half of the eligible base samples that v4 does not. Refuted under half.
- A prediction that fails is reported as a result.

## Deviations

(none yet)
