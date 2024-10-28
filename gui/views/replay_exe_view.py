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

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from gui.widgets.custom_qwidget import CustomQWidget
from gui.utils.screen_manager import ScreenManager
from gui.utils.exporter import export_result, export_params
from gui.widgets.mpl_canvas_widget import MplCanvas
from gui.workers.frame_devide_worker import FrameDivideWorker
from gui.workers.replay_detect_worker import DetectWorker
from cores.frame_editor import FrameEditor
import logging
from typing import List, Dict, Union, Any
import numpy as np


class ReplayExeWindow(CustomQWidget):
    def __init__(self, screen_manager: ScreenManager) -> None:
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self.screen_manager = screen_manager
        self.params: Dict[str, Any]
        self.results: List[int]
        self.failed_rates: List[float]
        self.graph_results: List[int]
        self.graph_failed_rates: List[float]
        self.graph_timestamps: List[str]

        super().__init__()
        screen_manager.add_screen('replay_exe', self)

    def initUI(self):
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
        if self.dt_worker is not None:
            self.term_label.setText('中止中...')
            self.dt_worker.cancel()

    def trigger(self, action, *args):
        if action == 'startup':
            self.startup(*args)
        elif action == 'continue':
            self.frame_devide_process(*args)

    def startup(self, params: Dict) -> None:
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
        self.params['first_frame'] = first_frame

        if 'click_points' in self.params and len(self.params['click_points']):
            self.screen_manager.get_screen(
                'replay_threshold').trigger('startup', self.params)
        else:
            self.screen_manager.get_screen('region_select').trigger(
                'startup', self.params, 'replay_exe')

    def frame_devide_process(self, params: Dict) -> None:
        self.params = params
        self.screen_manager.get_screen('log').trigger('clear')
        self.screen_manager.show_screen('log')

        self.fd_worker = FrameDivideWorker(params)
        self.fd_worker.end.connect(self.frame_devide_finished)
        self.fd_worker.start()
        self.logger.info('Frame Devide started.')

    def frame_devide_finished(
            self, frames: List[Union[str, np.ndarray]], timestamps: List[str]) -> None:
        self.logger.debug('timestamps: %s' % timestamps)
        self.logger.info('Frame Devide finished.')
        self.params['frames'] = frames
        self.params['timestamps'] = timestamps
        self.detect_process()

    def detect_process(self) -> None:
        self.dt_worker = DetectWorker(self.params)
        self.dt_worker.progress.connect(self.detect_progress)
        self.dt_worker.finished.connect(self.detect_finished)
        self.dt_worker.cancelled.connect(self.detect_cancelled)
        self.dt_worker.model_not_found.connect(self.model_not_found)
        self.dt_worker.start()
        self.logger.info('Detect started.')

    def model_not_found(self) -> None:
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

    def export_process(self, params: Dict) -> None:
        self.logger.info('Data exporting...')

        export_result(params)
        export_params(params)

        self.screen_manager.popup(f"保存場所：{params['out_dir']}")
        self.screen_manager.show_screen('menu')

    def clear_env(self) -> None:
        self.graph_label.clear()
        self.term_label.setText('')
        self.logger.info('Environment cleared.')
        self.screen_manager.restore_screen_size()
