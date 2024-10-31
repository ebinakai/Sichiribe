"""
リアルタイム解析を行うワーカークラス

1. 以下の処理を行う
  - モデルのロード
  - フレームのキャプチャ
  - フレームの編集
  - 推論処理
  - フレームの保存
  - UI への通知
2. キャプチャしたフレームを保存する場合は、フレーム保存用ディレクトリを作成する
3. モデルのロードに失敗した場合、モデルが見つからないことを UI に通知
4. フレームのキャプチャが失敗した場合、エラーを UI に通知
"""

from PySide6.QtCore import Signal, QThread
from gui.utils.data_store import DataStore
from cores.capture import FrameCapture
from cores.cnn import cnn_init
from cores.frame_editor import FrameEditor
import logging
from typing import Optional
import time
from datetime import timedelta
import cv2
import numpy as np
from pathlib import Path


class DetectWorker(QThread):
    ready = Signal()
    error = Signal(str)
    progress = Signal(int, float, str)
    send_image = Signal(np.ndarray)
    remaining_time = Signal(float)
    SLEEP_INTERVAL = 0.1

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.data_store = DataStore.get_instance()
        self.is_cancelled = False
        self.binarize_th: Optional[int] = None
        self._is_capturing = True

        if self.data_store.get("save_frame"):
            (Path(self.data_store.get("out_dir")) / "frames").mkdir(
                parents=True, exist_ok=True
            )

    def run(self) -> None:

        self.logger.info("DetectWorker started.")

        try:
            self.dt = cnn_init(num_digits=self.data_store.get("num_digits"))
        except Exception as e:
            self.logger.error(f"Failed to load the model: {e}")
            self.error.emit("CNNモデルの読み込みに失敗しました")
            return None

        try:
            self.fc = FrameCapture(device_num=self.data_store.get("device_num"))
        except Exception as e:
            self.logger.error(f"Failed to open camera: {e}")
            self.error.emit("カメラへのアクセスに失敗しました")
            return None

        self.fc.set_cap_size(*self.data_store.get("cap_size"))
        self.fe = FrameEditor(num_digits=self.data_store.get("num_digits"))

        start_time = time.time()
        end_time = time.time() + self.data_store.get("total_sampling_sec")
        frame_count = 0
        timestamps = []
        is_first_loop = True

        while time.time() < end_time and not self.is_cancelled:
            temp_time = time.time()

            # タイムスタンプを "HH:MM:SS" 形式で生成
            elapsed_time = time.time() - start_time
            timestamp = timedelta(seconds=int(elapsed_time))
            timestamp_str = str(timestamp)
            timestamps.append(timestamp_str)

            frame_batch = []
            self._is_capturing = True
            for i in range(self.data_store.get("num_digits")):
                frame = self.fc.capture()

                if frame is None:
                    self.error.emit("フレームの取得に失敗しました")
                    self.is_cancelled = True
                    break

                cropped_frame = self.fe.crop(frame, self.data_store.get("click_points"))
                if cropped_frame is None:
                    self.logger.error("Failed to crop the frame.")
                    continue
                frame_batch.append(cropped_frame)

                if self.data_store.get("save_frame"):
                    frame_filename = (
                        Path(self.data_store.get("out_dir"))
                        / "frames"
                        / f"frame_{frame_count:06d}.jpg"
                    )
                    cv2.imwrite(str(frame_filename), cropped_frame)
                    self.logger.debug(
                        f"Frame {frame_count} has been saved as: {frame_filename}"
                    )
                    frame_count += 1
            self._is_capturing = False

            # GUI への送信用の画像二値化であり、predict 内で再度処理する
            image_bin = self.dt.preprocess_binarization(
                frame_batch[0], self.binarize_th
            )
            self.send_image.emit(image_bin)

            value, failed_rate = self.dt.predict(frame_batch, self.binarize_th)
            self.logger.info(f"Detected: {value}, Failed rate: {failed_rate}")

            if is_first_loop:
                self.ready.emit()
                is_first_loop = False

            self.progress.emit(value, failed_rate, timestamp_str)

            elapsed_time = time.time() - temp_time
            time_to_wait = max(0, self.data_store.get("sampling_sec") - elapsed_time)
            time_end_wait = time.time() + time_to_wait
            if time_to_wait > 0:
                self.logger.debug(f"Waiting for {time_to_wait:.2f}s")

                while time.time() < time_end_wait and not self.is_cancelled:
                    remaining_time = end_time - time.time()
                    self.remaining_time.emit(max(remaining_time, 0))
                    time.sleep(self.SLEEP_INTERVAL)

        self.fc.release()

        return None

    def cancel(self) -> None:
        self.logger.info("DetectWorker terminating...")
        self.is_cancelled = True

    def update_binarize_th(self, value: Optional[int]) -> None:
        self.binarize_th = value
        self.logger.info(f"Update binarize_th: {self.binarize_th}")

        if not self._is_capturing:
            frame = self.fc.capture()
            if frame is None:
                self.logger.debug("Frame missing.")
                return None

            cropped_frame = self.fe.crop(frame, self.data_store.get("click_points"))
            if cropped_frame is None:
                self.logger.debug("Failed to crop the frame.")
                return None

            image_bin = self.dt.preprocess_binarization(cropped_frame, self.binarize_th)
            self.send_image.emit(image_bin)
