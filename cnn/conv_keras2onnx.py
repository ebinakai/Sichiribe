import tensorflow as tf
from tensorflow.keras.models import load_model
import subprocess, shutil

# Kerasモデルのロード
model_path = 'model/model_100x100.keras'
model = load_model(model_path)

# SavedModel形式で保存
saved_model_path = 'model/model_100x100'
tf.saved_model.save(model, saved_model_path)

# ONNX形式に変換
onnx_model_path = 'model/model_100x100.onnx'
subprocess.run(['python', '-m', 'tf2onnx.convert', '--saved-model', saved_model_path, '--output', onnx_model_path], check=True)

# SavedModel形式のフォルダを削除
shutil.rmtree(saved_model_path)