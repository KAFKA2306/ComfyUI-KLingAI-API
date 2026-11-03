# ComfyUIで既存制作工程を置き換える範囲

## 対象

既存の制作リポジトリは、それぞれの完成条件を保ちます。

| 制作先 | ComfyUIで生成する候補 | ComfyUIでは置き換えない工程 |
|---|---|---|
| KAFKA2306/image2outfit | 衣装の参考画像、質感画像、テクスチャ案 | 型紙・縫製・Blender・スキニング・Unity・品質検証 |
| KAFKA2306/vrmine | VRChat小型カフェの背景、壁と床のテクスチャ、小物の参考画像 | build-retro-cafe.py、world_build_factory.py、Unity・VRChat実行確認 |
| Tripo系3D工程 | 正面・背面・左右などの参考画像候補 | Tripo入力検証、メッシュ・リギング・VRM・アバター適合 |

ComfyUI生成の完了を製品完成に置き換えません。最終判定は各制作リポジトリの契約で行います。

## ローカルでの手順

1. 公式やコミュニティの配布元と更新履歴をカタログで確認する。未検証Workflowを自動実行しない。
2. 必要モデルとCustom Nodeを自分のComfyUIで確認する。商用利用・再配布可否は配布元のライセンスで確認する。
3. ComfyUIのFileメニューから Export Workflow (API) を選び、API形式JSONを保存する。普通のSave形式は受け付けない。
4. `uv sync --locked` で環境を用意し、以下の `uv run --locked` コマンドで準備・生成・出力回収を行う。Pythonの直接実行は禁止する。

~~~sh
uv run --locked python scripts/production_job.py targets
uv run --locked python scripts/production_job.py plan --target vrmine-cafe --workflow workflow-api.json
uv run --locked python scripts/production_job.py submit --target vrmine-cafe --workflow workflow-api.json --receipt .artifacts/receipt.json
uv run --locked python scripts/production_job.py collect --receipt .artifacts/receipt.json --output-root .artifacts/output
~~~

入力文字列などを変更するときは、同じnode IDに対して変更する入力だけを示したJSONを --patch で渡します。例: {"6":{"text":"warm cafe wall texture"}}。対象IDと入力名は選んだWorkflowを調べて指定してください。結線の差し替えは受け付けません。

submitは127.0.0.1またはlocalhostのComfyUIへ実際にジョブを投入します。collectはComfyUIがsuccess/completeと報告した場合だけファイルを保存し、SHA-256付きmanifestを作ります。画像・音声・一般的な動画ファイルに対応します。独自3Dノードが出力するメッシュなど未知の形式の回収は未対応です。

生成物は GENERATED_UNVERIFIED と記録します。画像を既存プロジェクトへ取り込む際は必ず、そのプロジェクトの正規入力と監査工程を通してください。上書き、完成状態への自動昇格、BOOTH投稿、VRChatアップロードをこのCLIは実行しません。

## 置換しない理由

衣装生成では元画像の観測と推測の区別、正しい型紙、貫通、ボーン、見た目の審査が重要です。VRChatワールドではUnity内の配置、スクリプト、SDKの検証、実クライアントのテストが必要です。ComfyUIが素材を生成しても、これらの証拠を代替しません。

## 自動更新と実行の境界

公開Workflowの収集は既存のworkflow-discovery.ymlが6時間ごとに行います。収集後も、未知の第三者コードを自動的に実行したり、新モデルを無断でインストールしたりはしません。採用する実際のWorkflowにはローカル実行環境、必要モデルと版の固定が必要です。GitHub ActionsではGPU、Blender、Unity実機を動かしたとは主張しません。

## 仕様の一次資料

- https://github.com/Comfy-Org/workflow_templates
- https://github.com/Comfy-Org/docs/blob/main/development/api-development/workflow-api-format.mdx
- https://docs.comfygit.org/

## 自動受け渡し

collect後に handoff コマンドで既存repoへ生成候補を自動コピーします。例えば vrmine の場合:

~~~sh
uv run --locked python scripts/production_job.py handoff --manifest .artifacts/output/vrmine-cafe/<promptId>/manifest.json --project-root ../vrmine
~~~

image2outfit と tripo-3d は --project-root ../image2outfit を使用します。ファイルのSHA-256を再検証し、各repoの非追跡作業領域（.image2outfit/comfyui または .artifacts/comfyui）へコピーします。生成候補は STAGED_UNREVIEWED として保存し、既存製品の正本・品質判定を変更しません。
