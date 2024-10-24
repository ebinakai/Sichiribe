'''
動画ファイルからフレームを切り出す処理を行うワーカークラス

1. スレッド処理によって、GUIがフリーズしないようにする
2. FrameEditorクラスを使用してフレームの切り出し処理を行う
'''

from PySide6.QtCore import Signal, QThread
from cores.frameEditor import FrameEditor
import os
import logging

class   FrameDivideWorker(QThread):
    end = Signal(list, list)

    def __init__(self, params):
        super().__init__()
        self.video_path = params['video_path']
        self.video_skip_sec = params['video_skip_sec']
        self.save_frame = params['save_frame']
        self.out_dir = os.path.join(params['out_dir'], 'frames')
        self.click_points = params['click_points']
        self.fe = FrameEditor(params['sampling_sec'], params['num_frames'], params['num_digits'])
        self.logger = logging.getLogger('__main__').getChild(__name__)
        
    def run(self):
        frames = self.fe.frame_devide(self.video_path, 
                                      self.video_skip_sec, 
                                      self.save_frame,
                                      self.out_dir,
                                      click_points=self.click_points,
                                      )
            
        timestamps = self.fe.generate_timestamp(len(frames))
        self.end.emit(frames, timestamps)
        return None
