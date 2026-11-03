---
id: "docs-index"
title: "設計書とナレッジの索引"
kind: "index"
status: "active"
updated: "2026-11-04"
tags: ["索引","設計","ナレッジ"]
related: ["docs/design/system.md","docs/knowledge/registry.md"]
sources: []
---

# 設計書とナレッジ

`docs/` は、仕組みと手順を定める設計書、出典と用語を整理するナレッジに分ける。8領域の目標、収集条件、Workflow候補、制作案件の設定は `config/registry.json` で管理する。収集結果と制作履歴は `catalog` ブランチの `data/workflow_registry.json` に保存する。文書には設定や履歴を複製せず、各ファイルの役割と参照先を書く。

## 設計書

- [全体設計](design/system.md)：公開Workflowの収集から制作までの処理と責任分担
- [台帳の保全・復旧](design/durability.md)：永続保存、別PCからの復旧、競合統合、制作と公開の出典管理
- [制作工程への接続](design/production.md)：ComfyUIへの投入、出力回収、制作先への受け渡し
- [作品構成と演出](design/creative.md)：制作単位の依存関係と変更の影響

## ナレッジ

- [Workflow台帳と用語](knowledge/registry.md)：収集データの構造、状態、検索方法
- [一次資料と情報源](knowledge/sources.md)：公開元の区分、原典と利用条件の確認

## 文書の規則

各Markdownファイルの先頭に、`id`、`title`、`kind`、`status`、`updated`、`tags`、`related`、`sources` を含むYAMLフロントマターを付ける。値はJSON互換の形式で記述する。

`kind` には `index`、`design`、`knowledge` のいずれか、`status` には `active` または `reference` を指定する。`tags` は重複しない検索語を2件以上とし、`related` には実在するリポジトリ内のファイルパス、`sources` には一次資料のHTTPS URLを記載する。

本文は日本語で書き、固有名詞とコードの識別子は元の表記を保つ。設計上の判断と確認方法を残し、作業記録はGitの履歴で管理する。文書のメタデータと内部リンクは次のコマンドで検査する。

```sh
uv run --locked python scripts/validate_docs.py
```
