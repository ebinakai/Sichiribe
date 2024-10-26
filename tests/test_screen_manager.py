import pytest
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QLabel
from gui.utils.screen_manager import ScreenManager


@pytest.fixture
def main_window(qtbot):
    window = QMainWindow()
    stacked_widget = QStackedWidget()
    window.setCentralWidget(stacked_widget)
    qtbot.addWidget(window)
    window.show()
    return window, stacked_widget


@pytest.mark.usefixtures("prevent_window_show")
class TestScreenManager:
    def test_add_and_show_screen(self, main_window):
        window, stacked_widget = main_window
        screen_manager = ScreenManager(stacked_widget, window)

        screen1 = QLabel("Screen 1")
        screen_manager.add_screen("screen1", screen1)

        screen_manager.show_screen("screen1")
        assert stacked_widget.currentWidget() == screen1

    def test_screen_not_found(self, main_window, caplog):
        window, stacked_widget = main_window
        screen_manager = ScreenManager(stacked_widget, window)

        screen_manager.show_screen("non_existent_screen")
        assert "Screen 'non_existent_screen' not found" in caplog.text

    def test_save_and_restore_screen_size(self, main_window):
        window, stacked_widget = main_window
        screen_manager = ScreenManager(stacked_widget, window)
        pos, size = screen_manager.save_screen_size()

        window.resize(800, 600)
        window.move(100, 100)

        screen_manager.restore_screen_size()

        assert window.size() == size
        assert window.frameGeometry().topLeft() == pos
