# Swarm basins: does the agent swarm explore, or hill-climb one basin?

Written 2026-11-14, before the first run on real board data.

## Question

The swarm improves one number (base-model MATH score with no training) by proposing changes, measuring them on
MATH-500, and keeping what helps. That is hill climbing. Hill climbing stalls in a local optimum when proposals stay
near the current best. Fork-and-Flush (arXiv 2610.07447) and Bespoke Labs' idea-basin maps show this for single
coding agents. We measure it for a multi-person agent swarm, from the team board, live.

## Method

`analysis/run.py`, with the method details in its docstring. Items are board items. Basins come from an LLM
partition, repeated 3 times with shuffled orders. A t-STE map is fit from about 90 triplet appearances per item,
each triplet judged in both orders. The planted-data checks are in `analysis/selftest.py` (all pass at commit 159fdb0).

## Hypotheses and what refutes them

1. H1, the swarm hill-climbs: the pooled switch rate of each person's posts in time order is below the
   time-shuffled null. Refuted if the real rate is at or above the null's 5th percentile (p_below >= 0.05).
2. H2, coverage saturates: the cumulative number of basins stops growing in the second half of posts while
   posts keep arriving. Refuted if more than a third of basins first appear in the second half.
3. H3, unclaimed basins exist: at least one basin holds ideas with no work or result item. Refuted if every
   basin with an idea also has work or a result.

## Instrument conditions (each run reports them; a run that fails them supports no claim)

- Partition stability: mean adjusted Rand between the 3 partitions >= 0.5.
- Basins predict triplets better than permuted basins (p_above < 0.01).
- Order consistency of triplet answers >= 0.8.
- The map must beat the same-author and same-kind label baselines on triplets. If same-author wins, the
  basins encode who posted, not what was done.

## Known limits

- Automatic k from triplets failed on planted data: silhouette, held-out triplet prediction and subsample stability
  all chose 2-3 on 5- and 7-cluster data. So k comes from the LLM partition, and its granularity is the judge's.
- 2D maps distort clusters: on planted 5-cluster data ARI is 0.631 in 2D and 0.935 in 5D. The 2D map is for
  display only. Basins are never read off it.
- Literature check not done: the Exa key returned 401 on 2026-11-14.
