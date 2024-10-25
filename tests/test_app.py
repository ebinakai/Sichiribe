import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from gui.views.splash_view import SplashScreen
from gui.views.main_view import MainWindow


@pytest.fixture()
def app(qtbot):
    """Create an instance of QApplication for the tests."""
    if QApplication.instance() is None:
        app = QApplication([])
    else:
        app = QApplication.instance()

    yield app
    app.quit()


def test_splash_screen(app, qtbot):
    splash_window = SplashScreen()
    qtbot.addWidget(splash_window)

    splash_window.show()
    assert splash_window.isVisible(), "SplashScreen is not visible"

    QTimer.singleShot(20, splash_window.close)
    qtbot.waitUntil(lambda: not splash_window.isVisible(), timeout=30)
    assert not splash_window.isVisible(), "SplashScreen is still visible"


def test_main_window(app, qtbot):
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    main_window.show()
    assert main_window.isVisible(), "MainWindow is not visible"
