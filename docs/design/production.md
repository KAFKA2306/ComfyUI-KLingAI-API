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

ComfyUIにWorkflowを送信して素材を回収し、制作先へ渡す手順を示す。作品の品質と公開状態は、素材を受け取った制作先で確認する。

## API形式のWorkflowを実行する

Pythonの環境管理とCLIの実行には `uv` を使う。ComfyUIをローカルの `http://127.0.0.1:8188` で起動し、実際に使用するWorkflowを「Export Workflow (API)」から `workflow-api.json` に保存する。制作先は固定一覧ではなく、`--target` に英小文字・数字・`-`・`_` からなる1～64文字の識別子を指定する。

以下の `TARGET` は制作案件の任意の識別子であり、8領域のいずれかに固定しない。

```sh
TARGET=project-identifier
RECEIPT=.cache/jobs/receipt.json
OUTPUT_ROOT=.cache/jobs/output
uv run --locked python -m gwp.production_job plan --target "$TARGET" --workflow workflow-api.json
uv run --locked python -m gwp.production_job submit --target "$TARGET" --workflow workflow-api.json --receipt "$RECEIPT"
uv run --locked python -m gwp.production_job collect --receipt "$RECEIPT" --output-root "$OUTPUT_ROOT"
```

`plan`はWorkflowと入力値を検査する。`submit`はComfyUIへ実行を依頼し、受け取ったジョブIDを`receipt`に保存する。`collect`は実行履歴で成功を確認した場合にファイルを回収し、それぞれのSHA-256を記録する。処理が終わっていなければ、完了後に`collect`を再実行する。

送信中に通信が切れた場合、`receipt` に `SUBMISSION_UNKNOWN` が残る。この状態では同じWorkflowを再送せず、次のコマンドでComfyUIの実行待ち・実行中のジョブを照合する。

```sh
uv run --locked python -m gwp.production_job status --receipt "$RECEIPT"
```

`status` がジョブIDを特定すると、`receipt` の状態が `SUBMITTED_NOT_COMPLETE` に更新される。その後、ジョブの成功を確認できた時点で`collect`を実行する。照合できない場合は送信結果を未確認のまま保持し、同じジョブを再送しない。新しいジョブを送るときは別のreceiptファイルを指定する。

## 制作先への受け渡し

制作先の既存ディレクトリを `PROJECT_ROOT` に指定する。BashまたはWSLではreceiptに記録されたジョブIDを読み取り、次のように受け渡す。

```sh
PROJECT_ROOT=/path/to/existing/project
PROMPT_ID=$(uv run --locked python -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["promptId"])' "$RECEIPT")
uv run --locked python -m gwp.production_job handoff --manifest "$OUTPUT_ROOT/$TARGET/$PROMPT_ID/manifest.json" --project-root "$PROJECT_ROOT"
```

`handoff` はSHA-256を照合し、制作先の `.artifacts/comfyui/<target>/<promptId>/` にファイルをコピーする。この作業領域は制作先のGit管理から除外する。回収できる拡張子は画像・動画・音声のほか、GLB・FBX・OBJを含む。3Dデータの構造や外観、利用条件は制作先で検査する。


