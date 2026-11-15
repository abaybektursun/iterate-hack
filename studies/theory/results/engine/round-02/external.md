# External findings for round 02

Published mechanisms that could explain the least-explained results in before.jsonl. Targets (team items):
(a) DARE: a random 0.1-3 % of the MLP delta scaled by 1/q recovers like the whole MLP delta, while the top-changed neurons do no better than random ones (knowledge-8229be, knowledge-69adda, result-156f7b); in bytegraft (SFT, 1B) the same sparse copy gives 0 (knowledge-b8d41a).
(b) RL is a small, nearly linear nudge to almost every neuron; attribution ranking beats weight-change ranking 3x (result-904bbf, result-e2482e).
(c) The cued base loops at T 0.6 (98-119 cap hits) and has 0 rule-A loops at T 1.0; RL does not depend on temperature (result-e870a1, result-dadeec, result-533123, knowledge-787e53, knowledge-1497e8).
(d) The gap is in every length quartile and largest on the longest problems; base short answers are wrong more often (knowledge-9e4147, result-5de032, result-5e17a6).
(e) RL's change at the answer-start token follows format, not correctness; KL is less sparse than published (top 4 % of positions carry 38.7 %) (result-fdc8da).
(f) Math-RL and Code-RL deltas are nearly orthogonal (cos 0.014) yet change the same entries 1.64x more than chance with 50.8 % sign agreement (result-c9b27e, result-e2482e).
(g) Base and RL compute almost the same activations on general text; RL top-activating contexts change at the level of 2.5x noise (knowledge-87618d, knowledge-9c5052).
(h) Cued base pass@16 95.4 above RL pass@1, yet RL leads on harder sets (knowledge-8a31ad, result-82b4dc).

---

### 2610.37719 — What a Weight Update Buys: Leverage Across Training Stages, 2026
- Finding: For 5 Olmo-3-7B RL-Zero deltas the "leverage" (Fisher curvature along the RL-minus-base direction divided by that of a random same-norm direction) is 708 geometric mean (388-1,508); pretraining windows read 0.86 and SFT 5.5 (Sec 3, Table 1). A sign-flip null (same magnitudes, random signs) loses most of the effect, and magnitude alignment c_sign/c_profile is 1.1-1.6, i.e. about 1: the effect sits in the signs and cross-coordinate structure, not in large weights on high-Fisher coordinates (Table 2). DARE damage follows (1-p)/(p*rho_sign): OLMo-2-1B RLVR (rho_sign 474) loses 0.2 / 2.0 / 22 % of its own KL at keep 0.5 / 0.1 / 0.01, predicted 0.2 / 1.9 / 21 %; SFT-like deltas with rho_sign < 6 fail by keep 0.1 (Sec 7, Fig 5).
- Bears on: knowledge-8229be, knowledge-69adda, result-156f7b, knowledge-b8d41a, knowledge-c788b4 — explains why DARE works on the RL delta (high sign coherence) and fails on the bytegraft SFT delta, and why ranking neurons by change magnitude finds nothing; predicts DARE at keep 0.1 % on the Olmo-3 Think-SFT delta collapses, a sign-flipped RL delta of equal norm gives near-base accuracy, and that the RL delta at a = 1 is ~700x more consequential in KL than the norm-matched random edit (so a random arm on Olmo RL should not reproduce the WSP-style random gain).
- Already cited by the team: no

### 2410.09344 — DARE the Extreme: Revisiting Delta-Parameter Pruning for Fine-Tuned Models, 2024
- Finding: Theorem 3.1 bounds DARE's output change |h_diff_i| by (Psi(p)/(1-p)) * sqrt(n (c_bar_i^2 + sigma_i^2) log(2/gamma)), where c_ij = dW_ij x_j: DARE fails when the drop rate is high or the delta entries have large mean/variance relative to activations. MetaMath-LLaMA-7B (mean |delta| 0.017) drops sharply already at p > 0.1 (Table 6, App C.6); with small deltas DARE beats importance-based pruning, with large deltas importance-based pruning wins (Sec 5.3).
- Bears on: knowledge-8229be, knowledge-b8d41a, result-e2482e — the Olmo RL delta is 0.24 % of weight norm, the Think-SFT delta 24.8 % (100x larger), so the theorem predicts DARE survives on RL and not on SFT; predicts that DARE at q = 0.1 % on the RL delta scaled by a > 1 (larger delta) degrades faster than at a = 1, and that magnitude-ranked pruning would beat random only for the SFT delta.
- Already cited by the team: no (the team names DARE but not this paper)

