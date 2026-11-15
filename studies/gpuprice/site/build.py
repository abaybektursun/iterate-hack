"""Writes studies/gpuprice/site/data.json for the results page.

python3 studies/gpuprice/site/build.py     (from the repository root; stdlib only)

Reads content.json (hand-written text), results/ledger/*.json, the locked-origin metrics named in content.json,
the submission CSV and data/event_series_v1.csv. Only reads stored results: nothing is scored here.
A missing file or field stops the build with an error.
"""
import csv, datetime, json, subprocess
from pathlib import Path

SITE = Path(__file__).resolve().parent
STUDY = SITE.parent
load = lambda p: json.loads(Path(p).read_text())
C = load(SITE / "content.json")

# Climb: one point per ledger entry scored on the dev origins with the full cell count. Entries scored on a subset
# (the open-weights LLM arms, 516 cells) are left out because their pooled skill is not comparable.
DEV_ORIGINS, DEV_CELLS = "2026-10-01..2026-10-30", 3109
labels = dict(C["climb_labels"])
climb = []
for f in sorted((STUDY / "results/ledger").glob("*.json")):
    e = load(f)
    if e["origins"] != DEV_ORIGINS or e["cells"]["scored"] != DEV_CELLS:
        continue
    h = {k: v["skill_pooled"] for k, v in e["by_horizon"].items()}
    family = e["name"].split("-")[0]
    climb.append({"id": e["name"], "utc": e["utc"], "skill": e["skill_pooled"],
                  "h1": h.get("1"), "h3": h.get("3"), "h7": h.get("7"),
                  "family": "it" if family.startswith("it") else family,
                  "label": labels.pop(e["name"], e["name"])})
assert not labels, f"climb_labels without a ledger entry on the dev origins: {sorted(labels)}"
climb.sort(key=lambda r: (r["utc"], r["id"]))
best = float("-inf")
for r in climb:
    assert len(r["label"]) <= 60, r["label"]
    r["best"] = r["skill"] > best
    best = max(best, r["skill"])

# Locked origins: the skill of each row is read from the metrics file and key that content.json names.
def pooled(m):
    return m["pooled"] if "pooled" in m else m["overall"]["skill_pooled"]

locked = [{"name": x["name"], "skill": pooled(load(STUDY / x["file"])[x["key"]]), "note": x["note"]} for x in C["locked"]]
m3 = load(STUDY / "results/spec3/locked-01/metrics.json")
assert C["hero"]["value"] == f'{m3["candidate 2"]["pooled"]:+.3f}', "hero value differs from the locked metrics"
assert C["hero"]["baseline"]["value"] == f'{m3["lve"]["pooled"]:+.3f}', "hero baseline differs from the locked metrics"

# Forecast: the submission CSV; `last` is the series' last value at the origin from the event catalog.
ORIGIN, HORIZONS = "2026-11-06", [1, 3, 7]
with open(STUDY / "data/event_series_v1.csv") as f:
    last = {r["series_id"]: float(r["last_value_to_as_of"]) for r in csv.DictReader(f)}
series = {}
with open(STUDY / "results/submission/forecast_2026-11-06.csv") as f:
    for r in csv.DictReader(f):
        assert r["origin_date"] == ORIGIN, r
        series.setdefault(r["series_id"], {})[r["horizon_days"]] = [float(r["q10"]), float(r["q50"]), float(r["q90"])]
for s, q in series.items():
    assert sorted(q, key=int) == [str(h) for h in HORIZONS], (s, list(q))

out = {
    "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=SITE, check=True,
                             capture_output=True, text=True).stdout.strip(),
    "title": C["title"], "subtitle": C["subtitle"], "hero": C["hero"], "stats": C["stats"],
    "locked": locked, "climb": climb,
    "findings": C["findings"], "negatives": C["negatives"], "method": C["method"],
    "forecast": {"origin": ORIGIN, "horizons": HORIZONS,
                 "series": [{"id": s, "last": last[s], "q": q} for s, q in sorted(series.items())]},
    "repro": C["repro"],
}
(SITE / "data.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(f'wrote {SITE / "data.json"}: {len(climb)} climb entries ({sum(r["best"] for r in climb)} best), '
      f'{len(locked)} locked rows, {len(series)} series')
