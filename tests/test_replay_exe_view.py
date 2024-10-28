import pytest
from unittest.mock import Mock, patch
from gui.views.replay_exe_view import ReplayExeWindow


@pytest.fixture
def window(qtbot):
    screen_manager = Mock()
    window = ReplayExeWindow(screen_manager)
    window.worker = Mock()
    window.params = {}
    window.graph_results = []
    window.graph_failed_rates = []
    window.graph_timestamps = []
    qtbot.addWidget(window)
    window.show()
    return window


@pytest.mark.usefixtures("prevent_window_show")
class TestMethods:
    def test_initial_ui_state(self, window):
        assert window.term_label.text() == ""
        assert window.graph_label is not None

    @patch("gui.views.replay_exe_view.FrameEditor")
    def test_startup(self, mock_frame_editor, window):
        extracted_frame = Mock()
        window.graph_label = Mock()
        mock_frame_editor_instance = Mock()
        mock_frame_editor_instance.frame_devide.return_value = extracted_frame
        mock_frame_editor.return_value = mock_frame_editor_instance
        test_params = {
            "sampling_sec": 5,
            "num_frames": 1,
            "num_digits": 4,
            "video_path": "test.mp4",
            "video_skip_sec": 5,
        }

        window.startup(test_params)

        assert window.graph_label.gen_graph.called_once()
        assert window.term_label.text() == ""
        assert window.results == []
        assert window.failed_rates == []
        assert window.graph_results == []
        assert window.graph_failed_rates == []
        assert window.graph_timestamps == []
        assert window.params["first_frame"] == extracted_frame
        assert mock_frame_editor.called_once()
        assert mock_frame_editor_instance.frame_devide.called_once()
        window.screen_manager.get_screen.assert_called_once_with("region_select")

    @patch("gui.views.replay_exe_view.export_result")
    @patch("gui.views.replay_exe_view.export_params")
    def test_export_process(self, export_params, export_result, window):
        export_result = Mock()
        export_params = Mock()
        window.screen_manager.popup = Mock()
        window.screen_manager.show_screen = Mock()
        window.params = {"out_dir": "test"}

        window.export_process(window.params)

        assert export_result.called_once()
        assert export_params.called_once()
        assert window.screen_manager.popup.called_once()
        window.screen_manager.show_screen.assert_called_once_with("menu")


@pytest.mark.usefixtures("prevent_window_show")
class TestUserActions:
    def test_cancel_action(self, window):
        window.dt_worker = Mock()

        window.cancel()

        window.dt_worker.cancel.assert_called_once()
        assert window.term_label.text() == "中止中..."


@pytest.mark.usefixtures("prevent_window_show")
class TestWorkerCallback:
    @patch("gui.views.replay_exe_view.FrameDivideWorker")
    def test_frame_devide_process(self, worker_class, window):
        worker_instance = Mock()
        worker_class.return_value = worker_instance

        window.frame_devide_process({"test": "test"})

        assert window.params == {"test": "test"}
        assert worker_instance.start.called_once()
        worker_instance.end.connect.assert_called_once_with(
            window.frame_devide_finished
        )
        window.screen_manager.get_screen.assert_called_once_with("log")

    def test_frame_devide_finished(self, window):
        frames = ["frame1", "frame2"]
        timestamps = ["00:01", "00:02"]
        window.detect_process = Mock()

        window.frame_devide_finished(frames, timestamps)

        assert window.params["frames"] == frames
        assert window.params["timestamps"] == timestamps
        window.detect_process.assert_called_once()

    @patch("gui.views.replay_exe_view.DetectWorker")
    def test_detect_process(self, worker_class, window):
        worker_instance = Mock()
        worker_class.return_value = worker_instance

        window.detect_process()

        assert worker_instance.start.called_once()
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

        assert window.clear_env.called_once()
        window.screen_manager.show_screen.assert_called_once_with("menu")

    def test_detect_progress(self, window):
        window.update_graph = Mock()
        window.results = []
        window.failed_rates = []

        window.detect_progress(1, 0.2, "00:03")

        assert window.results[-1] == 1
        assert window.failed_rates[-1] == 0.2
        window.update_graph.assert_called_once()

    def test_detect_finished(self, window):
        window.export_process = Mock()
        window.results = [1, 2, 3]
        window.failed_rates = [0.1, 0.2, 0.3]
        window.params = {
            "results": window.results,
            "failed_rates": window.failed_rates,
            "timestamps": ["00:01", "00:02", "00:03"],
        }

        window.detect_finished()

        window.export_process.assert_called_once()

    def test_detect_cancelled(self, window):
        window.term_label = Mock()
        window.params = {"timestamps": ["00:01", "00:02", "00:03"]}
        window.results = [1]

        window.detect_cancelled()

        assert window.term_label.setText.called_once()
        assert len(window.params["timestamps"]) == len(window.results)

    def test_update_graph(self, window):
        window.graph_label = Mock()
        window.update_graph(1, 0.2, "00:03")

        assert window.graph_results[-1] == 1
        assert window.graph_failed_rates[-1] == 0.2
        assert window.graph_timestamps[-1] == "00:03"
        window.graph_label.update_existing_plot.assert_called_once()
