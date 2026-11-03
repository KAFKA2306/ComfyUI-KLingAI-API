---
id: "design-durable-registry"
title: "台帳の保全・復旧・制作履歴の設計"
kind: "design"
status: "active"
updated: "2026-11-04"
tags: ["台帳", "差分収集", "保全", "復旧", "制作履歴", "公開証拠"]
related: ["src/gwp/state.py", "src/gwp/ledger.py", "src/gwp/discovery.py", "scripts/catalog_sync.sh", ".github/workflows/collect.yml"]
sources: ["https://docs.github.com/en/rest/git/trees", "https://docs.github.com/en/rest/search/search", "https://docs.github.com/en/actions/reference/dependency-caching-reference"]
---

# 台帳の保全・復旧・制作履歴

## 正本とバックアップ

制作目標、収集条件、Workflow候補、制作案件の設定は、`main` ブランチの `config/registry.json` で管理する。収集結果と制作履歴は `catalog` ブランチの `data/workflow_registry.json` に保存し、同名の `.sha256` ファイルで整合性を確かめる。GitHub Actionsのキャッシュと一時成果物は作業用とする。

GitHubとは別のUSB、NAS、クラウドフォルダーなどにも、定期的にバックアップを保存する。`gwp.state backup` では、指定した保存先にSHA-256付きのコピーを作成できる。生成メディアとモデル本体はGitに入れず、台帳にはハッシュ、容量、保管場所、出典を記録する。認証情報は保存しない。

## PC交換・破損・復元

PCを交換した場合はリポジトリを `git clone` し、`catalog` ブランチを取得する。台帳と `.sha256` を `gwp.state verify` で検査し、別媒体のバックアップから戻すときは `gwp.state restore` を使う。破損した台帳は隔離し、検証済みの版から復元する。候補数が減ったときは前版とのID差分と収集エラーを調べ、原因を特定する。

## 同時更新・履歴・スキーマ

収集処理は最新の台帳を読み、更新結果を別ファイルへ書き出す。保存時には同期書き込みと原子的な置換を行い、旧版を退避する。`git push` が競合した場合は最新の台帳を再取得し、IDと改訂履歴を統合して再試行する。スキーマを更新するときも既存IDを保持する。訂正には変更前後の値、SHA-256、日時、根拠URLを記録する。

## 制作・公開履歴の確定

採用、モデル、権利、制作、公開の記録は、`catalog` から取得した作業用台帳に `gwp.ledger put` で追加する。`scripts/catalog_publish.sh` で共有台帳へ統合する。入力台帳には対応する `.sha256` ファイルが必要で、ハッシュが一致しない場合は送信を停止する。収集処理も同じ統合手順を使う。

複数のPCから更新された記録は、ID、改訂、変更イベントを照合して統合する。公開処理が失敗した場合も入力台帳は残す。制作・公開の履歴は `main` に直接書き込まない。

```sh
git fetch origin catalog
mkdir -p .cache
git show origin/catalog:data/workflow_registry.json > .cache/edit.json
git show origin/catalog:data/workflow_registry.json.sha256 > .cache/edit.json.sha256
uv run --locked python -m gwp.state verify --catalog .cache/edit.json
uv run --locked python -m gwp.ledger put --catalog .cache/edit.json --section projects --id sample-project --payload /path/to/project.json
bash scripts/catalog_publish.sh .cache/edit.json
```

`/path/to/project.json` は実際の案件記録ファイル、`sample-project` は登録する案件のIDに置き換える。既存記録の訂正には `--change-kind correction` を指定し、変更前後の値をイベントに残す。

## 発見・検索・改訂

原典ファイルの削除は、対象リポジトリの一覧を完全に取得できた場合に確認する。APIエラーや途中停止は収集失敗として記録する。GitHub検索の1,000件制限に達する場合は、作成日の範囲を分割して探索する。未走査の範囲も記録する。PNG内のWorkflowは静的に抽出し、探索中には実行しない。

内容が同じWorkflowでも出典ごとにIDを残し、Blob SHAで関連づける。改訂、作者変更、リポジトリ移転、配布停止を確認した場合は、出典URLと過去版への参照を保存する。検索語と用途タグは重複を許し、人気や独自採点による除外には使わない。

## 採用・制作・公開

`adoptions` にはWorkflow ID、固定コミット、Blob SHA、使用する制作案件と領域を記録する。`models` と `dependencies` には配布URL、固定版、ハッシュ、Custom Node、利用条件の出典を記録する。`environments` にはComfyUI、GPU、VRAM、ライブラリー、実測条件を記録する。第三者のコードは収集時に自動で導入・実行しない。

`jobs` にはWorkflow、入力、Seed、`client_id`、`prompt_id`、実行環境、ジョブ状態を記録する。送信結果が不明な場合は `submission_unknown` とし、サーバー側の状態を確認してから再送を判断する。生成ファイルごとにSHA-256を照合し、回収が一部にとどまる場合は全件成功と記録しない。

8領域の作品構成は `projects` と `gwp.creative` で扱う。素材・場面・音声・編集・配布物の依存関係を記録し、`assets` には素材のハッシュ、生成時の入力、保管先、`rights` には版ごとの権利根拠、`knowledge` には確認した知識を登録する。必要な素材が不足している作品は完成として記録しない。

`publications` に公開を記録する際は、作品URL、公開先、確認日時、確認方法、一次証拠URLを登録する。通信が切れて結果を確認できない場合は `upload_unknown` とし、重複投稿を避ける。非公開化や新版公開は変更として追記し、過去の記録を残す。権利上の指摘を受けた場合は `gwp.ledger lineage` で関連する素材と公開先を調べる。

## 運用コマンド

~~~sh
uv sync --locked
git fetch origin catalog
mkdir -p .cache
git show origin/catalog:data/workflow_registry.json > .cache/restored.json
git show origin/catalog:data/workflow_registry.json.sha256 > .cache/restored.json.sha256
uv run --locked python -m gwp.state verify --catalog .cache/restored.json
uv run --locked python -m gwp.state backup --catalog .cache/restored.json --output /path/to/separate/backup
uv run --locked python -m gwp.ledger query --catalog .cache/restored.json --section artifacts --term VRChat
~~~

収集設定の変更は `gwp.registry validate` で検査する。実行結果と公開状態は、それぞれの確認記録に基づいて登録する。
