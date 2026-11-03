# ComfyUI Workflow 出典カタログ

公開Workflowを継続的に発見し、出典をたどれる形で記録するリポジトリです。独自の点数や順位で他者の制作物を選別しません。

## 維持する原則

1. **出典を残す。** 元リポジトリ、ファイルの場所、参照時点のコミット、ファイルのハッシュを保存し、改訂履歴を消さない。
2. **見つけたものを勝手に捨てない。** 未分類、未確認、取得失敗、公開終了をそれぞれ明示して残す。検索用の分類は品質評価ではない。
3. **確認した事実だけを述べる。** ファイル名やノード名から動作・品質・互換性を断定しない。人気やスター数を品質の証明にしない。
4. **他者のコードを自動実行しない。** 収集器は公開情報だけを読む。Workflow、モデル、Custom Node、依存プログラムを自動でインストール・実行しない。
5. **利用条件を分離する。** 発見、動作確認、再配布、商用利用は別の確認事項。未検証のライセンスは未確認と記録する。
6. **追試できる記録にする。** 出典と改訂を追えるようにし、通信失敗を「候補ゼロ」と解釈しない。外部の成果物そのものは再配布しない。
7. **説明は日本語、内容は長期間有効な事実だけにする。** 古くなる順位表、作業日誌、重複した設計文書を増やさない。実装とテストを仕様の正本にする。

## 操作

Python 3.11以降の標準ライブラリだけで動作します。GPUや有料APIは不要です。

```sh
python -m unittest discover -s tests -v
PYTHONPATH=src python -m gwp.discovery sync
PYTHONPATH=src python -m gwp.discovery stats
PYTHONPATH=src python -m gwp.discovery search --term VRChat
PYTHONPATH=src python -m gwp.discovery export > workflows.csv
```

設定は `config/workflow_sources.json`、データの正本は `data/workflow_registry.json` です。検索用CSVは必要なときに生成し、同じ記録を複数箇所に保存しません。

## VRChatカフェ制作で守ること

制作物は `projects/vrchat-cafe/` に置きます。Unityの編集スクリプトは `unity/Assets/Editor/GWPCafeBuilder.cs`、出典の取得・GLBの確認は `scripts/cafe_pipeline.py`、Blenderでの変換は `scripts/blender_cafe_asset.py` です。

- VRChat Creator CompanionでWorldsプロジェクトを作り、そのプロジェクトが指定するUnityとSDKを使う。
- シーン生成後にVRChat SDKのBuild & Testを実行し、衝突判定・表示・動作を実際に確認する。
- Workflowの発見、GLBの形式検査、Unityへの取り込み、ワールド公開は、それぞれ別の完了条件として扱う。
- 公開済みと記録するのは、実際のアップロードとワールドURLを確認した後だけにする。
- 外部モデルや生成素材の利用条件は、公開前に個別に確認する。## 長期成果

世界中のWorkflowを継続的に利用し、**VRChatワールド、アバター・衣装、BOOTH商品、YouTube・Shorts、Podcast・音声、映画・アニメーション、3Dモデル、ゲーム制作を並列に進め、完成作品を公開する**ことを目指します。

VRChatの小さなカフェは実証対象の一つであり、他分野の開始条件ではありません。収集や一覧生成と作品の完成を混同せず、実装済みの工程と未実装の工程を区別します。詳しくは[長期成果と運用原則](docs/vision.md)。


