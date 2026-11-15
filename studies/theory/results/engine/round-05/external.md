External mechanisms from published work: decoding, RL weight changes, interpretability readouts, item difficulty, RL algorithms/rewards/data, graders and formats, and analogues outside language models (28 findings)
---

### 2407.01082 — Turning Up the Heat: Min-p Sampling for Creative and Coherent LLM Outputs, 2024
- Finding: Min-p truncation keeps tokens whose probability is at least p_base × p_max, so the cutoff tightens when the model is confident and loosens when it is not. Its advantage over top-p appears only at high temperature. Table 2 (Mistral-7B, GSM8K CoT 8-shot): at τ=1.0, min-p 30.86 vs top-p 27.67 vs temperature only 17.51; at τ=1.5, 18.42 vs 0.68 vs 0.00. At τ<1.5 min-p and top-p perform about the same (Sec 5.2.2, Table 10). Table 8b (Llama-3.2-1B-Instruct, GSM8K): greedy 46.55; at τ=1.5, min-p 0.1 gives 29.11 vs top-p 0.9 5.23.
- Where measured: Mistral-7B and Llama-3.2-1B/3B-Instruct; GPQA Main (5-shot) and GSM8K CoT (8-shot); vLLM; min-p 0.05/0.1 vs top-p 0.9/0.95, τ from 0 to 5.

### 2512.12895 — Wait, Wait, Wait... Why Do Reasoning Models Loop?, 2025
- Finding: Looping falls as temperature rises from 0 to 1.0 for every model tested. Smaller and distilled students loop more than their teachers. Loop fraction at T=0 (Sec 2, App. A, Table 1): R1-Distill-Qwen-1.5B 0.76, 7B 0.49, 32B 0.37; OpenThinker3-1.5B 0.30 vs its teacher QwQ-32B 0.04. RL-tuned Phi-4-reasoning-plus (0.45) loops about as much as Phi-4-reasoning (0.43). Only temperature is varied; top-p is never varied.
- Where measured: open reasoning models on AIME 2024+2025 (60 problems), 20 samples per problem and temperature, 30K-token cap, default top-k/top-p, no repetition penalty. A loop is a 30-gram that appears at least 20 times.

### 2610.24715 — When Do Repetition Loops Lock? Truncation Sampling, Bounded Penalties, and a Blind Spot in DRY, 2026
- Finding: Under top-p with threshold π > 1/2, a loop position becomes deterministic (escape probability exactly 0) once the loop token's raw probability reaches π. Applying temperature before top-p lowers that threshold: at T 0.7 / top-p 0.9 it falls from q ≥ 0.9 to q ≥ 0.823 (Theorem 1, Prop. 3). Pure sampling never locks, but its escape probability per repetition is only 10^-1.5 to 10^-3.5 (App. B). Teacher-forced on 150 repeated units, 71–100% of units stay locked under top-p 0.9 vs 0% under pure sampling (Table 2).
- Where measured: 11 open models, teacher-forced repeated units, Hugging Face transformers sampling order. The paper also tests the DRY penalty and structured generation.

### 1908.04319 — Neural Text Degeneration with Unlikelihood Training, 2019
- Finding: Maximum-likelihood training gives too much probability to repeats, and deterministic decoding exposes it. With greedy decoding, 43% of n-grams in model continuations are repeats vs 0.5% in human text. Top-k and nucleus sampling reduce repetition, but the token probabilities underneath stay the same (Sec 4). The authors' fix is a token- and sequence-level unlikelihood loss.
- Where measured: a Transformer LM trained with maximum likelihood on Wikitext-103, continuations of validation-set prefixes; GPT-2 samples in the appendix.

### 2505.17813 — Don't Overthink it. Preferring Shorter Thinking Chains for Improved LLM Reasoning, 2025
- Finding: Within one question, the shortest sampled thinking chain is more often right than a random or the longest chain. Accuracy shortest/random/longest (Table 1): LN-Super-49B 63.4/47.7/28.9, R1-32B 60.0/55.5/37.8, QwQ-32B 71.1/68.9/56.7, R1-670B 83.3/78.2/58.9. Across questions, harder questions get up to 2.9× more tokens. short-3@k (majority over the first 3 of k chains to finish) beats majority@k at every budget, by about 2–4 points (Sec 4.3).
- Where measured: four reasoning models; AIME24, AIME25 and HMMT (30 problems each); 20 samples, T 0.7, top-p 0.95, 32,768-token cap. Samples that hit the cap are left out of Table 1.

