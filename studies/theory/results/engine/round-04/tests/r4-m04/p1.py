"""r4-m04 prediction 1: Wait-rate share estimate S in theta0.25_plain vs T3 (base plain) and T2 (RL plain)."""
import json
import os
import re
import statistics
import subprocess

BASE = "runs/theory-tests"
FILES = {
    "theta": (f"{BASE}/abaybektursun-1114-163704-ffca/answers.jsonl",
              ["modal", "volume", "get", "iterate-runs", "abaybektursun-1114-163704-ffca/answers.jsonl"]),
    "T2": (f"{BASE}/s3/T2.jsonl",
           ["aws", "s3", "cp", "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t2-01/t2/T2.jsonl", None,
            "--profile", "iterate-ecr", "--only-show-errors"]),
    "T3": (f"{BASE}/s3/T3.jsonl",
           ["aws", "s3", "cp", "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl", None,
            "--profile", "iterate-ecr", "--only-show-errors"]),
}
WAIT = re.compile(r"\bWait\b")


def out(measured, met, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": met, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))


def fetch(path, cmd):
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cmd = [path if c is None else c for c in cmd]
    if cmd[0] == "modal":
        cmd = cmd + [path]
    subprocess.run(cmd, check=True)


def load(path):
    rows, seen = [], set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            pi = r.get("problem_index")
            if pi in seen:
                continue
            seen.add(pi)
            rows.append(r)
    return rows


def rate(r):
    text = r.get("text") or ""
    n_new = r.get("n_new") or 0
    return 1000.0 * len(WAIT.findall(text)) / max(n_new, 1)


def slim(r):
    return {k: v for k, v in r.items() if k not in ("text", "prompt", "parsed_gold", "parsed_answer")} | {
        "text_head": (r.get("text") or "")[:300], "wait_count": len(WAIT.findall(r.get("text") or ""))}


def main():
    data = {}
    for k, (p, cmd) in FILES.items():
        try:
            fetch(p, cmd)
            data[k] = load(p)
        except Exception as e:
            out(None, False, None, f"cannot read {k} file {p}: {e}", None)
            return
    for k, rows in data.items():
        if not rows:
            out(None, False, None, f"{k} file has no rows", None)
            return
        if any("text" not in r or "n_new" not in r for r in rows):
            out(None, False, None, f"{k} rows lack field text or n_new", None)
            return
    rates = {k: [rate(r) for r in rows] for k, rows in data.items()}
    m = statistics.median(rates["T2"])  # same as numpy.median (mean of two middle values for even n)

    def F(k, strict=False):
        rs = rates[k]
        return sum(1 for x in rs if (x > m if strict else x >= m)) / len(rs)

    Ft, F2, F3 = F("theta"), F("T2"), F("T3")
    alt = None
    a2, a3, at = F("T2", True), F("T3", True), F("theta", True)
    if a2 - a3 != 0:
        alt = round((at - a3) / (a2 - a3), 3)
    ex = slim(data["theta"][0])
    ex["wait_rate"] = rates["theta"][0]
    ex["T2_median_rate"] = m
    if F2 - F3 == 0:
        out(None, False, alt, f"F_T2 - F_T3 = 0 (F_T2={F2}, F_T3={F3}, m={m}); S undefined", ex)
        return
    S = round((Ft - F3) / (F2 - F3), 3)
    out(S, bool(S < 0.60 or S > 0.92), alt, None, ex)


if __name__ == "__main__":
    main()
