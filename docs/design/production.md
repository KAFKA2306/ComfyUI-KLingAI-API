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

ローカルのComfyUIへAPI形式のWorkflowを送信し、生成したファイルを制作先へ渡します。画像・動画・音声・3D素材の生成から、作品への組み込みと公開までを区別します。

## 実行の準備

Pythonの環境とCLIは `uv` で管理します。ComfyUIを `http://127.0.0.1:8188` で起動し、使用するWorkflowを「Export Workflow (API)」で `workflow-api.json` に保存します。

`TARGET` は制作先を区別する1～64文字の識別子です。英小文字、数字、ハイフン、下線を使えます。固定の制作先一覧への登録は必要ありません。各実行の `RECEIPT` は別ファイルにしてください。

```sh
TARGET=project-identifier
RECEIPT=.cache/jobs/receipt.json
OUTPUT_ROOT=.cache/jobs/output
uv run --locked python -m gwp.production_job plan --target "$TARGET" --workflow workflow-api.json
uv run --locked python -m gwp.production_job submit --target "$TARGET" --workflow workflow-api.json --receipt "$RECEIPT"
```

`plan` はWorkflowの入力形式を検査します。`submit` はComfyUIへ実行を依頼し、応答から得たジョブIDをreceiptに保存します。送信途中の通信断ではreceiptが `SUBMISSION_UNKNOWN` のまま残ります。重複送信を避けるため、この状態では新たな `submit` を行わず、次のコマンドで確認します。

```sh
uv run --locked python -m gwp.production_job status --receipt "$RECEIPT"
uv run --locked python -m gwp.production_job collect --receipt "$RECEIPT" --output-root "$OUTPUT_ROOT"
```

`status` は取得できた実行状態を表示します。`collect` はComfyUIの完了履歴が成功を示した場合に出力を回収し、各ファイルのSHA-256を記録します。未完了・失敗・結果不明のジョブから完成ファイルを回収したことにはしません。

## 制作先への受け渡し

既存の制作プロジェクトのディレクトリーを `PROJECT_ROOT` に指定します。BashまたはWSLでは、receiptのジョブIDを読み取って次のように実行できます。

```sh
PROJECT_ROOT=/path/to/existing/project
PROMPT_ID=$(uv run --locked python -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["promptId"])' "$RECEIPT")
uv run --locked python -m gwp.production_job handoff --manifest "$OUTPUT_ROOT/$TARGET/$PROMPT_ID/manifest.json" --project-root "$PROJECT_ROOT"
```

`handoff` はファイルのハッシュを確認し、`PROJECT_ROOT/.artifacts/comfyui/$TARGET/$PROMPT_ID/` へコピーします。制作先では `.artifacts/` をGit管理から除外してください。拡張子の許可とSHA-256の一致はファイル内容の品質、3D構造、権利を保証しません。制作先で実素材の表示、性能、利用条件を確認してから作品へ組み込みます。
