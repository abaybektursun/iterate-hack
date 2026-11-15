# cleanneurons SPEC1: neuron-level edits of the Olmo 3 base (written 2026-11-14, before any run)

Question: can a change to a small set of MLP neurons move the base `allenai/Olmo-3-1025-7B` toward
`allenai/Olmo-3.1-7B-RL-Zero-Math` on MATH-500? Two parts. Part T measures how concentrated the RL change is in
neurons (it uses the RL weights, so it is a measurement and never a "no reward" row). Part L looks for neurons that
make the base loop, using the base only, and switches them off (a "no reward" row if it works).

Literature and prior state: board `knowledge-e6bc68`, `knowledge-9d0f85`. No published neuron-level base-vs-RL
transplant exists. Scoreboard today: base 82.8 (cue + restart) vs RL 92.8 on MATH-500; base with cue at
T 0.6 / top-p 1.0 is 378/500 with 98 cap hits and 71 rule-A loops (`studies/rlneurons/results/day1/math500_base_cue_t06_p10-01`).

## Definitions

- Models, tokenizer, prompt, cue, cap, graders: those of `studies/rlneurons` (`data/rln4/frozen4.json`). All code
  imports them from `studies.rlneurons`; nothing is copied.
- Neuron (l, n): layer l in 0..31, unit n in 0..11007 of the gated MLP `down_proj(silu(gate_proj(x)) * up_proj(x))`.
  Its weights are row n of `model.layers.{l}.mlp.gate_proj.weight` and of `up_proj.weight`, and column n of
  `down_proj.weight`. Its activation is `a = silu(gate_proj(x)) * up_proj(x)`, the input of `down_proj`.
  32 x 11,008 = 352,256 neurons.
- Edit file (JSON), the one interface between the parts and the generation job:
  `{"name": str, "zero": {"<l>": [n, ...]}, "copy_neurons": {"<l>": [n, ...]}, "copy_families": [...]}`.
  `zero`: set column n of `down_proj` to 0 (the neuron writes nothing). `copy_neurons`: replace the neuron's three
  weight vectors by the RL model's. `copy_families`: replace whole tensor families by the RL model's, any of
  `mlp`, `attn` (q, k, v, o projections), `other` (every remaining tensor: norms, embeddings, lm_head). Absent keys
  mean no change. Copies are exact bf16 copies, so no rounding question arises.
- Stored answers: `/runs/inputs/rln5/T1.jsonl` (base with cue, T 1.0) and `T2.jsonl` (RL, T 1.0), asserted against
  `studies/rlneurons/data/rln5/map_inputs.json`, turned into token sequences with `rln5_map.build`.

## Part T: transplant curve (job `jobs/transplant_curve.py`, one H100, both models in bf16)

Teacher forcing only. Rows: per cell, the answers with 500 <= n_new <= 3,000 that are not cap hits, sorted by
problem index, 40 evenly spaced (`--rows`). Scored positions: every position after the prompt.

For each arm A (the base with an edit applied in memory) and each position: KL(RL || A) in nats, and whether A's
top-1 token equals RL's. "Decisive" positions: per cell, the 4 % of positions with the largest KL(RL || base).
Closure of arm A on a position set: 1 - mean KL(RL || A) / mean KL(RL || base).

Neuron ranking: s(l, n) = squared L2 norm of (RL - base) over the neuron's three weight vectors, computed in
float32. Arms:

| Arm | Edit |
|---|---|
| `none`, `all` | no edit; every tensor from RL |
| `mlp`, `attn`, `other` | one whole family from RL |
| `top{k}` for k in 0.1, 0.3, 1, 3, 10, 30 % | the k % of neurons with the largest s |
| `rnd{k}_s{0,1}` for the same k | the same number of neurons drawn uniformly, two seeds |
| `mlpL0-7`, `mlpL8-15`, `mlpL16-23`, `mlpL24-31` | all neurons of those layers |

