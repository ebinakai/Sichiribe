# 警告がだるいので非表示
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='cv2')

# ログの設定
import logging
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger(__name__)

import argparse
from utils.capture import FrameCapture
from utils.frameEditor import FrameEditor
from utils.ocr import OCR as Detector
from utils.common import get_now_str
import time
import os
import cv2

# クラスのインスタンスを作成してフレームをキャプチャ
if __name__ == "__main__":
  
  # 引数を取得
  parser = argparse.ArgumentParser(description='7セグメントディスプレイの数字を読み取る') 
  parser.add_argument('--device', help="カメラデバイスの番号", type=int, default=0)
  parser.add_argument('--num-frames', help="サンプリングするフレーム数", type=int, default=20)
  parser.add_argument('--interval-min', help="サンプリング間隔（分）", type=float, default=1)
  parser.add_argument('--total-sampling-min', help="サンプリングする合計時間（分）", type=float, default=20)
  parser.add_argument('--save-frame', help="キャプチャしたフレームを保存するか", action='store_true')
  parser.add_argument('--debug', help="デバッグモードを有効にする", action='store_true')
  args = parser.parse_args()
  
  if args.save_frame:
    now = get_now_str()
    save_dir = f"frames_{now}"
    os.makedirs(save_dir)
  
  fc = FrameCapture(device_num=args.device)
  fe = FrameEditor()
  dt = Detector()
  
  # 画角を調整するためにカメラフィードを表示
  fc.show_camera_feed()

  # フレームをキャプチャ
  frame = fc.capture()
  selected_rect = fe.region_select(frame)
  
  
  interval_sec = args.interval_min * 60
  total_duration_seconds = args.total_sampling_min * 60
  end_time = time.time() + total_duration_seconds
  frame_count = 0
  while time.time() < end_time:
    start_time = time.time()
    frames = []

    for i in range(args.num_frames):
      frame = fc.capture()
      
      if frame is None:
        continue
      
      # 推論処理
      cropped_frame = fe.crop(frame, selected_rect)
      frames.append(cropped_frame)
      
      # フレームを保存
      if args.save_frame:
        frame_filename = os.path.join(save_dir, f"frame_{frame_count}.jpg")
        cv2.imwrite(frame_filename, cropped_frame)
        logger.debug(f"Frame {frame_count} has been saved as: {frame_filename}")
        frame_count += 1
    
    if len(frames) != 0:
      value, failed_rate = dt.detect(frames)
      logger.info(f"Detected: {value}, Failed rate: {failed_rate}")
          
    elapsed_time = time.time() - start_time
    time_to_wait = max(0, interval_sec - elapsed_time)

    if time_to_wait > 0:
      logger.debug(f"Waiting for {time_to_wait:.2f}s")
      time.sleep(time_to_wait)
  
  fc.release()
  