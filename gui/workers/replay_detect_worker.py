'''
動画ファイル解析を行うワーカークラス

1. 以下の処理を行う
    - モデルのロード
    - 推論処理
    - フレームの保存
    - UIへの通知
2. キャプチャしたフレームを保存する場合は、フレーム保存用ディレクトリを作成する
3. モデルのロードに失敗した場合、モデルが見つからないことを UI に通知
'''

from PySide6.QtCore import Signal, QThread
import logging

# モデルを読み込む
from cores.cnn_core import select_cnn_model
Detector = select_cnn_model()

class DetectWorker(QThread):
    progress = Signal(int, float, str)
    cancelled = Signal()
    model_not_found = Signal()

    def __init__(self, params):
        super().__init__()
        self.params = params
        self.dt = Detector(params['num_digits'])
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self._is_cancelled = False

    def run(self):
        self.logger.info("DetectWorker started.")
        
        if not self.dt.load():
          self.logger.error("Failed to load the model.")
          self.model_not_found.emit()
          return None
        
        for frame, timestamp in zip(self.params['frames'], self.params['timestamps']):
            if self._is_cancelled: 
                self.cancelled.emit()
                self.params = None
                return None
            
            result, failed_rate = self.dt.detect(frame, binarize_th=self.params['threshold'])
            self.logger.info(f"Detected Result: {result}")
            self.logger.info(f"Failed Rate: {failed_rate}")
            self.progress.emit(result, failed_rate, timestamp)
            
        return None
        
    def cancel(self):
        self.logger.info("DetectWorker terminating...") 
        self._is_cancelled = True
