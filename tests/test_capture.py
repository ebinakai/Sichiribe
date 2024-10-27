import pytest
from unittest.mock import Mock, patch
import numpy as np
import cv2
from cores.capture import FrameCapture


@pytest.fixture
def sample_frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
@patch('cv2.VideoCapture')
@patch('time.sleep')
def frame_capture(mock_sleep, mock_video_capture, sample_frame):
    mock_cap_instance = Mock()
    mock_cap_instance.read.return_value = (True, sample_frame)
    mock_video_capture.return_value = mock_cap_instance
    capture = FrameCapture(device_num=0)
    return capture


class TestFrameCapture:
    @patch('cv2.VideoCapture')
    def test_init(self, mock_video_capture, frame_capture):
        assert mock_video_capture.called_once_with(1)

    @patch('cv2.VideoCapture')
    def test_capture_success(self, mock_video_capture, frame_capture):
        result = frame_capture.capture()

        assert mock_video_capture.read.called_once()
        assert isinstance(result, np.ndarray), "Output is not a numpy array"
        assert result.shape == (480, 640, 3), "Output shape is not correct"

    def test_capture_failure(self, frame_capture):
        frame_capture.cap.read.return_value = (False, None)
        result = frame_capture.capture()

        assert result is None, "Output is not None"
        assert frame_capture.cap.read.called_once()

    @patch('cv2.destroyAllWindows')
    @patch('cv2.VideoCapture')
    def test_release(self, mock_video_capture, mock_destroy, frame_capture):
        frame_capture.release()

        assert mock_video_capture.release.called_once()
        assert mock_destroy.called_once()

    def test_set_cap_size(self, frame_capture):
        # return value for [logger, logger, output, output]
        frame_capture.cap.get.side_effect = [0, 0, 1280.0, 720.0]
        width, height = frame_capture.set_cap_size(1280, 720)

        assert width == 1280.0, "Output width is not correct"
        assert height == 720.0, "Height is not correct"
        assert frame_capture.cap.set.call_count == 2
        frame_capture.cap.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        frame_capture.cap.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    @pytest.mark.timeout(0.5)
    @patch('cv2.imshow')
    @patch('cv2.waitKey')
    @patch('cv2.destroyAllWindows')
    def test_show_camera_feed_exit(
            self, mock_destroy, mock_wait_key, mock_imshow, frame_capture):
        mock_wait_key.return_value = ord('y')
        frame_capture.show_camera_feed()
        _, expected_output = frame_capture.cap.read.return_value

        assert mock_imshow.called_with("Press 'y' to finish.", expected_output)
        assert mock_destroy.called_once()
