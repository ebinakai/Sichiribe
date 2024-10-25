import pytest
from PySide6.QtWidgets import QStackedWidget
from gui.views.main_view import MainWindow


@pytest.fixture
def window(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window


def test_main_window_title(window):
    assert window.windowTitle() == 'Sichiribe', "Window title is incorrect"


def test_stacked_widget_initialization(window):
    assert isinstance(window.centralWidget(),
                      QStackedWidget), "Central widget is not a QStackedWidget"
