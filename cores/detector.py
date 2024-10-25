import logging
import cv2
import numpy as np


class Detector():
    def __init__(self) -> None:
        self.logger = logging.getLogger("__main__").getChild(__name__)

    def load_image(self, image) -> np.ndarray:
        if isinstance(image, np.ndarray):
            if len(image.shape) == 3:
                image_gs = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                image_gs = image
        else:
            # 画像ファイルをグレースケールで読み込む
            image_gs = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

        return image_gs

    def preprocess_binarization(
            self,
            image,
            binarize_th=None,
            output_grayscale=False) -> np.ndarray:

        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            image = image

        if binarize_th is None:
            # 大津の2値化
            _, image_bin = cv2.threshold(
                image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            _, image_bin = cv2.threshold(
                image, binarize_th, 255, cv2.THRESH_BINARY)

        # 背景が黒（0）のピクセルが全体の50%未満の場合は反転（使用する学習モデルの特性上の理由）
        black_pixels = np.sum(image_bin == 0)
        white_pixels = np.sum(image_bin == 255)
        if black_pixels > white_pixels:
            image_bin = cv2.bitwise_not(image_bin)

        # ノイズ除去
        image_bin = cv2.medianBlur(image_bin, ksize=9)

        if output_grayscale:
            return image_bin

        image_cl = cv2.cvtColor(image_bin, cv2.COLOR_GRAY2BGR)

        return image_cl

    def get_failed_rate(self, data: list, correct_value: float) -> float:
        total = len(data)
        if total == 0:
            return 1.0

        correct = data.count(correct_value)
        failed = total - correct
        return failed / total if total > 0 else 0
