"""k=6: (med_M - med_R) / (med_E - med_R) of finished-answer mean_logprob medians; R cued base, M step 400 plain, E step 2800 plain."""
import json, math, os, subprocess, sys

D = "runs/theory-tests/duel-r4-m10t2"
B = "s3://pg-lineage-769063704696/results/rlneurons/r3"
FILES = {
    "R": (f"{B}/base-01/out/F_math500.jsonl", f"{D}/base01_F_math500.jsonl"),
    "M": (f"{B}/s0400_s0100-01/out/s0400/P_math500.jsonl", f"{D}/s0400_P_math500.jsonl"),
    "E": (f"{B}/s2800-01/out/P_math500.jsonl", f"{D}/s2800_P_math500.jsonl"),
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


def ok(r):
    return finished(r) and valid_mlp(r)


def ratio(data, S):
    meds = {}
    for name, rows in data.items():
        meds[name] = median([float(rows[p]["mean_logprob"]) for p in S if ok(rows[p])])
    if any(v is None for v in meds.values()):
        return None, meds
    den = meds["E"] - meds["R"]
    if den == 0:
        return "undefined", meds
    return (meds["M"] - meds["R"]) / den, meds


def main():
    try:
        for uri, path in FILES.values():
            fetch(uri, path)
        data = {k: load(v[1]) for k, v in FILES.items()}
    except Exception as e:
        out(nc=f"cannot read row files: {e!r}")
    S = sorted(set(data["R"]) & set(data["M"]) & set(data["E"]))
    if not S:
        out(nc="no problem_index common to all three files")
    for name, rows in data.items():
        if not any("mean_logprob" in rows[p] for p in S):
            out(nc=f"field mean_logprob absent in {name}")
    val, meds = ratio(data, S)
    if val is None:
        out(nc=f"a file has no finished rows with finite mean_logprob: {meds}")
    if val == "undefined":
        out(nc="undefined: med_E - med_R equals 0")
    # alt: paired reading -- only problems finished (finite mean_logprob) in all three files
    S2 = [p for p in S if all(ok(data[n][p]) for n in data)]
    alt, meds2 = ratio(data, S2) if S2 else (None, None)
    if alt == "undefined":
        alt = None
    ex = next(data["M"][p] for p in S if ok(data["M"][p]))
    print(f"# |S|={len(S)} medians={meds}; alt(paired) |S2|={len(S2)} medians={meds2}", file=sys.stderr)
    out(measured=val, refuted=False, alt=alt, ex=strip(ex))


main()
