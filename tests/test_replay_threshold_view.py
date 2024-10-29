import pytest
from unittest.mock import Mock
from gui.views.replay_threshold_view import ReplayThresholdWindow
from gui.utils.data_store import DataStore
import numpy as np


@pytest.fixture
def window(qtbot):
    screen_manager = Mock()
    screen_manager.save_screen_size.return_value = (800, 600)
    window = ReplayThresholdWindow(screen_manager)
    qtbot.addWidget(window)
    window.first_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    window.show()
    return window


@pytest.mark.usefixtures("prevent_window_show")
class TestReplayThresholdWindow:
    def setup_method(self):
        self.data_store = DataStore.get_instance()
        self.data_store.clear()

    def test_initial_ui_state(self, window):
        assert window.binarize_th.value() == 0
        assert window.binarize_th_label.text() == "自動設定"
        assert window.extracted_label.pixmap() is not None

    def test_trigger(self, window):
        window.startup = Mock()
        window.trigger("startup")

        assert window.startup.called_once()

        with pytest.raises(ValueError):
            window.trigger("invalid")

    def test_threshold_update(self, window):
        window.binarize_th.setValue(128)
        assert window.binarize_th_label.text() == "128"
        assert window.extracted_label.pixmap().isNull() == False

        window.binarize_th.setValue(0)
        assert window.binarize_th_label.text() == "自動設定"

    def test_next_button_action(self, window):
        window.binarize_th.setValue(150)
        window.next_button.click()

        assert self.data_store.get("threshold") == 150
        window.screen_manager.get_screen.assert_called_with("replay_exe")
