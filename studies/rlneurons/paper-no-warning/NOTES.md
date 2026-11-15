# Notes for the "no early warning" paper (data layer)

`uv run --no-project --with numpy --with math-verify==0.9.0 python studies/rlneurons/paper-no-warning/build_facts.py` (22 s) writes `facts.json` and `examples.json`. It reads only files in git; 64 checks against stored readouts pass (`checks_against_readouts`). Not committed.

## Definitions
- AUROC, every instrument: share of (right sample, wrong sample) pairs the instrument ranks correctly, ties 0.5, orientation fixed before looking. **Across** = pairs of any two samples, pooled; **within** = pairs of two samples of one problem. Target: `score_v3` (the probe readout also has the label-free flag as target).
- Intervals: bootstrap over problems, 2,000 resamples, seed 0 (within: over the problems that have a pair, as `analysis/critic_probe.py`). Ceilings: paired bootstrap, 10,000 resamples, in points.
- Agreement flag: the sample finished and its answer is in the largest group of agreeing answers of the 4 samples, group of 2 or more (`critic_ceiling.plurality_flags`). Equals correctness on 96.5 % of base samples.
- "Length so far at t" = min(tokens, t): at t one knows only whether the sample has ended, and when.

## Arms (`facts.json` `arms`)
- Base + cue: `allenai/Olmo-3-1025-7B` @ a81bae42, prefix `' line!\n\nOkay'` (3 tokens), T 1.0 / top-p 1.0, cap 16,384, grader v3, 4 samples, attempt 0. MATH-500 (500) job `-153825-208b`; hard328 (328) job `-200457-e8e6`. RL: `allenai/Olmo-3.1-7B-RL-Zero-Math` @ 364820b0, plain prompt, same sampling.
- Probe: the base re-reads its 2,000 MATH-500 samples; residual stream of layers 12, 20, 28 at the last prompt token and after 250 / 500 / 1,000 / 2,000 answer tokens; logistic regression, 5 folds by problem, trained on the agreement flag. Copied from `results/critic/probe-02/metrics.json`: activations and per-sample scores are not in git.
- Text signs of the drift study: **Think-SFT + cue on hard328 + fresh2026**, tokens 4,000 / 8,000 / 12,000. Not the base, not MATH-500. Copied (texts not in git).
- Recomputed here on the base: length, cap hit, rule-A loop, agreement (from `rows.jsonl`); zlib ratio, "wait", restart phrases on the first 1,000 / 3,000 / 6,000 characters (`data/wrongstep/base_cue_answer_heads_v1.jsonl.gz`, 6,000 characters = about 2,000 tokens).