Outputs in `$OUT_DIR`: `metrics.json` (per arm and per cell: mean KL and closure on all and on decisive positions,
top-1 agreement with RL, number of neurons, share of sum(s) the arm holds; config, commit, job id),
`rank.npz` (s as float32 [32, 11008]), `profile.json` (share of sum(s) per layer; share held by the top
0.1/0.3/1/3/10/30 % of neurons; share of the total squared weight change in mlp / attn / other),
`examples.json` (for one row of each cell: 20 decisive positions with the context, RL's, the base's and `top1`'s
top-1 tokens and KLs).

Hypothesis T1: the RL change is concentrated in neurons: `top1` closes at least 50 % of the KL on decisive
positions. Refuted if `top1` closes less than 20 %. Between the two the answer is "partly".
Hypothesis T2: the change lives in the MLPs: `mlp` closes more than `attn` on decisive positions (2602.20904 found
this for a distilled reasoning model). Refuted if `attn` closes more.

Controls (the job writes every file, then fails if one fails): `all` gives mean KL below 1e-4; `none` reproduces
the base's KL exactly; after each arm the edit is undone and one edited tensor is compared bit for bit with the
base's; `rnd{k}` closures are reported next to `top{k}` as the null, and `top{k}`'s share of sum(s) next to both,
so that "top beats random" is not read as sparsity when it only reflects more changed weight.

## Part T2: attribution ranking (added 2026-11-14 after Part T; `transplant_curve.py --rank attr`)

Part T ranked neurons by weight change and found closure about proportional to the number of neurons copied. That does
not show that no small set exists: weight change may be a poor ranking. Part T2 ranks by effect. Rows are split in two
halves by order (A ranks, B scores). On half A, with L = mean KL(RL || base) over the decisive positions after the cue,
the score of neuron (l, n) is the first-order drop of L when the neuron is copied from RL:
-(theta_RL - theta_base) . dL/dtheta summed over its three weight vectors (one backward pass per row, gradients
accumulated in float32). Arms `attr{k}` for k in 0.1, 0.3, 1, 3, 10 % are scored on half B next to `top{k}` and `rnd{k}`
on the same rows, cue positions left out.

Hypothesis T3: a small set exists that weight change misses: `attr1` closes at least 30 % of the decisive KL on half B.
Refuted if `attr1` closes less than 15 %; then the RL change is spread over neurons under both rankings.
Control: the first-order prediction for `attr1` and the measured drop of L on half A are both reported; a ranking whose
top set does not lower L on its own rows is broken.

## Part T3: is the RL change a constant push? (added 2026-11-14 after Part T2 and the first Part I run; `transplant_curve.py --bias`)

