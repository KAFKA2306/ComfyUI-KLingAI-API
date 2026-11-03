---
id: "design-production"
title: "ComfyUIと制作工程の接続"
kind: "design"
status: "active"
updated: "2026-11-04"
tags: ["制作","素材","受け渡し","uv"]
related: ["src/gwp/production_job.py","src/gwp/production.py"]
sources: ["https://github.com/Comfy-Org/workflow_templates"]
---

# ComfyUIと制作工程の接続

ComfyUIの生成物を制作先へ渡す手順を定める。生成ジョブの成功だけでは、作品の動作・品質・公開は確認できない。

## API形式のWorkflowを実行する

ComfyUIを`http://127.0.0.1:8188`で起動し、使うWorkflowを「Export Workflow (API)」で`workflow-api.json`に保存する。CLIは`uv`で実行する。`--target`には英小文字・数字・`-`・`_`で構成した1～64文字の制作案件IDを指定する。

以下の`TARGET`は制作案件IDの記入例であり、特定の領域に固定しない。

```sh
TARGET=project-identifier
RECEIPT=.cache/jobs/receipt.json
OUTPUT_ROOT=.cache/jobs/output
uv run --locked python -m gwp.production_job plan --target "$TARGET" --workflow workflow-api.json
uv run --locked python -m gwp.production_job submit --target "$TARGET" --workflow workflow-api.json --receipt "$RECEIPT"
uv run --locked python -m gwp.production_job collect --receipt "$RECEIPT" --output-root "$OUTPUT_ROOT"
```

`plan`は入力を検査し、`submit`はComfyUIから返されたジョブIDをreceiptに記録する。`collect`は成功履歴を確認してから生成ファイルを回収し、各ファイルのSHA-256を保存する。

## 制作先への受け渡し

`PROJECT_ROOT`に既存プロジェクトのディレクトリを指定する。BashまたはWSLではreceiptからジョブIDを読み取り、次のコマンドでファイルを渡す。

```sh
PROJECT_ROOT=/path/to/existing/project
PROMPT_ID=$(uv run --locked python -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["promptId"])' "$RECEIPT")
uv run --locked python -m gwp.production_job handoff --manifest "$OUTPUT_ROOT/$TARGET/$PROMPT_ID/manifest.json" --project-root "$PROJECT_ROOT"
```

`handoff`はSHA-256を照合してから、制作先の`.artifacts/comfyui/$TARGET/`へコピーする。この領域は制作先のGit管理から除外する。画像・動画・音声・GLB・FBX・OBJなどを受け渡せるが、ファイルの拡張子とハッシュが正しくても、3D構造や見た目の品質は保証できない。制作先で素材の利用条件、動作、性能、公開条件を確認する。
