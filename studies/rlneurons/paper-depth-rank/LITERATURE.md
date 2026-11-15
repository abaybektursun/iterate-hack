# Prior work for "rank and depth split of the RL update" (paper-depth-rank)

Read on 2026-11-15 from arxiv.org/html (full text, with appendices where the page served them). Quotes are exact
sentence fragments from the HTML. Where a page was cut off before an appendix, that is noted. Every arXiv id
below resolves to the title given.

Claim under test: in Olmo 3 RL-Zero-Math 7B, the RL update (RL minus base, per matrix, SVD) has (a) singular
direction 1, which changes how often answers finish inside the token limit without adding right answers, and
(b) directions 2-8, which add right answers while keeping cut-offs at base level. By depth on math, layers 0-10
add right answers and cut-offs, and layers 22-31 only remove cut-offs. A random rank-8 edit does nothing. The
depth split does not replicate on an RL-on-code pair.

## Closest prior work

### 1. Cai et al. 2510.00553, rank-1 recovers RL gains (closest on the rank claim; this is the source to argue against)
- Title: On Predictability of Reinforcement Learning Dynamics for Large Language Models
- Authors: Yuchen Cai, Ding Cao, Xin Xu, Zijun Yao, ... Junfeng Fang. 2025 (ICLR 2026).
- Shows: Abstract: the top singular subspace "nearly fully determines reasoning improvements, recovering over 99% of
  performance gains." Sec. 2.2: "even a single Rank-1 Subspace is sufficient to recover performance close to that of
  the fully trained model." Sec. 2.2 also says that "several subspaces associated with relatively large singular
  values ... still contribute substantially to reasoning improvements." Sec. 3.2: "MLP modules, particularly those
  in mid-to-high layers, tend to achieve higher" R^2 of the linear trajectory. No length or termination analysis.
- Relation: contradicts in part. They put the accuracy gain in direction 1. We find direction 1 changes finishing
  and not accuracy, and directions 2-8 carry the accuracy. Our paper must say this directly and give possible
  reasons: a different model (Olmo 7B, RL-Zero), a token limit that turns finishing into accuracy, and their scoring.
```bibtex
@article{cai2025predictability,
  title={On Predictability of Reinforcement Learning Dynamics for Large Language Models},
  author={Cai, Yuchen and Cao, Ding and Xu, Xin and Yao, Zijun and Huang, Yuqing and Tan, Zhenyu and Zhang, Benyi and Sun, Guangzhong and Liu, Guiquan and Fang, Junfeng},
  journal={arXiv preprint arXiv:2510.00553},
  year={2025}
}
```

### 2. RELEX, 2605.21468 (id OK)
- Title: You Only Need Minimal RLVR Training: Extrapolating LLMs via Rank-1 Trajectories
- Authors: Zhepei Wei, Xinyu Zhu, Wei-Lin Chen, Chengsong Huang, Jiaxin Huang, Yu Meng. 2026.
- Shows: Abstract: "the majority of downstream performance gains are captured by a rank-1 approximation of the
  parameter deltas." Sec. 3.1 (Finding 1): "a single component per tensor accounts for nearly all task-relevant
  change." Sec. 4.3 / Fig. 5: "Component 1 alone accounts for 81.4% of the variance". Components 2-5 are
  "lower-variance, noisier, and less monotonic." Accuracy is the only metric (MATH and OOD). There is no length or
  cut-off measurement and no per-layer study (Fig. 4 shows only representative modules).
- Relation: contradicts in part, the same way as Cai et al. It is also background for SVD of the per-tensor delta.
```bibtex
@article{wei2026relex,
  title={You Only Need Minimal {RLVR} Training: Extrapolating {LLMs} via Rank-1 Trajectories},
  author={Wei, Zhepei and Zhu, Xinyu and Chen, Wei-Lin and Huang, Chengsong and Huang, Jiaxin and Meng, Yu},
  journal={arXiv preprint arXiv:2605.21468},
  year={2026}
}
```

