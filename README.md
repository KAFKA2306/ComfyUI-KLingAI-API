# ComfyUI-KLingAI-API

ComfyUI 上で KLing AI API を呼び出すためのカスタムノードです。API の仕様は [KLing AI API ドキュメント](https://docs.qingque.cn/d/home/eZQArO-0RpjbQMpf5DPa-w8Rp?identityId=1oEER8VjdS8#section=h.wxrj3t7cbpg3)を参照してください。

## セットアップ
1. `ComfyUI/custom_nodes` に本リポジトリをクローンまたはシンボリックリンクします。
   ```bash
   git clone https://github.com/KwaiVGI/ComfyUI-KLingAI-API
   ```
2. 依存関係を `uv` でインストールします。
   ```bash
   uv pip install pyjwt httpx pillow numpy pydantic
   ```
3. `config.ini` に KLing API キーを設定し、ファイルはローカル管理のままにします。
4. ComfyUI を再起動してノードを読み込みます。

## 動作確認
- モジュールのコンパイルチェック: `uv run python -m compileall py`
- API スモークテスト: `uv run python examples/api_test.py`（実行前に API キーを環境変数または `config.ini` に設定）

## 追加情報
- KLing AI サービスの料金は [KLing AI Pricing](https://klingai.com/dev-center) を参照してください。
