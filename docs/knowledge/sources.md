---
id: "knowledge-sources"
title: "一次資料と情報源"
kind: "knowledge"
status: "active"
updated: "2026-11-04"
tags: ["出典","一次資料","ComfyUI","ライセンス"]
related: ["config/registry.json","docs/knowledge/registry.md"]
sources: ["https://github.com/Comfy-Org/workflow_templates","https://github.com/comfyanonymous/ComfyUI_examples"]
---

# 一次資料と情報源

Workflowの取得対象と検索条件は `config/registry.json` に登録します。取得元を追加・変更する場合は設定を更新し、原典一覧をMarkdownへ重複して保存しません。

## Workflowの公開元

公式の公開元は[Comfy-Orgのテンプレート](https://github.com/Comfy-Org/workflow_templates)、[公開Workflow](https://github.com/Comfy-Org/workflows)、[ComfyUIの作例](https://github.com/comfyanonymous/ComfyUI_examples)です。[Comfy-Orgの公開リポジトリ](https://github.com/orgs/Comfy-Org/repositories)から関連する公開元も確認できます。

コミュニティの候補は登録したリポジトリと検索語で探します。取得したファイルに原典URL、パス、固定コミット、Blob SHAを記録します。取得失敗やファイル削除は候補の品質とは別の情報として扱います。

## モデル情報と参考サイト

Hugging FaceとCivitaiから取得するモデル情報は、Workflow本体の取得とは区別します。RunningHub、Reddit、Comfy Registry、OpenArtなどは、取得APIを確認できていない場合、参照先として登録します。

制作に採用する際は、Workflow、モデル、Custom Node、生成素材それぞれの利用条件を原典で調べます。再配布と商用利用の条件は異なるため、利用先ごとに確認し、出典URLを保存します。
