---
id: "design-system"
title: "Workflowの収集と制作基盤の設計"
kind: "design"
status: "active"
updated: "2026-11-04"
tags: ["設計","Workflow","出典","ComfyUI"]
related: ["config/registry.json","src/gwp/discovery.py","src/gwp/production.py"]
sources: ["https://github.com/Comfy-Org/workflow_templates"]
---

# Workflowの収集と制作基盤の設計

公開Workflow、Subgraph、Blueprintを出典付きで収集し、8領域の制作に利用する。領域は並行して進め、収集した候補と知識を共有する。目標・案件・取得元・採用候補は`config/registry.json`に設定する。

## 情報の流れ

| 処理 | ファイルと役割 |
| --- | --- |
| 収集条件 | `config/registry.json`：公開元、検索語、用途の分類 |
| 発見・静的確認 | `src/gwp/discovery.py`：候補の列挙、改訂履歴、JSON形式の確認 |
| 永続台帳 | `catalog:data/workflow_registry.json`：出典・改訂・探索状態・採用・制作・公開履歴 |
| 検索・出力 | `gwp.discovery search / export`：取得結果から検索し、CSV・JSONを生成 |
| 素材生成 | `src/gwp/production.py`：選んだAPI形式WorkflowをローカルComfyUIに投入 |
| 作品の完成 | Blender、Unity、制作先の編集環境と公開サービスで確認 |

[収集ジョブ](../../.github/workflows/collect.yml)は6時間ごとの起動を設定し、取得結果を`catalog`ブランチへ保存する。実行時刻はGitHub Actionsの運用に左右される。`.cache/`は一時保存先とする。復旧と競合時の処理は[台帳保全設計](durability.md)を参照する。

## 出典と実行の境界

原典ごとにリポジトリ、パス、固定コミット、Blob SHAを保存する。同じ内容でも作者が異なれば出典を分ける。取得・解析に失敗した候補は残し、APIエラーを削除の根拠にしない。

静的確認で分かるのはファイル形式やノード参照までで、動作・品質・商用利用の可否は確定しない。収集時に第三者のWorkflow、Custom Node、モデルは実行しない。検索APIと巡回数には上限があるため、台帳は公開Workflowの網羅的な一覧ではない。実行と作品への組み込みは[制作工程](production.md)で扱う。