## Headline, MATH-500 base + cue (2,000 samples, 1,642 right; 150 problems with both outcomes, 478 pairs)
| Instrument | Across | Within [95 %] | problems / pairs |
|---|---|---|---|
| Difficulty alone: RL's solve rate / base's other 3 samples | 0.759 / 0.801 | 0.5 by construction | 150 / 478 |
| Probe at the last prompt token, L12 / L20 / L28 (copied, no interval) | 0.731 / 0.765 / 0.766 | 0.500 exactly | 150 / 478 |
| Probe L12 after 1,000 tokens, target flag (the spec's number) | 0.668 | 0.571 [0.509, 0.634] | 110 / 340 |
| Same probe, target correctness (not in the README table) | 0.683 | **0.585 [0.525, 0.645]** | 125 / 373 |
| Mean entropy / log-prob so far, 250 tokens (flag) | 0.640 / 0.627 | 0.566 [0.508, 0.626] / 0.555 | 137 / 445 |
| Lowest tenth of problem dependence, 1,000 tokens (copied) | - | 0.575 [0.516, 0.637] | 150 / 478 |
| zlib ratio, first 6,000 characters (recomputed) | 0.596 | 0.564 [0.497, 0.629] | 104 / 305 |
| Length so far at token 1,000 / 2,000 | 0.617 / 0.725 | 0.497 / 0.521 [0.484, 0.557] | 150 / 478 |
| **Length so far at token 4,000 / 8,000 / 12,000** | 0.797 / 0.827 / 0.839 | **0.572 [0.523, 0.619] / 0.625 [0.570, 0.679] / 0.662 [0.602, 0.718]** | 150 / 478 |
| Did not hit the cap | 0.624 | 0.576 [0.553, 0.603] | 150 / 478 |
| **Length at the end (shorter = right)** | 0.842 | **0.680 [0.620, 0.738]** (0.735 among samples past 1,000 tokens) | 150 / 478 |
| **Agreement with the other 3 samples** | 0.932 | **0.893 [0.855, 0.929]** | 150 / 478 |
| Think-SFT, zratio at 12,000 (copied; best of 18 text cells) | 0.623 | 0.568 [0.480, 0.657] | 77 / 213 |

Same pattern on hard328 base + cue (105 / 342): length at the end 0.648 [0.578, 0.716], at 12,000 0.614, at 4,000 0.535 [0.494, 0.575], agreement 0.828; RL MATH-500 (57 / 188): end 0.755, agreement 0.883.

## Ceilings (MATH-500, right of 500; `ceiling_math500`, `ceiling_hard328`)
- Base one sample 410.5 (4,008 tokens); shortest finished of 4: 434; vote over 4: 446; perfect critic over 2 / 3 / 4 samples: 450.3 / 461.0 / 467 (16,034 tokens). RL one sample 460.0 (4,687 tokens), vote 474, pass@4 482.
- Perfect critic over 4 minus RL one sample **+1.40 points [-0.05, +2.85]**; over 3: +0.20 [-1.15, +1.55]; over 2: **-1.93 [-3.33, -0.62]**; vote minus RL -2.80 [-4.7, -1.0]; base pass@4 minus RL pass@4 -3.0 [-4.8, -1.4]. Stop-and-restart with a perfect critic at token 1,000: 459.2 at 4,013 tokens (answer key), 438.7 (agreement flag).
- hard328: base pass@4 207 against RL one sample 200.0, +2.13 [-0.99, +5.18]; against RL pass@4 240, -10.1 [-14.0, -6.4].
- The vote takes 63 % of the room between one sample and pass@4, the shortest sample 42 %.

**Power.** Within-problem half-widths are 0.06 to 0.09 (probe 0.063 at 340 pairs; drift 0.089 at 213 pairs). Largest AUROC not excluded: 0.634 (probe, flag), 0.645 (probe, correctness), 0.657 (zratio). A true AUROC near 0.62 would be found about half the time; nothing here can tell 0.50 from 0.57.

## Does the thesis survive? In part. Threats, strongest first
1. **"Not which attempt" is false at the end of the answer.** Agreement orders attempts of one problem at 0.893, final length at 0.680, and both are label-free. The claim holds only for *early, single-sample* instruments, and must say so.
2. **A trivial instrument equals the best probe.** "Has it finished by token 4,000" scores 0.572 [0.523, 0.619] within problem, interval above 0.5; the probe's 0.571 is no better than a token counter. By 8,000 tokens length gives 0.625. The failure is "early" (first 2,000 tokens: 0.50 to 0.52), not "within problem" as such.
3. **"≈ 0.57" is a best-of-many, and it is not null.** 0.571 is the maximum of 12 probe cells (interval above 0.5); the same probe against correctness gives 0.585 [0.525, 0.645] and 0.564 [0.507, 0.623] at 500 tokens; low-decile problem dependence 0.575 [0.516, 0.637]. Honest wording: a weak signal (0.55 to 0.59) exists; an AUROC above 0.66 is excluded.
4. **The 0.73 to 0.77 across-problem probe is weaker than difficulty alone** (RL's solve rate 0.759, the base's other samples 0.801, final length 0.842) and has no stored interval. It shows the probe reads difficulty, nothing more.
5. **"A perfect critic matches RL" needs 4 samples** (16,034 tokens against RL's 4,687). With 2 samples it is 1.9 points below RL. RL given the same critic is 3.0 points ahead (10.1 on hard328). The stop-and-restart figure 459.2 at 4,013 tokens assumes a perfect verdict at token 1,000.
6. **The 0.57 text number is another model and set** (Think-SFT, hard328 + fresh2026). On the base the control tops at 0.548; for RL one of 18 control cells is above 0.5 (zratio at 12,000: 0.643 [0.539, 0.744]).

## Caveats found
- Post hoc: `probe-02` replaced `probe-01` after the flag was redefined (string match -> grouped answers) and the C grid changed; the "best layer" per row is picked after scoring; the drift spec was written after its instrument checks; the head text signs and the length-so-far rows are defined in this script, not in a spec; `v3-stated` (self-review) is a post-hoc grader.
- Self-review: the base fixes 7 of 63 wrong finished drafts (6 are format repairs by the README's hand read) and breaks 2; RL fixes 0 of 35 and breaks 3. Forced commit at 8,000 tokens: +0.2 points on MATH-500, -3.7 [-6.4, -1.2] on hard328. Stop rule on text signs: 0.8 % and 1.1 % of tokens saved. The entropy-gate section holds no within-problem instrument.
- Instrument checks of this script: a problem-level score gives exactly 0.5 within; a planted sign 0.762; length shuffled within problems 0.491 [0.433, 0.551].
- README numbers that do not match the readouts: "110 to 137 problems have both outcomes" (critic section) is 92 to 137 (92 at 2,000 tokens). The critic table's "RL, one sample 456" and the vote section's "-2.0 [-4.0, 0.2]" use RL sample 0; the 4-sample mean is 460.0 and -2.80 [-4.7, -1.0]. Everything else compared reproduces.
- Could not be recomputed (copied): every probe, log-prob, entropy and problem-dependence AUROC, all drift signs, any interval for a pooled probe AUROC.
- **Not shown by the data:** nonlinear or multi-position probes; activations past 2,000 tokens or of the RL model; a critic that reads the finished answer; any set beyond MATH-500, hard328, fresh2026; a live stop-and-restart run (all policies are replays on stored samples).

**Example (`examples.json`):** MATH-500 problem 1 (gold `p - q`), base + cue: sample 0 right (`p - q`, 4,280 tokens, probe score 1.248, agrees), sample 1 wrong (`2(p - q)`, 5,285 tokens, probe 1.166, does not agree). The probe orders this pair correctly; so does length.
