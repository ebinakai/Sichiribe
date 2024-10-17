'''
画面の管理を行うクラス

1. 画面遷移を行う
2. 画面サイズの保存、復元を行う
3. ポップアップメッセージボックスの表示を行う
'''

from PySide6.QtWidgets import QApplication, QStackedWidget, QWidget, QMainWindow, QMessageBox
from PySide6.QtGui import QPalette
from PySide6.QtCore import QEventLoop, QTimer
import logging

class ScreenManager:
    def __init__(self, stacked_widget: QStackedWidget, main_window: QMainWindow):
        self.stacked_widget = stacked_widget
        self.main_window = main_window
        self.logger = logging.getLogger('__main__').getChild(__name__)
        self.screens = {}
    
    def add_screen(self, name, widget: QWidget):
        self.screens[name] = widget
        self.stacked_widget.addWidget(widget)
    
    def show_screen(self, name):
        if name in self.screens:
            self.stacked_widget.setCurrentWidget(self.screens[name])
            self.main_window.setFocus()
        else:
            self.logger.error(f"Screen '{name}' not found")
            
    def get_screen(self, name) -> QWidget:
        if name in self.screens:
            return self.screens[name]
        else:
            self.logger.error(f"Screen '{name}' not found")
            return None

    def check_if_dark_mode(self):
        palette = QApplication.palette()
        return palette.color(QPalette.ColorRole.Window).value() < 128

    def resie_defualt(self):
        self.main_window.resize(640, 480)

    def center(self):
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        window_rect = self.main_window.frameGeometry()
        
        x = (screen_rect.width() - window_rect.width()) // 2
        y = (screen_rect.height() - window_rect.height()) // 2
        
        self.main_window.move(x, y)
        
    def quit(self):
        self.logger.info("Quitting application")
        QApplication.quit()

    def save_screen_size(self):
        self.window_pos = self.main_window.frameGeometry().topLeft()
        self.window_size = self.main_window.size()
        return self.window_pos, self.window_size
    
    def restore_screen_size(self):
        QApplication.processEvents()
        if self.window_pos is not None and self.window_size is not None:
            self.logger.info("Screen geometry restoring...")
            
            # 現在の画面内のオブジェクトが処理を終えるまで10ms待つ
            loop = QEventLoop()
            QTimer.singleShot(10, loop.quit)
            loop.exec_()
            
            self.main_window.move(self.window_pos)
            self.main_window.resize(self.window_size)
            self.window_pos = None
            self.window_size = None
            
        else: 
            self.logger.error("No screen size saved")

    def popup(self, message: str, is_modal=False):
        self.logger.debug("Popup message: %s" % message)
        
        msg_box = QMessageBox(self.main_window)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # 同期処理または非同期処理
        if is_modal:
            msg_box.exec()
        else:
            msg_box.show()
