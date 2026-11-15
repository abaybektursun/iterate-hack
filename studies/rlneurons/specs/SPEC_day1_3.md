# Day-1 #3: restart and four-sample vote rows on both models (board idea-8b9cc7)

Written 2026-11-14, before any GPU run. Code: `jobs/run_cell.py` (`--samples`, `--restarts`), `analysis/day1_vote.py`,
`analysis/day1_vote_test.py`.

## Question

At AI2's setting (T 1.0 / top-p 1.0) the base with the opening cue scores 410 of 500 on MATH-500 and RL 463 (grader v3,
one sample). How many points do two procedures that use no reward add to each model, and at how many generated tokens per
problem: (a) restart an answer that hit the 16,384-token cap, (b) plurality vote over four samples? Both models get the same
procedure. The configuration is chosen on MATH-500 and then run unchanged on the 328 harder problems.

Known before the run (team memory): Maj@4 adds 0.8 points to a 73.6 % model on MATH-500 (arXiv 2507.18122, Table 1). Wang et
al. (2610.06851, App. E.2, Fig. 21) plot majority vote at k = 1..32 on MATH-500 for cued base and RL, figure only, at their
setting (T 0.6, cap 31,744, their grader); they report no restart-on-cap experiment and no vote on harder sets. Ours: restart
row at T 0.6, 414 of 500 against 354 single (README "Established numbers").

## Procedure (identical for both models)

One job per model and problem set: `run_cell --samples 4 --restarts 2`. One job is one run folder.