### 2504.07086 — A Sober Look at Progress in Language Model Reasoning: Pitfalls and Paths to Reproducibility, 2025
- Finding: Single-run benchmark scores move with things unrelated to the model. Across 20 seeds, pass@1 has a standard deviation of 5–15 points on AIME'24 and AMC'23, and one question shifts pass@1 by 2.5–3.3 points (Sec 3, Fig. 2). Hardware alone changes accuracy by up to 8 points (OpenRS-1.5B) and 6 points (R1-Distill-7B) on AIME'24, even with deterministic CUDA settings (Sec 3, Fig. 10). Prompt template and framework also change scores: instruction-tuned models drop without their chat template, while Qwen2.5-Math base models can gain without one (Fig. 9).
- Where measured: nine 1.5B–7B reasoning models; AIME'24, AMC'23, MATH500; standardized Docker; A100 vs H100 clusters; vLLM.

### 2610.22438 — Rank Measures of Fine-Tuning Updates Need a Noise Baseline, 2026
- Finding: The direction of a fine-tuning update carries its function; its size does not. Qwen3-0.6B on GSM8K (greedy, Sec 5.1, Table 4): base 59.5%; base plus a Gaussian update with the real update's per-matrix Frobenius norm, 4.1% and 4.8% (two draws); real singular values in random directions, 5.8%; base plus the real update (instruct), 64.5%. Rank counting calls updates nearly full rank, but stable rank sits 4.5× below a Gaussian null (Qwen2.5-0.5B SFT 0.097 vs 0.436, Table 1). With model, optimizer and tokens fixed, SFT, wikitext, code and DPO updates have similar stable ranks (Table 2).
- Where measured: Qwen3-0.6B, Qwen2.5-0.5B, SmolLM2-360M and 7 released base/post-trained pairs. The real updates are 1–13% of weight norm.

### 2509.04259 — RL's Razor: Why Online Reinforcement Learning Forgets Less, 2025
- Finding: How much a fine-tune forgets is predicted by the forward KL between base and fine-tuned policy, measured on the new task's inputs. Weight-change size predicts it poorly. Quadratic-fit R² for forgetting (Sec 6, Table 1): forward KL 0.96, reverse KL 0.93, total variation 0.80, weight change L1 0.34, Fisher-weighted L2 0.58, activation change 0.52–0.55. The R² is 0.71 for LLM runs (Fig. 11). On-policy RL converges to KL-minimal solutions among those that solve the task; SFT does not.
- Where measured: ParityMNIST/FashionMNIST 3-layer MLP (~500 runs per method); Qwen2.5-3B-Instruct with GRPO (binary reward, no KL penalty) vs SFT; OpenVLA-7B robotics.

### 2510.00553 — On Predictability of Reinforcement Learning Dynamics for Large Language Models, 2025
- Finding: A rank-1 truncation of each matrix's RL update, rescaled to the full update's norm, recovers close to 100% of the fully trained model's accuracy (Sec 2.1–2.2, Fig. 3a, Table 8). For other training the same truncation recovers much less: offline distillation 1.5%, SFT 2.5%, on-policy distillation 56.4%, DPO 62.25% (App. C, Tables 7–8). Scaling the rank-1 update by λ from 0.1 to 1.0, MATH-500 accuracy rises fast, then saturates and peaks near λ≈0.7 (Fig. 4b). Linear extrapolation from 40% of training reaches 53.31 vs 53.38 for the full run (Table 1).
- Where measured: Qwen3-8B-Base trained with PPO, RLOO, GRPO, Dr.GRPO and DAPO; MATH-500, AIME24 and 4 other benchmarks; 32 samples, T 0.6. No random-direction control.

