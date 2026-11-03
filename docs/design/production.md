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

制作先は固定リストを持ちません。CLIは制作先の識別子を検査し、出力先は受け渡し先の `.artifacts/comfyui/` です。

## 実行手順

ComfyUIから **Export Workflow (API)** したJSONを指定し、Python実行には必ず `uv` を使います。

```sh
uv run --locked python -m gwp.production_job plan --target vrmine-cafe --workflow workflow-api.json
uv run --locked python -m gwp.production_job submit --target vrmine-cafe --workflow workflow-api.json --receipt .artifacts/receipt.json
uv run --locked python -m gwp.production_job collect --receipt .artifacts/receipt.json --output-root .artifacts/output
uv run --locked python -m gwp.production_job handoff --manifest .artifacts/output/vrmine-cafe/PROMPT_ID/manifest.json --project-root ../vrmine
```

`PROMPT_ID` は `submit` の応答に含まれる `promptId` です。`plan` は実行せず検査し、`submit` はローカルのComfyUIへ送信します。`collect` は成功履歴を検査してSHA-256付きの出力を回収します。`handoff` は指定した既存ディレクトリへハッシュ照合済みの素材をコピーします。
