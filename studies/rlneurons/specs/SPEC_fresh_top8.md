# The 1.5x top-8 edit on the fresh 2026 set (written 2026-11-15 15:10 UTC, before any job)

Board: follows work-ab0f72 (the edit on the 328: singles 207, 198, 199, 197, vote 214; RL 200.0 and 221) and result-5251c9
(fresh2026, n = 136: vote over 4 Think-SFT + cue 75, RL plain 57, base + cue 38; single means 60.0, 50.5, 29.5).

Question: base + 1.5 times the top 8 directions of (RL-Math 3.1 - base) had its size chosen on the 328. Does it stay level
with RL on 136 problems published after every weight file, where nothing about it was chosen?

Cells: four jobs, one per sample s = 0..3, on AWS L40S (`ih submit l40s-small`), each
`wsp_edit --recipe top8 --scale 1.5 --other math31 --rounding stochastic --seed 0 --dir /tmp/theta` (the command of job
`abaybektursun-1115-055641-b417`; `edit.json` must repeat add_rel 0.0011109 and cos_written_add 0.585) then
`run_fresh --model-path /tmp/theta --model-label top8x1.5_math31 --prompt cue --set fresh2026 --temperature 1.0 --top-p 1.0
--seed 7000000 + 10000 s`: the seeds, prompt, cap 16,384 and grader v3 of `SPEC_fresh.md`, no restarts.

Readout: `analysis/mixvote.py` with the three stored models' runs (`s3://.../handoff/fresh/`) and the four new runs: singles,
vote over 4 (`day1_vote.vote`), paired bootstrap against RL and the base.

Predictions, each with the observation that refutes it:

1. Single-sample mean of the edit is within 6 problems of RL's 50.5: in [44.5, 56.5]. Refuted outside.
2. Vote over 4 is between 50 and 62 of 136 (RL 57), above the base's 38 and below Think-SFT's 75. Refuted outside [50, 62].
3. Cap hits per sample are at most 30 of 136 (RL 20 to 23, base 49 to 59): the edit's effect on finishing carries over.
   Refuted above 30.

The edit uses the RL checkpoint's weights: this is not a route without reward. It tests whether 0.11 % of the weights
(intended addition) carries RL's gain to unseen problems.