### 2505.11711 — Reinforcement Learning Finetunes Small Subnetworks in Large Language Models, 2025
- Finding: In released RL checkpoints, 68.5–96.0% of bf16 weights are unchanged at |Δ| ≤ 1e-5 (Table 1: deepseek-math-7b-rl 68.5%, DeepSeek-R1-Zero 86.0%, Tulu-3-70B DPO 95.2%). Yet the update matrices are 99.2–99.8% of full rank and spread evenly over layers (Table 2). At tolerance 1e-8 sparsity drops a lot (math-shepherd PPO 52.45% vs 80.77%, App. A Table 6), so much of it is bf16 storage of tiny updates. Sparsity follows whether the training data is close to the policy: rejection-sampling SFT is 91.2% sparse, off-policy DPO 6.8–7.7% (Table 5).
- Where measured: public checkpoints from GRPO, PPO, PRIME, DPO, KTO and SimPO runs (7B–70B), each compared with its pre-RL checkpoint; plus the authors' own Qwen2.5 runs.

### 2507.12638 — Reasoning-Finetuning Repurposes Latent Representations in Base Models, 2025
- Finding: A backtracking steering vector computed only from base-model activations, at token positions before a backtracking event, reliably makes the reasoning model backtrack. It works about as well as the vector computed from the reasoning model's own activations (Fig. 3). The two vectors have cosine ≈0.74. Neither vector makes the base model backtrack: the direction already exists in the base, and fine-tuning gives it a new downstream use. The effect is not explained by token-level attributes.
- Where measured: base Llama-3.1-8B vs DeepSeek-R1-Distill-Llama-8B, residual stream at layer 10, difference-of-means vectors with a negative token offset, steering during generation on reasoning traces.

### 2509.06608 — Small Vectors, Big Effects: A Mechanistic Study of RL-Induced Reasoning via Steering Vectors, 2025
- Finding: One steering vector per layer, trained with an RL objective on a frozen base, explains a large share of the full RL gain. The last-layer vector alone closes over 50% of the base-to-full-RL gap in Qwen2.5-Math-7B (Fig. 1). It acts as a token-substitution bias on the first generated token: its logit-lens top token is "To", cosine 0.37. Prefixing "To" to every prompt raises base accuracy by 10–11 points under greedy and sampling, about 75% of that vector's gain (Fig. 6). The penultimate-layer vector works through the MLP and unembedding, up-weighting process words. The vectors transfer within a model family.
- Where measured: Qwen2.5-Math-7B and Llama-3.1-8B-Instruct (weaker effect, top token "Step"), math reasoning benchmarks, greedy and sampled decoding.

### 2506.01939 — Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective Reinforcement Learning for LLM Reasoning, 2025
- Finding: In reasoning traces, 50.64% of positions have entropy below 0.01 and only 20% exceed 0.672. The high-entropy "forking" tokens are connectors such as wait, however, thus and suppose (Sec 3). RL keeps where these positions are: the top-20% entropy positions overlap 86.67% between base and final RL model (Table 1). Training on only those 20% of tokens matches or beats all-token DAPO (MATH500 Acc@16, 32B: 94.88 vs 94.36; AIME25 +11.04 at 32B; Table 2), with longer responses. Lowering temperature only at forking tokens hurts much more than lowering it at the other tokens (Fig. 3).
- Where measured: Qwen3-8B/14B/32B base models, DAPO on DAPO-Math-17K, T 1.0, 16 samples, max length up to 28,672; AIME24/25, AMC23, MATH500; one run per setting.

### 2504.13837 — Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?, 2025
- Finding: RLVR raises pass@1 but the base matches or overtakes it at large k. Per-problem coverage on MATH500 with 128 samples (Sec 4.1, Table 2): solved by both 92.4%, base only 3.6%, RL only 1.0% (all of which the base solves within 1,024 samples), neither 3.0%. On AIME24 with 1,024 samples: base only 13.3%, RL only 0.0%. Base accuracy drops when T exceeds 1.0 while the RL model is stable across T. Matching RL's temperature to base entropy still leaves RL pass@k below the base (Fig. 17).
- Where measured: Qwen2.5-7B base vs SimpleRL-Zoo GRPO, plus other Qwen/LLaMA RLVR pairs; T 0.6, top-p 0.95, 16,384-token cap, same zero-shot prompt for both; oracle pass@k only.

