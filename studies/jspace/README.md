# jspace: what the RL model holds in its workspace that the base does not

Reads Anthropic's Jacobian lens (J-lens, arXiv 2607.15495) on the base `allenai/Olmo-3-1025-7B` and on
`allenai/Olmo-3.1-7B-RL-Zero-Math` over the stored MATH-500 answers of `studies/rlneurons` (T1: base with cue, T2: RL,
T 1.0). Goal: explain the 53-problem gap with per-problem examples, and find tokens for a no-reward intervention.
Spec: `specs/SPEC1_lensdiff.md`. Board: idea-8a0a28, work-50d329.

All code runs from the repository root with the root on `PYTHONPATH`.

## Layout

| Path | What it is |
|---|---|
| `specs/SPEC1_lensdiff.md` | The plan, the instrument checks, hypotheses H1 to H3 and what refutes each. Written before any GPU job. |
| `lib/jlens_read.py` | The fitted base lens (`neuronpedia/jacobian-lens`, pinned revision), block-output hooks, the readout, the word-like token mask, the hit@K count. |
| `jobs/lensdiff.py` | The GPU job: both models over the stored answers with teacher forcing; aggregates, per-position shards and `checks.json` in `$OUT_DIR`. Imports `build` and `load` from `studies/rlneurons/jobs/rln5_map.py`. |
| `analysis/lensdiff_analyze.py` | Readout of a run folder: token diff (a), presence with intervals (b, H1), by problem group (c, H2), lead before ` Wait` (d, H3), where in the answer (e); writes `metrics.json` and `examples.json`. Needs the RLN-5 map run folder (`--map`). |
| `analysis/lensdiff_predict.py` | Exploratory: AUROC of per-answer lens features for "this answer is wrong", against answer length; writes `predict.json`. |
| `analysis/lensdiff_page.py`, `analysis/page_template.html` | Build the reading page `results/lensdiff/full-01/workspace-diff.html` (charts and a token-by-token reader of six answers) from `metrics.json`, the shards and `page_examples.json`. |
| `specs/SPEC2_workspace.md` | SPEC 2: do the lens paper's workspace tests pass on the RL model and on the base, and where do they differ; what `mhough/olmo3-jacobian-lenses` already published; hypotheses W1 to W6. No GPU run yet (2026-11-15). |
| `data/jlens_581d398/` | The six readout sets and `probe-swap.json` of `anthropics/jacobian-lens` at 581d398 (Apache-2.0, unchanged), with its LICENSE. |
| `prep/math_stimuli.py`, `data/math_stimuli_v1.json` | 240 arithmetic chains (120 with a swap) and 300 right/wrong twins, seed 20261114. |
| `jobs/fit_lens.py`, `jobs/fit_lens.sh` | Fit a J-lens for one model with the reference `jlens` code at a pinned commit (WikiText or math corpus). |
| `jobs/workspace_tests.py` | SPEC 2 job: readout sets, swap, twins on both models, each through its own head, with lens variants `pub`, `logit` and any `--lens-files`. |
| `analysis/workspace_analyze.py` | SPEC 2 readout: pass@k with null, swap flip rates with controls, twin gaps, all with bootstrap intervals. |
| `tools/finding_rl_wait_habit.py` (repository root) | The site page of the finding, `/finding/rl-wait-habit` on monitor.invariant.team, titled "More Wait, same score": the cued base pushed to the RL model's written rate of Wait / Hmm (SPEC 3, `steer/main-01` on branch `claude/wait-steering-f535b2`, commit `d3a8a58`) solves 413 of 500 against 410.5 without a push (+0.5 [-2.2, +3.0] points) and 409 with a random push of the same norm; the RL model 457. Switch: no push / push toward Wait / random push, over a strip of written rate and a strip of right answers, and the 40 blindly labelled passages of `steer/main-01/reading/` (16 of 20 pushed Waits filler, 7 of 20 own Waits fix a step). The lens difference of SPEC 1 (`lensdiff/matched-01`, 4.63 % against 6.29 %) is named in its panels. `python3 tools/finding_rl_wait_habit.py` checks every number against these artifacts. |
| `results/lensdiff/full-01/` | The full run: `run.json`, `checks.json` (the job's instrument checks), `metrics.json`, `examples.json` (138 answers, 5 positions each, with both readouts), `predict.json`, `reader_notes.md` (one reader's labels of 114 of those positions), `page_examples.json` and `workspace-diff.html` (the reading page). |

## Run it

