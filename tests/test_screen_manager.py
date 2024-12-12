import pytest
from PySide6.QtWidgets import QMainWindow, QStackedWidget
from gui.utils.screen_manager import ScreenManager
from gui.widgets.custom_qwidget import CustomQWidget


@pytest.fixture
def main_window(qtbot):
    window = QMainWindow()
    stacked_widget = QStackedWidget()
    window.setCentralWidget(stacked_widget)
    qtbot.addWidget(window)
    return window, stacked_widget


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestScreenManager:

    class SampleWidget(CustomQWidget):
        def __init__(self):
            super().__init__()

        def initUI(self):
            pass

    def test_add_and_show_screen(self, main_window):
        window, stacked_widget = main_window
        screen_manager = ScreenManager(stacked_widget, window)

        screen1 = self.SampleWidget()
        screen_manager.add_screen("screen1", screen1, "title")

        screen_manager.show_screen("screen1")
        assert stacked_widget.currentWidget() == screen1
        assert window.windowTitle() == "Sichiribe title"

    def test_screen_not_found(self, main_window):
        window, stacked_widget = main_window
        screen_manager = ScreenManager(stacked_widget, window)

        with pytest.raises(ValueError):
            screen_manager.show_screen("non_existent_screen")

    def test_save_and_restore_screen_size(self, main_window):
        window, stacked_widget = main_window
        screen_manager = ScreenManager(stacked_widget, window)
        pos, size = screen_manager.save_screen_size()

        window.resize(800, 600)
        window.move(100, 100)

        screen_manager.restore_screen_size()

        assert window.size() == size
        assert window.frameGeometry().topLeft() == pos
