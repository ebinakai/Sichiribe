# 7Segment detector

## Description

7セグメント表示器が示したデータをシリアル等で読み取れない場合のために、メータの表示状態を録画し、そこからデータを取り出すためのプログラムを作成した。処理の流れは以下の通りである。

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

# 実行
python3 main.py 解析する動画のファイルパス
```

## Execution

7セグメント表示器を移した動画から表示内容を解析するには `main.py` を実行する。
パラメータを設定することができ、そのパラメータは実行時に指定することができる。
実行例を以下に示す。

```bash
python3 main.py test/sample.mp4 --sampling-sec 5 --num-frames 30 --skip-sec 0 --format csv --debug
```

### Arguments

これらの引数は動画のパス以外はオプションなので、含めずに実行することも可能である。

| 引数 | 説明 |  
| --- | --- |  
| test/sample.mp4 | 解析する動画のパス |  
| --sampling-sec 5 | 動画をサンプリングする頻度 |  
| --num-frames 30 | 一回のサンプリングで何フレーム取得するか |  
| --skip-sec 0 | 動画の解析を始めるタイミング |  
| --format csv | 出力フォーマット(csv, json) |  
| --debug | ログをデバッグモードにする場合は含める |

## Program instructions

### File structure

```bash
├── main.py
└── utils
    ├── common.py
    ├── frameEditor.py
    ├── regionSelector.py
    ├── detector.py
    └── exporter.py
```

|  ファイル | 説明 |
| --- | --- |  
| `main.py` | 実行ファイル |
| `common.py` | 汎用的な機能の関数 |
| `frameEditor.py` |  動画のフレームに関する機能 |
| `regionSelector.py` | 画像内の7セグ表示器の座標を選択する機能 |
| `detector.py` | 7セグ表示器から数字を推測するプログラム |
| `exporter.py` | 取得した結果を任意の形式で出力・保存する部分 |

### Process flow configuration

1. 指定された引数を元に設定を適用
2. 動画の読み込み・フレームの分割
   1. すでに分割済みのファイルがある場合は、再度分割するかの確認がされる
   2. 読み込み動画やサンプリングに関する変数等を変更した場合は再分割するを選択すると良い
3. 7セグメント表示器が写っている部分をクロップする
   1. クロップ部分を選択後、確認のウィンドウが立ち上がるが小さい場合があるので注意
   2. 確認ウィンドウがアクティブな状態で y/n のどちらかを押下する
4. クロップした部分を解析して表示内容を読み取る
5. 読み取った内容を外部ファイル等に出力する
