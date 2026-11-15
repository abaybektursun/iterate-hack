"""k=4: share of step-100 plain finished answers with mean_logprob > median of cued base finished answers."""
import json, math, os, subprocess, sys

D = "runs/theory-tests/duel-r4-m10t2"
B = "s3://pg-lineage-769063704696/results/rlneurons/r3"
FILES = {
    "R": (f"{B}/base-01/out/F_math500.jsonl", f"{D}/base01_F_math500.jsonl"),
    "X": (f"{B}/s0400_s0100-01/out/s0100/P_math500.jsonl", f"{D}/s0100_P_math500.jsonl"),
}


def out(measured=None, refuted=False, alt=None, nc=None, ex=None):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))
    sys.exit(0)


def fetch(uri, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["aws", "s3", "cp", uri, path, "--profile", "iterate-ecr", "--quiet"], check=True)


def load(path):
    rows = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("sample") != 0:
                continue
            pi = r.get("problem_index")
            if pi is None or pi in rows:
                continue
            rows[pi] = r
    return rows


def finished(r):
    if "cap_hit" in r and r["cap_hit"] is not None:
        return r["cap_hit"] is False
    return r.get("finish_reason") == "stop"


def valid_mlp(r):
    v = r.get("mean_logprob")
    if v is None or isinstance(v, bool):
        return False
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def median(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def strip(r):
    return {k: (v[:200] + "..." if isinstance(v, str) and len(v) > 200 else v) for k, v in r.items()}


def share(R, X, S):
    rf = [R[p] for p in S if finished(R[p]) and valid_mlp(R[p])]
    xf = [X[p] for p in S if finished(X[p]) and valid_mlp(X[p])]
    M = median([float(r["mean_logprob"]) for r in rf])
    if M is None or not xf:
        return None, None, None
    above = [r for r in xf if float(r["mean_logprob"]) > M]
    return len(above) / len(xf), (above[0] if above else xf[0]), (M, len(rf), len(xf), len(above))


def main():
    try:
        for uri, path in FILES.values():
            fetch(uri, path)
        R = load(FILES["R"][1])
        X = load(FILES["X"][1])
    except Exception as e:
        out(nc=f"cannot read row files: {e!r}")
    S = sorted(set(R) & set(X))
    if not S:
        out(nc="no problem_index common to both files")
    for name, rows in (("R", R), ("X", X)):
        if not any("mean_logprob" in rows[p] for p in S):
            out(nc=f"field mean_logprob absent in {name}")
    val, ex, info = share(R, X, S)
    if val is None:
        out(nc="no finished rows with finite mean_logprob in R or X")
    # alt: paired reading -- only problems finished (with finite mean_logprob) in both files
    S2 = [p for p in S if finished(R[p]) and valid_mlp(R[p]) and finished(X[p]) and valid_mlp(X[p])]
    alt, _, info2 = share(R, X, S2) if S2 else (None, None, None)
    print(f"# |S|={len(S)} median_R={info[0]} nR_fin={info[1]} nX_fin={info[2]} n_above={info[3]}; alt(paired) info={info2}",
          file=sys.stderr)
    out(measured=val, refuted=False, alt=alt, ex=strip(ex))


main()
