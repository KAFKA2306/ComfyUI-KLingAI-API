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

# ComfyUI制作基盤：8領域の作品制作

公開されているComfyUIのWorkflowを収集し、出典と改訂履歴を記録します。収集したWorkflowを利用し、次の8領域で作品を制作・公開することが長期目標です。

## 対等な8つの長期目標

| 領域 | 公開する作品 |
| --- | --- |
| VRChatワールド | Chill World、探索・交流ワールド |
| アバター・衣装 | VRM、衣装、アクセサリー |
| BOOTH商品 | 3D素材、背景、デジタル商品 |
| YouTube・Shorts | 解説、短編、キャラクター動画 |
| Podcast・音声 | 音声番組、ナレーション、音響素材 |
| 映画・アニメーション | 短編、連続映像、映像作品 |
| 3Dモデル | キャラクター、建築、家具、ゲーム向けモデル |
| ゲーム制作 | ゲーム本体、ワールド、キャラクター、UI、素材 |

8領域は対等です。各領域で制作・検証・公開を並行して進め、特定の作品の完成を他領域の着手条件にしません。

## 設計書とナレッジ

文書の一覧は[設計書とナレッジの索引](docs/README.md)にあります。収集の仕組みは[全体設計](docs/design/system.md)、制作の手順は[制作工程](docs/design/production.md)、作品内の依存関係は[作品構成と演出](docs/design/creative.md)で説明します。

8領域、収集元、Workflow候補、制作案件の設定は `config/registry.json` で管理します。収集結果と制作履歴は `catalog` ブランチの `data/workflow_registry.json` に保存し、`.cache/` は一時作業用に使います。保存と復旧の手順は[台帳の保全・復旧](docs/design/durability.md)を参照してください。

## 実行方法

Python 3.11以上を使用し、環境構築、スクリプト、テストは `uv` から実行します。

~~~sh
uv sync --locked
uv run --locked python -m gwp.registry validate
uv run --locked python -m gwp.registry summary
uv run --locked python scripts/validate_docs.py
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.state verify --catalog .cache/workflow_registry.json
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
~~~

`sync` は公開情報を取得するためにネットワークへ接続します。制作先への素材の受け渡しには[制作工程のコマンド](docs/design/production.md)を使います。

## 制作の原則

公式とコミュニティの公開Workflowを収集し、人気や独自スコアで候補を除外しません。第三者のWorkflowやCustom Node、モデルは、収集時には実行しません。

生成した素材は各制作先で組み込みと品質確認を行ってから公開します。仮素材だけの作品を完成品として扱わず、認証情報、モデル本体、生成メディア、個人情報はGitに保存しません。
