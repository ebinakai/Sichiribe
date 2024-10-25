import pytest
from unittest.mock import MagicMock
from gui.utils.screen_manager import ScreenManager
from gui.views.log_view import LogWindow


@pytest.fixture
def window(qtbot):
    screen_manager = MagicMock(spec=ScreenManager)
    window = LogWindow(screen_manager)
    qtbot.addWidget(window)
    window.show()
    return window


def test_initial_ui_state(window):
    assert window.log_display.toPlainText() == ''


def test_log_emission(window, qtbot):
    log_message = "This is a test log message."

    window.emitter.new_log.emit(log_message)

    assert window.log_display.toPlainText() == log_message


def test_clear_log(window, qtbot):
    log_message = "Another test log message."
    window.emitter.new_log.emit(log_message)
    assert window.log_display.toPlainText() == log_message

    window.clear_log()
    assert window.log_display.toPlainText() == ''
