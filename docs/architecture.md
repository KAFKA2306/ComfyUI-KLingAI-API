---
id: architecture
title: アーキテクチャとデータの正本
type: specification
status: active
updated: 2026-11-03
tags: [アーキテクチャ, データの正本, 出典追跡, Workflow, 自動化]
---

# アーキテクチャとデータの正本

## 責務と流れ

~~~text
公開元（公式・コミュニティ）
    ↓ 発見・記録（第三者コードは実行しない）
出典台帳：data/workflow_registry.json
    ↓ 版と用途の検索（候補を排除しない）
制作要求：8領域それぞれ独立
    ↓ Workflow・依存関係・利用条件の確認
ローカルComfyUIで素材生成（対応先のみ実装）
    ↓ 入出力のハッシュ・実行記録
Blender / Unity / 動画・音声編集 / 配布先の固有工程
    ↓ 各領域固有の品質・権利・公開条件
作品の完成と公開URLを記録
~~~

この図は**制作案件ごとの工程順**です。8領域を順番に処理する図ではありません。各領域の案件は相互に待たず並列実行できます。

## 構成要素と正本

| 責務 | 正本・実装 | 用途 |
| --- | --- | --- |
| 収集元と用途検索語 | `config/workflow_sources.json` | 公開元、取得方法、検索用分類 |
| Workflow候補と版 | `data/workflow_registry.json` | 出典付き候補の機械可読な正本 |
| 収集と検索 | `src/gwp/discovery.py` | GitHub等の公開情報を取得し検索・CSV出力 |
| 定期更新 | `.github/workflows/collect.yml` | 6時間ごとの収集ジョブと検証 |
| 生成可能な制作先 | `config/production_targets.json` | 受け渡し対象と完成判定の責任先 |
| 生成・受け渡し | `src/gwp/production.py`, `src/gwp/production_job.py` | ローカルComfyUIへ投入、回収、ハッシュ確認、限定的な転送 |
| VRChatカフェ | `projects/vrchat-cafe/workflows.json`, `projects/vrchat-cafe/publication.json` | 候補と公開確認状態 |
| カフェ制作補助 | `projects/vrchat-cafe/cafe_pipeline.py`, `projects/vrchat-cafe/blender_cafe_asset.py`, `projects/vrchat-cafe/GWPCafeBuilder.cs` | 出典取得、GLB形式確認、シーン生成の補助 |

**生成された索引・作業ログを別の正本として増殖させない。** CSVは `uv run --locked python -m gwp.discovery export` で都度再生成します。Markdownは設計・手順の正本であり、収集データそのものの複製ではありません。

## 境界と交換可能性

1. 作品の制作要求を、ComfyUI固有のノードIDから分離する。
2. 原典の識別子は公開元、固定コミット、パス、Blob SHA、改訂履歴を使う。
3. 入力形式を確認してから、固定版のWorkflowと必要モデル・Custom Nodeを採用する。
4. 収集と実行を分離する。未知の外部コードを無条件にインストール・実行しない。
5. 結果を版、入力、環境、出力ハッシュ、測定値と一緒に保存する。未測定値は空欄とする。
6. 品質判定と公開は制作先の責務とする。画像が生成できてもVRChatワールド完成にはならない。
7. ComfyUIやモデルを交換しても、出典、制作要求、完成判定、公開実績は失わない。


## 運用を壊さないためのルール

- 大容量メディア、モデル、認証情報、機密情報はGitへ入れない。
- 既存データの正本は上表に一本化する。別の台帳を無断で作らない。
- 権利・互換性・動作を未確認なら明示する。GitHub Issueの存在だけで個別Workflowの品質を断定しない。
- 変更は差分とテストを確認し、既存の制作先が持つ完成判定を自動で上書きしない。
