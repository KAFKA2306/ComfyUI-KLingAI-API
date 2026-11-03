"""作品の創作設計を検証し、素材・シーン変更の波及先を追う。実行・公開はしない。"""
import argparse
import heapq
import json
import re
from pathlib import Path

from gwp.registry import load_registry
KINDS = {"direction", "asset", "scene", "shot", "sound", "interaction", "edit", "package"}
IDENT = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def _id(value, field):
    if not isinstance(value, str) or not IDENT.fullmatch(value):
        raise ValueError(f"{field}: 識別子が不正です")
    return value


def _strings(values, field, required=False):
    if not isinstance(values, list) or (required and not values):
        raise ValueError(f"{field}: 文字列配列が必要です")
    if any(not isinstance(x, str) or not x.strip() for x in values) or len(values) != len(set(values)):
        raise ValueError(f"{field}: 空欄か重複があります")
    return values


def validate(plan, registry=None):
    """一元台帳の参照と制作依存を検査する。作品の美的評価は行わない。"""
    if not isinstance(plan, dict) or plan.get("schema_version") != 1:
        raise ValueError("schema_version は1が必要です")
    _id(plan.get("project_id"), "project_id")
    if not isinstance(plan.get("title"), str) or not plan["title"].strip():
        raise ValueError("title が空です")
    if registry is None:
        registry = load_registry()
    project = registry["projects"].get(plan["project_id"])
    if project is None:
        raise ValueError("制作案件が一元台帳 config/registry.json にありません")
    missions = _strings(plan.get("missions"), "missions", True)
    if any(x not in registry["missions"] or x not in project["mission_ids"] for x in missions):
        raise ValueError("missions が一元台帳の制作案件と一致しません")
    workflow_ids = {workflow["id"] for workflow in registry["workflows"]}
    pipeline_ids = {pipeline["id"] for pipeline in registry.get("pipelines", [])}
    continuity = plan.get("continuity")
    if not isinstance(continuity, dict):
        raise ValueError("continuity は辞書にしてください")
    for key, value in continuity.items():
        _id(key, "continuity key")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"continuity.{key} が空です")
    units = plan.get("units")
    if not isinstance(units, list) or not units:
        raise ValueError("制作単位 units がありません")
    by_id = {}
    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError("unit は辞書にしてください")
        ident = _id(unit.get("id"), "unit id")
        if ident in by_id:
            raise ValueError(f"unit id が重複: {ident}")
        if unit.get("kind") not in KINDS:
            raise ValueError(f"{ident}: kind が未知です")
        if not isinstance(unit.get("purpose"), str) or not unit["purpose"].strip():
            raise ValueError(f"{ident}: purpose が空です")
        _strings(unit.get("deliverables"), f"{ident}.deliverables", True)
        _strings(unit.get("requires", []), f"{ident}.requires")
        _strings(unit.get("continuity_refs", []), f"{ident}.continuity_refs")
        _strings(unit.get("workflow_ids", []), f"{ident}.workflow_ids")
        _strings(unit.get("pipeline_ids", []), f"{ident}.pipeline_ids")
        if any(wid not in workflow_ids for wid in unit.get("workflow_ids", [])):
            raise ValueError(f"{ident}: 一元台帳にないWorkflowがあります")
        if any(pid not in pipeline_ids for pid in unit.get("pipeline_ids", [])):
            raise ValueError(f"{ident}: 一元台帳にない制作パイプラインがあります")
        if any(ref not in continuity for ref in unit.get("continuity_refs", [])):
            raise ValueError(f"{ident}: 不明な共有表現があります")
        by_id[ident] = unit
    children = {ident: [] for ident in by_id}
    degree = {}
    for ident, unit in by_id.items():
        requires = unit.get("requires", [])
        degree[ident] = len(requires)
        for dependency in requires:
            if dependency not in by_id or dependency == ident:
                raise ValueError(f"{ident}: 不明または自己参照の依存先: {dependency}")
            children[dependency].append(ident)
    pending = [ident for ident, count in degree.items() if count == 0]
    heapq.heapify(pending)
    order = []
    while pending:
        ident = heapq.heappop(pending)
        order.append(ident)
        for child in children[ident]:
            degree[child] -= 1
            if degree[child] == 0:
                heapq.heappush(pending, child)
    if len(order) != len(by_id):
        raise ValueError("制作単位の依存関係が循環しています")
    releases = plan.get("releases")
    if not isinstance(releases, list) or not releases:
        raise ValueError("releases がありません")
    seen = set()
    for release in releases:
        if not isinstance(release, dict):
            raise ValueError("release は辞書にしてください")
        name = _id(release.get("id"), "release id")
        if name in seen:
            raise ValueError(f"公開先の重複: {name}")
        seen.add(name)
        if release.get("mission") not in missions:
            raise ValueError(f"{name}: missionsにない公開領域です")
        for dep in _strings(release.get("requires"), f"{name}.requires", True):
            if dep not in by_id:
                raise ValueError(f"{name}: 不明な制作単位: {dep}")
    return order


def impact(plan, changed, registry=None):
    """変更起点に依存する制作単位と公開先を返す。自動再生成は行わない。"""
    order = validate(plan, registry)
    units = {unit["id"]: unit for unit in plan["units"]}
    if changed not in units:
        raise ValueError(f"制作単位がありません: {changed}")
    affected = {changed}
    for ident in order:
        if any(dep in affected for dep in units[ident].get("requires", [])):
            affected.add(ident)
    return {"changed": changed,
            "affected_units": [ident for ident in order if ident in affected],
            "affected_releases": [r["id"] for r in plan["releases"]
                                  if any(dep in affected for dep in r["requires"])],
            "meaning": "再検討する範囲。制作・品質検証・公開の実施を意味しません"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="作品の構成・依存関係・変更影響")
    parser.add_argument("command", choices=("validate", "order", "impact"))
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--unit", help="impact の変更起点となる制作単位ID")
    args = parser.parse_args(argv)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        order = validate(plan)
        if args.command == "validate":
            result = {"project_id": plan["project_id"], "unit_count": len(order),
                      "release_ids": [r["id"] for r in plan["releases"]], "structure": "valid"}
        elif args.command == "order":
            result = {"project_id": plan["project_id"], "creation_order": order}
        else:
            if not args.unit:
                parser.error("impact に --unit が必要です")
            result = impact(plan, args.unit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(2, f"制作構成の検査失敗: {exc}\n")


if __name__ == "__main__":
    main()
