import pytest
from unittest.mock import Mock
from cores.cnn import CNNCore, select_cnn_model


@pytest.fixture
def detector():
    Detector = select_cnn_model()
    detector = Detector(num_digits=4)
    return detector


class TestCNN:
    def test_detector_initialization(self, detector):
        assert isinstance(detector, CNNCore)

    @pytest.mark.parametrize("test_case", [
        ("single_path", lambda path, _: path),      # Single path
        ("list_of_paths", lambda path, _: [path]),  # List of paths
        ("single_image", lambda _, img: img),       # Single image
        ("list_of_images", lambda _, img: [img]),   # List of images
    ])
    def test_prediction(self, detector, sample_frame_gs, test_case):
        detector.load_image = Mock()
        detector.load_image.return_value = sample_frame_gs
        case_name, input_data_factory = test_case
        input_data = input_data_factory('dummy.jpg', sample_frame_gs)

        result, failed_rate = detector.predict(input_data)

        # Validate prediction results
        assert result is not None, f"{case_name}: Prediction result should not be None"
        assert isinstance(result, int), f"{case_name}: Result should be an int"
        assert isinstance(
            failed_rate, float), f"{case_name}: Failed rate should be a float"
        assert 0 <= failed_rate <= 1, f"{case_name}: Failed rate should be between 0 and 1"

    def test_prediction_with_invalid_path(self, detector):
        with pytest.raises(Exception):
            detector.predict("nonexistent_image.jpg")

    def test_prediction_with_invalid_image(self, detector):
        with pytest.raises(Exception):
            detector.predict(None)
