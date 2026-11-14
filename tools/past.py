"""Calls to the past.dev Memory API, with the key and identity from ~/.past/config.json.

PAST_API_KEY and PAST_IDENTITY in the environment override the file.
API reference: https://past.dev/docs/memory-api/api-reference
"""
import json
import os
import urllib.request
from pathlib import Path

_config_path = Path.home() / ".past" / "config.json"
_config = json.loads(_config_path.read_text()) if _config_path.exists() else {}
KEY = os.environ.get("PAST_API_KEY") or _config["apiKey"]
IDENTITY = os.environ.get("PAST_IDENTITY") or _config["identity"]


def call(method, path, body=None):
    request = urllib.request.Request(
        f"https://api.past.dev/api/v1/{path}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(request))
