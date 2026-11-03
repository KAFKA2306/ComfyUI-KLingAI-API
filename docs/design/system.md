---
id: "design-system"
title: "Workflowの収集と制作基盤の設計"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["設計","Workflow","出典","ComfyUI"]
related: ["config/registry.json","src/gwp/discovery.py","src/gwp/production.py"]
sources: ["https://github.com/Comfy-Org/workflow_templates"]
---

# Workflowの収集と制作基盤の設計

公開Workflow、Subgraph、Blueprintの出典と改訂履歴を記録する。候補は8領域で共有し、各領域の制作は並行して進める。収集元、候補、制作案件の設定は `config/registry.json` で管理する。候補の登録には人気や独自スコアを使わない。

## 情報の流れ

| 処理 | ファイルと役割 |
| --- | --- |
| 収集条件 | `config/registry.json`：公開元、検索語、用途の分類 |
| 発見・静的確認 | `src/gwp/discovery.py`：候補の列挙、改訂履歴、JSON形式の確認 |
| 保存台帳 | `catalog:data/workflow_registry.json`：出典・改訂・探索状態・採用・制作・公開履歴 |
| 検索・出力 | `gwp.discovery search / export`：取得結果から検索し、CSV・JSONを生成 |
| 素材生成 | `src/gwp/production.py`：選んだAPI形式WorkflowをローカルComfyUIに投入 |
| 作品の仕上げ | 各制作先で生成素材を組み込み、品質を確認して公開 |

[定期収集](../../.github/workflows/collect.yml)は6時間ごとに実行し、収集結果を `catalog` ブランチへ保存する。作業中のデータは `.cache/` に置く。破損時の復旧と競合時の統合は[台帳の保全・復旧](durability.md)に定める。

## 出典と実行の境界

- 原典のリポジトリ、パス、固定コミット、Blob SHAを記録し、異なる作者の出典を一つにまとめない。
- 未分類の候補や取得・解析の失敗も記録する。APIエラーを候補が存在しない証拠として扱わない。
- ファイルの静的確認と、モデルを使った実行確認を区別する。静的確認だけでは品質や商用利用条件は確定しない。
- 収集時に第三者のWorkflow、Custom Node、モデルを自動で導入・実行しない。
- GitHub検索と巡回には件数の上限がある。収集結果を世界中のWorkflowの完全な一覧とは呼ばない。

Workflowの投入と生成素材の受け渡しは[制作工程](production.md)に定める。
