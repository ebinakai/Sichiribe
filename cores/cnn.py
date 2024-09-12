from cores.cnn_core import CNNCore
import os
import logging
import cv2 
import numpy as np
from pathlib import Path

# TensorFlow と h5py のログを無効にする
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('h5py').setLevel(logging.ERROR)

class CNN(CNNCore):
  def __init__(self, num_digits):
    super().__init__(num_digits)
    self.logger = logging.getLogger("__main__").getChild(__name__)
    
    # 学習済みモデルの絶対パスを取得
    current_dir = Path(__file__).resolve().parent
    model_path = current_dir / '..' / 'model' / 'model_100x100.keras'
    model_path = model_path.resolve()
    self.model_path = str(model_path)
  
  def load(self):
    if self.model is None:
      from tensorflow.keras.models import load_model
      self.model = load_model(self.model_path)
    self.logger.info("CNN Model loaded.")
    
  # 画像から数字を推論
  def inference_7seg_classifier(self, image: np.ndarray) -> list:
    # 各桁を一度に処理できるように画像を準備
    preprocessed_images = self.preprocess_image(image)
    
    # モデルに一度に入力して推論
    predictions = self.model.predict(np.array(preprocessed_images), verbose=0) # verbose=0: ログ出力を抑制

    # 結果を処理
    argmax_indices = predictions.argmax(axis=1)  # 各行に対して最大値のインデックスを取得

    return argmax_indices
  