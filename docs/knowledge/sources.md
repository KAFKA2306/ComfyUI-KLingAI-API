---
id: "knowledge-sources"
title: "一次資料と情報源"
kind: "knowledge"
status: "active"
updated: "2026-11-03"
tags: ["出典","一次資料","ComfyUI","ライセンス"]
related: ["config/registry.json","docs/knowledge/registry.md"]
sources: ["https://github.com/Comfy-Org/workflow_templates","https://github.com/comfyanonymous/ComfyUI_examples"]
---

# 一次資料と情報源

公開元と検索条件は `config/registry.json` で管理する。対象を追加・変更する際は設定台帳を更新し、文書には情報源の種類と確認方法を記す。

## Workflowの公開元

公式・開発元の公開先には[Comfy-Orgのテンプレート](https://github.com/Comfy-Org/workflow_templates)、[公開Workflow](https://github.com/Comfy-Org/workflows)、[ComfyUIの作例](https://github.com/comfyanonymous/ComfyUI_examples)がある。関連リポジトリは[Comfy-Orgの一覧](https://github.com/orgs/Comfy-Org/repositories)から調べられる。

コミュニティのWorkflowは、設定したリポジトリと検索語で探す。取得したファイルには、原典URL、コミットSHA、ファイルパス、Blob SHAを記録する。取得に失敗した場合は失敗として記録し、品質の評価には使わない。

## モデル情報と参考サイト

Hugging FaceとCivitaiのAPIではモデル情報を取得する。RunningHub、Reddit、Comfy Registry、OpenArtなどは、Workflowファイルを取得するAPIを確認できていない場合、参考先として記録する。

Workflowを採用する際は、原典にある依存モデルやCustom Node、生成素材の利用条件を確認する。GitHubのスター数やIssueの件数は、個別Workflowの動作実績とは区別する。
