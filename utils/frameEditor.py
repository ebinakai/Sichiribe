import cv2
import logging
import os
import glob
from datetime import timedelta
from utils.common import ask_user_confirmation, clear_directory

# ロガーの設定
logger = logging.getLogger("__main__").getChild(__name__)

class FrameEditor:
  def __init__(self, sampling_sec=3, num_frames_per_sample=10):
    self.frame_paths = []
    self.cropped_frame_paths = []
    self.sampling_sec = sampling_sec                   # サンプリング間隔（秒）
    self.num_frames_per_sample = num_frames_per_sample # サンプリングするフレーム数
    self.sampling_count = 0                            # サンプリングした数(フレーム数ではない)
    logger.debug("Frame Editor loaded.")

  # 動画をフレームに分割
  # [説明] 誤認識を許容するために連続したフレームをサンプリングしているのでグループ化する
  def frame_devide(self, video_path, skip_sec=0, output_dir='frames'):
    
    # フレーム保存用のディレクトリ
    os.makedirs(output_dir, exist_ok=True)

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
    saved_frame = glob.glob(f"{output_dir}/*")
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
        clear_directory(output_dir)
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
        frame_filename = os.path.join(output_dir, f'frame_{frame_count:06d}.jpg')
        cv2.imwrite(frame_filename, frame)
        self.frame_paths.append(frame_filename)

        if frame_count % interval_frames == 0:
          self.sampling_count += 1

        logger.debug(f"Frame saved to '{frame_filename}'.")
    
    # リソースの解放
    cap.release()
    
    logger.info(f"Extracted {len(self.frame_paths)} frames at {self.sampling_sec}-sec intervals and saved to '{output_dir}' directory.")
    
    return self.frame_paths

  # 切り出したフレームをトリミング
  def frame_crop(self, selected_rect, output_dir="frames_cropped", gray_scale=False):
    
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 出力ディレクトリ内のファイルを削除
    clear_directory(output_dir)
    
    for frame_path in self.frame_paths:
    
      # 画像の読み込み
      if gray_scale:
        image_gs = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
        # 二値化（しきい値を調整する）
        _, image_bin = cv2.threshold(image_gs, 90, 255, cv2.THRESH_BINARY_INV)

        # 二値化された画像をカラーに変換
        image = cv2.cvtColor(image_bin, cv2.COLOR_GRAY2BGR)
      
      else: 
        image = cv2.imread(frame_path)     
        
      # 画像が正常に読み込まれたか確認
      if image is None:
        logger.error("Error: Could not read image file.")
        continue

      start_x, start_y, end_x, end_y = selected_rect

      # 画像の切り取り
      cropped_frame = image[start_y:end_y, start_x:end_x]

      # 切り取った画像の保存
      cropped_frame_path = os.path.join(output_dir, os.path.basename(frame_path))
      cv2.imwrite(cropped_frame_path, cropped_frame)
      self.cropped_frame_paths.append(cropped_frame_path)

    return self.cropped_frame_paths

  # サンプルフレームをグループ化
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
    
