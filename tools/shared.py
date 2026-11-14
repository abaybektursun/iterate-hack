# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Team credentials, shared through the private GitHub repository abaybektursun/iterate-hack-team instead of chat.

  uv run tools/shared.py setup              install every shared credential on this machine
  uv run tools/shared.py put aws <file>     (the owner) store the team AWS key; <file> is the JSON from `aws iam create-access-key`
  uv run tools/shared.py put past           (the owner) store the past.dev project key; it is typed at a hidden prompt

Whoever can read that repository can read them (needs `gh auth login`). It is cloned to ~/.iterate-hack-team.
setup writes:
  aws   the AWS profile iterate-ecr (region us-east-1): the team store on S3 (board, events, traces) and the
        ECR images for `tools/vast.py up --image`
  past  ~/.past/config.json with your git email as identity and recall off; an existing file is left unchanged
No command prints a credential.
"""
import getpass
import json
import subprocess
import sys
from pathlib import Path

REPO = "abaybektursun/iterate-hack-team"
DIR = Path.home() / ".iterate-hack-team"


def git(*args):
    subprocess.run(["git", "-C", str(DIR), *args], check=True)


def sync():
    if DIR.exists():
        git("pull", "-q", "--rebase")
    else:
        subprocess.run(["gh", "repo", "clone", REPO, str(DIR), "--", "-q"], check=True)


def put(name, *args):
    if name == "aws":
        key = json.loads(Path(args[0]).read_text())["AccessKey"]
        value = {"id": key["AccessKeyId"], "secret": key["SecretAccessKey"]}
    else:
        assert name == "past", "name must be aws or past"
        value = {"key": getpass.getpass("past.dev project key (hidden): ").strip()}
    sync()
    (DIR / "shared").mkdir(exist_ok=True)
    (DIR / "shared" / f"{name}.json").write_text(json.dumps(value))
    git("add", f"shared/{name}.json")
    git("commit", "-qm", f"shared: {name}")
    git("push", "-q")
    print(f"stored {name}")


def setup():
    sync()
    shared = {p.stem: json.loads(p.read_text()) for p in (DIR / "shared").glob("*.json")}
    if "aws" in shared:
        for field, value in (("aws_access_key_id", shared["aws"]["id"]), ("aws_secret_access_key", shared["aws"]["secret"]),
                             ("region", "us-east-1")):
            subprocess.run(["aws", "configure", "set", field, value, "--profile", "iterate-ecr"], check=True)
        print("aws: wrote the AWS profile iterate-ecr")
    config = Path.home() / ".past" / "config.json"
    if "past" in shared and config.exists():
        print(f"past: {config} exists, left unchanged")
    elif "past" in shared:
        email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout.strip()
        config.parent.mkdir(exist_ok=True)
        config.touch(mode=0o600)
        config.write_text(json.dumps({"apiKey": shared["past"]["key"], "identity": email, "recall": False}, indent=1))
        print(f"past: wrote {config}")
    print("not shared yet: " + (", ".join(sorted({"aws", "past"} - set(shared))) or "nothing"))


if __name__ == "__main__":
    command, *args = sys.argv[1:] or ["help"]
    {"put": put, "setup": setup}.get(command, lambda *_: sys.exit(__doc__))(*args)
