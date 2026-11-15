# xshift: do weight edits that are nearly orthogonal in weight space shift the residual stream along one direction

Sub-study of `SPEC_xreward.md`. Written 2026-11-15, before the full job (a smoke run on 2 inputs and 3 edits came first; it only
checked that the job writes its outputs and that the selftest passes).

Known (README, "xreward"): adding the top 8 singular directions per layer matrix of (RL-Zero-Math 3.1 - base) to the Olmo 3 7B base
at size s lowers the cap hits on the 328 harder problems monotonically (96 at -1, 77 base, 50, 46, 25, 5, 9 at 0.5, 1, 1.5, 2, 3); a
random rank-8 edit of equal norm gives 67 to 79. Other donors, ranks, layer bands and module families were scored too
(`results/xreward/edits/readout.json`). The donors' top-8 subspaces barely overlap in weight space. Nothing is measured in
activations.

## Claim

Edits that are nearly orthogonal in weight space shift the residual stream along one shared direction, and an edit's projection on
that direction predicts its stored cap-hit count.

## Measurement (`jobs/xshift.py`, one H100 job, no generation)

- Inputs: the stored base + cue answers on hard328 (T 1.0, job `abaybektursun-1114-151534-e72c`, sha256 asserted), built as
  `xreward_trace.build` builds them (chat prompt + the stored answer text re-tokenized), each cut to its first 2,048 answer tokens.
  N = 48: the 24 cap hits and the 24 finished answers with the lowest problem indices.
- Positions: the sequence positions of answer tokens 0, 16, 32, ... of each input. Residual stream = the output of each of the 32
  layers (forward hook on the layer), before the final norm.
- Edits: 28 cells of `analysis/xreward_edits.NEW`, with their exact `wsp_edit` arguments: Math 3.1 top-8 at -1, 0.5, 1, 1.5, 2, 3;
  rand8 at -1, 1, 1.5, 2, 3; k = 1 at 1, 2, 3; k = 64; attention only, MLP only; layers 0-10, 11-21, 22-31 at 1.5; Code 3.1,
  Code 3.0, Math 3.0, IF, General at 1; Think-SFT at 0.02; `proj` and `projc` with donor Code 3.0. Left out: `bulk`, `rbulk`
  (reference = the RL model) and Think-SFT at 1 (327 cap hits, a broken model).
- For each edit: the float32 addition of every selected matrix is added to the weight in memory, the same inputs are run, and
  shift = edited - base residual at every stored position. Then the weights are restored from the stored tensors and a bit
  fingerprint of every parameter is compared with the base's.
