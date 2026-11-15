# SPEC_freshaudit: independent second transcription of the 77 PDF-transcribed fresh2026 statements

Board: idea-60f12e, work-831689. Audits result-5251c9 (Think-SFT + cue 75, RL plain 57, base + cue 38 of 136 under the vote
over 4; Think-SFT minus RL +13.2 points [+7.4, +19.1]; order-averaged +14.5 [+8.5, +20.6], result-f941b8). Written
2026-11-15 UTC before any second transcription exists and before any diff is read. Branch `freshaudit` (main is frozen).
No GPU, no model run: the three models are not rerun.

## Question

77 of the 136 problems of `data/fresh/fresh2026_v1.json` (HMMT February 2026 Guts 28; HMMT November 2026 General 7, Theme 6,
Team 8, Guts 28) were transcribed from the official solutions PDFs by Claude subagents; the answer keys were checked, the
statements were not. A wrong statement with a right key makes a problem unsolvable or changes its answer. How many of the 77
statements and answers differ from the PDF in their mathematics, and what does the Think-SFT minus RL contrast become
without them?

## Sources

`prep/freshaudit_prep.py` fetches the five PDFs from the urls of `data/fresh/transcribed_v1/sources.json` and stops unless
each sha256 equals the recorded one (so the audit reads the files the first transcription read), and the three PDFs of the
control (below). Each PDF goes into its own directory under `runs/freshaudit/pdf/` (not committed: copyright); every page
is rendered to a PNG (110 dpi, `pdftoppm`) and to its text layer (`pdftotext -layout`). Urls, sha256 and page counts go to
`results/fresh/audit-01/sources.json`.

## Second transcription (blind)

One fresh subagent per batch of at most 7 problems (15 batches). It gets only: the paths of the page PNGs and of the page
text files of its batch, and the problem numbers. It does not get the data file, `transcribed_v1/`, the repository path of
either, or any model output, and is told not to open anything outside its page directory. It must use two routes for every
problem: read the rendered page (the authority for exponents, fractions, signs, subscripts) and read the text layer (the
authority for the spelling of words and long numbers), and report where the two disagree. Output per problem: `number`,
`problem` (statement verbatim, mathematics in LaTeX), `answer` (the "Answer:" line as printed, LaTeX), `figure` (true if the
PDF prints a figure with the problem), `note`. Stored in `results/fresh/audit-01/second/<batch>.json`.

## Diff: normalisation and classes (fixed here)

`analysis/freshaudit.py`. Normalisation `norm`, applied to both versions of a statement and of an answer:

1. Unicode NFKC; curly quotes, backticks and `''` to `"` and `'`; en and em dashes to `-`.
2. Math delimiters removed: `$`, `$$`, `\(`, `\)`, `\[`, `\]`.
3. `\dfrac`, `\tfrac` to `\frac`; `\dbinom`, `\tbinom` to `\binom`; `\left`, `\right`, `\big`-family, `\displaystyle`
   removed; `\le` to `\leq`, `\ge` to `\geq`, `\ne` to `\neq`; `\ldots`, `\dots`, `\cdots`, `…` to `...`; `\colon` to `:`;
   `\lvert`, `\rvert`, `\vert` to `|`; `\mathrm{deg}`-free: `^{\circ}` to `^\circ`.
4. Spacing commands removed: `\,` `\;` `\:` `\!` `\ ` `\quad` `\qquad` `~`.
5. `\text{..}`, `\textbf{..}`, `\textit{..}`, `\emph{..}`, `\mathrm{..}`, `\operatorname{..}` replaced by their content.
6. Braces around a single character or number after `^` or `_` removed (`x^{2}` to `x^2`); every other brace kept.
7. Tokens: a LaTeX command, a number (digits, with inner `,` or `.`; thousands commas removed), a word, or one other
   character. All whitespace dropped between tokens. A final `.` dropped. Case kept.

Two versions with equal token lists are IDENTICAL. Otherwise `difflib.SequenceMatcher` on the token lists gives the
differing spans (each with 6 tokens of context). Stage 1, mechanical: a span is FLAG if a token on either side is a number,
a LaTeX command, a non-letter character other than `, . ; : " ' ( ) -`, a single letter, or a word of the list (not, no,
non, distinct, different, same, equal, positive, negative, nonnegative, nonzero, integer, integers, real, rational, complex,
prime, odd, even, least, most, exactly, minimum, maximum, minimal, maximal, smallest, largest, greatest, sum, product,
difference, ratio, number, all, any, every, each, some, only, ordered, unordered, and, or, if, than, less, more, greater,
fewer, between, inclusive, exclusive, first, last, second, third, with, without, replacement, uniformly, independently,
random, expected, probability, area, perimeter, length, radius, diameter, remainder, digits, digit); otherwise WORDS.

Stage 2, third read: every problem with at least one span (FLAG or WORDS), and every answer that differs, goes to a fresh
reader with the PDF page (PNG and text layer) and the two versions labelled A and B in an order drawn per problem
(`random.Random(0)`), so the reader does not know which is the data file. For each span the reader gives the final class by
this rule and quotes the PDF clause (one clause, at most 25 words):

- COSMETIC: wording, typography or LaTeX notation differs, the mathematics is the same (e.g. `\cdot` against `\times`,
  `\overline{AB}` against `AB` for a segment, "Compute" against "Find", an omitted point value such as `[5]`).
- MATERIAL: a number, sign, exponent, subscript, variable, condition, quantifier, named object or the question asked
  differs, so that the two versions are different problems or one is ill-posed. The reader states which version matches
  the PDF: A, B, or neither.
- ANSWER (answers only): the two golds are not the same value. Stage 1 for answers: equal after `norm`, or grader v3
  (`rln4_lib.grade_v3`, the prep rule `right`) takes each as right against the other: no difference. An official answer
  printed as `a = b` is split as in `fresh_prep.py` (gold `a`).

