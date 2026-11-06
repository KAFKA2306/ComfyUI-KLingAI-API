---
id: "knowledge-sources"
title: "一次資料と情報源"
kind: "knowledge"
status: "active"
updated: "2026-11-06"
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

## ACE-Step 1.5のテキスト条件から音声を作る構成

[Comfy-Org公式ACE-Step 1.5テンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_ace_step_1_5_split_4b.json)（原典Blob SHA `fe1c94c6de37b8b900a5c83b0decff4d3d490e02`）では、`DualCLIPLoader`と`TextEncodeAceStepAudio1.5`でテキスト条件を作り、`EmptyAceStep1.5LatentAudio`、`KSampler`、`VAEDecodeAudio`、`SaveAudioMP3`へ接続する。モデルは`UNETLoader`と`VAELoader`から供給する。原典には`acestep_v1.5_turbo.safetensors`、`ace_1.5_vae.safetensors`、`qwen_0.6b_ace15.safetensors`、`qwen_4b_ace15.safetensors`への参照がある。入力はテキスト条件、出力はMP3音声である。

主な再利用先はPodcast・音声。YouTube・Shorts、映画・アニメーション、ゲーム制作、VRChatワールドでは音楽・音声素材への利用を検討できる。アバター・衣装、BOOTH商品、3Dモデルへの直接適用は未確認。参照音声を入力する[Chatterbox Dialog TTS](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio-chatterbox_tts_dialog.json)とは異なり、この構成ではテキスト条件と潜在音声から生成する。

ノードとモデルの対応版、必要VRAM、各モデルのライセンス、商用利用条件、実機動作、音声品質は未確認である。これらは人気30・更新30・制作領域適合40の順位付けには含めない。GitHubスター数と最終push日時を利用する場合、それらはリポジトリ単位の指標であり、このWorkflow単体の人気や更新日ではない。

## 単一の透視画像からテクスチャ付きGLBを作る構成

[Comfy-Org公式MoGe Perspective-to-Mesh](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_moge_perspective_to_mesh.json)（原典Blob SHA `c4a412f9844b033f93782112a404188764afe4a9`）は、`LoadImage`から透視画像を入力し、MoGeの推論・メッシュ化を含むサブグラフを通して`SaveGLB`へ出力する。サブグラフはOpenGLとDirectXの法線プレビューも出力する。幅2048ピクセルを超える入力は、設定により推論前に長辺2048へ縮小できる。メッシュ間引きと深度の不連続をまたぐ面の除去も調整できる。

[360度パノラマからGLBを作る構成](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_moge_panorama_to_mesh.json)とは異なり、単一の透視画像から見えている形状を推定する。主な再利用先は3Dモデル、ゲーム制作、VRChatワールド、BOOTH商品の3D素材。YouTube・Shortsと映画・アニメーションでは背景素材への応用を検討できる。アバター・衣装とPodcast・音声への直接適用は未確認。

