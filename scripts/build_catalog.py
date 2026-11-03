#!/usr/bin/env python3
"""Build lossless source-linked discovery views from observed ComfyUI workflow metadata.

Category hits are tentative search tags, never a statement of compatibility or quality.
No external code or downloaded models are executed.
"""
from __future__ import annotations

import csv
import io
import json
from collections import defaultdict
from pathlib import Path


def load(path: Path, fallback: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else fallback


def categorize(asset: dict, inspected: dict, categories: list[dict]) -> list[str]:
    # A bounded path and statically observed node names only. Never inspect user prompts.
    corpus = " ".join([
        asset.get("path", ""),
        asset.get("source_repository", ""),
        " ".join(inspected.get("node_types", [])),
        " ".join(inspected.get("models", [])),
    ]).lower()
    return [item["id"] for item in categories
            if any(word.lower() in corpus for word in item["keywords"])] or ["other"]


def render(root: Path) -> dict:
    cfg = load(root / "config/use-cases.json", {})
    categories = cfg["categories"]
    if not categories or len({c["id"] for c in categories}) != len(categories):
        raise ValueError("duplicate or empty category definitions")
    practices = load(root / "registry/practices.json", {"assets": []})
    inspected = {x["id"]: x for x in
                 load(root / "registry/insights.json", {"inspected": []})["inspected"]}
    combined = {x["source_repository"].lower() + ":" + x["path"]: x
                for x in practices["assets"]}
    newer = load(root / "data/workflow_registry.json", {"artifacts": {}})
    for item in newer.get("artifacts", {}).values():
        source = item.get("source", "")
        if not source.startswith("github:"):
            continue
        repository = source[len("github:"):]
        path = item["path"]
        identity = repository.lower() + ":" + path
        revisions = item.get("revisions") or []
        sha = item["blob_sha"]
        combined[identity] = {
            "id": identity, "source_repository": repository, "path": path,
            "url": item["source_url"], "source_commit": item["commit_sha"],
            "blob_sha": sha, "kind": item.get("format", "workflow_candidate"),
            "license": item.get("license", "UNKNOWN"),
            "first_seen": revisions[0].get("observed_at", "") if revisions else "",
            "last_changed": revisions[-1].get("observed_at", "") if revisions else "",
            "lifecycle": "present",
        }
        inspected[identity] = {
            "id": identity, "blob_sha": sha,
            "format": item.get("format", item.get("inspection", "not_inspected")),
            "node_types": item.get("node_types", []),
            "models": item.get("model_references", []),
            "node_count": item.get("node_count", ""),
        }
    assets = list(combined.values())
    if len({a["id"] for a in assets}) != len(assets):
        raise ValueError("duplicate asset ids")
    rows = []
    for a in sorted(assets, key=lambda x: x["id"].casefold()):
        audit = inspected.get(a["id"], {})
        fresh = audit.get("blob_sha") == a.get("blob_sha")
        record = {
            "id": a["id"],
            "source_repository": a["source_repository"],
            "path": a["path"],
            "source_url": a["url"],
            "source_commit": a["source_commit"],
            "blob_sha": a["blob_sha"],
            "kind": a["kind"],
            "license": a.get("license", "UNKNOWN"),
            "first_seen": a.get("first_seen", ""),
            "last_changed": a.get("last_changed", ""),
            "lifecycle": a.get("lifecycle", "present"),
            "inspection": audit.get("format", "not_inspected") if fresh else "not_inspected",
            "node_count": audit.get("node_count", "") if fresh else "",
            "categories": categorize(a, audit if fresh else {}, categories),
        }
        rows.append(record)
    # Preserve EVERY discovered candidate, even if no category matched or the source
    # disappeared upstream. Never filter by popularity, completeness, license or vendor.
    by_tag = defaultdict(list)
    for r in rows:
        for label in r["categories"]:
            by_tag[label].append(r["id"])
    output = root / "catalog"
    output.mkdir(parents=True, exist_ok=True)
    by_category = {
        "schema_version": 1,
        "generated_from": "registry/practices.json + data/workflow_registry.json",
        "total": len(rows),
        "categories": {c["id"]: {"title": c["title"], "count": len(by_tag[c["id"]]),
                                  "workflow_ids": by_tag[c["id"]]} for c in categories},
        "other": {"count": len(by_tag["other"]), "workflow_ids": by_tag["other"]},
    }
    (output / "by-usecase.json").write_text(
        json.dumps(by_category, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    buf = io.StringIO(newline="")
    columns = ["id", "source_repository", "path", "source_url", "source_commit",
               "blob_sha", "kind", "license", "first_seen", "last_changed",
               "lifecycle", "inspection", "node_count", "categories"]
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for r in rows:
        writer.writerow({**r, "categories": ";".join(r["categories"])})
    (output / "all-workflows.csv").write_text(buf.getvalue(), encoding="utf-8-sig")
    by_id = {r["id"]: r for r in rows}
    lines = [
        "# ComfyUI Workflow Atlas",
        "",
        f"Discovered candidate files: **{len(rows)}**. This is a discovery index, not a quality ranking.",
        "",
        "All sources remain discoverable in [all-workflows.csv](all-workflows.csv). "
        "Unclassified entries remain in **Other**. No unreviewed upstream code was run.",
        "",
        "Category labels use filename/repository/node-name matches only; they are not proof "
        "that a workflow will produce a complete YouTube video, VRChat avatar or world.",
        "",
    ]
    for category in categories + [{"id": "other", "title": "Other / Unclassified"}]:
        key = category["id"]
        ids = by_tag[key]
        lines += [f"## {category['title']} ({len(ids)})", ""]
        if not ids:
            lines += ["No matching candidates observed yet.", ""]
            continue
        # GitHub README remains readable; the CSV/JSON above contain all entries.
        for id_ in ids[:40]:
            a = by_id[id_]
            title = a["path"].rsplit("/", 1)[-1].replace("|", "/").replace("]", "\\]")
            lines.append(f"- [{title}]({a['source_url']}) | {a['source_repository']} | "
                         f"{a['kind']} | {a['inspection']} | {a['license']}")
        if len(ids) > 40:
            lines.append(f"- … and {len(ids) - 40} more in the complete CSV / JSON.")
        lines.append("")
    (output / "index.md").write_text("\n".join(lines), encoding="utf-8")
    return {"all": len(rows), "categorized": len(rows) - len(by_tag["other"]),
            "other": len(by_tag["other"]), "categories": {k: len(v) for k, v in by_tag.items()}}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args()
    print(json.dumps(render(args.root), ensure_ascii=False, indent=2))
