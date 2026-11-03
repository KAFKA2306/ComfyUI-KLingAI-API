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

公開元と検索条件は`config/registry.json`に置く。情報源を追加・変更するときは設定を更新し、Markdownに同じ一覧を写さない。

## Workflowの公開元

公式の参照先は[Comfy-Orgのテンプレート](https://github.com/Comfy-Org/workflow_templates)、[公開Workflow](https://github.com/Comfy-Org/workflows)、[ComfyUIの作例](https://github.com/comfyanonymous/ComfyUI_examples)。関連するリポジトリは[Comfy-Orgの一覧](https://github.com/orgs/Comfy-Org/repositories)からたどれる。

コミュニティの候補は設定したリポジトリと検索語で探し、原典URL・固定コミット・パス・Blob SHAを記録する。取得できなかった場合は原因を残し、品質の判定に使わない。

## モデル情報と参考サイト

Hugging FaceとCivitaiのAPIから得るのはモデルのメタデータであり、Workflow本体ではない。RunningHub、Reddit、Comfy Registry、OpenArtは、取得APIを確認できるまでは参考先として記録する。

採用するときはWorkflow、依存モデル、Custom Node、生成素材の利用条件を原典ごとに確かめる。公開されている事実だけでは、実行可否や再配布・商用利用の許可は分からない。GitHubのスター数やIssue数も品質の証明にはならない。
