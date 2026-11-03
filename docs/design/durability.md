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

収集したWorkflowと制作履歴は、差分を追加しながら保持します。更新が失敗しても、直前に確定した台帳を使用できるようにします。

## 正本と保存先

mainの `config/registry.json` は制作目標・収集条件・制作案件の設定です。mainブランチの `data/workflow_registry.json` と `data/workflow_registry.json.sha256` は収集結果と制作履歴の正本です。`.cache/` はローカル作業領域で、GitHub Actionsのキャッシュや成果物も正本にはしません。

GitHubの履歴だけに依存しないよう、別媒体にも台帳を保管します。`gwp.state backup` は指定したディレクトリーへバックアップを作ります。バックアップの実行時期と保存先は運用者が管理します。生成メディアとモデル本体はGitへ入れず、台帳にはハッシュ、容量、保管場所、出典を記録します。

## 保存・差分統合

`scripts/catalog_sync.sh` はmainの台帳を取得し、整合性を確認して公開元を差分収集します。続いて `scripts/catalog_publish.sh` が最新のmainと差分を統合し、Gitへ保存します。ほかのPCが先に更新した場合は、新しい台帳を再取得して統合し、最大5回再試行します。入力ファイルは成功・失敗にかかわらず残します。

コードの原子的なファイル置換と、Gitへの保存は別の工程です。`gwp.state` は旧版の退避、スキーマ1から2への移行、SHA-256による整合確認を扱います。`status` または `verify --other` は前回の台帳から消えたIDを示します。欠損の原因はこの検査では特定しません。

## 別PCで取得・検証する

次の手順はBashまたはWSLを想定します。Gitからmainを取得し、台帳本体と検証用ファイルを同じ場所へ保存します。

```sh
git fetch origin main
mkdir -p .cache
git show origin/main:data/workflow_registry.json > .cache/restored.json
git show origin/main:data/workflow_registry.json.sha256 > .cache/restored.json.sha256
uv run --locked python -m gwp.state verify --catalog .cache/restored.json
```

破損時は、元のファイルを保持したまま正常なバックアップを確認し、`gwp.state restore --catalog <復旧先> --other <バックアップファイル>` で復元します。実行前にバックアップの検証ファイルも確認してください。

## 制作・公開履歴の更新

作品、採用Workflow、依存モデル、実行ジョブ、権利、公開の履歴は `gwp.ledger` で更新します。更新したローカル台帳は `scripts/catalog_publish.sh` でmainへ統合します。操作例では、`PROJECT_ID` に実際の案件ID、`PAYLOAD` にその案件のJSONファイルを指定します。

```sh
PROJECT_ID=project-id
PAYLOAD=/path/to/project.json
git fetch origin main
mkdir -p .cache
git show origin/main:data/workflow_registry.json > .cache/edit.json
git show origin/main:data/workflow_registry.json.sha256 > .cache/edit.json.sha256
uv run --locked python -m gwp.state verify --catalog .cache/edit.json
uv run --locked python -m gwp.ledger put --catalog .cache/edit.json --section projects --id "$PROJECT_ID" --payload "$PAYLOAD"
bash scripts/catalog_publish.sh .cache/edit.json
```

既存IDの内容を訂正する場合は `gwp.ledger put` に `--change-kind correction` を加えます。訂正イベントには変更前後のSHA-256と日時を保存します。保存できなかった場合、入力ファイルをそのまま保持して再実行します。

## 収集元の変更・実行の履歴

公開元の取得に失敗した場合は、削除と判定しません。ファイルの完全な一覧を取得できた場合に限り、削除を認定します。検索上限に達した期間は分割して探索し、なお取得できない範囲を記録します。PNG内のWorkflowは静的に抽出し、収集段階では実行しません。

原典ID、固定コミット、Blob SHA、改訂履歴を保持します。別作者が公開した同じ内容は出典別に保存し、ハッシュで関係を示します。候補の人気は収集対象から除外する理由にはしません。

採用・依存・実行は `adoptions`、`models`、`dependencies`、`environments`、`jobs` に記録します。送信結果が不明なジョブは `submission_unknown` として保持し、ComfyUI側の状態確認前に再送しません。

素材は `assets`、権利の根拠は `rights`、公開の確認は `publications` に記録します。`publications` を `verified` にするには、作品のHTTPS URL、公開先、案件ID、確認日時・方法、一次証拠URLが必要です。結果が分からないアップロードは `upload_unknown` と記録します。影響する作品・公開先は `gwp.ledger lineage` で追跡します。

## バックアップと検索

```sh
BACKUP_DIR=/path/to/independent/backup
uv run --locked python -m gwp.state backup --catalog .cache/restored.json --output "$BACKUP_DIR"
uv run --locked python -m gwp.ledger query --catalog .cache/restored.json --section artifacts --term VRChat
```

`BACKUP_DIR` にバックアップの保存先ディレクトリーを指定します。