A problem's class is MATERIAL if any span is MATERIAL, ANSWER if its answers differ in value, else COSMETIC, else IDENTICAL.
Verdict per MATERIAL or ANSWER problem: `v1 wrong` (the PDF matches the second transcription, or neither), or `v1 right`
(the PDF matches the data file; the second transcription erred). Every FLAG span that the reader calls COSMETIC is listed
with the reader's reason and read by the main session against the page. The kept problems that the second transcriber marks
`figure` are listed (the first transcription dropped problems with a figure the words do not describe); they are read
against the page in stage 2 and counted MATERIAL (`v1 wrong`) only if the statement cannot be solved without the figure.

## Instrument checks, before the real diff is read

1. Planted material corruptions, 10: copies of 10 v1 statements (drawn with `random.Random(1)` from the 77), each with one
   change: 4 change a number, 3 flip a sign or an inequality or an exponent, 3 drop or invert a condition (e.g. "distinct",
   "positive", "at least" to "at most"). Diffed against the unchanged v1 statement. Pass: all 10 are FLAG at stage 1, and
   all 10 come back MATERIAL from stage 2 with the corrupted side named as not matching the PDF. They enter the stage-2
   queue unmarked, mixed with the real problems.
2. Planted cosmetic changes, 10: copies of 10 other v1 statements: `\frac` to `\dfrac`, `$..$` to `\(..\)`, added spaces
   and `\,`, straight to curly quotes, `\le` to `\leq`, `\left( \right)` added, `\ldots` to `\dots`, a final period
   removed, "Compute" to "Find" or "Determine", `\cdot` to `\times`. Pass: none is MATERIAL in the final class (the first
   eight kinds must be IDENTICAL after `norm`; the last two must come back COSMETIC from stage 2).
3. Known-good control, 15: 15 of the 29 kept `hmmt_feb2026` problems of the individual rounds (MathArena index 1 to 30:
   Algebra and Number Theory, Combinatorics, Geometry), drawn with `random.Random(0)`, second-transcribed from the official
   round PDFs by the same procedure and diffed against the MathArena text in the data file. Expected: 0 MATERIAL, 0 ANSWER.
   If not: the third read says whether the second transcription (instrument) or the MathArena text (upstream) departs from
   the PDF, and it is reported as which. AIME 2026 is not in the control: no official PDF url is recorded and the MAA does
   not post one.

If check 1 or 2 fails, the instrument is fixed (a new spec amendment, stated) before the real diff is read.

## Rescore (offline, stored rows only)

`analysis/freshaudit.py rescore`: rows of `results/fresh/{sft1_cue,rl_plain,base_cue}_s4-01/` (cap 16,384) and of
`results/cap32vote/fresh2026_sft1_cue_s4-01/` (Think-SFT at 32,768 and the same answers cut at 16,384), loaded with
`analysis/ordervote.py` `cells` (branch `ordervote`, merged into this branch), which gives per problem the vote in the
stored order (`day1_vote.vote`) and its expectation under a random tie-break (`selector.tie_random`). Per model: one sample
(mean of the 4), vote stored order, vote expected. Contrasts Think-SFT minus RL, Think-SFT minus base, RL minus base (and
Think-SFT at 32,768 minus RL): paired bootstrap over problems, 5,000 resamples, `numpy.random.default_rng(0)`, in points.
The script stops unless set (a) reproduces 75 / 57 / 38 and 75.5 / 55.8 / 38.8.

- (a) all 136.
- (b) the 136 minus every problem with verdict `v1 wrong` (MATERIAL or ANSWER).
- (c) the 59 Hugging Face problems plus the transcribed problems that are IDENTICAL after `norm` in statement and answer
  (no judgment of a reader involved).
- also: the 77 transcribed only, before and after the exclusions of (b).

Problems with a wrong v1 statement are excluded, not rescored: the stored model answers were produced on the v1 statement.
If any `v1 wrong` is found, `data/fresh/fresh2026_v2.json` is written with the corrected statements or answers and a
changelog (`fresh2026_v2_changelog.md`); `fresh2026_v1.json` is not edited.

## Hypotheses, each with the observation that refutes it

H1. Fewer than 5 of the 77 problems have a material error in the data file (verdict `v1 wrong`, statement or answer).
Refuted if 5 or more.

H2. Excluding them (set b) moves Think-SFT minus RL under the vote over 4 by less than 1.5 points from set (a), in the
stored order and as the expectation, and both intervals still exclude 0. Refuted if either moves by 1.5 points or more, or
either interval contains 0.

H3. The `v1 wrong` problems do not favour one model: among them, the number where Think-SFT's vote is right and RL's wrong
minus the number where RL's is right and Think-SFT's wrong is at most 2 in absolute value. Refuted if it is 3 or more.

Predictions: `v1 wrong` on 1 of 77 (0 to 3); answers that differ in value 0; problems IDENTICAL after `norm` 45 of 77 (30 to
60), the rest COSMETIC; control 0 MATERIAL of 15, 9 IDENTICAL (MathArena edits LaTeX); set (c) Think-SFT minus RL, stored
order, between +9 and +17 points with an interval above 0.

## Outputs

`results/fresh/audit-01/`: `run.json`, `sources.json`, `second/` (the second transcriptions), `planted.json` (the 20 plants
and what each stage returned), `diff.json` (stage 1, every problem), `third_read.json` (stage 2), `audit.md` and
`audit.json` (problem id, class, both versions' differing span, PDF quote, verdict), `readout.json` and `readout.md` (the
rescored numbers), `examples.json` (one problem scored right and one scored wrong with its stored rows).
