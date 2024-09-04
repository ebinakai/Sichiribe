from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import pyqtSignal, QObject
from gui.utils.screen_manager import ScreenManager
from gui.workers.frame_devide_worker import FrameDivideWorker
from gui.workers.export_worker import ExportWorker
import logging

# ログをメインスレッドに送信するためのクラス
class LogEmitter(QObject):
    new_log = pyqtSignal(str)

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

    def frame_devide_process(self, params):
        self.params = params
        
        # ワーカーのインスタンスを作成
        self.screen_manager.show_screen('log')
        self.worker = FrameDivideWorker(params)
        self.worker.finished.connect(self.frame_devide_finished)
        self.worker.start()
        self.logger.info('Frame Devide started.')

    def frame_devide_finished(self, frames, timestamps):
        self.logger.info('Frame Devide finished.')
        self.params['frames'] = frames
        self.params['timestamps'] = timestamps
        self.screen_manager.get_screen('replay_exe').detect_process(self.params)
        
    def export_process(self, params):
        self.params = params
        self.screen_manager.show_screen('log')
        self.worker = ExportWorker(params)
        self.worker.finished.connect(self.export_finished)
        self.worker.start()
        self.logger.info('Export started.')
        
    def export_finished(self):
        self.logger.info('Export finished.')
        self.screen_manager.show_screen('menu')
        self.screen_manager.resie_defualt()
        self.screen_manager.center()
