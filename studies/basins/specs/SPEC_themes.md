# SPEC themes: a second level over the swarm's clusters (written before the run, 2026-11-15)

Question: do the judge's clusters of board items (swarm/main-03: 218 items, 12 clusters) themselves fall into a few
larger themes, and is that grouping stable?

Method: one judge call per order (`analysis/swarm_themes.py`, judge gpt-6.1-sol as in main-03). The judge sees each
cluster's name and its first 8 items (180 characters each) under a neutral label, and puts every cluster into one of
3 to 5 themes. It also gives each theme and each cluster a name of one or two words, used on the page. Order 1 shows
the clusters in a shuffled order with other labels.

Control: an exact copy of one cluster, under another label and the name "Unnamed", is added to both calls. It must
land in the theme of its original in both orders. If it does not, the grouping is not read from the content and no
number is reported.

Prediction: the two orders agree on at least 56 of the 66 pairs of clusters (same theme or not). Refuted if fewer:
then the page shows one level only.

Output: `results/swarm/themes-01/metrics.json` (themes of order 0, themes of order 1, pairs agreed of 66, the control)
and `run.json`. The prompts and raw answers hold board text and stay in `runs/swarm/themes-01-calls/` (not committed).
