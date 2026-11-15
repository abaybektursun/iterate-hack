"""Shard k of N of one rlneurons cell: the problems at positions k, k+N, k+2N, ... of the set, through the unchanged
studies/rlneurons/jobs/run_cell.py. The change named in meta/abaybektursun.md (2026-11-14 21:21 UTC) and not landed; this
wrapper exists so SPEC1 Part B can measure it without a second writer in run_cell.py. Delete it when run_cell.py has --shard.

    /opt/rln-vllm/bin/python -m studies.metaharness.jobs.shard_cell --shard 0/4 <the run_cell.py arguments>

Seeds are per problem index (seed + 10000 * sample + 1000 * attempt + index), so every request is the one the whole cell
sends. Each shard writes its own answers.jsonl and metrics.json to its own $OUT_DIR.
"""
import sys

from studies.rlneurons.jobs import run_cell


def main():
    at = sys.argv.index("--shard")
    k, n = (int(x) for x in sys.argv[at + 1].split("/"))
    assert 0 <= k < n, f"--shard {sys.argv[at + 1]}: need 0 <= k < N"
    del sys.argv[at:at + 2]
    whole = run_cell.problems
    run_cell.problems = lambda name, fz: whole(name, fz)[k::n]
    run_cell.main()


if __name__ == "__main__":
    main()