Observation (job `sameraslan-1114-154532-cdc8`, `results/describe/attr_top100-01/`): of the 100 neurons whose copy from RL
moves the base most, 44 are on almost everywhere (|a| beyond the layer's p97 at more than half of all positions) against 1
of 100 random neurons; their mean |a| is ten times a random neuron's; their weights equal the base's to four digits. A
small weight change on an always-on neuron adds nearly the same vector to the residual stream at every position.

Hypothesis T4: the RL change of the MLPs acts mostly as one constant vector per layer. Arm `bias_mlp` adds to the base,
at every position, d_l = the mean over half-A positions of RL's MLP output minus the base's MLP output on the base's own
MLP input. Supported if `bias_mlp` closes at least half of what `mlp` closes on half B (decisive KL after the cue);
refuted if it closes less than a quarter of it. Control `bias_mlp_rnd`: a random vector of the same norm per layer must
close nothing. `bias_layer` (or `bias_resid_L*`) asks the same for the whole layer. Arm `dense` copies only the always-on
neurons from RL, with `dense_rnd` (the same number of other neurons per layer) as its control: supported as the carrier
if `dense` closes several times `dense_rnd`.

If T4 holds, the RL model is close to the base plus a fixed steering vector per layer, and the next question for a
no-reward route is whether that vector can be found without the RL model.

## Part L: loop neurons, base only (job `jobs/loop_neurons.py`, one H100)

1. Loops. For the 78 rows of `studies/rlneurons/data/rln4/k.json`: the sequence prompt + the base's own prefix
   (`own_prefix_ids`; SPEC4 §2 of rlneurons defines it) is continued by the base at T 0.6 / top-p 1.0 for up to
   2,500 tokens. Sampling noise is a function of (row, step) only, so that every later condition sees the same
   noise. Loop detector on token ids: the last 240 generated tokens are periodic (`tok[i] == tok[i - p]` for at
   least 95 % of them, some period p in 2..120); onset = the first position from which that holds. Rows that loop
   are split by problem index into half A (ranking) and half B (held-out test).
2. Ranking on half A. Window: up to 3,000 tokens ending 1,000 tokens after the onset. Loop positions: from
   onset + p on. Normal positions: the same number, drawn before the onset. m_loop = sum over loop positions of
   log P(actual next token), m_norm the same over normal positions. Attribution of neuron (l, n) to m is the
   sum over positions of a * dm/da (gradient times activation, one backward pass per window).
   Ranking `attr`: mean attribution to m_loop minus the absolute mean attribution to m_norm (a neuron that
   pushes the loop on and matters little for normal text ranks high).
   Ranking `act`: standardized difference of the mean activation, loop positions against normal positions.
3. Conditions, each an intervention on the base: `zero` of the top K neurons of a ranking for K in 10, 100, 1,000
   (`attr10` ... `act1000`); layer-matched random neurons for K in 100, 1,000, two seeds (`rnd100_s0` ...);
   Goodfire's top-K activation mask (per position and layer keep the K activations with the largest |a|, zero the
   rest) for K in 3,300, 1,100, 860, 330 (`mask3300` ...), with a random-K mask for 860 as its control; `none`.
   Measured for each: (a) held-out loop rate: half B rows restarted 300 tokens before their onset and continued
   800 tokens with the same noise, share that the detector flags; (b) on 40 finished right T1 answers
   (the Part T row rule applied to T1, right under grader v3 if the row has it): mean KL(base || condition) and
   the change of the mean log-prob of the written token.
4. Selection: the `zero` set with the lowest held-out loop rate among those with mean normal-text KL below
   0.01 nats (for scale, base against RL is 0.06 to 0.09). Written as `edit_loop.json` (the edit file format), with
   every other `zero` set as `edit_<condition>.json`.

Outputs in `$OUT_DIR`: `metrics.json` (per condition: held-out loop rate with its count, normal-text KL and
log-prob change; number of rows that looped, halves; config, commit, job id), `loops.json` (per row: onset,
period, the 300 characters before the onset and the looped text), `rank.npz` (both rankings, float32 [32, 11008]),
the edit files, `examples.json` (one held-out row that stopped looping and one that did not, under the selected
edit: text before and after).

Hypothesis L1: loops are neuron-sparse in the base: zeroing at most 1,000 neurons (0.3 %) halves the held-out loop
rate with normal-text KL below 0.01 nats, and layer-matched random neurons do not. Refuted if no `zero` condition
halves it under that KL, or if random neurons do as well.
Hypothesis L2 (Goodfire Table 1 on this model): `mask860` raises the mean loss on normal text by less than 5 %,
and the random-K mask raises it several times more. Refuted otherwise.

Controls: the detector must flag a planted loop and must not flag 20 finished T1 answers; `none` restarted with
the same noise must reproduce its own continuation token for token; zeroing a neuron in memory and through the
hook-free weight edit must give the same logits on one window.

### Detector version 2 (2026-11-15, before any Part L number was posted)

Version 1 above (period at most 120 tokens) flags 8 of the 38 cap hits of a base T 0.6 cell (job
`sameraslan-1114-153510-57fb`, 414 of 500 rows before a billing stop), against 28 with rule A: the base repeats whole
paragraphs word for word, with periods up to 574 tokens (median 232). Version 2: period p in 2..600; the rule fires when
`tok[i] == tok[i - p]` for at least 95 % of the last max(240, p) tokens. It flags the same 28 rows as rule A and none of
376 finished answers. The held-out continuation is 1,600 tokens, since a loop of period p can be flagged only
p + max(240, p) tokens after its onset. Every Part L and Part I output names the detector version. The K-route count
"5 of 78 rows looped" (job `sameraslan-1114-153500-bb54`) used version 1 and is not a loop rate.

## Part I: what the neurons do (job `jobs/describe_neurons.py`, one H100; added 2026-11-14 on Samer's request)

