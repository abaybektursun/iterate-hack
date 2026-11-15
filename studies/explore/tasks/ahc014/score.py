"""Scorer for ahc014 (Frontier-CS algorithmic problem 159, a port of AtCoder Heuristic Contest 014 "RectJoin").

    python score.py solution.py [--test]     prints {"score", "valid", "msg"} as one JSON line

The program reads one case on stdin and writes its operations to stdout, LIMIT seconds per case. Each output is
checked by the Frontier-CS checker (data/chk.cc, testlib, compiled once). Score: the mean over cases of V / V_best,
where V is AHC014's raw score and V_best is the reference best in the case's .ans file (Frontier-CS commit in
data/SOURCE_COMMIT). Validation: cases 1-5. --test: cases 6-10 (held out; only the analysis reads them).
Any case that fails (timeout, crash, checker rejects) makes the submission invalid.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

D = pathlib.Path(__file__).resolve().parent / "data"
LIMIT = 4  # seconds per case; the spec tells the program 3 s
CASES = {False: [1, 2, 3, 4, 5], True: [6, 7, 8, 9, 10]}


def checker():
    exe = D / "chk"
    if not exe.exists():  # compile once; os.replace makes concurrent first calls safe
        tmp = D / f"chk.{os.getpid()}"
        subprocess.run(["clang++", "-std=c++17", "-O2", "-I", str(D / "shim"), "-o", str(tmp), str(D / "chk.cc")],
                       check=True, capture_output=True)
        os.replace(tmp, exe)
    return exe


def main(prog, test):
    chk, ratios = checker(), []
    for i in CASES[test]:
        inp = (D / f"{i}.in").read_text()
        try:
            r = subprocess.run([sys.executable, prog], input=inp, capture_output=True, text=True, timeout=LIMIT)
        except subprocess.TimeoutExpired:
            return {"score": None, "valid": False, "msg": f"case {i}: program exceeded {LIMIT} s"}
        if r.returncode != 0:
            return {"score": None, "valid": False, "msg": f"case {i}: exit {r.returncode}; stderr: {r.stderr[-400:]}"}
        with tempfile.NamedTemporaryFile("w", suffix=".out", delete=False) as f:
            f.write(r.stdout)
        c = subprocess.run([str(chk), str(D / f"{i}.in"), f.name, str(D / f"{i}.ans")], capture_output=True, text=True)
        os.unlink(f.name)
        m = re.search(r"Value: (\d+)", c.stderr)
        if c.returncode not in (0, 7) or not m:  # testlib: 0 ok, 7 points; anything else is a rejected output
            return {"score": None, "valid": False, "msg": f"case {i}: checker rejected: {c.stderr.strip()[:400]}"}
        best = int((D / f"{i}.ans").read_text().split()[1])
        ratios.append(int(m.group(1)) / best)
    return {"score": round(sum(ratios) / len(ratios), 6), "valid": True,
            "msg": "per-case V/V_best: " + ", ".join(f"{x:.3f}" for x in ratios)}


print(json.dumps(main(sys.argv[1], "--test" in sys.argv)))