### 3. Ye et al. 2605.06523, rank-1 as a switch (id OK)
- Title: On the Implicit Reward Overfitting and the Low-rank Dynamics in RLVR
- Authors: Hao Ye, Jisheng Dang, Junfeng Fang, ... Tat-Seng Chua. 2026.
- Shows: Sec. 3.2: "a dominant Rank-1 direction acts as a switch to activate reasoning capabilities". Sec. 3.1:
  "non-rank-1 components in RLVR play a crucial role in preserving" non-reasoning abilities. Sec. 3.2: they are
  "responsible for safety, robustness, and subtle feature alignment". App. C: "deep layers(near the output side)
  tend to have clearer pattern" in the spectrum. There is no length, EOS or termination test. The "switch"
  evidence comes mostly from prior work and OOD evals (Table 1).
- Relation: partly overlaps, because it also assigns different roles to direction 1 and to the other directions.
  The roles are opposite to ours: they give accuracy to direction 1 and general abilities to the rest. We give
  finishing to direction 1 and accuracy to directions 2-8, and we measure both with a matched random control.
```bibtex
@article{ye2026implicit,
  title={On the Implicit Reward Overfitting and the Low-rank Dynamics in {RLVR}},
  author={Ye, Hao and Dang, Jisheng and Fang, Junfeng and Wang, Bimei and Zhang, Yizhou and Lv, Ning and Zhang, Wencan and Peng, Hong and Hu, Bin and Chua, Tat-Seng},
  journal={arXiv preprint arXiv:2605.06523},
  year={2026}
}
```

### 4. Zheng et al. 2605.28751, behaviour carried by middle layers, code RL (id OK; not a math paper)
- Title: Correctness vs Efficiency: Behavior Control with Weight-Space Extrapolation in Code RL
- Authors: Kunhao Zheng, Pierre Chambon, Jade Decugis, Jonas Gehring, Taco Cohen, Benjamin Negrevergne, Gabriel Synnaeve. 2026.
- Shows: Two code-RL checkpoints are interpolated or extrapolated in weight space to trade correctness failures
  against resource-limit failures (timeouts, memory). Here "efficiency" means the efficiency of the generated
  code, not response length. Sec. 3.3: at extreme coefficients "format errors rise sharply, mostly through token
  exhaustion." App. D.1: "No component type is low-rank". The "top 10 singular values of each layer's difference
  explain only 10 to 19% of variance." App. D.3 (layer stitching, Fig. 29-30): "The first and last quarter of
  layers (0 to 15 and 48 to 63) are nearly inert." and "The middle layers carry the full behavioral shift."
- Relation: partly overlaps, because it is a depth split of a weight difference into a behaviour. The difference
  is between two RL runs, not RL minus base. The behaviour is code efficiency against correctness, not finishing
  inside the token limit. They find the middle layers matter, while we find early layers for accuracy and late
  layers for cut-offs. Their delta is high-rank, which supports our observation that a code pair behaves
  differently.
```bibtex
@article{zheng2026correctness,
  title={Correctness vs Efficiency: Behavior Control with Weight-Space Extrapolation in Code {RL}},
  author={Zheng, Kunhao and Chambon, Pierre and Decugis, Jade and Gehring, Jonas and Cohen, Taco and Negrevergne, Benjamin and Synnaeve, Gabriel},
  journal={arXiv preprint arXiv:2605.28751},
  year={2026}
}
```

### 5. Zhang et al. 2607.01232, one layer can match full RL
- Title: Is One Layer Enough? Training A Single Transformer Layer Can Match Full-Parameter RL Training
- Authors: Zijian Zhang, Rizhen Hu, Athanasios Glentis, Dawei Li, Chung-Yiu Yau, Hongzhou Lin, Mingyi Hong. 2026.
- Shows: Intro: "high-contribution layers concentrate in the middle of the transformer stack". Sec. 3.2: "Across
  all three model scales, middle layers consistently exhibit higher contribution." Training layer 0 alone on
  Qwen3-8B-Base "exhibits a negative contribution". Accuracy only, with no length or truncation measurement and
  no SVD. App. C was cut off in the HTML read.
