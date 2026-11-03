---
id: "design-vrchat-cafe"
title: "VRChat小型カフェ制作設計"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["VRChat","カフェ","Unity","3D"]
related: ["projects/vrchat-cafe/workflows.json","projects/vrchat-cafe/GWPCafeBuilder.cs","projects/vrchat-cafe/cafe_pipeline.py"]
sources: ["https://creators.vrchat.com/worlds/creating-your-first-world/","https://vcc.docs.vrchat.com/"]
---

# VRChat小型カフェ制作設計

目的は歩行可能な小型カフェをVRChatへアップロードし、**実際のワールドURL**を確認することです。JSON、画像、GLB、Unityシーンの生成だけで公開済みとは判断しません。

初期設計は6 m × 6 m、天井高3 mの部屋に入口、窓、机、椅子、カウンター、照明、衝突判定、スポーン位置を持たせます。ただし実際の素材が揃わない状態で、Unityの標準形状・単色素材や空のシーンを代用品として完成扱いしません。

`projects/vrchat-cafe/workflows.json` にはHunyuan3D・TRELLIS2のカップ、Qwen 360の背景候補があります。12 GB GPUでの動作、モデルの商用権利、VRChat適合は確認していません。背景パノラマは衝突可能な建築メッシュの代替ではありません。

## 作業手順

1. `uv run --locked python projects/vrchat-cafe/cafe_pipeline.py check` で取得済みWorkflowの整合性を確認する。`snapshot` は出典JSON取得であり、生成ではない。
2. VRChat Creator CompanionでWorldsプロジェクトを作り、管理されるUnityとSDKを使う。権利と品質を確認した実素材を取り込む。
3. AI生成小物を採用する前にモデル・素材のライセンスを調べ、GLBの構造、材質、縮尺とUnityインポートを確認する。
4. VRChat SDKのBuild & Testで入口、衝突、表示、FPS、エラーを検証する。Questは別に実機検証する。
5. アップロード後、ワールドURLと公開状態を確認し、制作案件の公開記録に保存する。
