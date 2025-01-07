"""画面遷移と管理を行うメインウィンドウ"""

from PySide6.QtWidgets import QMainWindow, QStackedWidget
from gui.utils.router import init_screen_manager
from gui.utils.common import center_window


class MainWindow(QMainWindow):
    """
    メインウィンドウのViewクラス

    1. スタックウィジェットを使い、このウィジェット内に各画面を表示する
    2. 画面遷移は、gui/utils/screen_manager にて定義されたスクリーンマネージャーを使用して行う
    3. 画面の定義は、gui/views/* にある各画面のクラスを使う
    4. 画面のルーティングは、gui/utils/router.py にて行う
    """

    def __init__(self) -> None:
        super().__init__()

        stacked_widget = QStackedWidget()
        self.setCentralWidget(stacked_widget)

        screen_manager = init_screen_manager(stacked_widget, self)
        screen_manager.resize_defualt()
        screen_manager.show_screen("menu")
        center_window(self)
