import pytest
from unittest.mock import Mock
from gui.views.log_view import LogWindow


@pytest.fixture
def window(qtbot):
    screen_manager = Mock()
    window = LogWindow(screen_manager)
    qtbot.addWidget(window)
    window.show()
    return window


@pytest.mark.usefixtures("prevent_window_show")
class TestLogWindow:
    def test_initial_ui_state(self, window):
        assert window.log_display.toPlainText() == ""

    def test_trigger(self, window):
        window.clear_log = Mock()
        expected_output = "This is a test log message."
        window.trigger("clear")
        assert window.clear_log.called_once()

        with pytest.raises(ValueError):
            window.trigger("invalid", expected_output)

    def test_log_emission(self, window):
        log_message = "This is a test log message."

        window.emitter.new_log.emit(log_message)

        assert window.log_display.toPlainText() == log_message

    def test_clear_log(self, window):
        log_message = "Another test log message."
        window.emitter.new_log.emit(log_message)
        assert window.log_display.toPlainText() == log_message

        window.clear_log()
        assert window.log_display.toPlainText() == ""
