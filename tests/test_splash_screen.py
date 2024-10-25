import pytest
from unittest.mock import patch
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from gui.views.splash_view import SplashScreen


@pytest.fixture(autouse=True)
def prevent_window_show():
    with patch('PySide6.QtWidgets.QWidget.show'):
        yield


@pytest.fixture
def splash_screen(qtbot):
    screen = SplashScreen()
    qtbot.addWidget(screen)
    return screen


def test_splash_image_exists(splash_screen):
    assert splash_screen.image_path.exists(
    ), f"Not found: {splash_screen.image_path}"


def test_splash_image_display(splash_screen):
    label = splash_screen.findChild(QLabel)
    pixmap = label.pixmap()
    assert isinstance(pixmap, QPixmap)
    assert not pixmap.isNull()
