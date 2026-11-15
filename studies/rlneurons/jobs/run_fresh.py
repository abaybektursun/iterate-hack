"""run_cell with one more problem set: --set fresh2026 = data/fresh/fresh2026_v1.json (specs/SPEC_fresh.md), competition problems
published in 2026. Every other argument and all behaviour are run_cell's. The set is registered here and not in run_cell.py
because run_cell.py was being edited by another session (board work-ab6833) when this was written.

    /opt/rln-vllm/bin/python -m studies.rlneurons.jobs.run_fresh --model rl --prompt plain --set fresh2026 --temperature 1.0 --top-p 1.0 --seed 7000000 --commit ...
"""
from __future__ import annotations

import argparse
import json

from studies.rlneurons.jobs import run_cell as C

NAME = "fresh2026"
PATH = C.STUDY / "data" / "fresh" / "fresh2026_v1.json"
SHA256 = "dcf571ea8a4654228e17975e8c1e255e50072f74061c9b083f5aad5c21d8e7d7"
_problems, _add_argument = C.problems, argparse.ArgumentParser.add_argument


def problems(name, fz):
    if name != NAME:
        return _problems(name, fz)
    assert C.sha(PATH) == SHA256, f"{PATH} differs from the frozen set"
    return json.loads(PATH.read_text())


def add_argument(self, *names, **kw):
    if names == ("--set",):
        kw["choices"] = (*kw["choices"], NAME)
    return _add_argument(self, *names, **kw)


if __name__ == "__main__":
    C.problems, argparse.ArgumentParser.add_argument = problems, add_argument
    C.main()
