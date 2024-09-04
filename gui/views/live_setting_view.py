from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QComboBox, QSpinBox, QCheckBox
from PyQt6.QtCore import QTimer
from gui.utils.screen_manager import ScreenManager
from cores.exporter import get_supported_formats

class LiveSettingsWindow(QWidget):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()

        self.screen_manager = screen_manager
        screen_manager.add_screen('live_setting', self)
        self.initUI()

    def initUI(self):
        # レイアウトを作成
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.camera_id = QSpinBox()
        self.camera_id.setValue(0)
        form_layout.addRow('カメラID：', self.camera_id)

        self.num_digits = QSpinBox()
        self.num_digits.setValue(4)
        self.num_digits.setMinimum(1)
        form_layout.addRow('7セグ表示機の桁数：', self.num_digits)

        self.sampling_sec = QSpinBox()
        self.sampling_sec.setValue(10)
        self.sampling_sec.setMinimum(1)
        form_layout.addRow('動画をサンプリングする頻度(秒)：', self.sampling_sec)

        self.num_frames = QSpinBox()
        self.num_frames.setValue(10)
        self.num_frames.setMinimum(1)
        form_layout.addRow('1回のサンプリング取得するフレーム数：', self.num_frames)

        self.total_sampling_min = QSpinBox()
        self.total_sampling_min.setValue(1)
        self.total_sampling_min.setMinimum(1)
        form_layout.addRow('総サンプリング時間(分)：', self.total_sampling_min)

        self.format = QComboBox()
        for fmt in get_supported_formats():
            self.format.addItem(fmt)
        form_layout.addRow('ファイルフォーマット：', self.format)
        
        self.save_frame = QCheckBox()
        form_layout.addRow('フレームを保存する：', self.save_frame)

        # フッター
        self.back_button = QPushButton('戻る')
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(lambda: self.screen_manager.show_screen('menu'))
        footer_layout.addWidget(self.back_button)

        footer_layout.addStretch()  # スペーサー
        
        self.next_button = QPushButton('実行')
        self.next_button.setFixedWidth(100)
        self.next_button.setFocus()  # フォーカスを設定
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)  # フォーカス時にエンターキーで実行
        self.next_button.clicked.connect(self.run_live)
        footer_layout.addWidget(self.next_button)

        # メインレイアウトに追加
        main_layout.addLayout(form_layout)
        main_layout.addLayout(footer_layout)

    def run_live(self):
        # 読み込み処理は重いので、ここでimportする
        import live
        
        camera_id = self.camera_id.value()
        num_digits = self.num_digits.value()
        sampling_sec = self.sampling_sec.value()
        num_frames = self.num_frames.value()
        total_sampling_min = self.total_sampling_min.value()
        format = self.format.currentText()
        save_frame = self.save_frame.isChecked()
        
        live.main(device=camera_id, 
                  num_digits=num_digits, 
                  sampling_sec=sampling_sec, 
                  num_frames=num_frames, 
                  total_sampling_sec=total_sampling_min * 60, 
                  format=format, 
                  save_frame=save_frame)
