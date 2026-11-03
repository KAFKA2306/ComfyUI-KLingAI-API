---
id: "knowledge-registry"
title: "Workflow台帳・メタデータ・用語"
kind: "knowledge"
status: "active"
updated: "2026-11-03"
tags: ["Workflow","ナレッジ","メタデータ","検索"]
related: ["data/workflow_registry.json","src/gwp/discovery.py","config/workflow_sources.json"]
sources: ["https://github.com/Comfy-Org/workflows"]
---

# Workflow台帳・メタデータ・用語

`data/workflow_registry.json` が発見情報の唯一の正本です。`config/workflow_sources.json` は収集対象と検索分類の設定です。

| 領域 | 内容 |
| --- | --- |
| `repositories` | リポジトリ単位の巡回履歴 |
| `discoveries` | 発見した出典と探索経路。未走査も保持 |
| `artifacts` | Workflow候補、原典URL、commit SHA、Blob SHA、改訂履歴、静的確認 |
| `evidence` | リポジトリのIssue参照。個々のWorkflowの動作を証明しない |
| `feeds` | モデル情報。Workflow JSONの取得を意味しない |
| `references` | APIで直接収集していない参考先 |
| `search_progress` | 探索の進み具合とAPI失敗 |

**Workflow**はノードの処理構成です。**Subgraph**は構成の一部分、**Blueprint**は構成定義を含む形式です。**発見**は出典を記録したこと、**静的確認**はJSONを読んだこと、**実行検証**はモデルと環境で実際に動かしたことです。これらは別の状態として扱います。

**タグ**は検索と用途の分類に使います。独自スコア・ランキング・足切りを付けず、未分類候補も保存します。内容が同じファイルでも作者や出典が異なれば別の記録です。

## 検索と書き出し

```sh
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export > workflows.csv
```

エクスポートは台帳から生成する閲覧用データです。GitHub APIの検索件数や巡回数に上限があるため完全網羅とは断定しません。
