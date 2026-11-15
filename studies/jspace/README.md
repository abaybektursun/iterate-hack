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