```
uv run tools/gpu.py submit h100 --hours 1 -- "python -m studies.jspace.jobs.lensdiff --commit $(git rev-parse HEAD) --store-layers 20,24"
uv run tools/gpu.py get <job-id>
```

Smoke run: add `--n 12 --pick 20,36,46 --check-every 1`. Laptop dry run with small random models (no weights): add
`--dry-run --n 3 --inputs <folder with T1.jsonl and T2.jsonl> --out <new folder>`.

Inputs are in the Volume `iterate-runs` under `inputs/rln5/` (sha256 in `studies/rlneurons/data/rln5/map_inputs.json`).
Per-position shards stay in the Volume and in `runs/<job-id>/` (not committed).

Analysis (numpy only; the map run folder is job `sameraslan-1114-135831-c3ec` of `studies/rlneurons`):

```
PYTHONPATH=. python3 -m studies.jspace.analysis.lensdiff_analyze runs/<job-id> --map <map run folder> --out studies/jspace/results/lensdiff/full-02
PYTHONPATH=. python3 -m studies.jspace.analysis.lensdiff_predict runs/<job-id> studies/jspace/results/lensdiff/full-02
```

## Numbers (run `full-01`)

Job `sameraslan-1114-151743-3674` (H100, 1,377 s, commit `3af965d`): both models over the 1,000 stored answers, 4,314,803
positions after the prompt, the fixed readout at layers 10 to 30, layers 20 and 24 stored per position. Smoke job
`sameraslan-1114-151456-0389`. All numbers are keys of `results/lensdiff/full-01/metrics.json` unless a file is named.
Presence = the token is among the top 8 word-like tokens of the readout; rates are shares of generated positions; intervals
are 95 % bootstrap intervals over the 500 problems. T1 = the base's own answers, T2 = the RL model's answers.

Result: on identical text the RL model's layer-24 readout holds hold-on words (` Wait`, ` Hmm` and their variants) at 5.64 %
of positions against 4.56 % for the base (T1, +1.08 points [1.01, 1.15]), and wrap-up words (`<|endoftext|>`, ` Answer`,
` So`, `.The`) at 2.82 % against 4.22 % (-1.40 [-1.50, -1.31]). The shift is general: it is not larger on the problems the
base fails (H2 refuted). The readout leads the text (H3 holds). No lens feature predicts a wrong answer better than the
answer's length.

