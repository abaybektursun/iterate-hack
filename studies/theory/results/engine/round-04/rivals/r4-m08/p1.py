"""duel-r4-m08 p1: stratified post-minus-pre paired gap (RL plain minus base cue), clean harder 328, T 0.6."""
import json
import os
import subprocess
import sys

DIR = "runs/theory-tests/duel-r4-m08"
FILES = {
    "base": ("s3://pg-lineage-769063704696/results/rlneurons/r3/base-01/out/F_hard.jsonl",
             os.path.join(DIR, "base01_F_hard.jsonl")),
    "rl": ("s3://pg-lineage-769063704696/results/rlneurons/r3/s2800-01/out/P_hard.jsonl",
           os.path.join(DIR, "s2800_P_hard.jsonl")),
}
OVERLAP = "studies/rlneurons/results/rln3/rln3_overlap.json"  # = results/rln3/rln3_overlap.json in the rlneurons study
POST_SOURCES = {"aime2025", "hmmt_feb2025"}
N_STRATA = 4


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))
    sys.exit(0)


def fetch(uri, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def load_rows(path):
    best = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            uid = r["unique_id"]
            s = r.get("sample")
            s = 0 if s is None else s
            if uid not in best or s < (best[uid].get("sample") or 0):
                best[uid] = r
    return best


def slim(r):
    d = dict(r)
    if isinstance(d.get("text"), str) and len(d["text"]) > 200:
        d["text"] = d["text"][:200] + "...[truncated]"
    return d


def right(r):
    s = r.get("score")
    return 1 if s == 1 else 0


def main():
    try:
        for k, (uri, path) in FILES.items():
            fetch(uri, path)
        base = load_rows(FILES["base"][1])
        rl = load_rows(FILES["rl"][1])
        flags = json.load(open(OVERLAP))["sets"]["hard"]["flags"]
    except Exception as e:  # noqa
        out(None, False, None, f"could not read inputs: {e!r}", None)

    # Overlap flags are keyed by problem_index (string); map unique_id -> flag entry via the rows' problem_index.
    def flag_of(r):
        return flags.get(str(r["problem_index"]))

    problems = []
    for uid in sorted(set(base) & set(rl)):
        b, p = base[uid], rl[uid]
        fb, fp = flag_of(b), flag_of(p)
        if fb is None or fp is None:
            continue
        if fb is not fp:
            # inconsistent problem_index across files for the same unique_id; use the RL row's entry only if equal
            if fb.get("flag") != fp.get("flag") or fb.get("source") != fp.get("source"):
                continue
        if fp.get("flag") != "none":
            continue
        grp = "post" if fp.get("source") in POST_SOURCES else "pre"
        problems.append({"uid": uid, "grp": grp, "len": p["n_generated"], "len_new": p.get("n_new"),
                         "d": right(p) - right(b), "rl": p})

    if not problems:
        out(None, False, None, "no joined clean problems", None)

    n_post_total = sum(1 for q in problems if q["grp"] == "post")
    if n_post_total == 0:
        out(None, False, None, "no post problems in the joined clean set", None)

    def stat(key):
        ps = sorted(problems, key=lambda q: (q[key], q["uid"]))
        n = len(ps)
        size = n // N_STRATA
        strata = []
        for i in range(N_STRATA):
            lo = i * size
            hi = (i + 1) * size if i < N_STRATA - 1 else n
            strata.append(ps[lo:hi])
        w, dpost, dpre = [], [], []
        for s in strata:
            post = [q["d"] for q in s if q["grp"] == "post"]
            pre = [q["d"] for q in s if q["grp"] == "pre"]
            if post and not pre:
                continue  # dropped stratum
            w.append(len(post) / n_post_total)
            dpost.append(sum(post) / len(post) if post else 0.0)  # weight 0 when no post problems
            dpre.append(sum(pre) / len(pre) if pre else 0.0)
        tw = sum(w)
        if tw == 0:
            return None
        w = [x / tw for x in w]
        g_post = sum(a * b for a, b in zip(w, dpost))
        g_pre = sum(a * b for a, b in zip(w, dpre))
        return 100.0 * (g_post - g_pre)

    measured = stat("len")
    if measured is None:
        out(None, False, None, "every stratum with post problems has no pre problems", None)

    # alt: unstratified gap (no length matching): 100 * (mean d over post - mean d over pre)
    post = [q["d"] for q in problems if q["grp"] == "post"]
    pre = [q["d"] for q in problems if q["grp"] == "pre"]
    alt = 100.0 * (sum(post) / len(post) - sum(pre) / len(pre)) if pre else None

    ex = slim(next(q["rl"] for q in problems if q["grp"] == "post"))
    sys.stderr.write(f"n_joined_clean={len(problems)} n_post={n_post_total} n_pre={len(pre)}\n")
    out(measured, False, alt, None, ex)


if __name__ == "__main__":
    main()
