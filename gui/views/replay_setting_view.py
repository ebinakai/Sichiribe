from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QSpinBox, QComboBox, QCheckBox, QFileDialog
from PyQt6.QtCore import QTimer

class ReplaySettingsWindow(QWidget):
    def __init__(self, screen_manager):
        super().__init__()

        self.screen_manager = screen_manager
        screen_manager.add_screen('replay_setting', self)

        self.setWindowTitle('ファイル読み込み設定')
        self.setGeometry(200, 200, 640, 480)

        # メインレイアウトを作成
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        form_layout = QFormLayout()
        button_layout = QHBoxLayout()

        # ファイルパス
        self.video_path = QLineEdit()
        self.video_path.setReadOnly(True)
        self.video_path.setText('/Users/kaiebina/develop/pyworks/Sichiribe/contents/video_cropped.mp4')
        self.video_path_button = QPushButton('ファイル選択')
        self.video_path_button.clicked.connect(self.select_file)
        file_layout = QVBoxLayout()
        file_layout.addWidget(self.video_path)
        file_layout.addWidget(self.video_path_button)
        form_layout.addRow('解析する動画のパス：', file_layout)


        # 7セグメント表示器の桁数
        self.num_digits = QSpinBox()
        self.num_digits.setValue(4)
        form_layout.addRow('7セグメント表示器の桁数：', self.num_digits)

        # 動画をサンプリングする頻度
        self.sampling_sec = QSpinBox()
        self.sampling_sec.setValue(5)
        form_layout.addRow('動画をサンプリングする頻度 (秒)：', self.sampling_sec)

        # 一回のサンプリングで何フレーム取得するか
        self.num_frames = QSpinBox()
        self.num_frames.setValue(30)
        form_layout.addRow('一回のサンプリングで何フレーム取得するか：', self.num_frames)

        # 動画の解析を始めるタイミング
        self.video_skip_sec = QSpinBox()
        self.video_skip_sec.setValue(0)
        form_layout.addRow('動画の解析を始めるタイミング (秒)：', self.video_skip_sec)

        # 出力形式
        self.format = QComboBox()
        self.format.addItems(['json', 'csv'])
        form_layout.addRow('出力形式：', self.format)

        # キャプチャしたフレームを保存するか
        self.save_frame = QCheckBox()
        form_layout.addRow('キャプチャしたフレームを保存する：', self.save_frame)

        # 「戻る」ボタン
        self.back_button = QPushButton('戻る')
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(lambda: self.screen_manager.show_screen('menu'))
        button_layout.addWidget(self.back_button)

        button_layout.addStretch()  # スペーサー
        
        # 「実行」ボタン
        self.next_button = QPushButton('実行')
        self.next_button.setFixedWidth(100)
        self.next_button.setFocus()  # フォーカスを設定
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)  # フォーカス時にエンターキーで実行
        self.next_button.clicked.connect(self.run_file)
        button_layout.addWidget(self.next_button)
        
        # メインレイアウトに追加
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        
    def select_file(self):
        video_path, _ = QFileDialog.getOpenFileName(self, 'ファイルを選択', '', '動画ファイル (*.mp4 *.avi)')
        if video_path:
            self.video_path.setText(video_path)

    def run_file(self):
        # 読み込み処理は重いので、ここでimportする
        import replay
        
        # ファイル読み込みの処理をここに追加
        video_path = self.video_path.text()
        num_digits = self.num_digits.value()
        sampling_sec = self.sampling_sec.value()
        num_frames = self.num_frames.value()
        video_skip_sec = self.video_skip_sec.value()
        format = self.format.currentText()
        save_frame = self.save_frame.isChecked()
        
        self.screen_manager.show_screen('log')

        # ここで入力された値を用いて処理を実行
        replay.main(video_path, 
                    num_digits, 
                    sampling_sec, 
                    num_frames, 
                    video_skip_sec, 
                    format, 
                    save_frame
                )
        
        # self.screen_manager.show_screen('menu')