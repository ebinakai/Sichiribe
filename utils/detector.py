import logging
import cv2
import numpy as np

logger = logging.getLogger("__main__").getChild(__name__)

class Detector():
  def __init__(self):
    pass
    
  def preprocess_binarization(self, image):
    
    gs_threshold = self.get_threshold(image)
    
    # 画像がカラーかどうかを確認し、カラーの場合はグレースケールに変換する
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image = image
  
    # 二値化（しきい値を調整する）
    _, image_bin = cv2.threshold(image, gs_threshold, 255, cv2.THRESH_BINARY_INV)

    # 二値化された画像をカラーに変換
    image_cl = cv2.cvtColor(image_bin, cv2.COLOR_GRAY2BGR)
    
    return image_cl
    
  # k_means法によるしきい値の取得
  def get_threshold(self, image):
    # データの読み込み
    img = image if isinstance(image, np.ndarray) else cv2.imread(image, 0)
    data = img.reshape(-1)

    # ラベルの初期化
    labels = np.random.randint(0,2,data.shape[0])

    # 終了条件
    OPTIMIZE_EPSILON = 1

    m_0_old = -np.inf
    m_1_old = np.inf

    for i in range(1000):
      # それぞれの平均の計算
      m_0 = data[labels==0].mean()
      m_1 = data[labels==1].mean()

      # ラベルの再計算
      labels[np.abs(data-m_0) < np.abs(data-m_1)] = 0
      labels[np.abs(data-m_0) >= np.abs(data-m_1)] = 1
      
      # 終了条件
      if np.abs(m_0 - m_0_old) + np.abs(m_1 - m_1_old) < OPTIMIZE_EPSILON:
        break

      m_0_old = m_0
      m_1_old = m_1

    # 初期値によって，クラスが変化するため上界の小さい方を採用
    gs_threshold = np.minimum(data[labels==0].max(),data[labels==1].max())
    logger.debug("Threshold: %s", gs_threshold)
    return gs_threshold
  
  # 検出失敗率を取得
  def get_failed_rate(self, data: list):
    if len(data) == 0:
      return 1.0
    
    failed = data.count(None)
    total = len(data)
    return failed / total if total > 0 else 0