- Relation: background or partial. They train one layer at a time and do not slice the delta. They give no
  behavioural split by depth.
```bibtex
@article{zhang2026onelayer,
  title={Is One Layer Enough? Training A Single Transformer Layer Can Match Full-Parameter {RL} Training},
  author={Zhang, Zijian and Hu, Rizhen and Glentis, Athanasios and Li, Dawei and Yau, Chung-Yiu and Lin, Hongzhou and Hong, Mingyi},
  journal={arXiv preprint arXiv:2607.01232},
  year={2026}
}
```

## Other relevant work

### Zhu et al. 2511.08567, The Path Not Taken (id OK)
- Title: The Path Not Taken: RLVR Provably Learns Off the Principals. Authors: Hanqing Zhu, Zhenyu Zhang, Hanxian
  Huang, ..., Kai Sheng Tai. 2025.
- Shows: Sec. 4.2: "RL updates exhibit a sub-random overlap with principal weights, indicating a strong tendency to
  avoid them." Fig. 4: "RLVR maintains a stable top-k spectrum with minimal subspace rotation, unlike SFT." These
  are the singular directions of W, not of the delta. There is no ablation by behaviour or by singular direction.
- Relation: background.
```bibtex
@article{zhu2025path,
  title={The Path Not Taken: {RLVR} Provably Learns Off the Principals},
  author={Zhu, Hanqing and Zhang, Zhenyu and Huang, Hanxian and Su, DiJia and Liu, Zechun and Zhao, Jiawei and Fedorov, Igor and Pirsiavash, Hamed and Sha, Zhizhou and Lee, Jinwon and Pan, David Z. and Wang, Zhangyang and Tian, Yuandong and Tai, Kai Sheng},
  journal={arXiv preprint arXiv:2511.08567},
  year={2025}
}
```

### GeoRA 2601.09361 (id OK)
- Title: GeoRA: Geometry-Aware Low-Rank Adaptation for RLVR. Authors: Jiaying Zhang, Lei Shi, Jiguo Li, et al. 2026.
- Shows: Sec. 5.2: "the effective RLVR update space is not isotropic, but already structured and highly
  compressible". The full-fine-tuning delta has "a similarly compressible heavy-tailed spectrum". No per-direction
  behaviour.
- Relation: background (the RLVR delta has low effective rank).
```bibtex
@article{zhang2026geora,
  title={{GeoRA}: Geometry-Aware Low-Rank Adaptation for {RLVR}},
  author={Zhang, Jiaying and Shi, Lei and Li, Jiguo and Xu, Jun and Gao, Jiuchong and Hao, Jinghua and He, Renqing},
  journal={arXiv preprint arXiv:2601.09361},
  year={2026}
}
```

### Deng et al. 2605.25189, directional alignment and reward hacking
- Title: Directional Alignment Mitigates Reward Hacking in Reinforcement Learning for Language Models. Authors:
  Wenlong Deng, Jiaji Huang, Kaan Ozkara, Yushu Li, Christos Thrampoulidis, Xiaoxiao Li, Youngsuk Park. 2026.
- Shows: Intro: "a large fraction of the performance gain is captured by the leading singular direction of the
  parameter update matrix". App. A.2: "those weaker components are less stable than the leading one." No length
  analysis, and no test of whether separate directions give separate behaviours.
- Relation: background. It repeats the received view that direction 1 carries the gain.
```bibtex
@article{deng2026directional,
  title={Directional Alignment Mitigates Reward Hacking in Reinforcement Learning for Language Models},
  author={Deng, Wenlong and Huang, Jiaji and Ozkara, Kaan and Li, Yushu and Thrampoulidis, Christos and Li, Xiaoxiao and Park, Youngsuk},
  journal={arXiv preprint arXiv:2605.25189},
  year={2026}
}
```

