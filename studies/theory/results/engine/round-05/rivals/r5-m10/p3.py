"""duel-r5-m10 k=3: in P_math500 (base, plain, T 0.6), mean v3 of self-opened rows minus mean v3 of non-self-opened rows."""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R

DIR = pathlib.Path("runs/theory-tests/duel-r5-m10")
URL = "s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/P_math500.jsonl"


def fail(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None, "not_computable": reason, "example_row": None}))
    raise SystemExit(0)


def fetch():
    p = DIR / "P.jsonl"
    if not p.exists():
        DIR.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", URL, str(p), "--profile", "iterate-ecr"], capture_output=True, text=True)
        if r.returncode != 0 or not p.exists():
            fail(f"cannot fetch {URL}: {r.stderr.strip()[-300:]}")
    return p


def self_opened(text):
    return "\nOkay" in text[:60]


def self_opened_alt(text):  # other reading: an answer that starts with 'Okay' also opened itself
    return "\nOkay" in text[:60] or text.lstrip().startswith("Okay")


rows = [json.loads(l) for l in open(fetch()) if l.strip()]
for k in ("problem_index", "text", "gold", "sample"):
    if any(k not in r for r in rows):
        fail(f"field {k} missing in P_math500")
kept = {}
for r in rows:  # smallest sample per problem; ties keep the first row met
    i = r["problem_index"]
    if i not in kept or r["sample"] < kept[i]["sample"]:
        kept[i] = r
score = {i: R.grade_v3(r["gold"], r["text"])["score_v3"] for i, r in kept.items()}  # empty extraction -> 0; cap hits keep v3's score


def stat(opened):
    so = [score[i] for i in sorted(kept) if opened(kept[i]["text"])]
    no = [score[i] for i in sorted(kept) if not opened(kept[i]["text"])]
    if not so or not no:
        return None, len(so), len(no)
    return sum(so) / len(so) - sum(no) / len(no), len(so), len(no)


main, n_so, n_no = stat(self_opened)
alt, _, _ = stat(self_opened_alt)
if main is None:
    fail(f"a group is empty (self-opened {n_so}, non-self-opened {n_no}); the recipe says report nothing")
first = next(i for i in sorted(kept) if self_opened(kept[i]["text"]))
ex = dict(kept[first])
ex["text"] = ex["text"][:400]
ex["score_v3_recomputed"] = score[first]
print(json.dumps({"n_self_opened": n_so, "n_non_self_opened": n_no}))
print(json.dumps({"measured": main, "refuted_by_met": False, "alt_measured": alt, "not_computable": None, "example_row": ex}))
