---
id: readme
title: ComfyUI Workflows Factory
type: entrypoint
status: active
updated: 2026-11-03
tags: [制作基盤, Workflow, ナレッジ, 8領域, uv]
---

# ComfyUI Workflows Factory

公開されたComfyUI Workflowを**出典付きで蓄積・再利用**し、8つの制作目標を**同時並列**で進める共通基盤です。Workflowの収集自体は最終成果ではありません。各領域で完成作品を公開し、次の制作に知識と工程を再利用することが目的です。

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

番号や表の順番は**優先順位・実施順ではありません**。8領域は独立して着手・制作・検証・公開します。VRChatカフェは一つの実証案件であり、他の7領域の開始条件にはなりません。

## 文書の正本

- [設計・ナレッジ索引](docs/README.md)：文書規約、タグとメタデータ
- [全体設計](docs/design/system.md)：アーキテクチャ
- [制作工程](docs/design/production.md)：生成・受け渡し・完成判定
- [VRChat小型カフェ](docs/design/vrchat-cafe.md)：制作と公開の検証
- [Workflow台帳](docs/knowledge/registry.md)：用語と記録
- [一次資料](docs/knowledge/sources.md)：出典とライセンス

旧設計の経緯はGitの履歴に残し、現行の説明を重複させません。

## 必須の実行方法

Pythonの依存・仮想環境・コマンド実行は**uvを使用**します。Python 3.11以上が必要です。

~~~sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export > workflows.csv
~~~

収集更新は `uv run --locked python -m gwp.discovery sync`。ネットワークを使用し、`.cache/workflow_registry.json`を更新します。実際の制作コマンドは[制作工程](docs/design/production.md)に集約します。

## 守る境界

- 公式とコミュニティの公開実践を収集し、人気や独自採点を理由に候補を排除しない。
- 発見、形式確認、GPUでの実行、制作物の品質検証、公開完了を別々に記録する。
- 必要な制作素材が生成・確認できない場合は未完成とする。Unity標準形状・単色マテリアル・空のシーンなどを自動生成して実素材や完成作品の代わりにしない。
- 未確認のWorkflow・モデル・Custom Nodeを収集段階で自動実行しない。利用条件と改訂を確認する。
- モデル、GPU、ComfyUI自体が変わっても、制作目標と出典付き知識を持ち越せる設計とする。
- 秘密情報、モデル本体、生成メディア、個人情報をGitに含めない。

