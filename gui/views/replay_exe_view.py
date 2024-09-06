from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QPixmap
from gui.utils.screen_manager import ScreenManager
from gui.utils.common import convert_cv_to_qimage, gen_graph
from gui.workers.frame_devide_worker import FrameDivideWorker
from gui.workers.replay_detect_worker import DetectWorker
from gui.workers.export_worker import ExportWorker
from cores.frameEditor import FrameEditor
import logging

class ReplayExeWindow(QWidget):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()
        
        self.screen_manager = screen_manager
        screen_manager.add_screen('replay_exe', self)
        
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self.initUI()

    def initUI(self):
        # レイアウトを作成
        main_layout = QVBoxLayout()
        graph_layout = QVBoxLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # レイアウトの設定
        graph_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # グラフの設定
        self.graph_label = QLabel()
        graph_layout.addWidget(self.graph_label)
        
        # フッター
        self.term_button = QPushButton('中止')
        self.term_button.setFixedWidth(100)
        self.term_button.clicked.connect(self.cancel)
        footer_layout.addWidget(self.term_button)

        self.term_label = QLabel()
        self.term_label.setStyleSheet('color: red')
        footer_layout.addWidget(self.term_label)
        
        footer_layout.addStretch()  # スペーサー
        
        # メインレイアウトに追加
        main_layout.addStretch()
        main_layout.addLayout(graph_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)
        
    def cancel(self):
        if self.worker is not None:
            self.term_label.setText('中止中...')
            self.worker.cancel()  # ワーカーに停止を指示
        
    def startup(self, params):
        # 初期化
        self.term_label.setText('')
        self.graph_label.setFixedSize(420, 500) 
        self.results = []
        self.failed_rates = []
        self.params = params

        # 最初のフレームを取得
        self.fe = FrameEditor(self.params['sampling_sec'], self.params['num_frames'], self.params['num_digits'])
        first_frame = self.fe.frame_devide(self.params['video_path'], 
                        self.params['video_skip_sec'],
                        save_frame=False,
                        is_crop=False,
                        extract_single_frame=True) 
        self.params['first_frame'] = first_frame
        
        # 切り取り領域選択
        self.screen_manager.get_screen('region_select').startup(self.params, 'replay_exe')
     
    def frame_devide_process(self, params):
        self.params = params
        self.screen_manager.get_screen('log').clear_log()
        self.screen_manager.show_screen('log')
        
        # ワーカーのインスタンスを作成
        self.worker = FrameDivideWorker(params)
        self.worker.finished.connect(self.frame_devide_finished)
        self.worker.start()
        self.logger.info('Frame Devide started.')

    def frame_devide_finished(self, frames, timestamps):
        self.logger.debug('timestamps: %s' % timestamps)
        self.logger.info('Frame Devide finished.')
        self.params['frames'] = frames
        self.params['timestamps'] = timestamps
        self.detect_process()
   
    def detect_process(self):
        self.worker = DetectWorker(self.params)
        self.worker.progress.connect(self.show_result)
        self.worker.finished.connect(self.detect_finished)
        self.worker.cancelled.connect(self.detect_cancelled)
        self.worker.start()
        self.logger.info('Detect started.')
        
    def show_result(self, result, failed_rate):
        self.screen_manager.show_screen('replay_exe')
        self.results.append(result)
        self.failed_rates.append(failed_rate)
        
        # グラフの更新
        title = 'Results'
        xlabel = 'Frame'
        ylabel1 = 'Failed Rate'
        ylabel2 = 'Detected results'
        graph = gen_graph(self.params['timestamps'][:len(self.results)], self.failed_rates, self.results, title, xlabel, ylabel1, ylabel2, self.screen_manager.check_if_dark_mode())

        # QLabel に画像を設定
        q_image = convert_cv_to_qimage(graph)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.graph_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.graph_label.setPixmap(scaled_pixmap)
        
    def detect_finished(self, results):
        self.graph_label.setFixedSize(QSize(10, 10))  # サイズの固定を解除
        self.graph_label.clear()
        self.logger.info('Detect finished.')
        self.logger.info(f"Results: {results}")
        self.params['results'] = results
        self.params['failed_rates'] = self.failed_rates
        QTimer.singleShot(1, self.export_process)
        
    def detect_cancelled(self, results):
        self.term_label.setText('中止しました')
        self.logger.info('Detect cancelled.')
        self.logger.info(f"Results: {results}")
        self.params['results'] = results
        self.params['failed_rates'] = self.failed_rates
        self.params['timestamps'] = self.params['timestamps'][:len(self.results)]
        QTimer.singleShot(1, self.export_process)

    def export_process(self):
        self.logger.info('Export started.')
        self.worker = ExportWorker(self.params)
        self.worker.finished.connect(self.export_finished)
        self.worker.start()

    def export_finished(self):
        self.logger.info('Export finished.')
        self.screen_manager.show_screen('menu')
        self.screen_manager.get_screen('log').clear_log()
        self.screen_manager.resie_defualt()
        self.screen_manager.center()
        self.params = None
   