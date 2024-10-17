'''
ここではメインウィンドウを定義する

1. スタックウィジェットを使い、このウィジェット内に各画面を表示する
2. 画面遷移は、gui/utils/screen_manager にて定義されたスクリーンマネージャーを使用して行う
3. 画面の定義は、gui/views/* にある各画面のクラスを使う
4. 画面のルーティングは、gui/utils/router.py にて行う
'''

from PySide6.QtWidgets import QMainWindow, QStackedWidget
from gui.utils.router import init_screen_manager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sichiribe')
        
        # スタックウィジェットを作成
        stacked_widget = QStackedWidget()
        self.setCentralWidget(stacked_widget)
        
        # スクリーンマネージャーを初期化
        screen_manager = init_screen_manager(stacked_widget, self)
        screen_manager.resie_defualt()
        screen_manager.center()
        screen_manager.show_screen('menu')
