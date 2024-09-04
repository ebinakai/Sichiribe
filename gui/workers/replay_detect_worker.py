from PyQt6.QtCore import pyqtSignal, QThread
from cores.cnn import CNN as Detector
import logging

class DetectWorker(QThread):
    progress = pyqtSignal(int, float)
    finished = pyqtSignal(list)
    termination = pyqtSignal(list)

    def __init__(self, params):
        super().__init__()
        self.params = params
        self.dt = Detector(params['num_digits'])
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self._is_terminating = False  # 停止フラグ

    def run(self):
        self.logger.info("DetectWorker started.")
        self.dt.load()
        
        # テキスト検出
        results = []
        for frame in self.params['frames']:
            if self._is_terminating: 
                self.termination.emit(results)
                self.params = None
                return
            result, failed_rate = self.dt.detect(frame)
            
            # すべての桁(三桁以上)が8の場合はディスプレイが消灯していると判断し、検出失敗とする
            if str(result) == '8' * self.params['num_digits'] and self.params['num_digits'] > 2:
                failed_rate = 1.0
            
            results.append(result)
            self.logger.info(f"Detected Result: {result}")
            self.logger.info(f"Failed Rate: {failed_rate}")
            self.progress.emit(result, failed_rate)
            
        self.finished.emit(results)
        self.params = None
        
    def stop(self):
        self.logger.info("DetectWorker stopping...") 
        self._is_terminating = True  # 停止フラグを設定
