# Pythonファイルのアプリ化について

私はプログラムをExe化、つまりアプリ化することを目指した。  
最初に、`Pyintallery` というライブラリを使用しよう考えた。しかし`Pyinstaller`は、Pythonのファイルをただ、バンドル化しただけで、以下の欠点があった。

- 実行速度が遅い
- アプリサイズが肥大化する
- ウイルスアプリと認識される可能性がある

そのため、今回は `nuitka` というライブラリを用いることにした。  
このライブラリは、Pythonファイルを一度C言語でコンパイルし直すため、オーバーヘッドが少なく、実行速度が早いという特徴がある。唯一の欠点はビルドに時間がかかるというぐらいだ。

## PySide6 について

アプリを配布するにあたって、サイズを可能な限り小さくすることを試みた。  
サイズが大きいライブラリの一つが、GUI用のライブラリの `PySide6` だった。必要な機能だけを含む `PySide6_Essentials` に切り替えることで、サイズが約1/2になった。

```bash
pip uninstall PySide6
pip install PySide6_Essentials
```

## tflite-runtime について

アプリサイズの圧縮において一番の問題は `tensorflow` だった。ライブラリのフルサイズが1GBを超える。アプリ内では推論機能のみを用い、学習は行わないため、どうにか不要な機能を取り除きたい。  

まず、使用する学習済モデルを `.keras` から `.tflite` 形式に変換し、`tensorflow lite` を用いることで、モデルサイズを1/3ほどに圧縮できた。  
しかし、問題は推論機能のみが含まれる `tflite-runtime` は、エッジデバイス向けに linux 向けのビルドしか配布されていない。その他のプラットフォーム用には自分でビルドする必要があった。  
詳しい内容に方法については、 [公式サイト](https://www.tensorflow.org/lite/guide/build_cmake_pip?hl=ja) を参照してほしいが、とりあえず簡単に流れを説明しよう。  

### tflite-runtime のビルド

cmakeやbazel等のビルドツールを事前にインストールしておくこと。上記の公式サイトでその方法を確認することができる。  
また理由は不明だが、私の環境ではcmakeでのビルドは失敗したのでbazelでのビルドを行った。

```bash
# tensorflowのリポジトリを取得
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow 

# ビルド環境を作成
python -m venv env 
source ./env/bin/activate
pip install --upgrade pip
pip install pybind11 wheel

# MacOS用にビルドを実行
CUSTOM_BAZEL_FLAGS=--macos_cpus=arm64 PYTHON=[クローンしたフォルダ]/env/bin/python CI_BUILD_PYTHON=[クローンしたフォルダ]/env/bin/python tensorflow/lite/tools/pip_package/build_pip_package_with_bazel.sh
```

すると、以下のパスにwhlファイルが作成される。  

`tensorflow/lite/tools/pip_package/gen/tflite_pip/python3/dist/`  

**そのファイルをコピーしてプロジェクトフォルダのexternalsにコピーして以下のコマンドを実行すると**、ビルドした `tflite` がインストールされる。

```bash
pip install externals/ビルドされたファイル名.whl
```

## アプリのビルド

次にアプリのビルドに移る。ビルドする前に、きちんとライブラリと必要なモデル等をすべて認識し、実行可能かどうかの確認を忘れずに。  

Nuitkaを使ってビルドするには以下のライブラリが必要なのでインストールする。  

```bash
pip install nuitka zstandard orderedset
```

また、Macosへの対応は完全ではないためか、アプリ名の指定が効かなかったので、`app.py` を `Sichiribe.py` にリネームした。
ビルド用のスクリプトは `make.sh` である。brewでインストールしたライブラリ用の変数も含むが、各自必要なら編集して実行してほしい。

```bash
source make.sh
```

以上。
