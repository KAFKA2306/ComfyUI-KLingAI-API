#!/usr/bin/env python3
"""Observe official and community ComfyUI practices. Never execute upstream code."""
from __future__ import annotations
import argparse
import json
import math
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

API = "https://api.github.com"
SHA = re.compile(r"^[0-9a-f]{40}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SKIP = ("node_modules/", ".github/", "tests/", "test/", "scripts/",
        "docs/", "assets/", "site/", "archived/")
CONFIG_FILES = {"package.json", "package-lock.json", "tsconfig.json",
                "manifest.json", "config.json", "settings.json",
                "index.json", "bundles.json", "blueprints_bundles.json",
                "schema.json"}


def get_json(path):
    if not path.startswith("/") or "://" in path or ".." in path:
        raise ValueError("invalid API path")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "gwp-practice-watch",
               "X-GitHub-Api-Version": "2022-11-28"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    for attempt in range(3):
        try:
            with urlopen(Request(API + path, headers=headers), timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"GitHub HTTP {exc.code}: {path}") from exc
        except (URLError, TimeoutError) as exc:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"GitHub connection failed: {path}") from exc
    raise RuntimeError("unreachable")


def summarize(obj, kind):
    full = obj["full_name"]
    if not REPO.fullmatch(full):
        raise ValueError(f"invalid repository: {full}")
    return {"repository": full, "url": "https://github.com/" + full, "kind": kind,
            "description": obj.get("description"), "default_branch": obj["default_branch"],
            "stars": int(obj.get("stargazers_count") or 0),
            "pushed_at": obj.get("pushed_at"), "archived": bool(obj.get("archived")),
            "fork": bool(obj.get("fork")),
            "license": (obj.get("license") or {}).get("spdx_id") or "UNKNOWN"}


def official_repositories(get, org):
    rows, seen = [], set()
    for page in range(1, 101):
        results = get(f"/orgs/{quote(org)}/repos?type=public&per_page=100&page={page}")
        if not isinstance(results, list):
            raise ValueError("invalid org response")
        for item in results:
            row = summarize(item, "official")
            if not row["repository"].startswith(org + "/") or row["repository"] in seen:
                raise ValueError("duplicate or foreign repo")
            rows.append(row)
            seen.add(row["repository"])
        if len(results) < 100:
            break
    else:
        raise RuntimeError("organization pagination limit reached")
    if not rows:
        raise ValueError("empty official inventory")
    return sorted(rows, key=lambda r: r["repository"].casefold())


def community_repositories(get, config, official):
    seen = {r["repository"] for r in official}
    community = []
    for term in config["searches"]:
        args = urlencode({"q": term, "per_page": config["per_query"],
                          "sort": "stars", "order": "desc"})
        response = get("/search/repositories?" + args)
        if not isinstance(response.get("items"), list):
            raise ValueError("invalid community search")
        for item in response["items"]:
            full = item["full_name"]
            if full not in seen and not item.get("archived") and not item.get("fork"):
                seen.add(full)
                community.append(summarize(item, "community"))
    for full in config["curated"]:
        if full not in seen:
            obj = get("/repos/" + full)
            seen.add(full)
            community.append(summarize(obj, "community"))
    return sorted(community, key=lambda r: r["repository"].casefold())


def commit_sha(get, row):
    sha = get("/repos/" + row["repository"] + "/commits/" +
              quote(row["default_branch"], safe=""))["sha"]
    if not SHA.fullmatch(sha):
        raise ValueError("invalid upstream commit " + row["repository"])
    return sha


def candidate_json(path, official_templates=False):
    low = path.lower()
    if not low.endswith(".json") or any(low.startswith(p) for p in SKIP):
        return False
    name = low.rsplit("/", 1)[-1]
    if name in CONFIG_FILES or name.endswith(".schema.json"):
        return False
    if official_templates:
        return low.startswith(("templates/", "blueprints/", "packages/media_", "packages/blueprints/"))
    return "/" not in low or any(t in low for t in (
        "workflow", "blueprint", "subgraph", "example", "sample",
        "image", "video", "/3d/", "basic/", "conditioning/"))


def signal_score(row):
    """Search prioritization signal, NOT evidence of generation quality."""
    return min(100, min(50, round(10 * math.log10(row["stars"] + 1))) +
               (25 if row["kind"] == "official" else 0) +
               (0 if row["archived"] else 10) +
               (10 if row["license"] not in ("UNKNOWN", "NOASSERTION") else 0))


