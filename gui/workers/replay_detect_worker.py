"""
動画ファイル解析を行うワーカークラス

1. 以下の処理を行う
    - モデルのロード
    - 推論処理
    - フレームの保存
    - UIへの通知
2. キャプチャしたフレームを保存する場合は、フレーム保存用ディレクトリを作成する
3. モデルのロードに失敗した場合、モデルが見つからないことを UI に通知
"""

from PySide6.QtCore import Signal, QThread
from gui.utils.data_store import DataStore
from cores.cnn import cnn_init
import logging
import numpy as np


class DetectWorker(QThread):
    """動画ファイル解析を行うワーカークラス

    Attributes:
        progress: 推論結果を通知するシグナル
        send_image: 画像を送信するシグナル
        cancelled: キャンセルを通知するシグナル
        model_not_found: モデルが見つからないことを通知するシグナル
    """

    progress = Signal(int, float, str)
    send_image = Signal(np.ndarray)
    cancelled = Signal()
    model_not_found = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.data_store = DataStore.get_instance()
        self._is_cancelled = False

    def run(self) -> None:
        """スレッド処理を実行する

        1. モデルのロード
        2. 推論処理
        3. UI への通知
        4. 1-3 を動画フレーム数分繰り返す
        """
        self.logger.info("DetectWorker started.")

        try:
            self.dt = cnn_init(num_digits=self.data_store.get("num_digits"))
        except Exception as e:
            self.logger.error(f"Failed to load the model: {e}")
            self.model_not_found.emit()
            return None

        for frames, timestamp in zip(
            self.data_store.get("frames"), self.data_store.get("timestamps")
        ):
            if self._is_cancelled:
                self.cancelled.emit()
                return None

            # GUI への送信用の画像二値化であり、predict 内で再度処理する
            image_bin = self.dt.preprocess_binarization(
                frames[0], binarize_th=self.data_store.get("threshold")
            )
            self.send_image.emit(image_bin)

            result, failed_rate = self.dt.predict(
                frames, binarize_th=self.data_store.get("threshold")
            )
            self.logger.info(f"Detected Result: {result}")
            self.logger.info(f"Failed Rate: {failed_rate}")
            self.progress.emit(result, failed_rate, timestamp)

        return None

    def cancel(self) -> None:
        """スレッド処理をキャンセルする

        このメソッドが呼ばれると、キャンセルフラグが立つ
        """
        self.logger.info("DetectWorker terminating...")
        self._is_cancelled = True
