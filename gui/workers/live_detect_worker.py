from PySide6.QtCore import Signal, QThread
# from cores.cnn import CNN as Detector
from cores.cnn_lite import CNNLite as Detector
from cores.capture import FrameCapture
from cores.frameEditor import FrameEditor
import logging
import time
from datetime import timedelta
import os
import cv2
import numpy as np

class DetectWorker(QThread):
    progress = Signal(int, float, str)
    send_image = Signal(np.ndarray)
    finished = Signal()
    cancelled = Signal()

    def __init__(self, params):
        super().__init__()
        self.params = params
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self._is_cancelled = False  # 停止フラグ
        self.binarize_th = None
        self._is_capturing = True

    def run(self):
        self.logger.info("DetectWorker started.")
        
        if self.params['save_frame']:
          os.makedirs(os.path.join(self.params['out_dir'], 'frames'), exist_ok=True)
        
        self.fc = FrameCapture(device_num=self.params['device_num'])
        self.fc.set_cap_size(self.params['cap_size'][0], self.params['cap_size'][1])
        
        self.fe = FrameEditor(num_digits=self.params['num_digits'])
        self.dt = Detector(self.params['num_digits'])
        self.dt.load()
        
        start_time = time.time()
        end_time = time.time() + self.params['total_sampling_sec']
        frame_count = 0
        timestamps = []
        while time.time() < end_time:
          temp_time = time.time()
          frames = []   
          
          if self._is_cancelled:
            self.cancelled.emit()
            self.clear_env()
            return

          # タイムスタンプを "HH:MM:SS" 形式で生成
          elapsed_time = int(time.time() - start_time)
          timestamp = timedelta(seconds=elapsed_time)
          timestamp_str = str(timestamp)
          timestamps.append(timestamp_str)
          
          self._is_capturing = True
          for i in range(self.params['num_frames']):
            frame = self.fc.capture()
            
            if frame is None:
              continue
            
            # 推論処理
            cropped_frame = self.fe.crop(frame, self.params['click_points'])
            frames.append(cropped_frame)
            
            # UI に画像を通知
            image_bin = self.dt.preprocess_binarization(cropped_frame, self.binarize_th)
            self.send_image.emit(image_bin)
            
            # フレームを保存
            if self.params['save_frame']:
              frame_filename = os.path.join(self.params['out_dir'], 'frames', f"frame_{frame_count}.jpg")
              cv2.imwrite(frame_filename, cropped_frame)
              self.logger.debug(f"Frame {frame_count} has been saved as: {frame_filename}")
              frame_count += 1
          self._is_capturing = False
              
          # 推論処理
          value, failed_rate = self.dt.detect(frames, self.binarize_th)
          self.logger.info(f"Detected: {value}, Failed rate: {failed_rate}")
          
          # UI に推論結果を通知
          self.progress.emit(value, failed_rate, timestamp_str)
                
          elapsed_time = time.time() - temp_time
          time_to_wait = max(0, self.params['sampling_sec'] - elapsed_time)

          if time_to_wait > 0:
            self.logger.debug(f"Waiting for {time_to_wait:.2f}s")
            time.sleep(time_to_wait)
        
        self.clear_env()
        self.finished.emit()
        
    def cancel(self):
        self.logger.info("DetectWorker terminating...") 
        self._is_cancelled = True  # 停止フラグを設定

    def update_binarize_th(self, value):
        self.binarize_th = value
        self.logger.info(f"Update binarize_th: {self.binarize_th}")
        
        # UI に画像を通知
        if not self._is_capturing:
          frame = self.fc.capture()
          if frame is None:
            self.logger.debug("Frame missing.")
          cropped_frame = self.fe.crop(frame, self.params['click_points'])
          image_bin = self.dt.preprocess_binarization(cropped_frame, self.binarize_th)
          self.send_image.emit(image_bin)
        
    def clear_env(self):
        self.fc.release()
        self.fc = None
        self.dt = None
        self.fe = None
        self.logger.info("Clear environment.")
