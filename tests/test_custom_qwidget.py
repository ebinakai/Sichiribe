from unittest.mock import Mock
import pytest
from gui.widgets.custom_qwidget import CustomQWidget


@pytest.mark.usefixtures("prevent_window_show", "qt_test_environment")
class TestCustomQWidget:
    def test_init(self):
        with pytest.raises(NotImplementedError):
            CustomQWidget()

    def test_init_pass(self):
        CustomQWidget.initUI = Mock()
        CustomQWidget()
        CustomQWidget.initUI.assert_called_once()

    def test_trigger(self):
        CustomQWidget.initUI = Mock()
        custom_qwidget = CustomQWidget()

        with pytest.raises(NotImplementedError):
            custom_qwidget.trigger("test")
