#!/usr/bin/env python3
"""Safely inspect a bounded number of workflow JSON blobs without executing them."""
from __future__ import annotations
import argparse
import base64
import json
import re
from pathlib import Path

from practice_registry import encode, get_json

MODEL = re.compile(r"(?i)(?:[A-Za-z0-9_. /\\-]+\.(?:safetensors|ckpt|pt|pth|gguf|onnx))$")
MAX_BLOB = 750_000
MAX_PER_RUN = 30
MAX_PER_SOURCE = 5


def static_inspection(content: bytes) -> dict:
    if len(content) > MAX_BLOB:
        return {"format": "oversized", "node_count": 0, "node_types": [], "models": []}
    try:
        obj = json.loads(content)
    except (ValueError, UnicodeError):
        return {"format": "not_json", "node_count": 0, "node_types": [], "models": []}
    if not isinstance(obj, dict):
        return {"format": "unknown", "node_count": 0, "node_types": [], "models": []}
    if isinstance(obj.get("nodes"), list):
        nodes = obj["nodes"]
        names = [v.get("type") for v in nodes if isinstance(v, dict)]
        fmt = "comfyui_ui"
    else:
        nodes = [v for v in obj.values() if isinstance(v, dict) and "class_type" in v]
        names = [v.get("class_type") for v in nodes]
        fmt = "comfyui_api" if nodes else "unknown"
    kinds = sorted({str(name)[:120] for name in names if isinstance(name, str)})
    model_files = set()
    def visit(value, depth=0):
        if depth > 9 or len(model_files) >= 20:
            return
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ("prompt", "text", "negative_prompt", "description"):
                    continue
                visit(item, depth + 1)
        elif isinstance(value, list):
            for item in value[:300]:
                visit(item, depth + 1)
        elif isinstance(value, str) and len(value) < 260 and MODEL.fullmatch(value.strip()):
            model_files.add(value.strip()[:200])
    for node in nodes[:2000]:
        visit(node)
    return {"format": fmt, "node_count": len(nodes), "node_types": kinds[:300],
            "models": sorted(model_files)[:20]}


def blob_json(get, repository, sha):
    obj = get("/repos/" + repository + "/git/blobs/" + sha)
    if obj.get("encoding") != "base64":
        raise ValueError("unsupported Git blob encoding")
    if int(obj.get("size", 0)) > MAX_BLOB:
        return b" " * (MAX_BLOB + 1)
    data = base64.b64decode(obj["content"], validate=False)
    if len(data) > MAX_BLOB:
        return b" " * (MAX_BLOB + 1)
    return data


def pick_assets(assets, prior, limit=MAX_PER_RUN):
    done = {r["id"]: r["blob_sha"] for r in prior}
    grouped = {}
    for item in assets:
        if item.get("lifecycle") or done.get(item["id"]) == item["blob_sha"]:
            continue
        if item.get("same_content_as"):
            continue
        grouped.setdefault(item["source_repository"], []).append(item)
    for items in grouped.values():
        items.sort(key=lambda a: (-a["signal_score"], a["path"].casefold()))
    sources = sorted(grouped)
    picked = []
    for i in range(MAX_PER_SOURCE):
        for source in sources:
            if len(picked) >= limit:
                return picked
            if i < len(grouped[source]):
                picked.append(grouped[source][i])
    return picked


def infer_modality(asset):
    value = (asset["path"] + " " + " ".join(asset.get("node_types", []))).lower()
    if any(term in value for term in ("3d", "mesh", "hunyuan3d", "triposg", "trellis")):
        return "3d"
    if any(term in value for term in ("video", "wan2", "ltxv", "animate", "motion")):
        return "video"
    if asset["kind"] == "blueprint":
        return "blueprint"
    return "image_or_general"


def highlights(assets, inspected):
    by_id = {row["id"]: row for row in assets if not row.get("lifecycle")}
    candidates = []
    for row in inspected:
        asset = by_id.get(row["id"])
        if asset is None or row["format"] not in ("comfyui_ui", "comfyui_api"):
            continue
        merged = {**asset, **row}
        candidates.append(merged)
    sections = []
    for category in ("image_or_general", "video", "3d", "blueprint"):
        pool = [a for a in candidates if infer_modality(a) == category]
        pool.sort(key=lambda a: (-a["signal_score"], a["source_repository"], a["path"]))
        # Source diversity: no more than three examples from the same repository.
        selected, counts = [], {}
        for item in pool:
            source = item["source_repository"]
            if counts.get(source, 0) >= 3 or len(selected) >= 12:
                continue
            selected.append(item)
            counts[source] = counts.get(source, 0) + 1
        sections.append((category, selected))
    lines = [
        "# Discovered ComfyUI practice highlights",
        "",
        "All entries below are STATICALLY INSPECTED, NOT executed or GPU-qualified.",
        "GitHub popularity is a discovery signal, not a quality measurement.",
        "The shortlist changes as the six-hourly crawler inspects more candidates.",
        "",
    ]
    for heading, rows in sections:
        lines.extend(["## " + heading, ""])
        if not rows:
            lines.extend(["No inspected examples yet.", ""])
            continue
        for x in rows:
            model = ", ".join(x["models"][:2]) if x["models"] else "model unresolved"
            title = x["path"].split("/")[-1].replace("|", "/")
            lines.append(f"- [{title}]({x['url']}) | {x['source_repository']} | "
                         f"{x['node_count']} nodes | {model} | signal {x['signal_score']}/100")
        lines.append("")
    return "\n".join(lines) + "\n"


def audit(root: Path, get=get_json, max_new=MAX_PER_RUN):
    data = json.loads((root / "registry/practices.json").read_text(encoding="utf-8"))
    path = root / "registry/insights.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "schema_version": 1, "inspected": []}
    existing = {a["id"]: a for a in prior["inspected"]}
    new = pick_assets(data["assets"], prior["inspected"], max_new)
    for asset in new:
        try:
            content = blob_json(get, asset["source_repository"], asset["blob_sha"])
            parsed = static_inspection(content)
        except (ValueError, KeyError) as exc:
            parsed = {"format": "unreadable", "node_count": 0, "node_types": [],
                      "models": [], "error": type(exc).__name__}
        existing[asset["id"]] = {"id": asset["id"], "blob_sha": asset["blob_sha"], **parsed}
    all_inspected = sorted(existing.values(), key=lambda a: a["id"].casefold())
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_text(encode({"schema_version": 1, "count": len(all_inspected),
                            "inspected": all_inspected}), encoding="utf-8")
    (root / "registry/highlights.md").write_text(
        highlights(data["assets"], all_inspected), encoding="utf-8")
    return {"newly_inspected": len(new), "total_inspected": len(all_inspected)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--limit", type=int, default=MAX_PER_RUN)
    args = parser.parse_args()
    print(encode(audit(args.root, max_new=max(0, min(MAX_PER_RUN, args.limit)))))
