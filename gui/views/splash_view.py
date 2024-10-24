'''
スプラッシュスクリーンを表示するためのViewクラス

1. スプラッシュスクリーンはアプリケーションの起動時に表示される画面のこと
2. 表示する画像は、images フォルダ内の splash_image.png を使用
'''

from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from pathlib import Path

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # スプラッシュスクリーンの画像の絶対パスを取得
        current_dir = Path(__file__).resolve().parent
        self.image_path = current_dir / '..' / 'images' / 'splash_image.png'
        self.image_path = self.image_path.resolve()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel()
        
        pixmap = QPixmap(self.image_path)
        pixmap = pixmap.scaledToWidth(640, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pixmap)
        
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)  #
        layout.setSpacing(0)
        self.setLayout(layout)
        
        self.resize(pixmap.width(), pixmap.height())
        
        self.center()

    def center(self):
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        window_rect = self.frameGeometry()
        
        x = (screen_rect.width() - window_rect.width()) // 2
        y = (screen_rect.height() - window_rect.height()) // 2
        
        self.move(x, y)