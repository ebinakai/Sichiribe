import pytest
from unittest.mock import MagicMock, patch
from gui.views.live_setting_view import LiveSettingWindow


@pytest.fixture(autouse=True)
def prevent_window_show():
    with patch('PySide6.QtWidgets.QWidget.show'):
        yield


@pytest.fixture
def window(qtbot):
    screen_manager = MagicMock()
    window = LiveSettingWindow(screen_manager)
    qtbot.addWidget(window)
    window.show()
    return window


def test_initial_ui_state(window):
    assert window.device_num.value() == 0
    assert window.num_digits.value() == 4
    assert window.sampling_sec.value() == 10
    assert window.num_frames.value() == 10
    assert window.total_sampling_min.value() == 1
    assert window.format.count() > 0
    assert window.save_frame.isChecked() is False


def test_select_folder(window, mocker):
    mocker.patch(
        'gui.views.live_setting_view.QFileDialog.getExistingDirectory',
        return_value='/dummy/path')
    window.select_folder()
    assert window.out_dir.text() == '/dummy/path'


def test_calc_max_frames(window):
    window.sampling_sec.setValue(10)
    window.calc_max_frames()
    assert window.num_frames.maximum() == 50


def test_startup_with_empty_folder(window):
    window.startup()
    assert window.confirm_txt.text() == '保存場所を選択してください'


def test_startup_with_valid_params(window):
    window.out_dir.setText('/dummy/path')
    window.startup()
    assert window.confirm_txt.text() == ''

    window.screen_manager.get_screen.assert_called_once_with('live_feed')
    params = window.screen_manager.get_screen(
        'live_feed').startup.call_args[0][0]
    assert params['device_num'] == 0
    assert params['num_digits'] == 4
    assert params['sampling_sec'] == 10
    assert params['num_frames'] == 10
    assert params['total_sampling_sec'] == 60
    assert params['format'] == window.format.currentText()
    assert params['save_frame'] == window.save_frame.isChecked()
    assert params['out_dir'].startswith('/dummy/path/')
