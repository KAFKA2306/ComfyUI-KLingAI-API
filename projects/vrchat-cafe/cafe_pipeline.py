#!/usr/bin/env python3
"""VRChatカフェ用の出典保存とGLB形式検査。収集したWorkflowは実行しない。"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import struct
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
MAX_JSON = 3_000_000


def manifest_entries(root: Path) -> list[dict]:
    data = json.loads((root / "projects/vrchat-cafe/workflows.json").read_text(encoding="utf-8"))
    entries = data["workflows"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("workflow manifest must have entries")
    ids = set()
    for entry in entries:
        slug, repo, path = entry["id"], entry["repository"], entry["path"]
        if not ID_PATTERN.fullmatch(slug) or slug in ids:
            raise ValueError(f"invalid or duplicate id: {slug}")
        if not REPO_PATTERN.fullmatch(repo) or not path.startswith("templates/") or not path.endswith(".json") or ".." in path or "//" in path:
            raise ValueError(f"invalid source for {slug}")
        ids.add(slug)
    return entries


def github_json(path: str) -> dict:
    url = "https://api.github.com/" + path.lstrip("/")
    req = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "gwp-vrchat-cafe", "X-GitHub-Api-Version": "2022-11-28"})
    with urlopen(req, timeout=35) as response:
        return json.load(response)


def download_snapshot(entry: dict, get=github_json) -> tuple[bytes, dict]:
    repo, path = entry["repository"], entry["path"]
    # 取得前に参照先のコミットを確定する。
    meta = get(f"repos/{repo}")
    branch = meta["default_branch"]
    commit = get(f"repos/{repo}/commits/{quote(branch, safe='')}")["sha"]
    item = get(f"repos/{repo}/contents/{quote(path, safe='/')}?ref={commit}")
    if item["encoding"] != "base64" or item["type"] != "file" or int(item["size"]) > MAX_JSON:
        raise ValueError("unsupported or oversized upstream JSON")
    raw = base64.b64decode(item["content"])
    if len(raw) > MAX_JSON or not isinstance(json.loads(raw.decode("utf-8")), dict):
        raise ValueError("not a JSON workflow object")
    return raw, {"id": entry["id"], "source": f"https://github.com/{repo}/blob/{commit}/{path}",
                 "repository": repo, "path": path, "commit": commit, "blob_sha": item["sha"],
                 "sha256": hashlib.sha256(raw).hexdigest(), "license": "unverified",
                 "execution": "not-run", "review_required": True}


def snapshot(root: Path, get=github_json) -> list[dict]:
    # すべて取得できた場合だけ保存し、不完全な記録を作らない。
    gathered = [(entry, *download_snapshot(entry, get)) for entry in manifest_entries(root)]
    folder = root / "projects/vrchat-cafe/upstream"
    folder.mkdir(parents=True, exist_ok=True)
    for entry, raw, meta in gathered:
        path = folder / (entry["id"] + ".json")
        tmp = path.with_suffix(".json.tmp")
        tmp.write_bytes(raw)
        tmp.replace(path)
        meta_path = folder / (entry["id"] + ".source.json")
        tmp = meta_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(meta_path)
    return [meta for _, _, meta in gathered]


def verify_snapshots(root: Path) -> list[dict]:
    folder = root / "projects/vrchat-cafe/upstream"
    report = []
    for entry in manifest_entries(root):
        path = folder / (entry["id"] + ".json")
        source = folder / (entry["id"] + ".source.json")
        if not path.exists() or not source.exists():
            report.append({"id": entry["id"], "status": "not-downloaded"})
            continue
        raw = path.read_bytes()
        meta = json.loads(source.read_text(encoding="utf-8"))
        good = hashlib.sha256(raw).hexdigest() == meta.get("sha256") and meta.get("path") == entry["path"] and meta.get("repository") == entry["repository"]
        if good:
            try:
                good = isinstance(json.loads(raw.decode("utf-8")), dict)
            except (UnicodeError, ValueError):
                good = False
        report.append({"id": entry["id"], "status": "intact" if good else "mismatch",
                       "execution": meta.get("execution", "unknown")})
    return report


def inspect_glb(path: Path) -> dict:
    """形式検査のみ。見た目やVRChat適合性は検証しない。"""
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError("missing GLB magic")
    version, declared_size = struct.unpack_from("<II", data, 4)
    if version != 2 or declared_size != len(data):
        raise ValueError("GLB version/length mismatch")
    json_size, kind = struct.unpack_from("<I4s", data, 12)
    if kind != b"JSON" or json_size > len(data) - 20:
        raise ValueError("missing or invalid JSON chunk")
    document = json.loads(data[20:20 + json_size].decode("utf-8"))
    if document.get("asset", {}).get("version") != "2.0":
        raise ValueError("invalid glTF asset version")
    meshes = document.get("meshes", [])
    if not meshes:
        raise ValueError("GLB has no meshes")
    accessors = document.get("accessors", [])
    triangle_count = 0
    for mesh in meshes:
        for primitive in mesh.get("primitives", []):
            if primitive.get("mode", 4) != 4:
                continue
            index = primitive.get("indices", primitive.get("attributes", {}).get("POSITION"))
            if isinstance(index, int) and 0 <= index < len(accessors):
                triangle_count += accessors[index].get("count", 0) // 3
    return {"path": str(path), "status": "glb-container-valid", "meshes": len(meshes),
            "triangles_estimated": triangle_count, "materials": len(document.get("materials", [])),
            "note": "Topology, licensing, shading and actual Unity import are not verified"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("snapshot", "check", "glb"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--file", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "snapshot":
        result = snapshot(args.root)
    elif args.command == "check":
        result = verify_snapshots(args.root)
    else:
        if args.file is None:
            parser.error("glb requires --file")
        result = inspect_glb(args.file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "check" and args.strict and any(r["status"] != "intact" for r in result):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
