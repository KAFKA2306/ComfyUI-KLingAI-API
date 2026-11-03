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

公開元と検索語は `config/registry.json` に登録する。新しい取得先を追加するときも、同ファイルを更新する。

## Workflowの公開元

公式の入口には[Comfy-Orgのテンプレート](https://github.com/Comfy-Org/workflow_templates)、[公開Workflow](https://github.com/Comfy-Org/workflows)、[ComfyUIの作例](https://github.com/comfyanonymous/ComfyUI_examples)がある。[Comfy-Orgのリポジトリ一覧](https://github.com/orgs/Comfy-Org/repositories)では関連する公開元を確認できる。

コミュニティのWorkflowは、設定したリポジトリと検索語で探索する。取得したファイルには原典URL、固定コミット、パス、Blob SHAを記録する。APIエラーや配布元の削除は、その事実を記録し、候補の品質評価と混同しない。

## モデル情報と参考サイト

Hugging FaceとCivitaiのモデル情報は収集台帳の `feeds` に記録する。参考サイトは [`config/registry.json`](../../config/registry.json) の `reference_sources` で管理する。

権利情報は `rights` に対象・ライセンス・一次証拠URLとして登録する。必須項目は [`gwp.ledger`](../../src/gwp/ledger.py) に定義する。
