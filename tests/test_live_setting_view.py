import pytest
from unittest.mock import Mock, patch
from PySide6.QtCore import Qt
from gui.views.live_setting_view import LiveSettingWindow
from gui.utils.data_store import DataStore
import os


@pytest.fixture
def window(qtbot, mock_screen_manager):
    window = LiveSettingWindow(mock_screen_manager)
    qtbot.addWidget(window)
    window.show()
    return window


@pytest.mark.usefixtures("prevent_window_show")
class TestLiveSettingWindow:
    def setup_class(self):
        self.get_now_str_patcher = patch(
            "gui.views.live_setting_view.get_now_str", return_value="now"
        )
        self.mock_get_now_str = self.get_now_str_patcher.start()
        os.makedirs("dummy/dummy", exist_ok=True)

    def teardown_class(self):
        self.mock_get_now_str.stop()
        os.removedirs("dummy/dummy")

    def setup_method(self):
        self.data_store = DataStore.get_instance()
        self.data_store.clear()

    def test_initial_ui_state(self, window):
        assert window.device_num.value() == 0
        assert window.num_digits.value() == 4
        assert window.sampling_sec.value() == 10
        assert window.num_frames.value() == 10
        assert window.total_sampling_min.value() == 1
        assert window.format.count() > 0
        assert window.save_frame.isChecked() is False

    @patch(
        "gui.views.live_setting_view.QFileDialog.getExistingDirectory",
        return_value="/dummy/path",
    )
    def test_select_folder(self, mock_dialog, window, qtbot):
        qtbot.mouseClick(window.out_dir_button, Qt.LeftButton)
        assert window.out_dir.text() == "/dummy/path"

    def test_calc_max_frames(self, window):
        window.sampling_sec.setValue(10)
        window.calc_max_frames()
        assert window.num_frames.maximum() == 50

    @pytest.mark.parametrize(
        "test_data",
        [
            {"click_points": [1, 2, 3, 4], "expected_screen": "live_exe"},
            {"click_points": [], "expected_screen": "live_feed"},
        ],
    )
    @patch(
        "gui.views.live_setting_view.QFileDialog.getOpenFileName",
        return_value=["/dummy/path.json", ""],
    )
    def test_load_setting(self, mock_dialog, test_data, window, qtbot):
        window.screen_manager.get_screen.return_value = Mock()
        self.data_store.set("click_points", test_data["click_points"])
        window.settings_manager = Mock()
        window.settings_manager.validate.return_value = True
        window.settings_manager.load.return_value = {
            "out_dir": "/dummy/path",
            "click_points": test_data["click_points"],
            "cap_size": [100, 100],
        }

        window.load_setting()

        assert self.data_store.get("out_dir") == "/dummy/now"
        window.screen_manager.get_screen.assert_called_once_with(
            test_data["expected_screen"]
        )

    def test_next(self, window):
        window.out_dir.setText("dummy")
        window.next()
        assert window.confirm_txt.text() == ""

        window.screen_manager.get_screen.assert_called_once_with("live_feed")

        assert self.data_store.get("device_num") == window.device_num.value()
        assert self.data_store.get("num_digits") == window.num_digits.value()
        assert self.data_store.get("sampling_sec") == window.sampling_sec.value()
        assert self.data_store.get("num_frames") == window.num_frames.value()
        assert (
            self.data_store.get("total_sampling_sec")
            == window.total_sampling_min.value() * 60
        )
        assert self.data_store.get("format") == window.format.currentText()
        assert self.data_store.get("save_frame") == window.save_frame.isChecked()
        assert self.data_store.get("out_dir").endswith("dummy/now")

    def test_next_with_empty_folder(self, window, qtbot):
        qtbot.mouseClick(window.next_button, Qt.LeftButton)
        assert window.confirm_txt.text() != ""
