"""Inputs of the drive-01 job (specs/SPEC_direct_drive.md), from the stored answer files of two Modal jobs:

    modal volume get iterate-runs abaybektursun-1114-170304-c03c/answers.jsonl runs/inputs/code_cue_answers.jsonl
    modal volume get iterate-runs abaybektursun-1114-151534-e72c/answers.jsonl runs/inputs/math_cue_answers.jsonl
    python3 studies/theory/prep/drive_inputs.py

Writes studies/theory/data/drive/code_cue_answers_v1.jsonl.gz (all 538 rows, the fields the job reads) and
math_check_v1.jsonl.gz (16 whole rows of the 328 math answers, evenly spaced in traced length, for the reproduction check).
"""
import gzip
import hashlib
import json
import pathlib

SRC = pathlib.Path("runs/inputs")
OUT = pathlib.Path("studies/theory/data/drive")
CODE_SHA = "3b18494b1b7f28cec46f3100adcadb0a40f97e5fbdafb92e6daf59a0aa236457"
MATH_SHA = "4a3cc0bf4596e5f8282b323637daf9cf1ede4837446ef001cea7b7c42d3f421b"
KEEP = ("bench", "idx", "uid", "prompt", "prefix_ids", "text", "n_new", "cap_hit", "passed", "mode")
N_CHECK, MAX_TOKENS = 16, 6000


def read(path, sha):
    b = path.read_bytes()
    assert hashlib.sha256(b).hexdigest() == sha, f"{path} is not the expected file"
    return [json.loads(l) for l in b.decode().splitlines()]


def write(path, rows):
    with gzip.GzipFile(path, "wb", mtime=0) as f:
        f.write("".join(json.dumps(r) + "\n" for r in rows).encode())
    print(path, len(rows), path.stat().st_size)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    code = read(SRC / "code_cue_answers.jsonl", CODE_SHA)
    assert len(code) == 538, len(code)
    write(OUT / "code_cue_answers_v1.jsonl.gz", [{k: r[k] for k in KEEP} for r in code])
    math = read(SRC / "math_cue_answers.jsonl", MATH_SHA)
    assert len(math) == 328, len(math)
    srt = sorted(math, key=lambda r: (min(r["n_new"] + 3, MAX_TOKENS), r["problem_index"]))
    pick = [srt[round(i * (len(srt) - 1) / (N_CHECK - 1))] for i in range(N_CHECK)]
    write(OUT / "math_check_v1.jsonl.gz", pick)


if __name__ == "__main__":
    main()
