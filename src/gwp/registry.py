"""Filesystem workflow registry with explicit, immutable versions."""
import json
from pathlib import Path


def load_workflow(root: Path, workflow_id: str, version: str) -> dict:
    for value in (workflow_id, version):
        if not value or value in {".", ".."} or not all(c.isalnum() or c in "-_" for c in value):
            raise ValueError("workflow identifiers must be simple names")
    path = root / workflow_id / (version + ".json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise ValueError("workflow must be a nonempty JSON object")
    return data
