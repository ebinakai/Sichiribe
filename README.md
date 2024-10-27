<div align="center">
   <img
      src="res/Sichiribe_icon.png"
      alt="Sichiribe icon"
      width="100"
   >
   <h1>Sichiribe</h1>
   <p>7-Segment display Analyzer for JunLab 2024</p>

   <a href="https://github.com/ebinakai/Sichiribe/releases/">Releases</a> ･ 
   <a href="#概要">Features</a> ･ 
   <a href="#インストール">Installation</a> ･ 
   <a href="#参考資料">References</a> ･ 
   <a href="#ライセンス">License</a>
</div>

---  

![Python](https://img.shields.io/badge/python-3.9_|_3.10_|_3.11_|_3.12-blue)
[![Tensorflow](https://img.shields.io/badge/tensorflow-2.17.0-green)](https://github.com/tensorflow/tensorflow/tree/v2.17.0)
[![PySide](https://img.shields.io/badge/PySide-6-green)](https://pypi.org/project/PySide6/6.7.2/)
[![opencv](https://img.shields.io/badge/opencv-4.10-green)](https://pypi.org/project/opencv-python/4.10.0.84/)
[![License](https://img.shields.io/badge/lisence-MIT-blue)](https://github.com/EbinaKai/Sichiribe/blob/main/LICENSE.txt)
<br><br>
![Build Status](https://github.com/EbinaKai/Sichiribe/actions/workflows/build.yaml/badge.svg)

## 概要

7セグメント表示器が示したデータをシリアル等で読み取れない場合のために、メータの表示状態を録画し、そこからデータを取り出すためのプログラムを作成した。

### 仕様

- 動画を入力して、その動画を解析する
- カメラを接続して、リアルタイムで解析する
- 上記に項目をCLI及び、GUIで実行する
- [MacOS用のビルド(署名なし)](https://github.com/EbinaKai/Sichiribe/releases/tag/v0.1.5)

## インストール

仮想環境の作成等はMacOS・Linuxに準拠するため、Windowsで実行する際などは適宜読み替えてほしい。  
また、Linux環境以外で `tflite-runtime` を用いたい場合は [こちら](https://github.com/EbinaKai/Sichiribe/wiki/How-to-build-tflite%E2%80%90runtime) を参照するとよい。

```bash
# リポジトリのクローン
git clone https://github.com/EbinaKai/Sichiribe.git
cd Sichiribe

# 仮想環境の作成
python3 -m venv env

# 仮想環境の有効化
source ./env/bin/activate

# ライブラリのインストール
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### TensorFlowのインストール

環境に応じて、以下のいずれかの方法でTensorFlowをインストールしてほしい。

1. フルバージョンのTensorFlow (MacOS/Linux/Windows向け)  
   フル機能を備えたTensorFlowを利用する場合:

   ```bash
   pip install tensorflow==2.17.0
   ```

2. TensorFlow Metal (MacOS向けの追加インストール)  
   MacOSで Python 3.11 以前のバージョンを使用し、Metal APIを活用してGPUでの学習・推論を行う場合、追加で以下をインストールする:

   ```bash
   pip install tensorflow-metal
   ```

3. TensorFlow Lite Runtime (Linux環境、推論のみの場合)  
   軽量でモデルの推論のみを行い、学習をしない場合:

   ```bash
   pip install tflite-runtime
   ```

## モデルの用意

学習済モデルは、[Github | Release v0.1.1](https://github.com/EbinaKai/Sichiribe/releases/tag/v0.1.1) または [Github | Release v0.1.2](https://github.com/EbinaKai/Sichiribe/releases/tag/v0.1.2) においてあるので、そこからダウンロードして `model/` フォルダを作成して設置する。

```bash
mkdir model

# tensorflow を使用する場合
curl -L -o model/model_100x100.keras https://github.com/EbinaKai/Sichiribe/releases/download/v0.1.1/model_100x100.keras

# tflite-runtime を使用する場合
curl -L -o model/model_100x100.tflite https://github.com/EbinaKai/Sichiribe/releases/download/v0.1.2/model_100x100.tflite
```

## 使い方

- [GUIアプリの使い方](https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-GUI-App)
- [CLIによるカメラ映像のリアルタイム解析のやり方](https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-CLI#%E3%82%AB%E3%83%A1%E3%83%A9%E6%98%A0%E5%83%8F%E3%81%AE%E3%83%AA%E3%82%A2%E3%83%AB%E3%82%BF%E3%82%A4%E3%83%A0%E8%A7%A3%E6%9E%90-by-livepy)
- [CLIによる動画ファイルの解析のやり方](https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-CLI#%E5%8B%95%E7%94%BB%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%AE%E8%A7%A3%E6%9E%90-by-replaypy)

## ファイル構造

| ファイル | 説明 |
| --- | --- |  
| `app.py` | GUIアプリケーションの起動 |
| `live.py` | 外部カメラからライブ解析 |
| `replay.py` | 動画ファイルから解析 |
| `cores/common.py` | コアな汎用的な機能の関数詰め合わせ |
| `cores/capture.py` | カメラにアクセスする機能 |
| `cores/frame_editor.py` | 動画のフレームに関する機能及び7セグメント表示器の領域選択機能 |
| `cores/detector.py` | 7セグ表示器から数字を推測するプログラムの親クラス |
| `cores/cnn.py` | CNNモデルを用いて画像から数字を取得するプログラムのコア部分 |
| `cores/cnn.py` | CNNモデルをTensorflowのフルバージョン(.kerasモデル)で動かす場合 |
| `cores/cnn_lite.py` | CNNモデルをtflite-runtime(.tfliteモデル)で動かす場合 |
| `cores/exporter.py` | 取得した結果を任意の形式で出力・保存する機能 |
| `train/train.py` | CNNモデルを学習させるプログラム |
| `train/conv_keras2tf.py` | Kerasモデルをtflite形式に変換するプログラム |
| `gui/utils/common.py` | GUI用の汎用的な機能の関数詰め合わせ |
| `**gui**/utils/router.py` | GUIの各ページのルーティング関数 |
| `gui/utils/screen_manager.py` | GUIの各ページの管理クラス |
| `gui/views/splash_view.py` | GUI起動後のスプラッシュ画像 |
| `gui/views/main_view.py` | メインページ。この中に各ページをラップする |
| `gui/views/menu_view.py` | ライブ解析・動画ファイル解析を選択 |
| `gui/views/log_view.py` | ログの表示画面 |
| `gui/views/region_select_view.py` | 7セグメント表示機の領域選択画面 |
| `gui/views/live_setting_view.py` | ライブ解析の設定画面 |
| `gui/views/live_feed_view.py` | ライブ解析のカメラ画角確認画面 |
| `gui/views/live_exe_view.py` | ライブ解析の処理画面。推論結果のグラフと7セグ画像が表示される |
| `gui/views/replay_setting_view.py` | 動画ファイル解析の設定画面 |
| `gui/views/replay_threshold_view.py` | ２値化のしきい値を設定 |
| `gui/views/replay_exe_view.py` | 動画ファイル解析の処理画面。推論結果のグラフが表示される |
| `gui/workers/live_feed_worker.py` | ライブ解析のカメラ画角確認のバックグランド処理 |
| `gui/workers/live_detect_worker.py` | ライブ解析の推論のバックグランド処理 |
| `gui/workers/frame_devide_worker.py` | 動画ファイル解析のフレーム分割のバックグランド処理 |
| `gui/workers/replay_detect_worker.py` | 動画ファイル解析の推論のバックグランド処理 |
| `gui/widgets/mpl_canvas_widget.py` | グラフを表示するウィジェット |
| `sample/*` | テスト用ファイル |

## モデル学習

CNNモデルを学習させるためには以下のプログラムを実行する。
参考にしたサイトは [ここ](https://child-programmer.com/seven-segment-digits-ocr-original-model/ "【7セグメント編】オリジナル学習済みモデルの作成方法：連続デジタル数字画像認識プログラミング入門（Python・OpenCV・Keras・CNN）") 。  
上記サイトからデータセットも落としてこれるので、学習前にダウンロードしたあとに zip を解凍してプロジェクトフォルダに追加すること。また、カスタムデータセットを作成した際は、一文字ごとに分割して PNG形式で保存するとプログラムを改変せずに実行できる。  

```bash
# 学習(ファイル内のパラメーターを調整してから実行)
python cnn/train.py

# 軽量モデルに変換
python cnn/conv_keras2tf.py
```

## 参考資料

- [子供プログラマー](https://child-programmer.com/seven-segment-digits-ocr-original-model/ "【7セグメント編】オリジナル学習済みモデルの作成方法：連続デジタル数字画像認識プログラミング入門（Python・OpenCV・Keras・CNN）")
- [Github | Kazuhito00/7segment-display-reader](https://github.com/Kazuhito00/7segment-display-reader "Kazuhito00/7segment-display-reader")

## ライセンス

このプロジェクトは MIT ライセンスのもとで公開されています。詳細については、[LICENSE.txt](LICENSE.txt) ファイルをご覧ください。
