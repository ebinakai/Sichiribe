import pytest
from unittest.mock import MagicMock, patch
from gui.views.replay_exe_view import ReplayExeWindow


@pytest.fixture(autouse=True)
def prevent_window_show():
    with patch('PySide6.QtWidgets.QWidget.show'):
        yield


@pytest.fixture
def window(qtbot):
    screen_manager = MagicMock()
    window = ReplayExeWindow(screen_manager)
    window.worker = MagicMock()
    window.params = {}
    window.graph_results = []
    window.graph_failed_rates = []
    window.graph_timestamps = []
    qtbot.addWidget(window)
    window.show()
    return window


def test_initial_ui_state(window):
    assert window.term_label.text() == ""
    assert window.graph_label is not None


def test_cancel_action(window):
    window.cancel()

    window.worker.cancel.assert_called_once()
    assert window.term_label.text() == "中止中..."


def test_frame_devide_finished(window):
    frames = ['frame1', 'frame2']
    timestamps = ['00:01', '00:02']
    window.detect_process = MagicMock()

    window.frame_devide_finished(frames, timestamps)

    assert window.params['frames'] == frames
    assert window.params['timestamps'] == timestamps
    window.detect_process.assert_called_once()


def test_detect_finished(window):
    window.export_process = MagicMock()
    window.results = [1, 2, 3]
    window.failed_rates = [0.1, 0.2, 0.3]
    window.params = {
        'results': window.results,
        'failed_rates': window.failed_rates,
        'timestamps': ["00:01", "00:02", "00:03"]
    }

    window.detect_finished()
    window.export_process.assert_called_once()


def test_update_graph(window):
    window.graph_label = MagicMock()
    window.update_graph(1, 0.2, "00:03")

    assert window.graph_results[-1] == 1
    assert window.graph_failed_rates[-1] == 0.2
    assert window.graph_timestamps[-1] == "00:03"
    window.graph_label.update_existing_plot.assert_called_once()
