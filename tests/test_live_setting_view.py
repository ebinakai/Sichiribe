import pytest
from unittest.mock import Mock, patch
from PySide6.QtCore import Qt
from gui.views.live_setting_view import LiveSettingWindow


@pytest.fixture
def expected_params():
    return {
        "device_num": 0,
        "num_digits": 4,
        "sampling_sec": 10,
        "num_frames": 10,
        "total_sampling_sec": 60,
        "format": "csv",
        "save_frame": False,
        "out_dir": "/dummy/path",
    }


@pytest.fixture
def window(qtbot):
    screen_manager = Mock()
    window = LiveSettingWindow(screen_manager)
    qtbot.addWidget(window)
    window.show()
    return window


@pytest.mark.usefixtures("prevent_window_show")
class TestLiveSettingWindow:
    @classmethod
    def setup_class(self):
        self.get_now_str_patcher = patch(
            "gui.views.live_setting_view.get_now_str", return_value="now"
        )
        self.validate_patcher = patch(
            "gui.views.live_setting_view.validate_output_directory", return_value=True
        )
        exporter_patcher = patch("gui.views.live_setting_view.Exporter")

        self.mock_get_now_str = self.get_now_str_patcher.start()
        self.mock_validate = self.validate_patcher.start()
        self.mock_expoter = exporter_patcher.start()

    @classmethod
    def teardown_class(self):
        self.mock_get_now_str.stop()
        self.mock_validate.stop()
        self.mock_expoter.stop()

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
    def test_load_setting(self, mock_dialog, test_data, window, expected_params, qtbot):
        next_screen = Mock()
        window.screen_manager.get_screen.return_value = next_screen
        expected_params["click_points"] = test_data["click_points"]

        with patch(
            "gui.views.live_setting_view.load_setting",
            return_value=expected_params.copy(),
        ):
            qtbot.mouseClick(window.load_button, Qt.LeftButton)

        window.screen_manager.get_screen.assert_called_once_with(
            test_data["expected_screen"]
        )
        expected_params["out_dir"] = "/dummy/now"
        next_screen.trigger.assert_called_once_with("startup", expected_params)

    def test_next_with_empty_folder(self, window, qtbot):
        qtbot.mouseClick(window.next_button, Qt.LeftButton)
        assert window.confirm_txt.text() != ""

    def test_next_with_valid_params(self, window):
        window.out_dir.setText("/dummy/path")
        window.next()
        assert window.confirm_txt.text() == ""

        window.screen_manager.get_screen.assert_called_once_with("live_feed")
        params = window.screen_manager.get_screen("live_feed").trigger.call_args[0][1]
        assert params["device_num"] == 0
        assert params["num_digits"] == 4
        assert params["sampling_sec"] == 10
        assert params["num_frames"] == 10
        assert params["total_sampling_sec"] == 60
        assert params["format"] == window.format.currentText()
        assert params["save_frame"] == window.save_frame.isChecked()
        assert params["out_dir"].startswith("/dummy/path/")
