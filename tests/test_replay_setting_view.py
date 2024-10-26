import pytest
from unittest.mock import MagicMock, patch
from gui.views.replay_setting_view import ReplaySettingWindow


@pytest.fixture
def window(qtbot):
    screen_manager = MagicMock()
    window = ReplaySettingWindow(screen_manager)
    qtbot.addWidget(window)
    window.show()
    return window


@pytest.mark.usefixtures("prevent_window_show")
class TestReplaySettingWindow:
    def test_initial_ui_state(self, window):
        assert window.video_path.text() == ''
        assert window.num_digits.value() == 4
        assert window.sampling_sec.value() == 5
        assert window.num_frames.value() == 30
        assert window.video_skip_sec.value() == 0
        assert window.format.count() > 0
        assert window.save_frame.isChecked() is False

    def test_select_file(self, window):
        with patch('gui.views.replay_setting_view.QFileDialog.getOpenFileName', return_value=('/dummy/path/video.mp4', '')):
            window.select_file()
            assert window.video_path.text() == '/dummy/path/video.mp4'

    def test_startup_with_empty_video_path(self, window):
        window.startup()
        assert window.confirm_txt.text() == '動画ファイルを選択してください'

    def test_startup_with_valid_params(self, window):
        window.video_path.setText('/dummy/path/video.mp4')
        window.startup()

        assert window.confirm_txt.text() == ''
        window.screen_manager.get_screen(
            'replay_exe').startup.assert_called_once()
        params = window.screen_manager.get_screen(
            'replay_exe').startup.call_args[0][0]

        assert params['video_path'] == '/dummy/path/video.mp4'
        assert params['num_digits'] == 4
        assert params['sampling_sec'] == 5
        assert params['num_frames'] == 30
        assert params['video_skip_sec'] == 0
        assert params['format'] == window.format.currentText()
        assert params['save_frame'] == window.save_frame.isChecked()