- Saved per edit, layer and group (all; cap-hit inputs; finished inputs; first, middle, last third of an input's positions): the
  mean shift vector, its norm, the RMS over positions of the shift's norm, and the share of the summed squared shift that lies on
  the mean direction (sum of squared projections on the unit mean / sum of squared norms).
- Logit lens per edit: with m = the base's mean residual at the last layer over all positions and D = the edit's mean shift there,
  logits = unembedding(final_norm(m + D)) - unembedding(final_norm(m)); the 20 tokens raised most and the 20 lowered most.

Two choices that differ from the scored cells, both stated here before the run:

1. No rounding. The scored cells wrote `base + addition` to BF16 with stochastic rounding (`wsp_edit --rounding stochastic`). Here
   the base is held in float32 (its BF16 values exactly), the float32 addition is added with no rounding, and the forward pass
   runs in float32. Reason: the additions are 4e-4 to 2e-3 of the weight norm, mostly below half a BF16 unit in the last place of
   the entry they are added to, so plain nearest rounding of the sum to BF16 returns the base entry and drops most of the edit
   (`wsp_edit`'s selftest 5 shows exactly this). The job reports per edit what nearest rounding would keep
   (`nearest_bf16_effective_scale`). So this measures the intended edit; the scored cells are that edit plus rounding noise of
   about the same norm. Float32 also keeps the shift (about 1e-3 of the residual) above the arithmetic noise of the forward pass.
2. The additions are built from singular vectors cached once per donor and matrix (`wsp_delta_anatomy.spectrum`), by a short
   function with `wsp_edit.target`'s formulas, not by calling `target` 6,000 times. The selftest compares it with `target` on one
   matrix for every edit. rand8 uses `wsp_edit.edit`'s draw (seed 0, sorted names), so it is the scored cell's random edit.

The analysis asserts that each edit's `add_rel` (norm of the addition / norm of the edited base matrices) equals the scored cell's
within 0.1 %.

## Selftest (first in the job, on the real model; the job stops if a check fails)

a. The first edit at scale 0, through the same apply and forward path: largest |shift| is exactly 0.
b. While an edit is applied the parameter fingerprint differs from the base's; after the restore it is identical.
c. For every edit, the in-memory addition of one matrix equals `wsp_edit.target`'s addition (relative difference below 1e-5); an
   addition 1 % too large fails the same check.
d. A planted edit: u (x-bar / |x-bar|^2)^T times 0.1 of the mean output norm is added to `mlp.down_proj` of layer 12, with u a
   random unit vector and x-bar the mean input of that matrix. Olmo 3 passes the MLP output through
   `post_feedforward_layernorm` (gain g) before the residual stream, so the planted direction arrives as g * u. The mean shift at
   layer 12 must have cosine above 0.9 with g * u and below 0.1 in absolute value with g * (another random vector); the shift in
   layers 0 to 11 must be exactly 0.

## Predictions

L* = layer 24 (0-based index of the layer whose output is read), fixed here. All layers are reported too.

Direction: u_math = unit mean shift of `top8_math31` at L* (group all); u_code = the same of `top8_code31`. The projection of an
edit E is x_E = <mean shift of E at L*, u>, with u = u_code for every edit built from Math 3.1's difference (its `--other` is
`math31` or `rl_math`: the sizes, k = 1, k = 64, module families, layer bands, `proj`, `projc`), and u = u_math for the others
(Code 3.1, Code 3.0, Math 3.0, IF, General, Think-SFT 0.02). So no edit is projected on a direction fitted from its own donor.

- P1. Spearman correlation over the 23 non-random edits between x_E and the stored cap hits is at most -0.8. Refuted if |rho| <
  0.5, or if the plain norm of the mean shift predicts cap hits as well: |rho_norm| >= |rho_proj| - 0.05.
- P2. Each of the five random edits has |<mean shift, u_math>| below 10 % of `top8_math31`'s (which is its norm). Refuted if any
  is at or above 10 %.
- P3. cosine(IF, Math 3.1) > 0.5 at L*; cosine(Think-SFT 0.02, Math 3.1) < 0.3 and cosine(General, Math 3.1) < 0.3. Refuted
  part by part by the opposite inequality.

Also reported, not predictions: the cosine matrix between all edits' mean shifts at L*; rho with one direction for all edits; rho
of cap hits with the weight-space size `add_rel` and with the RMS shift; the cosine between the cap-hit and finished group means.

## Outputs

`results/xshift/run-01/`: `readout.json` (P1 to P3, per-edit rows, cosine matrix, logit-lens lists), `run.json` (commit, job id,
command), `metrics.json` (the job's: per edit, group and layer), `examples.json` (one cap-hit and one finished input). The mean
shift vectors (`shifts.npz`, about 50 MB) stay in `runs/<job-id>/`, not committed. Analysis: `analysis/xshift.py`, numpy.

## Amendment 1 (2026-11-15, before the run): the shift of the input-side, output-side and shifted-pair edits

xreward amendment 12 found that RL's input directions with random outputs (`rinx1.5_math31`), its output directions with random
inputs (`routx1.5_math31`) and both subspaces with pairs shifted (`permx1.5_math31`) all score as the random edit (158 to 163 right
against 159; the full edit 203). One run, arms `top8x1.5_math31,rand8x1.5_math31,rinx1.5_math31,routx1.5_math31,permx1.5_math31`,
same inputs and settings as run-01; read at layer 24, group all: RMS shift, and the cosine of each mean shift with the full edit's.

- Q1. The input side sets the size of the shift: `rin` and `perm` have an RMS shift of at least a third of the full edit's;
  `rout` at most 5 times the random edit's. Refuted part by part by the opposite inequality.
- Q2. So a large shift is not enough for the gain: `rin` and `perm` have |cosine| with the full edit's mean shift below 0.3.
  Refuted if either is at or above 0.3 (then direction does not explain why they fail).

## Amendment 2 (2026-11-15, before the computation; work-9d7cfb): do the directions compound through depth?

Offline, on run-01's stored mean shift vectors (`runs/abaybektursun-1115-130144-40a0/shifts.npz`, group all). run-01 holds the full
1.5 edit (`top8x1.5_math31`) and the same edit restricted to layers 0-10, 11-21 and 22-31. If each layer's edit acted alone, the
full edit's mean shift at a layer would equal the sum of the band edits' mean shifts there.

- Instrument check: at layers 0 to 10 the full edit's mean shift equals the L0-10 band's (relative difference below 1e-3), and the
  L11-21 and L22-31 bands' shifts are exactly 0 there.
- R1. At layer 31 the norm of the full edit's mean shift is at least 1.5 times the norm of the sum of the three bands' mean
  shifts. Refuted if the ratio is below 1.2: the bands add, and compounding does not explain the 12-fold gap between the paired
  edit and the input-only edit of amendment 1.
- Also reported: the same ratio at layers 16, 21, 24; the cosine between the full shift and the sum; RMS shifts of the bands.
