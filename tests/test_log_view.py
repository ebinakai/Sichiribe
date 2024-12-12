import pytest
from gui.views.log_view import LogWindow


@pytest.fixture
def window(qtbot, mock_screen_manager):
    window = LogWindow(mock_screen_manager)
    qtbot.addWidget(window)
    return window


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestLogWindow:
    def test_initial_ui_state(self, window):
        assert window.log_display.toPlainText() == ""

    def test_log_emission(self, window):
        log_message = "This is a test log message."

        window.emitter.new_log.emit(log_message)

        assert window.log_display.toPlainText() == log_message
