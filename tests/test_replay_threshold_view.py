import pytest
from unittest.mock import MagicMock
from gui.views.replay_threshold_view import ReplayThresholdWindow
import numpy as np


@pytest.fixture
def window(qtbot):
    screen_manager = MagicMock()
    screen_manager.save_screen_size.return_value = (800, 600)
    window = ReplayThresholdWindow(screen_manager)
    qtbot.addWidget(window)
    window.show()
    window.startup({
        'first_frame': np.zeros((100, 100, 3), dtype=np.uint8),
        'click_points': [[10, 10], [90, 90], [10, 90], [90, 10]]
    })
    return window


@pytest.mark.usefixtures("prevent_window_show")
class TestReplayThresholdWindow:
    def test_initial_ui_state(self, window):
        assert window.binarize_th.value() == 0
        assert window.binarize_th_label.text() == '自動設定'
        assert window.extracted_label.pixmap() is not None

    def test_threshold_update(self, window):
        window.binarize_th.setValue(128)
        assert window.binarize_th_label.text() == '128'
        assert window.extracted_label.pixmap().isNull() == False

        window.binarize_th.setValue(0)
        assert window.binarize_th_label.text() == '自動設定'

    def test_next_button_action(self, window):
        window.binarize_th.setValue(150)
        window.next_button.click()

        window.screen_manager.get_screen.assert_called_with('replay_exe')
        params = window.screen_manager.get_screen().trigger.call_args[0][1]
        assert 'threshold' in params, 'Not found binarize_th in args'
