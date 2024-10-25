import pytest
from unittest.mock import MagicMock
from PySide6.QtCore import Qt, QPoint, QPointF
from PySide6.QtGui import QMouseEvent
from gui.widgets.clickable_label import ClickableLabel


@pytest.fixture
def label(qtbot):
    label = ClickableLabel()
    qtbot.addWidget(label)
    label.show()
    return label


def create_mouse_event(event_type, pos, button=Qt.MouseButton.LeftButton):
    return QMouseEvent(
        event_type,
        QPointF(pos),
        QPointF(pos),
        button,
        button,
        Qt.KeyboardModifier.NoModifier
    )


def test_mouse_press_event(label, qtbot):
    mock_callback = MagicMock()
    label.handle_event = mock_callback

    event = create_mouse_event(
        QMouseEvent.Type.MouseButtonPress,
        QPoint(0, 0)
    )
    label.mousePressEvent(event)

    mock_callback.assert_called_once_with(event)
    assert label.drawing == True, "drawing should be True"


def test_mouse_move_event(label, qtbot):
    mock_callback = MagicMock()
    label.handle_event = mock_callback
    label.drawing = True

    event = create_mouse_event(
        QMouseEvent.Type.MouseMove,
        QPoint(10, 10)
    )
    label.mouseMoveEvent(event)

    mock_callback.assert_called_once_with(event)


def test_mouse_release_event(label, qtbot):
    label.drawing = True

    event = create_mouse_event(
        QMouseEvent.Type.MouseButtonRelease,
        QPoint(0, 0)
    )
    label.mouseReleaseEvent(event)

    assert label.drawing == False, "drawing should be False"
