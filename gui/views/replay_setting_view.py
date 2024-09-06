from PySide6.QtWidgets import *
from gui.utils.screen_manager import ScreenManager
from cores.common import get_now_str
from cores.exporter import get_supported_formats
import os

class ReplaySettingsWindow(QWidget):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()

        self.screen_manager = screen_manager
        screen_manager.add_screen('replay_setting', self)
        self.initUI()

    def initUI(self):
        # レイアウトを作成
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # ファイルパス
        self.video_path = QLineEdit()
        self.video_path.setReadOnly(True)
        self.video_path_button = QPushButton('ファイル選択')
        self.video_path_button.clicked.connect(self.select_file)
        file_layout = QVBoxLayout()
        file_layout.addWidget(self.video_path)
        file_layout.addWidget(self.video_path_button)
        form_layout.addRow('解析する動画のパス：', file_layout)

        # 7セグメント表示器の桁数
        self.num_digits = QSpinBox()
        self.num_digits.setValue(4)
        self.num_digits.setFixedWidth(50)
        self.num_digits.setMinimum(1)
        form_layout.addRow('7セグメント表示器の桁数：', self.num_digits)

        # 動画をサンプリングする頻度
        self.sampling_sec = QSpinBox()
        self.sampling_sec.setValue(5)
        self.sampling_sec.setFixedWidth(50)
        self.sampling_sec.setMinimum(1)
        form_layout.addRow('動画をサンプリングする頻度 (秒)：', self.sampling_sec)

        # 一回のサンプリングで何フレーム取得するか
        self.num_frames = QSpinBox()
        self.num_frames.setValue(30)
        self.num_frames.setFixedWidth(50)
        self.num_frames.setMinimum(1)
        form_layout.addRow('一回のサンプリングで何フレーム取得するか：', self.num_frames)

        # 動画の解析を始めるタイミング
        self.video_skip_sec = QSpinBox()
        self.video_skip_sec.setValue(0)
        self.video_skip_sec.setFixedWidth(50)
        form_layout.addRow('動画の解析を始めるタイミング (秒)：', self.video_skip_sec)

        # 出力形式
        self.format = QComboBox()
        for fmt in get_supported_formats():
            self.format.addItem(fmt)
        form_layout.addRow('出力フォーマット：', self.format)

        # キャプチャしたフレームを保存するか
        self.save_frame = QCheckBox()
        form_layout.addRow('キャプチャしたフレームを保存する：', self.save_frame)

        # フッター
        self.back_button = QPushButton('戻る')
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(lambda: self.screen_manager.show_screen('menu'))
        footer_layout.addWidget(self.back_button)

        footer_layout.addStretch()  # スペーサーを追加してボタンを右寄せ
        
        self.confirm_txt = QLabel()
        self.confirm_txt.setStyleSheet('color: red')
        footer_layout.addWidget(self.confirm_txt)
        
        self.next_button = QPushButton('実行')
        self.next_button.setFixedWidth(100)

        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)  # フォーカス時にエンターキーで実行
        self.next_button.clicked.connect(self.startup)
        footer_layout.addWidget(self.next_button)
        
        # メインレイアウトに追加
        main_layout.addLayout(form_layout)
        main_layout.addLayout(footer_layout)
        
    def select_file(self):
        video_path, _ = QFileDialog.getOpenFileName(self, 'ファイルを選択', '', '動画ファイル (*.mp4 *.avi)')
        if video_path:
            self.video_path.setText(video_path)
            
    def back(self):
        self.confirm_txt.setText('')
        self.screen_manager.show_screen('menu')
        
    def startup(self):
        self.confirm_txt.setText('')
        
        if self.video_path.text() == '':
            self.confirm_txt.setText('動画ファイルを選択してください')
            return
        
        # 必要なパラメータを設定
        params = {
            'video_path': self.video_path.text(),
            'num_digits': self.num_digits.value(),
            'sampling_sec': self.sampling_sec.value(),
            'num_frames': self.num_frames.value(),
            'video_skip_sec': self.video_skip_sec.value(),
            'format': self.format.currentText(),
            'save_frame': self.save_frame.isChecked(),
            'out_dir': os.path.join(os.path.dirname(self.video_path.text()), get_now_str())
        }
        
        self.screen_manager.get_screen('replay_exe').startup(params)
        