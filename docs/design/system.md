---
id: "design-system"
title: "Workflow収集・制作基盤の設計"
kind: "design"
status: "active"
updated: "2026-11-03"
tags: ["設計","Workflow","出典","ComfyUI"]
related: ["config/registry.json","src/gwp/discovery.py","src/gwp/production.py"]
sources: ["https://github.com/Comfy-Org/workflow_templates"]
---

# Workflow収集・制作基盤の設計

公開Workflow・Subgraph・Blueprintを世界中から継続的に発見し、元の出典と改訂を保ったまま制作工程に利用します。独自スコア・順位・人気による足切りは設けません。

| 層 | 役割・正本 |
| --- | --- |
| 情報源 | [config/registry.json](../../config/registry.json)：公開先、検索語、参考先、用途分類 |
| 発見 | [src/gwp/discovery.py](../../src/gwp/discovery.py)：候補ファイルの列挙と構造の静的確認 |
| 台帳 | `.cache/workflow_registry.json`（実行時キャッシュ）：出典、コミットSHA、Blob SHA、改訂、探索状態 |
| 閲覧 | `gwp.discovery search / export`：既存台帳から検索・CSV/JSON出力 |
| 素材生成 | [src/gwp/production.py](../../src/gwp/production.py)：選択されたAPI形式Workflowのみをローカル実行 |


制作のCLIは[制作工程への接続](production.md)を参照してください。
