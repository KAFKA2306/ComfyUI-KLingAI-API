---
id: "design-vrchat-cafe"
title: "VRChat小型カフェの制作設計"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["VRChat","カフェ","Unity","3D"]
related: ["config/registry.json","projects/vrchat-cafe/cafe_pipeline.py"]
sources: ["https://creators.vrchat.com/worlds/creating-your-first-world/","https://vcc.docs.vrchat.com/"]
---

# VRChat小型カフェの制作設計

小型カフェをVRChatで歩けるワールドとして完成させ、公開ページのURLと公開状態を確認する。入口、窓、客席、カウンター、照明、衝突判定、スポーン位置を備え、来訪者が実際に利用できる空間にする。

## 素材を用意する

[一元台帳](../../config/registry.json)の `projects.vrchat-cafe.workflows` に、Hunyuan3DとTRELLIS2による小物、Qwenによる360度背景の参照元を記している。原典のJSONを保存して内容を確認するには次を実行する。

```sh
uv run --locked python projects/vrchat-cafe/cafe_pipeline.py snapshot
uv run --locked python projects/vrchat-cafe/cafe_pipeline.py check --strict
```

`snapshot` は公開元のJSONを取得し、`check --strict` は取得したファイルの整合性を確認する。両者はモデルの実行や作品の生成を行わない。採用するWorkflowのモデル、Custom Node、素材の利用条件を調べてから実際に生成する。

生成したGLBは次のコマンドで基本構造を確認できる。ファイル名は実際に生成したものに置き換える。

```sh
uv run --locked python projects/vrchat-cafe/cafe_pipeline.py glb --file cup.glb
```

背景パノラマは建築メッシュや衝突判定の代わりにならない。外観、材質、縮尺、Unityへの取り込み結果は実際の素材で確認する。

## ワールドを作って公開する

VRChat Creator CompanionでWorldsプロジェクトを作成し、指定されたUnityとSDKを使う。BlenderとUnityに利用条件を確認した素材を組み込み、客席や移動経路を整える。必要な素材が不足する場合は制作を続け、標準形状だけの仮シーンを完成品として扱わない。

VRChat SDKのBuild & Testで歩行、衝突、表示、フレームレート、エラーを確認する。Questにも公開する場合は、その対象環境で別に検証する。アップロード後にワールドページを開き、実際の公開URLと公開状態を確認する。