### 2511.08567 — The Path Not Taken: RLVR Provably Learns Off the Principals, 2025
- Finding: RLVR updates avoid the principal (top singular) directions and land in low-curvature, spectrum-preserving subspaces (Gate II); bf16 storage hides sub-ULP updates (Gate III), so apparent sparsity is a readout of a model-conditioned bias. Five RLVR runs on different datasets and algorithms from one base share the updated-entry mask with Jaccard far above the Bernoulli baseline (Sec 2.2, Table 2); raising the learning rate makes the sparsity disappear; RLVR sparsity 36-92 % vs SFT 0.6-18.8 % (Table 1). Updating only non-principal, low-magnitude weights tracks dense RLVR; restricting to principal weights is worst (Sec 5).
- Bears on: result-c9b27e, result-156f7b, knowledge-8229be — explains why Math-RL and Code-RL touch the same entries 1.64x more than chance while their directions are orthogonal (the mask is set by the base, the direction by the data), and why magnitude ranking fails; predicts the shared-entry excess is concentrated in low-|w| entries off the principal subspace, and that the RL delta's projection on each matrix's top-k singular directions is smaller than a random matched-norm delta's.
- Already cited by the team: no

### 2609.22146 — GRRR: The Geometry of Reshaping, Rotation, and Routing in Decoder LLM post-training, 2026
- Finding: Independent RL updates from one base have update-direction cosine 0.003-0.037 (median per matrix), above the isotropic null; data, not algorithm label, sets the direction (Sec 6, App G, Fig 5). For MiMo-7B-RL-Zero (RL from base), off-diagonal-only and null-space-only parts of the update each recover 74 % and 80 % of the math gain, together 95 %; diagonal-only 21 % (App E, Table 6): the gain is redundant across components.
- Bears on: result-c9b27e, result-904bbf, knowledge-69adda — the team's cos 0.014 is the published normal level for two RL runs, not evidence of task specificity; redundancy predicts that two disjoint random halves of the Olmo delta (like DARE draws) each recover most of the gain, and that removing the top-singular part of each matrix costs little.
- Already cited by the team: no

### 2609.36262 — Understanding LLM Parameter Update Sparsity through the Lens of Fisher, 2026
- Finding: On Qwen3-1.7B-Base, the top 1 % of coordinates by diagonal Fisher on the model's own samples (no reward) contain 47.4 % of the top 1 % by RL gradient magnitude, vs 1.0 % random (Sec 3.2, Fig 2a). Training only the top 0.1 % Fisher coordinates recovers 85.2 % of the RL gain; a same-size random mask gives almost none (22.65 -> 23.90 vs full 56.41; Table 8). On-policy token Fisher is 0.16 of a uniform reference at init and 0.04 after RL (Table 3).
- Bears on: result-904bbf, result-156f7b — explains why an effect-based (attribution) ranking beats a change-magnitude ranking 3x; predicts a label-free Fisher-ranked neuron transplant on Olmo closes more KL than the weight-change ranking and approaches the attribution ranking, with no RL labels used.
- Already cited by the team: no

### https://thinkingmachines.ai/blog/lora/ — LoRA Without Regret (Thinking Machines Lab), 2025
- Finding: Rank-1 LoRA matches full fine-tuning for policy-gradient RL on MATH; argument: policy gradient absorbs about 1 bit per episode, so ~10,000 problems x 32 samples = 320,000 bits, below the 3M parameters of rank-1 LoRA on Llama-3.1-8B (section "LoRA for RL"). MLP-only LoRA beats attention-only at equal parameter count.
- Bears on: knowledge-69adda, knowledge-8229be, result-904bbf, knowledge-2ded8a — if RL stores only ~10^5-10^6 bits, the useful change is a few directions spread over every neuron, which is why no neuron subset carries it and why unbiased noise along the delta is tolerated; predicts a rank-1 or rank-4 per-matrix approximation of the Olmo delta recovers most of the MATH-500 gain (the never-run test in knowledge-69adda), and that MLP-only beats attention-only (as observed: 86.4 vs 83.0).
- Already cited by the team: no