### LiNeS 2410.17146 (id OK)
- Title: LiNeS: Post-training Layer Scaling Prevents Forgetting and Enhances Model Merging. Authors: Ke Wang, Nikolaos
  Dimitriadis, Alessandro Favero, Guillermo Ortiz-Jimenez, François Fleuret, Pascal Frossard. 2024.
- Shows: Sec. 3: "we hypothesize that updates to the shallow layers contribute minimally to target tasks". It also
  says shallow updates "distort the general features learned during pre-training". This is vision and
  classification fine-tuning, not RL.
- Relation: background. It is a depth split of a task vector into two behaviours (task skill and forgetting). In
  our math result the target task gain sits in the shallow layers (0-10), the opposite of LiNeS.
```bibtex
@article{wang2024lines,
  title={{LiNeS}: Post-training Layer Scaling Prevents Forgetting and Enhances Model Merging},
  author={Wang, Ke and Dimitriadis, Nikolaos and Favero, Alessandro and Ortiz-Jimenez, Guillermo and Fleuret, Fran{\c{c}}ois and Frossard, Pascal},
  journal={arXiv preprint arXiv:2410.17146},
  year={2024}
}
```

### Reasoning vectors 2509.01363 (id OK)
- Title: Reasoning Vectors: Transferring Chain-of-Thought Capabilities via Task Arithmetic. Authors: Mohammad Zbeeb,
  Hasan Abed Al Kader Hammoud, Bernard Ghanem. 2025.
- Shows: The GRPO-minus-SFT vector "captures the reasoning capability instilled by reinforcement learning"
  (Abstract). It is applied whole, with no layer or spectral analysis and no length measurement. Sec. 4.1: "We
  report results from a single run for each experiment."
- Relation: background.
```bibtex
@article{zbeeb2025reasoning,
  title={Reasoning Vectors: Transferring Chain-of-Thought Capabilities via Task Arithmetic},
  author={Zbeeb, Mohammad and Hammoud, Hasan Abed Al Kader and Ghanem, Bernard},
  journal={arXiv preprint arXiv:2509.01363},
  year={2025}
}
```

### Task arithmetic 2212.04089 (id OK)
- Title: Editing Models with Task Arithmetic. Authors: Gabriel Ilharco, Marco Tulio Ribeiro, Mitchell Wortsman, et
  al. 2022 (ICLR 2023). Abstract: "Negating a task vector decreases performance on the target task, with little
  change in model behavior on control tasks." Relation: background (fine-tuned minus base as an object).
```bibtex
@article{ilharco2022editing,
  title={Editing Models with Task Arithmetic},
  author={Ilharco, Gabriel and Ribeiro, Marco Tulio and Wortsman, Mitchell and Gururangan, Suchin and Schmidt, Ludwig and Hajishirzi, Hannaneh and Farhadi, Ali},
  journal={arXiv preprint arXiv:2212.04089},
  year={2022}
}
```

### LoRA 2106.09685 (id OK)
- Title: LoRA: Low-Rank Adaptation of Large Language Models. Authors: Edward J. Hu, Yelong Shen, Phillip Wallis,
  Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen. 2021. Abstract: "an empirical investigation into
  rank-deficiency in language model adaptation". Sec. 4.1 states the hypothesis that the weight change during
  adaptation has a low "intrinsic rank". Relation: background.
```bibtex
@article{hu2021lora,
  title={{LoRA}: Low-Rank Adaptation of Large Language Models},
  author={Hu, Edward J. and Shen, Yelong and Wallis, Phillip and Allen-Zhu, Zeyuan and Li, Yuanzhi and Wang, Shean and Wang, Lu and Chen, Weizhu},
  journal={arXiv preprint arXiv:2106.09685},
  year={2021}
}
```

### Intruder dimensions 2410.21228 (id OK)
- Title: LoRA vs Full Fine-tuning: An Illusion of Equivalence. Authors: Reece Shuttleworth, Jacob Andreas, Antonio
  Torralba, Pratyusha Sharma. 2024.
