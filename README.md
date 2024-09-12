# 7Segment detector

## Description

7セグメント表示器が示したデータをシリアル等で読み取れない場合のために、メータの表示状態を録画し、そこからデータを取り出すためのプログラムを作成した。

## Requirements

- Python 3.9

## Features

- 動画を入力して、その動画を解析する
- カメラを接続して、リアルタイムで解析する
- 上記に項目をCLI及び、GUIで実行する
- プログラムのExe化

## Init

仮想環境の作成等はLinuxに準拠するため、Windowsで実行する際などは適宜読み替えてほしい。  

```bash
# リポジトリのクローン
git clone git@github.com:EbinaKai/7segDetector.git
cd 7segDetector

# 仮想環境の作成
python3 -m venv env

# 仮想環境の有効化
source ./env/bin/activate

# ライブラリのインストール
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# 以下のいずれかのtensorflowをインストールする
pip install tensorflow # フルバージョンのtensorflowを用いる場合
pip install tensorflow-metal # macosでGPUを用いる場合はこれも

pip install tflite-runtime # linux環境でモデルの学習をしない場合
```

## Install model

学習済モデルは、[Github | Release v0.1.2](https://github.com/EbinaKai/Sichiribe/releases/tag/v0.1.2) においてあるので、そこからダウンロードして `model/` フォルダを作成して設置する。

## GUI Execution

GUIでの諸項目の実行を行うには以下のコマンドを実行する。

```bash
python Sichiribe.py
```

階層構造及び画面フローを以下に示す。

![Sichiribe drawio](https://github.com/user-attachments/assets/2fd9e63e-ee8f-48d0-8029-18967d18aa0e)

## REPLAY Execution

7セグメント表示器を移した動画から表示内容を解析するには `replay.py` を実行する。
パラメータを設定することができ、そのパラメータは実行時に指定することができる。
実行例を以下に示す。

```bash
# 一番シンプルな例
python3 replay.py test/sample.mp4  

# 諸項目を設定する場合
python3 replay.py test/sample.mp4 --num-digits 4 --sampling-sec 5 --num-frames 30 --skip-sec 0 --format csv --save-frame --debug
```

### Arguments

これらの引数は動画のパス以外はオプションなので、含めずに実行することも可能である。

| 引数 | 説明 |  
| --- | --- |  
| test/sample.mp4 | 解析する動画のパス |  
| --num-digits 4 | 7セグメント表示器の桁数 |
| --sampling-sec 5 | 動画をサンプリングする頻度 |  
| --num-frames 30 | 一回のサンプリングで何フレーム取得するか |  
| --skip-sec 0 | 動画の解析を始めるタイミング |  
| --format csv | 出力形式 (json または csv) |
| --save-frame | キャプチャしたフレームを保存するか（保存しない場合、メモリの使用量が増加します） |
| --debug | ログをデバッグモードにする場合は含める |

## Live Execution

カメラを接続して、ライブで解析する場合

```bash
# 短時間解析（6秒）のサンプル
python live.py --device 1 --num-frames 10 --sampling-sec 2 --total-sampling-min 0.1 --format csv --save-frame --debug
```

### Arguments

これらの引数はオプションなので、含めずに実行することも可能である。

| 引数 | 説明 |  
| --- | --- |  
| --device 1 | カメラデバイスの番号 |
| --num-digits 4 | 7セグメント表示器の桁数 |
| --sampling-sec 5 | 動画をサンプリングする頻度 |  
| --num-frames 10 | 一回のサンプリングで何フレーム取得するか |
| --total-sampling-min 1 | サンプリングする合計時間（分） |
| --format csv | 出力形式 (json または csv) |
| --save-frame | キャプチャしたフレームを保存するかどうか |
| --debug | ログをデバッグモードにする場合は含める |

## Program instructions

### File structure

|  ファイル | 説明 |
| --- | --- |  
| `Sichiribe.py` | GUIアプリケーションの起動 |
| `live.py` | 外部カメラからライブ解析 |
| `replay.py` | 動画ファイルから解析 |
| `cores/common.py` | コアな汎用的な機能の関数詰め合わせ |
| `cores/capture.py` | カメラにアクセスする機能 |
| `cores/frameEditor.py` | 動画のフレームに関する機能及び7セグメント表示器の領域選択機能 |
| `cores/detector.py` | 7セグ表示器から数字を推測するプログラムの親クラス |
| `cores/ocr.py` | OCRにて画像から数字を取得するプログラム |
| `cores/cnn.py` | CNNモデルを用いて画像から数字を取得するプログラム |
| `cores/exporter.py` | 取得した結果を任意の形式で出力・保存する機能 |
| `cnn/train.py` | ディープラーニングモデルを学習するプログラム |
| `cnn/conv_keras2tf.py` | Kerasモデルをtflite形式に変換するプログラム |
| `gui/utils/common.py` | GUI用の汎用的な機能の関数詰め合わせ |
| `gui/utils/router.py` | GUIの各ページのルーティング関数 |
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
| `test/something` | テスト用ファイル |

### Process flow configuration

プログラムの処理の流れは以下の通りである。  
GUI内の処理もCLI処理に準拠したフローで実行される

**`live.py`**

1. 指定された引数を元に設定を適用
2. カメラ画角の確認
3. 7セグメント表示器が写っている部分をクロップする
   1. クロップ部分を選択後、確認のウィンドウが立ち上がるが小さい場合があるので注意
   2. 確認ウィンドウがアクティブな状態で y/n のどちらかを押下する
4. クロップした部分を解析して表示内容を読み取る
   1. 設定された頻度でサンプリングを行う
   2. 設定された解析時間を超えた場合にサンプリングを終了
5. 読み取った内容を外部ファイル等に出力する

**`replay.py`**

1. 指定された引数を元に設定を適用
2. 動画の読み込み・フレームの分割
   1. すでに分割済みのファイルがある場合は、再度分割するかの確認がされる
   2. 読み込み動画やサンプリングに関する変数等を変更した場合は再分割するを選択すると良い
3. 7セグメント表示器が写っている部分をクロップする
   1. クロップ部分を選択後、確認のウィンドウが立ち上がるが小さい場合があるので注意
   2. 確認ウィンドウがアクティブな状態で y/n のどちらかを押下する
4. クロップした部分を解析して表示内容を読み取る
5. 読み取った内容を外部ファイル等に出力する

## Model Training

CNNモデルを学習させるためには以下のプログラムを実行する。
参考にしたサイトは [ここ](https://child-programmer.com/seven-segment-digits-ocr-original-model/ "【7セグメント編】オリジナル学習済みモデルの作成方法：連続デジタル数字画像認識プログラミング入門（Python・OpenCV・Keras・CNN）") 。  
上記サイトからデータセットも落としてこれるので、学習前にダウンロードしたあとに zip を解凍してプロジェクトフォルダに追加すること。また、カスタムデータセットを作成した際は、一文字ごとに分割して PNG形式で保存するとプログラムを改変せずに実行できる。  

```bash
# 学習(ファイル内のパラメーターを調整してから実行)
python cnn/train.py

# 軽量モデルに変換
python cnn/conv_keras2tf.py
```

## References

- [子供プログラマー](https://child-programmer.com/seven-segment-digits-ocr-original-model/ "【7セグメント編】オリジナル学習済みモデルの作成方法：連続デジタル数字画像認識プログラミング入門（Python・OpenCV・Keras・CNN）")
- [Github | Kazuhito00/7segment-display-reader](https://github.com/Kazuhito00/7segment-display-reader "Kazuhito00/7segment-display-reader")