### 2601.04537 — Linear Dynamics in the RLVR Training of Large Language Models, 2026
- Finding: RLVR weight trajectories are close to linear in training step (median per-weight R^2 0.868, 82.4 % of weights above 0.7), also for RL run directly on a base (Qwen3-8B, DAPO-Math, GRPO; Sec 5.1, App C.2). Logit extrapolation along the trajectory with alpha > 1 raises MATH500 avg@64 0.8803 -> 0.8900 and AIME24 0.4193 -> 0.4458 (Sec 6.1, Table 1).
- Bears on: result-904bbf, knowledge-8229be, knowledge-b8d41a — a linear trajectory fits the team's finding that first-order neuron scores add up (0.542 predicted vs 0.549 measured); predicts base + a*(RL - base) on Olmo rises monotonically up to a = 1 and keeps a small gain or plateau slightly past 1 (unlike the SFT bytegraft peak at 0.7-0.8), with length and stop rate drifting before accuracy falls.
- Already cited by the team: no

### 2404.16792 — Model Extrapolation Expedites Alignment (ExPO), 2024
- Finding: Under a first-order approximation, the reward is linear along theta_0 + gamma*delta for small ||delta||; interpolations between SFT and DPO/RLHF models give intermediate scores, and amplifying the delta (theta_1 + alpha*delta) lifts a DPO model trained 20 % of the steps above the fully trained one, up to +8.4 LC win rate on AlpacaEval 2.0, and 12 released models by up to +4.5 (Sec 2.3, Table 2). Gains require the alignment delta to be small.
- Bears on: knowledge-8229be, result-904bbf — gives the published rationale for why a small RL delta behaves linearly and tolerates unbiased noise; predicts the Olmo RL delta (0.24 % of norm) sits in the regime where a > 1 helps a little on MATH-500 before format/length breaks, and that the RL-Zero step_0100 delta extrapolated to a ~ 28 gets a large part of the final gain.
- Already cited by the team: no

### 2509.04259 — RL's Razor: Why Online Reinforcement Learning Forgets Less, 2025
- Finding: On-policy RL converges to the KL-minimal policy among those that solve the task (Theorem 5.2); forgetting is predicted by KL(pi_0 || pi) on the new task (quadratic fit R^2 0.96 ParityMNIST, 0.71 LLMs); on-policy methods reach the same accuracy at much smaller KL than SFT or SimPO (Sec 4-5).
- Bears on: knowledge-87618d, knowledge-9c5052, result-fdc8da — explains why RL leaves general-text activations at r 0.999 and top contexts at 2.5x noise while math text diverges, and why mean KL per token is only 0.06-0.09 nats; predicts RL-Zero-Code shows the same pattern on code text and near-identity on math text, and that the Think-SFT model diverges on general text far more than RL.
- Already cited by the team: no

### 2512.12895 — Wait, Wait, Wait... Why Do Reasoning Models Loop?, 2025 (ICML 2026)
- Finding: All tested reasoning models loop at low temperature and looping falls as T rises; harder problems loop more (OpenThinker3-1.5B greedy: 51 % hard vs 13 % easy; Sec 2, Fig 11). Two mechanisms: risk aversion (when the progress-making action is hard to learn, its mass is diffused across alternatives while an easy cyclic action keeps its mass; Prop 3.1) and temporally correlated errors (the same top-1 choice repeats at consecutive decision points in 80.5 % of visits; Sec 4). Temperature removes loops but not the error: at T 1 the learned model's responses are 2.74x a perfect learner's length (67.4 vs 24.6) and reach 72.25 % at equal budget (Sec 3.3).
- Bears on: result-e870a1, result-dadeec, knowledge-787e53, knowledge-9e4147, result-82b4dc — explains loops at T 0.6 and none at T 1.0, more cap hits on the longest quartile, and why T 1.0 still leaves a 10.6-point gap at higher token use; predicts base loop onsets come at points where the base's next-step distribution is flat (high entropy over progress steps) with a restatement as top-1, and that at T 1.0 the cued base's right answers stay longer than RL's on matched problems.
- Already cited by the team: no

### 2206.02369 — Learning to Break the Loop: Analyzing and Mitigating Repetitions for Neural Text Generation, 2022
- Finding: Sentence-level repetition self-reinforces: the probability of repeating a sentence rises almost monotonically with the number of times it is already in context and saturates at a ceiling; sentences with higher initial probability (e.g. produced by maximization-based decoding) reinforce faster (Sec 3, Fig 2-3, 7).
- Bears on: result-e870a1, knowledge-1497e8, knowledge-4fb5eb — explains why a base loop at T 0.6 runs to the 16,384 cap once started and why low temperature (higher-probability text) triggers it; predicts P(next copy of the repeated block) under the base rises over the first 2-5 repeats in saved cap-hit answers, and that the repeat-reading neurons (layers 10-15) increase activation with repeat count.
- Already cited by the team: no

