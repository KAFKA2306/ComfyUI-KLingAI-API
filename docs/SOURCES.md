# 収集元と確認範囲

ここは公開Workflowの**出典を保持する収集台帳**であり、ComfyUI本体、Custom Nodeの導入ツール、VRChat対応作品の完成保証を置き換えません。

## 主な公開元

- 公式テンプレート・Blueprint：https://github.com/Comfy-Org/workflow_templates
- 公式Workflow：https://github.com/Comfy-Org/workflows
- 公式の実例：https://github.com/comfyanonymous/ComfyUI_examples
- 公式組織：https://github.com/orgs/Comfy-Org/repositories
- 動画制作例：https://github.com/kijai/ComfyUI-WanVideoWrapper
- コミュニティWorkflow：https://github.com/pjecuacion/comfyui_workflows
- 3D制作例：https://github.com/Alex92908/image-to-3d-comfyui
- 音声制作例：https://github.com/skyiron/ComfyUI-TTS-Audio-Suite
- 音声制作例：https://github.com/wildminder/ComfyUI-Chatterbox
- VRChat関連例：https://github.com/AEmotionStudio/ComfyUI-VRChat-Assets

そのほかの公開元は`config/workflow_sources.json`を参照してください。RunningHub、Reddit、Comfy Registry、Civitai、OpenArt、ComfyWorkflowsなどは確認できた取得方法・利用条件の範囲で扱います。参照先を記録しただけのサイトからWorkflow本体を収集したとは主張しません。

## 保存先

- `data/workflow_registry.json`：出典付きの収集台帳と変更履歴
- `registry/official.json`、`registry/community.json`：旧方式の公開元
- `registry/practices.json`：旧方式のファイル候補
- `registry/insights.json`：静的検査の記録
- `catalog/all-workflows.csv`：未分類も含む全候補
- `catalog/by-usecase.json`：重複所属を認める用途別索引
- `catalog/index.md`：閲覧用一覧

用途タグは検索の手掛かりにすぎず、実行可否、作品の完成品質、販売許可を証明しません。VRChat制作にはBlender、Unity、VRChat SDK、最適化や公開前の確認も必要です。

```sh
python scripts/practice_registry.py
python scripts/audit_practices.py
python scripts/build_catalog.py
```

未対応範囲と注意事項は[収集台帳の仕様](workflow-first-registry.md)を参照してください。
