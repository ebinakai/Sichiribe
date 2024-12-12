from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt


class ClickableLabel(QLabel):
    """マウスイベントに対応できるラベルクラス

    マウスクリックとドラッグ時にイベントが発火する
    """

    # コールバック関数はマウスイベント内で呼び出され、イベントが引き継がれる
    def __init__(self, parent=None, handle_event=lambda x: x) -> None:
        super().__init__(parent)
        self.handle_event = handle_event
        self.drawing = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            self.handle_event(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.drawing:
            current_point = event.position().toPoint()
            self.handle_event(event)
            self.last_point = current_point

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
