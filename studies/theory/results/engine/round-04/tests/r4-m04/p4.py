"""r4-m04 prediction 4: Wait-rate share estimate S_cue in theta0.25_cue vs T1 (base cue) and rl_cue."""
import json
import os
import re
import statistics
import subprocess

BASE = "runs/theory-tests"
FILES = {
    "theta": (f"{BASE}/abaybektursun-1114-153102-b029/answers.jsonl",
              ["modal", "volume", "get", "iterate-runs", "abaybektursun-1114-153102-b029/answers.jsonl"]),
    "RLcue": (f"{BASE}/abaybektursun-1114-153110-e985/answers.jsonl",
              ["modal", "volume", "get", "iterate-runs", "abaybektursun-1114-153110-e985/answers.jsonl"]),
    "T1": (f"{BASE}/s3/T1.jsonl",
           ["aws", "s3", "cp", "s3://pg-lineage-769063704696/results/rlneurons/r4/base_rl-02/out/T1.jsonl", None,
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
    m = statistics.median(rates["RLcue"])  # same as numpy.median

    def F(k, strict=False):
        rs = rates[k]
        return sum(1 for x in rs if (x > m if strict else x >= m)) / len(rs)

    Ft, Fr, F1 = F("theta"), F("RLcue"), F("T1")
    at, ar, a1 = F("theta", True), F("RLcue", True), F("T1", True)
    alt = round((at - a1) / (ar - a1), 3) if ar - a1 >= 0.1 else None
    if Fr - F1 < 0.1:
        # refuted_by: "or undefined"
        out(None, True, alt, None, None)
        return
    ex = slim(data["theta"][0])
    ex["wait_rate"] = rates["theta"][0]
    ex["RLcue_median_rate"] = m
    S = round((Ft - F1) / (Fr - F1), 3)
    out(S, bool(S < 0.42 or S > 0.92), alt, None, ex)


if __name__ == "__main__":
    main()
