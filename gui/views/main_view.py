from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from gui.utils.router import get_screen_manager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sichiribe')
        self.setGeometry(200, 200, 640, 480)
        
        # スタックウィジェットを作成
        stacked_widget = QStackedWidget()
        screen_manager = get_screen_manager(stacked_widget)
        self.setCentralWidget(stacked_widget)
        
        screen_manager.show_screen('menu')
        
        self.center()

    def center(self):
        # ディスプレイサイズを取得
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        
        # ウィンドウサイズを取得
        window_rect = self.frameGeometry()
        
        # 中央に配置するための位置を計算
        x = (screen_rect.width() - window_rect.width()) // 2
        y = (screen_rect.height() - window_rect.height()) // 2
        
        # 計算した位置にウィンドウを移動
        self.move(x, y)