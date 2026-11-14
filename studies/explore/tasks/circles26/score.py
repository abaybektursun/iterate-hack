"""Scorer for circles26: `python score.py solution.py [--test]` prints {"score", "valid", "msg"} as one JSON line.

The task has no held-out split (the objective is exact), so --test scores the same way.
"""
import json
import math
import subprocess
import sys

N, TOL, LIMIT = 26, 1e-9, 60


def main():
    try:
        r = subprocess.run([sys.executable, sys.argv[1]], capture_output=True, text=True, timeout=LIMIT)
    except subprocess.TimeoutExpired:
        return {"score": None, "valid": False, "msg": f"program exceeded {LIMIT} s"}
    lines = [l for l in r.stdout.strip().splitlines() if l.strip().startswith("{")]
    if not lines:
        return {"score": None, "valid": False, "msg": f"no JSON line in output; exit {r.returncode}; stderr: {r.stderr[-400:]}"}
    try:
        c = json.loads(lines[-1])["circles"]
        c = [(float(x), float(y), float(rad)) for x, y, rad in c]
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        return {"score": None, "valid": False, "msg": f"bad JSON: {e}"}
    if len(c) != N:
        return {"score": None, "valid": False, "msg": f"{len(c)} circles, need {N}"}
    for k, (x, y, rad) in enumerate(c):
        if not (rad > 0 and x - rad >= -TOL and x + rad <= 1 + TOL and y - rad >= -TOL and y + rad <= 1 + TOL):
            return {"score": None, "valid": False, "msg": f"circle {k} ({x:.4f}, {y:.4f}, r={rad:.4f}) outside the square or r <= 0"}
    for i in range(N):
        for j in range(i + 1, N):
            d = math.hypot(c[i][0] - c[j][0], c[i][1] - c[j][1])
            if d < c[i][2] + c[j][2] - TOL:
                return {"score": None, "valid": False, "msg": f"circles {i} and {j} overlap by {c[i][2] + c[j][2] - d:.2e}"}
    return {"score": round(sum(x[2] for x in c), 6), "valid": True, "msg": "ok"}


print(json.dumps(main()))
