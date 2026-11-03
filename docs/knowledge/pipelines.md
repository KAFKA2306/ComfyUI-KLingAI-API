---
id: "knowledge-pipelines"
title: "外部ツールを組み合わせる制作パイプライン"
kind: "knowledge"
status: "active"
updated: "2026-11-04"
tags: ["制作パイプライン","音源","歌詞","字幕","Shorts"]
related: ["config/registry.json","src/gwp/registry.py","docs/design/creative.md"]
sources: ["https://github.com/852wa/JIZURA","https://github.com/wickeddoc/syncalong","https://github.com/UseSuno/UseSunoMVStudio","https://github.com/jaydemks/phrasync","https://github.com/blizzardcldasl/audio-lyrics-skill","https://github.com/dancolta/clipcut"]
---

# 外部ツールを組み合わせる制作パイプライン

ComfyUIのWorkflow JSONは `workflows`、複数のツールをつなぐ工程は一元台帳の `pipelines` に保存する。外部アプリをComfyUIのWorkflow JSONと数えない。工程に書いた入出力は原典で確認できる形式だが、ツール間の自動連携やローカル実行の成功を意味しない。

## 登録一覧

| 制作目的 | 工程 | 成果物 |
| --- | --- | --- |
| 歌詞付き楽曲から文字PV | [syncalong](https://github.com/wickeddoc/syncalong) → [JIZURA](https://github.com/852wa/JIZURA) | MP4・透過PNG連番 |
| 音源だけから文字PV | [audio-lyrics](https://github.com/blizzardcldasl/audio-lyrics-skill) → 歌詞校正 → JIZURA | MP4 |
| 歌詞MVの演出を変更 | syncalong → [UseSuno MV Studio](https://github.com/UseSuno/UseSunoMVStudio) | MP4・WebM |
| 背景動画＋歌詞演出 | syncalong → [Phrasync](https://github.com/jaydemks/phrasync) | MP4 |
| 音声の字幕動画化 | Phrasync | 字幕入りMP4・SRT |
| 話し動画のShorts化 | [clipcut](https://github.com/dancolta/clipcut) | MP4 |

## 歌詞から文字PVを作る

確定歌詞とMP3を用意し、syncalongで行頭時刻付きのLRCへ変換する。

```sh
uv run --with 'syncalong[whisper]' syncalong lyrics.txt song.mp3 > lyrics.lrc
```

Whisperによる認識にはモデルとffmpegが必要。歌唱のタイミングや認識結果を必ず試聴・修正する。JIZURAにLRCと同じ音源を読み込み、シードとレイアウトを選んで動画を出力する。透明PNG連番は編集ソフトで重ねる素材にも使える。

## 探索と採用のルール

- `uv run --locked python -m gwp.registry list --kind pipelines` で工程を一覧する。
- `pipelines[].steps` の入力 `requires` は初期 `inputs` または前の工程の `provides` に存在させる。登録時に検査する。
- `projects[].pipeline_ids` と制作単位の `pipeline_ids` から工程を参照する。ComfyUI用の `workflow_ids` とは分ける。
- 公式サイト・開発元の一次資料URLを記録し、入力、出力、手動確認が必要な箇所、利用条件を調べる。第三者ツールを収集時にインストール・実行しない。
- 音源、歌詞、生成動画の公開権は各素材とサービスの利用条件から別途確認する。