### 2601.05693 — Circular Reasoning: Understanding Self-Reinforcing Loops in Large Reasoning Models, 2026
- Finding: LoopBench loop rate falls with temperature but not to zero; Qwen3-8B-base 42.29 % / 22.29 % / 20.15 % at T 0.1 / 0.6 / 1.0 (with top-k/top-p changed jointly); numerical loops barely change with T (38.86 / 20.57 / 19.86 %) (Tables 1, 6, 7). Loops start at a reasoning impasse followed by a self-correction and retry (Sec 3.2, Fig 6-7).
- Bears on: result-dadeec, knowledge-1497e8, result-5e17a6 — loops begin at impasses, which fits the base finishing far more often from RL's sound prefix (48 vs 23); predicts loop onsets in the cued base sit right after a 'Wait'/self-correction line, and that at T 1.0 the base's failure mode shifts from loops to long non-repeating cap hits (as seen: 16 RL-only cap hits with no loop).
- Already cited by the team: no

### 2007.14966 — Mirostat: A Neural Text Decoding Algorithm that Directly Controls Perplexity, 2020
- Finding: Repetition rate is a near-linear function of the observed cross-entropy of the generated text, mostly independent of the sampling method (Sec 5.2, Fig 3); small k/p make perplexity fall with length (boredom trap, repetition), large k/p make it rise (confusion trap, incoherence) (Sec 3, 5.1).
- Bears on: result-dadeec, knowledge-9e4147, result-7968b8 — explains why removing top-p at T 0.6 (354 -> 378) and raising T to 1.0 both cut loops, and why the plain base loses 28 points on short problems at T 1.0 (confusion trap) while gaining on the longest (escaping the boredom trap); predicts that per-token surprise of the base's generated text falls with position before loop onset, and that a fixed-surprise sampler at the RL model's per-token surprise removes most base loops.
- Already cited by the team: no

### 2509.09677 — The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs, 2025
- Finding: With step accuracy p and no correction, success after t steps is p^t, so horizon length grows hyperbolically past ~80 % step accuracy (Sec 2.1). Per-step accuracy falls as the task goes on because of self-conditioning: injecting errors into a model's own history lowers later-step accuracy, and scaling model size does not remove it; thinking models are not affected (Sec 3.2, Fig 5).
- Bears on: knowledge-9e4147, result-5de032, knowledge-1497e8, result-5e17a6 — a small per-step error gap compounds into a gap that grows with solution length (Q4 -20.0 vs Q1 -11.2 points), and self-conditioning explains why the base finishes from RL's prefix (48/78) but not its own (23/78); predicts that splicing a base prefix with one injected arithmetic error lowers the base's continuation accuracy more than RL's, and that the RL-minus-base gap per quartile fits 1 - p_rl^L vs 1 - p_base^L with one step-error parameter each.
- Already cited by the team: no

### 2510.07364 — Base Models Know How to Reason, Thinking Models Learn When, 2025
- Finding: A hybrid that generates with the base and, only where base and RL disagree on the next token, adds a base-model steering vector chosen by the RL model's SAE category recovers ~76 % of the RL base-to-thinking gap (Open-Reasoner-Zero pairs) but ~11 % for SFT-distilled pairs, while steering only 5-12 % of tokens (Abstract, Sec 3.7, Table 1-2); RL teaches when to deploy existing behaviors, SFT installs new ones.
- Bears on: result-e2482e, knowledge-6f3040, knowledge-9e4147, result-fdc8da — matches the RL delta pointing along deliberation words the base already has ('Wait', 'Okay') and being orthogonal to the Think-SFT delta; predicts that a base + few steering vectors triggered at RL-disagreement positions recovers most of the 10.6-point MATH-500 gap on Olmo, and that the same construction for Think-SFT recovers little.
- Already cited by the team: no

