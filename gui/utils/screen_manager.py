"""画面情報を保持し、管理を行う機能"""

from PySide6.QtWidgets import QApplication, QStackedWidget, QMainWindow, QMessageBox
from PySide6.QtGui import QPalette
from PySide6.QtCore import QEventLoop, QTimer, QPoint, QSize
from gui.widgets.custom_qwidget import CustomQWidget
import logging
from dataclasses import dataclass
from typing import Tuple, Dict, Optional


@dataclass
class ScreenInfo:
    """画面情報を保持するデータクラス"""

    widget: CustomQWidget
    title: str


class ScreenManager:
    """
    画面の管理を行うクラス

    Methods:
        add_screen: 画面を追加する
        show_screen: 画面を表示する
        get_screen: 画面を取得する
        check_if_dark_mode: ダークモードかどうかを判定する
        resize_defualt: 画面のデフォルトサイズにリサイズする
        save_screen_size: 画面サイズを保存する
        restore_screen_size: 画面サイズを復元する
        popup: ポップアップメッセージボックスを表示する
        quit: アプリケーションを終了する
    """

    def __init__(self, stacked_widget: QStackedWidget, main_window: QMainWindow):
        self.stacked_widget = stacked_widget
        self.main_window = main_window
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.screens: Dict[str, ScreenInfo] = {}
        self.window_pos: Optional[QPoint] = None
        self.window_size: Optional[QSize] = None

    def add_screen(self, name: str, widget: CustomQWidget, title: str) -> None:
        """
        Args:
            name (str): 画面呼び出し時の名前
            widget (CustomQWidget): 画面のウィジェットオブジェクト
            title (str): 画面のタイトル

        Returns:
            None
        """
        self.screens[name] = ScreenInfo(widget=widget, title=title)
        self.stacked_widget.addWidget(widget)

    def show_screen(self, name: str) -> None:
        """
        Args:
            name (str): 画面の名前
        """
        if name in self.screens:
            widget = self.screens[name].widget
            widget.display()
            self.main_window.setWindowTitle(f"Sichiribe {self.screens[name].title}")
            self.stacked_widget.setCurrentWidget(widget)
            self.main_window.setFocus()
        else:
            raise ValueError(f"Screen '{name}' not found")

    def get_screen(self, name: str) -> CustomQWidget:
        """
        Args:
            name (str): 画面の名前

        Returns:
            CustomQWidget: 画面のウィジェットオブジェクト
        """
        if name in self.screens:
            return self.screens[name].widget
        else:
            raise ValueError(f"Screen '{name}' not found")

    def check_if_dark_mode(self) -> bool:
        """
        画面の平均色が暗いかどうかを判定する

        Returns:
            bool: ダークモードかどうか
        """
        palette = QApplication.palette()
        return palette.color(QPalette.ColorRole.Window).value() < 128

    def resize_defualt(self) -> None:
        self.main_window.resize(640, 480)

    def save_screen_size(self) -> Tuple[QPoint, QSize]:
        """
        Returns:
            Tuple[QPoint, QSize]: 画面の位置とサイズ
        """
        self.window_pos = self.main_window.frameGeometry().topLeft()
        self.window_size = self.main_window.size()
        return self.window_pos, self.window_size

    def restore_screen_size(self) -> None:
        """
        保存された画面の位置とサイズを復元する
        リサイズ後は、保存された位置とサイズはクリアされる
        """
        QApplication.processEvents()
        if self.window_pos is not None and self.window_size is not None:
            self.logger.info("Screen geometry restoring...")

            # 現在の画面内のオブジェクトが処理を終えるまで10ms待つ
            loop = QEventLoop()
            QTimer.singleShot(10, loop.quit)
            loop.exec()

            self.main_window.move(self.window_pos)
            self.main_window.resize(self.window_size)
            self.window_pos = None
            self.window_size = None

        else:
            self.logger.error("No screen size saved")

    def popup(self, message: str) -> None:
        """
        画面にポップアップメッセージボックスを表示する
        同期処理のため、メッセージボックスが閉じられるまで処理がブロックされる

        Args:
            message (str): 表示内容
        """
        self.logger.debug("Popup message: %s" % message)

        msg_box = QMessageBox(self.main_window)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.show()

    def quit(self) -> None:
        self.logger.info("Quitting application")
        QApplication.quit()
