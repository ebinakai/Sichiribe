import os, sys

# 現在のファイルのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))

# プロジェクトのルートディレクトリを追加
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(project_root)

# utils ディレクトリを追加
sys.path.append(current_dir)

import cv2
import logging
import glob
import numpy as np
from datetime import timedelta
from utils.common import ask_user_confirmation, clear_directory

# ロガーの設定
logger = logging.getLogger("__main__").getChild(__name__)

class FrameEditor:
  def __init__(self, 
               sampling_sec=3, 
               num_frames_per_sample=10,
               num_digits=4,
               crop_width=100,
               crop_height=100,
  ):

    self.frame_paths = []
    self.cropped_frame_paths = []
    self.sampling_sec = sampling_sec                   # サンプリング間隔（秒）
    self.num_frames_per_sample = num_frames_per_sample # サンプリングするフレーム数
    self.sampling_count = 0                            # サンプリングした数(フレーム数ではない)
    self.num_digits = num_digits    # 読み取り桁数
    self.crop_width = crop_width    # 1文字ごとのクロップ幅
    self.crop_height = crop_height  # 1文字ごとのクロップ高さ
    
    self.click_points = [] 
    logger.debug("Frame Editor loaded.")

  # 動画をフレームに分割
  def frame_devide(self, 
                   video_path, 
                   skip_sec=0, 
                   out_dir='frames'
  ):
    
    # フレーム保存用のディレクトリ
    os.makedirs(out_dir, exist_ok=True)

    # 動画の読み込み
    cap = cv2.VideoCapture(video_path)

    # 動画が正常に読み込まれたか確認
    if not cap.isOpened():
      logger.error("Error: Could not open video file.")
      exit(1)

    # 動画のフレームレートを取得
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval_frames = 1 if self.sampling_sec == 0 else  int(fps * self.sampling_sec)
    skip_frames = fps * skip_sec

    # 既にフレームが存在する場合は再分割するか確認
    saved_frame = glob.glob(f"{out_dir}/*")
    if len(saved_frame) > 0:
      logger.info("Frame files already exist.")

      # ユーザーが'y'を選択した場合
      if ask_user_confirmation("Do you want to skip spliting the frames?"):
        self.frame_paths = sorted(saved_frame)
        self.sampling_count = int((cap.get(cv2.CAP_PROP_FRAME_COUNT) - skip_frames) / interval_frames) + 1
        logger.info("Frame splitting skipped.")
        return self.frame_paths

      # ユーザーが'n'を選択した場合
      else:
        # フレーム保存用のディレクトリ内のファイルを削除
        clear_directory(out_dir)
        logger.info("Frame re-splitting.")

    frame_count = -1
    while True:
      # フレームの読み込み
      ret, frame = cap.read()
      if not ret:
        break
      
      # フレームカウントの更新
      frame_count += 1
      
      # スキップフレーム数に達していない場合はスキップ
      if frame_count < skip_frames:
        continue

      # サンプリング間隔に基づいてフレームを保存
      if frame_count % interval_frames < self.num_frames_per_sample:
        frame_filename = os.path.join(out_dir, f'frame_{frame_count:06d}.jpg')
        cv2.imwrite(frame_filename, frame)
        self.frame_paths.append(frame_filename)

        if frame_count % interval_frames == 0:
          self.sampling_count += 1

        logger.debug(f"Frame saved to '{frame_filename}'.")
    
    # リソースの解放
    cap.release()
    
    logger.info(f"Extracted {len(self.frame_paths)} frames at {self.sampling_sec}-sec intervals and saved to '{out_dir}' directory.")
    
    return self.frame_paths

  # 切り出したフレームをトリミング
  def frame_crop(self, 
                 selected_rect, 
                 frames=None, 
                 out_dir="frames_cropped"
  ):
    
    # 出力ディレクトリの作成
    os.makedirs(out_dir, exist_ok=True)
    
    # 出力ディレクトリ内のファイルを削除
    clear_directory(out_dir)
    
    frames = self.frame_paths if frames is None else frames
    
    for frame in frames:
    
      # 画像の読み込み
      if isinstance(frame, str):
        image = cv2.imread(frame)
        
      # 画像が正常に読み込まれたか確認
      if image is None:
        logger.error("Error: Could not read image file.")
        continue

      # 画像の切り取り
      cropped_frame = self.crop(image, selected_rect)

      # 切り取った画像の保存
      cropped_frame_path = os.path.join(out_dir, os.path.basename(frame))
      cv2.imwrite(cropped_frame_path, cropped_frame)
      self.cropped_frame_paths.append(cropped_frame_path)

    return self.cropped_frame_paths

  # 誤認識を許容するために連続したフレームをサンプリングしているのでグループ化する
  def group_frame_paths(self, frames):
    grouped_frame_paths = [
      frames[i:i + self.num_frames_per_sample]
      for i in range(0, len(frames), self.num_frames_per_sample)
    ]
    return grouped_frame_paths
  
  # 切り出したフレームの間隔からタイムスタンプを生成
  def generate_timestamp(self):
    timestamps = []
    
    # タイムスタンプの生成
    for i in range(0, self.sampling_count):
      timestamp = timedelta(seconds=self.sampling_sec * i)
      # タイムスタンプを "HH:MM:SS" 形式でリストに追加
      timestamps.append(str(timestamp))
    
    return timestamps

  # クリックポイント4点から画像を切り出す
  def crop(
    self,
    image, 
    click_points, 
  ):
    extract_image = None
    
    if len(click_points) == 4:
      # 射影変換
      pts1 = np.float32([
        click_points[0],
        click_points[1],
        click_points[2],
        click_points[3],
      ])
      pts2 = np.float32([
        [0, 0],
        [self.crop_width * self.num_digits, 0],
        [self.crop_width * self.num_digits, self.crop_height],
        [0, self.crop_height],
      ])
      M = cv2.getPerspectiveTransform(pts1, pts2)
      extract_image = cv2.warpPerspective(
        image, M, (self.crop_width * self.num_digits, self.crop_height))
          
    return extract_image

  # 7セグメント領域を選択
  def region_select(self, image):
    img = image if isinstance(image, np.ndarray) else cv2.imread(image)

    # GUI準備
    window_name = "Select 7seg Region"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, self.mouse_callback)

    while True:
      img_clone = img.copy()
      
      extract_image = self.crop(img_clone, self.click_points)

      # デバッグ情報描画
      img_clone, extract_image = self.draw_debug_info(
        img_clone,
        extract_image,
        self.click_points,
      )

      # 描画更新
      cv2.imshow(window_name, img_clone)
      if extract_image is not None:
          cv2.imshow('Result', extract_image)

      # キー入力(ESC:プログラム終了)
      key = cv2.waitKey(100)
      if key == ord('y'):  # yキーで選択終了
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        return self.click_points if len(self.click_points) == 4 else None

  # マウスイベントのコールバック関数
  def mouse_callback(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
      new_point = np.array([x, y])

      if len(self.click_points) < 4:
        # 4点未満なら普通に追加
        self.click_points.append(new_point)
      else:
        # 4点以上の場合、最も近い点を入れ替える
        distances = np.linalg.norm(np.array(self.click_points) - new_point, axis=1)
        closest_index = np.argmin(distances)
        self.click_points[closest_index] = new_point
          
      if len(self.click_points) == 4:
        self.click_points = self.order_points(self.click_points)

  # クリックポイントをソート
  def order_points(self, points):
    points = np.array(points)

    # x座標で昇順にソート
    sorted_by_x = points[np.argsort(points[:, 0])]

    # 左側の2点と右側の2点に分ける
    left_points = sorted_by_x[:2]
    right_points = sorted_by_x[2:]

    # 左側の2点のうち、y座標が小さいものを左上、大きいものを左下とする
    left_points = left_points[np.argsort(left_points[:, 1])]
    top_left, bottom_left = left_points

    # 右側の2点のうち、y座標が小さいものを右上、大きいものを右下とする
    right_points = right_points[np.argsort(right_points[:, 1])]
    top_right, bottom_right = right_points

    # ソートされた点を順番に返す
    return np.array([top_left, top_right, bottom_right, bottom_left])
  
  # クリックポイントを描画
  def draw_debug_info(
    self,
    image,
    extract_image,
    click_points_,
  ):
    for click_point in click_points_:
      cv2.circle(
          image, (click_point[0], click_point[1]), 5, (0, 255, 0), -1
      )
    if len(self.click_points) >= 3:
      cv2.drawContours(
          image, [np.array(self.click_points)], -1, (0, 255, 0), 2
      )
    if extract_image is not None:
        for index in range(self.num_digits):
            temp_x = int((extract_image.shape[1] / self.num_digits) * index)
            temp_y = extract_image.shape[0]
        
            if index > 0 :
                cv2.line(extract_image, (temp_x, 0), (temp_x, temp_y),
                        (0, 255, 0), 1)
    return image, extract_image

if __name__ == "__main__":
  file_path = "test/sample.jpg"

  fe = FrameEditor()
  click_points = fe.region_select(file_path)
  print(click_points)
