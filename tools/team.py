"""The team store: the S3 bucket iterate-hack-team-769063704696 (us-east-1, in Abay's AWS account), which holds
what the team shares: the board, the events and the traces. Modal is not used for it, because each person has
their own Modal workspace.

Access is through the AWS profile iterate-ecr, which `uv run tools/shared.py setup` writes. The same key pulls
the ECR images. It can read and write objects in this bucket, cannot delete them, and stops working Sunday
2026-11-15 at 23:59 PST. The bucket keeps every version of every object.

A Store is a prefix of JSON objects, one object per key, so two writers never touch the same object. When two
writers do write the same key, the later write wins.
"""
import functools
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BUCKET = "iterate-hack-team-769063704696"
PROFILE = "iterate-ecr"
CACHE = Path.home() / ".cache" / "iterate-hack"


@functools.cache
def s3():
    import boto3
    from botocore.config import Config

    return boto3.Session(profile_name=PROFILE, region_name="us-east-1").client("s3", config=Config(max_pool_connections=64))


class Store:
    def __init__(self, name):
        self.name = name

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
        cache_file = CACHE / f"{self.name}.json"
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
