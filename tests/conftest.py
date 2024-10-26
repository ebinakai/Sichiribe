import pytest
from unittest.mock import patch


@pytest.fixture()
def prevent_window_show():
    with patch('PySide6.QtWidgets.QWidget.show'):
        yield