- Shows: Sec. 1: "fully fine-tuned models remain spectrally similar to the pre-trained model and do not contain
  intruder dimensions." Sec. 5 / Fig. 8: scaling the top intruder direction down reduces forgetting while barely
  changing test accuracy. This is one singular direction separated from task accuracy by behaviour, but for LoRA
  and for the singular vectors of W_tuned, not of the delta.
- Relation: background. It is the nearest precedent for "one direction, a different behaviour than accuracy".
```bibtex
@article{shuttleworth2024lora,
  title={{LoRA} vs Full Fine-tuning: An Illusion of Equivalence},
  author={Shuttleworth, Reece and Andreas, Jacob and Torralba, Antonio and Sharma, Pratyusha},
  journal={arXiv preprint arXiv:2410.21228},
  year={2024}
}
```

### Weight-diff interpretability: WeightWatch 2508.00161
- Title: Watch the Weights: Unsupervised monitoring and control of fine-tuned LLMs. Authors: Ziqian Zhong, Aditi
  Raghunathan. 2025 (ICLR 2026).
- Shows: Sec. 3: "the principal directions of the weight difference ΔW encode key capabilities introduced during
  fine-tuning". Sec. 6.2 labels individual directions with different themes (refusal, math, emoji). The study uses
  activations along the directions. There are no RL reasoning models and no length analysis.
- Relation: partly overlaps. Different delta directions carry different behaviours, but in chat and backdoor
  models, read from activations, and without a weight-ablation behavioural readout of finishing against accuracy.
```bibtex
@article{zhong2025watch,
  title={Watch the Weights: Unsupervised Monitoring and Control of Fine-tuned {LLMs}},
  author={Zhong, Ziqian and Raghunathan, Aditi},
  journal={arXiv preprint arXiv:2508.00161},
  year={2025}
}
```

### Length as a direction: ThinkEdit 2503.22048
- Title: ThinkEdit: Interpretable Weight Editing to Mitigate Overly Short Thinking in Reasoning Models. Authors:
  Chung-En Sun, Ge Yan, Tsui-Wei Weng. 2025.
- Shows: "reasoning length is governed by a linear direction in the representation space". "the middle layers play
  a key role in regulating reasoning length". Editing 0.2% of weights (the o_proj of short-reasoning heads) gives
  "+3.34%" overall accuracy.
- Relation: partly overlaps. Length is a direction, but in activations of a distilled reasoning model, not in the
  RL weight delta. It also does not separate finishing from accuracy.
```bibtex
@article{sun2025thinkedit,
  title={{ThinkEdit}: Interpretable Weight Editing to Mitigate Overly Short Thinking in Reasoning Models},
  author={Sun, Chung-En and Yan, Ge and Weng, Tsui-Wei},
  journal={arXiv preprint arXiv:2503.22048},
  year={2025}
}
```

### Layer importance invariant after post-training 2506.22638
- Title: Layer Importance for Mathematical Reasoning is Forged in Pre-Training and Invariant after Post-Training.
  Authors: Aadim Nepal, Safal Shrestha, Anubhav Shrestha, Minwu Kim, Jalal Naghiyev, Ravid Shwartz-Ziv, Keith Ross. 2025.
- Shows: Sec. 3.1: "instruction tuning, distillation, and RLVR do not shift which layers are essential". The study
  ablates layers of the model, not the delta.
- Relation: background.
```bibtex
@article{nepal2025layer,
  title={Layer Importance for Mathematical Reasoning is Forged in Pre-Training and Invariant after Post-Training},
  author={Nepal, Aadim and Shrestha, Safal and Shrestha, Anubhav and Kim, Minwu and Naghiyev, Jalal and Shwartz-Ziv, Ravid and Ross, Keith},
  journal={arXiv preprint arXiv:2506.22638},
  year={2025}
}
```

### Wang et al. 2610.06851, the cue paper (id OK)
- Title: Base Models Can Reason By Taking a Cue From Training Data. Authors: Sophie L. Wang, Amil Dravid, Rulin Shao,
  Kevin Farhat, Sewon Min, Alexei A. Efros. 2026.
