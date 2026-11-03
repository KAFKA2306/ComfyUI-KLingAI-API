---
id: "design-creative"
title: "作品構成と演出の設計"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["作品構成","演出","制作単位","依存関係"]
related: ["src/gwp/creative.py","projects/vrchat-cafe/creative.json","docs/design/production.md"]
sources: []
---

# 作品構成と演出の設計

1つの作品を、素材、場面、音、操作、公開用の成果物に分けて管理する。各制作単位の目的と依存先を明確にし、素材の変更が作品のどこに影響するかを調べられるようにする。

## 制作仕様のデータ

[カフェの制作仕様](../../projects/vrchat-cafe/creative.json)は、作品の構成と必要な成果物を記述するJSONである。

| キー | 内容 |
| --- | --- |
| `project_id`、`title` | 作品の識別子と名前 |
| `missions` | 8領域のうち、この作品が属する領域 |
| `continuity` | 複数の素材でそろえる美術、人物、音などの条件 |
| `units` | 制作単位ごとの目的、成果物、依存先、参照元 |
| `releases` | 公開先の識別子と、公開に必要な制作単位 |

`workflow_ids` は一元台帳 `config/registry.json` の登録済みWorkflow IDを参照する。存在しないIDや、制作案件と一致しない領域は `validate` で検出する。ライセンスや品質の良否をここでは判定しない。

制作単位には、例えば `architecture`（建築メッシュ）、`cup`（陶器カップ）、`lighting`（照明）、`world-assembly`（Unityへの統合）がある。`lighting` は建築と家具が必要で、`world-assembly` は照明、歩行設定、カップ、環境音がそろってから進める。

## 依存関係を確認する

Pythonの実行には `uv` を使う。

```sh
uv run --locked python -m gwp.creative validate --plan projects/vrchat-cafe/creative.json
uv run --locked python -m gwp.creative order --plan projects/vrchat-cafe/creative.json
uv run --locked python -m gwp.creative impact --plan projects/vrchat-cafe/creative.json --unit cup
```

`validate` は必須項目、参照先、依存関係の循環を確認する。`order` は制作単位の依存関係から実施順を返す。`impact` は指定した単位を変更したとき、確認し直す必要がある単位と公開先を返す。

これらのコマンドは素材の生成、作品の品質検査、公開を実行しない。素材の生成と受け渡しには[制作工程への接続](production.md)のCLIを使う。生成した素材が作品の条件に合うかは、実際の制作先で確認する。

## 8領域への展開

同じ構造を、動画なら脚本・カット・音声・字幕、音声番組なら構成・収録・編集、ゲームなら操作・状態・UI・世界の制作単位に適用できる。各領域で完成に必要な成果物を定め、参照するWorkflowと依存関係を結び付ける。
