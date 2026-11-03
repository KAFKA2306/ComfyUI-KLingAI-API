---
id: "design-vrchat-cafe"
title: "VRChat小型カフェ制作設計"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["VRChat","カフェ","Unity","3D"]
related: ["config/registry.json","projects/vrchat-cafe/cafe_pipeline.py"]
sources: ["https://creators.vrchat.com/worlds/creating-your-first-world/","https://vcc.docs.vrchat.com/"]
---

# VRChat小型カフェ制作設計

[候補Workflow](../../config/registry.json)には、カップの3Dモデルと360度背景に使うWorkflowの原典パスが登録されています。取得・形式検査の処理は[cafe_pipeline.py](../../projects/vrchat-cafe/cafe_pipeline.py)にあります。

## コマンド

~~~sh
uv run --locked python projects/vrchat-cafe/cafe_pipeline.py snapshot
uv run --locked python projects/vrchat-cafe/cafe_pipeline.py check --strict
uv run --locked python projects/vrchat-cafe/cafe_pipeline.py glb --file path/to/model.glb
~~~
