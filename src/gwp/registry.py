"""8領域、収集元、Workflow候補、制作案件を管理する設定台帳。"""
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


def _mission_ids(row, missions, label):
    ids = row.get("mission_ids", [])
    if not isinstance(ids, list) or any(not isinstance(mid, str) or mid not in missions for mid in ids):
        raise ValueError(f"{label}: 不明なミッションがあります")


def validate_registry(data):
    """参照整合性を検査し、人気や用途で候補を除外しない。"""
    if not isinstance(data, dict) or data.get("schema_version") != 2:
        raise ValueError("台帳の版が不正です")
    missions = data.get("missions")
    if not isinstance(missions, dict) or len(missions) != 8:
        raise ValueError("8つの制作領域が必要です")
    for key, row in missions.items():
        if not ID.fullmatch(key) or not isinstance(row, dict) or not row.get("title"):
            raise ValueError(f"ミッションが不正です: {key}")
        _tags(row, key)

    workflows = data.get("workflows")
    if not isinstance(workflows, list):
        raise ValueError("Workflow候補はリストにしてください")
    workflow_ids = set()
    for flow in workflows:
        if not isinstance(flow, dict):
            raise ValueError("Workflow候補は辞書にしてください")
        wid, repo, path = flow.get("id"), flow.get("repository"), flow.get("path")
        if not isinstance(wid, str) or not ID.fullmatch(wid) or wid in workflow_ids:
            raise ValueError(f"Workflow IDが不正または重複: {wid}")
        if not isinstance(repo, str) or not REPO.fullmatch(repo):
            raise ValueError(f"{wid}: 公開元が不正です")
        if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path or any(
            part in ("", ".", "..") for part in path.split("/")
        ):
            raise ValueError(f"{wid}: 公開元パスが不正です")
        if flow.get("source_key") != "github:" + repo.lower() + ":" + path:
            raise ValueError(f"{wid}: 出典IDが一致しません")
        _tags(flow, wid)
        _mission_ids(flow, missions, wid)
        for field in ("purpose", "license"):
            if not flow.get(field):
                raise ValueError(f"{wid}: {field}がありません")
        workflow_ids.add(wid)

    projects = data.get("projects")
    if not isinstance(projects, dict):
        raise ValueError("制作案件は辞書にしてください")
    for key, row in projects.items():
        if not ID.fullmatch(key) or not isinstance(row, dict) or not row.get("title"):
            raise ValueError(f"制作案件が不正です: {key}")
        _tags(row, key)
        _mission_ids(row, missions, key)
        used = row.get("workflow_ids", [])
        if not isinstance(used, list) or any(not isinstance(w, str) or w not in workflow_ids for w in used):
            raise ValueError(f"{key}: 不明なWorkflowがあります")

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
                  "workflows": len(data["workflows"]), "sources": len(data["github_repos"])}
    elif args.kind == "sources":
        result = data["github_repos"]
    else:
        result = data[args.kind]
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
