from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # スプラッシュスクリーンのレイアウトを設定
        layout = QVBoxLayout()
        label = QLabel()
        pixmap = QPixmap("gui/images/splash_image.png")
        pixmap = pixmap.scaledToWidth(640, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pixmap)
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)  # マージンを0に設定
        layout.setSpacing(0)  # スペーシングを0に設定
        self.setLayout(layout)
        
        # ウィンドウのサイズを設定
        self.resize(pixmap.width(), pixmap.height())
        
        # スプラッシュスクリーンをディスプレイの中央に配置
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