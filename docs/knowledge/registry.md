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

制作目標、制作案件、収集元の設定はmainの `config/registry.json` に保存します。収集した候補と制作履歴はcatalogの `data/workflow_registry.json` に保存し、ローカルの `.cache/workflow_registry.json` は作業コピーとして使います。保存・復旧・競合統合は[台帳の保全・復旧](../design/durability.md)に記載します。

## 台帳の項目

| 項目 | 記録内容 |
| --- | --- |
| `repositories`・`discoveries` | 巡回したリポジトリ、発見した公開元、探索経路 |
| `artifacts` | 候補の原典URL、固定コミット、Blob SHA、改訂履歴 |
| `evidence` | 公開元のIssueへの参照 |
| `feeds`・`references` | モデルのメタデータと参考サイト |
| `search_progress`・`content_index` | 未走査範囲、取得エラー、同じBlob SHAを持つ公開元 |
| `events` | 台帳の追記・訂正の履歴 |
| `adoptions`・`models`・`dependencies`・`environments` | Workflowの採用版、モデル、Custom Node、実行環境 |
| `projects`・`jobs`・`assets` | 制作案件、実行状態、生成素材 |
| `rights`・`publications`・`knowledge` | 利用条件、公開の確認、再利用する知識 |

公開ファイルの存在確認を「発見」、形式・ノード参照の読み取りを「静的確認」、指定した環境での実行を「実行確認」と呼びます。これらの状態は別に記録します。Issueがあることは個々のWorkflowの動作確認になりません。

Workflowはノードを接続した処理構成です。Subgraphは再利用する部分的な構成です。この収集処理では、JSONの `definitions.subgraphs` を含む場合にBlueprintと識別します。ファイル名や分類だけで利用条件や品質を決めません。

用途タグは検索に使います。作者・出典が異なる候補は別IDに保持し、内容が同じ場合はハッシュで関係を示します。

## 台帳の確認と出力

以下は `.cache/workflow_registry.json` に台帳を取得済みの場合の操作です。取得手順は[台帳の保全・復旧](../design/durability.md)を参照してください。

```sh
uv run --locked python -m gwp.state verify --catalog .cache/workflow_registry.json
uv run --locked python -m gwp.discovery stats --catalog .cache/workflow_registry.json
uv run --locked python -m gwp.discovery search --catalog .cache/workflow_registry.json --term VRChat
uv run --locked python -m gwp.discovery export --catalog .cache/workflow_registry.json --format csv > workflows.csv
uv run --locked python -m gwp.discovery export --catalog .cache/workflow_registry.json --format json > workflows.json
```

CSVとJSONの書き出し結果は閲覧用です。正本として編集せず、必要なときに台帳から再生成します。収集対象の件数はGitHub検索と巡回の上限に左右されます。
## Workflow候補の絞り込み

`gwp.select` は台帳を変更せず、8領域の用途、公開元の人気、更新時期から表示順を決めます。検索に使う指標と作品の品質は区別してください。

`--mission` に指定するIDは `vrchat-world`、`avatars`、`booth`、`youtube`、`podcast`、`movies`、`3d-models`、`games` です。

```sh
uv run --locked python -m gwp.select --mission 3d-models --sort suitable --inspected-only
uv run --locked python -m gwp.select --mission youtube --sort popular --min-stars 1
uv run --locked python -m gwp.select --mission vrchat-world --sort latest --updated-within-days 90
uv run --locked python -m gwp.select --mission games --sort suitable --format csv > game-workflows.csv
```

`suitable` は用途登録、検索語、静的確認の結果を使って表示順を決めます。`popular` はリポジトリのスター数、`latest` はリポジトリの最終push日時を使います。これらは個別Workflowの人気、更新日、品質を表しません。

`--inspected-only` は形式を静的確認した候補だけを表示します。`--min-stars` と `--updated-within-days` は指定した条件で表示を絞ります。指標が取得できない候補は、その条件を指定した場合に表示されません。収集台帳からは削除しません。

既定ではGitHubから公開元のメタデータを取得します。`--offline` は台帳内の情報のみを使います。原典だけが設定に登録され、未収集の候補は `registry-only` と表示します。実行や商用利用を確認した意味ではありません。
