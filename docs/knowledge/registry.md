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

設定は`main`の`config/registry.json`、収集・改訂・制作・公開履歴は`catalog`の`data/workflow_registry.json`に置く。`.cache/workflow_registry.json`は作業コピーであり、復旧には使わない。保存と復旧の手順は[台帳の保全設計](../design/durability.md)を参照する。

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

Workflowはノードを接続した処理構成、Subgraphは再利用する部分構成を指す。収集器は`definitions.subgraphs`を含むJSONをBlueprintとして分類する。分類結果だけで動作や品質を判断しない。

「発見」は公開ファイルの存在確認、「静的確認」は形式・参照の読み取り、「実行確認」は指定環境での動作確認を指す。用途タグは検索用であり、順位や採否を決めない。同じ内容でも作者や出典が違えば別の候補として残す。

## 検索と出力

リポジトリのルートで`uv`から実行する。

```sh
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.state verify --catalog .cache/workflow_registry.json
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export --format csv > .cache/workflow_registry.csv
uv run --locked python -m gwp.discovery export --format json > .cache/workflow_registry_export.json
```

検索APIには件数上限があり、巡回数にも制限を設けている。エクスポートしたCSV・JSONは再生成可能な出力であり、正本として編集しない。
