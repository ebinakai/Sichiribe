# 警告がだるいので非表示
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='cv2')

# ロガーの設定
import logging
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger(__name__)

import argparse
from utils.frameEditor import FrameEditor
from utils.ocr import OCR as Detector
from utils.exporter import Exporter, get_supported_formats

def run(  video_path, 
          sampling_sec, 
          num_frames_per_sample, 
          video_skip_sec,
          output_format
        ):

  # インスタンスの生成
  fe = FrameEditor(sampling_sec, num_frames_per_sample)
  dt = Detector()
  ep = Exporter(method=output_format)

  # フレームの切り出し
  frame_paths = fe.frame_devide(video_path, video_skip_sec)
  timestamps = fe.generate_timestamp()

  # トリミング範囲の選択
  selected_rect = fe.region_select(frame_paths[0])

  # 選択範囲のトリミング
  cropped_frame_paths = fe.frame_crop(selected_rect)

  # 連続したフレームをグループ化する
  grouped_frame_paths = fe.group_frame_paths(cropped_frame_paths)

  # OCRでテキスト検出
  ocr_results = []
  for paths in grouped_frame_paths:
    ocr_result, failed_rate = dt.detect(paths)
    ocr_results.append(ocr_result)
    logger.info(f"OCR Result: {ocr_result}")
    logger.info(f"Failed Rate: {failed_rate}")

  # 結果のエクスポート
  data = ep.format(ocr_results, timestamps)
  ep.export(data)


if __name__ == "__main__":
  export_formats = get_supported_formats()
  
  # 引数を取得
  parser = argparse.ArgumentParser(description='7セグメントディスプレイの数字を読み取る') 
  parser.add_argument('video_path', help='解析する動画のパス')
  parser.add_argument('--sampling-sec', help="サンプリング間隔（秒）", type=int, default=10)
  parser.add_argument('--num-frames', help="サンプリングするフレーム数", type=int, default=20)
  parser.add_argument('--skip-sec', help="動画の先頭からスキップする秒数", type=int, default=0)
  parser.add_argument('--format', help="出力形式 (json または csv)", choices=export_formats, default='json')
  parser.add_argument('--debug', help="デバッグモードを有効にする", action='store_true')
  args = parser.parse_args()
  
  # ログレベルを設定
  logger.setLevel(logging.DEBUG) if args.debug else logger.setLevel(logging.INFO)
  logger.debug("args: %s", args)
  
  # 実行
  run(args.video_path, args.sampling_sec, args.num_frames, args.skip_sec, args.format)
  logger.info("All Done!")
