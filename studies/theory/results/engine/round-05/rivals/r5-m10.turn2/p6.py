"""p6: hard328, base plain (7ba0) not self-opened rows with 'Wait'/'Hmm': mean score_v3 minus mean score_v3 of base cue (e72c) on the same problems."""
import json, pathlib, subprocess, sys

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01/{}/answers.jsonl"
PLAIN, CUE = "abaybektursun-1114-132922-7ba0", "abaybektursun-1114-151534-e72c"


def out(**kw):
    base = {"measured": None, "refuted_by_met": False, "alt_measured": None, "not_computable": None, "example_row": None}
    base.update(kw)
    print(json.dumps(base, default=str))
    sys.exit(0)


def load(job):
    path = pathlib.Path(f"runs/theory-tests/{job}/answers.jsonl")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", S3.format(job), str(path), "--profile", "iterate-ecr", "--only-show-errors"], capture_output=True, text=True)
        if r.returncode != 0 or not path.exists():
            out(not_computable=f"cannot fetch {S3.format(job)}: {r.stderr.strip()[:300]}")
    kept, order = {}, {}
    with path.open() as f:
        for n, line in enumerate(f):
            if not line.strip():
                continue
            r = json.loads(line)
            if "problem_index" not in r:
                out(not_computable=f"{job} row lacks problem_index")
            i = r["problem_index"]
            if i not in kept:
                kept[i] = r
            elif "attempt" in r and "attempt" in kept[i] and r["attempt"] is not None and kept[i]["attempt"] is not None \
                    and r["attempt"] < kept[i]["attempt"]:
                kept[i] = r  # smallest attempt; ties / no attempt field -> first in file order
    return kept


def sc(r):
    v = r.get("score_v3")
    return 0 if v is None else v  # null/missing counts 0; cap_hit rows keep theirs


def self_opened(text):  # main: newline immediately followed by 'Okay' in the first 60 characters
    return "\nOkay" in text[:60]


def self_opened_alt(text):  # other reading: 'Okay' anywhere in the first 60 characters
    return "Okay" in text[:60]


def has_marker(text):
    return ("Wait" in text) or ("Hmm" in text)


def main():
    plain, cue = load(PLAIN), load(CUE)
    if any("text" not in r for r in plain.values()):
        out(not_computable="7ba0 row lacks text")

    def stat(opened):
        L = [i for i, r in plain.items() if not opened(r["text"] or "") and has_marker(r["text"] or "") and i in cue]
        if not L:
            return None, L
        return sum(sc(plain[i]) for i in L) / len(L) - sum(sc(cue[i]) for i in L) / len(L), L

    m, L = stat(self_opened)
    a, _ = stat(self_opened_alt)
    if m is None:
        out(not_computable="L is empty: recipe says report nothing")
    ex = dict(plain[L[0]])
    for k in ("answer_tokens", "prompt"):
        ex.pop(k, None)
    ex["text"] = ex["text"][:300]
    ex["cue_score_v3"] = sc(cue[L[0]])
    out(measured=m, refuted_by_met=False, alt_measured=a, example_row=ex)  # refuted_by is null


main()
