from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QPixmap
from gui.utils.screen_manager import ScreenManager
from gui.utils.common import convert_cv_to_qimage, gen_graph
from gui.workers.detect_worker import DetectWorker
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
        self.term_button.clicked.connect(self.termination)
        footer_layout.addWidget(self.term_button)

        self.term_label = QLabel()
        self.term_label.setStyleSheet('color: red')
        footer_layout.addWidget(self.term_label)
        
        footer_layout.addStretch()  # スペーサー
        
        main_layout.addStretch()
        main_layout.addLayout(graph_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)
        
    def termination(self):
        if self.worker is not None:
            self.term_label.setText('中止中...')
            self.worker.stop()  # ワーカーに停止を指示
        
    def detect_process(self, params):
        # 初期化
        self.term_label.setText('')
        self.graph_label.setFixedSize(420, 500) 
        self.results = []
        self.failed_rates = []
        
        self.params = params
        self.worker = DetectWorker(params)
        self.worker.proguress.connect(self.show_result)
        self.worker.finished.connect(self.detect_finished)
        self.worker.termination.connect(self.detect_termination)
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
        
        # QImage への変換
        q_image = convert_cv_to_qimage(graph)
        
        # QLabel のサイズに合わせて QPixmap をリサイズ
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.graph_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        # QLabel に画像を設定
        self.graph_label.setPixmap(scaled_pixmap)
        
    def detect_finished(self, results):
        self.graph_label.setFixedSize(QSize(10, 10))  # サイズの固定を解除
        self.graph_label.clear()
        self.logger.info('Detect finished.')
        self.logger.info(f"Results: {results}")
        self.params['results'] = results
        self.params['failed_rates'] = self.failed_rates
        QTimer.singleShot(1, lambda: self.screen_manager.get_screen('log').export_process(self.params))
        
    def detect_termination(self, results):
        self.term_label.setText('中止しました')
        self.logger.info('Detect cancelled.')
        self.logger.info(f"Results: {results}")
        self.params['results'] = results
        self.params['failed_rates'] = self.failed_rates
        self.params['timestamps'] = self.params['timestamps'][:len(self.results)]
        QTimer.singleShot(1, lambda: self.screen_manager.get_screen('log').export_process(self.params))
        