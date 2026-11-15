"""signed1, what the raw answers show (specs/SPEC_signed1.md): for each signed-trained cell against the cued base on the 328,
the problems finished by both, the new cap hits, loops among cap hits and the rate of the word Wait.

    python3 -m studies.rlneurons.analysis.signed1_read

Inputs: runs/<job>/answers.jsonl of the jobs in results/signed1/readout.json. Writes results/signed1/read.json.
"""
import collections
import json
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[1] / "results" / "signed1"
cells = json.loads((OUT / "readout.json").read_text())["cells"]
load = lambda j: {r["problem_index"]: r for r in map(json.loads, open(f"runs/{j}/answers.jsonl"))}
wait = lambda rows: round(sum(1000 * len(re.findall(r"\bWait\b", r["text"])) / max(r["n_new"], 1) for r in rows.values()) / len(rows), 2)


def looped(r):
    c = collections.Counter(l for l in r["text"][-6000:].split("\n") if len(l) > 20)
    return bool(c) and c.most_common(1)[0][1] >= 4


b = load(cells["base_cue"]["job_id"])
out = {"base_cue": {"wait_per_1000_tokens": wait(b)}}
for name, c in cells.items():
    if name == "base_cue":
        continue
    a = load(c["job_id"])
    both = [i for i in a if not a[i]["cap_hit"] and not b[i]["cap_hit"]]
    new = [i for i in a if a[i]["cap_hit"] and not b[i]["cap_hit"]]
    caps = [i for i in a if a[i]["cap_hit"]]
    out[name] = {"finished_in_both": len(both), "right_signed": sum(a[i]["score_v3"] for i in both), "right_base": sum(b[i]["score_v3"] for i in both),
                 "new_cap_hits": len(new), "new_cap_hits_base_right": sum(b[i]["score_v3"] for i in new),
                 "cap_hits": len(caps), "cap_hits_with_a_line_repeated_4_times_in_last_6000_chars": sum(looped(a[i]) for i in caps),
                 "wait_per_1000_tokens": wait(a)}
(OUT / "read.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
