from utils.detector import Detector
import os
import logging
import statistics
import cv2 
import numpy as np

# TensorFlow と h5py のログを無効にする
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('h5py').setLevel(logging.ERROR)

from tensorflow.keras.models import load_model
from utils.detector import Detector

logger = logging.getLogger("__main__").getChild(__name__)

class CNN(Detector):
  def __init__(self, num_digits):
    self.num_digits = num_digits
    
    # 画像の各種設定
    self.folder = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '']  # 空白の表示に対応させるため、blankのところを「' '」で空白に設定
    self.image_width = 28        # 使用する学習済みモデルと同じwidth（横幅）を指定
    self.image_height = 28       # 使用する学習済みモデルと同じheight（縦の高さ）を指定
    self.color_setting = 1          # 学習済みモデルと同じ画像のカラー設定にする。モノクロ・グレースケールの場合は「1」。カラーの場合は「3」
    self.cv2_color_setting = 0   # 学習済みモデルと同じ画像のカラー設定にする。cv2.imreadではモノクロ・グレースケールの場合は「0」。カラーの場合は「1」
    self.crop_size = 100
    self.model = load_model('model/model_best.keras')
  
  # 画像から数字を推論
  def inference_7seg_classifier(self, image):

    # 各桁を一度に処理できるように画像を準備
    images = []
    for index in range(self.num_digits):
      # 画像を一桁にトリミング
      img = image[0:100, index * 100:(index + 1) * 100]
      img = cv2.resize(img, (self.image_width, self.image_height))
      img_ = img.reshape(self.image_width, self.image_height, self.color_setting).astype('float32') / 255
      images.append(img_)

    # モデルに一度に入力して推論
    predictions = self.model.predict(np.array(images), verbose=0) # verbose=0: ログ出力を抑制

    # 結果を処理
    results = [ self.folder[prediction.argmax()] for prediction in predictions ]

    # 結合する
    results_str = ''.join(results)
    
    return int(results_str) if results_str != '' else None
  
  def detect(self, images):
    # [引数] images: ファイルパスまたはnumpy画像データまたはそれを含んだリスト
    
    detect_nums = []
    
    # リスト化する
    if not isinstance(images, list):
      images = [images]
    
    for i, image in enumerate(images):
      
      # 画像を読み込む
      image_gs = self.load_image(image)
        
      # 画像が正常に読み込まれたか確認
      if image_gs is None:
        logger.error("Error: Could not read image file.")
        continue
      
      # 画像のリサイズ
      image_gs = cv2.resize(image_gs, (self.crop_size * self.num_digits,  self.crop_size))

      # 二値化処理
      image_bin = self.preprocess_binarization(image_gs, output_grayscale=True)
      
      # cnnで数字を検出
      detect_num = self.inference_7seg_classifier(image_bin)

      # 数字が検出されなかった場合 
      if detect_num == '':
        logger.debug("No number detected.")
        continue
      
      detect_nums.append(detect_num)
      
    logger.debug("Detected numbers: %s", detect_nums)

    # 最頻値を取得
    detect_num = statistics.mode(detect_nums) if len(detect_nums) > 0 else None
    logger.debug("Detected number: %s", detect_num)
    
    # 誤検知率を取得
    failed_rate = self.get_failed_rate(detect_nums)
    
    return detect_num, failed_rate
  