import pytest
import cv2
from cores.cnn import CNNCore, select_cnn_model


@pytest.fixture
def detector():
    Detector = select_cnn_model()
    detector = Detector(num_digits=4)
    detector.load()
    return detector


@pytest.fixture
def sample_image_path():
    return 'tests/data/sample.jpg'


@pytest.fixture
def sample_image(sample_image_path):
    image = cv2.imread(sample_image_path)
    assert image is not None, f"Image not found at {sample_image_path}"
    return image


class TestCNN:
    def test_detector_initialization(self, detector):
        assert isinstance(detector, CNNCore)

    def test_detector_loading(self, detector):
        assert detector.load()

    @pytest.mark.parametrize("test_case", [
        ("single_path", lambda path, _: path),      # Single path
        ("list_of_paths", lambda path, _: [path]),  # List of paths
        ("single_image", lambda _, img: img),       # Single image
        ("list_of_images", lambda _, img: [img]),   # List of images
    ])
    def test_prediction(self, detector, sample_image_path,
                        sample_image, test_case):
        case_name, input_data_factory = test_case
        input_data = input_data_factory(sample_image_path, sample_image)

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
