# Problem dependence of the early answer text as a label-free sign of a wrong sample (work-2cd5d0)

Written before the job. Follows result-c495fe (a judged misreading has already cost 32 points before its sentence) and the rule
screen (the base's misread steps lose 4.62 nats under problem contrast: they depend less on the problem than other text).

Question: does the early text of a wrong sample depend less on the problem than the early text of a right sample of the same
problem, enough to tell them apart with no label and no second model?

Measure. For each of the 2,000 stored samples of the cued base on MATH-500 (4 per problem, T 1.0, job
`abaybektursun-1114-153825-208b`; input `data/wrongstep/base_cue_answer_heads_v1.jsonl.gz`, the first 6,000 characters of each)
and each of its first 1,000 answer tokens t: d_t = log p_base(t | problem, text before) - log p_base(t | empty problem, text
before). Both from the unchanged base (`jobs/probdep_tokens.py`). This is the per-token quantity that context-aware decoding
(Shi et al. 2023, arXiv 2305.14739) adds to the logits; here it is only read. Features per sample at K = 250, 500, 1,000 tokens:
mean d_t over the first K tokens; the share of tokens with d_t < 0; the mean of the lowest 10 % of d_t.

Statistic: within-problem AUROC of right against wrong (pairs of one right and one wrong sample of the same problem, as in
`analysis/critic_probe.py`), bootstrap over problems, 5,000 resamples. Samples shorter than K tokens use what they have.
Controls: the same AUROC for the answer length n_new (the known confound), for the mean log p_base alone, and with the feature
shuffled within the problem. Comparison: the linear probe on activations, 0.571 [0.509, 0.634] at 1,000 tokens (result-b30f15).

Predictions (each with what refutes it):
- P1 mean d_t over the first 1,000 tokens is higher for the right sample: AUROC >= 0.60 with the interval above 0.55. Refuted if
  the interval includes 0.55.
- P2 the signal is not length: it stays above 0.55 among pairs whose two samples both have more than 1,000 tokens.
- P3 it is specific to misreadings: on the 60 judged wrong samples the mean d_t over the first 1,000 tokens is lowest for
  `misread`. Refuted if `misread` is not below both `slip` and `wrong_plan`.

Decision: if P1 and P2 hold, compute offline from the same rows what a restart at 1,000 tokens on low d and a vote weighted by d
give, against the perfect-critic bound 438.7 (results/critic/ceiling-02). If P1 fails, problem dependence joins the activation
probe as a signal that does not separate the base's own samples, and the misreading result stays a property of single steps.
Cost: one job, about 10 GPU minutes.
