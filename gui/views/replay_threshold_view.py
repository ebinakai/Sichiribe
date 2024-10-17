'''
動画ファイル解析のための二値化しきい値を設定するViewクラス

1. 初期値は大津の二値化を適用した画像を表示
2. スライダーでしきい値を設定し、画像を更新する
3. 次へボタンを押すと、しきい値をパラメータに保存し、次の画面に遷移する
'''

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QLabel, QSlider
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from gui.utils.screen_manager import ScreenManager
from gui.utils.common import convert_cv_to_qimage
from cores.frameEditor import FrameEditor
from cores.detector import Detector
import logging
import numpy as np

class ReplayThresholdWindow(QWidget):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()
        
        self.screen_manager = screen_manager
        screen_manager.add_screen('replay_threshold', self)
        
        self.fe = FrameEditor()
        self.dt = Detector()
        
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self.initUI()
        
    # レイアウトを作成
    def initUI(self):
        main_layout = QVBoxLayout()
        extracted_image_layout = QHBoxLayout()
        form_layout = QFormLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # レイアウトの設定
        extracted_image_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 選択領域表示用レイアウト
        self.extracted_label = QLabel()
        self.extracted_label.setMinimumHeight(100)
        extracted_image_layout.addWidget(self.extracted_label)
        
        # しきい値設定
        slider_layout = QHBoxLayout()  # 水平レイアウトを作成
        self.binarize_th = QSlider()
        self.binarize_th.setFixedWidth(200)
        self.binarize_th.setRange(0, 255)
        self.binarize_th.setOrientation(Qt.Orientation.Horizontal)
        self.binarize_th.valueChanged.connect(self.update_binarize_th)
        self.binarize_th_label = QLabel()
        slider_layout.addWidget(self.binarize_th)  # スライダーを追加
        slider_layout.addWidget(self.binarize_th_label)  # ラベルを追加
        form_layout.addRow("画像二値化しきい値：", slider_layout)   # そのレイアウトをaddRowに渡す

        # フッターレイアウト
        self.next_button = QPushButton('次へ')
        self.next_button.setFixedWidth(100)
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)  # フォーカス時にエンターキーで実行
        self.next_button.clicked.connect(self.next)
        
        footer_layout.addStretch()  # スペーサー
        footer_layout.addWidget(self.next_button)
        
        # メインレイアウトに追加
        main_layout.addLayout(extracted_image_layout)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)
     
    def startup(self, params):
        self.logger.info('Starting ReplayThresholdWindow.')
        self.screen_manager.show_screen('replay_threshold')
        
        # ウィンドウの位置とサイズを保存
        window_pos, window_size = self.screen_manager.save_screen_size()
     
        # 初期化
        self.params = params
        self.threshold = None
        self.first_frame = self.fe.crop(params['first_frame'], params['click_points'])
        self.binarize_th.setValue(0)
        self.binarize_th_label.setText('自動設定')
        self.update_binarize_th(0)
               
    def update_binarize_th(self, value):
        self.threshold = None if value == 0 else value
        binarize_th_str = '自動設定' if self.threshold is None else str(self.threshold)
        self.binarize_th_label.setText(binarize_th_str)
        
        # 画像の二値化
        image_bin = self.dt.preprocess_binarization(self.first_frame, self.threshold)
        self.display_extract_image(image_bin)

    def display_extract_image(self, image: np.ndarray):
        q_image = convert_cv_to_qimage(image)
        self.extracted_label.setPixmap(QPixmap.fromImage(q_image))
        
    def next(self):
        self.logger.info("Set threshold finished.")
        self.params['threshold'] = self.threshold
        self.clear_env()

        self.screen_manager.get_screen('replay_exe').frame_devide_process(self.params)
        self.params = None

    def clear_env(self):
        self.extracted_label.clear()
        self.first_frame = None
        self.threshold = None
        self.logger.info('Environment cleared.')
        self.screen_manager.restore_screen_size()

        