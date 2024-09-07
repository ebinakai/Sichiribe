from cores.cnn import CNN
import os
import logging
import cv2 
import numpy as np

# TensorFlow と h5py のログを無効にする
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('h5py').setLevel(logging.ERROR)

class CNNLite(CNN):
  def __init__(self, num_digits):
    super().__init__(num_digits)
    self.logger = logging.getLogger('__main__').getChild(__name__)
    self.model_path = 'model/model_100x100.tflite'

  def load(self):
    if self.model is None:
      from tensorflow import lite as tflite
      # TensorFlow Lite モデルの読み込み
      self.model = tflite.Interpreter(model_path=self.model_path)
      self.model.allocate_tensors()
      self.input_details = self.model.get_input_details()
      self.output_details = self.model.get_output_details()
      self.logger.info("TFLite Model loaded.")
  
  # 画像から数字を推論
  def inference_7seg_classifier(self, image: np.ndarray) -> list:
    # 各桁に分割
    preprocessed_images = self.preprocess_image(image)
    
    predictions = []
    for preprocessed_image in preprocessed_images:
      img_ = np.expand_dims(preprocessed_image, axis=0)  # バッチサイズの次元を追加
      
      # 推論
      self.model.set_tensor(self.input_details[0]['index'], img_)
      self.model.invoke()
      output_data = self.model.get_tensor(self.output_details[0]['index'])
      predictions.append(output_data)
      
    # 結果を処理
    predictions = np.array(predictions).squeeze()  # (num_digits, num_classes) 形状に変換
    argmax_indices = predictions.argmax(axis=1)  # 各行に対して最大値のインデックスを取得

    return argmax_indices
  
  def detect(self, images, binarize_th=None) -> tuple[int, float]:
    # [引数] images: ファイルパスまたはnumpy画像データまたはそれを含んだリスト
    if self.model is None:
      self.logger.error("CNN Model unloaded.")
    
    results = np.zeros((0, self.num_digits))
    
    # リスト化する
    if not isinstance(images, list):
      images = [images]
    
    for i, image in enumerate(images):
      
      # 画像を読み込む
      image_gs = self.load_image(image)
        
      # 画像が正常に読み込まれたか確認
      if image_gs is None:
        self.logger.error("Error: Could not read image file.")
        continue
      
      # 画像のリサイズ
      image_gs = cv2.resize(image_gs, (self.crop_size * self.num_digits,  self.crop_size))

      # 二値化処理
      image_bin = self.preprocess_binarization(image_gs, binarize_th, output_grayscale=True)
      
      # cnnで数字を検出
      argmax_indices = self.inference_7seg_classifier(image_bin)

      results = np.vstack([results, argmax_indices])
    
    # 最頻値を取得
    result, errors_per_digit = self.find_mode_per_column_np(results)
    
    # 最後にラベルに対応させる
    result_digits = self.folder[result.astype(int)]
    result_int = int(''.join(result_digits)) if len(result_digits) > 0 else 0
    
    # 誤検知率を取得
    failed_rate = np.mean(errors_per_digit)
    
    self.logger.debug("Detected label: %s", result)
    self.logger.debug("Error: %s", failed_rate)
    return result_int, failed_rate
  
  def find_mode_per_column_np(self, predictions: np.ndarray) -> list[np.ndarray, np.ndarray]:
    result = []
    errors_per_digit = []
    for i in range(predictions.shape[1]):  # 各桁に対して
      digit_predictions = predictions[:, i]  # 各列を抽出
      
      # np.unique を使って最頻値を取得
      values, counts = np.unique(digit_predictions, return_counts=True)
      mode_value = values[np.argmax(counts)]  # 最も頻出する値を取得

      # 誤検知率を計算
      incorrect_predictions = np.sum(digit_predictions != mode_value)
      error_rate = incorrect_predictions / len(digit_predictions)
      
      result.append(mode_value)
      errors_per_digit.append(error_rate)
    return np.array(result), np.array(errors_per_digit)
