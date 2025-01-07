"""カメラリソースの管理機能"""

import cv2
import numpy as np
import time
import logging
from typing import Optional


class FrameCapture:
    """フレームのキャプチャに関するクラス"""

    def __init__(
        self,
        device_num: int = 0,
    ) -> None:

        self.logger = logging.getLogger("__main__").getChild(__name__)

        self.cap = cv2.VideoCapture(device_num)
        if not self.cap.isOpened():
            raise Exception("Failed to open camera.")

        # カメラに接続するまで待機
        time.sleep(0.1)

    def show_camera_feed(self) -> None:
        """カメラフィードを表示する

        OpenCVのウィンドウがアクティブな間、フレームを取得し続ける

        yキーを押すとウィンドウが閉じる
        """
        while cv2.waitKey(10) & 0xFF != ord("y"):
            frame = self.capture()
            if frame is None:
                break

            window_title = "Press 'y' to finish."
            cv2.imshow(window_title, frame)

        self.logger.debug("Camera feed window closed.")
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def capture(self) -> Optional[np.ndarray]:
        """フレームを取得する"""
        ret, frame = self.cap.read()
        if ret:
            return frame
        else:
            self.logger.error("Failed to capture frame")
            return None

    def release(self) -> None:
        """カメラリソースを解放する"""
        self.cap.release()
        cv2.destroyAllWindows()

    def set_cap_size(self, width: float, height: float) -> tuple[float, float]:
        """カメラの解像度を設定する

        Args:
            width (float): 幅
            height (float): 高さ

        Returns:
            tuple[float, float]: 設定された幅と高さ
        """
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.logger.debug(
            "set_cap_size called: {0} x {1}".format(
                self.cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
            )
        )
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.logger.debug("set to {0} x {1}".format(width, height))
        return width, height
