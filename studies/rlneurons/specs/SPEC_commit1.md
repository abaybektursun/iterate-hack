# SPEC commit1: a closing cue for answers that run long (board work-3d68e2)

Written 2026-11-15 05:30 UTC, before any run.

## Why

On the 328 harder problems the cued base (T 1.0 / top-p 1.0, job abaybektursun-1114-151534-e72c) is right on 164. Its answers of
at most 8,000 generated tokens: 144, 124 right. Its answers over 8,000 tokens: 184, 40 right, at up to 16,384 tokens each
(77 hit the cap). A fresh restart at 12,000 tokens gained +2.7 points at twice the tokens (result-2c2cae). RL 3.1 was trained
with truncated answers as negatives (Olmo 3 report A.6.4); the base has no signal of its budget. The forced-commit arm C of
RLN-3 (knowledge-0b450e) was never scored.

## Procedure (`jobs/commit_cue.py`)

For every stored answer longer than N tokens: keep its first N tokens, append a commit line, let the same model continue at
T 1.0 / top-p 1.0. N in 4,000 / 8,000 / 12,000. Two forms of the line:

- box: `\n\nFinal answer: \boxed{`, at most 64 new tokens, the answer is the content of that box;
- voice: `\n\nI have used most of my space, so I will stop exploring here, settle on the most likely answer from my work above,
  and write it down.\n\n`, at most 1,024 new tokens, graded as any answer (v3).

A configuration (N, form) is a policy over a whole set: answers of at most N tokens count as stored; longer ones count as their
committed continuation. Its score is the number right; its cost is the mean of min(stored tokens, N) + new tokens.

## Choice and test

The configuration is chosen on MATH-500 (stored rows of job abaybektursun-1114-153825-208b, sample 0: 405 of 500 right, 145
answers over 4,000 tokens): the most right; among configurations within 2 problems of the best, the one with the fewest tokens.
That one configuration is the headline on the 328, paired with the stored 164 (bootstrap over problems, 10,000 resamples).
The other five are reported as secondary. All six run in one job, so the choice is made by this rule, not after reading the 328.

## Hypotheses and what refutes them

- H1: the chosen configuration scores above the stored 164 on the 328 with an interval above 0, at fewer tokens than 9,344 per
  problem. Refuted if the interval contains 0 or lies below it.
- H2: the voice form beats the box form at the same N on both sets (a base model continues a transcript better than it fills a
  forced box). Refuted if box >= voice at 2 of 3 N on either set.
- H3 (cost of committing): among stored answers that were right after N tokens, the commit keeps at least 60 %. Reported per N.

Control inside the design: the stored outcome of the same answer is the same context's own continuation without the line.
Also reported: committed answers right among stored cap hits (stored score 0 by definition).

## RL, same procedure

If H1 holds, the same job with `--model rl` on RL's stored rows (jobs -183640-e828 and -151540-86ef), the configuration fixed.

## Instrument check

Smoke `--n 4` per set; read every row: the box content is the extracted answer, the voice continuation ends with an answer and
stops, no continuation starts a new problem.
