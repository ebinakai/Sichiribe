import pytest
from unittest.mock import MagicMock, Mock
from unittest.mock import patch
import numpy as np


@pytest.fixture()
def prevent_window_show():
    def mock_show(self):
        self._visible = True
    
    def mock_isVisible(self):
        return getattr(self, '_visible', False)
    
    def mock_close(self):
        self._visible = False
    
    with patch('PySide6.QtWidgets.QWidget.show', mock_show), \
         patch('PySide6.QtWidgets.QWidget.isVisible', mock_isVisible), \
         patch('PySide6.QtWidgets.QWidget.close', mock_close):
        yield



@pytest.fixture
def sample_frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def sample_frame_gs():
    return np.zeros((480, 640, 1), dtype=np.uint8)


@pytest.fixture
def mock_screen_manager():
    manager = Mock()
    manager.save_screen_size.return_value = (MagicMock(), None)
    return manager
