import pytest
from unittest.mock import Mock, patch
import numpy as np
from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QMouseEvent
from gui.views.region_select_view import RegionSelectWindow
from gui.utils.data_store import DataStore
from tests.test_helper import create_mouse_event


@pytest.fixture
def mock_frame_editor():
    with patch("gui.views.region_select_view") as mock:
        editor = mock.return_value
        editor.order_points.return_value = [[0, 0], [100, 0], [100, 100], [0, 100]]
        editor.crop.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        editor.draw_region_outline.return_value = (
            np.zeros((200, 200, 3), dtype=np.uint8),
            np.zeros((100, 100, 3), dtype=np.uint8),
        )
        yield editor


@pytest.fixture
def window(qtbot, mock_screen_manager, mock_frame_editor):
    with patch("PySide6.QtWidgets.QApplication.primaryScreen") as mock_screen:
        mock_geometry = Mock()
        mock_geometry.width.return_value = 1920
        mock_geometry.height.return_value = 1080
        mock_screen.return_value.availableGeometry.return_value = mock_geometry

        window = RegionSelectWindow(mock_screen_manager)
        window.fe = mock_frame_editor
        qtbot.addWidget(window)
        return window


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestSelectRegionWindow:
    def setup_method(self):
        self.data_store = DataStore.get_instance()
        self.data_store.clear()

    def test_initial_ui_state(self, window):
        assert len(window.click_points) == 0
        assert window.main_label is not None
        assert window.extracted_label is not None
        assert window.back_button is not None
        assert window.confirm_txt is not None
        assert window.back_button is not None
        assert window.next_button is not None

    def test_trigger(self, window):
        window.startup = Mock()
        window.trigger("startup")

        with pytest.raises(ValueError):
            window.trigger("invalid")

    def test_startup(self, window):
        self.data_store.set("num_digits", 2)
        self.data_store.set("first_frame", np.zeros((480, 640, 3), dtype=np.uint8))
        window.startup("replay_exe")

        assert window.prev_screen == "replay_exe"
        assert window.fe is not None
        assert window.screen_manager.save_screen_size.called_once()
        window.screen_manager.show_screen.assert_called_with("region_select")

    def test_label_clicked_add_points(self, window):
        window.image_size = QSize(200, 200)
        window.image = np.zeros((200, 200, 3), dtype=np.uint8)
        window.image_original = np.zeros((200, 200, 3), dtype=np.uint8)
        window.resize_scale = 1.0

        points = [(50, 50), (150, 50), (150, 150), (50, 150)]
        for x, y in points:
            event = create_mouse_event(QMouseEvent.Type.MouseButtonPress, QPoint(x, y))
            window.label_clicked(event)

        assert len(window.click_points) == 4
        assert window.fe.order_points.called_once()

    def test_finish_select_with_incomplete_points(self, window):
        window.click_points = [(50, 50)]
        window.finish_select()

        assert window.confirm_txt.text() != ""

    def test_finish_select_success(self, window):
        self.data_store.set("num_digits", 4)
        window.prev_screen = "replay_exe"
        window.resize_scale = 1.0
        window.click_points = [(0, 0), (100, 0), (100, 100), (0, 100)]
        window.finish_select()

        assert self.data_store.get("click_points")
        assert len(self.data_store.get("click_points")) == 4

    def test_cancel_select(self, window):
        window.prev_screen = "replay_exe"

        window.cancel_select()
        assert window.click_points == []
        assert window.confirm_txt.text() == ""

    def test_switch_back(self, window):
        window.prev_screen = "live_feed"
        window.switch_back()
        window.screen_manager.get_screen.assert_called_with("live_feed")

        window.prev_screen = "replay_exe"
        window.switch_back()
        window.screen_manager.show_screen.assert_called_with("replay_setting")

    def test_switch_next(self, window):
        window.prev_screen = "live_feed"
        window.switch_next()
        window.screen_manager.get_screen.assert_called_with("live_exe")

        window.prev_screen = "replay_exe"
        window.switch_next()
        window.screen_manager.get_screen.assert_called_with("replay_threshold")

    def test_clear_env(self, window):
        window.click_points = [(0, 0), (1, 1)]
        window.confirm_txt.setText("テストメッセージ")

        window.clear_env()
        assert window.click_points == []
        assert window.confirm_txt.text() == ""
