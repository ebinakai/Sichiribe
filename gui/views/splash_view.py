from PySide6.QtWidgets import QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from pathlib import Path
from gui.widgets.custom_qwidget import CustomQWidget
from gui.utils.common import center_window


class SplashScreen(CustomQWidget):
    """スプラッシュスクリーンを表示するためのViewクラス

    スプラッシュスクリーンはアプリケーションの起動時に表示される画面のこと

    表示する画像は、images フォルダ内の splash_image.png を使用
    """

    def __init__(self) -> None:
        current_dir = Path(__file__).resolve().parent
        self.image_path = current_dir / ".." / "images" / "splash_image.png"
        self.image_path = self.image_path.resolve()

        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout()
        label = QLabel()

        pixmap = QPixmap(self.image_path)
        pixmap = pixmap.scaledToWidth(640, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pixmap)

        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.resize(pixmap.width(), pixmap.height())

        center_window(self)
