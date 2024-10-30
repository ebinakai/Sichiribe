from unittest.mock import Mock
from PySide6.QtWidgets import QApplication
import pytest
from gui.widgets.custom_qwidget import CustomQWidget


@pytest.fixture()
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestCustomQWidget:
    def test_init(self, qapp):
        with pytest.raises(NotImplementedError):
            CustomQWidget()

    def test_init_pass(self, qapp):
        CustomQWidget.initUI = Mock()
        CustomQWidget()
        CustomQWidget.initUI.assert_called_once()

    def test_trigger(self, qapp):
        CustomQWidget.initUI = Mock()
        custom_qwidget = CustomQWidget()

        with pytest.raises(NotImplementedError):
            custom_qwidget.trigger("test")
