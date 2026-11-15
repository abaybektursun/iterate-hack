# uv run --with modal python meta/reviews/abaybektursun/20261115-2258-paper6/measure.py > <before.txt|after.txt>
# Runs gpu.py's command check (gpu.check_cmd, after the change) on the full commands of every job in the team's job dict:
# prints the two jobs that failed on --model + --model-label (496b, 4575), and every past job the check would refuse with its state.
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "tools"))
import gpu

check = getattr(gpu, "check_cmd", None)
print("gpu.check_cmd exists:", check is not None)
records = {k: r for k, r in gpu.load().items() if "job" in r}
refused, n = [], len(records)
for k, r in records.items():
    if check is None:
        continue
    try:
        check(r["job"]["cmd"])
    except AssertionError as e:
        refused.append((k, str(e)[:80]))
for jid in ("abaybektursun-1115-161411-496b", "abaybektursun-1115-161425-4575"):
    print(jid, "refused at submit:", any(r[0] == jid for r in refused))
print("jobs checked:", n, "refused:", len(refused))
for jid, why in sorted(refused):
    print(" ", jid, gpu.state(records[jid]), why)
