"""Three helpers the rlneurons jobs import, copied verbatim from interp_research (clean-neurons, 6ec0f0f90) so the jobs do not
pull in the unrelated modules they lived in:
  hf_setup          from infra/pg/humboldt_core.py
  hf_online_setup   from infra/pg/diff_harvest.py
  retry_transport   from infra/pg/mercator_core.py
hf_online_setup reads the Hugging Face token from HF_TOKEN; without it, it falls back to the AWS SSM parameter of the owner's
account (/pg-lineage/hf-token), which a teammate cannot read: set HF_TOKEN (the Modal secret hf-token does).
"""
from __future__ import annotations

import os


def hf_setup():
    """§0.2.7 env pins, in the one place every HUMBOLDT job calls FIRST, before importing
    transformers/datasets. HF_HUB_DISABLE_XET=1 is the house fix for the Xet download wedge
    (reference_hf_xet_wedge); hf_online_setup authenticates the gated Gemma/PaliGemma repos."""
    os.environ["HF_HUB_DISABLE_XET"] = "1"
    # A DOWNLOAD THAT HANGS IS WORSE THAN ONE THAT FAILS. Without a timeout `snapshot_download`
    # can sit on a stalled connection indefinitely: the re-census wedged mid-shard on a 7B model
    # and held a live instance with a frozen log for five hours until the reaper took it, and a
    # retry cannot help because a hang raises nothing (M-D97). Set HERE rather than in the one job
    # that hung, so every downloading job in the program gets it.
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "60")
    hf_online_setup()


def hf_online_setup():
    """Set HF_TOKEN (from SSM via the instance role) + online mode, so the GATED PaliGemma/Gemma
    repos load (cache-backed but authenticated — run_job.sh's HF_HUB_OFFLINE=1 would force an
    unauthenticated offline path that still 401s on a gated metadata check) AND the probe datasets
    can stream. Call FIRST in a job main(), before any transformers/datasets import. Fail-loud."""
    import os
    import subprocess
    if os.environ.get("HF_TOKEN"):
        # already provisioned (e.g. a Vast box with no aws CLI/creds — the launcher ships the
        # read-scoped token via env); just flip online mode.
        os.environ["HF_HUB_OFFLINE"] = "0"
        os.environ["HF_DATASETS_OFFLINE"] = "0"
        return
    tok = subprocess.run(
        ["aws", "ssm", "get-parameter", "--name", "/pg-lineage/hf-token", "--with-decryption",
         "--query", "Parameter.Value", "--output", "text", "--region", "us-east-1"],
        check=True, capture_output=True, text=True).stdout.strip()
    if not tok:
        raise RuntimeError("empty HF token from SSM /pg-lineage/hf-token")
    os.environ["HF_TOKEN"] = tok
    os.environ["HF_HUB_OFFLINE"] = "0"
    os.environ["HF_DATASETS_OFFLINE"] = "0"


def retry_transport(fn, *, what: str, attempts: int = 4):
    """Call `fn()`, retrying a TRANSPORT failure a bounded number of times. Returns (value, n_retry).

    A SYSTEM boundary, not a scientific one — the same carve-out `mercator_rowgram` documents and
    the only kind this program guards. An arm that streams a dozen multi-gigabyte checkpoints will
    eventually meet `peer closed connection without sending complete message body` mid-file, and
    M-D2 lost a run to one after it had already trained its dictionary to FVU 0.4372 (M-D67).

    Only transport errors are caught. A missing repo, a gated repo, a shape mismatch or anything
    scientific still propagates on the first occurrence, and the retry count is returned so a flaky
    run is visible in the artifact rather than indistinguishable from a clean one.
    """
    import time
    import httpx
    from huggingface_hub.errors import HfHubHTTPError
    transient = (httpx.RemoteProtocolError, httpx.ReadError, httpx.ConnectError,
                 httpx.ReadTimeout, httpx.WriteError, HfHubHTTPError, ConnectionError)
    last = None
    for i in range(attempts):
        try:
            return fn(), i
        except transient as e:            # noqa: PERF203 - a bounded transport retry, counted
            last = e
            print(f"[retry] transport failure on {what} (attempt {i + 1}/{attempts}): "
                  f"{type(e).__name__}: {str(e)[:160]}", flush=True)
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"{what}: {attempts} transport attempts failed; last was "
                       f"{type(last).__name__}: {last}")
