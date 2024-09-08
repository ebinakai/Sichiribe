from PySide6.QtCore import Signal, QThread
# from cores.cnn import CNN as Detector
from cores.frameEditor import FrameEditor
import os
import cv2
import numpy as np
import logging

class DetectWorker(QThread):
    progress = Signal(int, float, str)
    send_image = Signal(np.ndarray)
    end = Signal()
    cancelled = Signal()
    model_not_found = Signal()

    def __init__(self, params):
        super().__init__()
        self.params = params
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self._is_cancelled = False  # 停止フラグ
        self.binarize_th = None
        self._is_capturing = True