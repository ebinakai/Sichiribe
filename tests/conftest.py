import pytest
from unittest.mock import MagicMock, Mock
from unittest.mock import patch
import numpy as np
import os


@pytest.fixture(scope="session", autouse=True)
def qt_test_environment():
    # CI環境での実行時はオフスクリーンバックエンドを使用
    if os.environ.get("CI"):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-runner"
    yield


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


@pytest.fixture
def mock_screen_manager():
    manager = Mock()
    manager.save_screen_size.return_value = (MagicMock(), None)
    return manager
