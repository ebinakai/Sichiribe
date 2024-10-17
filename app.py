'''
GUIアプリケーションを起動するためのメインプログラムこのスクリプトを実行することで、GUIアプリケーションが起動する
詳細については、docs/execution_gui.mdを参照
'''

# ログの設定
import logging
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from gui.views.splash_view import SplashScreen
from gui.views.main_view import MainWindow
        
def main():
    splash_ms = 2000 # スプラッシュスクリーンを表示する時間（ミリ秒）
    
    # アプリケーションを作成
    app = QApplication([])
    
    # スプラッシュスクリーン用の画像を読み込む
    splash_window = SplashScreen()
    splash_window.show()
    window = MainWindow()

    # 指定時間後にスプラッシュスクリーンを閉じて、メインウィンドウを表示
    QTimer.singleShot(splash_ms, window.show)
    QTimer.singleShot(splash_ms, splash_window.close)

    # イベントループを開始
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
