# ファイル構成

```
[ft_lab.game.Ball]
  [config]
    [extension.toml]    設定ファイル
  [data]                Extensionで参照する画像など
  [docs]                Extensionで参照するドキュメント

  [ft_lab]
    [game]
      [Ball]
        [resources]     参照するリソース類
          [audio]       音データ
          [background]  背景のexr画像
          [images]      タイトル画像
          [usd]         使用するアセットとテクスチャ

        [scripts]       Pythonスクリプト
        __init__.py
        main.py         開始のPythonスクリプト
```

「ft_lab.game.Ball」がExtensionとしてのモジュール名になります。      

「ft_lab/game/Ball/resources」にExtensionで使用する画像や音データ、USDファイルなどを配置しています。      
ゲーム開始時にこれらの情報はStageに読み込まれます。       

## extension.tomlの指定

```
[dependencies]
"omni.audioplayer" = {}
```
の指定により、"omni.audioplayer"Extensionを起動します。     
これはAudioの再生で必要なモジュールです。    

## スクリプトのファイル

|ファイル名|説明|     
|---|---|     
|main.py|Extensionとしてはじめに見る部分。<br>メニューの管理を行っています。|     
|scripts/AudioControl.py|"omni.audioplayer"を使用してoggファイルを再生します。|     
|scripts/BallControl.py|ボールを配置、移動を管理します。|     
|scripts/ChangePostProcessing.py|Post Processingのパラメータを変更します。|     
|scripts/CreateStage.py|"resources"フォルダ内のusdファイルを読み込み、新しくStageを構築します。|     
|GameWorkflow.py|ゲームの流れを管理します。タイトル画面/ゲーム/ゲームオーバーの一連の流れの処理を行います。|     
|InputControl.py|キーボードまたはGamePadでの入力を管理します。|     
|LoadImageRGBA.py|リソース内の画像をPILを使ってomni.ui.ByteImageProviderに格納します。|     
|MoveRacket.py|ラケットを動かします。|     
|OverlayControl.py|オーバレイの描画を行います。|     
|StageInfo.py|ステージの情報です。スコアやLIFEの値もここで定義しています。|     
|StateData.py|状態遷移用の情報です。|     
