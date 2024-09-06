import logging
# Pillow と matplotlib のログを無効にする
logging.getLogger('PIL').setLevel(logging.ERROR)
logging.getLogger('matplotlib').setLevel(logging.ERROR)

from PySide6.QtGui import QImage
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import cv2
import io


def convert_cv_to_qimage(cv_img: np.ndarray) -> QImage:
    """Convert a CV image (numpy array) to QImage."""
    height, width, channels = cv_img.shape
    
    # 画像が BGR 形式の場合
    if channels == 3:
        bytes_per_line = 3 * width
        qimage = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        return qimage.rgbSwapped()  # OpenCV uses BGR, QImage expects RGB

    # 画像が RGBA 形式の場合
    elif channels == 4:
        bytes_per_line = 4 * width
        qimage = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888)
        return qimage

    else:
        raise ValueError("Unsupported number of channels: {}".format(channels))

  # 画像を規定の大きさにリサイズ
def resize_image(image: np.ndarray, target_width: int, target_height: int) -> tuple[np.ndarray, float]:
  
  height, width = image.shape[:2]
  resize_scale_width = float(target_width / width)
  resize_scale_height = float(target_height / height)
  aspect_ratio = height / width
  
  # リサイズスケールの決定
  if resize_scale_width < resize_scale_height:
    resize_scale = resize_scale_width
    target_height = int(target_width * aspect_ratio)
  else:
    resize_scale = resize_scale_height
    target_width = int(target_height / aspect_ratio)
  
  resized_image = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)
  
  return resized_image, resize_scale

def gen_graph(x_val, y_val1, y_val2, title, xlabel, ylabel1, ylabel2, dark_theme=False) -> np.ndarray: 
  # ダークテーマの設定
  if dark_theme:
    plt.style.use('dark_background')
    title_color = 'white'
    label_color = 'white'
    bg_color = '#323232'
  else:
    title_color = 'black'
    label_color = 'black'
    bg_color = '#ECECEC'

  # FigureとAxesを作成
  fig, ax1 = plt.subplots()

  # 最初のデータセットをプロット
  line1, = ax1.plot(x_val, y_val1, marker='o', color='royalblue', label=ylabel1)
  ax1.set_xlabel(xlabel, color=label_color)
  ax1.tick_params(axis='y', labelcolor='royalblue')
  ax1.set_ylim(-0.2, 1)

  # 右側のY軸を作成して別のデータセットをプロット
  ax2 = ax1.twinx()
  line2, = ax2.plot(x_val, y_val2, marker='s', color='tomato', label=ylabel2)
  ax2.tick_params(axis='y', labelcolor='tomato')

  # レジェンドを追加
  lines = [line1, line2]
  ax1.legend(lines, [line.get_label() for line in lines], loc='upper left')

  # タイトルを設定
  plt.title(title, color=title_color)

  # 表示するラベルの数を制限
  max_labels = 5
  step = max(1, len(x_val) // max_labels)  # 指定数のラベルが表示されるようにステップを計算
  plt.xticks(ticks=range(0, len(x_val), step), labels=[x_val[i] for i in range(0, len(x_val), step)])

  # Figureオブジェクトを取得
  fig = plt.gcf()
  
  # 背景色の設定
  fig.patch.set_facecolor(bg_color)
  fig.patch.set_edgecolor(bg_color)
  plt.gca().set_facecolor(bg_color)

  # FigureをCanvasに描画
  buf = io.BytesIO()
  fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, facecolor=bg_color)

  buf.seek(0)

  # PILで画像を開き、NumPy配列に変換
  image = Image.open(buf)
  image_np = np.array(image)

  # 後処理: バッファを閉じる
  buf.close()

  # 元のFigureを閉じる
  plt.close(fig)
  
  return image_np
