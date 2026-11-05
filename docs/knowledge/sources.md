---
id: "knowledge-sources"
title: "一次資料と情報源"
kind: "knowledge"
status: "active"
updated: "2026-11-04"
tags: ["出典","一次資料","ComfyUI","ライセンス"]
related: ["config/registry.json","docs/knowledge/registry.md"]
sources: ["https://github.com/Comfy-Org/workflow_templates","https://github.com/comfyanonymous/ComfyUI_examples"]
---

# 一次資料と情報源

公開元と検索語は `config/registry.json` に登録する。新しい取得先を追加するときも、同ファイルを更新する。

## Workflowの公開元

公式の入口には[Comfy-Orgのテンプレート](https://github.com/Comfy-Org/workflow_templates)、[公開Workflow](https://github.com/Comfy-Org/workflows)、[ComfyUIの作例](https://github.com/comfyanonymous/ComfyUI_examples)がある。[Comfy-Orgのリポジトリ一覧](https://github.com/orgs/Comfy-Org/repositories)では関連する公開元を確認できる。

コミュニティのWorkflowは、設定したリポジトリと検索語で探索する。取得したファイルには原典URL、固定コミット、パス、Blob SHAを記録する。APIエラーや配布元の削除は、その事実を記録し、候補の品質評価と混同しない。

## モデル情報と参考サイト

Hugging FaceとCivitaiのモデル情報は収集台帳の `feeds` に記録する。参考サイトは [`config/registry.json`](../../config/registry.json) の `reference_sources` で管理する。

権利情報は `rights` に対象・ライセンス・一次証拠URLとして登録する。必須項目は [`gwp.ledger`](../../src/gwp/ledger.py) に定義する。

## 会話音声のWorkflow構成

[Chatterbox Dialog TTSの公式テンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio-chatterbox_tts_dialog.json)では、2つの`LoadAudio`で話者の参照音声を読み込み、片方を`AudioCrop`で切り出してから`FL_ChatterboxDialogTTS`へ入力する。会話文をノード内で指定し、生成した`dialog_audio`を`SaveAudioMP3`へ渡す。参照音声は`AUDIO`、生成結果も`AUDIO`であり、保存先はMP3形式である。

主な再利用先はPodcast・音声。YouTube・Shorts、映画・アニメーション、ゲーム制作、VRChatワールドでは台詞音声の制作工程として利用を検討できる。アバター・衣装、BOOTH商品、3Dモデルへの直接の適用は、この原典だけでは確認できない。類似する単一話者の音声合成と異なり、複数話者の参照音声と会話文を1つのノードに入力する構造を持つ。

`FL_ChatterboxDialogTTS`の配布元、必要なカスタムノードの版、モデルの取得先、VRAM、各モデルと参照音声のライセンス、実機動作、商用利用条件は、このJSONだけでは確定できない。利用前にそれぞれの一次資料と実機で確認する。これらの条件はWorkflowの自動順位付けに加点・減点しない。

## 単一画像からスプライトシートとアニメーションを作る構成

[Comfy-Org公式テンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/template_purz_nb2_single_image_sprite_sheet.json)（原典Blob SHA `4d0d760e84173c19c6d28cd10601cd8558fdcaad`）は、`LoadImage`の画像を`GeminiNanoBanana2`へ渡し、画像を分割するサブグラフを通して、複数の`SaveImage`でフレームを保存する。`SaveImageWithAlpha`は透過画像を、2つの`VHS_VideoCombine`はアニメーション出力を扱う。ノートにはGIF・WebMの出力を意図すると記載されているが、保存形式や実際の生成成功は未検証である。

入力は画像と生成指示文、出力先はフレーム画像、スプライトシート、アニメーションである。ゲーム制作のキャラクターアニメーションとBOOTH商品の2D素材に直接応用でき、YouTube・Shortsや映画・アニメーションの素材制作にも応用を検討できる。VRChatワールド、アバター・衣装、Podcast・音声、3Dモデルへの直接適用は原典から確認できない。

`GeminiNanoBanana2`は外部画像生成機能への依存がある。分割処理はUUID型のサブグラフであり、`VHS_VideoCombine`と`SaveImageWithAlpha`を含むノードの配布元・対応版、必要モデル、API利用条件、費用、必要VRAM、素材と出力物のライセンス、商用利用可否は未確認である。単純な静止画生成Workflowと異なり、フレーム分割と動画結合を一続きにする。これらの条件は自動順位付けに含めず、人気30・更新30・領域適合40の外で確認する。人気と更新日がGitHubリポジトリ単位の場合、個別Workflowの値ではない。

## 開始画像と終了画像から動画を生成する構成

[Comfy-OrgのWan2.1 First/Last Frame公式テンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/wan2.1_flf2v_720_f16.json)（原典Blob SHA `97db669a9e12309f4ecfb29f4499ee819d126459`）は、2つの`LoadImage`から開始・終了画像を取り込み、`CLIPVisionLoader`・`CLIPVisionEncode`、`WanFirstLastFrameToVideo`、`KSampler`、`VAEDecode`、`CreateVideo`、`SaveVideo`を組み合わせる。`UNETLoader`、`CLIPLoader`、`VAELoader`、`ModelSamplingSD3`も含む。入力は開始・終了画像とテキスト条件、出力は生成動画である。静止画像からの通常の動画生成と異なり、終端画像も条件として渡す。

YouTube・Shorts、映画・アニメーション、ゲーム制作、VRChatワールドの映像素材に再利用を検討できる。アバター・衣装、BOOTH商品、Podcast・音声、3Dモデルへの直接適用は原典だけでは確認できない。必要なモデルファイルとその版、カスタムノードの要否、VRAM、ライセンス、商用利用条件、実機動作は未確認であり、採点対象にしない。

## 360度パノラマからGLBメッシュを作る構成

[Comfy-Org公式のMoGeパノラマWorkflow](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_moge_panorama_to_mesh.json)は、`LoadImage`から正距円筒図法の360度画像を入力し、サブグラフ内の`MoGePanoramaInference`で12方向の画像を推論・統合し、`MoGePointMapToMesh`を経て`SaveGLB`でメッシュを保存する。原典は通常2:1の全天球画像を想定し、出力は内側から見る球状のGLBである。単一の透視画像を使う[別テンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_moge_perspective_to_mesh.json)と異なり、複数方向の深度をCPUで統合する。

主な再利用先はVRChatワールド、3Dモデル、ゲーム制作。BOOTH商品の3D背景素材にも応用を検討できる。映画・アニメーションとYouTube・Shortsでは3D背景としての利用を検討できるが、アバター・衣装とPodcast・音声への直接適用は原典から確認できない。

モデルの参照先は[Comfy-Org/MoGe](https://huggingface.co/Comfy-Org/MoGe)で、テンプレートには`moge_1_vitl_fp16.safetensors`と`moge_2_vitl_normal_fp16.safetensors`が記載されている。必要VRAM、実機動作、ComfyUI対応版、モデルと出力物のライセンス、商用利用条件は未確認。パノラマの分割解像度とバッチ数はGPU負荷、統合解像度はCPU負荷に関係する。これらの条件は人気30・更新30・領域適合40の採点に含めない。人気と更新日がGitHubリポジトリ単位の場合、個別Workflowの値ではない。

## Qwen-Image-2512で360度背景画像を生成する構成

[Comfy-Org公式360度画像テンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/template_qwen_Image_2512_360_lora.json)（原典Blob SHA `614e3cc51b13d0ee58dd635b2695465d26bfd512`）は、`PrimitiveStringMultiline`で360度画像の指示語と場面の文章を入力し、`StringConcatenate`で結合して、Qwen-Image-2512とLoRAを扱うサブグラフに渡す。生成された`IMAGE`を`SaveImage`で保存する。既定の画像サイズは2048×1024で、正距円筒図法の2:1パノラマを想定する。単純な画像生成との違いは、360度用LoRAと指示語を併用し、左右がつながる背景画像を狙う点にある。

サブグラフ内には`UNETLoader`、`CLIPLoader`、`VAELoader`、`ModelSamplingAuraFlow`などがある。原典が指定するモデルはQwen-Image-2512 FP8、Qwen 2.5 VLのテキストエンコーダ、Qwen Image VAE、360度用LoRA、任意のLightning LoRA。原典に記載されたファイル容量は順に19.03GB、8.74GB、242MB、720.1MB、1.58GBであり、必要VRAMを表す数値ではない。原典のノード属性はComfyUI標準ノードを示すが、実際の対応バージョンと追加依存の有無は利用環境で確認する。

8領域での再利用先は、VRChatワールドとゲーム制作の環境背景、BOOTH商品の背景素材、YouTube・Shortsと映画・アニメーションの背景、3Dモデル制作時の背景参照。アバター・衣装とPodcast・音声への直接適用は未確認。モデル・LoRAごとのライセンス、商用利用条件、必要VRAM、左右境界の品質、実機動作は未確認であり、採点しない。人気と更新日はGitHubリポジトリ単位の代理指標であり、個別Workflowの人気・更新日ではない。自動順位付けは人気30・更新30・制作領域適合40に限定する。
