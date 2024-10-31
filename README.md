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
- [ビルド(Mac版は署名なし)](https://github.com/EbinaKai/Sichiribe/releases/tag/v0.1.7)

## インストール

仮想環境の作成等はMacOS・Linuxに準拠するため、Windowsで実行する際などは適宜読み替えてほしい。  

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

## モデルの用意

学習済モデルは、[Github | Release v0.1.6](https://github.com/EbinaKai/Sichiribe/releases/tag/v0.1.6) 、[Github | Release v0.1.1](https://github.com/EbinaKai/Sichiribe/releases/tag/v0.1.1) または [Github | Release v0.1.2](https://github.com/EbinaKai/Sichiribe/releases/tag/v0.1.2) においてあるので、そこからダウンロードして `model/` フォルダを作成して設置する。

```bash
mkdir -p model

# onnxruntime を使用する場合（デフォルト）
curl -L -o model/model_100x100.onnx https://github.com/EbinaKai/Sichiribe/releases/download/v0.1.6/model_100x100.onnx

# tensorflow を使用する場合
curl -L -o model/model_100x100.keras https://github.com/EbinaKai/Sichiribe/releases/download/v0.1.1/model_100x100.keras

# tflite-runtime を使用する場合
curl -L -o model/model_100x100.tflite https://github.com/EbinaKai/Sichiribe/releases/download/v0.1.2/model_100x100.tflite
```

## 使い方

- [GUIアプリの使い方](https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-GUI-App)
- [CLIによるカメラ映像のリアルタイム解析のやり方](https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-CLI#execution-live)
- [CLIによる動画ファイルの解析のやり方](https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-CLI#execution-replay)

## モデル学習

CNNモデルを学習させるためには以下のプログラムを実行する。
参考にしたサイトは [ここ](https://child-programmer.com/seven-segment-digits-ocr-original-model/ "【7セグメント編】オリジナル学習済みモデルの作成方法：連続デジタル数字画像認識プログラミング入門（Python・OpenCV・Keras・CNN）") 。  
上記サイトからデータセットも落としてこれるので、学習前にダウンロードしたあとに zip を解凍してプロジェクトフォルダに追加すること。また、カスタムデータセットを作成した際は、一文字ごとに分割して PNG形式で保存するとプログラムを改変せずに実行できる。  

```bash
# 学習(ファイル内のパラメーターを調整してから実行)
python train/train.py

# 軽量モデルに変換
python train/conv_keras2tf.py
```

## 参考資料

- [子供プログラマー](https://child-programmer.com/seven-segment-digits-ocr-original-model/ "【7セグメント編】オリジナル学習済みモデルの作成方法：連続デジタル数字画像認識プログラミング入門（Python・OpenCV・Keras・CNN）")
- [Github | Kazuhito00/7segment-display-reader](https://github.com/Kazuhito00/7segment-display-reader "Kazuhito00/7segment-display-reader")

## ライセンス

このプロジェクトは MIT ライセンスのもとで公開されています。詳細については、[LICENSE.txt](LICENSE.txt) ファイルをご覧ください。