| | Number | Key |
|---|---|---|
| Check 1, plumbing | max difference 0.0 for both models | `checks.plumbing` |
| Check 2, hit@8, base on T1 (J-lens / logit lens / other layer's J / shifted window) | L16 0.181 / 0.126 / 0.300 / 0.095; L20 0.346 / 0.361 / 0.559 / 0.148; L24 0.536 / 0.490 / 0.457 / 0.239; L28 0.622 / 0.570 / 0.526 / 0.314 | `checks.hit.by_layer` |
| Check 2, verdict | By the spec's rule the lens works at layers 24, 26, 28 (and at 10 to 14, where it is at the shifted-window level, 0.35 against 0.32). At 16 to 22 the J of layer l + 8 reads upcoming tokens better than the layer's own J, so layer 20 numbers are exploratory. | same |
| Check 3, transfer | hit@8 at L24: RL on T2 0.539, base on T1 0.536 | same |
| Check 4, demo prompt | base L20, position of ` boot`: ` Italy` is in the J-lens top 10, absent from the logit-lens top 10 | `checks.json` `demo` |
| H1, hold-on family, L24 | T1: base 4.56 %, RL 5.64 %, +1.08 [1.01, 1.15]. T2: 5.52 %, 6.12 %, +0.60 [0.56, 0.65] | `b_presence.*.hold_on` |
| H1, single tokens, T1 L24 | ` Wait` 3.43 -> 4.17 (+0.75 [0.70, 0.80]); ` Hmm` 1.17 -> 1.83 (+0.66 [0.61, 0.72]); ` wait` 2.84 -> 3.47; ` check` 0.39 -> 0.37; ` verify` 0.24 -> 0.21; ` But` 1.04 -> 0.88. Neutral: ` the` -0.10, ` so` -0.02, ` Therefore` +0.04, ` equation` -0.11 | `b_presence.T1_L24.tokens` |
| H1, verdict | Holds for the ` Wait` / ` Hmm` tokens, 5 to 7 times the neutral shifts. Does not hold for ` check`, ` verify`, ` But`, ` double`. | |
| Wrap-up family | T1 L24: 4.22 % -> 2.82 %. T1 L20: 10.54 % -> 8.02 % (-2.52 [-2.69, -2.35]). `<|endoftext|>` alone, T1 L24: 1.97 % -> 1.20 % | `b_presence.*.wrap_up`, `a_vocab_diff` |
| Token diff, T1 L24, RL more (exploratory) | ` Wait`, ` perhaps`, ` maybe`, ` which`, ` Hmm`, ` wait`, ` somehow`, `Wait`, ` hmm`, ` something`, ` actually`, ` indeed`, ` yes`, ` probably` | `a_vocab_diff.T1_L24.rl_more` |
| Token diff, T1 L24, base more | `<|endoftext|>`, digits `2 1 4 3 0 5 6`, ` if`, ` So`, `.The`, ` If`, ` and` | `a_vocab_diff.T1_L24.base_more` |
| Token diff, T1 L16, RL more | ` somehow`, ` hopefully`, ` perhaps`, ` indeed`, ` unfortunately`, ` presumably`, ` certainly`, ` actually`, ` maybe`, ` probably` | `a_vocab_diff.T1_L16.rl_more` |
| H2, hold-on difference by group, T1 L24 | both +1.31 [1.21, 1.41] (398); rl_only +0.93 [0.83, 1.06] (65); rl_only minus both -0.37 [-0.52, -0.22]. Refuted: the sign is the opposite. | `c_by_group.T1_L24_hold_on` |
| H3, lead, T1 L24 | 6,020 positions where RL's top-1 next token becomes ` Wait` after 32 positions without it. Hold-on presence in the RL readout 2 to 8 positions before: 9.4 %; 9 to 16 before: 7.8 %; 17 to 32 before: 6.3 %; far from any such position: 4.36 %. Base readout: 6.9 %, 5.9 %, far 3.40 %. | `d_lead.T1_L24` |
| Held against written | ` Wait` is the written token at 0.26 % of T1 positions and RL's top-1 next token at 0.43 %; it is in the RL readout at 4.17 % | `d_lead.T1_wait_rates`, `b_presence` |
| Where, T1 L24 | Hold-on presence after ` Let`: base 11.3 %, RL 25.6 %. At the 4 % of positions with the largest KL(base, RL): 17.0 % and 19.5 %; elsewhere 4.04 % and 5.06 %. By tenth of the answer it falls from 5.5 % / 7.1 % (third tenth) to 1.8 % / 2.1 % (last tenth). | `e_where.T1_L24` |
| Wrong-answer prediction (exploratory) | AUROC for "the base's answer is wrong": length 0.831; best lens feature (share of positions with a wrap-up token in the base readout, L24) 0.241, that is 0.759 when reversed. RL answers: length 0.962, best lens feature 0.154 (0.846 reversed). | `predict.json` |

Reader's check of the examples (`results/lensdiff/full-01/reader_notes.md`, one reader, a subagent): the top 3 positions by
readout log-prob gap in 30 answers of the group rl_only (slips, misreads, changed answers), 90 positions: 10 at the first wrong
step or its first use, 26 where a wrong value is reused or a separate local slip occurs, 20 at the wrong final answer, 21 at a
correct step, 13 unclear. In 8 answers of the group both, 10 of 24 positions sit at the final answer. The positions mark
generic boundaries more than errors. In 23 of the 90 the RL top-8 is word fragments while the base top-8 is one repeated copy
token, so the log-prob gap is a noisy way to pick positions; presence in the top 8 is the measure used for all numbers above.

Limits. The lens was fitted on the base and on WikiText, and passes its check only at layers 24 to 28, where its top-1
token equals the model's next token at 52 to 73 % of positions; part of the L24 difference is therefore the difference of the
two next-token distributions. The lead (H3) and the layer-16 token diff are the evidence that it is more than that. No lens
fitted on the RL model was used. One sample per problem.

Saved examples: `results/lensdiff/full-01/examples.json`, for each of 138 answers the 5 positions where the RL readout's
hold-on log-prob exceeds the base's the most, with the text before and after and both top-8 lists.

### Run `lensdiff/matched-01`: SPEC 1 again with a lens fitted per model

Job `sameraslan-1114-193314-20a2` (H100, commit `abfcfc1`): the same 4,314,803 positions, each model read through its own fitted
lens (the fits of `workspace/own-01`), its own final norm and its own `lm_head`. Numbers are keys of
`results/lensdiff/matched-01/metrics.json`; `examples.json` of this run is not committed.

The result of `full-01` holds and the hold-on difference is larger:

| T1, layer 24 | `full-01` (one lens and head for both) | `matched-01` (own lens and head) | Key |
|---|---|---|---|
| Hold-on family, base -> RL | 4.56 % -> 5.64 % (+1.08 [1.01, 1.15]) | 4.63 % -> 6.29 % (+1.66 [1.57, 1.76]) | `b_presence.T1_L24.hold_on` |
| Wrap-up family, base -> RL | 4.22 % -> 2.82 % (-1.40 [-1.50, -1.31]) | 4.20 % -> 2.85 % (-1.35 [-1.44, -1.26]) | `b_presence.T1_L24.wrap_up` |
| ` Wait` alone | 3.43 % -> 4.17 % | 3.49 % -> 4.86 % | `b_presence.T1_L24.tokens` |
| Neutral ` the`, ` so` | -0.10, -0.02 | +0.06, +0.12 | same |
| H2: rl_only minus both | -0.37 [-0.52, -0.22] | -0.37 [-0.59, -0.13] | `c_by_group.T1_L24_hold_on` |
| H3: hold-on 2 to 8 positions before RL's ` Wait`, against far from it | 9.4 % against 4.36 % | 10.7 % against 4.99 % | `d_lead.T1_L24` |

So the difference does not come from reading the RL model through the base model's lens and head. The wrap-up tokens lie on the
token-frequency direction that a last-block lens amplifies (SPEC 2, controls); the matched lenses share that property, so this
run does not test that artifact. The logit-lens top-8 was not stored.

## Numbers, SPEC 2: workspace tests on both models (run `workspace/pub-01`)

Job `sameraslan-1114-184704-836d` (H100, 368 s, commit `3208566`): `jobs/workspace_tests.py` on both models, each through its own
final norm and `lm_head`, layers 12 to 30 in steps of 3, lens variants `pub` (published Neuronpedia base lens), `mh` (the mhough
pair, base and RL-Zero-Math 3.0) and `logit`. All numbers are keys of `results/workspace/pub-01/metrics.json`; intervals are 95 %
bootstrap intervals over items. The fitted per-model lenses (`own`) are not in this run.

Result: the workspace tests pass in both models, and the two models are the same on every one of them. The only difference
found is in how the hold-on words respond to a wrong result, and it is small: in the output, +0.35 nats for RL against +0.28
for the base.

| | Base | RL | Key |
|---|---|---|---|
| Multihop, intermediate in the readout top 10 (`pub`), items the model answers | 0.929 (n 21) | 0.950 (n 20) | `readout.multihop.pub.*.pass10` |
| the same minus the null (another item's intermediate) | +0.746 [0.556, 0.897] | +0.758 [0.567, 0.925] | `...pass10_minus_null` |
| the same with the logit lens | 0.905 | 0.900 | `readout.multihop.logit` |
| Typo, correct spelling in the top 10: `pub` / `logit` (n 96) | 0.615 / 0.438 | 0.615 / 0.438 | `readout.typo` |
| Multilingual (`pub`, n 36 and 35) | 0.493 | 0.481 | `readout.multilingual` |
| Order-ops, the partial result (`pub` / `logit`, n 29); null 0.59 to 0.69 | 0.897 / 0.966 | 0.931 / 0.966 | `readout.order-ops` |
| Arithmetic chains, partial results (`pub` / `logit`, n 141 and 139); null 0.16 to 0.18 | 0.404 / 0.670 | 0.392 / 0.655 | `readout.chains` |
| RL minus base on items both answer, `pub` and `logit`, every set | within [-0.04, +0.10] of 0; multihop, association, poetry exactly 0 | | `*.rl_minus_base_pass10_shared` |
| the same with the `mh` lens pair (RL lens fitted on the 3.0 model) | chains -0.054 [-0.098, -0.014]; all other sets include 0 | | same |
| Two-hop swap, eligible items | 44 of 90 | 44 of 90 | `swap.probe-swap.*.eligible` |
| Swap flips with lens vectors (best strength 1 to 2) | 0.364 [0.227, 0.500] | 0.364 [0.227, 0.500] | `swap.probe-swap.*.pub.flip` |
| Swap flips, null replacement / logit-lens vectors | 0.068 / 0.182 | 0.023 / 0.182 | `...null_flip`, `...logit.flip` |
| Chain swap of the partial result (n 116 and 115): lens / null | 0.043 / 0.017 | 0.035 / 0.009 | `swap.chains` |
| Twins, output: hold-on log-prob after a wrong result minus after the right one (n 300) | +0.279 [0.255, 0.305] | +0.346 [0.318, 0.374] | `twins.output_hold` |
| the same, RL minus base | +0.066 [0.061, 0.072]; neutral words -0.010 [-0.014, -0.006] | | `twins.output_hold.rl_minus_base` |
| Twins, readout at L24 (`pub`): the same gap | +0.133 [0.103, 0.165] | +0.160 [0.125, 0.198] | `twins.lens.pub.L24.hold_lp` |
| the same, RL minus base | +0.027 [0.018, 0.035]; neutral words -0.001 [-0.007, 0.004] | | same |
| Twins: log-prob each model gives the right result before it is written | -0.008 | -0.004 | `twins.output_right_logprob_before_result` |
| Twins: top next token after the wrong line | `So` 194, `Now` 99 | `So` 195, `Now` 103 | `twins.output_top_after_error` |
| Twins: right result in the readout top 10 while reading the wrong one (L24) | 0.000 | 0.000 | `twins.lens.pub.L24.right_in_top10_at_wrong_number` |

Verdicts against SPEC 2 (with `pub`; `own` still to run):
- W1 holds for both models on multihop, typo and multilingual (lens minus null far above 0). On multihop the logit lens does as
  well as the J-lens (0.90 against 0.93) when the minimum is taken over layers 12 to 30; the J-lens reads the intermediate
  earlier (layer 18: 0.38 to 0.45 against 0.14).
- W2 holds for both: 36 % flips against 2 to 7 % for the null and 18 % for logit-lens vectors, 16 of 44 items in each model.
- W3 holds: no standard set differs between the models.
- W4 is refuted: RL does not hold arithmetic partial results more readably (chains -0.007 [-0.040, 0.025] with `pub`; -0.054
  [-0.098, -0.014] with `mh`, whose RL lens belongs to another checkpoint). On chains and
  order-ops the logit lens reads the partial result better than the J-lens, and the order-ops null is high (0.6), so numbers
  are a weak test of this lens. The chain swap fails in both models (4 %).
- W5 holds in sign and is small: RL's hold-on response to a wrong result is 24 % larger in the output (0.346 against 0.279
  nats) and 20 % larger in the L24 readout. Both models know the right result (probability above 0.99) and both continue
  with `So` or `Now` after the wrong line.
- W6 is refuted: the right result is never in the readout top 10 while the wrong one is read.

Only 20 to 21 of the 93 multihop items are answered correctly (most prompts end in a space token, which forces the answer to
come without its leading space); the no-trailing-space variant has 15 correct of 83 and gives the same picture (0.47 for both).

### Run `workspace/own-01`: the same tests with a lens fitted per model

Lens fits: jobs `sameraslan-1114-185927-7df1` (base) and `sameraslan-1114-185933-d625` (RL), `jobs/fit_lens.sh`, 100 WikiText
prompts of 128 tokens (the same list), layers 10 to 30, 1,896 s and 1,905 s on one H100 each (19 s per prompt); the lens files
stay in the Volume. Tests: job `sameraslan-1114-193308-0545` (385 s, commit `abfcfc1`), variants `pub`, `logit`, `own`. Numbers
are keys of `results/workspace/own-01/metrics.json`.

Every verdict of `pub-01` holds with `own`:

| | Base | RL | Key |
|---|---|---|---|
| Multihop pass@10 (`own`) | 0.929 (n 21) | 0.950 (n 20) | `readout.multihop.own` |
| Typo pass@10 (`own`, n 96) | 0.510 | 0.479; RL minus base -0.031 [-0.073, 0.010] | `readout.typo.own` |
| Chains pass@10 (`own`) | 0.450 | 0.424; RL minus base on shared items -0.022 [-0.058, 0.011] | `readout.chains.own` |
| Two-hop swap flips (`own`, 44 eligible, strength 1) | 0.364 [0.227, 0.500] | 0.364 [0.227, 0.500] | `swap.probe-swap.*.own.flip` |
| the same, null replacement | 0.045 | 0.023 | `...null_flip` |
| Twins, readout at L24 (`own`): hold-on gap, error minus correct | +0.128 [0.097, 0.158] | +0.154 [0.118, 0.191] | `twins.lens.own.L24.hold_lp` |
| the same, RL minus base | +0.027 [0.018, 0.035]; neutral words -0.005 [-0.010, 0.001] | | same |

The 100-prompt fit reads typos less well than the published 568-prompt lens (0.51 against 0.62 on the base); the two models
stay equal under either.


## SPEC 3: steering the cued base along the hold-on lens direction during generation

Spec `specs/SPEC3_steer.md`; code `lib/steer.py` (directions, arm names), `jobs/steer_gen.py` (the GPU job: run_cell's vLLM engine
built in-process with a forward hook on one block), `analysis/steer_analyze.py` (readout), `jobs/steer_readout.py` (the layer-24 readout
under each vector, teacher forcing), `analysis/steer_reading.py` (blind excerpts of inserted hold-on words for a reader). Board:
idea-da9dca, work-74703c.

```
uv run tools/gpu.py submit h100 --hours 1 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.jspace.jobs.steer_gen --arms none,steer:hold:L24:0.068 --commit $(git rev-parse HEAD)"
PYTHONPATH=. python3 -m studies.jspace.analysis.steer_analyze --runs runs/<job-id> [...] --out studies/jspace/results/steer/<run>
```

### Run `steer/dose-01`: which strength gives the RL model's written Wait rate

Job `sameraslan-1114-203946-8e12` (H100, 11 minutes, commit `313a104`; smoke `sameraslan-1114-203816-b34d`): the 63 MATH-500 problems
whose index is a multiple of 8, cap 1,024 tokens, 17 arms. Numbers are keys of `results/steer/dose-01/metrics.json` (`arms.<arm>`).
The instrument checks passed (`checks.json`): alpha 8 makes every generated token ` wait`, a bias of +20 nats every token ` Wait`.

| Arm | Hold-on words per 1,000 tokens | Ratio to `none` | Finished within 1,024 tokens and right, of 63 |
|---|---|---|---|
| `none` | 6.53 | 1.00 | 21 |
| layer 24, alpha 0.03 / 0.06 / 0.12 / 0.25 / 0.5 | 7.37 / 8.09 / 15.9 / 92.5 / 840 | 1.13 / 1.24 / 2.44 / 14.2 / 129 | 19 / 16 / 12 / 1 / 0 |
| layer 20, alpha 0.06 / 0.12 / 0.25 / 0.5 | 7.19 / 8.52 / 20.8 / 133 | 1.10 / 1.31 / 3.19 / 20.3 | 16 / 15 / 2 / 0 |
| logit bias on the hold-on tokens, 0.5 / 1 / 2 nats | 8.77 / 10.0 / 26.7 | 1.34 / 1.54 / 4.09 | 17 / 15 / 13 |
| random direction, layer 24, alpha 0.12 / 0.5 | 6.47 / 6.26 | 0.99 / 0.96 | 20 / 10 |
| hold minus wrap, layer 24, alpha 0.12 / 0.25 | 14.6 / 127 | 2.24 / 19.4 | 13 / 2 |

S4 holds: the written hold-on rate rises with strength at both sites, and a random direction of the same norm leaves it
unchanged. The rise is steep: doubling alpha from 0.12 to 0.25 at layer 24 turns the answer into repeated "wait". The strengths
that give 1.41 times the rate of `none` (the RL model's ratio), by the spec's rule (`dose.*.strength_at_target`): alpha 0.068 at
layer 24, alpha 0.128 at layer 20, a bias of 0.64 nats. The last column is not an accuracy: 42 of 63 answers of `none` are cut
by the 1,024-token cap.

### Run `steer/main-01`: the score with the push at the RL model's written Wait rate

One job per arm on one H100 each (31 to 36 minutes), commit `1534ce9` for the steering arms, `7f269e9` for `none` and `2d6f378` for the bias arm: all 500 MATH-500 problems, cue, T 1.0, top-p 1.0, cap 16,384, grader v3, seed 41,000,000 + index in every arm. Jobs: `none`
`sameraslan-1114-214944-eb61`, `none` with a second seed `sameraslan-1114-223704-bee0` (commit `1cc3ac8`), `bias:hold:0.64`
`sameraslan-1114-214251-10c3`, `steer:hold:L24:0.068` `sameraslan-1114-205156-86f8`, `steer:hold:L20:0.128` `sameraslan-1114-205203-840e`,
`steer:rand:L24:0.068` `sameraslan-1114-205210-8d88`, `steer:hold:L24:0.1` `sameraslan-1114-205216-17de`. Numbers are keys of
`results/steer/main-01/metrics.json` (`arms.<arm>`, `pairs`); intervals are 95 % bootstrap intervals over the 500 problems. Raw rows:
Volume `iterate-runs`, `/runs/<job id>/answers.jsonl`.

Result: pushing the base model along the lens direction of Wait / Hmm until it writes them as often as the RL model does not
raise its score, and a stronger push lowers it. S1 is refuted.

| Arm | Right of 500 | Minus `none`, points | Minus four stored unsteered samples (mean 410.5), points | Hold-on words per 1,000 tokens | Tokens, mean / median | Cap hits | Ends without an answer |
|---|---|---|---|---|---|---|---|
| `none` | 430 |  | +3.9 [+1.2, +6.6] | 6.28 | 3,911 / 1,938 | 21 | 5 |
| `none`, second seed (41,010,000 + index) | 411 | -3.8 [-7.2, -0.2] | +0.1 [-2.6, +2.9] | 6.34 | 4,040 / 1,915 | 23 | 5 |
| `steer:rand:L24:0.068`, random direction | 409 | -4.2 [-7.8, -0.6] | -0.3 [-3.1, +2.5] | 6.05 | 4,029 / 1,969 | 23 | 3 |
| `steer:hold:L24:0.068`, the RL model's written rate | 413 | -3.4 [-6.6, +0.0] | +0.5 [-2.2, +3.0] | 8.32 | 4,158 / 2,140 | 22 | 13 |
| `steer:hold:L24:0.1`, stronger | 381 | -9.8 [-13.6, -6.2] | -5.9 [-8.8, -2.8] | 11.21 | 4,491 / 2,647 | 22 | 39 |
| `steer:hold:L20:0.128`, layer 20 | 398 | -6.4 [-10.0, -2.6] | -2.5 [-5.7, +0.7] | 9.09 | 4,619 / 2,368 | 31 | 27 |
| `bias:hold:0.64`, logit bias | 421 | -1.8 [-5.2, +1.6] | +2.1 [-0.7, +4.7] | 9.72 | 4,471 / 2,174 | 28 | 4 |

Reference: the RL model with the same cue scores 457 (`rlneurons` `day1_wdiff/rl_cue-01`) and writes 8.81 hold-on words per 1,000
tokens (stored T2).

Verdicts against the spec:
- S0, the instrument, holds on the second seed. `none` scores 430 with the seeds of every other arm, above the range 404 to 418,
  and 411 with a second seed. The 430 repeats with its seeds (the `none` arm of a job stopped for time, `sameraslan-1114-205149-0570`:
  426, with 436 of 500 texts identical) and 48 of its texts are identical to stored T1, which has the same seeds, so the sampling
  path is that of the stored cells. The two seeds differ by 3.8 points [+0.2, +7.6], the size of the difference between `none` and
  the random direction, so 430 is a high draw and one arm's score moves by several points between draws. The unsteered mean of
  this engine is 420.5 (stored cells 410.5). Every arm is shown against `none` and against the stored samples.
- S1 is refuted. `steer:hold:L24:0.068` writes 8.32 hold-on words per 1,000 tokens (1.33 times `none`; the RL model 8.81) and
  scores 413: -3.4 [-6.6, +0.0] points against `none`, +0.4 [-3.2, +3.8] against the second seed of `none`, +0.5 [-2.2, +3.0] against the stored unsteered samples, +0.8 [-2.6, +4.2] against the random direction of the same norm. Against the stored samples the interval excludes a gain of more than 3.0 points; the gap to the RL model is 9.3.
- S2 is refuted: the logit bias does not do worse than the push. `steer:hold:L24:0.068` minus `bias:hold:0.64`: -1.6 [-5.0, +1.8] points
  (`pairs`). The bias reached a higher written rate (9.72, 1.55 times `none`) than the dose run predicted.
- S3: the random direction leaves the written rate unchanged (6.05, 0.96 times `none`). Its score is 409: -4.2 [-7.8, -0.6] points against `none`, -0.3 [-3.1, +2.5] against the stored samples. Against the second seed of `none` it is -0.4 [-4.0, +3.0]. S3 holds: the difference against the first `none` is the high draw of that run (S0).
- Dose: at layer 24, alpha 0.068 -> 0.1 takes the written rate from 8.32 to 11.21, the median answer from 2,140 to 2,647 tokens,
  the answers that end without stating an answer from 13 to 39 (`none` 5, random direction 3), and the score from 413 to 381.
  Cap hits stay at 22. The same written rate reached from layer 20 costs more (398, 27 answers without an answer, 31 cap hits).

Why it does not help (evidence, each in `metrics.json` unless a file is named):
- The push adds the word without a check. Every arm shares its sampling noise with `none`, so an answer equals the `none` answer up
  to the first token the arm changed. With the push that first change comes after a median of 229 characters and is a hold-on
  word in 87 of 500 answers; with the logit bias after 756 characters and in 262 of 465; with the random direction in 9 of 494
  (`arms.*.first_divergence`). One blind reader (a subagent, `results/steer/main-01/reading/`, 20 excerpts per kind, the key
  hidden) labelled what such an inserted word does: of 20 inserted by the push 16 are filler or the next step phrased with
  "Wait", 3 confirm an earlier step, 1 corrects a mistake; of 20 inserted by the bias 9, 8 and 1 (2 unfounded doubts); of 20
  hold-on words the unsteered model wrote by itself 3, 7 and 7. The kinds differ in where they sit in the answer (median
  offset 252, 1,011 and 6,202 characters), so this is a description and no matched comparison.
- No selective gain where the RL model gains. On the 65 problems that stored T1 got wrong and stored T2 got right, the arms
  score: `none` 42 and 37 (second seed), random direction 35, push 35, bias 38, stronger push 31 (`arms.*.right_by_group.rl_only`). A fresh sample of
  the unsteered model recovers these problems as well as any push.
- The loss at higher strength is derailment rather than too much checking: the answers lost end without an answer or in unrelated
  words (39 of 500 at alpha 0.1), and the mean log-probability of the sampled tokens falls from -0.40 (`none`, random) to -0.47
  (alpha 0.068) and -0.73 (alpha 0.1) (`arms.*.mean_token_logprob`).
- Inside the model the push overshoots (run `steer/readout-01` below): the strength that matches the RL model's written rate
  puts a hold-on word in the layer-24 readout at 31 % of positions, against 4.75 % without a push and 6.29 % in the RL model.
  A push of a quarter of that strength (alpha 0.017) already gives 7.2 %. So the readout difference of SPEC 1 is small compared
  with what a constant lens vector must do to change the text: the readout is a trace of the RL model's habit rather than a handle
  that produces it.
- It agrees with result-855858 (checking markers do not separate right from wrong samples) and with result-96e819 (a
  self-review pass fixes nothing); a teammate predicted 0 points [-2, +1] before the run.

Limits. One sample per problem and arm: one arm's score has a standard deviation of about 7 problems (the two seeds of `none` differ by 19
problems). The push is a constant vector at every position; a push applied only at chosen positions was
not tested. Strengths were matched on the written rate, which the bias arm overshot. One reader for the excerpts. The push
at the strength that matches the RL model's readout (alpha about 0.011) was not scored.

Saved examples: `results/steer/main-01/examples.json`, per arm the shortest answer scored right and the shortest finished answer
scored wrong, with gold, extracted answer and score.

### Run `steer/readout-01`: what the push does to the layer-24 readout

Job `sameraslan-1114-214804-e127` (H100, 52 s, commit `7f269e9`; smoke `sameraslan-1114-214652-7b06`): `jobs/steer_readout.py`, the base
model over 43 of its stored T1 answers (index a multiple of 8, at most 6,000 tokens; 78,843 generated positions) with teacher
forcing and each vector switched on; the readout through the lens fitted on the base model (`workspace/own-01`), not the
published lens the vectors come from. Keys of `results/steer/readout-01/readout.json` (`arms.<arm>`).

| Arm | Hold-on token in the top 8 of the layer-24 readout | Top output token is a hold-on token | KL(unsteered, steered) per position |
|---|---|---|---|
| `none` | 4.75 % [4.25, 5.22] (SPEC 1, all 500 answers: 4.63 %; RL model 6.29 %) | 0.585 % | 0 |
| layer 24, alpha 0.017 | 7.20 % | 0.602 % | 0.0001 |
| layer 24, alpha 0.034 | 11.9 % | 0.616 % | 0.0003 |
| layer 24, alpha 0.068 (main run) | 31.0 % [28.8, 33.0] | 0.686 % | 0.0013 |
| layer 24, alpha 0.1 | 51.4 % | 0.803 % | 0.0076 |
| layer 20, alpha 0.128 (main run) | 43.2 % | 0.680 % | 0.0077 |
| random direction, layer 24, alpha 0.068 | 4.61 % | 0.581 % | 0.0004 |
| layer 24, alpha 0.5 (must change the readout) | 100 % | 3.50 % | 0.176 |

The readout moves far more than the output: at alpha 0.068 the hold-on words are 6.5 times as often in the readout and 1.17
times as often the top output token, which matches the published observation that lens vectors write weakly (knowledge-16c252).

Page: `tools/finding_wait_push.py` (repository root), `/finding/wait-push` on the team site, unlisted (`UNLISTED = True`): a switch
No push / RL's Wait rate / Harder push over the written Wait rate and the problems solved, with the RL model's values as dashed lines.
