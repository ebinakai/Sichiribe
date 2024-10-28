'''
リアルタイムで7セグメントディスプレイの数字を読み取る
詳細については、https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-CLI#execution-live を参照
'''

from cores.cnn import cnn_init
import cv2
import os
from datetime import timedelta
import time
from pathlib import Path
from cores.common import get_now_str, load_config
from cores.exporter import Exporter, get_supported_formats
from cores.frame_editor import FrameEditor
from cores.capture import FrameCapture
import argparse
import logging
from typing import Dict, Any
import warnings

# 警告がだるいので非表示
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='cv2')

formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger('__main__').getChild(__name__)

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]


def get_args() -> argparse.Namespace:
    export_formats = get_supported_formats()

    # 引数を取得
    parser = argparse.ArgumentParser(description='7セグメントディスプレイの数字を読み取る')
    parser.add_argument('--config', help='設定ファイルのパス', type=str, default=None)
    parser.add_argument(
        '--device_num',
        '--device',
        help='カメラデバイスの番号',
        type=int,
        default=0)
    parser.add_argument(
        '--num-digits',
        help='7セグメント表示器の桁数',
        type=int,
        default=4)
    parser.add_argument(
        '--num-frames',
        help='サンプリングするフレーム数',
        type=int,
        default=20)
    parser.add_argument(
        '--sampling-sec',
        help='サンプリング間隔（秒）',
        type=int,
        default=10)
    parser.add_argument(
        '--total-sampling-min',
        help='サンプリングする合計時間（分）',
        type=float,
        default=20)
    parser.add_argument(
        '--format',
        help='出力形式 (json または csv)',
        choices=export_formats,
        default='json')
    parser.add_argument(
        '--save-frame',
        help='キャプチャしたフレームを保存するか',
        action='store_true')
    parser.add_argument('--debug', help='デバッグモードを有効にする', action='store_true')
    args = parser.parse_args()

    return args


def main(params: Dict[str, Any]) -> None:

    if params['save_frame']:
        now = get_now_str()
        out_dir = ROOT / f"frames_{now}"
        os.makedirs(out_dir)

    fc = FrameCapture(device_num=params['device_num'])
    fe = FrameEditor(num_digits=params['num_digits'])
    dt = cnn_init(num_digits=params['num_digits'])
    ep = Exporter(out_dir='results')

    if 'click_points' in params and len(params['click_points']) == 4:
        click_points = params['click_points']
        params['is_save_config'] = False

    else:
        # 画角を調整するためにカメラフィードを表示
        fc.show_camera_feed()

        frame = fc.capture()
        if frame is None:
            logger.error('Failed to capture the frame.')
            return
        click_points = fe.region_select(frame)
        params['is_save_config'] = True
    params['click_points'] = click_points

    start_time = time.time()
    end_time = time.time() + params['total_sampling_sec']
    frame_count = 0
    timestamps = []
    results = []
    failed_rates = []
    while time.time() < end_time:
        temp_time = time.time()
        frames = []

        for i in range(params['num_frames']):
            frame = fc.capture()

            if frame is None:
                continue

            cropped_frame = fe.crop(frame, click_points)
            if cropped_frame is None:
                continue
            frames.append(cropped_frame)

            if params['save_frame']:
                frame_filename = os.path.join(
                    out_dir, f"frame_{frame_count}.jpg")
                cv2.imwrite(frame_filename, cropped_frame)
                logger.debug(
                    f"Frame {frame_count} has been saved as: {frame_filename}")
                frame_count += 1

        if len(frames) != 0:
            value, failed_rate = dt.predict(frames)
            logger.info(f"Detected: {value}, Failed rate: {failed_rate}")
            results.append(value)
            failed_rates.append(failed_rate)

            # タイムスタンプを "HH:MM:SS" 形式で生成
            elapsed_time = time.time() - start_time
            timestamp = timedelta(seconds=int(elapsed_time))
            timestamps.append(str(timestamp))

        elapsed_time = time.time() - temp_time
        time_to_wait = max(0, params['sampling_sec'] - elapsed_time)

        if time_to_wait > 0:
            logger.debug(f"Waiting for {time_to_wait:.2f}s")
            time.sleep(time_to_wait)

    fc.release()

    data = ep.format(results, failed_rates, timestamps)
    ep.export(data, method=params['format'])
    if params['is_save_config']:
        ep.export(params, method='json', base_filename='params')


if __name__ == '__main__':

    args = get_args()
    params = vars(args)

    if params.pop('debug'):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.debug("args: %s", args)

    params['total_sampling_sec'] = params.pop('total_sampling_min') * 60

    config_path = params.pop('config')
    if config_path is not None:
        required_keys = set(params.keys())
        required_keys.add('click_points')
        params = load_config(config_path, required_keys)

    logger.debug("params: %s", params)
    main(params)

    logger.info('All Done!')
