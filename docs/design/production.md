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

以下は、アバター向け素材を生成する例である。

```sh
uv run --locked python -m gwp.production_job plan --target avatars --workflow workflow-api.json
uv run --locked python -m gwp.production_job submit --target avatars --workflow workflow-api.json --receipt .cache/jobs/avatars-receipt.json
uv run --locked python -m gwp.production_job collect --receipt .cache/jobs/avatars-receipt.json --output-root .cache/jobs/output
```

`plan` は入力を検査する。`submit` はComfyUIへ実行を依頼し、戻されたジョブIDをreceiptに保存する。`collect` はジョブの成功履歴を確認してからファイルを回収し、それぞれのSHA-256を記録する。送信しただけでは生成が完了したことにならない。

## 制作先への受け渡し

隣の `../image2outfit` に実際の制作リポジトリがある場合、BashまたはWSLでは次のコマンドで受け渡せる。

```sh
PROMPT_ID=$(uv run --locked python -c 'import json; from pathlib import Path; print(json.loads(Path(".cache/jobs/avatars-receipt.json").read_text(encoding="utf-8"))["promptId"])')
uv run --locked python -m gwp.production_job handoff --manifest ".cache/jobs/output/avatars/$PROMPT_ID/manifest.json" --project-root ../image2outfit
```

`handoff` はファイルのハッシュを照合し、制作先の `.artifacts/comfyui/avatars/` 配下にコピーする。制作先ではこの作業領域をGit管理から除外する。CLIが回収できるのは対応形式の画像・動画・音声で、GLBは対象外である。

素材を受け取った制作先が、依存モデルと素材の利用条件、見た目、性能、公開条件を確認して作品を完成させる。
