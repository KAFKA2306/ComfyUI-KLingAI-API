---
id: "design-production"
title: "ComfyUIと制作工程の接続"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["制作","素材","受け渡し","uv"]
related: ["src/gwp/production_job.py","src/gwp/production.py"]
sources: ["https://github.com/Comfy-Org/workflow_templates"]
---

# ComfyUIと制作工程の接続

ComfyUIで生成した画像、動画、音声、3Dファイルを制作先へ渡す手順を定める。ファイルを回収した後は、各制作先で品質を確認し、作品に組み込んで公開する。

## API形式のWorkflowを実行する

Pythonの実行には `uv` を使う。ComfyUIを `http://127.0.0.1:8188` で起動し、使うWorkflowを「Export Workflow (API)」で `workflow-api.json` に保存する。`--target` には制作案件の識別子を指定する。使用できる文字は英小文字・数字・`-`・`_`、長さは1～64文字である。

例では、制作案件の識別子に `project-identifier` を使う。

```sh
TARGET=project-identifier
RECEIPT=.cache/jobs/receipt.json
OUTPUT_ROOT=.cache/jobs/output
uv run --locked python -m gwp.production_job plan --target "$TARGET" --workflow workflow-api.json
uv run --locked python -m gwp.production_job submit --target "$TARGET" --workflow workflow-api.json --receipt "$RECEIPT"
uv run --locked python -m gwp.production_job collect --receipt "$RECEIPT" --output-root "$OUTPUT_ROOT"
```

`plan` は入力の形式を確認する。`submit` はComfyUIにWorkflowを送信し、返された `promptId` を `receipt` に保存する。`collect` は成功したジョブからファイルを回収し、各ファイルのSHA-256を記録する。

## 制作先への受け渡し

既存の制作先ディレクトリーを `PROJECT_ROOT` に指定する。BashまたはWSLでは、`receipt` に保存した `promptId` を読み取って素材を渡す。

```sh
PROJECT_ROOT=/path/to/existing/project
PROMPT_ID=$(uv run --locked python -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["promptId"])' "$RECEIPT")
uv run --locked python -m gwp.production_job handoff --manifest "$OUTPUT_ROOT/$TARGET/$PROMPT_ID/manifest.json" --project-root "$PROJECT_ROOT"
```

`handoff` はSHA-256を照合し、制作先の `.artifacts/comfyui/$TARGET/` 以下へファイルをコピーする。この作業領域はGit管理から除外する。回収できる拡張子には画像・動画・音声のほか、GLB・FBX・OBJがある。ファイルの中身や見た目、動作、利用条件は制作先で確認する。
