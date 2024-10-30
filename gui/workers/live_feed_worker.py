"""
カメラの画角をキャプチャするためのワーカークラス

1. キャプチャデバイスを設定し、キャプチャサイズを取得する
2. キャプチャデバイスからフレームを取得し、進捗を通知する
3. キャンセルフラグが立った場合は、キャンセルを通知し、キャプチャを終了する
4. 終了フラグが立った場合は、終了を通知し、キャプチャを終了する
"""

from PySide6.QtCore import Signal, QThread
from gui.utils.data_store import DataStore
from cores.capture import FrameCapture
import logging
import numpy as np
import time


class LiveFeedWorker(QThread):
    cap_size = Signal(tuple)
    progress = Signal(np.ndarray)
    end = Signal(np.ndarray)
    cancelled = Signal()
    error = Signal()
    SLEEP_TIME = 0.01

    def __init__(self, width: float, height: float) -> None:
        super().__init__()
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.data_store = DataStore.get_instance()
        self.width = width
        self.height = height
        self._is_cancelled = False
        self._is_finished = False

    def run(self) -> None:
        try:
            fc = FrameCapture(self.data_store.get("device_num"))
        except Exception as e:
            self.logger.error(f"Failed to open camera: {e}")
            self.error.emit()
            return None

        self.logger.info(
            "Capture device(%s) loaded." % self.data_store.get("device_num")
        )
        cap_width, cap_height = fc.set_cap_size(self.width, self.height)
        self.logger.debug("Capture size set to %d x %d" % (cap_width, cap_height))
        self.cap_size.emit((cap_width, cap_height))

        while True:
            if self._is_cancelled:
                self.cancelled.emit()
                break

            frame = fc.capture()
            if frame is None:
                self.error.emit()
                break

            if self._is_finished:
                self.end.emit(frame)
                break

            self.progress.emit(frame)
            time.sleep(self.SLEEP_TIME)

        fc.release()
        return None

    def stop(self) -> None:
        self.logger.info("Capture Feed stopping...")
        self._is_finished = True

    def cancel(self) -> None:
        self.logger.info("Capture Feed canceling...")
        self._is_cancelled = True
