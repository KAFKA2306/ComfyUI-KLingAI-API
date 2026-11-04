"""収集済みWorkflowの保守的な評価・類似整理・制作領域への割当。"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from gwp.registry import load_registry
from gwp.select import MISSION_CATEGORIES, matches, source_rows, _time
from gwp.state import load_catalog


def evaluate(item, catalog, registry, now, vram_gb=None):
    repo = item.get("source", "").removeprefix("github:")
    meta = catalog.get("repositories", {}).get(repo, {})
    stars = meta.get("stargazers_count")
    popularity = round(15 * min(1, math.log1p(stars) / math.log1p(10000)), 2) if type(stars) is int and stars >= 0 else None
    pushed = _time(meta.get("pushed_at"))
    days = max(0, (now - pushed).total_seconds() / 86400) if pushed else None
    freshness = round(15 * max(0, 1 - days / 365), 2) if days is not None else None
    inspected = item.get("inspection") == "complete"
    models = sorted(set(item.get("model_references") or []))
    nodes = sorted(set(item.get("node_types") or []))
    license_id = meta.get("license_spdx")
    license_score = 20 if license_id and license_id not in ("NOASSERTION", "OTHER") else None
    required_vram = item.get("required_vram_gb")
    vram_ok = (vram_gb >= required_vram) if isinstance(required_vram, (int, float)) and vram_gb is not None else None
    environment = 20 if inspected and vram_ok is True and item.get("runtime_verified") is True else None
    mission_scores = {}
    for mission in MISSION_CATEGORIES:
        hits = matches(item, registry, mission)
        explicit = mission in item.get("mission_ids", [])
        if hits or explicit:
            mission_scores[mission] = min(30, (20 if explicit else 0) + min(10, 2 * len(hits)))
    suitability = max(mission_scores.values(), default=0)
    known = [x for x in (popularity, freshness, environment, license_score) if x is not None]
    score = round(sum(known) + suitability, 2)
    blockers = []
    if not inspected:
        blockers.append("Workflow構造未検査")
    if not license_id or license_id in ("NOASSERTION", "OTHER"):
        blockers.append("ライセンス未確認")
    if not models:
        blockers.append("必要モデル未特定")
    if not nodes:
        blockers.append("ノード構成未特定")
    if vram_ok is None:
        blockers.append("VRAM要件未確認")
    elif not vram_ok:
        blockers.append("VRAM不足")
    if item.get("runtime_verified") is not True:
        blockers.append("実機実行未確認")
    return {
        "id": item.get("id"), "source_url": item.get("source_url"),
        "score_observed": score, "score_max": 100,
        "score_components": {"popularity": popularity, "freshness": freshness,
                             "environment": environment, "license": license_score,
                             "mission_fit": suitability},
        "mission_scores": mission_scores, "required_models": models,
        "node_types": nodes, "custom_nodes": "未確認",
        "required_vram_gb": required_vram, "input_formats": item.get("input_formats"),
        "output_formats": item.get("output_formats"), "license_spdx": license_id,
        "readiness": "verified" if not blockers else "unverified",
        "blockers": blockers, "path": item.get("path"),
    }


def report(catalog, registry, *, vram_gb=None, now=None):
    now = now or datetime.now(timezone.utc)
    rows = [evaluate(item, catalog, registry, now, vram_gb)
            for item in source_rows(catalog, registry) if not item.get("missing_upstream")]
    # 同一用途・同一ノード構成・同一モデル参照が確定したものだけを統合する。
    groups = {}
    for row in rows:
        signature = (tuple(sorted(row["mission_scores"])), tuple(row["node_types"]),
                     tuple(row["required_models"]), str(row["input_formats"]),
                     str(row["output_formats"]))
        key = signature if row["node_types"] and row["required_models"] else ("unique", row["id"])
        groups.setdefault(key, []).append(row)
    winners = []
    for group in groups.values():
        group.sort(key=lambda r: (-r["score_observed"], len(r["blockers"]), str(r["id"])))
        winner = dict(group[0])
        winner["similar_candidates"] = [r["id"] for r in group[1:]]
        winners.append(winner)
    assignments = {}
    for mission in registry["missions"]:
        eligible = [r for r in winners if mission in r["mission_scores"]]
        eligible.sort(key=lambda r: (-r["mission_scores"][mission], -r["score_observed"], str(r["id"])))
        assignments[mission] = [{"workflow_id": r["id"], "score": r["score_observed"],
                                  "mission_fit": r["mission_scores"][mission],
                                  "readiness": r["readiness"], "blockers": r["blockers"]}
                                 for r in eligible[:5]]
    return {"schema_version": 1, "metric_note": "人気と更新日はリポジトリ単位。未確認点は加点せず、実行可能とは断定しない。",
            "candidates": len(rows), "groups": len(groups),
            "ranked": sorted(winners, key=lambda r: (-r["score_observed"], str(r["id"]))),
            "assignments": assignments}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Workflow候補を採点・類似整理・8領域に割り当てる")
    parser.add_argument("--catalog", type=Path, default=Path(".cache/workflow_registry.json"))
    parser.add_argument("--registry", type=Path, default=Path("config/registry.json"))
    parser.add_argument("--vram-gb", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = report(load_catalog(args.catalog, allow_missing=False),
                    load_registry(args.registry), vram_gb=args.vram_gb)
    data = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
