import pytest
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from gui.views.splash_view import SplashScreen


@pytest.fixture
def splash_screen(qtbot):
    screen = SplashScreen()
    qtbot.addWidget(screen)
    return screen


@pytest.mark.usefixtures("prevent_window_show")
class TestSplashScreen:
    def test_splash_image_exists(self, splash_screen):
        assert splash_screen.image_path.exists(
        ), f"Not found: {splash_screen.image_path}"

    def test_splash_image_display(self, splash_screen):
        label = splash_screen.findChild(QLabel)
        pixmap = label.pixmap()
        assert isinstance(pixmap, QPixmap)
        assert not pixmap.isNull()
