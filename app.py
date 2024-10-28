'''
GUIアプリケーションを起動するためのメインプログラムこのスクリプトを実行することで、GUIアプリケーションが起動する
詳細については、https://github.com/EbinaKai/Sichiribe/wiki/How-to-use-GUI-App を参照
'''

from gui.views.main_view import MainWindow
from gui.views.splash_view import SplashScreen
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
import sys
import logging
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)


def main() -> None:
    show_splash_ms = 2000

    app = QApplication([])

    splash_window = SplashScreen()
    splash_window.show()
    window = MainWindow()

    QTimer.singleShot(show_splash_ms, window.show)
    QTimer.singleShot(show_splash_ms, splash_window.close)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
