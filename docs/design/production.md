---
id: "design-production"
title: "制作工程への接続"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["制作","素材","受け渡し","uv"]
related: ["src/gwp/production_job.py","src/gwp/production.py"]
sources: ["https://github.com/Comfy-Org/workflow_templates"]
---

# 制作工程への接続

ComfyUIの責任は素材の生成です。画像・動画・GLBの生成成功と、Unityでの動作、BOOTH販売、VRChat公開を同一視しません。

| 対象 | ComfyUIから渡す候補 | 完成判定 |
| --- | --- | --- |
| `image2outfit` | 衣装・素材の画像、テクスチャ | 型紙、スキニング、Unity、品質検査 |
| `vrmine-cafe` | カフェの背景、小物、質感 | Blender、Unity、VRChat実機 |
| `tripo-3d` | 3D入力用の多視点画像 | メッシュ、リグ、アバター適合 |

制作先は固定リストを持ちません。CLIは制作先の識別子を検査し、完成判定は受け渡し先の制作プロジェクトが保持します。

## 実行手順

ComfyUIから **Export Workflow (API)** したJSONを指定し、Python実行には必ず `uv` を使います。

```sh
uv run --locked python -m gwp.production_job plan --target vrmine-cafe --workflow workflow-api.json
uv run --locked python -m gwp.production_job submit --target vrmine-cafe --workflow workflow-api.json --receipt .artifacts/receipt.json
uv run --locked python -m gwp.production_job collect --receipt .artifacts/receipt.json --output-root .artifacts/output
uv run --locked python -m gwp.production_job handoff --manifest .artifacts/output/vrmine-cafe/＜promptId＞/manifest.json --project-root ../vrmine
```

`plan` は実行せず検査し、`submit` はローカルのComfyUIへ送信します。`collect` は成功履歴を検査してSHA-256付きの出力を回収します。`handoff` は対象リポジトリを識別し、素材を指定の非追跡領域に受け渡します。

モデル・Custom Nodeの権利、GPU動作、Blender/Unity適合、公開の成功はそれぞれ別に検証します。受け渡しが成功しても完成済みにはしません。
