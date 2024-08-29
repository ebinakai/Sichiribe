from utils.detector import Detector

import easyocr
import logging
import cv2
import statistics
import numpy as np

logger = logging.getLogger("__main__").getChild(__name__)

class OCR(Detector):
  def __init__(self):
    self.reader = easyocr.Reader(['en'])
  
  def detect(self, images, result_idx=0):
    # [引数] images: ファイルパスまたはnumpy画像データまたはそれを含んだリスト
    # [引数] result_idx: OCRの結果のうち、何番目の結果を取得するか（デフォルトは0）
    
    detect_nums = []
    
    # リスト化する
    if not isinstance(images, list):
      images = [images]
    
    for i, image in enumerate(images):
      
      # imageがNumPy配列（すでにロードされた画像）かどうかを確認
      if isinstance(image, np.ndarray):
        # グレースケール画像に変換（もしすでにグレースケールでなければ）
        if len(image.shape) == 3:  # 3チャンネル（カラー画像）の場合
          image_gs = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
          image_gs = image  # すでにグレースケールの場合
      else:
        # 画像ファイルをグレースケールで読み込む
        image_gs = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        
      # 画像が正常に読み込まれたか確認
      if image_gs is None:
        logger.error("Error: Could not read image file.")
        continue

      # 二値化処理
      image_bin = self.preprocess_binarization(image_gs)
      
      # ocrでテキストを検出
      result = self.reader.readtext(image_bin)

      # テキストが検出されなかった場合 
      if len(result) == 0:
        logger.debug("No text detected.")
        continue
      
      # 検出されたテキストを数値に変換
      try: 
        detect_txt = result[result_idx][1]
        detect_nums.append(float(detect_txt))  #なんかここでリストに入っていない
        
      except:
        logger.debug("Could not convert detected text to number.")
        continue
      
    logger.debug("Detected numbers: %s", detect_nums)

    # 最頻値を取得
    detect_num = statistics.mode(detect_nums) if len(detect_nums) > 0 else None
    logger.debug("Detected number: %s", detect_num)
    
    # 誤検知率を取得
    failed_rate = self.get_failed_rate(detect_nums)
    
    return detect_num, failed_rate