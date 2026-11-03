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

設計書は制作基盤の動作と運用方法、ナレッジはWorkflowの出典と用語を扱います。8領域の目標・収集元・制作案件は `config/registry.json` にまとめ、収集データと制作履歴はcatalogブランチに保存します。文書へ台帳を複製しません。

## 設計書

- [全体設計](design/system.md)：収集、素材生成、作品完成の責任分担
- [台帳の保全・復旧](design/durability.md)：永続保存、PC交換、更新競合、制作・公開履歴
- [制作工程](design/production.md)：ローカルComfyUIへの投入、回収、制作先への受け渡し
- [作品構成と演出](design/creative.md)：制作単位の依存関係と変更の影響

## ナレッジ

- [Workflow台帳と用語](knowledge/registry.md)：記録項目、状態区分、検索方法
- [一次資料と情報源](knowledge/sources.md)：取得元と利用条件の確認

## 文書の規則

全Markdownファイルの先頭に、`id`、`title`、`kind`、`status`、`updated`、`tags`、`related`、`sources` を含むYAMLフロントマターを付けます。値はJSON互換のYAMLで記述します。

`kind` は `index`・`design`・`knowledge`、`status` は `active`・`reference` のいずれかです。`tags` は重複しない検索語を2件以上、`related` は存在するリポジトリ内のパス、`sources` は対応する一次資料のHTTPS URLを指定します。

本文は日本語で書き、固有名詞・コマンド・ファイル名の表記は維持します。設計判断、実行条件、確認方法を記し、進捗メモや同じ内容の説明を増やしません。文書のメタデータと内部リンクは次のコマンドで検査します。

```sh
uv run --locked python scripts/validate_docs.py
```
