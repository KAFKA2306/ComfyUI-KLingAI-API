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
| VRChatワールド | Chill World、探索・交流・体験型ワールド |
| アバター・衣装 | VRM、衣装、アクセサリー |
| BOOTH商品 | 3D素材、背景、デジタル商品 |
| YouTube・Shorts | 解説動画、短編、キャラクター動画 |
| Podcast・音声 | 音声番組、ナレーション、音響素材 |
| 映画・アニメーション | 短編、連続映像、映像作品 |
| 3Dモデル | キャラクター、建築、家具、ゲーム向けモデル |
| ゲーム制作 | ゲーム本体、ワールド、キャラクター、UI、素材 |

8領域は対等です。各領域で制作・検証・公開を並行して進め、特定の作品の完成を別の領域の開始条件にしません。

## 設計書と台帳

[文書索引](docs/README.md)から、[全体設計](docs/design/system.md)、[台帳の保全・復旧](docs/design/durability.md)、[制作工程](docs/design/production.md)、[作品構成と演出](docs/design/creative.md)、[台帳と用語](docs/knowledge/registry.md)、[情報源](docs/knowledge/sources.md)を参照できます。

制作目標・収集条件・制作案件の設定は、`main` ブランチの [config/registry.json](config/registry.json)で管理します。収集した候補と制作履歴の正本は、mainブランチの `data/workflow_registry.json` と同名の `.sha256` ファイルです。ローカルの `.cache/` は作業用です。

## 実行方法

Python 3.11以上が必要です。Pythonの環境構築、依存関係、スクリプト、テストは `uv` で実行します。

```sh
uv sync --locked
uv run --locked python -m gwp.registry validate
uv run --locked python scripts/validate_docs.py
uv run --locked python -m unittest discover -s tests -v
```

ローカルで収集台帳を読む場合は、mainから台帳本体と検証用ファイルを取得します。BashまたはWSLで次のコマンドを実行してください。

```sh
git fetch origin main
mkdir -p .cache
git show origin/main:data/workflow_registry.json > .cache/workflow_registry.json
git show origin/main:data/workflow_registry.json.sha256 > .cache/workflow_registry.json.sha256
uv run --locked python -m gwp.state verify --catalog .cache/workflow_registry.json
uv run --locked python -m gwp.discovery stats --catalog .cache/workflow_registry.json
uv run --locked python -m gwp.discovery search --catalog .cache/workflow_registry.json --term VRChat
```

収集から競合統合、mainへの保存までの運用コマンドは `bash scripts/catalog_sync.sh` です。GitHubへの読み書き権限とネットワーク接続が必要です。`gwp.discovery sync` 単体はローカル台帳を更新し、mainへは保存しません。収集結果の保存と復旧は[台帳の保全・復旧](docs/design/durability.md)、素材生成は[制作工程](docs/design/production.md)を参照してください。

## Workflow候補の絞り込み

既存の台帳は変更せず、用途と静的確認の結果で候補を並べられます。次の例は上で取得した台帳を参照します。

```sh
uv run --locked python -m gwp.select --mission 3d-models --sort suitable --inspected-only
uv run --locked python -m gwp.select --mission youtube --sort popular --min-stars 1
uv run --locked python -m gwp.select --mission games --sort latest --updated-within-days 90
```

`popular` はGitHubリポジトリのスター数、`latest` はリポジトリの最終push日時を使います。Workflow単体の人気や更新時刻を示すものではありません。絞り込みの条件は[台帳と用語](docs/knowledge/registry.md)にまとめています。