### 2505.24864 — ProRL: Prolonged Reinforcement Learning Expands Reasoning Boundaries in Large Language Models, 2025
- Finding: How much RL widens pass@128 depends on how well the base already does on a task, with a significant negative correlation (Fig. 3). Tasks where the base already has high pass@128 show minimal or negative pass@128 gain after RL; tasks where it is low gain most. The low-gain tasks also have low creativity index against DOLMA, i.e. high overlap with pretraining data. Over 2k+ RL steps with KL control and reference-policy resets, average pass@1 rises 14.7% on math, 13.9% on code and 54.8% on logic puzzles vs the starting model (Fig. 1). Some tasks go from 0 at any k for the base to 100% pass (Fig. 4).
- Where measured: DeepSeek-R1-Distill-Qwen-1.5B trained into Nemotron-Research-Reasoning-Qwen-1.5B; math, code, STEM, logic-puzzle and instruction-following tasks; pass@k up to 128.

### 2504.03380 — Online Difficulty Filtering for Reasoning Oriented Reinforcement Learning, 2025
- Finding: Expected policy improvement under GRPO is lower-bounded by the Bernoulli variance p(x)(1−p(x)) of each prompt's pass rate. Prompts with p ∈ {0,1} give zero advantage and no gradient; p≈0.5 gives the most signal (Sec 3). Keeping only prompts with intermediate online pass rates raises the 5-benchmark average from 26.3 (plain GRPO) to 30.1 at 0.2<p<0.8, peaking at 0.3<p<0.7. Skewed filters that drop only easy or only hard prompts score 23.8–25.9 (Table 1).
- Where measured: Qwen2.5-3B base, SFT cold start on 1.1K R1-distilled NuminaMath solutions, then GRPO with 16 rollouts on Eurus-2-RL math prompts; MATH500, AIME, AMC, Minerva, OlympiadBench.

### 2405.10938 — Observational Scaling Laws and the Predictability of Language Model Performance, 2024
- Finding: The model × benchmark score matrix is low-rank. The first principal component explains nearly 80% of the variance and the top 3 about 97% (Fig. 2a). The components read as general capability, reasoning (math and code) and programming (Fig. 2b). These low-dimensional capability scores predict performance on complex and "emergent" tasks better than compute-based scaling laws.
- Where measured: 77 public LMs from several families on 7 standard benchmarks (Open LLM Leaderboard and EvalPlus); PCA of benchmark scores.

### 2506.10947 — Spurious Rewards: Rethinking Training Signals in RLVR, 2025
- Finding: On Qwen2.5-Math-7B, rewards with no correctness signal give most of the RLVR gain. MATH-500 gain over 49.4% (Sec 2.2, Fig. 1): ground truth +29.1, wrong majority-vote label +24.1, random reward (p=0.5) +21.4, format only +13.8 to +16.4. Random reward with p=0 gives no change. The gains largely vanish on AIME25 and do not appear for OLMo2-7B or Llama models. The mechanism is a pre-existing behavior: code-style reasoning (60.9% accurate vs 28.0% without) rises from 65% to about 90% of responses within 15 steps; 58.3% of the gain comes from problems that switch to code (Sec 5, Table 1).
- Where measured: Qwen2.5-Math-7B/1.5B, Qwen2.5-7B, OLMo2-7B, Llama3; GRPO without KL, 16 rollouts, 300 steps on DeepScaleR prompts; MATH-500 greedy, AMC avg@8, AIME24/25.

