# Round 05: version 5.1 unchanged, fresh held-out items, second coordinator

Written before the run (2026-11-15, frustea). Code: `lib/round.py` at commit 33b083f (version 5.1, owner abaybektursun);
this round changes no code. Cutoff 2026-11-15T04:29:33, one second after the newest item round 04 held out
(result-5da8a9), so every item an earlier round scored on is evidence. `--from round-04` carries round 04's
survivors with their rival results and its 3 untested theories.

Command:

```
uv run studies/theory/lib/round.py studies/theory/results/engine/round-05 all --cutoff 2026-11-15T04:29:33 \
  --skip gpuprice --skip "theory round" --skip "theory skill" --skip "Theory engine" \
  --from studies/theory/results/engine/round-04
```

## Hypotheses

- H1 (the tests run on a second laptop): at least half of all offline predictions return a number (round 04: 29 of
  42). Refuted below half; the likely cause is then row files this machine cannot read.
- H2 (the carried untested theories get a state): at least 2 of the 3 theories round 04 left untested for missing
  grader packages have 2 or more computed predictions. Refuted below 2.
- H3 (a theory beats a rival): at least one survivor ends `beats rival` after both turns (round 04: 0 of 3 with the
  second turn counted). Refuted if none: five rounds then hold no theory that beat its rival.

## Limits

Those of SPEC_round04.md and SPEC_round04_duel.md. One run, no repeat.
