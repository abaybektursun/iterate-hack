"""Bootstrap over series of the pooled-skill difference between two scored forecasts. Laptop.

runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/fm2_boot.py runs/gpuprice/evals/<A>/cells.csv runs/gpuprice/evals/<B>/cells.csv
Prints pooled skill of A and B, A - B, and its 95 % interval from 5,000 resamples of the series (with replacement;
the 30 origins of a series overlap, so the series is the unit). Also the difference on each half of the origins.
"""
import sys
import numpy as np, pandas as pd

K = ["series_id", "origin_date", "horizon_days"]
a, b = (pd.read_csv(p) for p in sys.argv[1:3])
m = a[K + ["loss", "baseline_loss"]].merge(b[K + ["loss"]], on=K, suffixes=("_a", "_b"))
assert len(m) == len(a) == len(b)
skill = lambda x, c: 1 - x[c].sum() / x.baseline_loss.sum()
print("cells", len(m), "series", m.series_id.nunique(), "A %.4f B %.4f A-B %.4f" % (skill(m, "loss_a"), skill(m, "loss_b"), skill(m, "loss_a") - skill(m, "loss_b")))
s = m.groupby("series_id")[["loss_a", "loss_b", "baseline_loss"]].sum().values
rng = np.random.default_rng(0)
i = rng.integers(len(s), size=(5000, len(s)))
t = s[i].sum(1)
d = (t[:, 1] - t[:, 0]) / t[:, 2]
print("95 %% interval of A-B over series: [%.4f, %.4f], share of resamples above 0: %.3f" % (*np.quantile(d, [0.025, 0.975]), (d > 0).mean()))
for name, x in (("origins to 2026-10-15", m[m.origin_date <= "2026-10-15"]), ("origins from 2026-10-16", m[m.origin_date > "2026-10-15"])):
    print(name, "A %.4f B %.4f A-B %.4f" % (skill(x, "loss_a"), skill(x, "loss_b"), skill(x, "loss_a") - skill(x, "loss_b")))
print("series won by A:", int((s[:, 0] < s[:, 1]).sum()), "lost:", int((s[:, 0] > s[:, 1]).sum()))
