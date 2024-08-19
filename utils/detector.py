import easyocr
import logging
import cv2
import statistics

logger = logging.getLogger("__main__").getChild(__name__)

class Detector():
  def __init__(self, model='ocr'):
    
    # 画像処理モデルを選択
    if model == 'ocr':
      self.reader = easyocr.Reader(['en'])
      self.detector = self.detect_ocr
    else:
      logger.error("Model not found.")
      
    logger.debug("Detector loaded.")
  
  def detect(self, image):
    # リスト化する
    if isinstance(image, str):
      image = [image]
      
    result = [self.detector(img) for img in image]
    failed_rate = self.get_failed_rate(result)
    return result, failed_rate

  def detect_ocr(self, images, result_idx=0):
    # [引数] images: ファイルパスまたはnumpy画像データまたはそれを含んだリスト
    
    detect_nums = []
    
    # リスト化する
    if not isinstance(images, list):
      images = [images]
    
    for image in images:
      
      if isinstance(image, str):
        # 画像の読み込み
        image_gs = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        
      # 画像が正常に読み込まれたか確認
      if image_gs is None:
        logger.error("Error: Could not read image file.")
        continue

      # 二値化（しきい値を調整する）
      _, image_bin = cv2.threshold(image_gs, 90, 255, cv2.THRESH_BINARY_INV)

      # 二値化された画像をカラーに変換
      image_cl = cv2.cvtColor(image_bin, cv2.COLOR_GRAY2BGR)  
      
      # ocrでテキストを検出
      result = self.reader.readtext(image_cl)

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
      
    # 最頻値を取得
    detect_num = statistics.mode(detect_nums) if len(detect_nums) > 0 else None
      
    logger.info("Detected: %s", detect_num)
    return detect_num
  
  # 検出失敗率を取得
  def get_failed_rate(self, data: list):
    failed = data.count(None)
    total = len(data)
    return failed / total if total > 0 else 0