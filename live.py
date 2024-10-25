'''
リアルタイムで7セグメントディスプレイの数字を読み取る
詳細については、https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-CLI#execution-live を参照
'''

from cores.cnn_core import select_cnn_model
import cv2
import os
from datetime import timedelta
import time
from cores.common import get_now_str
from cores.exporter import Exporter, get_supported_formats
from cores.frameEditor import FrameEditor
from cores.capture import FrameCapture
import argparse
import logging
import warnings

# 警告がだるいので非表示
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='cv2')

formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger('__main__').getChild(__name__)


# モデルを読み込む
Detector = select_cnn_model()


def get_args():
    export_formats = get_supported_formats()

    # 引数を取得
    parser = argparse.ArgumentParser(description='7セグメントディスプレイの数字を読み取る')
    parser.add_argument('--device', help="カメラデバイスの番号", type=int, default=0)
    parser.add_argument(
        '--num-digits',
        help="7セグメント表示器の桁数",
        type=int,
        default=4)
    parser.add_argument(
        '--num-frames',
        help="サンプリングするフレーム数",
        type=int,
        default=20)
    parser.add_argument(
        '--sampling-sec',
        help="サンプリング間隔（秒）",
        type=int,
        default=10)
    parser.add_argument(
        '--total-sampling-min',
        help="サンプリングする合計時間（分）",
        type=float,
        default=20)
    parser.add_argument(
        '--format',
        help="出力形式 (json または csv)",
        choices=export_formats,
        default='json')
    parser.add_argument(
        '--save-frame',
        help="キャプチャしたフレームを保存するか",
        action='store_true')
    parser.add_argument('--debug', help="デバッグモードを有効にする", action='store_true')
    args = parser.parse_args()

    return args


def main(device,
         num_digits,
         sampling_sec,
         num_frames,
         total_sampling_sec,
         format,
         save_frame,
         out_dir='results',
         ):

    fc = FrameCapture(device_num=device)
    fe = FrameEditor(num_digits=num_digits)
    dt = Detector(num_digits=num_digits)
    ep = Exporter(format, out_dir)

    dt.load()

    # 画角を調整するためにカメラフィードを表示
    fc.show_camera_feed()

    frame = fc.capture()
    click_points = fe.region_select(frame)

    start_time = time.time()
    end_time = time.time() + total_sampling_sec
    frame_count = 0
    timestamps = []
    results = []
    failed_rates = []
    while time.time() < end_time:
        temp_time = time.time()
        frames = []

        for i in range(num_frames):
            frame = fc.capture()

            if frame is None:
                continue

            cropped_frame = fe.crop(frame, click_points)
            frames.append(cropped_frame)

            if save_frame:
                frame_filename = os.path.join(
                    save_dir, f"frame_{frame_count}.jpg")
                cv2.imwrite(frame_filename, cropped_frame)
                logger.debug(
                    f"Frame {frame_count} has been saved as: {frame_filename}")
                frame_count += 1

        if len(frames) != 0:
            value, failed_rate = dt.detect(frames)
            logger.info(f"Detected: {value}, Failed rate: {failed_rate}")
            results.append(value)
            failed_rates.append(failed_rate)

            # タイムスタンプを "HH:MM:SS" 形式で生成
            elapsed_time = int(time.time() - start_time)
            timestamp = timedelta(seconds=elapsed_time)
            timestamps.append(str(timestamp))

        elapsed_time = time.time() - temp_time
        time_to_wait = max(0, sampling_sec - elapsed_time)

        if time_to_wait > 0:
            logger.debug(f"Waiting for {time_to_wait:.2f}s")
            time.sleep(time_to_wait)

    fc.release()

    data = ep.format(results, failed_rates, timestamps)
    ep.export(data)


if __name__ == "__main__":

    args = get_args()

    if args.save_frame:
        now = get_now_str()
        save_dir = f"frames_{now}"
        os.makedirs(save_dir)

    logger.setLevel(
        logging.DEBUG) if args.debug else logger.setLevel(
        logging.INFO)
    logger.debug("args: %s", args)

    main(
        device=args.device,
        num_digits=args.num_digits,
        sampling_sec=args.sampling_sec,
        num_frames=args.num_frames,
        total_sampling_sec=args.total_sampling_min * 60,
        format=args.format,
        save_frame=args.save_frame,
    )

    logger.info("All Done!")
