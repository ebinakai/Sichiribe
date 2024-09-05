from cores.detector import Detector
import os
import logging
import cv2 
import numpy as np

# TensorFlow と h5py のログを無効にする
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('h5py').setLevel(logging.ERROR)

class CNN(Detector):
  def __init__(self, num_digits):
    self.num_digits = num_digits
    
    self.logger = logging.getLogger("__main__").getChild(__name__)
    
    # 画像の各種設定
    self.folder = np.array(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ''])  # 空白の表示に対応させるため、blankのところを「' '」で空白に設定
    self.image_width = 100        # 使用する学習済みモデルと同じwidth（横幅）を指定
    self.image_height = 100       # 使用する学習済みモデルと同じheight（縦の高さ）を指定
    self.color_setting = 1        # 学習済みモデルと同じ画像のカラー設定にする。モノクロ・グレースケールの場合は「1」。カラーの場合は「3」
    self.cv2_color_setting = 0    # 学習済みモデルと同じ画像のカラー設定にする。cv2.imreadではモノクロ・グレースケールの場合は「0」。カラーの場合は「1」
    self.crop_size = 100          # 画像をトリミングするサイズ
    self.model = None
    
  def load(self):
    if self.model is None:
      from tensorflow.keras.models import load_model
      self.model = load_model('model/model_100x100.keras')
    self.logger.info("CNN Model loaded.")
  
  # 画像から数字を推論
  def inference_7seg_classifier(self, image: np.ndarray) -> list:
    # 各桁を一度に処理できるように画像を準備
    images = []
    for index in range(self.num_digits):
      # 画像を一桁にトリミング
      img = image[0:self.crop_size, index * self.crop_size:(index + 1) * self.crop_size]
      img = cv2.resize(img, (self.image_width, self.image_height))
      img_ = img.reshape(self.image_width, self.image_height, self.color_setting).astype('float32') / 255
      images.append(img_)

    # モデルに一度に入力して推論
    predictions = self.model.predict(np.array(images), verbose=0) # verbose=0: ログ出力を抑制

    # 結果を処理
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
