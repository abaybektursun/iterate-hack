# /// script
# requires-python = ">=3.11"
# dependencies = ["modal>=1.4"]
# ///
"""Jobs per GPU class since a UTC epoch time, from the Modal Dict iterate-jobs: count, queue wait, GPU minutes, and
how many run or wait now.   uv run lanes.py <hours back>"""
import sys, time
import modal

d = dict(modal.Dict.from_name("iterate-jobs").items())
since, now = time.time() - float(sys.argv[1]) * 3600, time.time()
for cls in ("h100", "short", "b200"):
    ids = [k[4:] for k, v in d.items() if k.startswith("job:") and v["class"] == cls and v["at"] >= since]
    started = [i for i in ids if f"start:{i}" in d]
    ended = lambda i: f"end:{i}" in d or f"cancel:{i}" in d
    waits = sorted((d[f"start:{i}"]["at"] - d[f"job:{i}"]["at"]) / 60 for i in started)
    gpu_min = sum(((d[f"end:{i}"]["at"] if f"end:{i}" in d else now) - d[f"start:{i}"]["at"]) / 60 for i in started if f"end:{i}" in d or not ended(i))
    waiting = [i for i in ids if i not in started and not ended(i)]
    oldest = max(((now - d[f"job:{i}"]["at"]) / 60 for i in waiting), default=0)
    print(f"{cls}: {len(ids)} submitted, {len(started)} started, median wait {waits[len(waits)//2] if waits else 0:.1f} min, "
          f"GPU min {gpu_min:.0f}, waiting now {len(waiting)} (oldest {oldest:.0f} min)")
