---
id: "knowledge-registry"
title: "Workflow台帳と用語"
kind: "knowledge"
status: "active"
updated: "2026-11-03"
tags: ["Workflow","ナレッジ","メタデータ","検索"]
related: ["src/gwp/discovery.py","config/registry.json"]
sources: ["https://github.com/Comfy-Org/workflows"]
---

# Workflow台帳と用語

公開Workflowの出典と改訂を検索するデータは、既定で `.cache/workflow_registry.json` に生成する。8領域の目標、制作案件、Workflow候補、収集条件、検索分類は `config/registry.json` に集約する。`workflows` は案件から独立して登録する候補一覧、`projects` は制作する案件の記録であり、特定の領域を必須とはしない。キャッシュはGitへコミットされず、長期間の保管を保証するものではない。

## 収集データの構造

| キー | 記録する内容 |
| --- | --- |
| `repositories` | リポジトリ単位の巡回結果と確認時点 |
| `discoveries` | 発見した公開元と探索経路 |
| `artifacts` | 候補ファイル、原典URL、コミットSHA、Blob SHA、改訂履歴 |
| `evidence` | リポジトリのIssue参照。個別Workflowの動作証拠とは区別する |
| `feeds` | モデル情報。WorkflowのJSONを取得した意味ではない |
| `references` | 自動取得の対象として確認されていない参考先 |
| `search_progress` | 検索の進行状況とAPIの失敗 |

Workflowはノードを接続した処理構成、Subgraphは再利用できる部分的な構成を指す。Blueprintは、この収集処理では `definitions.subgraphs` を含むJSONとして識別する。名称やファイルの形式だけでは、動作や品質は判断できない。

発見は公開ファイルの存在を確認したこと、静的確認はファイルの形式や参照を読んだこと、実行確認は指定した環境で動作を確かめたことを指す。用途タグは候補を探すために使い、ランキングや採用可否の判定には使わない。作者や出典が違う候補は別に記録する。

## 検索と出力

リポジトリのルートで、Pythonのコマンドを `uv` から実行する。

```sh
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export --format csv > .cache/workflow_registry.csv
uv run --locked python -m gwp.discovery export --format json > .cache/workflow_registry_export.json
```

収集結果はGitHub検索の件数上限と巡回数の制約を受ける。エクスポートした一覧は収集データから再生成し、別の正本として編集しない。
