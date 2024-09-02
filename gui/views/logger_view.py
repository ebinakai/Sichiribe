from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
import logging

class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        log_entry = self.format(record)
        self.text_edit.append(log_entry)
  
class LogWindow(QWidget):
    def __init__(self, screen_manager):
        super().__init__()

        self.screen_manager = screen_manager
        screen_manager.add_screen('log', self)
        
        self.setWindowTitle('Log viewer')
        self.setGeometry(100, 100, 600, 400)
        
        # レイアウトと QTextEdit ウィジェットを設定
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        
        # ログの出力先をログウィンドウに設定
        self.logger = logging.getLogger('__main__')
        log_handler = QTextEditLogger(self.log_display)
        self.logger.addHandler(log_handler)
    
    def append_log(self, message):
        self.log_display.append(message)