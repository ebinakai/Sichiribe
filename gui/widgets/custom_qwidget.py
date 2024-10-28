"""
カスタムウィジェットを作成するためのクラスを定義する

1. このウィジェットを継承して各GUIコンポーネントを作成する
"""

from PySide6.QtWidgets import QWidget


class CustomQWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        raise NotImplementedError("initUI() must be implemented in subclass")

    def trigger(self, action: str, *args) -> None:
        pass
