"""8領域、収集元、Workflow候補、制作案件を管理する設定台帳。"""
from __future__ import annotations

import argparse
import json
import re
from urllib.parse import urlsplit
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



def _nonempty_strings(items, label):
    if not isinstance(items, list) or not items or any(
        not isinstance(item, str) or not item.strip() for item in items
    ) or len(set(items)) != len(items):
        raise ValueError(f"{label}: 重複しない非空文字列配列が必要です")
    return items


def _validate_pipelines(data, missions, workflow_ids):
    """工程間の入出力と原典を検査する。ComfyUI JSONとは別種として扱う。"""
    rows = data.get("pipelines", [])
    if not isinstance(rows, list):
        raise ValueError("制作パイプラインはリストにしてください")
    seen = set()
    for row in rows:
        ident = row.get("id") if isinstance(row, dict) else None
        if not isinstance(ident, str) or not ID.fullmatch(ident) or ident in seen or ident in workflow_ids:
            raise ValueError(f"パイプラインIDが不正または重複: {ident}")
        seen.add(ident)
        for field in ("title", "purpose"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"{ident}: {field}がありません")
        _tags(row, ident)
        _mission_ids(row, missions, ident)
        available = set(_nonempty_strings(row.get("inputs"), ident + ".inputs"))
        steps = row.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError(f"{ident}: stepsがありません")
        for index, stage in enumerate(steps):
            label = f"{ident}.steps[{index}]"
            if not isinstance(stage, dict) or any(
                not isinstance(stage.get(key), str) or not stage[key].strip()
                for key in ("tool", "source_url", "action")
            ):
                raise ValueError(f"{label}: ツール・出典・操作が必要です")
            url = urlsplit(stage["source_url"])
            if url.scheme != "https" or not url.netloc or url.username or url.password:
                raise ValueError(f"{label}: 認証情報を含まないHTTPS URLが必要です")
            requires = set(_nonempty_strings(stage.get("requires"), label + ".requires"))
            provides = set(_nonempty_strings(stage.get("provides"), label + ".provides"))
            if not requires <= available:
                raise ValueError(f"{label}: 未生成の入力があります: {sorted(requires - available)}")
            available.update(provides)
        if not set(_nonempty_strings(row.get("outputs"), ident + ".outputs")) <= available:
            raise ValueError(f"{ident}: 工程から出力できない成果物です")
        _nonempty_strings(row.get("checks"), ident + ".checks")
    return seen


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

    pipeline_ids = _validate_pipelines(data, missions, workflow_ids)

    projects = data.get("projects")
    if not isinstance(projects, dict):
        raise ValueError("制作案件は辞書にしてください")
    for key, row in projects.items():
        if not ID.fullmatch(key) or not isinstance(row, dict) or not row.get("title"):
            raise ValueError(f"制作案件が不正です: {key}")
        _tags(row, key)
        _mission_ids(row, missions, key)
        pipeline_refs = row.get("pipeline_ids", [])
        if not isinstance(pipeline_refs, list) or any(
            not isinstance(pid, str) or pid not in pipeline_ids for pid in pipeline_refs
        ):
            raise ValueError(f"{key}: 不明な制作パイプラインがあります")
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
    parser.add_argument("--kind", choices=("missions", "projects", "workflows", "pipelines", "sources"), default="workflows")
    args = parser.parse_args(argv)
    data = load_registry(args.registry)
    if args.command == "validate":
        result = {"status": "valid"}
    elif args.command == "summary":
        result = {"missions": len(data["missions"]), "projects": len(data["projects"]),
                  "workflows": len(data["workflows"]), "pipelines": len(data.get("pipelines", [])),
                  "sources": len(data["github_repos"])}
    elif args.kind == "sources":
        result = data["github_repos"]
    else:
        result = data[args.kind]
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