def collect_assets(get, rows, selected, previous, timestamp):
    lookup = {r["repository"]: r for r in rows}
    earlier = {a["id"]: a for a in previous.get("assets", [])}
    assets, scan, scanned_heads = [], [], {}
    for full in list(dict.fromkeys(selected)):
        row = lookup.get(full)
        if row is None:
            raise ValueError("missing scanned source: " + full)
        if row["archived"]:
            raise ValueError("scanned source archived: " + full)
        head = commit_sha(get, row)
        scanned_heads[full] = head
        tree = get("/repos/" + full + "/git/trees/" + head + "?recursive=1")
        if tree.get("truncated"):
            raise ValueError("incomplete Git tree: " + full)
        count = 0
        for entry in tree["tree"]:
            path, blob = entry.get("path", ""), entry.get("sha", "")
            if entry.get("type") != "blob" or not candidate_json(
                    path, full == "Comfy-Org/workflow_templates"):
                continue
            if not SHA.fullmatch(blob) or entry.get("size", 0) > 5_000_000:
                continue
            key = full + ":" + path
            old = earlier.get(key, {})
            changed = old.get("blob_sha") != blob
            assets.append({
                "id": key, "source_repository": full, "source_commit": head,
                "path": path, "blob_sha": blob,
                "url": "https://github.com/" + full + "/blob/" + head + "/" + quote(path),
                "kind": "blueprint" if "blueprint" in path.lower() or "subgraph" in path.lower()
                        else "workflow_candidate",
                "license": row["license"], "signal_score": signal_score(row),
                "verification": "unverified",
                "first_seen": old.get("first_seen", timestamp),
                "last_changed": timestamp if changed else old.get("last_changed", timestamp),
            })
            count += 1
        scan.append({"repository": full, "revision": head, "candidate_count": count})
    result = sorted(assets, key=lambda a: a["id"].casefold())
    first_by_content = {}
    for asset in result:
        first = first_by_content.setdefault(asset["blob_sha"], asset["id"])
        if first != asset["id"]:
            asset["same_content_as"] = first
    if len({a["id"] for a in result}) != len(result):
        raise ValueError("duplicate asset")
    return result, scan, scanned_heads


def read_or(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def encode(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def discover(root, get=get_json, timestamp=None):
    config = json.loads((root / "config/practice-sources.json").read_text(encoding="utf-8"))
    timestamp = timestamp or datetime.now(timezone.utc).isoformat(timespec="seconds")
    official = official_repositories(get, config["organization"])
    previous = read_or(root / "registry/official.json", {})
    if len(previous.get("repositories", [])) >= 20 and len(official) < (
            len(previous["repositories"]) * 0.8):
        raise ValueError("suspicious official repository count drop")
    community = community_repositories(get, config, official)
    # Search rankings can change without a source disappearing. Preserve past discoveries.
    prior_community = read_or(root / "registry/community.json", {}).get("repositories", [])
    known_repos = {r["repository"] for r in official + community}
    for old in prior_community:
        if old["repository"] not in known_repos:
            community.append({**old, "discovery_state": "not_seen_in_latest_search"})
            known_repos.add(old["repository"])
    community.sort(key=lambda r: r["repository"].casefold())
    all_rows = official + community
    prior_practices = read_or(root / "registry/practices.json", {})
    assets, scanned, heads = collect_assets(
        get, all_rows, config["scan_repositories"], prior_practices, timestamp)
    current_ids = {a["id"] for a in assets}
    for old in prior_practices.get("assets", []):
        if old["id"] not in current_ids:
            assets.append({**old, "lifecycle": "removed_or_unscanned_upstream"})
            current_ids.add(old["id"])
    assets.sort(key=lambda a: a["id"].casefold())
    if not assets:
        raise ValueError("empty practice registry")
    refs = []
    official_lookup = {r["repository"]: r for r in official}
    for name in config["track_upstreams"]:
        full = config["organization"] + "/" + name
        row = official_lookup.get(full)
        if row is None or row["archived"]:
            raise ValueError("missing or archived critical upstream " + full)
        refs.append({"name": name, "repository": row["url"],
                     "revision": heads.get(full) or commit_sha(get, row),
                     "state": "observed_not_deployed"})
    files = {
        "registry/official.json": {"schema_version": 1, "count": len(official), "repositories": official},
        "registry/community.json": {"schema_version": 1, "count": len(community), "repositories": community},
        "registry/practices.json": {"schema_version": 1, "count": len(assets),
                                    "scanned": scanned, "assets": assets,
                                    "policy": "unverified_metadata_only"},
        "dependencies/sources.lock.json": {"schema_version": 2, "organization": config["organization"],
                                            "policy": "observed candidates only; never deployed automatically",
                                            "sources": refs},
    }
    # All network calls and structural checks finish before any file is replaced.
    for rel, data in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(encode(data), encoding="utf-8")
        tmp.replace(path)
    return {"official": len(official), "community": len(community),
            "practices": len(assets), "tracked": len(refs)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(encode(discover(args.root)))
