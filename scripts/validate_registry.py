#!/usr/bin/env python3
"""Check that an observed source is never reported as GPU-qualified."""
import json
import re
from pathlib import Path

def validate(root):
    read = lambda file: json.loads((root / file).read_text(encoding="utf-8"))
    names = ["registry/official.json", "registry/community.json",
             "registry/practices.json", "dependencies/sources.lock.json"]
    if not all((root / file).exists() for file in names):
        raise ValueError("missing snapshot; run practice_registry.py")
    official, community, practices, lock = [read(name) for name in names]
    for part in (official, community, practices):
        key = "assets" if part is practices else "repositories"
        if part["count"] != len(part[key]):
            raise ValueError("inconsistent catalog count")
    repos = [r["repository"] for r in official["repositories"] + community["repositories"]]
    if len(repos) != len(set(repos)):
        raise ValueError("duplicate source")
    if any(not r["repository"].startswith("Comfy-Org/") for r in official["repositories"]):
        raise ValueError("foreign official repository")
    ids = [a["id"] for a in practices["assets"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate practice")
    for a in practices["assets"]:
        if a["source_repository"] not in repos or a["id"] != a["source_repository"] + ":" + a["path"]:
            raise ValueError("invalid provenance")
        if a["verification"] != "unverified":
            raise ValueError("unsafe automatic qualification")
        for key in ("source_commit", "blob_sha"):
            if not re.fullmatch(r"[0-9a-f]{40}", a[key]):
                raise ValueError("invalid SHA")
    for a in lock["sources"]:
        if a["state"] != "observed_not_deployed" or not re.fullmatch(r"[0-9a-f]{40}", a["revision"]):
            raise ValueError("unsafe or invalid dependency revision")
    if read("registry/decisions.json")["schema_version"] != 1:
        raise ValueError("invalid decision schema")
    print(f"Validated {official['count']} official, {community['count']} community and {practices['count']} practice entries")

if __name__ == "__main__":
    validate(Path(__file__).resolve().parents[1])
