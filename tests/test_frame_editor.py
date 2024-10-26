import pytest
import numpy as np
from unittest.mock import Mock, patch
import cv2
from cores.frame_editor import FrameEditor


@pytest.fixture
def frame_editor():
    return FrameEditor(
        sampling_sec=3,
        num_frames_per_sample=10,
        num_digits=4,
        crop_width=100,
        crop_height=100
    )


@pytest.fixture
def sample_frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def sample_click_points():
    return np.array([[129, 596], [179, 595], [178, 616], [128, 617]])


class TestFrameEditor:
    def test_initial_ui_state(self, frame_editor):
        assert frame_editor.sampling_sec == 3
        assert frame_editor.num_frames_per_sample == 10
        assert frame_editor.num_digits == 4
        assert frame_editor.crop_width == 100
        assert frame_editor.crop_height == 100
        assert len(frame_editor.click_points) == 0

    @patch('cv2.VideoCapture')
    def test_frame_devide_normal(
            self, mock_video_capture, frame_editor, sample_frame):
        # VideoCaptureのモックを設定
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30.0
        mock_cap.read.side_effect = [
            (True, sample_frame)] * 100 + [(False, None)]
        mock_video_capture.return_value = mock_cap

        frames = frame_editor.frame_devide(
            "dummy.mp4",
            save_frame=False,
            is_crop=False
        )

        assert isinstance(frames, list)
        assert isinstance(frames[0][0], np.ndarray)
        assert mock_cap.release.called_once()

    @patch('cv2.VideoCapture')
    def test_frame_devide_single_frame(
            self, mock_video_capture, frame_editor, sample_frame):
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30.0
        mock_cap.read.return_value = (True, sample_frame)
        mock_video_capture.return_value = mock_cap

        frame = frame_editor.frame_devide(
            "dummy.mp4",
            save_frame=False,
            is_crop=False,
            extract_single_frame=True
        )

        assert isinstance(frame, np.ndarray)
        assert mock_cap.release.called_once()

    def test_generate_timestamp(self, frame_editor):
        n = 5
        timestamps = frame_editor.generate_timestamp(n)

        assert isinstance(timestamps, list)
        assert len(timestamps) == n
        assert all(isinstance(ts, str) for ts in timestamps)
        assert timestamps[0] == "0:00:00"
        assert timestamps[1] == "0:00:03"

    def test_order_points(self, frame_editor, sample_click_points):
        expected_points = sample_click_points.copy()
        for i in range(4):
            np.random.shuffle(sample_click_points)
            ordered_points = frame_editor.order_points(sample_click_points)

            assert np.array_equal(ordered_points, expected_points)
        assert isinstance(ordered_points, np.ndarray)

    def test_crop(self, frame_editor, sample_frame, sample_click_points):
        cropped = frame_editor.crop(sample_frame, sample_click_points)

        assert isinstance(cropped, np.ndarray)
        assert cropped.shape[0] == frame_editor.crop_height
        assert cropped.shape[1] == frame_editor.crop_width * \
            frame_editor.num_digits

    def test_crop_invalid_points(self, frame_editor, sample_frame):
        invalid_points = [[0, 0], [0, 1]]
        result = frame_editor.crop(sample_frame, invalid_points)
        assert result is None

    def test_draw_debug_info(
            self, frame_editor, sample_frame, sample_click_points):
        extract_frame = np.zeros((100, 400, 3), dtype=np.uint8)

        frame_edited, extract_edited = frame_editor.draw_debug_info(
            sample_frame,
            extract_frame,
            sample_click_points
        )

        assert isinstance(frame_edited, np.ndarray)
        assert isinstance(extract_edited, np.ndarray)
        assert frame_edited.shape == sample_frame.shape
        assert extract_edited.shape == extract_frame.shape

    @pytest.mark.timeout(0.5)
    @patch('cv2.namedWindow')
    @patch('cv2.imshow')
    @patch('cv2.waitKey')
    @patch('cv2.destroyAllWindows')
    def test_region_select(self, mock_destroy, mock_wait_key,
                           mock_imshow, mock_name_window, frame_editor, sample_frame, sample_click_points):
        mock_wait_key.return_value = ord('y')
        frame_editor.click_points = sample_click_points.tolist()
        result = frame_editor.region_select(sample_frame)

        assert isinstance(result, list)
        assert len(result) == 4
        assert mock_destroy.called_once()

    def test_mouse_callback(self, frame_editor):
        frame_editor.mouse_callback(
            cv2.EVENT_LBUTTONDOWN, 100, 100, None, None)
        assert len(frame_editor.click_points) == 1

        frame_editor.mouse_callback(
            cv2.EVENT_LBUTTONDOWN, 200, 100, None, None)
        frame_editor.mouse_callback(
            cv2.EVENT_LBUTTONDOWN, 200, 200, None, None)
        frame_editor.mouse_callback(
            cv2.EVENT_LBUTTONDOWN, 100, 200, None, None)
        assert len(frame_editor.click_points) == 4

        frame_editor.mouse_callback(
            cv2.EVENT_LBUTTONDOWN, 101, 201, None, None)
        assert len(frame_editor.click_points) == 4
