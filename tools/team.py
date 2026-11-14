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
from concurrent.futures import ThreadPoolExecutor

BUCKET = "iterate-hack-team-769063704696"
PROFILE = "iterate-ecr"


@functools.cache
def s3():
    import boto3

    return boto3.Session(profile_name=PROFILE, region_name="us-east-1").client("s3")


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
        pages = s3().get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=f"{self.name}/")
        keys = [o["Key"][len(self.name) + 1:-len(".json")] for page in pages for o in page.get("Contents", [])]
        with ThreadPoolExecutor(32) as pool:
            return list(zip(keys, pool.map(self.__getitem__, keys)))
