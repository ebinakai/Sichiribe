import pytest
from PySide6.QtWidgets import QStackedWidget
from gui.views.main_view import MainWindow


@pytest.fixture
def window(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    return window


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestMainWindow:
    def test_main_window_title(self, window):
        assert window.windowTitle() != "", "Window title is Empty"

    def test_stacked_widget_initialization(self, window):
        assert isinstance(
            window.centralWidget(), QStackedWidget
        ), "Central widget is not a QStackedWidget"
