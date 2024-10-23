#!/bin/bash

set -ex

LOGFILE="sichiribe_install_$(date '+%Y-%m-%d_%H-%M-%S').log"
exec > >(tee -i "$LOGFILE") 2>&1

ARCH=$(uname -m)
cd ~

# デフォルトのPythonバイナリは `python` とするが、`PYTHON` が指定されていればそれを使用
PYTHON_BIN=${PYTHON:-python}

# tensorflow-src ディレクトリが存在しない場合にクローン
if [ ! -d "tensorflow-src" ]; then
    git clone https://github.com/tensorflow/tensorflow tensorflow-src
fi
cd tensorflow-src

# ビルド環境を作成
$PYTHON_BIN -m venv env 
source ./env/bin/activate
pip install numpy wheel pybind11

# アーキテクチャに基づいて対応する CPU フラグを設定
if [ "$ARCH" == "arm64" ]; then
    CPU_FLAG="darwin_arm64"
elif [ "$ARCH" == "x86_64" ]; then
    CPU_FLAG="darwin_x86_64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

# CUSTOM_BAZEL_FLAGS にアーキテクチャに基づいた CPU フラグを含めて、MacOS用にビルドを実行
CI_BUILD_PYTHON=$PYTHON_BIN CUSTOM_BAZEL_FLAGS="--config=macos --cpu=$CPU_FLAG -c opt" tensorflow/lite/tools/pip_package/build_pip_package_with_bazel.sh

# ビルド済みwhlパッケージを確認
WHL_FILE=$(ls ~/tensorflow-src/tensorflow/lite/tools/pip_package/gen/tflite_pip/$PYTHON_BIN/dist/*.whl)

# ビルド環境をから抜ける
deactivate

# アプリケーションのビルド環境を作成
cd ~
rm -rf sichiribe-src
git clone https://github.com/EbinaKai/Sichiribe.git sichiribe-src
cd sichiribe-src
git checkout feature/app/macos
$PYTHON_BIN -m venv env
source ./env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install $WHL_FILE
pip install nuitka zstandard orderedset imageio

# モデルファイルをダウンロードするURL
MODEL_URL="https://github.com/EbinaKai/Sichiribe/releases/download/v0.1.2/model_100x100.tflite"
MODEL_DIR="./model"
MODEL_FILE="$MODEL_DIR/model_100x100.tflite"

# モデルファイルをダウンロード
mkdir -p "$MODEL_DIR"
curl -L -o "$MODEL_FILE" "$MODEL_URL"

# ビルド
BILD_SCRIPT="./script/build.sh"
if [ -f "$BILD_SCRIPT" ]; then
    bash "$BILD_SCRIPT"
else
    echo "ビルドスクリプトが見つかりません。"
fi