### 2610.30882 — Inherited, Not Invented: Tracing the Provenance of Wait in Reasoning Models, 2026
- Finding: Olmo-3-1025-7B base already writes 'wait' at 4.9 per 1k tokens (inherited from mid-training reasoning traces; <= 0.04 in stage-1 pretraining); Olmo-3-7B-RL-Zero-Math multiplies it to 12.68 per 1k (peak 17.0 at step 1900) (Table 2, Sec 4). On injected-error prefixes RL's 'wait' follows 73.7 % of error prefixes (base 47.1 %) and 25.4 % of error-free ones (base 19.9 %): d' 0.57 -> 1.09, criterion 0.11 -> -0.24 (Sec 4.1, Fig 4). The released RL-Zero-Math hits the length limit on 29.1 % of responses (Table 14).
- Bears on: result-fdc8da, result-e2482e, knowledge-6f3040, result-5e17a6 — RL's lower P(stop) at the base's true ends and its preference for ' Wait' at early gaps are a more liberal, more sensitive error-check criterion; predicts that RL's extra length concentrates after the first candidate answer, and that the 13 short wrong base answers are ones where RL places 'Wait' right after the base's (wrong) candidate.
- Already cited by the team: no

### 2603.22446 — Sparse but Critical: A Token-Level Analysis of Distributional Shifts in RLVR Fine-Tuning of LLMs, 2026
- Finding: Base-vs-RL JS divergence on RL text is near zero at > 98 % of positions for SimpleRL and > 83 % for DAPO (Qwen2.5-32B, AIME24; Sec 2.2, Fig 2). Sampling only the high-divergence positions from RL during base generation: SimpleRL 3.86 % of tokens lifts base 8.23 -> > 25 (RL level), DAPO needs 7.8 % (280 tokens) for > 44 (Table 1); reverse swaps of ~5 % (SimpleRL) or ~10 % (DAPO) drop RL to base level, smoothly with the number of swaps. RL weight gap sigma 0.00136-0.00143 vs SFT 0.0035-0.0094 (App A.3).
- Bears on: result-fdc8da, knowledge-d692e4 — the published sparsity depends on how long/strong the RL recipe is (DAPO denser than SimpleRL), which can explain Olmo 3.1's denser KL (top 4 % = 38.7 %) after 2,800 steps at 16k; predicts the RL step_0100 checkpoint shows sparse KL like SimpleRL, and that forward cross-sampling on Olmo needs ~8 % of positions (not 4 %) to reach RL's MATH-500 score.
- Already cited by the team: no

### 2603.22117 — On the Direction of RLVR Updates for LLM Reasoning: Identification and Exploitation, 2026
- Finding: Replacing only the base tokens with large negative log p_RL - log p_base (~10 % of tokens) by RL samples reaches RL's AIME24 avg@32 (ORZ-32B 3.02 -> 46.15; DAPO-Qwen-32B 6.67 -> 52.50); magnitude-only metrics and random positions recover much more slowly (Sec 3.2, Fig 2). 89-97 % of tokens have |log-ratio| < 0.25-0.5; the tokens RL raises most are reasoning actions and transitions (wait, think, step), low-probability under both models (App E).
- Bears on: result-fdc8da, knowledge-6f3040 — the signed log-ratio, not the KL magnitude, identifies the decisive positions, which fits D following format at the answer start and RL raising 'Wait'/'Hmm'; predicts that on Olmo, gating by signed log-ratio beats gating by KL at equal swap budget, and that the decisive swaps sit on transition words rather than on the answer line.
- Already cited by the team: no

### 2506.01939 — Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective RL for LLM Reasoning, 2025
- Finding: In CoT, 50.64 % of tokens have entropy < 0.01 and only 20 % exceed 0.672 (Sec 3, Fig 2); RLVR keeps the base's high-entropy positions (> 86 % overlap of the top-20 % entropy positions with the base at convergence, Qwen3-14B DAPO, Table 1) and mainly changes entropy at those positions. Policy gradient on only the top 20 % entropy tokens matches full RL on Qwen3-8B and beats it on 32B (+11.04 AIME25); training on the bottom 80 % fails.
- Bears on: result-fdc8da, result-904bbf, knowledge-87618d — RL acts at the base's own forking positions, consistent with base entropy finding RL-different positions and with activations diverging only on math text; predicts that on Olmo the 4 % most-different positions are almost all within the base's top-20 % entropy positions and that the remaining KL (61 %) is spread over medium-entropy tokens.
- Already cited by the team: no

### 2505.22617 — The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models, 2025
- Finding: Without entropy control, policy entropy collapses early (73 % of entropy consumption and 76 % of the gain in the first 200 of 2,400 steps across 11 runs; Sec 2.3, Fig 2) and accuracy follows R = -a exp(H) + b (Sec 2.4). Entropy change equals the covariance of log-probability and logit change, which stays positive, so entropy falls monotonically (Sec 3).
- Bears on: result-533123, knowledge-9e4147, result-fdc8da — a low-entropy RL policy is insensitive to temperature (T 0.6 vs 1.0: -0.2 points), while the high-entropy base is not; predicts RL's mean per-token entropy on its own answers is well below the cued base's, that RL at T 1.2-1.5 still holds near 92 %, and that most of the RL-Zero gain is already present at step ~400 (the step-400 checkpoint).
- Already cited by the team: no

