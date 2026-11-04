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

## 会話音声のWorkflow構成

[Chatterbox Dialog TTSの公式テンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio-chatterbox_tts_dialog.json)では、2つの`LoadAudio`で話者の参照音声を読み込み、片方を`AudioCrop`で切り出してから`FL_ChatterboxDialogTTS`へ入力する。会話文をノード内で指定し、生成した`dialog_audio`を`SaveAudioMP3`へ渡す。参照音声は`AUDIO`、生成結果も`AUDIO`であり、保存先はMP3形式である。

主な再利用先はPodcast・音声。YouTube・Shorts、映画・アニメーション、ゲーム制作、VRChatワールドでは台詞音声の制作工程として利用を検討できる。アバター・衣装、BOOTH商品、3Dモデルへの直接の適用は、この原典だけでは確認できない。類似する単一話者の音声合成と異なり、複数話者の参照音声と会話文を1つのノードに入力する構造を持つ。

`FL_ChatterboxDialogTTS`の配布元、必要なカスタムノードの版、モデルの取得先、VRAM、各モデルと参照音声のライセンス、実機動作、商用利用条件は、このJSONだけでは確定できない。利用前にそれぞれの一次資料と実機で確認する。これらの条件はWorkflowの自動順位付けに加点・減点しない。
