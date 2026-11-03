---
id: "readme"
title: "ComfyUI制作基盤"
kind: "index"
status: "active"
updated: "2026-11-03"
tags: ["ComfyUI","Workflow","制作","8領域","uv"]
related: ["docs/README.md","src/gwp/discovery.py"]
sources: ["https://github.com/Comfy-Org/ComfyUI","https://github.com/Comfy-Org/workflow_templates"]
---

# ComfyUI制作基盤：8領域の作品制作

公開Workflowを出典と改訂を保って収集し、作品の制作に利用します。最終的な成果は収集件数ではなく、次の8領域で完成させて公開する作品です。

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

8領域は独立して制作します。VRChatカフェは制作案件の一つであり、他領域の着手条件ではありません。

## 設計書とナレッジ

[文書索引](docs/README.md)から、[全体設計](docs/design/system.md)、[制作工程](docs/design/production.md)、[作品構成と演出](docs/design/creative.md)、[VRChatカフェ設計](docs/design/vrchat-cafe.md)、[台帳と用語](docs/knowledge/registry.md)、[情報源](docs/knowledge/sources.md)を参照できます。

8領域、収集元、採用Workflow、制作案件の設定正本は`config/registry.json`です。収集結果の再生成可能なキャッシュは`.cache/workflow_registry.json`です。両者の役割は[全体設計](docs/design/system.md)で定義します。

## 実行方法

Python 3.11以上を使います。環境構築、依存関係、スクリプト、テストは`uv`経由で実行します。

~~~sh
uv sync --locked
uv run --locked python -m gwp.registry validate
uv run --locked python -m gwp.registry summary
uv run --locked python scripts/validate_docs.py
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
~~~

`sync`はネットワークに接続します。制作先への素材の受け渡しは[制作工程](docs/design/production.md)で説明します。

## 制作の原則

公式とコミュニティ双方の公開Workflowを収集し、人気や独自採点を理由に候補を除外しません。発見しただけの第三者Workflow、Custom Node、モデルを自動実行しません。

素材の生成、作品への組み込み、品質の確認、公開は別工程です。単色の仮素材や空のシーンを実素材の代わりに完成扱いしません。認証情報、モデル本体、生成メディア、個人情報はGitに含めません。
