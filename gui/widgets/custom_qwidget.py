"""
カスタムウィジェットを作成するためのクラスを定義する

1. このウィジェットを継承して各GUIコンポーネントを作成する
"""

from PySide6.QtWidgets import QWidget
from gui.utils.data_store import DataStore


class CustomQWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.data_store = DataStore.get_instance()

    def initUI(self) -> None:
        raise NotImplementedError("initUI() must be implemented in subclass")

    def trigger(self, action: str, *args) -> None:
        raise NotImplementedError("trigger() must be implemented in subclass if used")

    def display(self) -> None:
        pass
