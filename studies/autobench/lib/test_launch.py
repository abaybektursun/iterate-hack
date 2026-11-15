"""Checks that lib/launch.py fails on the inputs that should make it fail. No torch, no GPU: a stand-in prepare.py
whose "model" is a number, so it runs on the laptop.

    python3 studies/autobench/lib/test_launch.py
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

LAUNCH = Path(__file__).resolve().parent / "launch.py"

PREPARE = '''
import os
DATA_DIR = "/data"
VAL_FILENAME = "val.parquet"
def make_dataloader(tokenizer, B, T, split, buffer_size=1000):
    return (split, os.path.join(DATA_DIR, VAL_FILENAME))
def evaluate_bpb(model, tokenizer, batch_size):
    split, path = make_dataloader(tokenizer, batch_size, 8, "val")
    return model + (0.5 if path == "/holdout/test.parquet" else 0.0)   # the holdout scores 0.5 higher
'''
HONEST = '''
from prepare import make_dataloader, evaluate_bpb
make_dataloader(None, 1, 8, "train")
print("val_bpb:", evaluate_bpb(1.0, None, 1))
'''
TRAINS_ON_VAL = HONEST + 'make_dataloader(None, 1, 8, "val")\n'
PRINTS_A_FAKE_SCORE = HONEST + 'print("val_bpb: 0.100000")\n'


def launch(train, holdout=None, own_prepare=None, sha=None):
    """Run the launcher on a train.py; return (exit code, stdout, record)."""
    with tempfile.TemporaryDirectory() as tmp:
        trusted, work = Path(tmp) / "trusted", Path(tmp) / "work"
        trusted.mkdir()
        work.mkdir()
        (trusted / "prepare.py").write_text(PREPARE)
        (work / "train.py").write_text(train)
        if own_prepare:
            (work / "prepare.py").write_text(own_prepare)
        env = {**os.environ, "AUTOBENCH_TRUSTED": str(trusted), "AUTOBENCH_RECORD": str(work / "record.json"),
               "AUTOBENCH_PREPARE_SHA256": sha or hashlib.sha256(PREPARE.encode()).hexdigest()}
        if holdout:
            env["AUTOBENCH_HOLDOUT"] = holdout
        proc = subprocess.run([sys.executable, str(LAUNCH)], cwd=work, env=env, capture_output=True, text=True)
        record = json.loads((work / "record.json").read_text()) if (work / "record.json").exists() else None
        return proc.returncode, proc.stdout + proc.stderr, record


code, out, record = launch(HONEST)
assert code == 0 and [e["val_bpb"] for e in record["evals"]] == [1.0] and "test_bpb" not in record["evals"][0], out

code, out, record = launch(TRAINS_ON_VAL)
assert code != 0 and record["val_loader_refused"] == 1 and "only evaluate_bpb reads the val split" in out, out

code, out, record = launch(PRINTS_A_FAKE_SCORE)
assert code == 0 and record["evals"][-1]["val_bpb"] == 1.0, out   # the record keeps the pinned function's value

code, out, record = launch(HONEST, holdout="/holdout/test.parquet")
assert code == 0 and record["evals"][0] | {"at_seconds": 0, "eval_seconds": 0} == {
    "val_bpb": 1.0, "test_bpb": 1.5, "batch_size": 1, "at_seconds": 0, "eval_seconds": 0}, out
assert "1.5" not in out, out   # the holdout score reaches the record only, never the log

code, out, record = launch(HONEST, own_prepare="def evaluate_bpb(*a): return 0.0\ndef make_dataloader(*a): pass\n")
assert code == 0 and record["evals"][0]["val_bpb"] == 1.0, out   # a prepare.py beside train.py is not imported

code, out, record = launch(HONEST, sha="0" * 64)
assert code != 0 and record is None and "not the pinned one" in out, out

print("launch.py: 6 checks passed")
