---
id: knowledge
title: ナレッジとメタデータの管理
type: policy
status: active
updated: 2026-11-03
tags: [ナレッジ基盤, メタデータ, タグ, 出典, 改訂履歴]
---

# ナレッジとメタデータの管理

## 何を保存するか

公開Workflow・Subgraph・Blueprint・モデル参照を**捨てずに見つける**ための出典台帳と、実際に使った結果を**再現できるようにする**ための制作記録を分離します。独自スコア、スター数、主観的な品質順位による収集対象の足切りはしません。

候補の保存と、実際に使ってよいかの判断は別工程です。動作可否や権利を未確認のものは「未確認」として残します。

## 文書の必須メタデータ

すべての `*.md` は先頭にYAMLフロントマターを持ち、次の5項目以上を必須とします。

| 項目 | 意味 |
| --- | --- |
| `id` | 重複しない安定ID |
| `title` | 日本語の文書名（固有名詞は例外） |
| `type` | `entrypoint` / `strategy` / `specification` / `policy` / `operations` |
| `status` | `active` または `archived` |
| `updated` | 最終確認日、YYYY-MM-DD |
| `tags` | 用途や検索軸を示す空でない日本語タグの配列 |

例：

~~~yaml
---
id: article-id
title: 文書の目的
type: specification
status: active
updated: 2026-11-03
tags: [Workflow, 出典, VRChat]
---
~~~

本文は日本語を基本とし、リンクは原則として現在存在する相対パス・一次資料を指します。重複する説明は一つの正本へ集約し、旧説明はGit履歴に残します。年月だけで陳腐化する技術ランキングを永久ルールと混在させません。

## Workflow候補のメタデータ

台帳 `data/workflow_registry.json` が保持する主な情報：

- 識別子、公開元リポジトリ、原典URL、パス、コミットSHA、Blob SHA、観測時点
- 改訂履歴、形式、静的検査の状態、参照されるノードとモデル（取得できた場合）
- 公開元の失敗、未解析、未分類、取得制限も状態として残す
- 用途分類は `config/workflow_sources.json` の検索語による**非排他的タグ**。機能・品質の保証ではない

制作に採用した際は、別途、作者と利用条件、モデル／Custom Nodeの版、実行環境、入力、出力ハッシュ、所要時間、ピークVRAM、失敗記録、制作先、公開証拠を結び付けます。

## 必須の状態区分

| 状態 | 意味 |
| --- | --- |
| 発見 | 公開ファイルまたはURLを確認した |
| 静的確認 | 形式やノード参照を読めた |
| 実行確認 | 指定環境で実行ログと出力を確認した |
| 作品統合 | 制作先で形式・見た目・性能等を確認した |
| 公開確認 | 実際の公開先URLと公開状態を確認した |

「発見」を「実行済み」と呼ばず、「素材生成」を「完成品公開」と呼びません。状態の詳細は実装が出す `inspection` や `state` と混同せず、対応関係を明記します。

## 原典の入口

- 公式テンプレート：[Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates)
- 公式Workflow：[Comfy-Org/workflows](https://github.com/Comfy-Org/workflows)
- 公式の実例：[ComfyUI_examples](https://github.com/comfyanonymous/ComfyUI_examples)
- 公式組織：[Comfy-Org](https://github.com/orgs/Comfy-Org/repositories)
- 公開動画例：[WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper)
- コミュニティ例：[comfyui_workflows](https://github.com/pjecuacion/comfyui_workflows)
- 3D例：[image-to-3d-comfyui](https://github.com/Alex92908/image-to-3d-comfyui)
- 音声例：[ComfyUI-TTS-Audio-Suite](https://github.com/skyiron/ComfyUI-TTS-Audio-Suite)
- VRChat関連例：[ComfyUI-VRChat-Assets](https://github.com/AEmotionStudio/ComfyUI-VRChat-Assets)

その他の正式な取得対象、検索語、API／参照のみの区別は `config/workflow_sources.json` が正本です。CivitaiやHugging Faceのモデル情報と、実際に取得できたWorkflowを混同しません。GitHub検索APIの件数制限や取得失敗を隠しません。

## 変更の扱い

1. 原典の版・ハッシュを記録して、以前の履歴を消さない。
2. 更新を発見しても、自動で稼働中の制作環境へ採用しない。
3. 互換性・ライセンス・実行結果を別々に確認する。
4. 制作先の目的と完成証拠を紐付け、他領域への再利用に役立てる。
5. 文書を変えるときは必須メタデータ、日本語、リンク先、現行のコマンド・パスを確認する。
