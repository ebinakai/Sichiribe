from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap
from gui.widgets.custom_qwidget import CustomQWidget
from gui.utils.screen_manager import ScreenManager
from gui.utils.common import convert_cv_to_qimage, resize_image
from gui.workers.live_feed_worker import LiveFeedWorker
import logging
from typing import List
import numpy as np


class LiveFeedWindow(CustomQWidget):
    """カメラの画角を確認するカメラフィード画面を表示するViewクラス

    1. カメラフィードを表示
    2. 戻るボタンを押すと、カメラフィードを停止し、前の画面に戻る
    3. 次へボタンを押すと、カメラフィードを停止し、7セグメント領域選択画面に遷移する
    """

    def __init__(self, screen_manager: ScreenManager) -> None:
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.screen_manager = screen_manager
        self.results: List[int]
        self.failed_rates: List[float]

        super().__init__()
        screen_manager.add_screen("live_feed", self, "カメラフィード")

    def initUI(self):
        """UIの初期化"""
        main_layout = QVBoxLayout()
        header_layout = QVBoxLayout()
        feed_layout = QVBoxLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)

        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feed_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.header_description = QLabel("画角を調整してください")
        header_layout.addWidget(self.header_description)

        self.feed_label = QLabel()
        feed_layout.addWidget(self.feed_label)

        self.back_button = QPushButton("戻る")
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self.back)

        self.next_button = QPushButton("次へ")
        self.next_button.setFixedWidth(100)
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)
        self.next_button.clicked.connect(self.next)

        footer_layout.addWidget(self.back_button)
        footer_layout.addStretch()
        footer_layout.addWidget(self.next_button)

        main_layout.addLayout(header_layout)
        main_layout.addStretch()
        main_layout.addLayout(feed_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)

    def trigger(self, action, *args):
        """アクションをトリガーする

        Args:
            action (str): アクション名
            args: その他の引数
        """
        if action == "startup":
            self.startup()
        else:
            raise ValueError(f"Invalid action: {action}")

    def back(self) -> None:
        """戻るボタンがクリックされたときの処理"""
        self.logger.debug("Back button clicked.")
        if self.worker is not None:
            self.worker.cancel()

    def next(self) -> None:
        """次へボタンがクリックされたときの処理"""
        self.logger.debug("Next button clicked.")
        if self.worker is not None:
            self.worker.stop()  # ワーカーに停止を指示

    def startup(self) -> None:
        """カメラフィードを開始する"""
        self.logger.info("Starting LiveFeedWindow.")
        self.feed_label.setText("読込中...")
        self.screen_manager.show_screen("live_feed")
        self.logger.info("Capture Feed starting...")

        # 初期化
        self.results = []
        self.failed_rates = []
        p_, s_ = self.screen_manager.save_screen_size()

        # 表示画像サイズを計算 (できるだけ小さな画像で処理)
        window_rect = self.geometry()
        self.target_width = window_rect.width() * 0.8
        self.target_height = window_rect.height() * 0.8
        self.logger.debug(
            "window width: %d window height: %d"
            % (window_rect.width(), window_rect.height())
        )

        self.worker = LiveFeedWorker(self.target_width, self.target_height)
        self.worker.cap_size.connect(self.recieve_cap_size)
        self.worker.progress.connect(self.show_feed)
        self.worker.end.connect(self.feed_finished)
        self.worker.cancelled.connect(self.feed_cancelled)
        self.worker.error.connect(self.feed_error)
        self.worker.start()
        self.logger.info("Feed started.")

    def recieve_cap_size(self, cap_size: List[int]) -> None:
        """ワーカーからキャプチャサイズを受け取る"""
        self.data_store.set("cap_size", cap_size)
        self.logger.debug("Capture size: %d x %d" % (cap_size[0], cap_size[1]))

    def show_feed(self, frame: np.ndarray) -> None:
        """フィードをラベルに表示する"""
        frame, _ = resize_image(frame, self.target_width, self.target_height)
        qimage = convert_cv_to_qimage(frame)
        self.feed_label.setPixmap(QPixmap(qimage))

    def feed_finished(self, first_frame: np.ndarray) -> None:
        """フィードが終了したときの処理"""
        self.logger.info("Feed finished.")
        self.data_store.set("first_frame", first_frame)
        self.clear_env()
        QTimer.singleShot(
            10,
            lambda: self.screen_manager.get_screen("region_select").trigger(
                "startup", "live_feed"
            ),
        )

    def feed_cancelled(self) -> None:
        """フィードがキャンセルされたときの処理"""
        self.clear_env()
        QTimer.singleShot(1, lambda: self.screen_manager.show_screen("live_setting"))
        self.logger.info("Feed cancelled.")

    def feed_error(self) -> None:
        """フィードでエラーが発生したときの処理

        設定画面に戻る
        """
        self.clear_env()
        self.screen_manager.popup("カメラにアクセスできませんでした")
        QTimer.singleShot(1, lambda: self.screen_manager.show_screen("live_setting"))
        self.logger.error("Feed missing frame.")

    def clear_env(self) -> None:
        """環境をクリアする"""
        self.feed_label.clear()
        self.logger.info("Environment cleared.")
        self.screen_manager.restore_screen_size()
