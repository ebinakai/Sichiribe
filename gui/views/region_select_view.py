"""解析する7セグメント領域の選択画面"""

import logging
from typing import List
import numpy as np
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import Qt, QSize, QTimer
from gui.widgets.custom_qwidget import CustomQWidget
from gui.utils.screen_manager import ScreenManager
from cores.frame_editor import FrameEditor
from gui.utils.common import convert_cv_to_qimage, resize_image
from gui.widgets.clickable_label import ClickableLabel


class RegionSelectWindow(CustomQWidget):
    """
    解析する7セグメント領域を選択する画面のViewクラス

    1. 4点を選択することで7セグメント領域を囲むことができる
    2. opencvの画像処理を行うため、FrameEditorクラスを利用する
    3. 選択が終わると次の画面に遷移する
    """

    def __init__(self, screen_manager: ScreenManager) -> None:
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.screen_manager = screen_manager
        self.click_points: List = []
        self.image_size: QSize

        super().__init__()
        screen_manager.add_screen("region_select", self, "7セグメント領域選択")

        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        self.target_width = int(screen_rect.width() * 0.8)
        self.target_height = int((screen_rect.height() - 100) * 0.8)

    def initUI(self):
        """UIの初期化"""
        main_layout = QVBoxLayout()
        header_layout = QVBoxLayout()
        image_layout = QVBoxLayout()
        extracted_image_layout = QHBoxLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)

        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        extracted_image_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.header_description = QLabel("7セグメント領域として4点を選択してください")
        header_layout.addWidget(self.header_description)

        self.main_label = ClickableLabel(self, self.label_clicked)
        # サイズポリシーを設定して、ラベルが画像サイズに合わせて変わるようにする
        self.main_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        image_layout.addWidget(self.main_label)

        self.extracted_label = QLabel()
        self.extracted_label.setMinimumHeight(100)
        extracted_image_layout.addWidget(self.extracted_label)

        self.back_button = QPushButton("戻る")
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self.cancel_select)
        footer_layout.addWidget(self.back_button)

        footer_layout.addStretch()

        footer_right_layout = QHBoxLayout()
        self.confirm_txt = QLabel()
        self.confirm_txt.setStyleSheet("color: red")
        footer_right_layout.addWidget(self.confirm_txt)
        self.next_button = QPushButton("次へ")
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)
        self.next_button.setFixedWidth(100)
        self.next_button.clicked.connect(self.finish_select)
        footer_right_layout.addWidget(self.next_button)

        footer_layout.addLayout(footer_right_layout)

        main_layout.addLayout(header_layout)
        main_layout.addLayout(image_layout)
        main_layout.addLayout(extracted_image_layout)
        main_layout.addLayout(footer_layout)

    def trigger(self, action, *args) -> None:
        """アクションをトリガーする

        Args:
            action (str): アクション名

        Raises:
            ValueError: アクションが不正な場合
        """
        if action == "startup":
            self.startup(*args)
        else:
            raise ValueError(f"Invalid action: {action}")

    def set_image(self, image: np.ndarray) -> None:
        """領域選択用の画像を設定する

        画像を画面サイズに合わせてリサイズする

        Args:
            image (np.ndarray): 領域選択用の画像
        """
        self.image_original = image
        self.image, self.resize_scale = resize_image(
            image, self.target_width, self.target_height
        )

        height, width, channel = self.image.shape
        self.image_size = QSize(width, height)

        self.update_image(self.image.copy())

    def label_clicked(self, event: QMouseEvent) -> None:
        """ラベルがクリックされたときの処理

        マウスイベントからクリックされた座標を取得し、クリックポイントを更新する
        """
        if (
            event.button() == Qt.MouseButton.LeftButton
            or event.button() == Qt.MouseButton.NoButton
            and len(self.click_points) == 4
        ):

            # QLabel内の座標を取得
            label_pos = event.position().toPoint()

            if (
                label_pos.x() <= 0
                or label_pos.x() >= self.image_size.width()
                or label_pos.y() <= 0
                or label_pos.y() >= self.image_size.height()
            ):
                return

            new_point = np.array([label_pos.x(), label_pos.y()]).astype(np.int32)

            if len(self.click_points) < 4:
                self.click_points.append(new_point)
            else:
                # 最も近い点を入れ替える
                distances = np.linalg.norm(
                    np.array(self.click_points) - new_point, axis=1
                )
                closest_index = np.argmin(distances)
                self.click_points[closest_index] = new_point

            if len(self.click_points) == 4:
                self.click_points = self.fe.order_points(self.click_points)

            self.update_image(self.image.copy())

    def display_image(self, image: np.ndarray) -> None:
        """画像をラベルに表示する

        Args:
            image (np.ndarray): 表示する画像
        """
        q_image = convert_cv_to_qimage(image)
        self.main_label.setPixmap(QPixmap.fromImage(q_image))
        self.main_label.adjustSize()

    def display_extract_image(self, image: np.ndarray) -> None:
        """切り取った画像をラベルに表示する

        Args:
            image (np.ndarray): 表示する画像
        """
        q_image = convert_cv_to_qimage(image)
        self.extracted_label.setPixmap(QPixmap.fromImage(q_image))

    def update_image(self, image: np.ndarray) -> None:
        """画像を更新する

        1. 選択領域を切り出す
        2. クリックポイントを描画して表示する
        3. 切り取った画像を表示する
        """
        click_points = np.array(self.click_points) / self.resize_scale
        extract_image = self.fe.crop(self.image_original, click_points.tolist())
        image, extract_image = self.fe.draw_region_outline(
            image, extract_image, self.click_points
        )
        self.display_image(image)

        if extract_image is not None:
            self.display_extract_image(extract_image)

    def startup(self, prev_screen: str) -> None:
        """画面を起動する

        Args:
            prev_screen (str): 前の画面名
        """
        self.logger.info("Starting RegionSelectWindow.")
        self.prev_screen = prev_screen
        self.fe = FrameEditor(num_digits=self.data_store.get("num_digits"))

        window_pos, _ = self.screen_manager.save_screen_size()

        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        self.target_width = int(screen_rect.width() * 0.8)
        self.target_height = int((screen_rect.height() - 100) * 0.8)

        self.set_image(self.data_store.get("first_frame"))
        self.screen_manager.show_screen("region_select")
        QTimer.singleShot(1, lambda: self.window().move(window_pos.x(), 1))

    def finish_select(self) -> None:
        """選択を終了して次の画面に遷移する"""
        if len(self.click_points) != 4:
            self.confirm_txt.setText("7セグメント領域を囲ってください")
            return

        self.logger.info("Region selection finished.")
        click_points = np.array(self.click_points) / self.resize_scale
        self.data_store.set("click_points", click_points.tolist())

        self.clear_env()

        # ウィンドウサイズの適用を待ってから次の画面に遷移
        QTimer.singleShot(1, self.switch_next)

    def cancel_select(self) -> None:
        """選択をキャンセルして前の画面に戻る"""
        self.logger.info("Region selection canceled.")
        self.clear_env()
        QTimer.singleShot(1, lambda: self.switch_back())

    def switch_back(self) -> None:
        """前の画面に戻る

        Raises:
            ValueError: 前の画面が不正な場合
        """
        self.logger.debug(f"Switching to back screen({self.prev_screen}).")
        if self.prev_screen == "replay_exe":
            self.screen_manager.show_screen("replay_setting")
        elif self.prev_screen == "live_feed":
            self.screen_manager.get_screen("live_feed").trigger("startup")
        else:
            raise ValueError("Invalid previous screen.")
        self.prev_screen = ""

    def switch_next(self) -> None:
        """次の画面に遷移する

        Raises:
            ValueError: 次の画面が不正な場合
        """
        self.logger.debug(f"Switching to next screen({self.prev_screen}).")
        if self.prev_screen == "replay_exe":
            self.screen_manager.get_screen("replay_threshold").trigger("startup")
        elif self.prev_screen == "live_feed":
            self.screen_manager.get_screen("live_exe").trigger("startup")
        else:
            raise ValueError("Invalid previous screen.")
        self.prev_screen = ""

    def clear_env(self) -> None:
        """環境をクリアする"""
        self.main_label.clear()
        self.extracted_label.clear()
        self.click_points = []
        self.confirm_txt.setText("")
        self.screen_manager.restore_screen_size()
        self.logger.info("Environment cleared.")
