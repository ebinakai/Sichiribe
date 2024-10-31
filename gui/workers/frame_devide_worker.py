"""
動画ファイルからフレームを切り出す処理を行うワーカークラス

1. スレッド処理によって、GUIがフリーズしないようにする
2. FrameEditorクラスを使用してフレームの切り出し処理を行う
"""

from PySide6.QtCore import Signal, QThread
from gui.utils.data_store import DataStore
from cores.frame_editor import FrameEditor
from pathlib import Path
import logging


class FrameDivideWorker(QThread):
    end = Signal(list, list)

    def __init__(self) -> None:
        super().__init__()
        self.data_store = DataStore.get_instance()
        self.out_dir = str(Path(self.data_store.get("out_dir")) / "frames")
        self.fe = FrameEditor(self.data_store.get("num_digits"))
        self.logger = logging.getLogger("__main__").getChild(__name__)

    def run(self) -> None:
        frames, timestamps = self.fe.frame_devide(
            video_path=self.data_store.get("video_path"),
            video_skip_sec=self.data_store.get("video_skip_sec"),
            sampling_sec=self.data_store.get("sampling_sec"),
            batch_frames=self.data_store.get("batch_frames"),
            save_frame=self.data_store.get("save_frame"),
            out_dir=self.out_dir,
            click_points=self.data_store.get("click_points"),
        )

        self.end.emit(frames, timestamps)
        return None
