"""
動画ファイル解析のための二値化しきい値を設定するViewクラス

1. 初期値は大津の二値化を適用した画像を表示
2. スライダーでしきい値を設定し、画像を更新する
3. 次へボタンを押すと、しきい値をパラメータに保存し、次の画面に遷移する
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QLabel,
    QSlider,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from gui.widgets.custom_qwidget import CustomQWidget
from gui.utils.screen_manager import ScreenManager
from gui.utils.data_store import DataStore
from gui.utils.common import convert_cv_to_qimage
from cores.frame_editor import FrameEditor
from cores.cnn import CNNCore as Detector
import logging
from typing import Optional
import numpy as np


class ReplayThresholdWindow(CustomQWidget):
    def __init__(self, screen_manager: ScreenManager) -> None:
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.screen_manager = screen_manager
        self.data_store = DataStore.get_instance()
        self.threshold: Optional[int]
        self.fe = FrameEditor()
        self.dt = Detector(4)
        self.first_frame: Optional[np.ndarray] = None

        super().__init__()
        screen_manager.add_screen("replay_threshold", self, "二値化しきい値設定")

    def initUI(self):
        main_layout = QVBoxLayout()
        extracted_image_layout = QHBoxLayout()
        form_layout = QFormLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)

        extracted_image_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.extracted_label = QLabel()
        self.extracted_label.setMinimumHeight(100)
        extracted_image_layout.addWidget(self.extracted_label)

        slider_layout = QHBoxLayout()
        self.binarize_th = QSlider()
        self.binarize_th.setValue(0)
        self.binarize_th.setFixedWidth(200)
        self.binarize_th.setRange(0, 255)
        self.binarize_th.setOrientation(Qt.Orientation.Horizontal)
        self.binarize_th.valueChanged.connect(self.update_binarize_th)
        self.binarize_th_label = QLabel()
        self.binarize_th_label.setText("自動設定")
        slider_layout.addWidget(self.binarize_th)
        slider_layout.addWidget(self.binarize_th_label)
        form_layout.addRow("画像二値化しきい値：", slider_layout)

        self.next_button = QPushButton("次へ")
        self.next_button.setFixedWidth(100)
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)
        self.next_button.clicked.connect(self.next)

        footer_layout.addStretch()
        footer_layout.addWidget(self.next_button)

        main_layout.addStretch()
        main_layout.addLayout(extracted_image_layout)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)

    def trigger(self, action, *args):
        if action == "startup":
            self.startup()
        else:
            raise ValueError("Invalid action.")

    def startup(self) -> None:
        self.screen_manager.show_screen("replay_threshold")
        self.data_store.get_all()

        _p, _s = self.screen_manager.save_screen_size()

        self.threshold = None
        self.first_frame = self.fe.crop(
            self.data_store.get("first_frame"), self.data_store.get("click_points")
        )
        self.update_binarize_th(0)

    def update_binarize_th(self, value: int) -> None:
        self.threshold = None if value == 0 else value
        binarize_th_str = "自動設定" if self.threshold is None else str(self.threshold)
        self.binarize_th_label.setText(binarize_th_str)

        if self.first_frame is None:
            self.logger.error("Frame lost.")
            self.clear_env()
            self.screen_manager.restore_screen_size()
            self.screen_manager.show_screen("menu")
            return

        image_bin = self.dt.preprocess_binarization(self.first_frame, self.threshold)
        self.display_extract_image(image_bin)

    def display_extract_image(self, image: np.ndarray) -> None:
        q_image = convert_cv_to_qimage(image)
        self.extracted_label.setPixmap(QPixmap.fromImage(q_image))

    def next(self) -> None:
        self.logger.info("Set threshold finished.")
        self.data_store.set("threshold", self.threshold)
        self.clear_env()
        self.screen_manager.get_screen("replay_exe").trigger("continue")

    def clear_env(self) -> None:
        self.extracted_label.clear()
        self.binarize_th.setValue(0)
        self.logger.info("Environment cleared.")
        self.screen_manager.restore_screen_size()
