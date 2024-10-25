import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import Qt
from gui.views.live_exe_view import LiveExeWindow
import numpy as np


@pytest.fixture(autouse=True)
def prevent_window_show():
    with patch('PySide6.QtWidgets.QWidget.show'):
        yield


@pytest.fixture
def mock_screen_manager():
    manager = MagicMock()
    manager.check_if_dark_mode.return_value = False
    return manager


@pytest.fixture
def window(qtbot, mock_screen_manager):
    """Initialize test window with mocked dependencies"""
    window = LiveExeWindow(mock_screen_manager)
    # 必要な初期化を追加
    window.results = []
    window.failed_rates = []
    window.timestamps = []
    window.graph_results = []
    window.graph_failed_rates = []
    window.graph_timestamps = []
    window.params = {}
    qtbot.addWidget(window)
    return window


class TestUIInitialization:
    """Test cases for UI initialization"""

    def test_initial_state(self, window):
        """Test initial state of UI components"""
        assert window.extracted_label.pixmap(
        ) is None or window.extracted_label.pixmap().isNull()
        assert window.term_label.text() == ""
        assert window.binarize_th.value() == 0
        assert window.binarize_th_label.text() == ""

    def test_slider_configuration(self, window):
        """Test slider widget configuration"""
        assert window.binarize_th.minimum() == 0
        assert window.binarize_th.maximum() == 255
        assert window.binarize_th.orientation() == Qt.Orientation.Horizontal


class TestUserActions:
    """Test cases for user interactions"""

    def test_cancel_action(self, window):
        """Test cancel button functionality"""
        window.worker = MagicMock()
        window.cancel()

        window.worker.cancel.assert_called_once()
        assert window.term_label.text() == "中止中..."

    @pytest.mark.parametrize("value,expected_text", [
        (0, "自動設定"),
        (100, "100"),
        (255, "255")
    ])
    def test_binarize_threshold_update(self, window, value, expected_text):
        """Test threshold slider updates"""
        window.worker = MagicMock()
        window.update_binarize_th(value)

        assert window.binarize_th_label.text() == expected_text
        expected_value = None if value == 0 else value
        window.worker.update_binarize_th.assert_called_once_with(
            expected_value)

    def test_graph_clear(self, window):
        """Test graph clearing functionality"""
        # Setup test data
        window.results = [1, 2, 3]
        window.failed_rates = [0.1, 0.2, 0.3]
        window.timestamps = ["00:00:01", "00:00:02", "00:00:03"]
        window.graph_label = MagicMock()

        # 元のデータを保持するように変更
        window.graph_results = window.results.copy()
        window.graph_failed_rates = window.failed_rates.copy()
        window.graph_timestamps = window.timestamps.copy()

        window.graph_clear()

        # グラフデータがクリアされることを確認
        assert len(window.graph_results) == 1
        assert len(window.graph_failed_rates) == 1
        assert len(window.graph_timestamps) == 1
        window.graph_label.update_existing_plot.assert_called_once_with(
            ["00:00:03"], [0.3], [3])


class TestDetectionProcess:
    """Test cases for detection process"""

    def test_detect_finished(self, window):
        """Test detection completion handling"""
        window.results = [1, 2, 3]
        window.failed_rates = [0.1, 0.2, 0.3]
        window.timestamps = ["00:01", "00:02", "00:03"]
        window.export_process = MagicMock()
        window.graph_label = MagicMock()

        window.detect_finished()

        expected_params = {
            'results': [1, 2, 3],
            'failed_rates': [0.1, 0.2, 0.3],
            'timestamps': ["00:01", "00:02", "00:03"]
        }
        window.export_process.assert_called_once_with(expected_params)

    def test_detect_cancelled(self, window):
        """Test detection cancellation handling"""
        window.detect_cancelled()
        assert window.term_label.text() == "中止しました"

    def test_model_not_found(self, window):
        """Test model not found error handling"""
        # clear_env をモック化して環境クリアを防ぐ
        with patch.object(window, 'clear_env'):
            window.model_not_found()
            assert window.term_label.text() == "モデルが見つかりません"
            window.screen_manager.show_screen.assert_called_with('menu')


class TestImageHandling:
    """Test cases for image processing"""

    def test_display_extract_image(self, window):
        """Test image display functionality"""
        sample_image = np.zeros((100, 100, 3), dtype=np.uint8)
        window.display_extract_image(sample_image)

        assert window.extracted_label.pixmap() is not None
        assert not window.extracted_label.pixmap().isNull()

    def test_detect_progress_updates(self, window):
        """Test progress updates during detection"""
        # 必要な属性の初期化
        window.results = []
        window.failed_rates = []
        window.timestamps = []
        window.graph_results = []
        window.graph_failed_rates = []
        window.graph_timestamps = []
        window.graph_label = MagicMock()

        result, failed_rate, timestamp = 42, 0.15, "10:00:00"
        window.detect_progress(result, failed_rate, timestamp)

        # 結果の検証
        assert window.results == [42]
        assert window.failed_rates == [0.15]
        assert window.timestamps == ["10:00:00"]
        assert window.graph_results == [42]
        assert window.graph_failed_rates == [0.15]
        assert window.graph_timestamps == ["10:00:00"]
        window.screen_manager.show_screen.assert_called_with('live_exe')