A score change is reported together with its explanation. For every neuron set that Part L or Part T selects (an
edit file), and for the same number of layer-matched random neurons as the reference:

1. Activation record. Both poles of a neuron are treated as separate units (Goodfire): the positive side and the
   negative side of a = silu(gate) * up. Over the 80 stored answers of the Part T row rule plus the looped rows of
   Part L (`loops.json`): per neuron and pole the quantiles p50, p90, p99, p99.9, max of |a|, and the share of
   positions beyond the layer's own p97 (how sparse it fires).
2. Top contexts. Per neuron and pole, the 20 positions with the largest |a| from different answers where possible:
   60 tokens before, the token, 20 tokens after, the activation, and the next token the model wrote.
3. Output. The 15 tokens most promoted and most suppressed by the neuron's write direction, read through the final
   norm weight and `lm_head` (column n of `down_proj`). The effect on later layers' neurons is left out.
4. Timing against the loop. Mean activation of each selected neuron at offsets -200 .. +400 tokens around the loop
   onset, over the looped rows, against the same neuron on normal text. A loop neuron in the causal sense rises
   before or at the onset; one that only reacts to repeated text rises after one period.
5. Dose. Loop rate on half B (the Part L test) with the selected set's write scaled by 0, 0.5, 1, 2: a neuron set
   that drives loops gives a loop rate that grows with the factor.
6. Base against RL. For each selected neuron: cosine between the base's and the RL model's gate, up and down
   vectors, the ratio of their norms, and the mean |a| of the same neuron in the RL model on the same text. This
   says whether RL changed the neurons the edit touches (gain or direction) or left them alone.
7. Descriptions. A reader (an LLM subagent, given item 2 for the first 10 contexts only) writes one sentence per
   neuron pole. Test: for the other 10 top contexts mixed with 10 random contexts of the same answers, the reader
   marks which ones fire from the sentence alone; reported as accuracy against the 50 % chance level, next to the
   same test for the random reference neurons. A description that does not predict is reported as such.

Outputs: `neurons.json` (items 1, 3, 6 per neuron), `contexts.json` (item 2), `onset_trace.json` (item 4),
`dose.json` (item 5), later `descriptions.json` (item 7), and `analysis/` makes one figure per claim.

Hypothesis I1: the selected loop neurons are active before the loop onset and the loop rate follows the dose.
Refuted if they rise only after the first repeated period or the loop rate does not change with the factor: then
they detect repetition and the Part L effect, if any, has another cause.

## Part G: generation with an edit (job `jobs/run_edit.py`)

Builds a checkpoint directory from the base snapshot and an edit file (rewrites only the safetensors shards that
hold an edited tensor, links every other file), then runs `studies.rlneurons.jobs.run_cell` on it unchanged
(vLLM, graders, row format). `run_cell.py` has another writer, so it is not edited: `run_edit.py` points
`run_cell`'s model download at the built directory and writes `edit.json` and `build.json` (tensors changed,
neurons changed, sha256 of the edit file) next to `run_cell`'s outputs. Check before generation: the built
checkpoint, loaded tensor by tensor, differs from the base in exactly the tensors and entries the edit names.

Rows to run once Part T and Part L have reported (MATH-500, cue, one sample, grader v3):
- L: the selected loop edit at T 0.6 / top-p 1.0, seed 1,000,000 (the existing 378/500 cell is the paired
  baseline) and at T 1.0 / top-p 1.0, seed 41,000,000 (410/500). Success for the scoreboard: more than 414/500
  (82.8, cue + restart) at no more generated tokens per problem than the unedited cell. The strongest simple
  baseline for loop removal is a repetition penalty (rlneurons cell R1, 1.1 at T 0.6, not run): if the edit helps,
  that cell is run before any claim.
- T: `top1` and one random arm at T 1.0, only if Part T is not refuted; reported as a measurement with RL weights.

## Layout

`lib/neurons.py` (ranking, edit application in memory, checkpoint build), `jobs/`, `analysis/`,
`results/<experiment>/<arm>-<nn>/` with `run.json`, `metrics.json` and examples, `README.md` as the index.
