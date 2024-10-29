import pytest
from unittest.mock import Mock
from gui.views.live_exe_view import LiveExeWindow
import numpy as np
from datetime import timedelta


@pytest.fixture
def window(qtbot, mock_screen_manager):
    window = LiveExeWindow(mock_screen_manager)
    window.results = []
    window.failed_rates = []
    window.timestamps = []
    window.graph_results = []
    window.graph_failed_rates = []
    window.graph_timestamps = []
    qtbot.addWidget(window)
    return window


@pytest.mark.usefixtures("prevent_window_show")
class TestMethods:
    def test_initial_ui_state(self, window):
        assert (
            window.extracted_label.pixmap() is None
            or window.extracted_label.pixmap().isNull()
        )
        assert window.term_label.text() == ""
        assert window.binarize_th.value() == 0
        assert window.binarize_th_label.text() == ""
        assert window.binarize_th.minimum() == 0
        assert window.binarize_th.maximum() == 255
        assert window.graph_label is not None

    def test_trigger(self, window):
        window.startup = Mock()
        window.trigger("startup")

        window.startup.assert_called_once()

        with pytest.raises(ValueError):
            window.trigger("invalid")

    def test_display_extract_image(self, window):
        sample_image = np.zeros((100, 100, 3), dtype=np.uint8)
        window.display_extract_image(sample_image)

        assert window.extracted_label.pixmap() is not None
        assert not window.extracted_label.pixmap().isNull()

    def test_detect_progress_updates(self, window):
        window.graph_label = Mock()
        result, failed_rate, timestamp = 42, 0.15, "10:00:00"

        window.detect_progress(result, failed_rate, timestamp)
        assert window.results == [42]
        assert window.failed_rates == [0.15]
        assert window.timestamps == ["10:00:00"]
        assert window.graph_results == [42]
        assert window.graph_failed_rates == [0.15]
        assert window.graph_timestamps == ["10:00:00"]

        window.detect_progress(result, failed_rate, timestamp)
        assert window.results == [42, 42]
        assert window.failed_rates == [0.15, 0.15]
        assert window.timestamps == ["10:00:00", "10:00:00"]
        assert window.graph_results == [42, 42]
        assert window.graph_failed_rates == [0.15, 0.15]
        assert window.graph_timestamps == ["10:00:00", "10:00:00"]


@pytest.mark.usefixtures("prevent_window_show")
class TestUserActions:
    def test_cancel_action(self, window):
        window.worker = Mock()
        window.cancel()

        assert window.worker.cancel.called_once()
        assert window.term_label.text() == "中止中..."

    @pytest.mark.parametrize(
        "value, expected_text", [(0, "自動設定"), (100, "100"), (255, "255")]
    )
    def test_binarize_threshold_update(self, window, value, expected_text):
        window.worker = Mock()
        window.update_binarize_th(value)
        expected_value = None if value == 0 else value

        assert window.binarize_th_label.text() == expected_text
        window.worker.update_binarize_th.assert_called_once_with(expected_value)

    def test_graph_clear(self, window):
        window.results = [1, 2, 3]
        window.failed_rates = [0.1, 0.2, 0.3]
        window.timestamps = ["00:00:01", "00:00:02", "00:00:03"]
        window.graph_label = Mock()

        window.graph_results = window.results.copy()
        window.graph_failed_rates = window.failed_rates.copy()
        window.graph_timestamps = window.timestamps.copy()
        window.graph_clear()

        assert len(window.graph_results) == 1
        assert len(window.graph_failed_rates) == 1
        assert len(window.graph_timestamps) == 1
        window.graph_label.update_existing_plot.assert_called_once_with(
            ["00:00:03"], [0.3], [3]
        )


@pytest.mark.usefixtures("prevent_window_show")
class TestWorkerCallbacks:
    def test_display_extract_image(self, window):
        window.display_extract_image(np.zeros((100, 100, 3), dtype=np.uint8))
        assert not window.extracted_label.pixmap().isNull()

    def test_remaining_time(self, window):
        window.update_remaining_time(10.2)
        assert window.remaining_time_label.text() == str(timedelta(seconds=int(10.4)))

        window.update_remaining_time(14.5)
        assert window.remaining_time_label.text() != str(timedelta(seconds=int(10.4)))

    def test_model_not_found(self, window):
        window.clear_env = Mock()
        window.model_not_found()
        window.screen_manager.show_screen.assert_called_with("menu")
        window.clear_env.assert_called_once()
