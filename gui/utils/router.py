"""GUIアプリケーションの画面構成の定義ファイル"""

from PySide6.QtWidgets import QStackedWidget, QMainWindow
from gui.utils.screen_manager import ScreenManager
from gui.views.menu_view import MenuWindow
from gui.views.log_view import LogWindow
from gui.views.region_select_view import RegionSelectWindow
from gui.views.replay_setting_view import ReplaySettingWindow
from gui.views.replay_exe_view import ReplayExeWindow
from gui.views.replay_threshold_view import ReplayThresholdWindow
from gui.views.live_setting_view import LiveSettingWindow
from gui.views.live_feed_view import LiveFeedWindow
from gui.views.live_exe_view import LiveExeWindow


def init_screen_manager(
    stacked_widget: QStackedWidget, main_window: QMainWindow
) -> ScreenManager:
    """
    新たなビュークラスを追加する場合は、ここに追記する

    Args:
        stacked_widget (QStackedWidget): 画面遷移を行うためのスタックウィジェット
        main_window (QMainWindow): stacked_widgetをセントラルウィジェットに設定するためのウィンドウ

    Returns:
        ScreenManager: 画面管理クラス
    """

    screen_manager = ScreenManager(stacked_widget, main_window)

    menu_window = MenuWindow(screen_manager)
    log_window = LogWindow(screen_manager)
    region_select_window = RegionSelectWindow(screen_manager)
    replay_setting_window = ReplaySettingWindow(screen_manager)
    replay_exe_window = ReplayExeWindow(screen_manager)
    replay_threshold_window = ReplayThresholdWindow(screen_manager)
    live_setting_window = LiveSettingWindow(screen_manager)
    live_feed_window = LiveFeedWindow(screen_manager)
    live_exe_window = LiveExeWindow(screen_manager)

    stacked_widget.addWidget(menu_window)
    stacked_widget.addWidget(log_window)
    stacked_widget.addWidget(region_select_window)
    stacked_widget.addWidget(replay_setting_window)
    stacked_widget.addWidget(replay_exe_window)
    stacked_widget.addWidget(replay_threshold_window)
    stacked_widget.addWidget(live_setting_window)
    stacked_widget.addWidget(live_feed_window)
    stacked_widget.addWidget(live_exe_window)

    return screen_manager
