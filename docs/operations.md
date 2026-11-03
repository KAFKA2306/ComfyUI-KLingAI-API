---
id: operations
title: 運用と作品公開の手順
type: operations
status: active
updated: 2026-11-03
tags: [uv, 運用, 収集, テスト, VRChat, 制作]
---

# 運用と作品公開の手順

## 必須：uvで統一する

Python 3.11以上を用意し、ローカルとGitHub ActionsでPythonの環境管理とコマンド実行に`uv`を使います。モデルの依存環境は制作先ごとに管理します。

~~~sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m compileall -q src
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export > workflows.csv
~~~

CSVはUTF-8 BOM付き。Windowsや表計算で文字化けしにくい形式です。出典の正本を編集せずにいつでも再出力できます。

## 公開Workflowの収集

~~~sh
uv run --locked python -m gwp.discovery sync --max-repos 12 --discovery-pages 1 --inspect-limit 50
~~~

`sync` はインターネット接続とGitHub等へのアクセスが必要です。`.cache/workflow_registry.json`を更新します。失敗や未解析も記録し、候補を品質スコアで排除しません。

`.github/workflows/collect.yml` は6時間ごと（UTC 0:17、6:17、12:17、18:17）と手動実行で収集します。GitHub Actionsの開始時刻は前後します。GPU実行・作品公開は行いません。

## ローカルComfyUIから制作先への受け渡し

制作先の固定台帳は設けません。`--target` は生成物を整理するための任意の識別子です（英小文字・数字・`_`・`-`、1～64文字）。8つの制作領域すべてで同じCLIを利用できます。入力にはComfyUIの **Export Workflow (API)** で保存したJSONが必要です。

~~~sh
uv run --locked python -m gwp.production_job plan --target youtube-shorts --workflow workflow-api.json
uv run --locked python -m gwp.production_job submit --target youtube-shorts --workflow workflow-api.json --receipt .artifacts/receipt.json
uv run --locked python -m gwp.production_job collect --receipt .artifacts/receipt.json --output-root .artifacts/output
uv run --locked python -m gwp.production_job handoff --manifest .artifacts/output/youtube-shorts/<promptId>/manifest.json --project-root ../creative-project
~~~

`submit` は既定でローカル `http://127.0.0.1:8188` に実行要求を送ります。`<promptId>` はreceiptの値に置き換えます。受け渡し先には既存のプロジェクトディレクトリを指定します。生成物は `.artifacts/comfyui/<target>/<promptId>/` に保存し、SHA-256で内容を確認します。素材が生成できても作品の品質・完成・公開は保証されません。形式とファイルサイズの制限も維持します。

## VRChat小型カフェの公開確認

VRChatカフェは8領域のうちの一案件です。他の領域と並行して制作します。

1. `projects/vrchat-cafe/workflows.json` に記された候補の出典・モデル・ライセンスを確認する。
2. `uv run --locked python projects/vrchat-cafe/cafe_pipeline.py snapshot` で候補のWorkflowを取得し、`uv run --locked python projects/vrchat-cafe/cafe_pipeline.py check --strict` で保存物の整合性を調べる。取得だけでは実行成功ではありません。
3. 採用したWorkflowを実行し、実際の制作素材を得る。GLBは `uv run --locked python projects/vrchat-cafe/cafe_pipeline.py glb --file <path.glb>` で形式を確認する。ただし形式検査だけでは外観、権利、VRChat適合を保証しない。
4. 出典と利用条件を確認した実素材をBlender/Unityへ統合し、VRChat Creator Companionが指定するUnityとSDKでワールドを制作する。必要な実素材が無い場合は制作を未完了とする。標準形状だけの仮シーンや仮のテクスチャで完成工程を代替しない。
5. Build & Testで歩行・衝突判定・視認性・負荷と、実素材が意図どおり表示されることを実機で確認する。未実施なら合格にしない。
6. 認可済みのVRChatアカウントで公開し、**実際の公開ワールドURL**を制作先の正本に記録する。URL未確認なら公開済みとしない。

Workflow候補の収集やファイルの形式検査は、作品の完成を保証しません。8領域それぞれで制作先の条件を満たし、公開先のURLと公開状態を確認します。

## 検証と障害の記録

静的テスト、GPU実測、作品統合、公開確認を混同しません。障害は日時、操作、版、対象、エラー、再現手順、確認した結果を記録します。実行できなかった検証は「未実施」と明記します。大容量メディアや認証情報はGitへ保存しません。
