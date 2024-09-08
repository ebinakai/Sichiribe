from PySide6.QtCore import Signal, QThread
from cores.cnn_lite import CNNLite as Detector
import logging

class DetectWorker(QThread):
    progress = Signal(int, float, str)
    end = Signal()
    cancelled = Signal()

    def __init__(self, params):
        super().__init__()
        self.params = params
        self.dt = Detector(params['num_digits'])
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self._is_cancelled = False  # 停止フラグ

    def run(self):
        self.logger.info("DetectWorker started.")
        self.dt.load()
        
        # テキスト検出
        for frame, timestamp in zip(self.params['frames'], self.params['timestamps']):
            if self._is_cancelled: 
                self.cancelled.emit()
                self.params = None
                return
            result, failed_rate = self.dt.detect(frame, binarize_th=self.params['threshold'])
            
            # すべての桁(三桁以上)が8の場合はディスプレイが消灯していると判断し、検出失敗とする
            if str(result) == '8' * self.params['num_digits'] and self.params['num_digits'] > 2:
                failed_rate = 1.0
            
            self.logger.info(f"Detected Result: {result}")
            self.logger.info(f"Failed Rate: {failed_rate}")
            self.progress.emit(result, failed_rate, timestamp)
            
        self.end.emit()
        return None
        
    def cancel(self):
        self.logger.info("DetectWorker terminating...") 
        self._is_cancelled = True  # 停止フラグを設定
