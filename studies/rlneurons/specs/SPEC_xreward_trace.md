# xreward trace: when do the 8 directions act

Sub-study of `SPEC_xreward.md`. Written 2026-11-15, before the job.

## Amendment T

Known: base + the top 8 singular directions per layer matrix of (math31 - base) solves 192 of the hard328 (base 164, matched random
rank-8 edit 158, RL 206), with fewer cap hits (46 against 77) and RL's rate of deliberation words.

Claim. The rank-8 edit does not act uniformly over a solution: its drive is higher at self-check points, and differs between
answers that end at the 16,384-token cap and finished answers at the same token index.

Measurement (`jobs/xreward_trace.py`, one H100 job, no generation). The stored base + cue hard328 answers (T 1.0, job
`abaybektursun-1114-151534-e72c`, `/runs/<job>/answers.jsonl` on the Volume, sha256 asserted) are teacher-forced through the BASE
model, each cut to its first 6,000 answer tokens. For every layer and each of `mlp.up_proj`, `mlp.gate_proj`, `self_attn.q_proj`,
with d8 = U diag(s) V^T the top-8 part of (model - base) for that matrix (`wsp_delta_anatomy.spectrum`) and x the module's input at a
position:

    r = ||diag(s) V^T x|| / ||W_base x||

the size of the edit's change of that matrix's output relative to the base output (||U diag(s) V^T x|| = ||diag(s) V^T x||). Stored per
position as the mean over each layer band (0-7, 8-15, 16-23, 24-31). Position i of an answer is the input position that predicts
answer token i.

Conditions: `math31`; `rand0`, `rand1`, `rand2` (math31's singular values with a random orthonormal V, three fixed seeds); `if30`
and `code31` (their own top-8). The random ones control for ||x|| / ||W x||; if30 and code31 for "any RL run's directions".

Instrument check, first in the job, fails loud: x inside V gives the analytic r through a real Linear hook; x orthogonal to V gives 0.

Analysis (`analysis/xreward_trace.py`, numpy), each number per condition with a bootstrap interval over answers:
1. mean r by band; ratio math31 / random.
2. r at the positions that predict `Wait`, `Hmm`, `perhaps`, `Let me check` (and at the positions that read them), over r at all
   other positions of the same answer. Lexical control: the same for `So`, `Therefore`, `Then` (sentence openers that are not checks).
3. Loop onset (`rln4_lib.onset_lines`, `onset_period`): r in the 200 tokens before onset, in the loop, and at the same token index of
   finished answers. Checked on the laptop before the job: none of the 77 cap hits of this T 1.0 cell has an onset under either
   detector (they are long non-repeating work, zlib ratio 0.27 to 0.39). So this part reports the count and is replaced by: cap-hit
   against finished answers at the same token index (bins of 500 tokens).
4. r by decile of relative position, finished answers of at most 6,000 tokens.

Refutation. For the marker contrast: the claim is refuted if math31's ratio (marker positions over other positions) is inside the
interval of the random condition's ratio, or if the lexical control shows the same ratio. For cap against finished: refuted if the
math31 difference is inside the random condition's interval. A specific-to-math reading additionally needs math31 to differ from
if30 and code31.

Outputs: `results/xreward/trace-01/` (`run.json`, the job's `metrics.json`, `readout.json`, `examples.json`). The per-position
shards stay in `runs/<job-id>/` (not committed).
