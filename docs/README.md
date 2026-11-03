---
id: "docs-index"
title: "設計・ナレッジ索引"
kind: "index"
status: "active"
updated: "2026-11-03"
tags: ["索引","設計","ナレッジ"]
related: ["docs/design/system.md","docs/knowledge/registry.md"]
sources: []
---

# 設計書とナレッジ

`docs/` は設計書とナレッジの2分類に限定します。コード・テストと `data/workflow_registry.json` が動作・収集結果の正本です。Markdownには判断と確認方法だけを残します。

## 設計書

- [全体設計](design/system.md)：収集から制作までの責任分担
- [制作工程への接続](design/production.md)：API Workflowの実行・回収・受け渡し
- [VRChat小型カフェ](design/vrchat-cafe.md)：Unityでの制作と公開の判定

## ナレッジ

- [Workflow台帳と用語](knowledge/registry.md)：データ構造・検索と検証状態
- [一次資料と情報源](knowledge/sources.md)：出典の扱いとライセンス

## 文書の規則

全て日本語で記述し、先頭にYAML Front Matterを付けます。`id`、`title`、`kind`、`status`、`updated`、`tags`、`related`、`sources` が必須です。値はJSON互換のYAML形式にします。

`kind` は `index`、`design`、`knowledge`。`status` は `active`、`reference`。`tags` は重複のない2件以上の検索語であり、採用可否の判定には使いません。`related` は存在するリポジトリ内パス、`sources` は一次資料のHTTPS URLです。

日誌・古いADR・重複台帳は残さず、履歴はGitでたどります。`uv run --locked python scripts/validate_docs.py` でメタデータとリンクを検証します。
