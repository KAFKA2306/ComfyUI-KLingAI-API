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

`docs/`には、長期運用に必要な設計書と、出典・用語を扱うナレッジだけを置く。目標や収集元の設定は`config/registry.json`、収集・制作履歴は`catalog`ブランチの`data/workflow_registry.json`に保存する。実装はコードを正本とし、文書には同じデータや作業記録を複製しない。

## 設計書

- [全体設計](design/system.md)：公開Workflowの収集から制作までの処理と責任分担
- [台帳の保全・復旧](design/durability.md)：永続保存、別PCからの復旧、競合統合、制作と公開の出典管理
- [制作工程への接続](design/production.md)：ComfyUIへの投入、出力回収、制作先への受け渡し
- [作品構成と演出](design/creative.md)：制作単位の依存関係と変更の影響

## ナレッジ

- [Workflow台帳と用語](knowledge/registry.md)：収集データの構造、状態、検索方法
- [一次資料と情報源](knowledge/sources.md)：公開元の区分、原典と利用条件の確認

## 文書の規則

各Markdownファイルには、先頭に`id`、`title`、`kind`、`status`、`updated`、`tags`、`related`、`sources`を記載する。値はJSON互換のYAMLにする。

`kind`は`index`、`design`、`knowledge`のいずれか、`status`は`active`か`reference`とする。`tags`は重複しない語を2件以上指定する。`related`には実在するリポジトリ内パス、`sources`には確認した一次資料のHTTPS URLを記す。

本文は日本語で書き、コードの識別子と固有名詞は変えない。判断の根拠と実行手順は残し、重複や進捗メモは載せない。メタデータと内部リンクは次のコマンドで検査する。

```sh
uv run --locked python scripts/validate_docs.py
```
