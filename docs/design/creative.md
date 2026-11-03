---
id: "design-creative"
title: "作品構成と演出の接続設計"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["作品構成","演出","連続性","制作依存"]
related: ["src/gwp/creative.py","projects/vrchat-cafe/creative.json","docs/design/production.md"]
sources: []
---

# 作品構成と演出の接続設計

作品の意図、美術、素材、場面、公開を制作単位IDで結びます。Workflowは素材を作る手段であり、作品の完成条件の代わりではありません。採用する公開Workflowを独自スコアで選別せず、単色素材やUnity標準形状を実素材の代用品として完成扱いしません。

## 作品構成の正本

各作品の `creative.json` は制作要求の正本であり、進捗メモではありません。`missions` に制作領域、`continuity` に共有美術・人物・音の一貫性、`units` に制作単位の目的・必要な出力・依存先・候補原典ID、`releases` に公開先と必要な制作単位を記述します。素材本体や公開済みの証拠はこの仕様に偽装して保存しません。

## 8領域への適用

| 領域 | 具体的な制作単位 | 接続する成果 |
| --- | --- | --- |
| VRChat | 空間、建築、家具、照明、環境音、移動・衝突 | 歩行可能なUnityワールドと公開 |
| アバター・衣装 | 顔、衣装、表情、リグ、アニメーション | 同一人物の連続性と着替え |
| BOOTH | 商品本体、素材、説明画像、使用条件、ZIP | 購入者が使える配布商品 |
| YouTube・Shorts | 脚本、カット、音声、字幕、尺、サムネイル | 同期した動画編集と公開 |
| Podcast | 番組構成、台本、声、効果音、ミキシング | 音声エピソード |
| 映画・アニメ | 脚本、シーン、ショット、演技、色、音 | 連続した映像作品 |
| 3Dモデル | 形状、UV、材質、縮尺、リグ、形式 | 利用先に適合するモデル |
| ゲーム | ゲームルール、操作、状態、UI、世界、音 | プレイ可能なビルド |

## 変更影響と実行の境界

~~~sh
uv run --locked python -m gwp.creative validate --plan projects/vrchat-cafe/creative.json
uv run --locked python -m gwp.creative order --plan projects/vrchat-cafe/creative.json
uv run --locked python -m gwp.creative impact --plan projects/vrchat-cafe/creative.json --unit cup
~~~

`order` は依存関係に従う制作順、`impact` は変更した単位に依存する場面・公開先を示します。美術的な採用判断を自動化せず、創作の意図を勝手に決めません。素材実行は `gwp.production_job`、品質・権利・公開確認は各制作先の責務です。

## 演出上の具体的な確認

顔や服装が複数カットで変わらないか、台本と口の動きが音声に同期するか、ゲームの状態が入力で変化するか、3Dの実寸・照明・衝突が整合するか。これらは作品ごとの仕様として明示し、生成素材が存在しない場合は完成と呼びません。
