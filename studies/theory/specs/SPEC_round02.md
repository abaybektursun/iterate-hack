# Round 02: score a theory on its own claims, with its reversal as control

Written before the run (2026-11-15). Round 01's score (does a theory help a Sonnet predictor on all 58 targets) did not
separate real theories from a planted reversed one. Round 02 changes the instrument and keeps the split: cutoff
2026-11-14T23:42:26 UTC, the same as round 01, so the two scores can be compared on the same held-out items.

## Changes

1. **Score.** The author of a theory, after its file is fixed (sha256 recorded by the coordinator before the author sees
   the blind targets), states a value and an interval for each held-out target the theory speaks about. A claim is
   divergent when both no-theory agents (model opus) lie outside the interval. win = divergent and measured inside;
   loss = divergent and measured outside. `lib/v2.py score`.
2. **Control.** A candidate (wins >= 2 and wins > losses) is reversed by a fresh agent (model opus), which states the
   reversed theory's claims for the same targets. The theory passes only if its net is above its reversal's net.
3. **External findings.** One agent retrieves published findings by mechanism (`external.md`; paper sources only, no
   board item). Each new theory imports at least one mechanism from it that no item in `before.jsonl` cites.
4. **Standing theories.** The six round-01 theories enter unchanged (`theories/r1-*.json`); their round-01 authors state
   their claims. Five new generators (all, surprises, across, external, revise) write two theories each
   (`theories/r2-*.json`); `revise` starts from the round-01 theories.

## Hypotheses

- H1: the new score separates theories. Refuted if no theory is a candidate, or every candidate's reversal scores as
  well as the candidate.
- H2: importing external mechanisms yields theories that pass. Refuted if no passing theory has an import that carries
  one of its winning claims (read in the theory file by the reviewer).
- H3: the round-01 theories with predictions inside their intervals (all-2, across-2) are candidates under the new
  score. Refuted if they are not.

## Known limits, fixed before the run

- The held-out items are the ones round 01 used. The coordinator has seen them; generators, nulls and reversal agents
  have not. The coordinator writes no theory, claim or target.
- The round-01 authors state claims for theories they wrote 90 minutes ago; their context holds no held-out number.
- Thresholds (wins >= 2, both nulls outside the interval) are chosen here, before any claim exists.
