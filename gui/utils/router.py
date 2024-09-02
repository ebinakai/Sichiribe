from PyQt6.QtWidgets import QApplication, QStackedWidget
from gui.views.menu_view import MenuWindow
from gui.views.logger_view import LogWindow
from gui.views.replay_setting_view import ReplaySettingsWindow
from gui.views.live_setting_view import LiveSettingsWindow

import logging

logger = logging.getLogger('__main__').getChild(__name__)

class ScreenManager:
    def __init__(self, stacked_widget):
        self.stacked_widget = stacked_widget
        self.screens = {}
    
    def add_screen(self, name, widget):
        self.screens[name] = widget
        self.stacked_widget.addWidget(widget)
    
    def show_screen(self, name):
        if name in self.screens:
            self.stacked_widget.setCurrentWidget(self.screens[name])
        else:
            logger.error(f"Screen '{name}' not found")
            
    def quit(self):
        logger.info("Quitting application")
        QApplication.quit()
        
def get_screen_manager(stacked_widget: QStackedWidget) -> ScreenManager:
  
    screen_manager = ScreenManager(stacked_widget)

    # ビュークラスをインスタンス化
    menu_window = MenuWindow(screen_manager)
    replay_setting_window = ReplaySettingsWindow(screen_manager)
    live_setting_window = LiveSettingsWindow(screen_manager)
    log_window = LogWindow(screen_manager)
    
    # ビューをスタックウィジェットに追加
    stacked_widget.addWidget(menu_window)
    stacked_widget.addWidget(log_window)
    stacked_widget.addWidget(replay_setting_window)
    stacked_widget.addWidget(live_setting_window)
    
    return ScreenManager(stacked_widget)