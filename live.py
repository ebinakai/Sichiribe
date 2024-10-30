"""
リアルタイムで7セグメントディスプレイの数字を読み取る
詳細については、https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-CLI#execution-live を参照
"""

from cores.cnn import cnn_init
import cv2
from datetime import timedelta
import time
from pathlib import Path
from cores.common import get_now_str
from cores.settings_manager import SettingsManager
from cores.exporter import Exporter, get_supported_formats
from cores.frame_editor import FrameEditor
from cores.capture import FrameCapture
import argparse
import logging
from typing import Dict, Any
import warnings

# 警告がだるいので非表示
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="cv2")

formatter = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=formatter)
logger = logging.getLogger("__main__").getChild(__name__)

FILE = Path(__file__).resolve()
ROOT = FILE.parent


def get_args() -> argparse.Namespace:
    export_formats = get_supported_formats()

    # 引数を取得
    parser = argparse.ArgumentParser(
        description="7セグメントディスプレイの数字を読み取る"
    )
    parser.add_argument("--setting", help="設定ファイルのパス", type=str, default=None)
    parser.add_argument(
        "--device_num", "--device", help="カメラデバイスの番号", type=int, default=0
    )
    parser.add_argument(
        "--num-digits", help="7セグメント表示器の桁数", type=int, default=4
    )
    parser.add_argument(
        "--num-frames", help="サンプリングするフレーム数", type=int, default=20
    )
    parser.add_argument(
        "--sampling-sec", help="サンプリング間隔（秒）", type=int, default=10
    )
    parser.add_argument(
        "--total-sampling-min",
        help="サンプリングする合計時間（分）",
        type=float,
        default=20,
    )
    parser.add_argument(
        "--format",
        help="出力形式 (json または csv)",
        choices=export_formats,
        default="json",
    )
    parser.add_argument(
        "--save-frame", help="キャプチャしたフレームを保存するか", action="store_true"
    )
    parser.add_argument(
        "--debug", help="デバッグモードを有効にする", action="store_true"
    )
    args = parser.parse_args()

    return args


def main(settings: Dict[str, Any]) -> None:

    out_dir = ROOT / "results" / get_now_str()
    if settings["save_frame"]:
        (out_dir / "frames").mkdir(parents=True, exist_ok=True)

    frame_capture = FrameCapture(device_num=settings["device_num"])
    frame_editor = FrameEditor(num_digits=settings["num_digits"])
    detector = cnn_init(num_digits=settings["num_digits"])
    exporter = Exporter(out_dir=str(out_dir))

    if "click_points" in settings and len(settings["click_points"]) == 4:
        click_points = settings["click_points"]

    else:
        # 画角を調整するためにカメラフィードを表示
        frame_capture.show_camera_feed()

        frame = frame_capture.capture()
        if frame is None:
            logger.error("Failed to capture the frame.")
            return
        click_points = frame_editor.region_select(frame)
    settings["click_points"] = click_points

    start_time = time.time()
    end_time = start_time + settings["total_sampling_sec"]
    frame_count = 0
    timestamps = []
    results = []
    failed_rates = []
    while time.time() < end_time:
        temp_time = time.time()
        frames = []

        for i in range(settings["num_frames"]):
            frame = frame_capture.capture()

            if frame is None:
                continue

            cropped_frame = frame_editor.crop(frame, click_points)
            if cropped_frame is None:
                continue
            frames.append(cropped_frame)

            if settings["save_frame"]:
                frame_filename = out_dir / f"frame_{frame_count}.jpg"
                cv2.imwrite(str(frame_filename), cropped_frame)
                logger.debug(f"Frame {frame_count} has been saved as: {frame_filename}")
                frame_count += 1

        if len(frames) != 0:
            value, failed_rate = detector.predict(frames)
            logger.info(f"Detected: {value}, Failed rate: {failed_rate}")
            results.append(value)
            failed_rates.append(failed_rate)

            # タイムスタンプを "HH:MM:SS" 形式で生成
            elapsed_time = time.time() - start_time
            timestamp = timedelta(seconds=int(elapsed_time))
            timestamps.append(str(timestamp))

        elapsed_time = time.time() - temp_time
        time_to_wait = max(0, settings["sampling_sec"] - elapsed_time)

        if time_to_wait > 0:
            logger.debug(f"Waiting for {time_to_wait:.2f}s")
            time.sleep(time_to_wait)

    frame_capture.release()

    data = exporter.format(results, failed_rates, timestamps)
    exporter.export(
        data, method=settings["format"], prefix="result", with_timestamp=False
    )

    settings = settings_manager.remove_non_require_keys(settings)
    exporter.export(settings, method="json", prefix="settings", with_timestamp=False)


if __name__ == "__main__":

    args = get_args()
    settings = vars(args)

    if settings.pop("debug"):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.debug("args: %s", args)

    settings["total_sampling_sec"] = settings.pop("total_sampling_min") * 60

    settings_manager = SettingsManager("live")

    setting_path = settings.pop("setting")
    if setting_path is not None:
        settings = settings_manager.load(setting_path)
    else:
        settings["click_points"] = []

    settings_manager.validate(settings)
    logger.debug("settings: %s", settings)
    main(settings)

    logger.info("All Done!")
