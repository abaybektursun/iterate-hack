# SPEC: direct test hostcap (round-15/account-1/c1)

Board: idea work-4948a7, test work-b727e3. Written and pushed before any computation.

## Claim (plan, round 15, `results/wide/round-15/synthesis_tests.md`, section `round-15/account-1/c1`)

If on-policy RL under any reward concentrates in the inputs the base's own text drives (S1), Code-RL 3.1's weight
change must sit in RL-Math 3.1's top-8 input subspace far more than off-policy Think-SFT's diffuse change does. If each
reward wrote its own subspace, Code's capture would be no higher than Think-SFT's.

## Rows

`studies/theory/data/direct_host/cap_v1.json` (job abaybektursun-1114-221259-0871, k = 8): all 224 layer matrices
(32 layers x q, k, v, o, gate, up, down). Per matrix: `cap["code31>math31"]["cap_right"]` and
`cap["think_sft>math31"]["cap_right"]`, where cap_right(a>b) = ||d_a V_b||^2 / ||d_a||^2, d_a = model a - base,
V_b = top-8 right (input) singular vectors of model b's change.

## Statistic and computation

1. Per matrix r = cap_right(code31>math31) / cap_right(think_sft>math31).
2. Statistic = median of r over the 224 matrices (unitless ratio).
3. 90 % interval: resample the 224 matrices with replacement 10,000 times (numpy seed 0), median each time, 5th and
   95th percentiles.
4. Secondary (reported, not used by the verdict): the ratio of means (mean Code cap / mean Think-SFT cap); the
   number of matrices with r > 1; the median r per module type; the same ratio with Math 3.0's subspace (math30) and the
   base matrix's own subspace (base_w) as the target, to show whether Code's excess is specific to Math 3.1's inputs.

## Null and ranges (fixed in advance by the plan)

- Null: Think-SFT's own capture of the same subspace, so the ratio is about 1 if concentration is reward-specific and
  Code's change is as unrelated to Math's inputs as a diffuse fine-tune. Null value 1.0; null range [0.5, 1.5].
- account-1 range: [2.0, 60.0].

## Verdict rule (engine 14)

- holds: the 90 % interval lies wholly inside [2.0, 60.0] and n >= 50.
- refuted: the 90 % interval lies wholly outside [2.0, 60.0].
- otherwise undecided; state the n that would decide.
Also report where the value falls relative to the null range [0.5, 1.5].

## Outputs

`studies/theory/analysis/direct_hostcap.py` writes `studies/theory/results/direct/hostcap-01/`: `metrics.json`,
`examples.json` (two real rows that enter the statistic), `run.json`, and later `rows.json`.
