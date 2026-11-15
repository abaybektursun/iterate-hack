import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import compute_L, median

short_L, _, ex = compute_L("a0")
if not short_L:
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None,
                      "not_computable": "no short kept problems", "example_row": None}))
    sys.exit(0)
measured = median(short_L)
alt_s, _, _ = compute_L("last")
alt = median(alt_s) if alt_s else None
print(f"n_short={len(short_L)} alt_n_short={len(alt_s)}", file=sys.stderr)
refuted = False  # refuted_by is null
print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                  "not_computable": None, "example_row": ex}))
