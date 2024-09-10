from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap
from gui.utils.screen_manager import ScreenManager
from gui.utils.common import convert_cv_to_qimage, resize_image
from gui.workers.live_feed_worker import LiveFeedWorker
import logging

class LiveFeedWindow(QWidget):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()
        
        self.screen_manager = screen_manager
        screen_manager.add_screen('live_feed', self)
        
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self.initUI()

    def initUI(self):
        # レイアウトを作成
        main_layout = QVBoxLayout()
        header_layout = QVBoxLayout()
        feed_layout = QVBoxLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # レイアウトの設定
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feed_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # ヘッダーレイアウト
        self.header_description = QLabel("画角を調整してください")
        header_layout.addWidget(self.header_description)
        
        # フレームの設定
        self.feed_label = QLabel()
        feed_layout.addWidget(self.feed_label)
        
        # フッターレイアウト
        self.back_button = QPushButton('戻る')
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self.back)
        
        self.next_button = QPushButton('次へ')
        self.next_button.setFixedWidth(100)
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)  # フォーカス時にエンターキーで実行
        self.next_button.clicked.connect(self.next)

        footer_layout.addWidget(self.back_button)
        footer_layout.addStretch()  # スペーサーを追加してボタンを右寄せ
        footer_layout.addWidget(self.next_button)

        # メインレイアウトに追加
        main_layout.addLayout(header_layout)
        main_layout.addStretch()
        main_layout.addLayout(feed_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)
        
    def back(self):
        self.logger.debug("Back button clicked.")
        if self.worker is not None:
            self.worker.cancel()
        
    def next(self):
        self.logger.debug("Next button clicked.")
        if self.worker is not None:
            self.worker.stop()  # ワーカーに停止を指示
        
    def startup(self, params):
        self.logger.info("Starting LiveFeedWindow.")
        self.feed_label.setText("読込中...")
        self.screen_manager.show_screen('live_feed')
        self.logger.info('Capture Feed starting...')
        
        # 初期化
        self.results = []
        self.failed_rates = []
        window_pos, window_size = self.screen_manager.save_screen_size()
        
        # 表示画像サイズを計算
        window_rect = self.geometry()
        self.target_width = int(window_rect.width() * 0.8)
        self.target_height = int(window_rect.height() * 0.8)
        self.logger.debug('window width: %d window height: %d' % (window_rect.width(), window_rect.height()))
                
        self.params = params
        self.worker = LiveFeedWorker(params, self.target_width, self.target_height)  # できるだけ小さな画像で処理
        self.worker.cap_size.connect(self.recieve_cap_size)
        self.worker.progress.connect(self.show_feed)
        self.worker.end.connect(self.feed_finished)
        self.worker.cancelled.connect(self.feed_cancelled)
        self.worker.error.connect(self.feed_error)
        self.worker.start()
        self.logger.info('Feed started.')
        
    def recieve_cap_size(self, cap_size):
        self.params['cap_size'] = cap_size
        self.logger.debug('Capture size: %d x %d' % (cap_size[0], cap_size[1]))

    def show_feed(self, frame):
        frame, _ = resize_image(frame, self.target_width, self.target_height)
        qimage = convert_cv_to_qimage(frame)
        self.feed_label.setPixmap(QPixmap(qimage))
        
    def feed_finished(self, first_frame):
        self.logger.info('Feed finished.')
        self.params['first_frame'] = first_frame
        params = self.params
        self.clear_env()
        QTimer.singleShot(10, lambda: self.screen_manager.get_screen('region_select').startup(params, 'live_feed'))
    
    def feed_cancelled(self):
        self.clear_env()
        QTimer.singleShot(1, lambda: self.screen_manager.show_screen('live_setting'))
        self.logger.info('Feed cancelled.')
        
    def feed_error(self):
        self.clear_env()
        QTimer.singleShot(1, lambda: self.screen_manager.show_screen('live_setting'))
        self.logger.error('Feed missing frame.')
        
    def clear_env(self):
        self.feed_label.clear()
        self.target_width = None
        self.target_height = None
        self.params = None
        self.logger.info('Environment cleared.')
        self.screen_manager.restore_screen_size()
        