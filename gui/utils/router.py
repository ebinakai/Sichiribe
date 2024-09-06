from PySide6.QtWidgets import QStackedWidget, QMainWindow
from gui.utils.screen_manager import ScreenManager
from gui.views.menu_view import MenuWindow
from gui.views.log_view import LogWindow
from gui.views.region_select_view import RegionSelectWindow
from gui.views.replay_setting_view import ReplaySettingsWindow
from gui.views.replay_exe_view import ReplayExeWindow
from gui.views.live_setting_view import LiveSettingsWindow
from gui.views.live_feed_view import LiveFeedWindow
from gui.views.live_exe_view import LiveExeWindow
from gui.views.finish_view import FinishWindow
        
def init_screen_manager(stacked_widget: QStackedWidget, main_window: QMainWindow) -> ScreenManager:
  
    screen_manager = ScreenManager(stacked_widget, main_window)

    # ビュークラスをインスタンス化
    menu_window = MenuWindow(screen_manager)
    log_window = LogWindow(screen_manager)
    region_select_window = RegionSelectWindow(screen_manager)
    replay_setting_window = ReplaySettingsWindow(screen_manager)
    replay_exe_window = ReplayExeWindow(screen_manager)
    live_setting_window = LiveSettingsWindow(screen_manager)
    live_feed_window = LiveFeedWindow(screen_manager)
    live_exe_window = LiveExeWindow(screen_manager)
    finish_window = FinishWindow(screen_manager)
    
    # ビューをスタックウィジェットに追加
    stacked_widget.addWidget(menu_window)
    stacked_widget.addWidget(log_window)
    stacked_widget.addWidget(region_select_window)
    stacked_widget.addWidget(replay_setting_window)
    stacked_widget.addWidget(replay_exe_window)
    stacked_widget.addWidget(live_setting_window)
    stacked_widget.addWidget(live_feed_window)
    stacked_widget.addWidget(live_exe_window)
    stacked_widget.addWidget(finish_window)
    
    return screen_manager
