from tensorflow.keras.models import load_model
from tensorflow.lite.TFLiteConverter import from_keras_model

# Kerasモデルの読み込み
model_path = 'model/model_100x100.keras'
model = load_model(model_path)

# TFLite Converterを使って変換
converter = from_keras_model(model)
tflite_model = converter.convert()

# 変換後のモデルを保存
filename = 'model/model_100x100.tflite'
with open(filename, 'wb') as f:
    f.write(tflite_model)

print("Model converted and saved as TFLite format.")
