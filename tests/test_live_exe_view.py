import pytest
from unittest.mock import MagicMock
from gui.views.live_exe_view import LiveExeWindow
import numpy as np


@pytest.fixture
def window(qtbot):
    screen_manager = MagicMock()
    window = LiveExeWindow(screen_manager)
    window.params = {}
    qtbot.addWidget(window)
    window.show()
    return window


def test_initial_ui_state(window):
    assert window.extracted_label.pixmap().isNull()
    assert window.term_label.text() == ""
    assert window.binarize_th.value() == 0
    assert window.binarize_th_label.text() == ""


def test_cancel_action(window):
    window.worker = MagicMock()
    window.cancel()

    window.worker.cancel.assert_called_once()
    assert window.term_label.text() == "中止中..."


def test_update_binarize_th(window):
    window.worker = MagicMock()
    window.update_binarize_th(100)

    assert window.binarize_th_label.text() == "100"
    window.worker.update_binarize_th.assert_called_once_with(100)


def test_graph_clear(window):
    window.results = [1]
    window.failed_rates = [0.1]
    window.timestamps = ["00:00:00"]
    window.graph_label = MagicMock()
    window.graph_clear()

    window.graph_label.update_existing_plot.assert_called_once()
    assert window.graph_results == [1]
    assert window.graph_failed_rates == [0.1]
    assert window.graph_timestamps == ["00:00:00"]


def test_detect_finished(window):
    window.worker = MagicMock()
    window.export_process = MagicMock()
    window.results = [1, 2, 3]
    window.failed_rates = [0.1, 0.2, 0.3]
    window.timestamps = ["00:01", "00:02", "00:03"]

    window.detect_finished()
    window.export_process.assert_called_once_with({
        'results': [1, 2, 3],
        'failed_rates': [0.1, 0.2, 0.3],
        'timestamps': ["00:01", "00:02", "00:03"]
    })


def test_display_extract_image(window):
    sample_image = np.zeros((100, 100, 3), dtype=np.uint8)
    window.display_extract_image(sample_image)

    assert window.extracted_label.pixmap() is not None
    assert not window.extracted_label.pixmap().isNull()
