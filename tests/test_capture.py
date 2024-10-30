import pytest
from unittest.mock import Mock, patch
from itertools import cycle
import numpy as np
import cv2
from cores.capture import FrameCapture


@pytest.fixture
def sample_frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
@patch("cv2.VideoCapture")
@patch("time.sleep")
def init_frame_capture(mock_sleep, mock_video_capture, sample_frame):
    mock_cap_instance = Mock()
    mock_cap_instance.read.return_value = (True, sample_frame)
    mock_video_capture.return_value = mock_cap_instance
    frame_capture = FrameCapture(device_num=0)
    return frame_capture, mock_cap_instance


class TestFrameCapture:
    def test_init(self, init_frame_capture):
        capture, mock_video_capture = init_frame_capture
        assert capture.cap == mock_video_capture

    def test_capture_success(self, init_frame_capture):
        frame_capture, mock_video_capture = init_frame_capture
        result = frame_capture.capture()

        mock_video_capture.read.assert_called_once()
        assert isinstance(result, np.ndarray)
        assert result.shape == (480, 640, 3)

    def test_capture_failure(self, init_frame_capture):
        frame_capture, mock_video_capture = init_frame_capture
        frame_capture.cap.read.return_value = (False, None)
        result = frame_capture.capture()

        assert result is None
        frame_capture.cap.read.assert_called_once()

    @patch("cv2.destroyAllWindows")
    def test_release(self, mock_destroy, init_frame_capture):
        frame_capture, mock_video_capture = init_frame_capture
        frame_capture.release()

        mock_video_capture.release.assert_called_once()
        mock_destroy.assert_called_once()

    def test_set_cap_size(self, init_frame_capture):
        frame_capture, mock_video_capture = init_frame_capture
        # return value for [logger, logger, output, output]
        frame_capture.cap.get.side_effect = [0, 0, 1280.0, 720.0]
        width, height = frame_capture.set_cap_size(1280, 720)

        assert width == 1280.0
        assert height == 720.0
        assert frame_capture.cap.set.call_count == 2
        frame_capture.cap.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        frame_capture.cap.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    @pytest.mark.timeout(0.5)
    @patch("cv2.imshow")
    @patch("cv2.waitKey")
    @patch("cv2.destroyAllWindows")
    def test_show_camera_feed_exit(
        self, mock_destroy, mock_wait_key, mock_imshow, init_frame_capture
    ):
        frame_capture, mock_video_capture = init_frame_capture

        mock_wait_key.side_effect = cycle([ord("n") & 0xFF, ord("y") & 0xFF])

        frame_capture.show_camera_feed()

        mock_imshow.assert_called()
        mock_destroy.assert_called_once()
        assert mock_wait_key.call_count >= 2
