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

作品ごとに素材、場面、音、操作、公開用ファイルを制作単位として定義します。制作単位の依存関係を記録すると、素材を変更した際に確認し直す範囲を調べられます。制作内容や演出の良し悪しを自動で採点する機能ではありません。

## 制作仕様

各制作案件の `creative.json` に、次の情報を記述します。コマンドを実行する前に、案件IDと制作領域を[設定台帳](../../config/registry.json)の `projects` に登録してください。

| 項目 | 記述する内容 |
| --- | --- |
| `project_id`・`title` | 案件IDと作品名 |
| `missions` | 作品が属する制作領域 |
| `continuity` | 素材や場面で共有する美術、人物、音の条件 |
| `units` | 制作単位の目的、必要な成果物、依存先、Workflow参照 |
| `releases` | 公開先と、その公開に必要な制作単位 |

`units` の `workflow_ids` には `config/registry.json` に登録したWorkflow IDを指定します。`validate` は存在しないID、領域の不一致、依存関係の循環を検出します。モデルのライセンスや生成物の品質は、この構造検査では判定しません。

例えば動画は台本・音声・編集、3Dモデルは形状・材質・書き出しを制作単位に分けられます。作品ごとに必要な工程を定義し、その依存先を登録します。

## 制作順と変更の影響

`PLAN` と `UNIT` に既存の制作仕様ファイルと制作単位IDを指定します。次のパスとIDは実際の値に置き換えてください。

```sh
PLAN=/path/to/creative.json
UNIT=unit-id
uv run --locked python -m gwp.creative validate --plan "$PLAN"
uv run --locked python -m gwp.creative order --plan "$PLAN"
uv run --locked python -m gwp.creative impact --plan "$PLAN" --unit "$UNIT"
```

`order` は依存関係に沿った制作順を返します。`impact` は指定した単位に依存する制作単位と公開先を返します。結果は再検討する範囲であり、再生成の実施履歴ではありません。

素材の実行と受け渡しは[制作工程](production.md)のCLIで行います。作品の品質確認と公開は制作先で実施します。
