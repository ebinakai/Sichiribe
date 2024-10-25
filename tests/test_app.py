from gui.views.splash_view import SplashScreen
from gui.views.main_view import MainWindow


def test_splash_screen(qtbot):
    splash_window = SplashScreen()
    qtbot.addWidget(splash_window)

    splash_window.show()
    assert splash_window.isVisible(), "SplashScreen is not visible"

    splash_window.close()
    assert not splash_window.isVisible(), "SplashScreen is still visible"


def test_main_window(qtbot):
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    main_window.show()
    assert main_window.isVisible(), "MainWindow is not visible"
    main_window.close()
