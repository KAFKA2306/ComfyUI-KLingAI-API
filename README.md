# ComfyUI Workflows Factory

公式・コミュニティが公開するWorkflowを継続的に発見し、出典・改訂履歴を保ったまま制作業務に取り込む共通基盤です。

## 開発環境（uv必須）

このリポジトリのPython環境作成、依存関係の解決、スクリプト実行、テスト、GitHub Actionsには**必ず[uv](https://docs.astral.sh/uv/getting-started/installation/)を使用**します。`pip`や`poetry`による環境管理、`python`の直接実行は行いません。`uv.lock`をGitで管理し、実行時は`--locked`を指定します。

Python 3.11系の環境を`uv`で構築します。

~~~sh
uv sync --locked
~~~

## 収集・検索

- [用途別一覧](catalog/index.md)、[全候補CSV](catalog/all-workflows.csv)、[JSON](catalog/by-usecase.json)
- [収集対象](docs/SOURCES.md)、[出典を保つ管理方針](docs/workflow-first-registry.md)
- [自動収集](.github/workflows/workflow-discovery.yml)：6時間ごと、および手動で実行

公開Workflowに独自スコアや順位・足切りを設けません。未確認・未実行のものも出典付きで保存します。

## 業務への接続

対象は既存の image2outfit、vrmineのVRChat小型カフェ、3Dモデルの複数視点画像準備です。入力画像・テクスチャなどの生成工程をComfyUIへ移し、Blender・Unity・公開判定は既存の責任範囲に残します。詳しくは [制作工程への接続](docs/production-handoff.md)。

~~~sh
uv run --locked python scripts/production_job.py targets
uv run --locked python scripts/production_job.py plan --target vrmine-cafe --workflow workflow-api.json
uv run --locked python scripts/production_job.py submit --target vrmine-cafe --workflow workflow-api.json --receipt .artifacts/receipt.json
uv run --locked python scripts/production_job.py collect --receipt .artifacts/receipt.json --output-root .artifacts/output
~~~

実行先はローカルComfyUIのみ。GPUや商用利用の検証はCIでは実施しません。生成物はハッシュ付きで回収しますが、製品完成やVRChat公開済みとは判定しません。

## 開発・検証

~~~sh
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.discovery stats
uv run --locked python scripts/build_catalog.py
~~~

Python 3.11以上、外部ランタイム依存ライブラリは不要です。新規端末では先に `uv sync --locked` を実行してください。モデル・動画・音声・画像・秘密情報はGitにコミットしません。

生成結果を既存制作repoの作業領域に検証付きで渡す場合:

~~~sh
uv run --locked python scripts/production_job.py handoff --manifest .artifacts/output/vrmine-cafe/<promptId>/manifest.json --project-root ../vrmine
~~~

移管後も品質判定は未完了です。
