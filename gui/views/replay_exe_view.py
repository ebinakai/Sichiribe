'''
動画ファイル解析を行うViewクラス

1. 実際のフレーム分割・推論処理はDetectWorkerクラスで行う
2. 以下の処理を行う
    - 最初のフレームを7セグ領域切り取り画面に渡す
    - 7セグ領域切り取り画面からのパラメータを受け取り、フレーム分割を行う
    - 分割フレームを受け取り、解析を行う
    - 結果を MplCanvas のグラフに表示する
    - 結果をファイルに出力する
    - メニュー画面に戻る
'''

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from gui.utils.screen_manager import ScreenManager
from gui.utils.exporter import export_result, export_params
from gui.widgets.mpl_canvas_widget import MplCanvas
from gui.workers.frame_devide_worker import FrameDivideWorker
from gui.workers.replay_detect_worker import DetectWorker
from cores.frameEditor import FrameEditor
import logging
from typing import List, Union
import numpy as np


class ReplayExeWindow(QWidget):
    def __init__(self, screen_manager: ScreenManager) -> None:
        super().__init__()

        self.screen_manager = screen_manager
        screen_manager.add_screen('replay_exe', self)

        self.logger = logging.getLogger('__main__').getChild(__name__)
        self.initUI()

    def initUI(self) -> None:
        main_layout = QVBoxLayout()
        graph_layout = QVBoxLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)

        graph_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.graph_label = MplCanvas()
        graph_layout.addWidget(self.graph_label)

        self.term_button = QPushButton('中止')
        self.term_button.setFixedWidth(100)
        self.term_button.clicked.connect(self.cancel)
        footer_layout.addWidget(self.term_button)

        self.term_label = QLabel()
        self.term_label.setStyleSheet('color: red')
        footer_layout.addWidget(self.term_label)

        footer_layout.addStretch()

        main_layout.addStretch()
        main_layout.addLayout(graph_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)

    def cancel(self) -> None:
        if self.worker is not None:
            self.term_label.setText('中止中...')
            self.worker.cancel()

    def startup(self, params: dict) -> None:
        self.graph_label.gen_graph(
            title='Results',
            xlabel='Timestamp',
            ylabel1='Failed Rate',
            ylabel2='Detected results',
            dark_theme=self.screen_manager.check_if_dark_mode())
        self.term_label.setText('')
        self.params = params
        self.results = []
        self.failed_rates = []
        self.graph_results = []
        self.graph_failed_rates = []
        self.graph_timestamps = []

        # 最初のフレームを取得
        self.fe = FrameEditor(
            self.params['sampling_sec'],
            self.params['num_frames'],
            self.params['num_digits'])
        first_frame = self.fe.frame_devide(self.params['video_path'],
                                           self.params['video_skip_sec'],
                                           save_frame=False,
                                           is_crop=False,
                                           extract_single_frame=True)
        self.params['first_frame'] = first_frame[0]

        self.screen_manager.get_screen(
            'region_select').startup(self.params, 'replay_exe')

    def frame_devide_process(self, params: dict) -> None:
        self.params = params
        self.screen_manager.get_screen('log').clear_log()
        self.screen_manager.show_screen('log')

        self.worker = FrameDivideWorker(params)
        self.worker.end.connect(self.frame_devide_finished)
        self.worker.start()
        self.logger.info('Frame Devide started.')

    def frame_devide_finished(
            self, frames: List[Union[str, np.ndarray]], timestamps: List[str]) -> None:
        self.logger.debug('timestamps: %s' % timestamps)
        self.logger.info('Frame Devide finished.')
        self.params['frames'] = frames
        self.params['timestamps'] = timestamps
        self.detect_process()

    def detect_process(self) -> None:
        self.worker = DetectWorker(self.params)
        self.worker.progress.connect(self.detect_progress)
        self.worker.finished.connect(self.detect_finished)
        self.worker.cancelled.connect(self.detect_cancelled)
        self.worker.model_not_found.connect(self.model_not_found)
        self.worker.start()
        self.logger.info('Detect started.')

    def model_not_found(self) -> None:
        self.term_label.setText('モデルが見つかりません')
        self.logger.error('Model not found.')
        self.clear_env()
        self.screen_manager.show_screen('menu')

    def detect_progress(self, result: int, failed_rate: float,
                        timestamp: str) -> None:
        self.screen_manager.show_screen('replay_exe')
        self.results.append(result)
        self.failed_rates.append(failed_rate)
        self.update_graph(result, failed_rate, timestamp)

    def update_graph(self, result: int, failed_rate: float,
                     timestamp: str) -> None:
        self.graph_results.append(result)
        self.graph_failed_rates.append(failed_rate)
        self.graph_timestamps.append(timestamp)
        self.graph_label.update_existing_plot(
            self.graph_timestamps,
            self.graph_failed_rates,
            self.graph_results)

    def detect_finished(self) -> None:
        self.graph_label.clear()
        self.logger.info('Detect finished.')
        self.logger.info(f"Results: {self.results}")
        self.params['results'] = self.results
        self.params['failed_rates'] = self.failed_rates
        params = self.params
        self.clear_env()
        self.export_process(params)

    def detect_cancelled(self) -> None:
        self.term_label.setText('中止しました')
        self.logger.info('Detect cancelled.')
        self.params['timestamps'] = self.params['timestamps'][:len(
            self.results)]

    def export_process(self, params: dict) -> None:
        self.logger.info('Data exporting...')

        export_result(params)
        export_params(params)

        self.screen_manager.popup(f"保存場所：{params['out_dir']}")
        self.screen_manager.show_screen('menu')

    def clear_env(self) -> None:
        self.graph_label.clear()
        self.term_label.setText('')
        self.params = None
        self.results = None
        self.failed_rates = None
        self.graph_results = None
        self.graph_failed_rates = None
        self.graph_timestamps = None
        self.fe = None
        self.logger.info('Environment cleared.')
        self.screen_manager.restore_screen_size()
