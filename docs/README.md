---
id: "docs-index"
title: "設計書とナレッジの索引"
kind: "index"
status: "active"
updated: "2026-11-04"
tags: ["索引","設計","ナレッジ"]
related: ["docs/design/system.md","docs/knowledge/registry.md"]
sources: ["https://imoz.jp/humanizer.ja.txt"]
---

# 設計書とナレッジ

`docs/design/` は制作基盤の設計と操作手順、`docs/knowledge/` は出典と用語を扱う。

8領域の目標、収集元、制作案件、採用Workflowの設定は[一元台帳](../config/registry.json)に置く。収集・制作履歴は`main`ブランチの`data/workflow_registry.json`に保存する。処理の詳細は実装コードを参照する。`.cache/`は作業用の一時保存先とし、正本の情報を文書へ複製しない。

## 設計書

- [全体設計](design/system.md)：公開Workflowの収集から制作までの処理と責任分担
- [自律改善・記憶・監視](design/agent-loop.md)：毎時の調査、修正、評価と実行間メモリ
- [台帳の保全・復旧](design/durability.md)：永続保存、別PCからの復旧、競合統合、制作と公開の出典管理
- [制作工程への接続](design/production.md)：ComfyUIへの投入、出力回収、制作先への受け渡し
- [作品構成と演出](design/creative.md)：制作単位の依存関係と変更の影響

## ナレッジ

- [Workflow台帳と用語](knowledge/registry.md)：収集データの構造、状態、検索方法
- [一次資料と情報源](knowledge/sources.md)：公開元の区分、原典と利用条件の確認
- [外部ツールの制作パイプライン](knowledge/pipelines.md)：LRC、文字PV、字幕動画の工程と出典

## 文書の規則

各Markdown文書の先頭に、`id`、`title`、`kind`、`status`、`updated`、`tags`、`related`、`sources`を持つYAMLフロントマターを付ける。値はJSON互換のYAMLで記述する。

`kind`には`index`、`design`、`knowledge`のいずれかを指定し、`status`には`active`または`reference`を使う。`tags`は重複しない検索語を2件以上、`related`は実在するリポジトリ内のパスとする。`sources`には根拠となる一次資料のHTTPS URLを記載し、参照資料がない文書では空配列にする。

本文は日本語で書き、固有名詞やコードの識別子は元の表記を保つ。[推敲指針](https://imoz.jp/humanizer.ja.txt)に沿って、必要な説明を残す。

実装・検証結果・作品公開を断定する場合は、対応するコード、実行結果、一次資料、公開物のURLで裏付ける。根拠のない成果報告、作業日誌、一般的な注意書きを追加しない。文書と内部リンクの検査には次を使う。

```sh
uv run --locked python scripts/validate_docs.py
```
