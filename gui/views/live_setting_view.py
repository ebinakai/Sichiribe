'''
リアルタイム解析の設定を行うViewクラス

1. 以下を設定する
    - カメラID
    - 7セグメント表示器の桁数
    - 動画をサンプリングする頻度
    - 一回のサンプリングで何フレーム取得するか
    - 総サンプリング時間
    - 出力形式
    - キャプチャしたフレームを保存するか
2. 実行ボタンを押すと、次の画面に遷移する
'''

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QComboBox, QSpinBox, QCheckBox, QLineEdit, QFileDialog, QLabel
from gui.utils.screen_manager import ScreenManager
from cores.exporter import get_supported_formats
from cores.common import get_now_str
import logging
import os

class LiveSettingsWindow(QWidget):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()

        self.screen_manager = screen_manager
        screen_manager.add_screen('live_setting', self)
        self.initUI()
        self.logger = logging.getLogger('__main__').getChild(__name__)

    def initUI(self):
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.device_num = QSpinBox()
        self.device_num.setValue(0)
        self.device_num.setFixedWidth(50)
        form_layout.addRow('カメラID：', self.device_num)

        self.num_digits = QSpinBox()
        self.num_digits.setValue(4)
        self.num_digits.setFixedWidth(50)
        self.num_digits.setMinimum(1)
        form_layout.addRow('7セグ表示機の桁数：', self.num_digits)

        self.sampling_sec = QSpinBox()
        self.sampling_sec.setValue(10)
        self.sampling_sec.setFixedWidth(50)
        self.sampling_sec.setMinimum(3)
        self.sampling_sec.valueChanged.connect(self.calc_max_frames)
        form_layout.addRow('動画をサンプリングする頻度(秒)：', self.sampling_sec)

        self.num_frames = QSpinBox()
        self.num_frames.setValue(10)
        self.num_frames.setFixedWidth(50)
        self.num_frames.setMinimum(1)
        self.num_frames.setMaximum(60)
        form_layout.addRow('1回のサンプリング取得するフレーム数：', self.num_frames)

        self.total_sampling_min = QSpinBox()
        self.total_sampling_min.setValue(1)
        self.total_sampling_min.setFixedWidth(50)
        self.total_sampling_min.setMinimum(1)
        self.total_sampling_min.setMaximum(600)
        form_layout.addRow('総サンプリング時間(分)：', self.total_sampling_min)

        self.format = QComboBox()
        for fmt in get_supported_formats():
            self.format.addItem(fmt)
        form_layout.addRow('出力フォーマット：', self.format)
        
        self.save_frame = QCheckBox()
        form_layout.addRow('フレームを保存する：', self.save_frame)
        
        self.out_dir = QLineEdit()
        self.out_dir.setReadOnly(True)
        self.out_dir_button = QPushButton('フォルダ選択')
        self.out_dir_button.clicked.connect(self.select_folder)
        file_layout = QVBoxLayout()
        file_layout.addWidget(self.out_dir)
        file_layout.addWidget(self.out_dir_button)
        form_layout.addRow('保存場所：', file_layout)

        self.back_button = QPushButton('戻る')
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(lambda: self.screen_manager.show_screen('menu'))
        footer_layout.addWidget(self.back_button)

        footer_layout.addStretch()  # スペーサー
        
        self.confirm_txt = QLabel()
        self.confirm_txt.setStyleSheet('color: red')
        footer_layout.addWidget(self.confirm_txt)
        
        self.next_button = QPushButton('実行')
        self.next_button.setFixedWidth(100)
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)
        self.next_button.clicked.connect(self.startup)
        footer_layout.addWidget(self.next_button)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(footer_layout)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'フォルダを選択', '')

        if folder_path:
            self.out_dir.setText(folder_path)
            
    def calc_max_frames(self):
        sampling_sec = self.sampling_sec.value()
        self.num_frames.setMaximum(sampling_sec * 5)
            
    def startup(self):
        if self.out_dir.text() == '':
            self.confirm_txt.setText('保存場所を選択してください')
            return
        else:
            self.confirm_txt.setText('')
        
        params = {
            'device_num': self.device_num.value(),
            'num_digits': self.num_digits.value(),
            'sampling_sec': self.sampling_sec.value(),
            'num_frames': self.num_frames.value(),
            'total_sampling_sec': self.total_sampling_min.value() * 60,
            'format': self.format.currentText(),
            'save_frame': self.save_frame.isChecked(),
            'out_dir': os.path.join(self.out_dir.text(), get_now_str())
        }
    
        self.logger.debug("Starting live feed with params: %s", params)
        self.screen_manager.get_screen('live_feed').startup(params)

