"""カスタムウィジェットの基底クラス"""

from PySide6.QtWidgets import QWidget
from gui.utils.data_store import DataStore


class CustomQWidget(QWidget):
    """カスタムウィジェットの基底クラス

    このウィジェットを継承して各GUIコンポーネントを作成する
    """

    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.data_store = DataStore.get_instance()

    def initUI(self) -> None:
        """ウィジェットのUIを初期化する

        Raises:
            NotImplementedError: サブクラスで実装されていない場合
        """
        raise NotImplementedError("initUI() must be implemented in subclass")

    def trigger(self, action: str, *args) -> None:
        """ウィジェットのアクションをトリガーする

        Args:
            action (str): アクション名

        Raises:
            NotImplementedError: サブクラスで実装されていない場合
        """
        raise NotImplementedError("trigger() must be implemented in subclass if used")

    def display(self) -> None:
        """ウィジェットを表示されたときの処理"""
