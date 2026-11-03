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

- [超長期ゴール](docs/vision.md)：8領域の到達状態と成功条件
- [アーキテクチャ](docs/architecture.md)：現行実装、正本データ、交換可能な構成
- [ナレッジの管理](docs/knowledge.md)：出典、改訂、タグ、メタデータの規約
- [運用手順](docs/operations.md)：uv、収集、制作、検証、公開の証拠

変更履歴はGitで確認できます。

## 必須の実行方法

Python 3.11以上を使い、依存関係、仮想環境、スクリプトとテストの実行を**uv**で統一します。

~~~sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export > workflows.csv
~~~

収集更新は `uv run --locked python -m gwp.discovery sync`。ネットワークを使用し、`.cache/workflow_registry.json`を更新します。実際の制作コマンドは[運用手順](docs/operations.md)に集約します。

## 制作の原則

- 公式とコミュニティの公開実践を収集し、人気や独自採点を理由に候補を排除しない。
- 発見、形式確認、GPUでの実行、制作物の品質検証、公開完了を別々に記録する。
- 必要な制作素材が生成・確認できない場合は未完成とする。Unity標準形状・単色マテリアル・空のシーンなどを自動生成して実素材や完成作品の代わりにしない。
- 未確認のWorkflow・モデル・Custom Nodeを収集段階で自動実行しない。利用条件と改訂を確認する。
- モデル、GPU、ComfyUI自体が変わっても、制作目標と出典付き知識を持ち越せる設計とする。
- 秘密情報、モデル本体、生成メディア、個人情報をGitに含めない。

