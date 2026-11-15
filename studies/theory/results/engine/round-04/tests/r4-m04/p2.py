"""r4-m04 prediction 2: answer-format share estimate P = 1 - s_theta / s_T3 (answer-line rows without \\boxed)."""
import json
import os
import subprocess

BASE = "runs/theory-tests"
FILES = {
    "theta": (f"{BASE}/abaybektursun-1114-163704-ffca/answers.jsonl",
              ["modal", "volume", "get", "iterate-runs", "abaybektursun-1114-163704-ffca/answers.jsonl"]),
    "T3": (f"{BASE}/s3/T3.jsonl",
           ["aws", "s3", "cp", "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl", None,
            "--profile", "iterate-ecr", "--only-show-errors"]),
}
BOXED = "\\boxed"


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


def is_answer_line(text, alt=False):
    if BOXED in text:
        return False
    for line in text.splitlines():
        if alt:
            # other reading: whitespace, '*' and '#' stripped together in any order (e.g. "## **Answer:")
            s = line.lstrip(" \t\r\f\v*#")
        else:
            # literal: strip leading whitespace, then any leading '*' or '#' characters
            s = line.lstrip().lstrip("*#")
        if s.startswith("Answer:"):
            return True
    return False


def slim(r):
    return {k: v for k, v in r.items() if k not in ("text", "prompt", "parsed_gold", "parsed_answer")} | {
        "text_tail": (r.get("text") or "")[-300:]}


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
        if any("text" not in r for r in rows):
            out(None, False, None, f"{k} rows lack field text", None)
            return

    def s(k, alt=False):
        rows = data[k]
        return sum(1 for r in rows if is_answer_line(r.get("text") or "", alt)) / len(rows)

    st, s3 = s("theta"), s("T3")
    ast, as3 = s("theta", True), s("T3", True)
    alt = None if as3 < 0.05 else round(1 - ast / as3, 3)
    ex = None
    for r in data["theta"]:
        if is_answer_line(r.get("text") or ""):
            ex = slim(r)
            break
    if ex is None:
        ex = slim(data["theta"][0])
    if s3 < 0.05:
        # refuted_by: "or undefined"
        out(None, True, alt, None, None)
        return
    P = round(1 - st / s3, 3)
    out(P, bool(P < 0.60 or P > 0.92), alt, None, ex)


if __name__ == "__main__":
    main()
