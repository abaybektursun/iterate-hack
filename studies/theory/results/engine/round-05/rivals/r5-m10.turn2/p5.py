"""p5: within T3 (base plain, T 1.0) not self-opened rows: mean v3 of rows with 'Wait'/'Hmm' minus mean v3 of rows with neither."""
import json, pathlib, subprocess, sys

from studies.rlneurons.lib import rln4_lib as R  # grade_v3, as used by studies/rlneurons/grader/rln4_grader_v3.py

T3 = pathlib.Path("runs/theory-tests/s3/T3.jsonl")
T3_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"


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


def self_opened(text):  # main: newline immediately followed by 'Okay' within the first 60 characters
    return "\nOkay" in text[:60]


def self_opened_alt(text):  # other reading: 'Okay' anywhere in the first 60 characters
    return "Okay" in text[:60]


def has_marker(text):
    return ("Wait" in text) or ("Hmm" in text)


def main():
    fetch(T3, T3_S3)
    kept = {}
    with T3.open() as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if "problem_index" not in r or "text" not in r or "gold" not in r:
                out(not_computable="T3 row lacks problem_index, text or gold")
            if r["problem_index"] not in kept:
                kept[r["problem_index"]] = r
    scores = {i: R.grade_v3(r["gold"], r["text"] or "")["score_v3"] for i, r in kept.items()}

    def stat(opened):
        rem = [i for i, r in kept.items() if not opened(r["text"] or "")]
        M = [i for i in rem if has_marker(kept[i]["text"] or "")]
        N = [i for i in rem if not has_marker(kept[i]["text"] or "")]
        if not M or not N:
            return None, M
        return sum(scores[i] for i in M) / len(M) - sum(scores[i] for i in N) / len(N), M

    m, M = stat(self_opened)
    a, _ = stat(self_opened_alt)
    if m is None:
        out(not_computable="group M or N is empty: recipe says report nothing")
    ex = dict(kept[M[0]])
    ex.pop("answer_tokens", None)
    ex["text"] = ex["text"][:300]
    ex["score_v3_recomputed"] = scores[M[0]]
    out(measured=m, refuted_by_met=False, alt_measured=a, example_row=ex)  # refuted_by is null


main()
