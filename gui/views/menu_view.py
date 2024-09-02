from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt6.QtCore import QTimer

class MenuWindow(QWidget):
    def __init__(self, screen_manager):
        super().__init__()
        
        self.screen_manager = screen_manager
        screen_manager.add_screen('menu', self)
        
        self.setWindowTitle('Menu')
        self.setGeometry(200, 200, 640, 480)
        
        # レイアウトを作成
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        self.live_button = QPushButton('ライブカム')
        self.live_button.setFixedHeight(50)
        self.live_button.setFixedWidth(200)
        button_layout.addWidget(self.live_button)
        self.live_button.clicked.connect(lambda: self.screen_manager.show_screen('live_setting'))

        self.replay_button = QPushButton('ファイル読み込み')
        self.replay_button.setFixedHeight(50)
        self.replay_button.setFixedWidth(200)
        button_layout.addWidget(self.replay_button)
        self.replay_button.clicked.connect(lambda: self.screen_manager.show_screen('replay_setting'))
        
        self.quit_button = QPushButton('quit')
        self.quit_button.setFixedWidth(100)
        self.quit_button.clicked.connect(lambda: self.screen_manager.quit())
        footer_layout.addWidget(self.quit_button)
        footer_layout.addStretch()
        
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)
        
        # ウィンドウが表示された後にフォーカスを外すためのタイマー設定
        QTimer.singleShot(0, self.live_button.clearFocus)
