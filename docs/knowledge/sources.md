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

取得対象の一覧と検索条件は `config/registry.json` で管理する。公開元を追加・変更する場合は、その設定を更新する。Markdownに同じ一覧を複製しない。

## Workflowの公開元

公式の入口には[Comfy-Orgのテンプレート](https://github.com/Comfy-Org/workflow_templates)、[公開Workflow](https://github.com/Comfy-Org/workflows)、[ComfyUIの作例](https://github.com/comfyanonymous/ComfyUI_examples)がある。[Comfy-Orgのリポジトリ一覧](https://github.com/orgs/Comfy-Org/repositories)では関連する公開元を確認できる。

コミュニティのWorkflowは、設定したリポジトリと検索語から探す。取得したファイルには原典URL、固定コミット、パス、Blob SHAを結び付ける。更新や削除があっても、取得できなかった事実を候補の品質評価へ置き換えない。

## モデル情報と参考サイト

Hugging FaceとCivitaiのAPIから得るのはモデルのメタデータであり、Workflowファイルを取得したことにはならない。RunningHub、Reddit、Comfy Registry、OpenArtなどは、確認済みの取得APIがない場合は参考先として扱う。

Workflowを見つけても、実行可能性、再配布の許可、商用利用の許可までは確定しない。採用時にはWorkflow、依存モデル、Custom Node、生成素材について、原典の利用条件をそれぞれ調べる。GitHubのスター数やIssueの存在だけで個別Workflowの品質を断定しない。
