"""The team store, in Abay's AWS account (us-east-1): the DynamoDB table iterate-board holds the board and the
messages, and the S3 bucket iterate-hack-team-769063704696 holds the events and the traces. Modal is not used for
it, because each person has their own Modal workspace.

Access is through the AWS profile iterate-ecr (README, Setup step 2). The same key pulls the ECR images. It can
read and write the table and the bucket, cannot delete from either, and stops working Sunday 2026-11-15 at 23:59
PST.

Every stored time is UTC, written as 2026-11-14T20:15:02Z. With ITERATE_TEST=1 in the environment the tools use
the table iterate-board-test and the S3 prefix test/, which is what tools/selftest.py does.
"""
import functools
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TEST = os.environ.get("ITERATE_TEST") == "1"
BUCKET = "iterate-hack-team-769063704696"
PREFIX = "test/" if TEST else ""
TABLE = "iterate-board-test" if TEST else "iterate-board"
PROFILE = "iterate-ecr"
CACHE = Path.home() / ".cache" / ("iterate-hack-test" if TEST else "iterate-hack")


def who():
    """A person's name on the board, in channels and in job ids: the part of their git email before the @, without the
    number GitHub puts in front of a noreply address (82460915+sameraslan@users.noreply.github.com -> sameraslan)."""
    email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout.strip()
    return email.split("@")[0].split("+")[-1]


def review_loop(name):
    """True when one agent runs the team-meta-review skill in a loop for this person (it keeps meta/loop/<name>.md).
    board.py and gpu.py then do not ask this person's other agents to run a review."""
    return (Path(__file__).resolve().parent.parent / "meta" / "loop" / f"{name}.md").exists()


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@functools.cache
def session():
    import boto3

    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):  # the board page on Lambda (infra/monitor): the function's role
        return boto3.Session(region_name="us-east-1")
    if PROFILE not in boto3.Session().available_profiles:
        sys.exit(f"no AWS profile '{PROFILE}' on this machine. Get the team AWS key from Abay and run\n"
                 f"  aws configure --profile {PROFILE}\n(README.md, Setup step 2).")
    return boto3.Session(profile_name=PROFILE, region_name="us-east-1")


@functools.cache
def s3():
    from botocore.config import Config

    return session().client("s3", config=Config(max_pool_connections=64))


@functools.cache
def table():
    from botocore.config import Config

    retries = Config(retries={"max_attempts": 12, "mode": "adaptive"})  # a burst of writers is throttled for a few seconds
    return session().resource("dynamodb", config=retries).Table(TABLE)


class Store:
    """A prefix of JSON objects in the bucket, one object per key."""

    def __init__(self, name):
        self.name = PREFIX + name

    def __getitem__(self, key):
        try:
            body = s3().get_object(Bucket=BUCKET, Key=f"{self.name}/{key}.json")["Body"].read()
        except s3().exceptions.NoSuchKey:
            raise KeyError(key) from None
        return json.loads(body)

    def __setitem__(self, key, value):
        body = json.dumps(value, indent=1, sort_keys=True).encode()
        s3().put_object(Bucket=BUCKET, Key=f"{self.name}/{key}.json", Body=body, ContentType="application/json")

    def items(self):
        """Every key and value. One listing call per 1000 objects gives each object's ETag; only objects that are
        new or changed since the last call on this machine are downloaded, the rest come from CACHE."""
        cache_file = CACHE / f"{self.name.replace('/', '_')}.json"
        cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
        pages = s3().get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=f"{self.name}/")
        etags = {o["Key"][len(self.name) + 1:-len(".json")]: o["ETag"] for page in pages for o in page.get("Contents", [])}
        changed = [key for key, etag in etags.items() if cache.get(key, [None])[0] != etag]
        with ThreadPoolExecutor(64) as pool:
            for key, value in zip(changed, pool.map(self.__getitem__, changed)):
                cache[key] = [etags[key], value]
        cache = {key: cache[key] for key in etags}
        CACHE.mkdir(parents=True, exist_ok=True)
        temporary = cache_file.with_suffix(f".{os.getpid()}.tmp")  # several agents of one person share the cache
        temporary.write_text(json.dumps(cache))
        temporary.replace(cache_file)
        return [(key, entry[1]) for key, entry in cache.items()]
