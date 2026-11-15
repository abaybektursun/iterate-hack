# SPEC 3: does giving the base model RL's hold-on habit raise its MATH-500 score (work-74703c, idea-da9dca)

Written 2026-11-14 (UTC 2026-11-15), before any GPU job of this spec.

## Question

SPEC 1 and 2 found one difference inside the two models: on identical text the RL model's layer-24 J-lens readout holds
` Wait` / ` Hmm` at 6.29 % of positions against 4.63 % for the base (matched lenses), and wrap-up tokens less often. In
their own answers the RL model writes 8.81 hold-on words per 1,000 tokens and the cued base 6.24 (stored T2 and T1,
`\b(wait|hmm+)\b`, n = 500 each): 1.41 times as many.

If that habit is what RL added, pushing the base model's middle layers along the lens direction of the hold-on words
during generation should move its score from 410 of 500 toward the RL model's 457 to 463 (cue, T 1.0, grader v3).

## Prior work (read by a subagent, sections in full unless noted)

- 2610.24663 (Qwen3-4B-Base, AIME, Table 5): forcing "Wait" by rule lowers pass@1 from 10.0 % to 4.5 %; a logit bias of
  +2 / +4 gives 8.5 %. No activation steering.
- 2507.12638 (Ward et al.): a backtracking vector at layer 10 of 32 induces "Wait" in the R1 distill and never in its base
  model; later-layer vectors that decode to "Wait" under the logit lens steer worse. No accuracy.
- 2512.13979 (ReflCtrl, Table 3): a reflection direction on reasoning models, MATH-500: 85.98 -> 86.90 % and 93.06 -> 93.08 %;
  steering every token degrades above strength 0.3.
- 2510.07364 (Table 1): ten category vectors gated by the thinking model's SAE take a base from 63.9 to 75.7 % on MATH-500;
  no hold-on-only vector; norm-matched random vectors lose accuracy.
- Board: result-96e819 (an appended self-review pass fixes nothing in either model); knowledge-16c252 (lens steering is weak
  on open models).

No paper steers an untrained base toward "Wait" by activation and reports MATH accuracy. The nearest evidence predicts no
gain or a loss.

## Method (`jobs/steer_gen.py`, `lib/steer.py`)

Generation is that of `studies/rlneurons/jobs/run_cell.py`: prompt `pair1`, the three-token opening cue, T 1.0, top-p 1.0,
cap 16,384, stop id 100257, bf16, vLLM 0.32.0, the same row record and grader v3. The engine is built inside the job's
process with eager execution and no prefix cache, so that a forward hook on a block acts on every sequence (the three
differences from run_cell's engine; the arm `none` measures whether they change the score).

- Direction. For a token family F and layer l: the mean over t in F of unit((W_U[t] - mean over the vocabulary of W_U) J_l),
  scaled to unit length. J_l is the published base lens (`neuronpedia/jacobian-lens`, pinned in `lib/jlens_read.py`). `hold`:
  ` Wait`, `Wait`, ` wait`, ` Hmm`, `Hmm`, ` hmm`. `wrap`: `<|endoftext|>`, ` Answer`, ` So`, `.The`. `neutral`: ` the`, ` so`,
  ` Therefore`, ` and`, ` is`, ` of`. `rand`: a Gaussian direction, fixed seed.
- Steering arm `steer:<dir>:L<l>:<alpha>`: alpha * (median norm of the output of block l) * direction is added to the output of
  block l at every position of the prompt and the answer. Sites: layer 24 (where the finding was measured and the lens passes
  its instrument check) and layer 20 (earlier, so that more blocks can act on the change).
- Control `none`: the same hook adds a zero vector.
- Control `steer:rand`: the random direction at the same layer and norm.
- Control `bias:hold:<nats>`: the same preference at the output, a logit bias on the six hold-on tokens.
- The same seed per problem in every arm (seed 41,000,000 + index, the seed of T1), so arms share their sampling noise.

Instrument checks inside every job (`checks.json`; the job fails if one fails): `none` twice gives identical tokens; alpha 8
along `hold` changes the tokens of all but at most one of 8 problems at each steered layer (if it does not, the hook does not
reach generation); a bias of +20 nats makes the hold-on tokens more than half of the output.

## Runs and budget

1. Smoke: 8 problems, 128 tokens, four arms. About 0.1 H100-hours.
2. Dose run: the 32 problems whose index is a multiple of 16, cap 1,024 tokens. Arms: `none`; `hold` at layer 24 with alpha
   0.03, 0.06, 0.12, 0.25, 0.5; `hold` at layer 20 with alpha 0.06, 0.12, 0.25, 0.5; `rand` at layer 24 with 0.12 and 0.5;
   `holdwrap` at layer 24 with 0.12 and 0.25; `bias:hold` 0.5, 1, 2. Read out: hold-on words per 1,000 tokens, share of answers
   that end within the cap, loops. About 0.3 H100-hours. If no strength in the grid reaches the target, one more dose run with
   a shifted grid.
3. Strength rule, fixed here: alpha* (per site) and b* are the strengths at which the hold-on word rate is 1.41 times the rate
   of `none` in the dose run, by log-linear interpolation between the two neighbouring grid strengths. If steering loops or
   stops answering before it reaches 1.41, alpha* is the largest strength whose share of finished answers is within 10 points
   of `none`, and this is reported.
4. Main run: all 500 problems, cap 16,384, one sample. Arms: `none`, `steer:hold:L24:alpha*`, `steer:hold:L20:alpha*`,
   `steer:rand:L24:alpha*`, `bias:hold:b*`. About 0.5 H100-hours per arm (2.0 M tokens at 1,200 tokens per second, the rate
   of the stored cells): 2.5 H100-hours, as parallel jobs.
5. Reserve, at most 1.5 H100-hours: one follow-up chosen from the main run (a second strength, `holdwrap`, or a second sample).

Planned total: about 3 H100-hours, at most 4.5.

## Hypotheses and what refutes them

- S0, the instrument. `none` scores within 404 to 418 of 500, the range of the stored unsteered cells at this setting (T1 410;
  min-p and weight-difference controls 404 to 417). Outside it, comparisons with stored numbers are dropped and only the paired
  comparisons inside this run are used.
- S1, the habit raises the score. `steer:hold` at alpha* minus `none`, paired over the 500 problems: the 95 % bootstrap interval
  lies above 0. Refuted if it includes 0 or lies below it. Reported for both sites.
- S2, the workspace matters. `steer:hold` at alpha* minus `bias:hold` at b* (equal written hold-on rate): interval above 0.
  Refuted if it includes 0: then a decoding bias does the same.
- S3, the direction matters. `steer:rand` changes neither the hold-on rate (within 10 % of `none`) nor the score (interval of the
  difference includes 0). If `rand` moves them as much as `hold`, the effect of `hold` is not specific.
- S4, dose. In the dose run the hold-on word rate rises with alpha at each site. Refuted if it does not.

Prediction, stated before the run: S1 is refuted (difference within 3 points of 0) and cap hits rise with strength, because
the RL shift does not mark errors (SPEC 1, H2), a self-review pass fixes nothing (result-96e819) and forced "Wait" hurt a base
model (2610.24663).

## Readout (`analysis/steer_analyze.py`)

Per arm: right of n under grader v3 with a paired bootstrap interval against `none`, cap hits, rule-A loops, mean and median
generated tokens, hold-on words per 1,000 tokens, answers gained and lost against `none` by subject, the count of answers
identical to `none` and to the stored T1 row, and one saved answer scored right and one scored wrong.
