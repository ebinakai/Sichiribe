import app


class TestApp:
    def test_splash_screen(self, qtbot):
        splash_window = app.SplashScreen()
        qtbot.addWidget(splash_window)

        splash_window.show()
        assert splash_window.isVisible(), "SplashScreen is not visible"

        splash_window.close()
        assert not splash_window.isVisible(), "SplashScreen is still visible"

    def test_main_window(self, qtbot):
        main_window = app.MainWindow()
        qtbot.addWidget(main_window)

        main_window.show()
        assert main_window.isVisible(), "MainWindow is not visible"
        main_window.close()
