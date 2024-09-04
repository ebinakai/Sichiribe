import logging
import cv2
import numpy as np

class Detector():
  def __init__(self):
    self.logger = logging.getLogger("__main__").getChild(__name__)
  
  def load_image(self, image):
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
      
    return image_gs
    
  def preprocess_binarization(self, image, output_grayscale=False):
    # 画像がカラーかどうかを確認し、カラーの場合はグレースケールに変換する
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image = image

    # しきい値の取得
    gs_threshold = self.get_threshold(image)
  
    # 二値化（しきい値を調整する）
    _, image_bin = cv2.threshold(image, gs_threshold, 255, cv2.THRESH_BINARY_INV)

    # グレースケール画像を返す場合
    if output_grayscale:
        return image_bin

    # 二値化された画像をカラーに変換
    image_cl = cv2.cvtColor(image_bin, cv2.COLOR_GRAY2BGR)
    
    return image_cl
    
  # k_means法によるしきい値の取得
  def get_threshold(self, image):
      # データの読み込み
      img = image if isinstance(image, np.ndarray) else cv2.imread(image, 0)
      data = img.reshape(-1)

      # データの中央値で初期ラベルを設定
      median_value = np.median(data)
      labels = np.where(data < median_value, 0, 1)

      # 終了条件
      OPTIMIZE_EPSILON = 1

      m_0_old = -np.inf
      m_1_old = np.inf

      for i in range(1000):
          # ラベルが空でないことを確認
          if len(data[labels == 0]) == 0 or len(data[labels == 1]) == 0:
              raise ValueError("One of the labels has no data points. Check the initial label assignment.")

          # それぞれの平均の計算
          m_0 = data[labels == 0].mean()
          m_1 = data[labels == 1].mean()

          # ラベルの再計算
          labels[np.abs(data - m_0) < np.abs(data - m_1)] = 0
          labels[np.abs(data - m_0) >= np.abs(data - m_1)] = 1

          # 終了条件
          if np.abs(m_0 - m_0_old) + np.abs(m_1 - m_1_old) < OPTIMIZE_EPSILON:
              break

          m_0_old = m_0
          m_1_old = m_1

      # クラスが変化する可能性を考慮して上界の小さい方を採用
      gs_threshold = np.minimum(data[labels == 0].max(), data[labels == 1].max())
      return gs_threshold
  
  # 検出失敗率を取得
  def get_failed_rate(self, data: list, correct_value: float) -> float:
    total = len(data)
    if total == 0:
      return 1.0
    
    correct = data.count(correct_value)
    failed = total - correct
    return failed / total if total > 0 else 0
