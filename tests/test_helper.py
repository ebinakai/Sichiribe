from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QMouseEvent


def create_mouse_event(event_type, pos, button=Qt.MouseButton.LeftButton):
    return QMouseEvent(
        event_type,
        QPointF(pos),
        QPointF(pos),
        button,
        button,
        Qt.KeyboardModifier.NoModifier
    )