### 2504.13837 — Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?, 2025
- Finding: RLVR models win at small k, but base models overtake them as k grows to tens or hundreds on every benchmark and family tested (e.g. Minerva, 32B: base +9 % at k = 128; Fig 2, Sec 3); RL narrows coverage while raising the probability of already-present correct paths.
- Bears on: knowledge-8a31ad, result-82b4dc, result-5de032 — base pass@16 95.4 above RL pass@1 fits "RL reweights paths the base has"; predicts that on the harder 328, cued-base pass@k crosses RL pass@k somewhere in k = 16-128, and that of the 33 problems where the base finished with a wrong answer, most are solved by the base within 16 samples.
- Already cited by the team: no

### 2503.01307 — Cognitive Behaviors that Enable Self-Improving Reasoners (Four Habits of Highly Effective STaRs), 2025
- Finding: RL gains depend on whether the base already shows verification, backtracking, subgoal setting and backward chaining: Qwen-2.5-3B (has them) improves far more than Llama-3.2-3B (lacks them) under identical PPO on Countdown; priming Llama with traces containing these behaviors, even with wrong answers, lets it match Qwen; RL amplifies backtracking and verification (Sec 3-4, Fig 1-3).
- Bears on: result-c36598, result-e2482e, knowledge-8a31ad — the cue (2 tokens) works on Olmo because the base already has these behaviors from mid-training; predicts that RL's MATH-500 gain over the cued base is concentrated in answers where RL verifies after a first candidate, and that a plain base with zero verification lines at T 1.0 is the subgroup with the lowest accuracy.
- Already cited by the team: no

### 2611.02574 — RLVR Sharpens the Pencil, Not the Mind, 2026
- Finding: On OLMo-2-0425-1B-Instruct, GSM8K, 13 RLVR checkpoints: pass@1 0.580 -> 0.613 while pass@256 rises 0.945 -> 0.969 (Sec 4.1). A probe separating early from late checkpoints reaches AUROC 0.93 at the final answer token but is near chance at intermediate reasoning tokens (Sec 4.2, Fig 2b): RLVR's footprint is at the output end.
- Bears on: result-fdc8da, knowledge-87618d, knowledge-6f3040 — fits RL changing the answer-format token by -8.36 nats and RL's activations diverging most in late layers on math text; predicts the base-vs-RL activation difference on Olmo is largest at answer-line and stop positions, and smallest at mid-solution algebra tokens.
- Already cited by the team: no

### 2506.10947 — Spurious Rewards: Rethinking Training Signals in RLVR, 2025
- Finding: On Qwen2.5-Math-7B, random reward gives +21.4 MATH-500 points vs +29.1 for ground truth and format-only reward +13.8-16.4 (Sec 2.2, Fig 1); OLMo-2-7B base and SFT stay flat under format, incorrect and random rewards and gain only with ground truth (Sec 3, Fig 3).
- Bears on: knowledge-8229be, knowledge-69adda, result-fdc8da — part of RL's gain can be format alone, and every recovering transplant arm takes RL's format (Answer: line 0-4 % vs 39-46 %); for the OLMo lineage it predicts format is necessary but not sufficient: a base with the Answer: line format forced to \boxed (no weight change) should gain only a few points, far below the 10.6-point gap.
- Already cited by the team: no

### 2312.01552 — The Unlocking Spell on Base LLMs: Rethinking Alignment via In-Context Learning (URIAL), 2023
- Finding: Between a base and its aligned model, only 4.8-7.8 % of tokens are shifted (aligned token at base rank > 3); 82 % are unshifted (Sec 2.2, Fig 2-3). KL between base and aligned next-token distributions falls with position; shifted tokens are mostly discourse markers and appear early in the response (Fig 4).
- Bears on: result-c36598, result-fdc8da, knowledge-8a31ad — a 2-token cue can stand in for much of post-training because the shift is concentrated in the opening and in discourse markers; the Olmo top-1 disagreement rate (7.98-8.20 %) is the same order as URIAL's; predicts the per-position KL between RL and cued base falls with position after the cue except at answer/stop tokens.
- Already cited by the team: no
