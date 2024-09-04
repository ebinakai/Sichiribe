from PyQt6.QtCore import pyqtSignal, QThread
from cores.cnn import CNN as Detector
import logging

class DetectWorker(QThread):
    proguress = pyqtSignal(int, float)
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
                return
            result, failed_rate = self.dt.detect(frame)
            
            # すべての桁が8の場合は検出失敗とする
            if self.is_all_eights(result):
                failed_rate = 1.0
            
            results.append(result)
            self.logger.info(f"Detected Result: {result}")
            self.logger.info(f"Failed Rate: {failed_rate}")
            self.proguress.emit(result, failed_rate)
            
        self.finished.emit(results)
        
    def stop(self):
        self.logger.info("DetectWorker stopping...") 
        self._is_terminating = True  # 停止フラグを設定
        
    def is_all_eights(self, number):
        num_str = str(number)  # 数字を文字列に変換
        return len(num_str) >= 3 and all(char == '8' for char in num_str)