### 2504.20571 — Reinforcement Learning for Reasoning in Large Language Models with One Training Example, 2025
- Finding: RLVR on one training example lifts Qwen2.5-Math-1.5B MATH500 from 36.0% to 73.6%, and the six-benchmark average from 17.6% to 35.7%. That equals RL on the 1.2k DeepScaleR subset (73.6%, 35.9%); two examples give 74.8%. Many single examples each give about +30 points on MATH500. The base already shows self-reflection words (rethink, recheck, recalculate), and their frequency rises late in 1-shot training (Fig. 5).
- Where measured: Qwen2.5-Math-1.5B/7B, Llama3.2-3B-Instruct, DeepSeek-R1-Distill-Qwen-1.5B; GRPO and PPO; MATH500 plus five other math benchmarks.

### 2503.20783 — Understanding R1-Zero-Like Training: A Critical Perspective, 2025
- Finding: GRPO's 1/|o| length normalization weights correct short answers more and penalizes long wrong answers less, so wrong answers grow longer. Its per-question std normalization overweights prompts that are too easy or too hard (Sec 3.1). Dr. GRPO removes both terms and keeps reward the same while incorrect responses get much shorter (Fig. 5). Base models already reflect: DeepSeek-V3-Base writes "Aha"/"wait" on MATH500 (Fig. 3). On Qwen2.5-Math, dropping the prompt template improves average accuracy by about 60% over 4-shot prompting (Table 1). Their 7B base recipe reaches 43.3% on AIME 2024.
- Where measured: Qwen2.5(-Math), Llama, DeepSeek-V3-Base (685B) and other base models; MATH500 with R1 template; GRPO vs Dr. GRPO on MATH-level prompts.

### 2503.14476 — DAPO: An Open-Source LLM Reinforcement Learning System at Scale, 2025
- Finding: Progressive ablation on AIME24 avg@32 (Table 1): naive GRPO 30; plus overlong filtering, which masks the loss of truncated samples instead of giving them a punitive reward, 36; clip-higher (ε_high 0.28) 38; soft overlong punishment 41; token-level loss 42; dynamic sampling (drops prompts with accuracy 0 or 1) 50. DeepSeek-R1-Zero-Qwen-32B scores 47. Punishing truncated samples adds reward noise because sound but long reasoning gets penalized (Sec 3.4, Fig. 5).
- Where measured: Qwen2.5-32B base, DAPO-Math-17K, 16 samples per prompt, max 20,480 tokens (16,384 + 4,096 soft cache); evaluation T 1.0, top-p 0.7.

### 2505.22617 — The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models, 2025
- Finding: Without entropy or KL intervention, policy entropy drops sharply in the first steps and validation accuracy follows R = −a·exp(H) + b. That gives a ceiling of −a+b at H=0, fitted with 2 coefficients over 200+ points (Sec 2, Figs. 3–4). Fitting on the first 36 steps predicts the next 200 with RMSE 0.9% on math and 1.2% on code (Fig. 5). Entropy change is driven by the covariance between action log-probability and advantage. Clip-Cov and KL-Cov, which restrict high-covariance tokens, keep entropy up and improve accuracy.
- Where measured: Qwen2.5, Mistral, LLaMA and DeepSeek families, 0.5B–32B, GRPO and other policy-gradient methods on math and code tasks.

### 2505.14216 — Reinforcement Learning vs. Distillation: Understanding Accuracy and Capability in LLM Reasoning, 2025
- Finding: Distillation that adds no knowledge behaves like RLVR. SFT of the base on QwQ-32B solutions, only for questions the base already solves at least once in 256 samples, lifts MATH500 from 60% to 69%. Its pass@k curve converges with the base and even crosses it at large k (Fig. 4). Distillation that brings new knowledge (DeepSeek-R1-Distill) raises both accuracy and coverage: AIME25 pass@256 70.0% vs a base plateau of 56.7% up to pass@512.
- Where measured: Qwen2.5-1.5B-Math (replicated on Qwen2.5-3B, App. A.8); MATH train set (7,500 questions, 256 base samples each); AIME25 and MATH500 pass@k.

