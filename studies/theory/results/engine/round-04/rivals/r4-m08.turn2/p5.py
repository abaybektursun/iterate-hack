import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import compute_L, median

short_L, long_L, ex = compute_L("a0")
if not short_L or not long_L:
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                      "not_computable": "empty short or long group", "example_row": None}))
    sys.exit(0)
measured = median(short_L) - median(long_L)
a_s, a_l, _ = compute_L("last")
alt = (median(a_s) - median(a_l)) if (a_s and a_l) else None
print(f"n_short={len(short_L)} n_long={len(long_L)} alt={len(a_s)}/{len(a_l)}", file=sys.stderr)
refuted = False  # refuted_by is null
print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                  "not_computable": None, "example_row": ex}))
