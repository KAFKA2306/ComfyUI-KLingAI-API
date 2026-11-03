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

公開されたWorkflow、Subgraph、Blueprintを出典付きで収集し、8つの制作領域で再利用します。制作領域は独立して進め、収集結果と制作の知識を共有します。公開元の人気や独自の点数で収集対象を除外しません。

## 情報の保存先

| 役割 | 正本・実装 |
| --- | --- |
| 目標・案件・収集条件 | mainの `config/registry.json` |
| 発見・静的確認 | `src/gwp/discovery.py` |
| 出典・改訂・制作履歴 | catalogの `data/workflow_registry.json` |
| 台帳の保存・復元 | `src/gwp/state.py`、`scripts/catalog_sync.sh`、`scripts/catalog_publish.sh` |
| 台帳の検索・出力 | `gwp.discovery search`・`export`、用途別の並べ替えは `gwp.select` |
| 素材の生成・受け渡し | `src/gwp/production.py`、`src/gwp/production_job.py` |
| 作品構成と変更影響 | `src/gwp/creative.py` |

収集処理は[GitHub Actions](../../.github/workflows/collect.yml)から6時間おきとmain更新時に起動します。`scripts/catalog_sync.sh` がcatalogの正本を取得して差分を追加します。`gwp.discovery sync` を直接実行した場合はローカルの台帳が更新されるため、永続保存には別途 `scripts/catalog_publish.sh` が必要です。

更新競合、バックアップ、別PCからの復元は[台帳の保全・復旧](durability.md)で扱います。

## 収集から作品公開まで

1. 公開元のファイルを探索し、出典URL、固定コミット、Blob SHA、改訂履歴を保存します。
2. 候補の形式と依存モデルを調べ、作品の用途に合うWorkflowを選びます。
3. 利用条件を確かめ、API形式のWorkflowをローカルComfyUIで実行します。
4. 出力のハッシュを記録し、制作先の編集環境へ渡します。
5. 制作先で品質と動作を検証し、公開先のURLと確認結果を保存します。

ファイルの静的確認だけで実行や商用利用を認めることはできません。未分類のファイルや取得失敗は台帳に残します。GitHub検索と巡回には上限があるため、収集結果が公開Workflowの全件を含むとは扱いません。
