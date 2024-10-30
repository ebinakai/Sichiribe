from unittest.mock import patch
from cores.cnn import CNNCore
import numpy as np


class TestCNN:
    def setup_method(self):
        self.cnn = CNNCore(3)
        self.predictions = np.array([[0, 1, 2], [0, 1, 1], [1, 2, 2], [1, 1, 2]])
        self.image = np.zeros((100, 300), dtype=np.uint8)

    def test_init(self):
        assert self.cnn.num_digits == 3
        assert self.cnn.image_width == 100
        assert self.cnn.image_height == 100
        assert self.cnn.color_setting == 1

    def test_find_mode_per_column_np(self):
        expected_result = np.array([0, 1, 2])
        expected_errors_per_digit = np.array([0.5, 0.25, 0.25])

        result, errors_per_digit = self.cnn.find_mode_per_column_np(self.predictions)

        np.testing.assert_array_equal(errors_per_digit, expected_errors_per_digit)
        np.testing.assert_array_equal(result, expected_result)

    def test_preprocess_image(self):
        processed_images = self.cnn.preprocess_image(self.image)

        expected_shape = (3, 100, 100, 1)
        assert (
            processed_images.shape == expected_shape
        ), f"Expected shape {expected_shape}, but got {processed_images.shape}"

        # 値の範囲をチェック (0から1の範囲)
        assert np.all(processed_images >= 0) and np.all(
            processed_images <= 1
        ), "Image values should be in range [0, 1]."

    def test_predict(self):
        with patch(
            "cores.cnn.CNNCore.inference_7seg_classifier", return_value=[1, 1, 1]
        ):
            result, failed_rate = self.cnn.predict(self.image)

            assert result == 111
            assert failed_rate == 0
