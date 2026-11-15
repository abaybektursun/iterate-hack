"""p4: T3 (base plain, T 1.0) not self-opened rows with 'Wait'/'Hmm': mean v3 minus mean t1_right (cued base) on the same problems."""
import json, pathlib, subprocess, sys

from studies.rlneurons.lib import rln4_lib as R  # grade_v3, as used by studies/rlneurons/grader/rln4_grader_v3.py

T3 = pathlib.Path("runs/theory-tests/s3/T3.jsonl")
T3_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
PP = pathlib.Path("studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json")


def out(**kw):
    base = {"measured": None, "refuted_by_met": False, "alt_measured": None, "not_computable": None, "example_row": None}
    base.update(kw)
    print(json.dumps(base, default=str))
    sys.exit(0)


def fetch(path, uri):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", uri, str(path), "--profile", "iterate-ecr", "--only-show-errors"], capture_output=True, text=True)
        if r.returncode != 0 or not path.exists():
            out(not_computable=f"cannot fetch {uri}: {r.stderr.strip()[:300]}")


def self_opened(text):  # main reading: newline immediately followed by 'Okay' in the first 60 characters
    return "\nOkay" in text[:60]


def self_opened_alt(text):  # other reading: 'Okay' anywhere in the first 60 characters, newline or not
    return "Okay" in text[:60]


def has_marker(text):
    return ("Wait" in text) or ("Hmm" in text)


def main():
    fetch(T3, T3_S3)
    if not PP.exists():
        out(not_computable=f"{PP} not readable")
    kept = {}
    with T3.open() as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if "problem_index" not in r or "text" not in r or "gold" not in r:
                out(not_computable="T3 row lacks problem_index, text or gold")
            if r["problem_index"] not in kept:  # first in file order
                kept[r["problem_index"]] = r
    pp = {e["problem_index"]: e for e in json.loads(PP.read_text())}
    if any("t1_right" not in e for e in pp.values()):
        out(not_computable="per_problem.json entry lacks t1_right")

    scores = {}
    for i, r in kept.items():
        text = r["text"] or ""
        scores[i] = R.grade_v3(r["gold"], text)["score_v3"]  # cap hits keep v3 score; empty extraction -> 0

    def stat(opened):
        L = [i for i, r in kept.items() if not opened(r["text"] or "") and has_marker(r["text"] or "") and i in pp]
        if not L:
            return None, L
        A = sum(scores[i] for i in L) / len(L)
        B = sum((pp[i]["t1_right"] or 0) for i in L) / len(L)
        return A - B, L

    m, L = stat(self_opened)
    a, _ = stat(self_opened_alt)
    if m is None:
        out(not_computable="L is empty: recipe says report nothing")
    ex = dict(kept[L[0]])
    ex.pop("answer_tokens", None)
    ex["text"] = ex["text"][:300]
    ex["score_v3_recomputed"] = scores[L[0]]
    ex["t1_right"] = pp[L[0]]["t1_right"]
    print(f"n_L={len(L)} n_kept={len(kept)}", file=sys.stderr)
    refuted = False  # refuted_by is null
    out(measured=m, refuted_by_met=refuted, alt_measured=a, example_row=ex)


main()
