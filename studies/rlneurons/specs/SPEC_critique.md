# Draft-critique-revision on MATH-500 (board work-70152d), written 2026-11-15 ~02:20 UTC before any run

Untouched direction on the swarm's idea-basin map: "draft critique revision cycles". Can a model fix its own finished answer
with no verifier and no gold, and does RL change how well it does that?

## Closest published

Huang et al. 2310.01798 Tables 3-4: intrinsic self-correction lowers accuracy on GSM8K for every chat model tested (GPT-4
95.5 -> 91.5, GPT-3.5 75.9 -> 75.1, Llama-2 62.0 -> 43.5); answers move right -> wrong more often than wrong -> right.
s1 (2501.19393 Table 4): an appended "Wait" helps a little on a model fine-tuned on reasoning traces.
Differs in: an untrained base model and an RL-Zero model; the review is a continuation of the same 4k-token chain (no new chat
turn, no instruction to change the answer); MATH-500 with grader v3.

## Procedure (jobs/revise.py)

Draft = the stored T 1.0 / top-p 1.0 cue answer (base: seed 41000000, 410/500; RL: seed 66000000, 457/500; prep/critique_drafts.py,
sha256 base a2a9f38b..., RL f6e8ed77...). Drafts that hit the 16,384 cap (27 base, 8 RL) are not revised and keep their draft
score. Prompt = the pair1 prompt + the draft (re-tokenized, cue ids kept) + the fixed line
"\n\nWait, before I finalize, let me check this solution carefully for mistakes." The same model continues at T 1.0 / top-p 1.0,
cap 8,192, seed 77000000 + i (base) and 78000000 + i (RL). Score = v3 on draft + line + revision (the last answer wins).

## Predictions and refutations

1. Base: right -> wrong >= wrong -> right (Huang). Refuted if wrong -> right exceeds right -> wrong by 5 or more.
2. RL changes its answer less often than base. Refuted if RL's answer-changed count is higher.
3. Gap: revised base minus 410 vs revised RL minus 457. If the base gains more, self-review closes part of the gap.
Tokens: revision tokens per problem are reported beside the draft's (base 3,932, RL 4,696).

## Smoke

n = 20 on base before the full cells: the job writes rows, revisions finish below the cap, and the extracted answer of an
unchanged revision equals the draft's.
