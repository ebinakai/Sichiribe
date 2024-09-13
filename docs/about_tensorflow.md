# Tensorflow について

[Tensorflow](https://github.com/tensorflow/tensorflow) はGoogleが開発する機械学習を行うためのライブラリで、モデルの構築や学習及び推論を行うことができる。  

Tensorflowには、軽量版のTensorflow-Liteが含まれており、これは性能の低いエッジデバイスで機械学習モデルを実行するために最適化された、推論のみを行うライブラリです。Tensorflow-Liteは専用のモデルが必要になるため、フルバージョンのTensorflowで学習させたモデルを変換する必要がある。  

フルバージョンのTensorflowをインストールするには以下のコマンドを実行する。TensorflowにはTensorflow-Liteが含まれており、Lite用のモデルも実行することができる。

```python
pip install tensorflow
```

Tensorflow-Liteのみをインストールするには以下のコマンドを実行する。  
tflite-runtimeはLinux用のビルドしか用意されていないので、Windows・Macで使用する際は自分でビルドする必要がある。  

```python
pip install tflite-runtime
```

## tflite-runtimeのビルド

手順を示すが、詳しいことは [公式サイト](https://www.tensorflow.org/lite/guide/build_cmake_pip?hl=ja) を参照してほしい。

まず、ビルド環境を示す。

```bash
Hardware:

    Hardware Overview:

      Model Name: MacBook Pro
      Model Identifier: MacBookPro18,3
      Model Number: Z15J00224J/A
      Chip: Apple M1 Pro
      Total Number of Cores: 8 (6 performance and 2 efficiency)
      Memory: 16 GB
      System Firmware Version: 10151.101.3
      OS Loader Version: 10151.101.3
      Activation Lock Status: Enabled
```

ビルドを実行実行。

```bash
cd ~
git clone https://github.com/tensorflow/tensorflow tensorflow-src
cd tensorflow-src

# ビルド環境を作成
python -m venv env 
source ./env/bin/activate
pip install numpy wheel pybind11

# MacOS用にビルドを実行
CUSTOM_BAZEL_FLAGS=--macos_cpus=arm64 \
tensorflow/lite/tools/pip_package/build_pip_package_with_bazel.sh

# ビルド済みwhlパッケージを確認
ls tensorflow/lite/tools/pip_package/gen/tflite_pip/python3/dist
```

最終的に `*.whl` ファイルが生成されていればビルド成功だ。  
そのwhlパッケージをプロジェクトフォルダの直下に `externals` とかのフォルダを作成してその中にコピーする。`tflite-runtime.whl`などとリネームすると良い。インストールするには以下のコマンドを実行する。

```python
pip install externals/tflite-runtime.whl
```

以上。
