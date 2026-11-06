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
    popularity = round(30 * min(1, math.log1p(stars) / math.log1p(10000)), 2) if type(stars) is int and stars >= 0 else None
    pushed = _time(meta.get("pushed_at"))
    days = max(0, (now - pushed).total_seconds() / 86400) if pushed else None
    freshness = round(30 * max(0, 1 - days / 365), 2) if days is not None else None
    inspected = item.get("inspection") == "complete"
    models = sorted(set(item.get("model_references") or []))
    nodes = sorted(set(item.get("node_types") or []))
    license_id = meta.get("license_spdx")
    required_vram = item.get("required_vram_gb")
    vram_ok = (vram_gb >= required_vram) if isinstance(required_vram, (int, float)) and vram_gb is not None else None
    mission_scores = {}
    for mission in MISSION_CATEGORIES:
        hits = matches(item, registry, mission)
        explicit = mission in item.get("mission_ids", [])
        if hits or explicit:
            mission_scores[mission] = min(40, (30 if explicit else 0) + min(10, 2 * len(hits)))
    suitability = max(mission_scores.values(), default=0)
    known = [x for x in (popularity, freshness) if x is not None]
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
                             "mission_fit": suitability},
        "mission_scores": mission_scores, "required_models": models,
        "node_types": nodes, "custom_nodes": "未確認",
        "required_vram_gb": required_vram, "input_formats": item.get("input_formats"),
        "output_formats": item.get("output_formats"), "license_spdx": license_id,
        "readiness": "verified" if not blockers else "unverified",
        "blockers": blockers, "path": item.get("path"),
        "blob_sha": item.get("blob_sha"),
    }


def report(catalog, registry, *, vram_gb=None, now=None):
    now = now or datetime.now(timezone.utc)
    rows = [evaluate(item, catalog, registry, now, vram_gb)
            for item in source_rows(catalog, registry) if not item.get("missing_upstream")]
    # ノード名・モデル名が同じでも接続や設定が異なるため、内容一致の証拠にはならない。
    # Git Blob SHAが一致し、用途の割当も同じ場合だけまとめる。出典は候補IDで保持する。
    groups = {}
    for row in rows:
        blob = row.get("blob_sha")
        valid_blob = (isinstance(blob, str) and len(blob) == 40
                      and all(ch in "0123456789abcdef" for ch in blob.lower()))
        key = (("blob", blob.lower(), tuple(sorted(row["mission_scores"].items())))
               if valid_blob else ("unique", row["id"]))
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
        # 領域別の点数に他領域の適合度を混ぜない。
        def mission_score(row):
            parts = row["score_components"]
            return round(sum(value for value in (parts["popularity"], parts["freshness"])
                             if value is not None) + row["mission_scores"][mission], 2)

        eligible.sort(key=lambda r: (-mission_score(r), -r["mission_scores"][mission], str(r["id"])))
        assignments[mission] = [{"workflow_id": r["id"], "score": mission_score(r),
                                  "mission_fit": r["mission_scores"][mission],
                                  "readiness": r["readiness"], "blockers": r["blockers"]}
                                 for r in eligible[:5]]
    return {"schema_version": 1, "metric_note": "採点は人気30点・更新日30点・領域適合40点のみ。人気と更新日はリポジトリ単位。実行条件・ライセンスは参考情報であり採点しない。",
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
