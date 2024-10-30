import pytest
from unittest.mock import Mock, patch
from PySide6.QtCore import Qt
from gui.views.replay_setting_view import ReplaySettingWindow
from gui.utils.data_store import DataStore


@pytest.fixture
def expected_settings():
    return {
        "video_path": "samples/sample.mp4",  # このファイルは実在する必要がある
        "num_digits": 4,
        "sampling_sec": 10,
        "num_frames": 10,
        "video_skip_sec": 0,
        "format": "csv",
        "save_frame": False,
        "out_dir": "/dummy/path",
        "click_points": [],
    }


@pytest.fixture
def window(qtbot):
    screen_manager = Mock()
    window = ReplaySettingWindow(screen_manager)
    qtbot.addWidget(window)
    window.show()
    return window


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestReplaySettingWindow:
    def setup_class(self):
        get_now_str_patcher = patch(
            "gui.views.replay_setting_view.get_now_str", return_value="now"
        )

        self.mock_get_now_str = get_now_str_patcher.start()

    def teardown_class(self):
        self.mock_get_now_str.stop()

    def setup_method(self):
        self.data_store = DataStore.get_instance()
        self.data_store.clear()

    def test_initial_ui_state(self, window):
        assert window.video_path.text() == ""
        assert window.num_digits.value() == 4
        assert window.sampling_sec.value() == 5
        assert window.num_frames.value() == 30
        assert window.video_skip_sec.value() == 0
        assert window.format.count() > 0
        assert window.save_frame.isChecked() is False

    @patch(
        "gui.views.replay_setting_view.QFileDialog.getOpenFileName",
        return_value=["/dummy/path/video.mp4", ""],
    )
    def test_select_file(self, mock_dialog, window, qtbot):
        qtbot.mouseClick(window.video_path_button, Qt.LeftButton)
        assert window.video_path.text() == "/dummy/path/video.mp4"

    @patch(
        "gui.views.replay_setting_view.QFileDialog.getOpenFileName",
        return_value=["/dummy/path/dammy.json", ""],
    )
    def test_load_setting(self, mock_dialog, window, expected_settings, qtbot):
        next_screen = Mock()
        window.screen_manager.get_screen.return_value = next_screen
        window.settings_manager = Mock()
        window.settings_manager.load.return_value = expected_settings

        qtbot.mouseClick(window.load_button, Qt.LeftButton)

        assert self.data_store.get("out_dir") == "/dummy/now"
        next_screen.trigger.assert_called_once_with("startup")

    def test_next(self, window):
        window.next()
        assert window.confirm_txt.text() != ""

        window.video_path.setText("/dummy/path/video.mp4")
        window.settings_manager = Mock()
        window.settings_manager.validate.return_value = True
        window.next()

        window.screen_manager.get_screen("replay_exe").trigger.assert_called_once()
        assert self.data_store.get("video_path") == window.video_path.text()
        assert self.data_store.get("num_digits") == window.num_digits.value()
        assert self.data_store.get("sampling_sec") == window.sampling_sec.value()
        assert self.data_store.get("num_frames") == window.num_frames.value()
        assert self.data_store.get("video_skip_sec") == window.video_skip_sec.value()
        assert self.data_store.get("format") == window.format.currentText()
        assert self.data_store.get("save_frame") == window.save_frame.isChecked()
