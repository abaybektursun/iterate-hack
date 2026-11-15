# Round 06: first full round on version 6.3 (account, replicate, promotion, facts.json)

Written before the run (2026-11-15, frustea). Code: `lib/round.py` at main 0cd9faf (version 6.3 with --account-from, owner
abaybektursun); this round changes no engine code. Cutoff 2026-11-15T06:51:23, one second after the newest item round 05
held out (result-460e0a). `--from round-05` carries r5-m03 and the two rivals that won (r5-m03-rival, r5-m10-rival);
`--account-from results/account/run-03` gives the account job the three account runs.

Command (launcher of meta review 20261115-0840: inventory and external at the same time, then `all`):

```
sh studies/theory/jobs/round.sh studies/theory/results/engine/round-06 --cutoff 2026-11-15T06:51:23 \
  --skip gpuprice --skip "theory round" --skip "theory skill" --skip "Theory engine" \
  --from studies/theory/results/engine/round-05 --account-from studies/theory/results/account/run-03
```

## Hypotheses

- H1 (a promoted rival holds): at least one of the two rivals carried as theories from round 05 is not refuted and does
  not lose to its fresh rival. Refuted if both are refuted or lose: winning one duel then says little.
- H2 (replication): every decisive number the replicate stage recomputes equals the first computation (account run 03:
  all equal). Refuted by one that differs.
- H3 (launcher): inventory.md and external.md both exist within 1,000 s of the start (round 05: 1,359 s one after the
  other). Refuted above 1,000 s.

## Limits

Those of SPEC_round04.md and SPEC_round04_duel.md. One run. Open GPU prediction of round 05 (base + top8 + cue on
MATH-500, 425 [412, 438]): not measured by anyone before this round.