モデル参照先は[Comfy-Org/MoGe](https://huggingface.co/Comfy-Org/MoGe)。原典にはMoGe-1の`moge_1_vitl_fp16.safetensors`とMoGe-2の`moge_2_vitl_normal_fp16.safetensors`が記載され、後者は法線推定を扱う。必要VRAM、対応するComfyUI・ノードの版、モデル・出力物のライセンス、商用利用条件、実機動作は未確認であり、採点に含めない。人気30・更新30・制作領域適合40のみを採点し、GitHubスター数とpush日時はリポジトリ単位の代理指標として扱う。

## LTX-2.3の画像から映像と音声を作る構成

[Comfy-Org公式LTX-2.3 Image-to-Videoテンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_ltx2_3_i2v.json)では、`LoadImage`の入力画像と文章条件を使い、`LTXVImgToVideoInplace`、`SamplerCustomAdvanced`、`LTXVLatentUpsampler`、`LTXVAudioVAEDecode`、`SaveVideo`などを組み合わせる。映像・音声の潜在表現を生成・拡大・復号し、動画へ保存する構成である。単純な静止画像生成と異なり、画像から時間方向の映像と音声を扱う。

原典には[LightricksのLTX-2.3モデル](https://huggingface.co/Lightricks/LTX-2.3/)、22BのFP8チェックポイント、蒸留LoRA、Gemma 3系LoRA、空間アップスケーラーへの参照がある。これらはモデル依存を示すが、必要VRAMの実測値ではない。対応するComfyUI本体・カスタムノードの版、各モデルのライセンス、商用利用条件、生成品質、実機動作は未確認であり、利用前に原典と実行環境で確認する。

8領域ではYouTube・Shorts、映画・アニメーションの映像制作が直接の再利用候補である。ゲーム制作、VRChatワールド、BOOTH商品では動画素材としての利用を検討できる。Podcast・音声は生成音声の独立利用、アバター・衣装と3Dモデルは直接の適用が原典だけでは確認できない。類似する開始・終了画像指定の[Wan2.1 Workflow](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/wan2.1_flf2v_720_f16.json)とは入力条件と使用モデルが異なる。人気30・更新30・制作領域適合40のみを自動採点し、VRAM・モデル・ライセンス・実行環境は採点しない。GitHubのスター数とpush日時はリポジトリ単位であり、個別Workflowの指標ではない。


## Idolによる単一画像からGaussian Splatとメッシュを作る構成

[Comfy-Org公式Idolテンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_idol_image_to_gaussian_splat.json)（原典Blob SHA `bc8ecd97784ebd6f3849fe9c3f41cc0e01a9de7f`）は、`LoadImage`から単一の被写体画像を取り込み、画像からGaussian Splatを作るサブグラフに渡す。背景除去にはBiRefNetを使う設定がある。出力は`SplatToFile3D`によるSPZ、`SplatToMesh`と`SaveGLB`によるGLB、`RenderSplat`・`CreateVideo`・`SaveVideo`による回転プレビュー動画の3系統。原典のメッシュ変換解像度は384、プレビューは1024×1024・75フレーム・25fpsである。MoGeの透視画像からメッシュを推定する工程と異なり、Gaussian Splatを中間表現として使う。

モデルの一次参照先は[Comfy-Org/Idol](https://huggingface.co/Comfy-Org/Idol)と[Comfy-Org/BiRefNet](https://huggingface.co/Comfy-Org/BiRefNet)。原典には`idol_fp16.safetensors`、`idol_decoder_fp16.safetensors`、`dino_v3_vit_h_bf16.safetensors`、`flux2-vae.safetensors`、`birefnet.safetensors`が記載され、IdolはTripoSplat系ノードを使う。モデルファイル合計3.52GBという記載は必要VRAMではない。サブグラフの内部ノード版、カスタムノードの追加要否、必要VRAM、各モデルと出力物のライセンス、商用利用条件、実機動作は未確認。単一視点から推定するため背面・細部の形状は入力画像だけでは保証されない。

8領域では3Dモデル、ゲーム制作、VRChatワールド、BOOTH商品の3D素材が主な再利用候補。YouTube・Shortsと映画・アニメーションには回転プレビューを利用できる。アバター・衣装はメッシュの編集・リギング適性が未確認で、Podcast・音声への直接適用は確認できない。採点は人気30・更新30・領域適合40のみとし、モデル・VRAM・ライセンス・実行条件は別途確認する。GitHubスター数と更新日はリポジトリ単位の代理指標であり、この個別Workflowの評価値ではない。

## 単一画像からHunyuan3DのGLBを作る構成

[Comfy-Org公式Hunyuan3Dテンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_hunyuan3d_image_to_model.json)では、`LoadImage`の`IMAGE`を3D生成サブグラフへ渡し、出力を`SaveGLB`の`mesh`入力へ接続する。原典は`hunyuan3d-dit-v2_fp16.safetensors`を参照する。入力は単一画像、出力はGLB形式の3Dデータである。パノラマから周囲のメッシュを作るMoGeとは異なり、画像内の対象物を3D化する構成である。

主な再利用先は3Dモデル、ゲーム制作、VRChatワールド、BOOTH商品。アバター・衣装はメッシュの調整とリギングが別途必要であり、YouTube・Shorts、映画・アニメーションは3D素材として間接利用を検討できる。Podcast・音声への直接適用は確認できない。必要VRAM、サブグラフ内の詳細な依存関係、モデルとノードの配布条件、ライセンス、商用利用可否、実機動作は未確認である。これらは採点せず、人気30・更新30・制作領域適合40のみで順位付けする。GitHub単位の人気と更新日は個別Workflowの実績ではない。

## 4方向画像からHunyuan3D TurboでGLBを生成する構成

[Comfy-Org公式Hunyuan3D MultiView Turboテンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_hunyuan3d_multiview_to_model_turbo.json)（確認した原典Blob SHA `0f4b882dafc2241591be41761328bbfbd77fd1aa`）は、前・後・左・右の4画像をそれぞれ`LoadImage`で読み込み、`CLIPVisionEncode`から`Hunyuan3Dv2ConditioningMultiView`に接続する。`ImageOnlyCheckpointLoader`で`hunyuan3d-dit-v2-mv-turbo_fp16.safetensors`を参照し、`EmptyLatentHunyuan3Dv2`、`KSampler`、`VAEDecodeHunyuan3D`、`VoxelToMesh`、`SaveGLB`を経てGLB形式で保存する。原典のモデルリンクは[Comfy-Org/hunyuan3D_2.0_repackaged](https://huggingface.co/Comfy-Org/hunyuan3D_2.0_repackaged)で、チェックポイントの配布サイズは4.59GBと記載されている。これは必要VRAMの実測値ではない。

単一画像の[Hunyuan3Dテンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_hunyuan3d_image_to_model.json)と異なり、4方向の入力画像とMultiView専用の条件付け・チェックポイントを使う。3Dモデル、ゲーム制作、VRChatワールド、BOOTH商品の3D素材が主な再利用候補である。アバター・衣装はメッシュ編集とリギングが必要か未確認。YouTube・Shortsと映画・アニメーションは3D素材として間接利用を検討できる。Podcast・音声への直接適用は確認できない。必要VRAM、ライセンスと商用利用条件、カスタムノードの追加要否、実機での生成結果は未確認である。人気30・更新30・制作領域適合40のみで採点し、モデル・VRAM・ライセンス・実行条件は採点しない。GitHubスター数と更新日時はリポジトリ単位の代理指標であり、このWorkflow固有の実績ではない。

## 単一画像からTripoSplatでGaussian Splatを作る構成

[Comfy-Org公式TripoSplatテンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_triposplat_image_to_gaussian_splat.json)（原典Blob SHA `54c9ecc05a8270a6576faab6712fd12bf048c3fe`）は、`LoadImage`からTripoSplatの画像→Gaussian Splatサブグラフへ入力する。生成結果を`SplatToFile3D`でSPZに保存し、`RenderSplat`、`CreateVideo`、`SaveVideo`で回転プレビューを作る。別経路の`SplatToMesh`と`SaveGLB`は原典ではバイパス状態で、利用時に有効化する必要がある。メッシュ変換は実験的な出力として説明されている。既存のIdol方式とは生成モデルが異なり、両者の品質優劣は未検証である。

原典に記載されたモデルは`triposplat_fp16.safetensors`、`dino_v3_vit_h.safetensors`、`triposplat_vae_decoder_fp16.safetensors`、`flux2-vae.safetensors`、背景除去用`birefnet.safetensors`。配布元は[VAST-AI/TripoSplat](https://huggingface.co/VAST-AI/TripoSplat)と[Comfy-Org/BiRefNet](https://huggingface.co/Comfy-Org/BiRefNet)。必要VRAM、モデルとカスタムノードのライセンス、商用利用条件、実機動作は未確認であり、配布ファイル容量からVRAMを推定しない。

8領域では3Dモデル、ゲーム制作、VRChatワールド、BOOTH商品が直接の再利用候補。YouTube・Shortsと映画・アニメーションは回転プレビュー動画を素材として利用できる。アバター・衣装はリギングやメッシュ編集への適性が未確認で、Podcast・音声への直接利用は確認できない。順位付けは人気30・更新30・制作領域適合40のみとし、VRAM・ライセンス・モデル・実行条件は採点しない。GitHubの人気と更新日はリポジトリ単位であり、この個別Workflowの実績ではない。

## 動画から人物の3D姿勢とメッシュを推定する構成

[Comfy-Org公式SAM 3D Bodyテンプレート](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_sam3d_body.json)（原典Blob SHA `5a7000754c062a945f8024d45b0a5fd35ac58e37`）では、`LoadVideo`・`Video Slice`・`GetVideoComponents`で動画を取り込み、`RTDETR_detect`で人物を検出し、`SAM3_VideoTrack`で追跡する。`SAM3DBody_Loader`・`SAM3DBody_Predict`・`SAM3DBody_Smooth`で人体の3D姿勢・形状を推定し、`SAM3DBody_FaceExpression`で顔表情を補う。`BuildPoseFile`・`Save3DAdvanced`が3D出力、`SAM3DBody_Render`・`CreateVideo`・`SaveVideo`が動画出力の経路となる。`LoadMoGeModel`・`MoGeInference`・`MoGeGeometryToFOV`は画角推定の補助経路で、原典注記では任意とされる。複数人物の動画ではSAM3追跡が実用上重要と説明されている。

原典の参照モデルは`sam3.1_multiplex_fp16.safetensors`、`sam_3d_body_dinov3_bf16.safetensors`、`moge_2_vitl_normal_fp16.safetensors`、`rt_detr_v4-x-hgnet_fp32.safetensors`。一次配布先は[Comfy-Org/sam3.1](https://huggingface.co/Comfy-Org/sam3.1)、[Comfy-Org/sam-3d-body](https://huggingface.co/Comfy-Org/sam-3d-body)、[Comfy-Org/MoGe](https://huggingface.co/Comfy-Org/MoGe)、[Comfy-Org/SDPose](https://huggingface.co/Comfy-Org/SDPose)。入力は動画、出力候補は人物の3Dデータと描画動画。モデル容量は必要VRAMを示さない。各ノードの対応版、追加カスタムノードの要否、必要VRAM、ライセンス、商用利用条件、実機動作、リギング可能性は未確認である。単一画像から物体を生成するHunyuan3DやTripoSplatとは異なり、時間方向の人物検出・追跡と人体推定を扱う。

8領域ではアバター・衣装、3Dモデル、ゲーム制作、VRChatワールドで人物姿勢・メッシュの制作工程への再利用を検討できる。YouTube・Shortsと映画・アニメーションには人物の動きの解析・映像化、BOOTH商品には3D素材化の候補となる。Podcast・音声への直接適用は確認できない。自動採点は人気30・更新30・制作領域適合40のみとし、モデル・ライセンス・VRAM・実行環境は参考情報として独立させる。GitHubの人気と更新日はリポジトリ単位であり、個別Workflowの性能を示さない。