- Cells: base + cue and RL + plain prompt, T 1.0 / top-p 1.0, cap 16,384, MATH-500 (n = 500); then hard328 (n = 328).
- Seeds: attempt a of sample s of problem i uses `seed + 10000 * s + 1000 * a + i` (the RLN-3 rule `seed + 10000 x sample +
  index`, plus 1000 per restart; `run_cell` asserts index < 1000 and restarts < 10, so no two requests share a seed).
  `--seed`: 41000000 for base + cue on MATH-500 (T1's seeds) and 45000000 for RL on MATH-500 (T2's seeds), so sample 0,
  attempt 0 repeats T1 and T2; 3000000 on hard328 for both (Day-1 #1's seeds).
- Restart: when an attempt ends at the cap without the stop token and its attempt number is below 2, the same request is
  submitted again in the same job with the next attempt's seed. Every sample is restarted, not only sample 0. Each attempt is
  one row of `answers.jsonl` (fields `sample`, `attempt`).
- Restart row (SPEC4's rule): per problem, sample 0; the answer is the first attempt that did not hit the cap, else the last
  attempt. Its score is that attempt's `score_v3`. (The T 0.6 restart row in `grader/rln4_grader_v3.py` scored a final cap
  hit 0; here a final cap hit keeps its v3 score, as in every single-sample row. `restart_sample_0.final_cap_hits_right`
  in the readout is the count that differs.)
- Vote row: per problem, attempt 0 of samples 0-3 (no restarts). Each sample's answer is `extracted_v3`. A sample with no
  extracted answer casts no vote (a cap hit that did extract an answer votes). Samples are taken in sample order; a sample
  joins the first group whose first member agrees with it under `rln4_lib.agree` (both sides through `norm_v3`), else it
  starts a group. The largest group wins. Tie rule: among equally large groups, the group whose first member has the lowest
  sample number wins; so with four different answers the vote is sample 0's answer. The gold is not read. The vote's score is
  the `score_v3` of the winning group's first member. No group (no sample extracted an answer): scored wrong.
- pass@4: 1 when any attempt-0 sample is right. Upper bound of the vote row.
- Vote after restart (extra row, free): the same vote over each sample's restart-rule answer.
- Tokens per problem: every generated token (`n_new`) of every attempt the row uses, divided by n. Single: sample 0 attempt 0.
  Restart: all attempts of sample 0. Vote and pass@4: attempt 0 of the four samples. Vote after restart: every row of the job.
- Intervals: Wilson 95 % per row; paired bootstrap (5,000 resamples) for each row minus the single row, and with `--minus` for
  RL minus base per row.
- The readout refuses an unfinished run (missing sample, cap hit without its restart, `status` not `done`).

## Hypotheses and what refutes them

- H0 (instrument): sample 0, attempt 0 repeats T1 (410 right, 27 cap hits) and T2 (463, 6). Refuted, and nothing else is
  read, if the single row is outside 410 +- 20 (base) or 463 +- 15 (RL). Texts are not identical (other GPU, other batch).
- H1 (vote): the vote adds 2 to 6 points to base + cue and at most 2 to RL, so RL minus base is smaller under the vote than
  the single-sample 10.6. Refuted if the interval of base vote minus single includes 0, or if RL minus base under the vote is
  not below RL minus base single (same run, `--minus`).
- H2 (restart): at T 1.0 restarts add 1 to 3 points to base + cue (5 to 15 of its about 27 cap hits) and at most 1 to RL.
  Refuted if base restart minus single includes 0 or exceeds 4 points.
- H3 (cost): per added point the restart costs fewer generated tokens than the vote (restart about +10 % tokens, vote +300 %).
  Refuted if (vote minus single) / (vote tokens minus single tokens) exceeds the same ratio for the restart row.
- H4 (the remaining gap): no row of base + cue reaches the RL single row (463). Refuted if base vote, restart or vote after
  restart is at least 463, or its paired interval against RL single includes 0. Null to compare against: RL with the same
  procedure, and the mean of the four single samples (`each_sample.single_right`).

The MATH-500 result chooses one procedure (the base + cue row with the most right answers; if two are within 1 point, the one
with fewer tokens). That one is read on hard328; the hard328 job is the same command, so all rows exist there too.

## Commands

Laptop tests (no model):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote_test
uv run --no-project --with numpy --with math-verify==0.9.0 --with transformers==5.19.0 --with tokenizers==0.23.3 --with huggingface_hub --with jinja2 --with brotli python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --n 10 --samples 4 --restarts 2 --dry-run --out /tmp/d13/base --commit $(git rev-parse HEAD)
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run /tmp/d13/base --out /tmp/d13/o_base
```

The dry run must write 57 rows (40 first attempts, 13 first restarts, 4 second restarts) and the readout must print single 4,
restart 5, vote 7, pass_at_k 10, vote_after_restart 6 of 10 (the stand-in serves right, wrong, cap hit in turn). `--with
brotli`: on this laptop the tokenizer download failed without it (old system brotli against the current huggingface_hub).

GPU, MATH-500 first (one H100 job per model; run from a pushed commit that contains this branch):

```
uv run tools/gpu.py submit h100 --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --seed 41000000 --samples 4 --restarts 2 --commit $(git rev-parse HEAD)"
uv run tools/gpu.py submit h100 --hours 4 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set math500 --temperature 1.0 --top-p 1.0 --seed 45000000 --samples 4 --restarts 2 --commit $(git rev-parse HEAD)"
```

Then hard328 (same procedure; set `--hours` from Day-1 #1's mean generated tokens, see below):

```
uv run tools/gpu.py submit h100 --hours 6 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model base --prompt cue --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --samples 4 --restarts 2 --commit $(git rev-parse HEAD)"
uv run tools/gpu.py submit h100 --hours 6 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_cell --model rl --prompt plain --set hard328 --temperature 1.0 --top-p 1.0 --seed 3000000 --samples 4 --restarts 2 --commit $(git rev-parse HEAD)"
```

Readout (after `uv run tools/gpu.py get <job-id>`; base first, then RL minus base):

```
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/<base job> --out studies/rlneurons/results/day1_3/math500_base_cue-01
uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.day1_vote --run runs/<rl job> --out studies/rlneurons/results/day1_3/math500_rl-01 --minus studies/rlneurons/results/day1_3/math500_base_cue-01/readout.json
```

Each run folder gets `run.json`, `metrics.json`, `readout.json` (rows, per-problem 0/1 vectors) and `examples.json` (one vote
and one restart problem scored right and one scored wrong, with every attempt's seed, extracted answer, score and last 2,000
characters; the full texts are rows of `runs/<job>/answers.jsonl`, not committed).

## Tokens and time (estimates, not measured with this entry point)

- RL, MATH-500: T2 generated 2.35 M tokens for 500 answers (4,694 per problem, `results/rln4/modal_t2-01/metrics.json`). Four
  samples: 9.4 M, plus restarts of about 24 cap hits (at most 0.4 M each round): about 10 M tokens. At 1,415 tokens/s (T3, H100)
  about 2.0 h; at 1,803 (T2, H200) 1.5 h.
- Base + cue, MATH-500: T1's token total is not in the repository. Assumed about 2.3 M per sample (27 cap hits = 0.44 M, the
  rest near RL's length): 9.2 M, plus about 108 first restarts and their second restarts, at most 2.5 M: about 10 to 12 M
  tokens, 2.0 to 2.4 h at 1,415 tokens/s.
- hard328, either model: upper bound 328 x 4 x 16,384 = 21.5 M tokens for the first attempts (4.2 h at 1,415 tokens/s), up to
  three times that if every attempt hits the cap. Day-1 #1's `metrics.json` gives the real mean; set `--hours` from it.
- Add 3 min for setup and engine start. The engine keeps 128 sequences in flight, so four samples in one job take four
  times one sample; the two models run in parallel as two jobs.
- A job killed at `--hours` leaves an unfinished run that the readout refuses. Rerun with more hours; do not score it.

The GPU path of `run_cell` is still untested (README). Before the full jobs, run the base command with `--n 10 --hours 0.5`
and read its rows: sample and attempt fields, a restart row after each cap hit, seeds by the rule.

## Test record (laptop, 2026-11-14)

- `day1_vote_test`: all planted cases pass: four agree (4 votes); 2-2 tie (group of the lowest sample wins, in both orders);
  one sample without an answer (casts no vote); no answer in any sample (wrong); `\frac{1}{2}`, `0.5`, `\dfrac{2}{4}` are one
  answer; `\frac{1}{3}` and `\frac{1}{2}` stay apart; a wrong 3-1 majority scores 0. Restart merge on planted attempts (right
  at attempt 2; three cap hits; tokens summed). Five broken inputs raise (cap hit without restart, missing problem, missing
  sample, restart after a finished attempt, duplicate row).
- Mutations that must fail the test did: string equality in place of `agree`; samples voted in reverse order.
- Dry run, 10 MATH-500 problems, 4 samples, 2 restarts: 57 rows, 57 distinct seeds, all by the rule; readout as stated above
  (3 ties for first, pass@4 10 of 10). Same on 10 hard328 problems. A copy cut to 50 rows is refused ("cap hit without its
  restart"); `--minus` between a MATH-500 and a hard328 run is refused; an existing `--out` is refused.
- `run_cell` without the new options still prints 4 right, 3 cap hits of 10 with seeds `seed + index`.

## Results, MATH-500 (2026-11-15; T 1.0 / top-p 1.0, n = 500, grader v3, commit c36f562)

Run folders: `results/day1_3/math500_base_cue-01/` (job `abaybektursun-1114-153825-208b`) and `results/day1_3/math500_rl-01/`
(job `abaybektursun-1114-183640-e828`), each with `run.json`, `metrics.json`, `readout.json`, `examples.json`. Raw rows:
`runs/<job>/answers.jsonl` in the owner's Modal Volume (`uv run tools/gpu.py get <job>`), not committed.

| Row | Base + cue: right of 500 [Wilson 95 %] | tokens/problem | RL: right of 500 [Wilson 95 %] | tokens/problem | RL minus base, points [paired 95 %] |
|---|---|---|---|---|---|
| single (sample 0) | 405 [77.3, 84.2] | 3,808 | 456 [88.4, 93.4] | 4,675 | 10.2 [7.2, 13.2] |
| restart, up to 2 (sample 0) | 413 [79.0, 85.7] | 4,852 | 458 [88.8, 93.7] | 4,899 | 9.0 [6.0, 12.0] |
| vote over 4 | 446 [86.2, 91.6] | 16,034 | 474 [92.5, 96.4] | 18,747 | 5.6 [3.6, 7.8] |
| pass@4 (upper bound of the vote) | 467 [90.9, 95.3] | 16,034 | 482 [94.4, 97.7] | 18,747 | 3.0 [1.4, 4.8] |
| vote over 4 after restart | 450 [87.1, 92.3] | 19,697 | 475 [92.7, 96.6] | 19,864 | 5.0 [3.0, 7.0] |

Within a model, minus its single row (paired bootstrap): base restart +1.6 [0.6, 2.8], vote +8.2 [5.8, 10.8], vote after
restart +9.0 [6.4, 11.8]; RL restart +0.4 [0.0, 1.0], vote +3.6 [2.0, 5.2], vote after restart +3.8 [2.2, 5.6]. The four
single samples: base 405, 409, 410, 418; RL 456, 462, 464, 458. Across models at unequal tokens: base vote minus RL single
-2.0 [-4.0, 0.2] (16,034 against 4,675 tokens per problem); base vote after restart minus RL single -1.2 [-3.4, 1.0].

Jobs: base 2,137 rows (137 restarts), 9.85 M tokens, 1,213 tokens/s, 8,191 s wall; RL 2,041 rows (41 restarts), 9.93 M tokens,
1,360 tokens/s, 7,369 s wall; one H100 each. Smoke `abaybektursun-1114-152646-e76b` (10 problems): 45 rows, seeds by the rule,
5 restarts, single 8 of 10. The first RL job `abaybektursun-1114-153833-f4ab` died at 2,013 of 2,034 rows (runner
`FileExistsError` on `/runs/<job>`); it is not scored, the readout refuses it. Its 2,000 first attempts gave vote 469 against
474 in the rerun with the same seeds, so about 1 point of the vote row is run-to-run variation (vLLM is not batch-invariant).

Hypotheses:

- H0 held: base 405 right, 25 cap hits (T1: 410, 27); RL 456 right, 6 cap hits (T2: 463, 6).
- H1: the direction held (RL minus base 5.6 under the vote, 10.2 single), the predicted sizes were wrong: base +8.2 (predicted
  2 to 6), RL +3.6 (predicted at most 2). The prior, Maj@4 +0.8 on a 73.6 % model (2507.18122 Table 1), is far below both.
- H2 held: base +1.6, RL +0.4.
- H3 held: the restart costs 1,044 more tokens per problem for 1.6 points (650 per point), the vote 12,226 for 8.2 (1,490 per
  point).
- H4 refuted by its own criterion: the interval of base vote minus RL single includes 0. The base vote spends 3.4 times RL's
  single-sample tokens for that. With the same procedure RL stays 5.6 points ahead, and at about equal tokens (16 to 19 k per
  problem) RL's vote is 474 against the base's 446 to 450.

Raw rows read (base): the vote turns 43 problems from wrong to right and 2 from right to wrong (problems 50 and 403: a wrong
answer with 3 and 2 votes against a right sample 0). In the 43, sample 0 had a wrong answer 28 times and no answer 15 times (10
cap hits). 36 ties for first, 5 scored right. No winning group mixes right and wrong members; in 2 problems `agree` kept two
right answers apart (`east` / `East`, `$f(3) = 8$` / `8`) without changing the score. Sample-0 restarts: of 25 cap hits, 8 end
right, 8 wrong, 9 hit the cap three times. Rule A flags 0 of the base's 166 cap-hit rows and 1 of RL's 44: at T 1.0 the cap
hits are long answers, not loops. RL: 18 wrong to right, 0 right to wrong, 16 ties (3 right). Of the 54 problems the base
vote misses, RL's vote also misses 24. Grader note: `\text{Evelyn}}`-style endings extract as `Evelyn}` and score wrong (seen
in the smoke); grader v3 is unchanged.

Chosen for hard328 by the rule above: the vote over 4 after restart (base 450), i.e. the same command; not run yet.
