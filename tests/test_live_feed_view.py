import pytest
from unittest.mock import MagicMock, patch
from gui.utils.screen_manager import ScreenManager
from gui.views.live_feed_view import LiveFeedWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import numpy as np


@pytest.fixture(autouse=True)
def prevent_window_show():
    with patch('PySide6.QtWidgets.QWidget.show'):
        yield


@pytest.fixture
def window(qtbot):
    screen_manager = MagicMock(spec=ScreenManager)
    window = LiveFeedWindow(screen_manager)
    window.params = {}
    qtbot.addWidget(window)
    window.show()
    return window


def test_initial_ui_state(window):
    assert window.feed_label.text() == ""


def test_back_button(window, qtbot):
    window.worker = MagicMock()
    qtbot.mouseClick(window.back_button, Qt.MouseButton.LeftButton)
    window.worker.cancel.assert_called_once()


def test_next_button(window, qtbot):
    window.worker = MagicMock()
    qtbot.mouseClick(window.next_button, Qt.MouseButton.LeftButton)
    window.worker.stop.assert_called_once()


def test_feed_finished(window, qtbot):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    window.feed_finished(frame)

    qtbot.wait(20)
    window.screen_manager.get_screen.assert_called_once_with("region_select")


def test_feed_error(window):
    window.feed_error()
    window.screen_manager.popup.assert_called_once_with("カメラにアクセスできませんでした")


def test_clear_env(window):
    window.feed_label.setPixmap(QPixmap(10, 10))
    window.clear_env()

    assert window.feed_label.pixmap().isNull()
    assert window.target_width is None
    assert window.target_height is None
    assert window.params is None
