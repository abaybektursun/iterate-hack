# Promoted run 01: readout

**The round-04 winner r4-m10-rival (RL's first 100 steps install the opening the cue forces, with no per-token sharpening) stays standing but is not separated from a fresh rival: +1.49 nats on 3 tests (`metrics_v5.json`). 2 of the 3 tests asked for numbers that `facts.json` already held. Review: weak.**

## Hypotheses of `specs/SPEC_promoted01.md`

- P1 holds: `standing` carried r4-m10-rival with its 6 computed round-04 tests (5 inside, 1 outside, +7.81 nats; `metrics_v4.json`); a fresh rival was written (191 s) and 3 of 3 rival tests were computed. Also carried: r4-m08-rival (5 tests, +2.65, state "no gain", so no rival) and r4-m06, r4-m11, r4-m12 (untested).
- P2 holds at its minimum: 2 of 3 tests put the defender's centre outside the rival's interval (tests 1 and 3; on test 2 the centre 0 is inside the rival's [0, 0.10]). No second turn.
- P3 holds: +1.49 is above -2; the state is "not separated from rival", not a win.
- P4 not tested: no duel test reached 1 nat in size (+0.39, +0.81, +0.29), so `replicate` had nothing to recompute. It first crashed at 537adb7 on r4-m06, a carried theory with no tests file; 28db85f skips such theories.

## The fresh rival and its tests (`rivals/r4-m10-rival.json`, scripts `rivals/r4-m10-rival/p1-p3.py`)

Rival: 3.1's truncation-as-negative reward prunes the T 0.6 / top-p 0.95 loop hazard from the first steps, so cap hits fall steadily in log steps (cued base about 0.24, step 100 about 0.19, step 400 about 0.15, step 2,800 about 0.03) instead of staying at the cued-base level through step 400. On all 3 tests the measured value is inside both intervals; the gain comes from where the intervals sit.

| Test (plain prompt, T 0.6 / top-p 0.95, sample 0) | n | Measured [90 %] | Theory (defender) | Rival | Gain |
|---|---|---|---|---|---|
| 1. Cap-hit rate of step 400, MATH-500 | 500 | 0.196 [0.166, 0.226] | 0.235 [0.165, 0.305] | 0.15 [0.10, 0.20] | +0.39 |
| 2. Cap-hit rate step 100 minus step 400, paired, MATH-500 | 500 | +0.010 [-0.020, 0.040] | 0 [-0.05, 0.05] | 0.05 [0, 0.10] | +0.81 |
| 3. Step 400 minus cued base, paired, 400-problem hard set | 400 | -0.0475 [-0.0875, -0.0075] | -0.01 [-0.09, 0.07] | -0.10 [-0.18, -0.02] | +0.29 |

## Tests that asked for numbers already in `facts.json`

- Test 1: `facts.json` entry 25 (0-based; round-04 r4-m10, "Paired cap-hit rate difference, RL step 400 minus base", 0.066) plus the plain base's 65 of 500 (0.130, in the theory's statement) gives 0.196, the measured value (98 of 500).
- Test 2: entry 24 ("RL step 100 minus base", 0.076) minus entry 25 (0.066) gives 0.010, the measured value.
- Test 3 is not there: entry 26 is step 400 minus the plain base on the clean 328 (0.070), a different pair and problem set.

## Review (`reviews/r4-m10-rival.json`) and the state of the mechanism

Verdict weak. 6.0 of the 7.81 offline nats rest on one measurement (step 400's per-token log-prob equals the cued base's, p5 and p6), which Wang et al. 2610.06851 already implies (base and RL next-token distributions agree after the first two positions; prefilling the cue matches about 100 RL steps). The theory's own addition, cap hits flat at the cued-base level until late truncation-negative training, was fitted to step-100 and step-400 counts it had seen, and those counts sit below the cued base (103 and 98 against 119 of 500; test 3 excludes 0), as the rival says. State now: the opening-install part stands and is published; the cap-hit trajectory part is strained in level and untested in timing. The test that separates the two is plain T 0.6 cap hits at a checkpoint between steps 800 and 1,600 (theory about 0.20, rival 0.08 to 0.10).
