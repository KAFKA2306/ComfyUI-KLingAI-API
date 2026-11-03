---
id: "docs-index"
title: "設計書とナレッジの索引"
kind: "index"
status: "active"
updated: "2026-11-03"
tags: ["索引","設計","ナレッジ"]
related: ["docs/design/system.md","docs/knowledge/registry.md"]
sources: []
---

# 設計書とナレッジ

`docs/design/` は制作基盤の設計と操作手順、`docs/knowledge/` は出典と用語を扱う。

8領域の目標、収集元、制作案件、採用Workflowの設定は[一元台帳](../config/registry.json)に置く。収集・制作履歴は`catalog`ブランチの`data/workflow_registry.json`に保存する。処理の詳細は実装コードを参照する。`.cache/`は作業用の一時保存先とし、正本の情報を文書へ複製しない。

## 設計書

- [全体設計](design/system.md)：公開Workflowの収集から制作までの処理と責任分担
- [台帳の保全・復旧](design/durability.md)：永続保存、別PCからの復旧、競合統合、制作と公開の出典管理
- [制作工程への接続](design/production.md)：ComfyUIへの投入、出力回収、制作先への受け渡し
- [作品構成と演出](design/creative.md)：制作単位の依存関係と変更の影響

## ナレッジ

- [Workflow台帳と用語](knowledge/registry.md)：収集データの構造、状態、検索方法
- [一次資料と情報源](knowledge/sources.md)：公開元の区分、原典と利用条件の確認

## 文書の規則

各Markdown文書の先頭に、`id`、`title`、`kind`、`status`、`updated`、`tags`、`related`、`sources`を持つYAMLフロントマターを付ける。値はJSON互換のYAMLで記述する。

`kind`には`index`、`design`、`knowledge`のいずれかを、`status`には`active`または`reference`を指定する。`tags`は重複しない検索語を2件以上、`related`は実在するリポジトリ内のファイルパス、`sources`は一次資料のHTTPS URLを記載する。

本文は日本語で書き、固有名詞やコードの識別子は元の表記を保つ。設計上の判断と確認方法を残し、重複した説明や作業日誌はGitの履歴へ委ねる。文書と内部リンクの検査には次を使う。

```sh
uv run --locked python scripts/validate_docs.py
```
