---
id: "design-creative"
title: "作品構成と演出の設計"
kind: "design"
status: "active"
updated: "2026-11-04"
tags: ["作品構成","演出","制作単位","依存関係"]
related: ["src/gwp/creative.py","config/registry.json","docs/design/production.md"]
sources: []
---

# 作品構成と演出の設計

作品を素材、場面、音、操作、公開用の成果物などの制作単位に分ける。制作単位の依存関係を記録し、素材を変更したときに確認し直す工程と公開先を特定する。

## 制作仕様のデータ

作品ごとの `creative.json` に構成と必要な成果物を記述する。事前に[設定台帳](../../config/registry.json)の `projects` へ制作案件を登録し、`project_id` と領域を一致させる。

| キー | 内容 |
| --- | --- |
| `project_id`、`title` | 作品の識別子と名前 |
| `missions` | 8領域のうち、この作品が属する領域 |
| `continuity` | 複数の素材でそろえる美術、人物、音などの条件 |
| `units` | 制作単位ごとの目的、成果物、依存先、参照元 |
| `releases` | 公開先の識別子と、公開に必要な制作単位 |

制作単位の `workflow_ids` には、設定台帳の `workflows` に登録されたIDを指定する。`validate` はIDと領域の参照、制作単位の依存関係を検査する。利用条件や生成物の品質は制作先で確認する。

制作単位は作品の要求に応じて定義する。例えば映像なら脚本・音声・編集、3Dモデルなら形状・材質・書き出しを分けられる。

## 依存関係を確認する

Pythonの実行には `uv` を使う。`PLAN` には登録済みの作品の制作仕様ファイル、`UNIT` にはそのファイル内の制作単位IDを指定する。下のパスとIDは実際の値に置き換える。

```sh
PLAN=/path/to/creative.json
UNIT=asset-id
uv run --locked python -m gwp.creative validate --plan "$PLAN"
uv run --locked python -m gwp.creative order --plan "$PLAN"
uv run --locked python -m gwp.creative impact --plan "$PLAN" --unit "$UNIT"
```

`validate` は必須項目と参照先、依存関係の循環を検査する。`order` は依存関係に沿った制作順、`impact` は変更に伴う再確認の対象を出力する。素材の生成と受け渡しには[制作工程のCLI](production.md)を使う。
