import pytest
from PySide6.QtCore import Qt
from unittest.mock import MagicMock
from gui.views.menu_view import MenuWindow


@pytest.fixture
def window(qtbot):
    screen_manager = MagicMock()
    window = MenuWindow(screen_manager)
    qtbot.addWidget(window)
    window.show()
    return window


def test_buttons_creation(window):
    assert window.live_button is not None, "Live button is not created"
    assert window.replay_button is not None, "Replay button is not created"
    assert window.quit_button is not None, "Quit button is not created"


def test_live_button_click(window, qtbot):
    qtbot.mouseClick(window.live_button, Qt.LeftButton)
    window.screen_manager.show_screen.assert_called_with('live_setting')


def test_replay_button_click(window, qtbot):
    qtbot.mouseClick(window.replay_button, Qt.LeftButton)
    window.screen_manager.show_screen.assert_called_with('replay_setting')


def test_quit_button_click(window, qtbot):
    qtbot.mouseClick(window.quit_button, Qt.LeftButton)
    window.screen_manager.quit.assert_called_once()
