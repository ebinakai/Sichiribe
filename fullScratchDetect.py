import cv2
import logging
from logging import getLogger

# ロガーの設定
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)
logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)


# 画像表示用関数
def showImage(image, message="image showing"):
  cv2.imshow(message, image)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

# 画像の読み込み
file_path = "frame_cropped/frame_0000.jpg"
image_gs = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

# 二値化（しきい値を調整する）
_, image_bin = cv2.threshold(image_gs, 90, 255, cv2.THRESH_BINARY_INV)

# 二値化された画像をカラーに変換
image_cl = cv2.cvtColor(image_bin, cv2.COLOR_GRAY2BGR)

# 画像中の輪郭を検出
contours, _ = cv2.findContours(image_gs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 輪郭を左から右にソート
contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

# 桁数の確認（輪郭の数を数える）
num_digits = len(contours)
print(num_digits)

# 検出された輪郭を使って各桁を個別に分割
digit_images = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    digit_images.append(image_cl[y:y+h, x:x+w])

# バウンディングボックスを描画
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(image_cl, (x, y), (x+w, y+h), (0, 0, 255), 10)

# 画像を表示する
showImage(image_cl, "7 Segment Display with Bounding Boxes")