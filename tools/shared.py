# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Team credentials, shared through the private team store (tools/team.py, folder shared) instead of chat.

  uv run tools/shared.py setup              install every shared credential on this machine
  uv run tools/shared.py put ecr <file>     (the owner) store the ECR pull key; <file> is the JSON from `aws iam create-access-key`
  uv run tools/shared.py put past           (the owner) store the past.dev project key; it is typed at a hidden prompt

Whoever can read the repository abaybektursun/iterate-hack-team can read them. setup writes:
  ecr   the AWS profile iterate-ecr (region us-east-1), which tools/vast.py uses for `up --image <ECR image>`
  past  ~/.past/config.json with your git email as identity and recall off; an existing file is left unchanged
No command prints a credential.
"""
import getpass
import json
import os
import subprocess
import sys
from pathlib import Path

import team


def put(name, *args):
    if name == "ecr":
        key = json.loads(Path(args[0]).read_text())["AccessKey"]
        value = {"id": key["AccessKeyId"], "secret": key["SecretAccessKey"]}
    else:
        assert name == "past", "name must be ecr or past"
        value = {"key": getpass.getpass("past.dev project key (hidden): ").strip()}
    team.Store("shared")[name] = value
    print(f"stored {name}")


def setup():
    shared = dict(team.Store("shared").items())
    if "ecr" in shared:
        for field, value in (("aws_access_key_id", shared["ecr"]["id"]), ("aws_secret_access_key", shared["ecr"]["secret"]),
                             ("region", "us-east-1")):
            subprocess.run(["aws", "configure", "set", field, value, "--profile", "iterate-ecr"], check=True)
        print("ecr: wrote the AWS profile iterate-ecr")
    config = Path.home() / ".past" / "config.json"
    if "past" in shared and config.exists():
        print(f"past: {config} exists, left unchanged")
    elif "past" in shared:
        email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout.strip()
        config.parent.mkdir(exist_ok=True)
        config.touch(mode=0o600)
        config.write_text(json.dumps({"apiKey": shared["past"]["key"], "identity": email, "recall": False}, indent=1))
        print(f"past: wrote {config}")
    print("not shared yet: " + (", ".join(sorted({"ecr", "past"} - set(shared))) or "nothing"))


if __name__ == "__main__":
    command, *args = sys.argv[1:] or ["help"]
    {"put": put, "setup": setup}.get(command, lambda *_: sys.exit(__doc__))(*args)
