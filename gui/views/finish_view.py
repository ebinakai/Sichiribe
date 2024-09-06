from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from gui.utils.screen_manager import ScreenManager
import logging

class FinishWindow(QWidget):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()
        self.screen_manager = screen_manager
        screen_manager.add_screen('finish', self)
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self.initUI()

    def initUI(self):
        # レイアウトを追加
        main_layout = QVBoxLayout()
        header_layout = QVBoxLayout()
        contents_layout = QHBoxLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contents_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ヘッダーレイアウト
        self.header_description = QLabel("解析が完了しました。")
        header_layout.addWidget(self.header_description)

        # コンテンツレイアウト
        self.contents_label = QLabel("保存場所: ")
        self.contents = QLabel()
        contents_layout.addWidget(self.contents_label)
        contents_layout.addWidget(self.contents)
        
        # フッターレイアウト
        self.next_button = QPushButton('最初に戻る')
        self.next_button.setFixedWidth(100)
        self.next_button.setDefault(True)
        self.next_button.setAutoDefault(True)
        self.next_button.clicked.connect(self.next)
        footer_layout.addStretch()
        footer_layout.addWidget(self.next_button)
        
        # メインレイアウトに追加
        main_layout.addLayout(header_layout)
        main_layout.addLayout(contents_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)
        
    def next(self):
        self.screen_manager.show_screen('menu')
        self.parmas = None
        
    def startup(self, params):
        self.contents.setText(params['out_dir'])
        self.screen_manager.show_screen('finish')