---
id: "knowledge-registry"
title: "Workflow台帳と用語"
kind: "knowledge"
status: "active"
updated: "2026-11-04"
tags: ["Workflow","ナレッジ","メタデータ","検索"]
related: ["src/gwp/discovery.py","config/registry.json"]
sources: ["https://github.com/Comfy-Org/workflows"]
---

# Workflow台帳と用語

8領域の目標、Workflow候補、制作案件、収集条件は `main` ブランチの `config/registry.json` で管理する。収集した出典、改訂履歴、制作・公開履歴は `catalog` ブランチの `data/workflow_registry.json` に保存する。ローカルの `.cache/workflow_registry.json` は作業用コピーである。復旧手順は[台帳の保全・復旧](../design/durability.md)を参照する。

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
| `content_index` | 同じBlob SHAを持つ複数の公開元 |
| `events` | 追記・訂正の変更前後と根拠 |
| `adoptions`・`models`・`dependencies`・`environments` | 固定版の採用と実行依存 |
| `projects`・`jobs`・`assets` | 制作、実行、生成素材の来歴 |
| `rights`・`publications`・`knowledge` | 権利の根拠、公開証拠、再利用する知識 |

Workflowはノードを接続した処理の構成、Subgraphは再利用するためにまとめた部分構成を指す。この収集処理では、JSONに `definitions.subgraphs` が含まれるものをBlueprintとして識別する。形式を識別した後、実行結果と品質は別に確認する。

公開元の発見、候補ファイルの取得、JSONの静的確認、実行確認は別の段階として記録する。実行確認では、指定した環境でWorkflowが動作したかを扱う。用途タグは検索用であり、候補の順位付けや採用可否には使わない。出典が異なる候補は別IDで保持する。

## 検索と出力

リポジトリのルートで次のコマンドを実行する。

```sh
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.state verify --catalog .cache/workflow_registry.json
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export --format csv > .cache/workflow_registry.csv
uv run --locked python -m gwp.discovery export --format json > .cache/workflow_registry_export.json
```

GitHub検索の件数上限や巡回範囲の制約により、収集一覧は公開Workflowの全件を示すものではない。CSV・JSONは台帳の作業用コピーから生成し、別の正本として編集しない。
