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

`docs/` は、制作基盤の仕組みを定める設計書と、出典や用語を整理するナレッジに分ける。8領域の目標、収集元、制作案件と採用候補の設定は `config/registry.json` に一元化する。制作処理の実装はコード、公開情報の取得結果は `.cache/workflow_registry.json` を参照する。同じデータを文書に複製しない。特定の制作案件を全領域の共通設計の既定例にしない。

## 設計書

- [全体設計](design/system.md)：公開Workflowの収集から制作までの処理と責任分担
- [制作工程への接続](design/production.md)：ComfyUIへの投入、出力回収、制作先への受け渡し
- [作品構成と演出](design/creative.md)：制作単位の依存関係と変更の影響

## ナレッジ

- [Workflow台帳と用語](knowledge/registry.md)：収集データの構造、状態、検索方法
- [一次資料と情報源](knowledge/sources.md)：公開元の区分、原典と利用条件の確認

## 文書の規則

各Markdownファイルの先頭には、`id`、`title`、`kind`、`status`、`updated`、`tags`、`related`、`sources` を持つYAMLフロントマターを付ける。値にはJSON互換のYAMLを使う。

`kind` は `index`、`design`、`knowledge`、`status` は `active`、`reference` とする。`tags` には重複しない検索語を2件以上指定する。`related` は存在するリポジトリ内パス、`sources` は一次資料のHTTPS URLを記載する。

本文は日本語で書き、固有名詞やコードの識別子は元の表記を保つ。設計上の判断と確認方法を残し、重複した説明や作業日誌はGitの履歴へ委ねる。文書と内部リンクの検査には次を使う。

```sh
uv run --locked python scripts/validate_docs.py
```
