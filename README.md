---
id: readme
title: ComfyUI Workflows Factory
type: entrypoint
status: active
updated: 2026-11-03
tags: [制作基盤, Workflow, ナレッジ, 8領域, uv]
---

# ComfyUI Workflows Factory

公開されているComfyUIのWorkflowを探し、出典と改訂履歴を記録して制作に活用します。8つの領域で作品を同時並列に制作・公開し、使ったWorkflowと手順を次の制作にも生かすためのリポジトリです。

## 対等な8つの長期目標

| 領域 | 完成して公開するもの |
| --- | --- |
| VRChatワールド | カフェ、Chill World、探索・交流ワールド |
| アバター・衣装 | VRM、衣装、アクセサリー |
| BOOTH商品 | 販売・配布できる3D素材、背景、デジタル商品 |
| YouTube・Shorts | 解説、短編、キャラクター動画 |
| Podcast・音声 | 音声番組、ナレーション、音響素材 |
| 映画・アニメーション | 短編、連続映像、映像作品 |
| 3Dモデル | キャラクター、建築、家具、ゲーム向けモデル |
| ゲーム制作 | ゲーム本体、世界、キャラクター、UI、素材 |

8領域は対等です。領域ごとに制作・検証・公開を進め、VRChatカフェの完成を他の領域の開始条件にはしません。

## 文書の正本

- [設計書・ナレッジの索引](docs/README.md)：文書のメタデータとタグ規約
- [システム設計](docs/design/system.md)：出典収集と実行の境界
- [制作工程](docs/design/production.md)：ローカル生成・受け渡し
- [VRChatカフェ設計](docs/design/vrchat-cafe.md)：出典候補と形式検査
- [Workflow台帳と用語](docs/knowledge/registry.md)：データの意味と検索
- [一次資料](docs/knowledge/sources.md)：原典と利用条件

## 必須の実行方法

Python 3.11以上を使い、依存関係、仮想環境、スクリプトとテストの実行を**uv**で統一します。

~~~sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export > workflows.csv
~~~

収集更新は `uv run --locked python -m gwp.discovery sync`。ネットワークを使用し、`.cache/workflow_registry.json`を更新します。実際の制作コマンドは[制作工程](docs/design/production.md)に集約します。
