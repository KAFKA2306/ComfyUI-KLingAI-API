---
id: "knowledge-registry"
title: "Workflow台帳・メタデータ・用語"
kind: "knowledge"
status: "active"
updated: "2026-11-03"
tags: ["Workflow","ナレッジ","メタデータ","検索"]
related: ["src/gwp/discovery.py","config/registry.json"]
sources: ["https://github.com/Comfy-Org/workflows"]
---

# Workflow台帳・メタデータ・用語

`.cache/workflow_registry.json` は収集時に作られるキャッシュです。Gitへコミットせず、出典・改訂の記録はここから検索・再生成します。`config/registry.json` は8つの制作目標・収集対象・採用Workflow・制作案件の設定正本です。

| 領域 | 内容 |
| --- | --- |
| `repositories` | リポジトリ単位の巡回履歴 |
| `discoveries` | 発見した出典と探索経路。未走査も保持 |
| `artifacts` | Workflow候補、原典URL、commit SHA、Blob SHA、改訂履歴、静的確認 |
| `evidence` | リポジトリのIssue参照。個々のWorkflowの動作を証明しない |
| `feeds` | モデル情報。Workflow JSONの取得を意味しない |
| `references` | APIで直接収集していない参考先 |
| `search_progress` | 探索の進み具合とAPI失敗 |

## 検索と書き出し

```sh
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export > workflows.csv
```

出力項目は[discovery.py](../../src/gwp/discovery.py)の `export_catalog` に定義されています。
