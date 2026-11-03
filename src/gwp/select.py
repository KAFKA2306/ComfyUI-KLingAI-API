"""公開Workflowを用途・更新日・公開元の人気で探す。収集台帳は変更しない。"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote

from gwp.discovery import API, BASE
from gwp.registry import load_registry
from gwp.state import load_catalog

# 用途の手掛かり。品質判定ではなく、検索のための分類である。
MISSION_CATEGORIES = {
    "vrchat-world": ("vrchat", "chill-world", "game-world"),
    "avatars": ("avatars",),
    "booth": ("booth", "3d-models"),
    "youtube": ("youtube",),
    "podcast": ("podcast",),
    "movies": ("movies",),
    "3d-models": ("3d-models",),
    "games": ("game-world", "game-assets"),
}
WORKFLOW_FORMATS = {"workflow-ui", "workflow-api", "blueprint"}


def _time(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result if result.tzinfo else result.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def source_rows(catalog, registry):
    """収集結果に設定済みの原典候補を加える。元の台帳には書き込まない。"""
    rows = {key: dict(value) for key, value in catalog["artifacts"].items()}
    for configured in registry["workflows"]:
        key = configured["source_key"]
        if key in rows:
            rows[key]["mission_ids"] = configured["mission_ids"]
            continue
        repo, path = configured["repository"], configured["path"]
        rows[key] = {
            "id": key,
            "source": "github:" + repo.lower(),
            "path": path,
            "source_url": "https://github.com/" + repo + "/blob/HEAD/" + quote(path, safe="/"),
            "inspection": "registry-only",
            "format": "uninspected",
            "mission_ids": configured["mission_ids"],
            "missing_upstream": False,
        }
    return rows.values()


def matches(item, registry, mission):
    """ファイル名・ノード・モデル参照との文字列一致だけを返す。"""
    haystack = " ".join([
        item.get("path", ""),
        " ".join(item.get("node_types", [])),
        " ".join(item.get("model_references", [])),
    ]).casefold()
    category_ids = set(MISSION_CATEGORIES[mission])
    found = set()
    for category in registry["categories"]:
        if category["id"] in category_ids:
            found.update(word for word in category["keywords"] if word.casefold() in haystack)
    return sorted(found, key=str.casefold)


def candidates(catalog, registry, mission, *, inspected_only=False, term=""):
    words = term.casefold().split()
    for item in source_rows(catalog, registry):
        if item.get("missing_upstream"):
            continue
        verified = item.get("inspection") == "complete" and item.get("format") in WORKFLOW_FORMATS
        if inspected_only and not verified:
            continue
        category_hits = matches(item, registry, mission)
        explicit = mission in item.get("mission_ids", [])
        if not explicit and not category_hits:
            continue
        if words:
            haystack = " ".join([
                item.get("path", ""), item.get("source", ""),
                " ".join(item.get("node_types", [])),
                " ".join(item.get("model_references", [])),
            ]).casefold()
            if not all(word in haystack for word in words):
                continue
        yield {**item, "_verified": verified, "_hits": category_hits,
               "_registered": explicit}


def refresh_metadata(api, rows):
    """公開元のGitHub指標を照会する。Workflow個別の人気ではない。"""
    result = {}
    for repo in sorted({row["source"].removeprefix("github:") for row in rows}):
        try:
            meta = api.json(BASE + "/repos/" + quote(repo, safe="/"))
            result[repo] = {
                "stargazers_count": meta.get("stargazers_count"),
                "pushed_at": meta.get("pushed_at"),
                "license_spdx": (meta.get("license") or {}).get("spdx_id"),
                "metadata_error": None,
            }
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
            result[repo] = {"metadata_error": str(exc)[:200]}
    return result


def select_workflows(catalog, registry, mission, metadata=None, *, sort="suitable",
                     min_stars=0, updated_within_days=None, inspected_only=False,
                     term="", now=None):
    if mission not in registry["missions"] or mission not in MISSION_CATEGORIES:
        raise ValueError("不明な制作領域: " + mission)
    if sort not in ("suitable", "popular", "latest"):
        raise ValueError("sortはsuitable、popular、latestのいずれかです")
    if min_stars < 0 or (updated_within_days is not None and updated_within_days < 0):
        raise ValueError("絞り込み条件は0以上が必要です")
    now = now or datetime.now(timezone.utc)
    metadata = metadata or {}
    cutoff = now - timedelta(days=updated_within_days) if updated_within_days is not None else None
    result = []
    for item in candidates(catalog, registry, mission, inspected_only=inspected_only, term=term):
        repo = item["source"].removeprefix("github:")
        meta = metadata.get(repo) or catalog["repositories"].get(repo, {})
        stars = meta.get("stargazers_count")
        stars = stars if isinstance(stars, int) and not isinstance(stars, bool) else None
        pushed = _time(meta.get("pushed_at"))
        if min_stars and (stars is None or stars < min_stars):
            continue
        if cutoff is not None and (pushed is None or pushed < cutoff):
            continue
        result.append({
            "id": item["id"],
            "source_url": item["source_url"],
            "repository": repo,
            "path": item["path"],
            "format": item.get("format", "uninspected"),
            "inspection": item.get("inspection", "pending"),
            "verified_structure": item["_verified"],
            "registered_for_mission": item["_registered"],
            "matched_keywords": item["_hits"],
            "repository_stars": stars,
            "repository_pushed_at": meta.get("pushed_at"),
            "repository_license_spdx": meta.get("license_spdx"),
            "metadata_error": meta.get("metadata_error"),
        })

    def sort_key(row):
        verified = int(row["verified_structure"])
        registered = int(row["registered_for_mission"])
        hits = len(row["matched_keywords"])
        stars = row["repository_stars"]
        pop = (int(stars is not None), stars or 0)
        pushed = _time(row["repository_pushed_at"])
        timestamp = pushed.timestamp() if pushed else 0
        if sort == "popular":
            primary = (-pop[0], -pop[1], -verified, -registered, -hits, -timestamp)
        elif sort == "latest":
            primary = (-int(pushed is not None), -timestamp, -verified,
                       -registered, -hits, -pop[1])
        else:
            primary = (-verified, -registered, -hits, -pop[0], -pop[1], -timestamp)
        return (*primary, row["id"])

    return sorted(result, key=sort_key)


def main(argv=None):
    parser = argparse.ArgumentParser(description="最新・人気・用途別のWorkflow検索（品質の自動判定はしない）")
    parser.add_argument("--catalog", type=Path, default=Path(".cache/workflow_registry.json"))
    parser.add_argument("--registry", type=Path, default=Path("config/registry.json"))
    parser.add_argument("--mission", choices=sorted(MISSION_CATEGORIES), required=True)
    parser.add_argument("--sort", choices=("suitable", "popular", "latest"), default="suitable")
    parser.add_argument("--min-stars", type=int, default=0)
    parser.add_argument("--updated-within-days", type=int)
    parser.add_argument("--inspected-only", action="store_true")
    parser.add_argument("--offline", action="store_true", help="GitHubへの人気・更新日時の照会を行わない")
    parser.add_argument("--term", default="")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    args = parser.parse_args(argv)
    if args.limit < 1:
        parser.error("--limitは1以上です")
    try:
        catalog = load_catalog(args.catalog, allow_missing=False)
        registry = load_registry(args.registry)
        source_candidates = list(candidates(
            catalog, registry, args.mission,
            inspected_only=args.inspected_only, term=args.term))
        metadata = {} if args.offline else refresh_metadata(
            API(os.environ.get("GITHUB_TOKEN")), source_candidates)
        found = select_workflows(
            catalog, registry, args.mission, metadata,
            sort=args.sort, min_stars=args.min_stars,
            updated_within_days=args.updated_within_days,
            inspected_only=args.inspected_only, term=args.term)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f"Workflowの選定に失敗: {exc}\n")

    shown = found[:args.limit]
    if args.format == "json":
        print(json.dumps({
            "mission": args.mission, "sort": args.sort,
            "matched": len(found), "shown": len(shown),
            "metric_scope": "GitHubリポジトリ単位。Workflow個別の人気・更新日は未確認",
            "items": shown,
        }, ensure_ascii=False, indent=2))
    else:
        output = io.StringIO(newline="")
        fields = ["id", "source_url", "repository", "path", "format", "inspection",
                  "verified_structure", "registered_for_mission", "matched_keywords",
                  "repository_stars", "repository_pushed_at", "repository_license_spdx",
                  "metadata_error"]
        writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in shown:
            writer.writerow({**row, "matched_keywords": "/".join(row["matched_keywords"])})
        sys.stdout.write("\ufeff" + output.getvalue())


if __name__ == "__main__":
    main()
