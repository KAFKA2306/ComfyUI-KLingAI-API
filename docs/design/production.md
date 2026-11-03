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

ComfyUIで生成した画像・動画・音声を、作品制作に使うための受け渡し手順を定める。素材の生成成功と、Unityでの動作、商品販売、VRChatへの公開は、制作先で確認する別の工程である。

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

`plan` は入力を検査する。`submit` はComfyUIへ実行を依頼し、戻されたジョブIDをreceiptに保存する。`collect` はジョブの成功履歴を確認してからファイルを回収し、それぞれのSHA-256を記録する。送信後、`collect` がジョブの成功履歴を確認してファイルを回収する。処理が終わっていなければ、完了後に改めて`collect`を実行する。

送信中に通信が切れた場合、`receipt` に `SUBMISSION_UNKNOWN` が残る。この状態では同じWorkflowを再送せず、次のコマンドでComfyUIの実行待ち・実行中のジョブを照合する。

```sh
uv run --locked python -m gwp.production_job status --receipt "$RECEIPT"
```

`status` がジョブIDを特定すると、`receipt` の状態が `SUBMITTED_NOT_COMPLETE` に更新される。その後、ジョブの成功を確認できた時点で`collect`を実行する。照合できない場合は未確認のまま保持し、重複送信を避ける。

## 制作先への受け渡し

制作先の既存ディレクトリを `PROJECT_ROOT` に指定する。BashまたはWSLではreceiptに記録されたジョブIDを読み取り、次のように受け渡す。

```sh
PROJECT_ROOT=/path/to/existing/project
PROMPT_ID=$(uv run --locked python -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["promptId"])' "$RECEIPT")
uv run --locked python -m gwp.production_job handoff --manifest "$OUTPUT_ROOT/$TARGET/$PROMPT_ID/manifest.json" --project-root "$PROJECT_ROOT"
```

`handoff` はファイルのハッシュを照合し、制作先の `.artifacts/comfyui/$TARGET/` 配下にコピーする。制作先ではこの作業領域をGit管理から除外する。画像・動画・音声・GLB・FBX・OBJなど、コードが許可した拡張子を回収できるが、拡張子の確認だけでは3D構造や見た目を検証したことにならない。

素材を受け取った制作先が、依存モデルと素材の利用条件、見た目、性能、公開条件を確認して作品を完成させる。
