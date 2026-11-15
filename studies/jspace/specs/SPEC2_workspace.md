# SPEC 2: does a J-space workspace exist in the base and in the RL model, and where do they differ (work-dd8988)

Written 2026-11-14 (UTC 2026-11-15), before any GPU job of this spec.

## Question

1. Do the standard workspace tests of the lens paper (arXiv 2607.15495) pass on `allenai/Olmo-3.1-7B-RL-Zero-Math`?
2. Do they pass on the base `allenai/Olmo-3-1025-7B`, and where the two differ, why?
3. On arithmetic, where RL trained the model, is the difference larger than the +1.08 points of SPEC 1?

## What is already published (so it is not repeated here)

`mhough/olmo3-jacobian-lenses` (Hugging Face, read in full 2026-11-15): J-lenses for the base and ten post-trained Olmo 3 7B
models. Base against RL-Zero-Math: lens cosine 0.941, 2.9 % above the refit floor ("a light intervention"); MMLU equal; on 150
TriviaQA questions a covert-confidence readout has AUROC 0.66 for the base and 0.52 for RL-Zero-Math. Its workspace tests
(ignition, dual task, error monitoring, 5 to 10 items each) ran on the base only. Its RL-Zero-Math lens is the 3.0 model; no
lens exists for 3.1. Not in it: the lens paper's readout sets or swap on base against RL, any math text, any causal test.

## Stimuli

- `data/jlens_581d398/`: the six readout sets and `probe-swap.json` of `anthropics/jacobian-lens` at commit 581d398
  (Apache-2.0, copied unchanged). All are plain completions, so both models run them as written.
- `data/math_stimuli_v1.json` (`prep/math_stimuli.py`, seed 20261114): 240 arithmetic chains with one or two unstated partial
  results and two solved examples in front, 120 of them with a swap; 300 right/wrong twins (a short worked calculation whose
  last result is right or wrong by 1, 2 or 10). Every number is below 1,000, a single token in the Olmo tokenizer.

## Method (`jobs/workspace_tests.py`)

Each model is read through its own final norm and `lm_head`. Layers 12, 15, ..., 30. Lens variants: `pub` (the published
Neuronpedia base lens for both models), `own` (a lens fitted per model with `jobs/fit_lens.py`: 100 WikiText prompts, the
same list for both), `mh` (the mhough pair: base and RL-Zero-Math 3.0, as a lens-noise bar), `logit` (no Jacobian).

- Readout: rank of each intermediate at the readout position (final token; poetry: the last line break), tokens with no
  letter or digit masked, minimum over layers. pass@k = mean over items of the share of intermediates with rank <= k,
  k = 1 and 10. Null: the intermediates of another item of the same set. Order-ops and chains score the number only.
  Reported on the items each model answers correctly (greedy next token is a prefix of the target) and on the items both do.
- Swap (the J++ runner's rule): unit vectors `lm_head[t] J_l` of the intermediate and its replacement; at every layer and every
  position but the first, the two coordinates are exchanged and scaled by alpha in {0.5, 1, 2, 4}. Eligible: the clean answer
  is the top word-like token. Flip: the swap answer is the top word-like token. Controls: an unrelated replacement scored on
  the same swap answer (null), and logit-lens vectors.
- Twins: from the differing number to the end of the text, the readout log-probability of the hold-on family (` Wait`,
  `Wait`, ` wait`, ` Hmm`, `Hmm`, ` hmm`), of a neutral family (` the`, ` so`, ` Therefore`, ` and`, ` is`, ` of`), and the
  rank of the right result; the same hold-on log-probability from the model's own output.

## Hypotheses and what refutes them

- W1, a workspace readout exists in each model. For each model: lens pass@10 on multihop above the logit lens and above the
  null. Refuted for a model if its 95 % interval (bootstrap over items) for lens minus null includes 0.
- W2, it is causal in each model. Swap flip rate at the best alpha above the null arm and above logit-lens vectors.
  Refuted for a model if the lens flip rate is within the interval of either control.
- W3, the general workspace is unchanged by RL. On the six standard sets the RL minus base difference in pass@10 (items both
  answer) is within +-5 points. Refuted by a larger difference with an interval excluding 0. (Expected from the lens cosine
  0.941.)
- W4, RL holds arithmetic partial results more readably. Chains pass@10: RL above base on items both answer. Refuted if the
  interval of the difference includes 0.
- W5, RL's hold-on response is conditional on an error. Twins: (error minus correct) hold-on log-probability at layers 24 and
  27, last position; the RL gap is larger than the base gap. Refuted if the interval of the difference of gaps includes 0, or
  if the neutral family shows a gap of the same size. The same test on the output distribution is reported beside it: if
  only the output differs, the workspace adds nothing here.
- W6, the model holds the right value while reading the wrong one. Twins, error version: the right result is in the readout
  top 10 at the wrong number's position more often than a matched other number. Reported for both models; no directional
  claim.

A hypothesis counts as supported only if it holds with `own` and with `pub`; `logit` and `mh` are reported beside them.

## Controls taken from prior work

- Readout transfer: every claim uses each model's own lens and head (`own`), with the logit lens beside it.
- Final-block target: the published lenses target the last block, which amplifies a token-frequency direction (line break,
  end of text, "So"). The wrap-up result of SPEC 1 is therefore rechecked with `--lens-files` (matched lenses) and against the
  logit lens before it is used further.
- Lens noise: `mh` against `pub` on the base model gives the size of a difference that two fits of the same lens produce.

## Runs

1. Fit: `fit_lens.sh --model base` and `--model rl`, 100 prompts, layers 10 to 30 (smoke: `--n 2`).
2. `workspace_tests` smoke (`--limit 8`), then the full run with `pub`, `own`, `mh`, `logit`.
3. `lensdiff` rerun with matched lenses (SPEC 1 recheck).
