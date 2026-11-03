---
id: "design-durable-registry"
title: "台帳の保全・復旧・制作履歴の設計"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["台帳", "差分収集", "保全", "復旧", "制作履歴", "公開証拠"]
related: ["src/gwp/state.py", "src/gwp/ledger.py", "src/gwp/discovery.py", "scripts/catalog_sync.sh", ".github/workflows/collect.yml"]
sources: ["https://docs.github.com/en/rest/git/trees", "https://docs.github.com/en/rest/search/search", "https://docs.github.com/en/actions/reference/dependency-caching-reference"]
---

# 台帳の保全・復旧・制作履歴

## 正本とバックアップ

制作目標、収集条件、制作案件は main ブランチの config/registry.json を設定の正本とする。収集結果と制作履歴は catalog ブランチの data/workflow_registry.json と同名の .sha256 ファイルを正本とする。GitHub Actionsのキャッシュと一時成果物は正本ではない。

GitHub以外のUSB、NAS、クラウドフォルダにも定期的に別媒体バックアップを保存する。生成メディアとモデル本体はGitへ入れず、SHA-256、バイト数、保管場所と出典を台帳へ保存する。認証情報は台帳へ記録しない。

## PC交換・破損・復元

新PCはGitをcloneし、catalogをfetchして台帳とSHA-256ファイルを取得する。gwp.state verifyで整合性を検査する。別媒体から復元するときはgwp.state restoreを使う。破損した本体は隔離し、成功した過去版を戻す。原典の候補数が減った場合は前版とのID差分を出し、削除・収集不足・破損を区別する。単に件数だけを再生成して一致したとは主張しない。

## 同時更新・履歴・スキーマ

収集は最新台帳から別の候補ファイルを生成する。保存では同期書き込み、原子的な置換、正常版の退避を行う。Gitへpushが競合した場合は最新の正本を取得し、ID・改訂・別原典ごとに統合して再試行する。旧スキーマは既存IDを保持したまま移行する。追記と訂正は区別し、訂正には変更前後の値、SHA-256、日時、根拠URLを残す。

## 発見・検索・改訂

完全な原典ファイル一覧を取得できた場合にだけファイルの削除を認定する。APIの失敗や途中停止を削除扱いにしない。GitHub検索の1,000件制限は作成日期間の二分で回避し、未走査ページを記録する。分割しても上限を超える期間は未網羅と記録する。PNGに埋め込まれたWorkflowは静的に抽出し、探索中に実行しない。

同一内容のWorkflowも別作者の出典を別IDに保ち、Blob SHAから関連づける。既存Workflowの改訂、作者変更、リポジトリ移転、配布停止では出典リンクと過去版を保存する。検索語、同義語、8領域のタグは重複を許し、人気や独自採点による候補の排除はしない。

## 採用・制作・公開

adoptionsにはWorkflow ID、固定コミット、Blob SHA、適用する制作案件・領域を記録する。modelsとdependenciesには配布URL、固定版、ハッシュ、Custom Nodeと利用条件の出典を記録する。environmentsにはComfyUI、GPU、VRAM、ライブラリと実測条件を記録する。第三者の未確認コードは自動導入・実行しない。

jobsにはWorkflow、入力、Seed、client_id、prompt_id、環境、ジョブ状態を結びつける。送信が不確実ならsubmission_unknownとし、サーバー側の実行状態確認前に再送しない。生成物は個々のSHA-256で確認し、部分成功を成功としない。

8領域の制作はprojectsとgwp.creativeで構成し、素材・シーン・ショット・音声・編集・配布物の依存関係を扱う。assetsに素材のハッシュ・入力と保管先、rightsに版別の権利根拠、knowledgeに再利用できる確認済みの知識を登録する。作品に必要な素材が生成されない場合、仮の単色形状などを完成品の代わりにしない。

publicationsで公開確認を記録するには、作品のURL、公開先、確認日時、確認方法、一次証拠URLを要求する。通信断の状態はupload_unknownとして二重投稿を防ぐ。非公開化や新版公開は旧版を書き換えずに変更を記録する。権利上の指摘はgwp.ledger lineageで素材から影響作品・公開先へ逆引きする。

## 運用コマンド

~~~sh
uv sync --locked
git fetch origin catalog
git show origin/catalog:data/workflow_registry.json > .cache/restored.json
git show origin/catalog:data/workflow_registry.json.sha256 > .cache/restored.json.sha256
uv run --locked python -m gwp.state verify --catalog .cache/restored.json
uv run --locked python -m gwp.state backup --catalog .cache/restored.json --output /別媒体/backup
uv run --locked python -m gwp.ledger query --catalog .cache/restored.json --section artifacts --term VRChat
~~~

収集設定の変更はgwp.registry validateで検査する。失敗した処理や実施していないGPU・品質・公開検証を成功済みとして記録しない。
