import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QPoint
from PySide6.QtGui import QMouseEvent
from gui.widgets.clickable_label import ClickableLabel
from tests.test_helper import create_mouse_event


@pytest.fixture(autouse=True)
def prevent_window_show():
    with patch('PySide6.QtWidgets.QWidget.show'):
        yield


@pytest.fixture
def label(qtbot):
    label = ClickableLabel()
    qtbot.addWidget(label)
    label.show()
    return label


class TestClickableLabel:

    def test_mouse_press_event(self, label):
        mock_callback = MagicMock()
        label.handle_event = mock_callback

        event = create_mouse_event(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(0, 0)
        )
        label.mousePressEvent(event)

        mock_callback.assert_called_once_with(event)
        assert label.drawing == True, "drawing should be True"

    def test_mouse_move_event(self, label):
        mock_callback = MagicMock()
        label.handle_event = mock_callback
        label.drawing = True

        event = create_mouse_event(
            QMouseEvent.Type.MouseMove,
            QPoint(10, 10)
        )
        label.mouseMoveEvent(event)

        mock_callback.assert_called_once_with(event)

    def test_mouse_release_event(self, label):
        label.drawing = True

        event = create_mouse_event(
            QMouseEvent.Type.MouseButtonRelease,
            QPoint(0, 0)
        )
        label.mouseReleaseEvent(event)

        assert label.drawing == False, "drawing should be False"
