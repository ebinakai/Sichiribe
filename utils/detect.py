import easyocr
import cv2
import logging

# 文字の選択
reader = easyocr.Reader(['en'])
logger = logging.getLogger("__main__").getChild(__name__)

# 画像表示用関数
def showImage(image, message="image showing"):
  cv2.imshow(message, image)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

def detect_ocr(img, result_idx=0):
  result = reader.readtext(img)

  # テキストが検出されなかった場合 
  if len(result) == 0:
    logger.error("No text detected.")
    return
  
  # 検出されたテキストを数値に変換
  try: 
    detect_txt = result[result_idx][1]
    detect_num = float(detect_txt)
    
  except:
    logger.error("Could not convert detected text to number.")
    return
  
  return detect_num