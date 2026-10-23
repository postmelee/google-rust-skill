#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fetch pinned development references; never needed to use the skill (MIT)."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def fetch(repository, commit, path, destination, expected=None, git_blob=None):
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("References must use a full immutable commit SHA")
    destination = Path(destination)
    if destination.exists():
        data = destination.read_bytes()
    else:
        url = f"https://raw.githubusercontent.com/{repository}/{commit}/{path}"
        request = urllib.request.Request(url, headers={"User-Agent": "google-rust-skill-source-check"})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
    if expected and hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"SHA-256 mismatch: {destination}")
    actual_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if git_blob and actual_blob != git_blob:
        raise ValueError(f"Git blob mismatch: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        destination.write_bytes(data)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream-only", action="store_true")
    args = parser.parse_args()
    upstream = json.loads((ROOT / "provenance/upstream.json").read_text())
    print(fetch(upstream["repository"], upstream["commit"], upstream["path"],
                ROOT / ".cache/upstream/rustguide.md", git_blob=upstream["blob"]))
    if not args.upstream_only:
        baselines = json.loads((ROOT / "provenance/baselines.json").read_text())
        for entry in baselines["baselines"]:
            print(fetch(entry["repository"], entry["commit"], entry["path"],
                        ROOT / ".cache/baselines" / entry["condition"] / entry["destination"],
                        expected=entry["sha256"]))


if __name__ == "__main__":
    main()
