# Workflow中心の収集台帳

## 保存の原則

- **まず収集し、出典を残す。** 独自の評価点、人気、品質審査を収集からの排除条件にしない。
- JSON、JSONC、PNG、WebPなどは未分類でも候補として保持する。
- 発見したファイルが動作可能だとは決めつけない。
- GitHubの公開元リポジトリ、コミットSHA、パス、Blob SHAで版を識別する。
- 同じ内容でも作者・公開元が異なれば別記録として保持する。
- 取得失敗は「候補なし」と扱わない。
- Issueの件名やURLは公開元全体の参考情報であり、個々のWorkflowとの関係を断定しない。
- 公開Workflowを勝手に実行、再ライセンス、再配布しない。

## 収集の流れ

1. 設定済み公開元や検索からリポジトリを見つける。
2. 候補ファイルのURL、版、ファイル名、モデル参照を記録する。
3. UI形式、API形式、Blueprintの特徴を静的に確認する。
4. 変更された版を履歴に追加する。
5. 静的検査と参考情報を区別して保存する。
6. JSON・CSV・Markdownから用途別に検索できるようにする。

```sh
PYTHONPATH=src python -m gwp.discovery sync
PYTHONPATH=src python -m gwp.discovery stats
PYTHONPATH=src python -m gwp.discovery search --term KSampler
python -m unittest discover -s tests -v
```

定期収集はUTCの0:17、6:17、12:17、18:17（日本時間9:17、15:17、21:17、翌3:17）に設定されています。実際のGitHub Actions実行時刻は遅れる場合があります。手動実行も可能で、第三者のコードやモデルは実行しません。

1回あたりの処理上限は24リポジトリです。これは**処理待ちの上限であり、品質に基づく除外ではありません。** GitHubの検索API等の制限があるため、世界中の候補を完全に収集したとは主張しません。

## 既知の制限

- PNG／WebPの埋め込みWorkflowは未解析の候補がある。
- Civitai／Hugging Faceは一部モデルのメタデータ取得が中心。
- 外部APIが確認できないサイトは参照先にとどまる。
- 旧方式のGitHub Issue収集には件数制限がある。
- GPU実行、再現性の実測、ライセンス判定、自動採用、作品公開は未実装。

## 安全と検証

GitHub Actionsの短期トークンと既知のHTTPS APIを使用し、収集したJSONをコードとして実行しません。検証時はコミット固定の`source_url`と`blob_sha`を照合します。
