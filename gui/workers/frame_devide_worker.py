from PyQt6.QtCore import pyqtSignal, QThread
from cores.frameEditor import FrameEditor
import os
import logging

class   FrameDivideWorker(QThread):
    finished = pyqtSignal(list, list)

    def __init__(self, params):
        super().__init__()
        self.video_path = params['video_path']
        self.video_skip_sec = params['video_skip_sec']
        self.save_frame = params['save_frame']
        self.out_dir = os.path.join(params['out_dir'], 'frames')
        self.click_points = params['click_points']
        self.fe = FrameEditor(params['sampling_sec'], params['num_frames'], params['num_digits'])
        
    def run(self):
        # フレームの切り出し
        frames = self.fe.frame_devide(self.video_path, 
                                      self.video_skip_sec, 
                                      self.save_frame,
                                      self.out_dir,
                                      click_points=self.click_points,
                                      )
            
        timestamps = self.fe.generate_timestamp(len(frames))
        self.finished.emit(frames, timestamps)  # 処理完了を通知   