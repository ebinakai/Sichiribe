# 警告がだるいので非表示
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='cv2')

# ロガーの設定
import logging
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger('__main__').getChild(__name__)

import argparse
from cores.frameEditor import FrameEditor
from cores.cnn_lite import CNNLite as Detector
from cores.exporter import Exporter, get_supported_formats

def get_args():
  export_formats = get_supported_formats()
  
  # 引数を取得
  parser = argparse.ArgumentParser(description='7セグメントディスプレイの数字を読み取る') 
  parser.add_argument('video_path', help='解析する動画のパス')
  parser.add_argument('--num-digits', help="7セグメント表示器の桁数", type=int, default=4)
  parser.add_argument('--sampling-sec', help="サンプリング間隔（秒）", type=int, default=10)
  parser.add_argument('--num-frames', help="サンプリングするフレーム数", type=int, default=20)
  parser.add_argument('--skip-sec', help="動画の先頭からスキップする秒数", type=int, default=0)
  parser.add_argument('--format', help="出力形式 (json または csv)", choices=export_formats, default='json')
  parser.add_argument('--save-frame', help="キャプチャしたフレームを保存するか（保存しない場合、メモリの使用量が増加します）", action='store_true')
  parser.add_argument('--debug', help="デバッグモードを有効にする", action='store_true')
  args = parser.parse_args()
  
  return args

def main(video_path, 
         num_digits,
         sampling_sec, 
         num_frames, 
         video_skip_sec,
         format,
         save_frame,
         out_dir='results',
):
  # インスタンスの生成
  fe = FrameEditor(sampling_sec, num_frames, num_digits)
  dt = Detector(num_digits)
  ep = Exporter(format, out_dir)

  # モデルの読み込み
  dt.load()
  
  # フレームの切り出し
  frames = fe.frame_devide(video_path, video_skip_sec, save_frame)
  timestamps = fe.generate_timestamp(len(frames))
    
  # テキスト検出
  results = []
  failed_rates = []
  for frame in frames:
    result, failed_rate = dt.detect(frame)
    results.append(result)
    failed_rates.append(failed_rate)
    logger.info(f"Detected Result: {result}")
    logger.info(f"Failed Rate: {failed_rate}")

  # 結果のエクスポート
  data = ep.format(results, failed_rates, timestamps)
  ep.export(data)


if __name__ == "__main__":
  args = get_args()
  
  # ログレベルを設定
  logger.setLevel(logging.DEBUG) if args.debug else logger.setLevel(logging.INFO)
  logger.debug("args: %s", args)
  
  # 実行
  main(video_path=args.video_path, 
       num_digits=args.num_digits, 
       sampling_sec=args.sampling_sec, 
       num_frames=args.num_frames, 
       video_skip_sec=args.skip_sec, 
       format=args.format,
       save_frame=args.save_frame,
      )
  
  logger.info("All Done!")
