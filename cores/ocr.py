from cores.detector import Detector

import easyocr
import logging
import statistics
from typing import List, Union
import numpy as np


class OCR(Detector):
    def __init__(self) -> None:
        self.logger = logging.getLogger("__main__").getChild(__name__)

    def load(self) -> None:
        self.reader = easyocr.Reader(['en'])
        self.logger.info("OCR Model loaded.")

    def predict(self, images: Union[str, np.ndarray, List[Union[str,
                                                                np.ndarray]]], result_idx: int = 0) -> tuple[float, float]:
        # [引数] result_idx: OCRの結果のうち、何番目の結果を取得するか

        if self.reader is None:
            self.logger.error("OCR Model unloaded.")

        detect_nums = []

        # リスト化する
        if not isinstance(images, list):
            images = [images]

        for i, image in enumerate(images):

            # 画像を読み込む
            image_gs = self.load_image(image)

            # 画像が正常に読み込まれたか確認
            if image_gs is None:
                self.logger.error("Error: Could not read image file.")
                continue

            # 二値化処理
            image_bin = self.preprocess_binarization(image_gs)

            # ocrでテキストを検出
            result = self.reader.readtext(image_bin)

            # テキストが検出されなかった場合
            if len(result) == 0:
                detect_nums.append(None)
                self.logger.debug("No text detected.")
                continue

            # 検出されたテキストを数値に変換
            detect_txt = result[result_idx][1]
            try:
                detect_nums.append(float(detect_txt))  # なんかここでリストに入っていない

            except BaseException:
                detect_nums.append(None)
                self.logger.debug("Could not convert detected text to number.")
                continue

        self.logger.debug("Detected numbers: %s", detect_nums)

        # 最頻値を取得
        detect_num = statistics.mode(detect_nums) if len(
            detect_nums) > 0 else None
        self.logger.debug("Detected number: %s", detect_num)

        # 誤検知率を取得
        failed_rate = self.get_failed_rate(detect_nums, detect_num)

        return detect_num, failed_rate

    def get_failed_rate(self, data: list, correct_value: float) -> float:
        total = len(data)
        if total == 0:
            return 1.0

        correct = data.count(correct_value)
        failed = total - correct
        return failed / total if total > 0 else 0
