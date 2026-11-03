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

このリポジトリでは、公開されたComfyUI Workflowの出典と改訂履歴を残し、8領域の作品制作に使う。収集件数ではなく、完成して公開した作品を成果とする。

## 対等な8つの長期目標

| 領域 | 公開する作品 |
| --- | --- |
| VRChatワールド | カフェ、Chill World、探索・交流ワールド |
| アバター・衣装 | VRM、衣装、アクセサリー |
| BOOTH商品 | 3D素材、背景、デジタル商品 |
| YouTube・Shorts | 解説、短編、キャラクター動画 |
| Podcast・音声 | 音声番組、ナレーション、音響素材 |
| 映画・アニメーション | 短編、連続映像、映像作品 |
| 3Dモデル | キャラクター、建築、家具、ゲーム向けモデル |
| ゲーム制作 | ゲーム本体、ワールド、キャラクター、UI、素材 |

8領域は並行して進める。VRChatカフェはその一案件であり、ほかの領域の開始を妨げない。

## 設計書とナレッジ

詳しい設計と用語は[文書索引](docs/README.md)から参照する。

目標・収集元・制作案件は`config/registry.json`で設定する。収集したWorkflowと制作・公開履歴は`catalog`ブランチの`data/workflow_registry.json`へ保存する。`.cache/`は一時ファイル用で、正本にはしない。保存と復旧の方法は[台帳保全・復旧](docs/design/durability.md)を参照する。

## 実行方法

Python 3.11以上と`uv`を使う。環境構築・実行・テストは`uv`に統一する。

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

`sync`はネットワークへアクセスする。素材の生成と受け渡しは[制作工程](docs/design/production.md)を参照する。

## 制作の原則

公式とコミュニティの両方を探索し、人気や独自スコアで収集候補を除外しない。発見した第三者のWorkflow、Custom Node、モデルは自動実行しない。

素材の生成だけでは作品の完成や公開を意味しない。制作先で品質を確認し、公開URLを検証して記録する。仮素材や空のシーンを完成品として扱わない。認証情報・個人情報・モデル本体・生成メディアはGitへ登録しない。
