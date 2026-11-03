---
id: "design-durable-registry"
title: "台帳の保全・復旧・制作履歴の設計"
kind: "design"
status: "active"
updated: "2026-11-04"
tags: ["台帳", "差分収集", "保全", "復旧", "制作履歴", "公開証拠"]
related: ["src/gwp/state.py", "src/gwp/ledger.py", "src/gwp/discovery.py", "scripts/catalog_sync.sh", "scripts/catalog_publish.sh", ".github/workflows/collect.yml"]
sources: ["https://docs.github.com/en/rest/git/trees", "https://docs.github.com/en/rest/search/search", "https://docs.github.com/en/actions/reference/dependency-caching-reference"]
---

# 台帳の保全・復旧・制作履歴

## 正本とバックアップ

目標・収集条件・制作案件の設定は`main`の`config/registry.json`を正本とする。収集・制作・公開履歴は`catalog`の`data/workflow_registry.json`へ保存し、同名の`.sha256`ファイルで内容を検証する。GitHub Actionsのキャッシュや一時成果物は正本ではない。

GitHubだけでは独立したバックアップにならない。USB、NAS、別のクラウド保存先などに検証可能なスナップショットを作り、元のGitHubリポジトリが使えなくても復元できるか確認する。生成メディアとモデル本体はGitに置かず、台帳へSHA-256・容量・保管場所・出典を記録する。認証情報は保存しない。

## PC交換・破損・復元

PCを交換したらリポジトリをcloneして`catalog`をfetchし、JSONと`.sha256`を取得する。`gwp.state verify`で一致を確認する。破損時は`gwp.state restore`で検証済みの版から復元し、壊れたファイルを隔離する。候補数が減った場合は前版とIDを比較し、原典の削除・巡回漏れ・台帳の破損を分けて調べる。再収集で件数が一致しても、失われたIDや改訂履歴を復元した証拠にはならない。

## 同時更新・履歴・スキーマ

作業用台帳は`catalog`の最新版から作る。ローカル保存では一時ファイルを同期して置換し、検証済みの旧版を退避する。pushが競合したら正本を取り直し、IDと改訂履歴を統合して再試行する。旧スキーマからの移行では既存IDを保持する。訂正は追記と区別し、変更前後の値・SHA-256・日時・根拠URLをイベントとして残す。

## 制作・公開履歴の確定

制作・採用・モデル・権利・公開の記録は、`catalog`から取得した作業台帳へ`gwp.ledger put`で追加し、`scripts/catalog_publish.sh`で確定する。入力台帳に`.sha256`がなければ処理を止める。SHA-256の不一致も送信前に検出する。収集処理も同じ保存経路を使う。

複数PCの同時更新では、最新の`catalog`と作業台帳をID・改訂・イベント単位で統合する。pushが失敗したら最大5回まで再試行する。失敗時も入力台帳は残し、制作・公開記録を`main`へ直接書き込まない。

```sh
git fetch origin catalog
mkdir -p .cache
git show origin/catalog:data/workflow_registry.json > .cache/edit.json
git show origin/catalog:data/workflow_registry.json.sha256 > .cache/edit.json.sha256
uv run --locked python -m gwp.state verify --catalog .cache/edit.json
uv run --locked python -m gwp.ledger put --catalog .cache/edit.json --section projects --id sample-project --payload /path/to/project.json
bash scripts/catalog_publish.sh .cache/edit.json
```

`/path/to/project.json`と`sample-project`は実際のファイルと案件IDに置き換える。既存のIDを訂正するときは`--change-kind correction`を付ける。

## 発見・検索・改訂

原典の削除は、ファイル一覧を最後まで取得できたときだけ記録する。APIエラーや途中停止で見つからなかったファイルを削除済みと扱わない。GitHub検索は作成日で期間を分割して1,000件の取得上限に対応する。未探索ページや分割後も上限を超える区間は残す。PNG内のWorkflowはメタデータを読み取るだけで実行しない。

同じ内容でも作者や原典が違えば別IDで記録し、Blob SHAで関連づける。改訂、作者変更、移転、配布停止後も出典リンクと確認済みの過去版を残す。検索語・同義語・8領域タグは重複を許し、人気や独自採点で候補を除外しない。

## 採用・制作・公開

`adoptions`には採用したWorkflowのID・固定コミット・Blob SHA・制作案件を記録する。`models`と`dependencies`には配布URL、固定版、ハッシュ、利用条件の原典を残す。`environments`にはComfyUI・GPU・VRAM・ライブラリと検証条件を記録する。第三者コードは未確認のまま自動導入・実行しない。

`jobs`はWorkflow、入力、Seed、`client_id`、`prompt_id`、環境、状態を結びつける。送信結果が不明なら`submission_unknown`と記録し、サーバー側の状態を調べる前に再送しない。生成ファイルごとにSHA-256を確認し、部分成功と全件成功を区別する。

8領域の作品構成は`projects`と`gwp.creative`で管理する。`assets`には素材のハッシュ・入力・保管場所、`rights`には版ごとの権利根拠、`knowledge`には確認済みの知識を記録する。未完成の素材を単色の仮形状で代用して完成扱いしない。

`publications`で公開済みと記録するには、作品URL、公開先、確認日時・方法、一次証拠URLが必要となる。通信断で投稿結果が不明なら`upload_unknown`とし、確認前の二重投稿を避ける。非公開化や新版公開は履歴を残して更新する。権利上の問題が見つかったら`gwp.ledger lineage`で影響する作品と公開先を調べる。

## 運用コマンド

~~~sh
uv sync --locked
mkdir -p .cache
git fetch origin catalog
git show origin/catalog:data/workflow_registry.json > .cache/restored.json
git show origin/catalog:data/workflow_registry.json.sha256 > .cache/restored.json.sha256
uv run --locked python -m gwp.state verify --catalog .cache/restored.json
uv run --locked python -m gwp.state backup --catalog .cache/restored.json --output /別媒体/backup
uv run --locked python -m gwp.ledger query --catalog .cache/restored.json --section artifacts --term VRChat
~~~

収集設定の変更は`gwp.registry validate`で検査する。GPU・品質・公開の確認を実施していなければ、成功とは記録しない。
