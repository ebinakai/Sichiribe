from PyQt6.QtWidgets import QMainWindow, QStackedWidget
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
