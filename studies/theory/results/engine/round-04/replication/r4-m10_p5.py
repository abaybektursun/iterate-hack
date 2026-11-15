"""r4-m10 p5: share of step-400 cap hits (plain MATH-500, T 0.6 / top-p 0.95) that are rule-A loops.

Rule A as the recipe states it: for every p that is 0 or follows a newline with len(text) - p >= 8000,
w = text[p:p+8000]; loop if any zlib ratio (default level) < 0.10. Ratio over the UTF-8 bytes of the 8,000-character window.
Also reports rln3's stored loop_ratio is not rule A, so it is not used."""
import json
from common import bootstrap, cap_hit, first_sample0, ratio


def rule_a(text):
    if len(text) < 8000:
        return False, None
    starts = [0] + [i + 1 for i, c in enumerate(text) if c == "\n"]
    for p in starts:
        if len(text) - p < 8000:
            break
        if ratio(text[p:p + 8000]) < 0.10:
            return True, p
    return False, None


A = first_sample0("r3_s0400_s0100-01_out_s0400_P_math500.jsonl")
caps = [r for r in A.values() if cap_hit(r)]
flags = []
for r in caps:
    loop, onset = rule_a(r["text"])
    flags.append(int(loop))
    r["_loop"], r["_onset"] = loop, onset
share = lambda xs: sum(xs) / len(xs)
loops = [r for r in caps if r["_loop"]]
nonloops = [r for r in caps if not r["_loop"]]
print(json.dumps({
    "cap_hit_rows": len(caps), "loop_rows": sum(flags), "value": share(flags), "interval_90": bootstrap(flags, share),
    "loop_problem_indices": sorted(r["problem_index"] for r in loops),
    "nonloop_problem_indices": sorted(r["problem_index"] for r in nonloops),
    "loop_example": {"problem_index": loops[0]["problem_index"], "onset_char": loops[0]["_onset"], "len": len(loops[0]["text"]),
                     "tail": loops[0]["text"][-400:]} if loops else None,
    "nonloop_example": {"problem_index": nonloops[0]["problem_index"], "len": len(nonloops[0]["text"]),
                        "tail": nonloops[0]["text"][-400:]} if nonloops else None,
}))

# Alternative reading (not the recipe): rln3's stored loop_ratio field < 0.10 in place of rule A.
alt = [int(r["loop_ratio"] is not None and r["loop_ratio"] < 0.10) for r in caps]
print(json.dumps({"alt_stored_loop_ratio_lt_0.10": {"loop_rows": sum(alt), "value": share(alt),
                                                     "agree_with_rule_A": sum(a == b for a, b in zip(alt, flags))}}))
