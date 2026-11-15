"""Trusted launcher for one experiment. Runs inside the GPU container, in a directory that holds only train.py:

    python /trusted/launch.py

It loads the pinned prepare.py from $AUTOBENCH_TRUSTED (default /trusted) before train.py runs, so a prepare.py
written by an agent is never imported. It then replaces two functions of that module:

  make_dataloader   refuses the val split unless evaluate_bpb is the caller (train.py cannot train on val)
  evaluate_bpb      computes val_bpb as before and writes it to $AUTOBENCH_RECORD, so the score of record is the
                    returned value of the pinned function, not a line that train.py printed. When
                    $AUTOBENCH_HOLDOUT names a parquet file, it also scores the same model on that file
                    (test_bpb) and writes it to the record only: train.py and the log never see it.

train.py runs in this same process, so this is evidence of tampering, not a sandbox: a train.py that patches
these functions back is caught by analysis/audit.py and by reading the diff, not here.
"""
import hashlib
import json
import os
import runpy
import sys
import time

T0 = time.time()
TRUSTED = os.environ.get("AUTOBENCH_TRUSTED", "/trusted")
RECORD = os.environ["AUTOBENCH_RECORD"]
HOLDOUT = os.environ.get("AUTOBENCH_HOLDOUT")

sys.path.insert(0, TRUSTED)
import prepare  # noqa: E402  the pinned module; train.py's "from prepare import ..." gets this one

with open(prepare.__file__, "rb") as f:
    digest = hashlib.sha256(f.read()).hexdigest()
if digest != os.environ["AUTOBENCH_PREPARE_SHA256"]:
    sys.exit(f"autobench: {prepare.__file__} has sha256 {digest}, not the pinned one")

record = {"prepare_sha256": digest, "evals": [], "val_loader_refused": 0}
in_eval = False
pinned_loader = prepare.make_dataloader
pinned_eval = prepare.evaluate_bpb


def write_record():
    with open(RECORD, "w") as f:
        json.dump(record, f)


def make_dataloader(tokenizer, B, T, split, buffer_size=1000):
    if split != "train" and not in_eval:
        record["val_loader_refused"] += 1
        write_record()
        raise RuntimeError("autobench: only evaluate_bpb reads the val split")
    return pinned_loader(tokenizer, B, T, split, buffer_size)


def evaluate_bpb(model, tokenizer, batch_size):
    global in_eval
    in_eval = True
    try:
        start = time.time()
        val_bpb = pinned_eval(model, tokenizer, batch_size)
        entry = {"val_bpb": val_bpb, "at_seconds": round(start - T0, 1), "eval_seconds": round(time.time() - start, 1),
                 "batch_size": batch_size}
        if HOLDOUT:
            saved = prepare.DATA_DIR, prepare.VAL_FILENAME
            prepare.DATA_DIR, prepare.VAL_FILENAME = os.path.split(HOLDOUT)
            try:
                entry["test_bpb"] = pinned_eval(model, tokenizer, batch_size)
            finally:
                prepare.DATA_DIR, prepare.VAL_FILENAME = saved
    finally:
        in_eval = False
    record["evals"].append(entry)
    write_record()
    return val_bpb


prepare.make_dataloader = make_dataloader
prepare.evaluate_bpb = evaluate_bpb
write_record()
runpy.run_path("train.py", run_name="__main__")
