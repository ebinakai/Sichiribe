import pytest
from unittest.mock import Mock, patch
from gui.views.live_feed_view import LiveFeedWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import numpy as np


@pytest.fixture
def window(qtbot, mock_screen_manager):
    window = LiveFeedWindow(mock_screen_manager)
    qtbot.addWidget(window)
    window.show()
    return window


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestLiveFeedWindow:
    def test_initial_ui_state(self, window):
        assert window.feed_label.text() == ""

    def test_trigger(self, window):
        window.startup = Mock()
        window.trigger("startup")

        window.startup.assert_called_once_with()

        with pytest.raises(ValueError):
            window.trigger("invalid")

    @patch("gui.views.live_feed_view.LiveFeedWorker")
    def test_startup(self, mock_worker_class, window):
        mock_worker_instance = Mock()
        mock_worker_class.return_value = mock_worker_instance
        window.screen_manager.save_screen_size.return_value = (1920, 1080)

        window.startup()

        assert window.results == []
        assert window.failed_rates == []
        assert window.feed_label.text() != ""
        window.screen_manager.save_screen_size.assert_called_once()
        window.screen_manager.show_screen.assert_called_once_with("live_feed")
        mock_worker_class.assert_called_once()
        mock_worker_instance.cap_size.connect.assert_called_once_with(
            window.recieve_cap_size
        )
        mock_worker_instance.progress.connect.assert_called_once_with(window.show_feed)
        mock_worker_instance.end.connect.assert_called_once_with(window.feed_finished)
        mock_worker_instance.cancelled.connect.assert_called_once_with(
            window.feed_cancelled
        )
        mock_worker_instance.error.connect.assert_called_once_with(window.feed_error)
        mock_worker_instance.start.assert_called_once()

    def test_back_button(self, window, qtbot):
        window.worker = Mock()
        qtbot.mouseClick(window.back_button, Qt.MouseButton.LeftButton)
        window.worker.cancel.assert_called_once()

    def test_next_button(self, window, qtbot):
        window.worker = Mock()
        qtbot.mouseClick(window.next_button, Qt.MouseButton.LeftButton)
        window.worker.stop.assert_called_once()

    def test_feed_finished(self, window, qtbot):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        window.feed_finished(frame)

        qtbot.wait(20)
        window.screen_manager.get_screen.assert_called_once_with("region_select")

    def test_feed_error(self, window):
        window.feed_error()
        window.screen_manager.popup.assert_called_once_with(
            "カメラにアクセスできませんでした"
        )

    def test_clear_env(self, window):
        window.feed_label.setPixmap(QPixmap(10, 10))
        window.clear_env()

        assert window.feed_label.pixmap().isNull()
