from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import Signal, QObject
from gui.utils.screen_manager import ScreenManager
import logging

# ログをメインスレッドに送信するためのクラス
class LogEmitter(QObject):
    new_log = Signal(str)

class QTextEditLogger(logging.Handler):
    def __init__(self, emitter: LogEmitter):
        super().__init__()
        self.emitter = emitter

    def emit(self, record):
        log_entry = self.format(record)
        self.emitter.new_log.emit(log_entry)

class LogWindow(QWidget):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()
        self.screen_manager = screen_manager
        screen_manager.add_screen('log', self)
        self.initUI()

    def initUI(self):
        # レイアウトを追加
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

        # ログエミッタを作成し、ログハンドラを設定
        self.emitter = LogEmitter()
        self.logger = logging.getLogger('__main__')
        log_handler = QTextEditLogger(self.emitter)
        self.logger.addHandler(log_handler)

        # シグナルとスロットの接続
        self.emitter.new_log.connect(self.append_log)

    def append_log(self, message):
        self.log_display.append(message)

    def clear_log(self):
        self.log_display.clear()