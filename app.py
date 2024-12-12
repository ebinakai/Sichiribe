"""
GUIアプリケーションを起動するためのメインプログラム
"""

from gui.views.main_view import MainWindow
from gui.views.splash_view import SplashScreen
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
import sys
import logging
import argparse

SPLASH_SHOW_MS = 2000


def setup_logging(debug_mode: bool) -> None:
    """ログの設定

    Args:
        debug_mode (bool): デバッグモードかどうか
    """
    formatter = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(level=level, format=formatter)


def get_args() -> argparse.Namespace:
    """コマンドライン引数の取得

    Returns:
        argparse.Namespace: コマンドライン引数
    """
    parser = argparse.ArgumentParser(description="GUI Application")
    parser.add_argument(
        "--debug", action="store_true", help="デバッグモードを有効にする"
    )
    return parser.parse_args()


def main() -> None:
    """GUIアプリケーションのエントリーポイント
    """
    args = get_args()
    setup_logging(args.debug)

    app = QApplication([])

    splash_window = SplashScreen()
    splash_window.show()
    window = MainWindow()

    QTimer.singleShot(SPLASH_SHOW_MS, window.show)
    QTimer.singleShot(SPLASH_SHOW_MS, splash_window.close)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
