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

作品を素材・場面・音・操作・公開物などの制作単位に分け、目的と依存先を記録する。変更した素材に依存する制作単位と公開物を追跡できるようにする。

## 制作仕様のデータ

制作案件の`creative.json`に作品構成と成果物を記述し、案件IDと領域を[設定ファイル](../../config/registry.json)の`projects`に対応させる。

| キー | 内容 |
| --- | --- |
| `project_id`、`title` | 作品の識別子と名前 |
| `missions` | 8領域のうち、この作品が属する領域 |
| `continuity` | 複数の素材でそろえる美術、人物、音などの条件 |
| `units` | 制作単位ごとの目的、成果物、依存先、参照元 |
| `releases` | 公開先の識別子と、公開に必要な制作単位 |

`workflow_ids`には`config/registry.json`に登録したWorkflow IDを指定する。`validate`は存在しないIDや案件と一致しない領域を検出するが、ライセンスや品質は判定しない。

依存関係は作品の要件から決める。映像作品なら脚本・音声・編集、3Dモデルなら形状・材質・書き出しを別の制作単位として扱える。

## 依存関係を確認する

既存の制作仕様ファイルを`PLAN`、影響を調べたい制作単位IDを`UNIT`に指定する。コマンドは`uv`で実行する。

```sh
uv run --locked python -m gwp.creative validate --plan "$PLAN"
uv run --locked python -m gwp.creative order --plan "$PLAN"
uv run --locked python -m gwp.creative impact --plan "$PLAN" --unit "$UNIT"
```

`validate`は必須項目、参照先、依存関係の循環を検査する。`order`は依存順、`impact`は変更の影響を受ける制作単位と公開先を返す。いずれも素材の生成・品質検査・公開は行わない。生成と受け渡しは[制作工程](production.md)を参照する。

## 8領域への展開

動画では脚本・カット・音声・字幕、音声番組では構成・収録・編集、ゲームでは操作・状態・UI・世界を制作単位にできる。領域ごとに成果物を定め、使うWorkflowと依存先を結び付ける。
