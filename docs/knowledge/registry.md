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

8領域の目標・制作案件・収集条件・検索分類は main の `config/registry.json` を設定正本とする。収集した出典、改訂履歴、制作・公開履歴は catalog ブランチの `data/workflow_registry.json` に永続保存する。ローカルの `.cache/workflow_registry.json` は一時的な作業コピーであり、正本ではない。保存・復旧手順は[台帳の保全設計](../design/durability.md)に定める。

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

Workflowはノードを接続した処理構成、Subgraphは再利用できる部分的な構成を指す。Blueprintは、この収集処理では `definitions.subgraphs` を含むJSONとして識別する。名称やファイルの形式だけでは、動作や品質は判断できない。

発見は公開ファイルの存在を確認したこと、静的確認はファイルの形式や参照を読んだこと、実行確認は指定した環境で動作を確かめたことを指す。用途タグは候補を探すために使い、ランキングや採用可否の判定には使わない。作者や出典が違う候補は別に記録する。

## 検索と出力

リポジトリのルートで、Pythonのコマンドを `uv` から実行する。

```sh
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.state verify --catalog .cache/workflow_registry.json
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export --format csv > .cache/workflow_registry.csv
uv run --locked python -m gwp.discovery export --format json > .cache/workflow_registry_export.json
```

収集結果はGitHub検索の件数上限と巡回数の制約を受ける。エクスポートした一覧は収集データから再生成し、別の正本として編集しない。

## Workflowの選定と絞り込み

収集台帳は削除・上書きせず、用途の手掛かりで閲覧候補を抽出する。最新・人気・適性は別々の情報であり、品質の自動採点や採用判断を意味しない。

```sh
uv run --locked python -m gwp.select --mission 3d-models --sort suitable --inspected-only
uv run --locked python -m gwp.select --mission youtube --sort popular --min-stars 1
uv run --locked python -m gwp.select --mission vrchat-world --sort latest --updated-within-days 90
uv run --locked python -m gwp.select --mission games --sort suitable --format csv > .cache/game-workflows.csv
```

`--mission` にはREADMEに示した8領域の識別子を使う。`--sort suitable` は対応する検索語、明示的な用途登録、静的形式確認との一致を順序に利用する。`popular` はGitHubリポジトリのスター数、`latest` はリポジトリの最終push日を使う。どちらもWorkflow単体の利用者数、更新日、作品品質とは異なる。条件を掛ける場合は `--min-stars` と `--updated-within-days` を明示する。指標が欠損している候補は閾値指定時に一致しない。

既定では公開元のGitHubメタデータをその場で照会する。`--offline` では台帳中に利用できる公開元メタデータだけを利用し、存在しない値は推定しない。`--inspected-only` は `workflow-ui`、`workflow-api`、`blueprint` と静的に確認されたものだけを表示する。指定しなければ未検査の候補も保持して表示できる。設定正本に登録済みで収集台帳にない原典候補は `registry-only` と表示し、実行確認済みとはみなさない。

原典の利用条件はGitHubリポジトリのライセンスだけでは確定しない。モデル・Custom Node・制作物への利用許諾、GPUでの実行と出力品質は別に確認する。
