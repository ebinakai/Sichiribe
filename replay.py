"""
動画ファイルから7セグメントディスプレイの数字を読み取る
詳細については、https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-CLI#execution-replay を参照
"""

from cores.cnn import cnn_init
from cores.common import get_now_str
from cores.settings_manager import SettingsManager
from cores.export_utils import export, get_supported_formats, build_data_records
from cores.frame_editor import FrameEditor
from pathlib import Path
import argparse
import logging
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

    parser = argparse.ArgumentParser(
        description="7セグメントディスプレイの数字を読み取る"
    )
    parser.add_argument(
        "--video_path", help="解析する動画のパス", type=str, default=None
    )
    parser.add_argument("--setting", help="設定ファイルのパス", type=str, default=None)
    parser.add_argument(
        "--num-digits", help="7セグメント表示器の桁数", type=int, default=4
    )
    parser.add_argument(
        "--sampling-sec", help="サンプリング間隔（秒）", type=int, default=10
    )
    parser.add_argument(
        "--num-frames", help="サンプリングするフレーム数", type=int, default=20
    )
    parser.add_argument(
        "--video-skip-sec",
        "--skip",
        help="動画の先頭からスキップする秒数",
        type=int,
        default=0,
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


def main(settings) -> None:
    frame_editor = FrameEditor(settings["num_digits"])
    detector = cnn_init(num_digits=settings["num_digits"])

    out_dir = ROOT / "results" / get_now_str()

    if "click_points" in settings and len(settings["click_points"]) == 4:
        click_points = settings["click_points"]
    else:
        click_points = []

    sampled_frames, timestamps = frame_editor.frame_devide(
        video_path=settings["video_path"],
        video_skip_sec=settings["video_skip_sec"],
        sampling_sec=settings["sampling_sec"],
        batch_frames=settings["batch_frames"],
        save_frame=settings["save_frame"],
        out_dir=str(out_dir / "frames"),
        click_points=click_points,
    )
    settings["click_points"] = frame_editor.get_click_points()

    results = []
    failed_rates = []
    for frame_batch in sampled_frames:
        result, failed_rate = detector.predict(frame_batch)
        results.append(result)
        failed_rates.append(failed_rate)
        logger.info(f"Detected Result: {result}")
        logger.info(f"Failed Rate: {failed_rate}")

    data = build_data_records(
        {
            "results": results,
            "failed_rates": failed_rates,
            "timestamps": timestamps,
        }
    )
    settings = settings_manager.remove_non_require_keys(settings)
    export(data, format=settings["format"], out_dir=out_dir, prefix="result")
    export(settings, format=settings["format"], out_dir=out_dir, prefix="settings")


if __name__ == "__main__":
    args = get_args()
    settings = vars(args)

    if settings.pop("debug"):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.debug("args: %s", args)

    settings_manager = SettingsManager("replay")
    setting_path = settings.pop("setting")
    if setting_path is not None:
        settings = settings_manager.load(setting_path)
    elif settings["video_path"] is None:
        raise ValueError("video_path or setting is required.")
    else:
        settings["click_points"] = []

    settings_manager.validate(settings)
    logger.debug("settings: %s", settings)
    main(settings)

    logger.info("All Done!")
