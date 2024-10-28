import pytest
from unittest.mock import patch
import numpy as np


@pytest.fixture()
def prevent_window_show():
    with patch("PySide6.QtWidgets.QWidget.show"):
        yield


@pytest.fixture
def sample_frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def sample_frame_gs():
    return np.zeros((480, 640, 1), dtype=np.uint8)
