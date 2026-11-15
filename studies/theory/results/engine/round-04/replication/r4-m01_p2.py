"""r4-m01 p2: AUROC of -zlib9 ratio of text[:6000] for a later rule-A loop (stored loop_A), cued base, T 0.6 / top-p 1.0.

Keep len(text) >= 6000 and (loop_A false, or loop_A true with onset_A_char >= 7000)."""
import json
from common import auroc, bootstrap, ratio, rows

R = rows("d4fa_answers.jsonl")
kept = []
for r in R:
    if len(r["text"]) < 6000:
        continue
    if r["loop_A"]:
        if r.get("onset_A_char") is None or r["onset_A_char"] < 7000:
            continue
    elif r["loop_A"] is not False:
        raise ValueError(f"loop_A not boolean: {r['loop_A']!r}")
    kept.append((-ratio(r["text"][:6000], 9), bool(r["loop_A"])))
stat = lambda xs: auroc([s for s, _ in xs], [y for _, y in xs])
print(json.dumps({"rows_file": len(R), "kept": len(kept), "positives": sum(y for _, y in kept), "value": stat(kept),
                  "interval_90": bootstrap(kept, stat),
                  "loop_A_total": sum(bool(r["loop_A"]) for r in R),
                  "dropped_early_onset": sum(1 for r in R if len(r["text"]) >= 6000 and r["loop_A"]
                                             and (r.get("onset_A_char") is None or r["onset_A_char"] < 7000))}))
