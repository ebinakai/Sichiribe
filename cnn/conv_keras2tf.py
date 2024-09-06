import tensorflow as tf

# Kerasモデルの読み込み
model_path = 'model/model_100x100.keras'
model = tf.keras.models.load_model(model_path)

# TFLite Converterを使って変換
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# 変換後のモデルを保存
filename = 'model/model_100x100.tflite'
with open(filename, 'wb') as f:
    f.write(tflite_model)

print("Model converted and saved as TFLite format.")
