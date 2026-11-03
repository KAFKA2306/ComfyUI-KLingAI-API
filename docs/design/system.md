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

公開されたWorkflow、Subgraph、Blueprintを出典付きで収集し、必要な制作工程に取り入れる。8つの制作領域は独立して進め、収集した候補と知識を共有する。制作目標、案件、取得元、採用候補の設定は `config/registry.json` にまとめる。人気や独自スコアによって候補を除外しない。

## 情報の流れ

| 処理 | ファイルと役割 |
| --- | --- |
| 収集条件 | `config/registry.json`：公開元、検索語、用途の分類 |
| 発見・静的確認 | `src/gwp/discovery.py`：候補の列挙、改訂履歴、JSON形式の確認 |
| 取得結果 | `.cache/workflow_registry.json`：出典URL、コミットSHA、Blob SHA、探索状態 |
| 検索・出力 | `gwp.discovery search / export`：取得結果から検索し、CSV・JSONを生成 |
| 素材生成 | `src/gwp/production.py`：選んだAPI形式WorkflowをローカルComfyUIに投入 |
| 作品の完成 | Blender、Unity、制作先の編集環境と公開サービスで確認 |

収集結果の既定保存先 `.cache/workflow_registry.json` はGit管理外のキャッシュである。[定期収集](../../.github/workflows/collect.yml)は6時間ごとに実行し、前回のキャッシュの復元を試みる。GitHub Actionsの収集成果物は1日で期限切れになるため、長期間の記録が保管されていることをこの仕組みだけで保証しない。

## 出典と実行の境界

- 原典のリポジトリ、パス、固定コミット、Blob SHAを記録し、異なる作者の出典を一つにまとめない。
- 未分類の候補や取得・解析の失敗も記録する。APIエラーを候補が存在しない証拠として扱わない。
- ファイルの静的確認と、モデルを使った実行確認を区別する。静的確認だけでは品質や商用利用条件は確定しない。
- 収集時に第三者のWorkflow、Custom Node、モデルを自動で導入・実行しない。
- GitHub検索と巡回には件数の上限がある。収集結果を世界中のWorkflowの完全な一覧とは呼ばない。

制作への接続と完成条件の扱いは[制作工程への接続](production.md)に定める。
