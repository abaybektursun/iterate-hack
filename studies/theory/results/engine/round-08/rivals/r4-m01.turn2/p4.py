"""k=4: RL-prefix vs own-prefix finish rate, on problems where the RL-prefix
continuation's first 3000 chars are at least as compressible as the own-prefix one's."""
import json
import os
import subprocess
import sys
import zlib

ROOT = os.getcwd()
DIR = os.path.join(ROOT, "runs", "theory-tests", "duel-r4-m01.turn2")
BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r4/"
FILES = {
    "modal_rl": ("modal_k-01/k_a/K_rl.jsonl", "modal_K_rl.jsonl"),
    "modal_own": ("modal_k-01/k_a/K_own.jsonl", "modal_K_own.jsonl"),
    "aws_rl": ("base_rl-02/out/K_rl.jsonl", "base_rl-02_K_rl.jsonl"),
}


def out(measured, refuted, alt, nc, example):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": example}))


def short(row):
    return {k: (v[:300] + "...[truncated]" if isinstance(v, str) and len(v) > 300 else v)
            for k, v in row.items()}


def fetch(key, local):
    path = os.path.join(DIR, local)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        os.makedirs(DIR, exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", BUCKET + key, path, "--profile", "iterate-ecr",
                            "--only-show-errors"], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            raise RuntimeError(f"cannot fetch {BUCKET + key}: {r.stderr.strip()}")
    return path


def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def lowest_sample(rows):
    best = {}
    for r in rows:
        pi = r["problem_index"]
        if pi not in best or r["sample"] < best[pi]["sample"]:
            best[pi] = r
    return best


def ratio(s):
    b = s.encode("utf-8")
    return len(zlib.compress(b, 9)) / len(b)


def main():
    try:
        data = {name: load(fetch(key, local)) for name, (key, local) in FILES.items()}
    except Exception as e:  # noqa: BLE001
        out(None, False, None, f"file not readable: {e}", None)
        return
    for name, rows in data.items():
        for r in rows:
            for fld in ("problem_index", "sample", "text", "cap_hit"):
                if fld not in r:
                    out(None, False, None, f"field {fld} missing in {name} rows", None)
                    return
    mrl = lowest_sample(data["modal_rl"])
    mown = lowest_sample(data["modal_own"])
    arl = lowest_sample(data["aws_rl"])

    common = sorted(set(mrl) & set(mown))
    n_common = len(common)
    n_short = 0
    diffs, diffs_alt = [], []
    kept, kept_with_aws = [], 0
    example = None
    for pi in common:
        tr, to = mrl[pi]["text"], mown[pi]["text"]
        if tr is None or to is None or len(tr) < 3000 or len(to) < 3000:
            n_short += 1
            continue
        rR = ratio(tr[:3000])
        rO = ratio(to[:3000])
        if not rR <= rO:
            continue
        fins = [1.0 if mrl[pi]["cap_hit"] is False else 0.0]
        if pi in arl:
            fins.append(1.0 if arl[pi]["cap_hit"] is False else 0.0)
            kept_with_aws += 1
        finish_rl = sum(fins) / len(fins)
        finish_own = 1.0 if mown[pi]["cap_hit"] is False else 0.0
        diffs.append(finish_rl - finish_own)
        diffs_alt.append(fins[0] - finish_own)  # alt: modal K_rl row alone
        kept.append(pi)
        if example is None:
            example = short(mrl[pi])

    print(f"problems in both modal K_rl and K_own: {n_common}", file=sys.stderr)
    print(f"dropped for text < 3000 chars: {n_short}", file=sys.stderr)
    print(f"kept problems (rR <= rO): {len(kept)}; of them with a base_rl-02 row: {kept_with_aws}",
          file=sys.stderr)
    print(f"kept={len(kept)} kept_with_base_rl02={kept_with_aws} common={n_common} dropped_short={n_short}")
    if not diffs:
        out(None, False, None, "no problem kept after the length and compressibility filters", None)
        return
    measured = sum(diffs) / len(diffs)
    alt = sum(diffs_alt) / len(diffs_alt)
    refuted = False  # refuted_by is null
    out(measured, refuted, alt, None, example)


if __name__ == "__main__":
    main()