- Shows: Abstract: "RL makes these cues more likely, while fixing them recovers much of its performance gain over
  the base model." Sec. 2.3: cue probability rises "from 0.14 to 0.65 in Olmo-3-7B", and "KL peaks within the first
  two positions." Sec. 2.2: the cue "raises Olmo-3-7B's MATH-500 pass@1 from 42% to 78%, compared with 75% after
  RL." Sec. 2.4: the cue increases "mean response length from 4.8k to 6.7k tokens". Also: "Longer generation alone
  is therefore insufficient to explain why some openings improve accuracy." The budget is 31,744 tokens. The paper
  does not report cut-off rates by component.
- Relation: background for what RL changes in the same Olmo model, measured in behaviour, not in weights.
```bibtex
@article{wang2026base,
  title={Base Models Can Reason By Taking a Cue From Training Data},
  author={Wang, Sophie L. and Dravid, Amil and Shao, Rulin and Farhat, Kevin and Min, Sewon and Efros, Alexei A.},
  journal={arXiv preprint arXiv:2610.06851},
  year={2026}
}
```

### Olmo 3 2512.13961 (id OK)
```bibtex
@article{olmo2025olmo3,
  title={Olmo 3},
  author={{Team Olmo} and Ettinger, Allyson and others},
  journal={arXiv preprint arXiv:2512.13961},
  year={2025}
}
```

## Ids checked
All ids in the brief resolve to the papers named: 2605.21468, 2605.06523, 2605.28751, 2511.08567, 2601.09361,
2410.17146, 2509.01363, 2212.04089, 2106.09685, 2410.21228, 2610.06851, 2512.13961. Three of them differ from the
brief's description:
- 2605.28751 is about code RL, and its weight difference is between two RL checkpoints at different behaviour
  settings, not RL minus base. Its "efficiency" is the generated code's timeouts and memory, not response length.
- 2605.06523 does not test what the rank-1 switch does to length or termination. Its "switch" is about reasoning
  accuracy.
- The rank-1 paper the brief did not list, 2510.00553 (Cai et al.), is the strongest source for "rank-1 carries
  the gain" and should be cited.

## Verdicts: is the claim published?
1. Rank split (directions 2-8 carry accuracy and direction 1 does not): **not published, and it contradicts the
   published view.** Cai et al. 2510.00553, RELEX 2605.21468, Ye et al. 2605.06523 and Deng et al. 2605.25189 all
   put the accuracy gain in direction 1. Ye et al. give directions 2+ non-reasoning roles (safety, robustness).
2. Direction 1 = finishing inside the token limit: **not published.** No paper measures length, EOS or the cut-off
   rate for any singular direction of an RL delta. Length directions exist only in activations (ThinkEdit), and
   none of these papers separates finishing from accuracy.
3. Depth split (math: layers 0-10 add accuracy and cut-offs, layers 22-31 only remove cut-offs): **not published.**
   The closest papers say the middle layers carry the behaviour: Zheng et al. 2605.28751 (code-RL layer stitching,
   one behaviour axis), Zhang et al. 2607.01232 (single-layer training, accuracy only) and ThinkEdit (length).
   LiNeS places task skill in the deep layers. None splits accuracy and finishing by depth.
4. Cross-pair failure (the depth split does not hold on RL-on-code): **not published as such.** It agrees with
   Zheng et al.: in code RL the delta is high-rank (App. D.1) and the behaviour sits in the middle layers (App. D.3).

## Novelty statement (honest, 2 sentences)
Prior work reports that the top singular direction of an RLVR weight update recovers most of the accuracy gain.
Here, scoring finishing inside the token limit separately from correctness and comparing against a matched random
rank-8 edit, we find that in Olmo 3 RL-Zero-Math 7B direction 1 mainly changes how often the model finishes, while
directions 2-8 add right answers. We also find that early and late layers split accuracy from cut-off removal, a
depth split that did not replicate on an RL-on-code pair.
