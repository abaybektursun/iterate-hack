"""The team's Modal workspace, which holds the shared stores: the board, the events and the traces.

GPU jobs run in each person's own workspace (the active Modal profile), paid from their own credits. The shared
stores live in one workspace, abaybektursun, reached through the Modal profile of the same name. Setup, once:

  modal token new --profile abaybektursun --no-activate     # in the browser, pick the workspace abaybektursun

The stores are looked up with create_if_missing=False, so a profile that points at the wrong workspace fails
with NotFoundError instead of writing to an empty board.
"""
import functools
import os
import sys
import tomllib
from pathlib import Path

PROFILE = "abaybektursun"


@functools.cache
def client():
    import modal

    profiles = tomllib.loads(Path(os.environ.get("MODAL_CONFIG_PATH", Path.home() / ".modal.toml")).read_text())
    if PROFILE not in profiles:
        sys.exit(f"no Modal profile '{PROFILE}' for the team workspace. Run, once:\n"
                 f"  modal token new --profile {PROFILE} --no-activate\n"
                 f"and pick the workspace {PROFILE} in the browser (ask Abay for an invite first).")
    return modal.Client.from_credentials(profiles[PROFILE]["token_id"], profiles[PROFILE]["token_secret"])


def store(kind, name):
    """kind is modal.Dict or modal.Volume."""
    return kind.from_name(name, client=client())
