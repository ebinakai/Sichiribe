import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from PySide6.QtCore import Qt, QPoint, QPointF, QSize
from PySide6.QtGui import QMouseEvent
from gui.views.region_select_view import RegionSelectWindow


@pytest.fixture(autouse=True)
def prevent_window_show():
    with patch('PySide6.QtWidgets.QWidget.show'):
        yield


@pytest.fixture
def mock_screen_manager():
    manager = MagicMock()
    manager.save_screen_size.return_value = (MagicMock(), None)
    return manager


@pytest.fixture
def mock_frame_editor():
    with patch('cores.frame_editor.FrameEditor') as mock:
        editor = mock.return_value
        editor.order_points.return_value = [
            [0, 0], [100, 0], [100, 100], [0, 100]]
        editor.crop.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        editor.draw_debug_info.return_value = (
            np.zeros((200, 200, 3), dtype=np.uint8),
            np.zeros((100, 100, 3), dtype=np.uint8)
        )
        yield editor


@pytest.fixture
def window(qtbot, mock_screen_manager, mock_frame_editor):
    with patch('PySide6.QtWidgets.QApplication.primaryScreen') as mock_screen:
        mock_geometry = MagicMock()
        mock_geometry.width.return_value = 1920
        mock_geometry.height.return_value = 1080
        mock_screen.return_value.availableGeometry.return_value = mock_geometry

        window = RegionSelectWindow(mock_screen_manager)
        window.fe = mock_frame_editor
        qtbot.addWidget(window)
        return window


def create_mouse_event(pos, button=Qt.MouseButton.LeftButton):
    return QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(pos),
        QPointF(pos),
        button,
        button,
        Qt.KeyboardModifier.NoModifier
    )


def test_init(window):
    assert len(window.click_points) == 0
    assert window.target_width == int(1920 * 0.8)
    assert window.target_height == int((1080 - 100) * 0.8)


def test_startup(window):
    params = {
        'num_digits': 2,
        'first_frame': np.zeros((480, 640, 3), dtype=np.uint8)
    }
    window.startup(params, 'replay_exe')

    assert window.params == params
    assert window.prev_screen == 'replay_exe'
    assert window.fe is not None


def test_label_clicked_add_points(window, qtbot):
    window.image_size = QSize(200, 200)
    window.image = np.zeros((200, 200, 3), dtype=np.uint8)
    window.image_original = np.zeros((200, 200, 3), dtype=np.uint8)
    window.resize_scale = 1.0

    points = [(50, 50), (150, 50), (150, 150), (50, 150)]
    for x, y in points:
        event = create_mouse_event(QPoint(x, y))
        window.label_clicked(event)

    assert len(window.click_points) == 4

    window.fe.order_points.assert_called()


def test_finish_select_with_incomplete_points(window, qtbot):
    window.click_points = [(50, 50)]
    window.finish_select()

    assert window.confirm_txt.text() == '7セグメント領域を囲ってください'


def test_finish_select_success(window, qtbot):
    window.params = {'num_digits': 4}
    window.prev_screen = 'replay_exe'
    window.resize_scale = 1.0
    window.click_points = [(0, 0), (100, 0), (100, 100), (0, 100)]
    window.finish_select()

    assert 'click_points' in window.params
    assert len(window.params['click_points']) == 4


def test_cancel_select(window, qtbot):
    window.prev_screen = 'replay_exe'
    window.params = {'some': 'data'}

    window.cancel_select()
    assert window.click_points == []
    assert window.image is None
    assert window.confirm_txt.text() == ''


def test_clear_env(window):
    window.image = np.zeros((100, 100, 3))
    window.image_original = np.zeros((100, 100, 3))
    window.click_points = [(0, 0), (1, 1)]
    window.confirm_txt.setText('テストメッセージ')

    window.clear_env()
    assert window.image is None
    assert window.image_original is None
    assert window.click_points == []
    assert window.confirm_txt.text() == ''
