"""r4-m04 prediction 3: D = mean(score_v3 - t2_right) over theta0.25_plain rows whose text contains \\boxed."""
import json
import os
import subprocess

BASE = "runs/theory-tests"
THETA = f"{BASE}/abaybektursun-1114-163704-ffca/answers.jsonl"
THETA_CMD = ["modal", "volume", "get", "iterate-runs", "abaybektursun-1114-163704-ffca/answers.jsonl", THETA]
PER_PROBLEM = "studies/rlneurons/results/rln4/t1_t2_items-01/per_problem.json"
BOXED = "\\boxed"


def out(measured, met, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": met, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))


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


def b01(v):
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    try:
        return 1 if float(v) > 0 else 0
    except (TypeError, ValueError):
        return 0


def main():
    try:
        if not os.path.exists(THETA):
            os.makedirs(os.path.dirname(THETA), exist_ok=True)
            subprocess.run(THETA_CMD, check=True)
        rows = load(THETA)
    except Exception as e:
        out(None, False, None, f"cannot read theta file {THETA}: {e}", None)
        return
    try:
        pp = json.load(open(PER_PROBLEM))
    except Exception as e:
        out(None, False, None, f"cannot read {PER_PROBLEM}: {e}", None)
        return
    if isinstance(pp, dict):
        pp = list(pp.values()) if all(isinstance(v, dict) for v in pp.values()) else []
    t2 = {}
    for e in pp:
        if isinstance(e, dict) and "problem_index" in e and "t2_right" in e:
            t2.setdefault(e["problem_index"], e["t2_right"])
    if not t2:
        out(None, False, None, "per_problem.json has no problem_index/t2_right entries", None)
        return
    if any("text" not in r for r in rows):
        out(None, False, None, "theta rows lack field text", None)
        return

    def D(select):
        ds, ex = [], None
        for r in rows:
            if not select(r):
                continue
            pi = r.get("problem_index")
            if pi not in t2:
                continue
            d = b01(r.get("score_v3")) - b01(t2[pi])
            ds.append(d)
            if ex is None:
                ex = {k: v for k, v in r.items() if k not in ("text", "prompt", "parsed_gold", "parsed_answer")}
                ex["text_tail"] = (r.get("text") or "")[-300:]
                ex["t2_right"] = t2[pi]
                ex["d"] = d
        return (sum(ds) / len(ds) if ds else None), ex, len(ds)

    main_D, ex, n = D(lambda r: BOXED in (r.get("text") or ""))
    alt_D, _, _ = D(lambda r: r.get("mode_v3") == "boxed")
    alt = None if alt_D is None else round(alt_D, 4)
    if main_D is None:
        out(None, False, alt, "no theta row contains \\boxed with a per_problem.json entry", None)
        return
    main_D = round(main_D, 4)
    ex["n_kept"] = n
    out(main_D, bool(main_D < -0.10 or main_D > 0.02), alt, None, ex)


if __name__ == "__main__":
    main()
