# SPEC 1: J-lens workspace diff, base against RL (idea-8a0a28, work-50d329)

Written 2026-11-14, before any GPU job.

## Question

On identical text, which vocabulary tokens does the RL model (`allenai/Olmo-3.1-7B-RL-Zero-Math`) hold in its middle-layer
J-lens readout that the base model (`allenai/Olmo-3-1025-7B`) does not, and where in an answer does the difference appear?
The aim is an explanation of the 53-problem gap on MATH-500 (cued base 410, RL 463 of 500, grader v3) with concrete
per-problem examples, and a token list for a later intervention.

## Terms

- J-lens (Anthropic, arXiv 2607.15495): for layer l, `J_l` is the average Jacobian of the last block's output with respect to
  the output of block l. Readout of an activation h: `softmax(lm_head(final_norm(J_l h)))`. Its top tokens are the words the
  model is poised to write later in the text.
- Lens file: `neuronpedia/jacobian-lens`, revision `d2527c3cdbaa60dd4b65cbca1604921f044e989a`, file
  `olmo-3-1025-7b/jlens/Salesforce-wikitext/Olmo-3-1025-7B_jacobian_lens.pt` (fitted on the base, 568 WikiText prompts,
  layers 0 to 30, fp16). No lens exists for the RL model.
- Fixed readout: both models' activations are read through the same map: the base lens, the base final norm and the base
  `lm_head`. The difference of the two readouts is then a property of the activations alone.
- Word-like token: its decoded string has at least one letter or digit. The top-K lists hold word-like tokens only.
- Presence of token v at a position: v is in the top K = 8 word-like tokens of the readout.

## Inputs

The 1,000 stored answers of RLN-4 (T1: base with cue; T2: RL; T 1.0), the same files and token sequences as the RLN-5 map
(`studies/rlneurons/jobs/rln5_map.py`, `build`): Volume `iterate-runs`, `inputs/rln5/T1.jsonl` and `T2.jsonl`, sha256 in
`studies/rlneurons/data/rln5/map_inputs.json`. Problem groups (`both` 398, `rl_only` 65, `base_only` 12, `neither` 25) and the
hand labels of the 65 from `studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json`.

## Method

Teacher forcing, no sampling. Each stored answer goes through both models. At every position after the prompt, and at each
layer of 10, 12, ..., 30 (the workspace band of the paper is 38 to 92 % of depth, layers 12 to 29 of 32), the job computes the
fixed readout of each model's activation. Entry j of every per-position array is read at the input position that predicts
written token j, the same alignment as the RLN-5 map shards.

Saved: for every (cell, group, model, layer) the summed readout probability and the presence count of every vocabulary token;
at two stored layers, per position and model, the top-8 tokens with their log-probabilities and the log-probability of the
watch list.

Watch list, fixed here before the run. Self-check tokens: ` Wait`, `Wait`, ` wait`, ` check`, ` verify`, ` mistake`,
` error`, ` wrong`, ` But`, ` Hmm`, ` Actually`, ` again`, ` correct`, ` double`, ` careful`, ` confirm`. Neutral tokens:
` the`, ` so`, ` Therefore`, ` equation`. A string that is not one token in the tokenizer is dropped and listed.

## Instrument checks (in `checks.json`)

1. Plumbing: `lm_head(final_norm(output of block 31))` equals the model's logits (max absolute difference below 0.1) for
   both models.
2. The lens reads upcoming words. Hit@8 = share of positions where one of the top-8 tokens is among written tokens t+2 to
   t+32. Compared at each layer for: the J-lens; the logit lens (no J); the J of a different layer (l + 8 or l - 8), which
   should fail; and the J-lens scored against a window half an answer away (chance for this text). The lens counts as working
   at a layer if the J-lens hit@8 is above all three others.
3. Transfer to RL: the same hit@8 for RL activations on RL text. The fixed readout is used for RL only at layers where this
   is at least 0.9 of the base value on base text.
4. Demo prompt of the lens repository ("Fact: The currency used in the country shaped like a boot is"): top-10 at each
   layer for both models, saved for reading.

## Hypotheses and what refutes them

- H1. On identical text the RL model's readout holds self-check tokens more often than the base's. Refuted if no self-check
  token of the watch list has a 95 % interval (bootstrap over problems) for presence(RL) minus presence(base) above 0 at
  either stored layer, or if the neutral tokens shift by as much.
- H2. The difference of H1 is larger on the base's answers to `rl_only` problems than on its answers to `both` problems.
  Refuted if the interval of that difference of differences includes 0.
- H3. The readout leads the text: in the 16 positions before the RL model's top-1 next token becomes ` Wait` (from the RLN-5
  map shards), ` Wait` is present in the RL readout more often than at matched positions of the same answer. Refuted if the
  rates are equal within the interval.

The token ranking over the whole vocabulary (which tokens differ most) is exploratory and is reported as such.

## Known limits

- Single-token readouts; multi-digit numbers are mostly invisible.
- The lens was fitted on the base and on WikiText; the fit excluded the first 16 positions of each prompt.
- The lens score correlates with token rarity; the paired design (same text, same position, same readout map) cancels what
  is common to both models.
- One sample per problem; the hand labels are one reader's.

## Runs

1. Smoke: 12 shortest answers per cell plus problems 20, 36, 46; all layers; read `checks.json`, choose the two stored layers.
2. Full: all answers, all layers aggregated, two layers stored.

Follow-ups, not in this spec: a lens fitted on the RL model as the matched control; the base without the cue on the same
continuations (what the cue adds to the workspace).

## Deviations and additions (2026-11-14, after the smoke run, before the full run was read)

- Stored layers: 20 and 24, chosen from the smoke run's hit@8 table. Layer 20 fails check 2 (see README), so it is
  exploratory.
- Two token families were fixed after reading the smoke run's token diff and before the full run was analyzed: hold-on
  (` Wait`, `Wait`, ` wait`, ` Hmm`, `Hmm`, ` hmm`) and wrap-up (`<|endoftext|>`, ` Answer`, `Answer`, ` So`, `.The`). A
  position counts once when any token of a family is present. H2 and H3 are tested on the hold-on family.
- Check 2's "J of a different layer" uses layer l + 8 where it exists. For l up to 22 that is a later layer's J, which
  turned out to read upcoming tokens better than the layer's own J; it is a finding about the lens on this text, and the
  control only tests failure for layers 24 to 30 (which use l - 8).
- Added, exploratory: `analysis/lensdiff_predict.py` (does a lens feature predict a wrong answer better than length).
