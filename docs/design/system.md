---
id: "design-system"
title: "Workflow収集・制作基盤の設計"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["設計","Workflow","出典","ComfyUI"]
related: ["config/workflow_sources.json","src/gwp/discovery.py","src/gwp/production.py","data/workflow_registry.json"]
sources: ["https://github.com/Comfy-Org/workflow_templates"]
---

# Workflow収集・制作基盤の設計

公開Workflow・Subgraph・Blueprintを世界中から継続的に発見し、元の出典と改訂を保ったまま制作工程に利用します。独自スコア・順位・人気による足切りは設けません。

| 層 | 役割・正本 |
| --- | --- |
| 情報源 | `config/workflow_sources.json`：公開先、検索語、参考先、用途分類 |
| 発見 | `src/gwp/discovery.py`：候補ファイルの列挙と構造の静的確認 |
| 台帳 | `data/workflow_registry.json`：出典、コミットSHA、Blob SHA、改訂、探索状態 |
| 閲覧 | `gwp.discovery search / export`：既存台帳から検索・CSV/JSON出力 |
| 素材生成 | `src/gwp/production.py`：選択されたAPI形式Workflowのみをローカル実行 |
| 完成・公開 | Blender・Unity・各制作リポジトリ・公開サービスで別に確認 |

## 不変条件

1. 原典リポジトリ、ファイルパス、固定コミット、Blob SHAと改訂履歴を保持する。同内容でも異なる作者の出典は統合しない。
2. 未分類・未検証・読み取り失敗も記録する。APIエラーを候補ゼロと扱わない。
3. 静的にノードやモデル名を確認しても、実行可能性・品質・商用利用権限は保証しない。
4. 収集時に第三者Workflow・Custom Node・モデルを自動インストール・実行しない。
5. GitHub検索や巡回の上限があるため完全網羅は主張しない。モデルやサービスを特定のベンダーに固定しない。

素材の生成と製品完成を分離する具体的な契約は[制作工程への接続](production.md)に記載します。
