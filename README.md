# ComfyUI Workflow 出典カタログ

公開Workflowを継続的に発見し、出典と変更履歴を保ったまま制作に利用するためのリポジトリです。収集、実行、品質確認、公開は異なる工程として扱います。

## 守り続ける原則

1. **出典と改訂を記録する。** 元リポジトリ、ファイルの場所、コミット、ファイルのハッシュを保持する。元ファイルが変わっても過去の参照を消さない。
2. **候補を独断で選別しない。** 未分類、未検証、取得失敗、公開終了の情報も状態を明示して残す。検索のための分類を品質評価や順位にすり替えない。
3. **事実と推測を分ける。** ファイル名、人気、ノード名、モデル名だけで動作、品質、互換性を断定しない。実行可能性は実際の環境で別に検証する。
4. **第三者のプログラムを自動実行しない。** 出典収集ではWorkflow、モデル、Custom Node、外部コードを自動でインストール・実行しない。
5. **権利の確認を省略しない。** 公開されていること、利用可能なこと、再配布できること、商用利用できることは同じではない。未確認は未確認と記録する。
6. **生成物の完成を偽らない。** 画像・音声・3D素材の生成成功は、Unityへの取り込み、VRChatでの動作検証、製品化、公開の証拠にならない。それぞれの完成条件を確認する。
7. **復元・追試できる情報を残す。** 通信失敗を候補ゼロと扱わず、入力・出典・改訂・出力の関係を追跡できるようにする。外部成果物は必要なく複製しない。
8. **文書は日本語の確かな原則に限る。** 日付で古くなる順位や作業日誌、推測を含む説明、重複した設計書は置かない。具体的な動作と制約はコードおよびテストで検証する。
9. **Pythonは必ずuvで実行する。** 環境構築、依存関係管理、スクリプト、テスト、GitHub Actionsに[uv](https://docs.astral.sh/uv/getting-started/installation/)を使い、直接の`python`実行や`pip`・`poetry`での環境管理は行わない。

## 環境構築と実行

Python 3.11系を`uv`で管理し、`uv.lock`をGitで管理します。モデルや第三者のWorkflowはこの操作では実行しません。

```sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term VRChat
uv run --locked python -m gwp.discovery export > workflows.csv
```