### 2507.10532 — Reasoning or Memorization? Unreliable Results of Reinforcement Learning Due to Data Contamination, 2025
- Finding: Given the first 60% of each MATH-500 problem, Qwen2.5-Math-7B regenerates the remaining 40% exactly 54.6% of the time and answers 53.6% of the truncated problems correctly. Llama3.1-8B scores 3.8% and 2.4%; on the post-cutoff LiveMathBench, Qwen's completion rate is 0.0% (Fig. 1). The official chat template lowers Qwen base accuracy, and part of the apparent RL gain is adaptation to that template (Fig. 3–4). On a generated clean arithmetic set (RandomCalculation), only correct rewards improve Qwen2.5-Math-7B. Random rewards make training unstable, and inverted rewards collapse it (Fig. 7).
- Where measured: Qwen2.5(-Math)-7B, Llama3.1-8B(-Instruct); MATH-500, AMC, AIME, LiveMathBench 202505; RLVR on 5-step and 10-step RandomCalculation (700 train / 300 val problems).

### 2505.22203 — From Accuracy to Robustness: A Study of Rule- and Model-based Verifiers in Mathematical Reasoning, 2025
- Finding: Rule-based math verifiers have more than 99% precision, but they miss correct answers written in other forms. Average recall is 86%, 0.78 on Skywork-OR1, and below 0.6 on general science (Fig. 2, App. J). Recall falls as the model being graded gets stronger: long-CoT R1-Distill-7B/32B outputs average 0.92 (Fig. 3). A hybrid that sends rule-rejected answers to a model verifier adds about 3 recall points at more than 98% precision and lifts RL results by 2.3 points (peak 57.3). Some trained model verifiers are hacked during RL, accepting certain patterns as correct (Fig. 4, Table 2).
- Where measured: HuggingFace Math-Verify, Qwen-Math and other rule verifiers on responses from several policy models over common math RL datasets; RL with Qwen2.5 models vs a SimpleRL-Zoo baseline.

### 2109.01903 — Robust fine-tuning of zero-shot models (WiSE-FT), 2021
- Finding: Linearly interpolating weights, (1−α)·θ_zero-shot + α·θ_fine-tuned, improves accuracy on both the target distribution and shifted ones, even though the network is non-linear. At α=0.5, WiSE-FT gains 4–6 points under distribution shift over prior work while raising ImageNet accuracy by 1.6 points (Table 1). It gains 2–23 points on six further shifts. α=0.5 is close to optimal across experiments (App. B).
- Where measured: CLIP ViT models (plus 12 more backbones in App. C), end-to-end fine-tuned on ImageNet; ImageNet-V2/R/Sketch/A/ObjectNet and seven transfer datasets.

### 2212.04089 — Editing Models with Task Arithmetic, 2022
- Finding: A task vector τ = θ_ft − θ_pre, added with a scale λ chosen on validation data, edits behavior. A random vector of the same kind barely changes accuracy. Negating task vectors cuts ViT-L/14 accuracy on 8 target tasks from 64.8 to 19.0 while the control task (ImageNet) moves from 75.5 to 72.9. A random vector leaves targets at 60.9 (ViT-B/32: pre-trained 48.3, negated 24.0, random 45.7; Table 1). Adding task vectors gives multi-task models, and analogies τ_C + (τ_B − τ_A) improve task D with little or no data.
- Where measured: CLIP ViT-B/32, B/16 and L/14 on Cars, DTD, EuroSAT, GTSRB, MNIST, RESISC45, SUN397 and SVHN; also NLP models (T5, GPT-2) in later sections.

### 2207.12598 — Classifier-Free Diffusion Guidance, 2022
- Finding: Mixing conditional and unconditional score estimates with guidance weight w trades sample diversity for per-sample quality, monotonically. On 64×64 ImageNet (p_uncond 0.1), FID is best at a small weight (w=0.1: 1.55 vs 1.8 at w=0). Larger w raises Inception Score steadily (53.71 at w=0, 170.1 at w=1, 260.2 at w=4) while FID worsens (12.6 at w=1, 26.22 at w=4) (Table 1). The best IS needs w ≥ 4; the best FID needs w of 0.1–0.3 (Sec 4).
- Where measured: class-conditional diffusion models on ImageNet 64×64 (400k steps) and 128×128 (2.7M steps), p_uncond 0.1/0.2/0.5, w from 0 to 4.
