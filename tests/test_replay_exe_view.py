import pytest
from unittest.mock import Mock, patch, MagicMock
from gui.views.replay_exe_view import ReplayExeWindow
from gui.utils.data_store import DataStore
from cores.frame_editor import FrameEditor
import numpy as np


@pytest.fixture
def window(qtbot):
    screen_manager = Mock()
    window = ReplayExeWindow(screen_manager)
    window.worker = Mock()
    window.graph_results = []
    window.graph_failed_rates = []
    window.graph_timestamps = []
    window.fe = FrameEditor()
    qtbot.addWidget(window)
    return window


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestMethods:
    def setup_method(self):
        self.data_store = DataStore.get_instance()
        self.data_store.clear()
        self.data_store.set("sampling_sec", 10)
        self.data_store.set("batch_frames", 10)
        self.data_store.set("num_digits", 4)
        self.data_store.set("video_path", "dummy/path.mp4")
        self.data_store.set("video_skip_sec", 0)
        self.data_store.set("out_dir", "dummy/out_dir")

    def test_initial_ui_state(self, window):
        assert (
            window.extracted_label.pixmap() is None
            or window.extracted_label.pixmap().isNull()
        )
        assert window.term_label.text() == ""
        assert window.graph_label is not None

    def test_trigger(self, window):
        window.startup = Mock()
        window.trigger("startup")

        window.startup.assert_called_once_with()

        window.detect_start = Mock()
        window.trigger("continue")
        window.detect_start.assert_called_once()

        with pytest.raises(ValueError):
            window.trigger("invalid")

    @patch("gui.views.replay_exe_view.FrameEditor")
    def test_startup(self, mock_frame_editor, window):
        iter = MagicMock()
        iter.__next__.return_value = (Mock(), "00:00:00")
        window.graph_label = Mock()
        mock_frame_editor_instance = MagicMock()
        mock_frame_editor_instance.frame_devide_generator.return_value = iter
        mock_frame_editor.return_value = mock_frame_editor_instance

        window.startup()

        window.graph_label.gen_graph.assert_called_once()
        assert window.term_label.text() == ""
        assert window.results == []
        assert window.failed_rates == []
        assert window.graph_results == []
        assert window.graph_failed_rates == []
        assert window.graph_timestamps == []
        mock_frame_editor.assert_called_once()
        mock_frame_editor_instance.frame_devide_generator.assert_called_once()
        window.screen_manager.get_screen.assert_called_once_with("region_select")

    @patch("gui.views.replay_exe_view.export_result")
    @patch("gui.views.replay_exe_view.export_settings")
    def test_export(self, export_settings, export_result, window):
        self.data_store.set("out_dir", "test")
        window.settings_manager.save = Mock()

        window.export()

        export_result.assert_called_once()
        export_settings.assert_called_once()
        window.screen_manager.popup.assert_called_once()


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestUserActions:
    def test_cancel_action(self, window):
        window.dt_worker = Mock()

        window.cancel()

        window.dt_worker.cancel.assert_called_once()
        assert window.term_label.text() == "中止中..."


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestWorkerCallback:
    def setup_class(self):
        self.data_store = DataStore.get_instance()
        self.data_store.clear()

    @patch("gui.views.replay_exe_view.DetectWorker")
    def test_detect_start(self, worker_class, window):
        worker_instance = Mock()
        worker_class.return_value = worker_instance

        window.detect_start()

        worker_instance.start.assert_called_once()
        worker_instance.progress.connect.assert_called_once_with(window.detect_progress)
        worker_instance.finished.connect.assert_called_once_with(window.detect_finished)
        worker_instance.cancelled.connect.assert_called_once_with(
            window.detect_cancelled
        )
        worker_instance.model_not_found.connect.assert_called_once_with(
            window.model_not_found
        )

    def test_model_not_found(self, window):
        window.clear_env = Mock()

        window.model_not_found()

        window.clear_env.assert_called_once()
        window.screen_manager.show_screen.assert_called_once_with("menu")

    def test_detect_progress(self, window):
        window.update_graph = Mock()
        window.results = []
        window.failed_rates = []

        window.detect_progress(1, 0.2, "00:03")

        assert window.results[-1] == 1
        assert window.failed_rates[-1] == 0.2
        window.update_graph.assert_called_once()

    def test_display_extract_image(self, window):
        window.display_extract_image(np.zeros((100, 100, 3), dtype=np.uint8))
        assert not window.extracted_label.pixmap().isNull()

    def test_detect_finished(self, window):
        window.export = Mock()
        window.results = [1, 2, 3]
        window.failed_rates = [0.1, 0.2, 0.3]

        window.detect_finished()

        assert self.data_store.get("results") == window.results
        assert self.data_store.get("failed_rates") == window.failed_rates
        window.export.assert_called_once()

    def test_detect_cancelled(self, window):
        window.term_label = Mock()
        self.data_store.set("timestamps", ["00:01", "00:02", "00:03"])
        window.results = [1]

        window.detect_cancelled()

        window.term_label.setText.assert_called_once()
        assert len(self.data_store.get("timestamps")) == len(window.results)

    def test_update_graph(self, window):
        window.graph_label = Mock()
        window.update_graph(1, 0.2, "00:03")

        assert window.graph_results[-1] == 1
        assert window.graph_failed_rates[-1] == 0.2
        assert window.graph_timestamps[-1] == "00:03"
        window.graph_label.update_existing_plot.assert_called_once()
