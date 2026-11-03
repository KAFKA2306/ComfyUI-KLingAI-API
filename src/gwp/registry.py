"""制作目標・公開元・採用Workflow・プロジェクトをまとめた設定台帳。"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[2] / "config/registry.json"
ID = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _tags(row, label):
    tags = row.get("tags")
    if not isinstance(tags, list) or not tags or any(not isinstance(t, str) or not t.strip() for t in tags):
        raise ValueError(f"{label}: タグが不正です")


def validate_registry(data):
    """参照整合性だけ検査し、品質・人気による候補の除外を行わない。"""
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("台帳の版が不正です")
    missions = data.get("missions")
    if not isinstance(missions, dict) or not missions:
        raise ValueError("ミッションがありません")
    for key, row in missions.items():
        if not ID.fullmatch(key) or not isinstance(row, dict) or not row.get("title"):
            raise ValueError(f"ミッションが不正です: {key}")
        _tags(row, key)
    projects = data.get("projects")
    if not isinstance(projects, dict):
        raise ValueError("制作案件がありません")
    seen = set()
    for key, row in projects.items():
        if not ID.fullmatch(key) or not isinstance(row, dict) or not row.get("title"):
            raise ValueError(f"制作案件が不正です: {key}")
        _tags(row, key)
        for mid in row.get("mission_ids", []):
            if mid not in missions:
                raise ValueError(f"{key}: 不明なミッション {mid}")
        for flow in row.get("workflows", []):
            wid, repo, path = flow.get("id"), flow.get("repository"), flow.get("path")
            if not isinstance(wid, str) or not ID.fullmatch(wid) or wid in seen:
                raise ValueError(f"Workflow IDが不正または重複: {wid}")
            if not isinstance(repo, str) or not REPO.fullmatch(repo):
                raise ValueError(f"{wid}: 公開元が不正です")
            if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path or any(
                part in ("", ".", "..") for part in path.split("/")
            ):
                raise ValueError(f"{wid}: 公開元パスが不正です")
            if flow.get("source_key") != "github:" + repo.lower() + ":" + path:
                raise ValueError(f"{wid}: 出典IDが一致しません")
            for mid in flow.get("mission_ids", []):
                if mid not in missions:
                    raise ValueError(f"{wid}: 不明なミッション {mid}")
            _tags(flow, wid)
            for field in ("purpose", "license", "status"):
                if not flow.get(field):
                    raise ValueError(f"{wid}: {field}がありません")
            seen.add(wid)
    for name in ("github_repos", "github_queries", "metadata_feeds", "reference_sources", "github_organizations", "categories"):
        if not isinstance(data.get(name), list):
            raise ValueError(f"収集元設定が不足: {name}")
    return data


def load_registry(path=None):
    location = Path(path) if path is not None else REGISTRY
    return validate_registry(json.loads(location.read_text(encoding="utf-8")))


def main(argv=None):
    parser = argparse.ArgumentParser(description="一元台帳の確認")
    parser.add_argument("command", nargs="?", default="summary", choices=("summary", "validate", "list"))
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--kind", choices=("missions", "projects", "workflows", "sources"), default="workflows")
    args = parser.parse_args(argv)
    data = load_registry(args.registry)
    if args.command == "validate":
        result = {"status": "valid"}
    elif args.command == "summary":
        result = {"missions": len(data["missions"]), "projects": len(data["projects"]),
                  "workflows": sum(len(p["workflows"]) for p in data["projects"].values()),
                  "sources": len(data["github_repos"])}
    elif args.kind == "workflows":
        result = [{"project": key, **flow} for key, row in data["projects"].items() for flow in row["workflows"]]
    elif args.kind == "sources":
        result = data["github_repos"]
    else:
        result = data[args.kind]
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
