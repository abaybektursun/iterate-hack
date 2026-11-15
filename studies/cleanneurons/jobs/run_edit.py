"""cleanneurons Part G (specs/SPEC1.md): one rlneurons cell (jobs/run_cell.py, unchanged: vLLM, graders, row format) on the base with
an edit file applied. Runs in run_cell's venv:

    uv run tools/gpu.py submit h100 --hours 1.5 -- "bash studies/rlneurons/jobs/setup_vllm.sh && /opt/rln-vllm/bin/python -m studies.cleanneurons.jobs.run_edit
        --edit studies/cleanneurons/results/<experiment>/<run>/edit_loop.json -- --model base --prompt cue --set math500
        --temperature 0.6 --top-p 1.0 --seed 1000000 --commit $(git rev-parse HEAD)"

  --edit   repository path of an edit file (lib/neurons.py holds the format). Everything after `--` goes to run_cell as it is;
           --model must be base.

Steps: download the base snapshot (and RL's when the edit copies anything) with run_cell's snapshot_download call; build the edited
checkpoint in a local temporary directory (neurons.build_checkpoint: the shards that hold an edited tensor are rewritten, every other
file is a link); check it (neurons.diff_checkpoint: tensor by tensor against the base, exactly the entries the edit names differ);
then run_cell.main() with huggingface_hub.snapshot_download replaced by a function that returns the built directory for run_cell's
one download of the model's weights and passes every other call through. That call must happen exactly once (asserted). The
temporary directory is removed when run_cell returns or fails.

Writes next to run_cell's answers.jsonl and metrics.json (whose engine.model_dir is the built directory):
  edit.json    the edit file, byte for byte
  build.json   edit path and sha256, package versions, build_checkpoint's record (shards rewritten, files linked, tensors named, their
               dtypes, neurons copied and zeroed), diff (tensors loaded, entries named, entries that differ, tensors that differ),
               seconds, model_download_calls
With run_cell's --dry-run there are no weights: the build is skipped, build.json says so, and the replaced download must see no
call for the model's weights. Fail loud: no fallback; the try/finally only removes the temporary directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import sys
import tempfile
import time
from importlib import metadata

import huggingface_hub

from studies.cleanneurons.lib import neurons as N
from studies.rlneurons.jobs import run_cell as C
from studies.rlneurons.lib import n13_gen as G

PATTERNS = ["*.json", "*.safetensors", "*.jinja", "*.txt"]            # run_cell's model download


def main():
    argv = sys.argv[1:]
    assert "--" in argv, "usage: run_edit --edit <edit json> -- <run_cell arguments>"
    cut = argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("--edit", required=True)
    a = ap.parse_args(argv[:cut])
    cp = argparse.ArgumentParser(add_help=False, allow_abbrev=False)  # the three run_cell arguments this wrapper reads
    cp.add_argument("--model")
    cp.add_argument("--out", default=os.environ.get("OUT_DIR"))
    cp.add_argument("--dry-run", action="store_true")
    c, _ = cp.parse_known_args(argv[cut + 1:])
    assert c.model == "base", "an edit applies to the base: run_cell needs --model base"
    assert c.out, "no --out and no $OUT_DIR"
    out = pathlib.Path(c.out)
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "build.json").exists(), f"{out}/build.json exists: one fresh directory per run"

    raw = pathlib.Path(a.edit).read_bytes()
    edit = N.check_edit(json.loads(raw))
    (out / "edit.json").write_bytes(raw)
    fz = json.loads((C.D4 / "frozen4.json").read_text())
    repo, _, rev = fz["models"][C.MODELS["base"]]
    rl_repo, _, rl_rev = fz["models"][C.MODELS["rl"]]
    build = {"edit": a.edit, "edit_sha256": hashlib.sha256(raw).hexdigest(), "name": edit["name"], "dry_run": c.dry_run,
             "versions": {k: metadata.version(k) for k in ("torch", "safetensors", "huggingface_hub")},
             "base": [repo, rev], "rl": [rl_repo, rl_rev] if N.copies(edit) else None}
    real, built, t0 = huggingface_hub.snapshot_download, None, time.time()
    if c.dry_run:
        build["built"], build["why"] = False, "run_cell --dry-run: no weights, so no checkpoint is built"
    else:
        base_dir = real(repo, revision=rev, allow_patterns=PATTERNS)
        rl_dir = real(rl_repo, revision=rl_rev, allow_patterns=PATTERNS) if N.copies(edit) else None
        built = tempfile.mkdtemp(prefix="cleanneurons_")
        build.update(built=True, **N.build_checkpoint(base_dir, rl_dir, edit, built))
        build["build_s"] = time.time() - t0
        build["diff"] = N.diff_checkpoint(built, base_dir, rl_dir, edit)
        build["diff_s"] = time.time() - t0 - build["build_s"]
    G.dump(out / "build.json", build)

    hits = []

    def download(repo_id, *args, **kw):
        if "*.safetensors" not in (kw.get("allow_patterns") or ()):
            return real(repo_id, *args, **kw)
        assert built and repo_id == repo and kw.get("revision") == rev and not args, ("unexpected download of weights", repo_id, kw)
        hits.append(repo_id)
        return built

    huggingface_hub.snapshot_download = download                 # run_cell imports the name inside main()
    sys.argv = ["run_cell", *argv[cut + 1:]]
    try:
        C.main()
    finally:
        huggingface_hub.snapshot_download = real
        if built:
            shutil.rmtree(built)
    assert len(hits) == (0 if c.dry_run else 1), f"run_cell downloaded the model's weights {len(hits)} times"
    build["model_download_calls"] = len(hits)
    G.dump(out / "build.json", build)


if __name__ == "__main__":
    main()
