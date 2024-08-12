import cv2
import logging
import os

# ロガーの設定
logger = logging.getLogger("__main__").getChild(__name__)

def frameDevide(video_path, output_dir = 'frames'):
  # 動画ファイルのパス
  video_path = 'contents/video_cropped.mp4'

  # フレーム保存用のディレクトリ
  os.makedirs(output_dir, exist_ok=True)

  # 動画の読み込み
  cap = cv2.VideoCapture(video_path)

  # 動画が正常に読み込まれたか確認
  if not cap.isOpened():
    logger.error("Error: Could not open video file.")
    return

  frame_count = 0
  frame_paths = []
  while True:
    # フレームの読み込み
    ret, frame = cap.read()
    if not ret:
        break

    # フレームの保存
    frame_filename = os.path.join(output_dir, f'frame_{frame_count:04d}.jpg')
    cv2.imwrite(frame_filename, frame)
    
    # フレームカウントの更新
    frame_count += 1
    frame_paths.append(frame_filename)

  # リソースの解放
  cap.release()
  logger.info(f"Extracted {frame_count} frames and saved to '{output_dir}' directory.")
  
  return frame_paths

# 切り出したフレームをトリミング
def frameCrop(image_paths, crop_size, output_dir="frame_cropped", gray_scale=False):
  
  # image_pathsがリストでなければリストに変換
  if isinstance(image_paths, str):
    image_paths = [image_paths]

  # 出力ディレクトリの作成
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  
  for image_path in image_paths:
  
    # 画像の読み込み
    if gray_scale:
      image_gs = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
      # 二値化（しきい値を調整する）
      _, image_bin = cv2.threshold(image_gs, 90, 255, cv2.THRESH_BINARY_INV)

      # 二値化された画像をカラーに変換
      image = cv2.cvtColor(image_bin, cv2.COLOR_GRAY2BGR)
    
    else: 
      image = cv2.imread(image_path)     
      
    # 画像が正常に読み込まれたか確認
    if image is None:
      logger.error("Error: Could not read image file.")
      return

    start_x, start_y, end_x, end_y = crop_size

    # 画像の切り取り
    cropped_image = image[start_y:end_y, start_x:end_x]

    # 切り取った画像の保存
    os.makedirs(output_dir, exist_ok=True)
    cropped_image_path = os.path.join(output_dir, os.path.basename(image_path))
    cv2.imwrite(cropped_image_path, cropped_image)

    logger.info(f"Image cropped and saved to '{cropped_image_path}'.")

    return cropped_image_path
  