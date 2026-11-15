"""r5-m10 prediction 3: AUROC of cue_logprob_base (checks.json per_row.T1) for label = T3 row self-opened.
Self-opened (main): text[:60] contains '\\nOkay'. Mann-Whitney: fraction of (label 1, label 0) pairs with label-1 score higher,
ties 0.5. Problems missing from either file dropped. Cap hits not treated specially (an empty text is label 0).
alt_measured: same AUROC with self-opened = regex r'\\n\\s*Okay' match starting within the first 60 characters.
"""
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path.cwd()
T3_S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
T3 = ROOT / "runs/theory-tests/s3/T3.jsonl"
CK = ROOT / "studies/rlneurons/results/rln5/map-01/checks.json"


def nc(reason):
    print(json.dumps({"measured": None, "refuted_by_met": False, "alt_measured": None, "not_computable": reason, "example_row": None}))
    raise SystemExit(0)


def fetch():
    if not T3.exists():
        T3.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", T3_S3, str(T3), "--profile", "iterate-ecr"], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not T3.exists():
        nc("T3.jsonl could not be fetched from S3")
    if not CK.exists():
        nc("checks.json not found")


def self_open_main(text):
    return "\nOkay" in text[:60]


ALT_RE = re.compile(r"\n\s*Okay")


def self_open_alt(text):
    m = ALT_RE.search(text)
    return m is not None and m.start() < 60


def auroc(pos, neg):
    if not pos or not neg:
        return None
    s = 0.0
    for p in pos:
        for q in neg:
            s += 1.0 if p > q else (0.5 if p == q else 0.0)
    return s / (len(pos) * len(neg))


def trunc(r):
    r = dict(r)
    if isinstance(r.get("text"), str) and len(r["text"]) > 400:
        r["text"] = r["text"][:400] + "...[truncated]"
    return r


def main():
    fetch()
    t3 = {}
    for line in T3.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            t3.setdefault(r["problem_index"], []).append(r)
    for k, v in t3.items():
        if len(v) != 1:
            nc(f"T3 has {len(v)} rows for problem_index {k}; recipe assumes one sample per problem")
        if "text" not in v[0]:
            nc("T3 row lacks text")
    ck = json.loads(CK.read_text())
    try:
        lst = ck["per_row"]["T1"]
    except (KeyError, TypeError):
        nc("checks.json has no per_row.T1 list")
    sc = {}
    for e in lst:
        if "cue_logprob_base" not in e:
            nc("per_row.T1 entry lacks cue_logprob_base")
        sc.setdefault(e["problem_index"], []).append(e)
    for k, v in sc.items():
        if len(v) != 1:
            nc(f"per_row.T1 has {len(v)} entries for problem_index {k}")

    keys = [k for k in t3 if k in sc and sc[k][0]["cue_logprob_base"] is not None]

    def run(pred):
        pos, neg = [], []
        for k in keys:
            text = t3[k][0]["text"] if isinstance(t3[k][0]["text"], str) else ""
            (pos if pred(text) else neg).append(float(sc[k][0]["cue_logprob_base"]))
        return auroc(pos, neg), len(pos), len(neg)

    a, npos, nneg = run(self_open_main)
    a_alt, _, _ = run(self_open_alt)
    if a is None:
        nc(f"AUROC undefined: {npos} label-1 and {nneg} label-0 problems")
    k0 = next(k for k in sorted(keys) if self_open_main(t3[k][0]["text"] or ""))
    ex = trunc(t3[k0][0])
    ex["_checks_T1_entry"] = sc[k0][0]
    print(json.dumps({"n_pos": npos, "n_neg": nneg}))
    print(json.dumps({"measured": a, "refuted_by_met": bool(a < 0.53), "alt_measured": a_alt, "not_computable": None, "example_row": ex}))


if __name__ == "__main__":
    main()
