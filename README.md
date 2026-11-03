---
id: "readme"
title: "ComfyUI制作基盤"
kind: "index"
status: "active"
updated: "2026-11-04"
tags: ["ComfyUI","Workflow","制作","8領域","uv"]
related: ["docs/README.md","src/gwp/discovery.py"]
sources: ["https://github.com/Comfy-Org/ComfyUI","https://github.com/Comfy-Org/workflow_templates"]
---

# ComfyUI制作基盤

公開されているComfyUIのWorkflowを収集し、出典と改訂履歴を残して作品制作に利用します。目標は、次の8領域で作品を完成・公開し、制作に使った工程と知識を再利用できるようにすることです。

## 対等な8つの長期目標

| 領域 | 公開する作品 |
| --- | --- |
| VRChatワールド | カフェ、Chill World、探索・交流ワールド |
| アバター・衣装 | VRM、衣装、アクセサリー |
| BOOTH商品 | 3D素材、背景、デジタル商品 |
| YouTube・Shorts | 解説動画、短編、キャラクター動画 |
| Podcast・音声 | 音声番組、ナレーション、音響素材 |
| 映画・アニメーション | 短編、連続映像、映像作品 |
| 3Dモデル | キャラクター、建築、家具、ゲーム向けモデル |
| ゲーム制作 | ゲーム本体、ワールド、キャラクター、UI、素材 |

各領域の制作は並行して進めます。VRChatカフェは個別案件の一つで、他領域の開始条件にはしません。

## 設計書と台帳

設計書・制作手順・出典ナレッジは[文書索引](docs/README.md)にまとめています。

制作目標・収集条件・制作案件の設定は、mainの[config/registry.json](config/registry.json)で管理します。収集した候補と制作履歴の正本は、catalogブランチの `data/workflow_registry.json` と同名の `.sha256` ファイルです。ローカルの `.cache/` は作業用です。

## 実行方法

Python 3.11以上が必要です。Pythonの環境構築、依存関係、スクリプト、テストは `uv` で実行します。

```sh
uv sync --locked
uv run --locked python -m gwp.registry validate
uv run --locked python scripts/validate_docs.py
uv run --locked python -m unittest discover -s tests -v
```

ローカルで収集台帳を読む場合は、catalogから台帳本体と検証用ファイルを取得します。BashまたはWSLで次のコマンドを実行してください。

```sh
git fetch origin catalog
mkdir -p .cache
git show origin/catalog:data/workflow_registry.json > .cache/workflow_registry.json
git show origin/catalog:data/workflow_registry.json.sha256 > .cache/workflow_registry.json.sha256
uv run --locked python -m gwp.state verify --catalog .cache/workflow_registry.json
uv run --locked python -m gwp.discovery stats --catalog .cache/workflow_registry.json
uv run --locked python -m gwp.discovery search --catalog .cache/workflow_registry.json --term VRChat
```

収集から競合統合、catalogへの保存までの運用コマンドは `bash scripts/catalog_sync.sh` です。GitHubへの読み書き権限とネットワーク接続が必要です。`gwp.discovery sync` 単体はローカル台帳を更新し、catalogへは保存しません。収集結果の保存と復旧は[台帳の保全・復旧](docs/design/durability.md)、素材生成は[制作工程](docs/design/production.md)を参照してください。

## Workflow候補の絞り込み

既存の台帳は変更せず、用途と静的確認の結果で候補を並べられます。次の例は上で取得した台帳を参照します。

```sh
uv run --locked python -m gwp.select --mission 3d-models --sort suitable --inspected-only
uv run --locked python -m gwp.select --mission youtube --sort popular --min-stars 1
uv run --locked python -m gwp.select --mission games --sort latest --updated-within-days 90
```

`popular` はGitHubリポジトリのスター数、`latest` はリポジトリの最終push日時を使います。Workflow単体の人気や更新時刻を示すものではありません。絞り込みの条件は[台帳と用語](docs/knowledge/registry.md)にまとめています。

## 制作の原則

公式とコミュニティの公開Workflowを収集し、人気や独自の点数で候補を除外しません。外部のWorkflow、モデル、Custom Nodeは、利用条件と実行環境を確認してから使用します。

素材の生成、作品への組み込み、品質確認、公開は別の工程として扱います。必要な素材がない場合、単色の仮素材や空のシーンを完成作品の代わりにしません。認証情報、モデル本体、生成メディア、個人情報はGitへ保存しません。
