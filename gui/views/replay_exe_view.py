"""動画ファイル解析の実行画面"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from gui.widgets.custom_qwidget import CustomQWidget
from gui.utils.screen_manager import ScreenManager
from gui.utils.common import convert_cv_to_qimage
from gui.utils.exporter import export_result, export_settings
from gui.widgets.mpl_canvas_widget import MplCanvas
from gui.workers.replay_detect_worker import DetectWorker
from cores.frame_editor import FrameEditor
from cores.settings_manager import SettingsManager
import logging
from typing import List
import numpy as np


class ReplayExeWindow(CustomQWidget):
    """
    動画ファイル解析を行うViewクラス

    - 実際のフレーム分割・推論処理はDetectWorkerクラスで行う
    - 以下の処理を行う
        1. 最初のフレームを7セグ領域切り取り画面に渡す
        2. 7セグ領域切り取り画面からのパラメータを受け取り、フレーム分割を行う
        3. 分割フレームを受け取り、解析を行う
        4. 結果を MplCanvas のグラフに表示する
        5. 結果をファイルに出力する
    """

    def __init__(self, screen_manager: ScreenManager) -> None:
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.settings_manager = SettingsManager("replay")
        self.screen_manager = screen_manager
        self.results: List[int]
        self.failed_rates: List[float]
        self.graph_results: List[int]
        self.graph_failed_rates: List[float]
        self.graph_timestamps: List[str]

        super().__init__()
        screen_manager.add_screen("replay_exe", self, "動画解析中")

    def initUI(self):
        """UIの初期化"""
        main_layout = QVBoxLayout()
        graph_layout = QVBoxLayout()
        extracted_image_layout = QHBoxLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)

        graph_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        extracted_image_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.graph_label = MplCanvas()
        graph_layout.addWidget(self.graph_label)

        self.extracted_label = QLabel()
        self.extracted_label.setMinimumHeight(100)
        extracted_image_layout.addWidget(self.extracted_label)

        self.term_button = QPushButton("中止")
        self.term_button.setFixedWidth(100)
        self.term_button.clicked.connect(self.cancel)
        footer_layout.addWidget(self.term_button)

        self.term_label = QLabel()
        self.term_label.setStyleSheet("color: red")
        footer_layout.addWidget(self.term_label)

        footer_layout.addStretch()

        main_layout.addLayout(graph_layout)
        main_layout.addLayout(extracted_image_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer_layout)

    def cancel(self) -> None:
        """解析中止処理

        ボタンのクリックで解析を中止する
        """
        if self.dt_worker is not None:
            self.term_label.setText("中止中...")
            self.dt_worker.cancel()

    def trigger(self, action, *args):
        """アクションをトリガーする

        Args:
            action (str): アクション名

        Raises:
            ValueError: アクションが不正な場合
        """
        if action == "startup":
            self.startup(*args)
        elif action == "continue":
            self.detect_start()
        else:
            raise ValueError(f"Invalid action: {action}")

    def startup(self) -> None:
        """各種初期化処理を行う

        動画ファイルから最初のフレームを取得し、7セグメント領域切り取り画面に渡す
        """
        self.graph_label.gen_graph(
            title="Results",
            xlabel="Timestamp",
            ylabel1="Failed Rate",
            ylabel2="Detected results",
            dark_theme=self.screen_manager.check_if_dark_mode(),
        )
        self.term_label.setText("")
        self.results = []
        self.failed_rates = []
        self.graph_results = []
        self.graph_failed_rates = []
        self.graph_timestamps = []

        # 最初のフレームを取得
        self.fe = FrameEditor(self.data_store.get("num_digits"))
        gen = self.fe.frame_devide_generator(
            video_path=self.data_store.get("video_path"),
            video_skip_sec=self.data_store.get("video_skip_sec"),
            is_crop=False,
            extract_single_frame=True,
        )
        frame, _ = next(gen)
        gen.close()
        self.data_store.set("first_frame", frame)

        if (
            self.data_store.has("click_points")
            and len(self.data_store.get("click_points")) == 4
        ):
            self.screen_manager.get_screen("replay_threshold").trigger("startup")
        else:
            self.screen_manager.get_screen("region_select").trigger(
                "startup", "replay_exe"
            )

    def detect_start(self) -> None:
        """フレーム分割処理完了時の処理

        解析処理を開始する

        Args:
            frames (List[Union[str, np.ndarray]]): 分割されたフレームまたはそのパスのリスト
            timestamps (List[str]): タイムスタンプのリスト
        """

        self.screen_manager.show_screen("replay_exe")

        self.dt_worker = DetectWorker()
        self.dt_worker.progress.connect(self.detect_progress)
        self.dt_worker.send_image.connect(self.display_extract_image)
        self.dt_worker.finished.connect(self.detect_finished)
        self.dt_worker.cancelled.connect(self.detect_cancelled)
        self.dt_worker.model_not_found.connect(self.model_not_found)
        self.dt_worker.start()
        self.logger.info("Detect started.")

    def model_not_found(self) -> None:
        """モデルが見つからなかった場合の処理

        ワーカーからのシグナルを受け取り、メニュー画面に戻る
        """
        self.logger.error("Model not found.")
        self.screen_manager.show_screen("menu")
        self.clear_env()

    def detect_progress(self, result: int, failed_rate: float, timestamp: str) -> None:
        """解析進捗を受け取る

        ワーカーからのシグナルを受け取り、結果をグラフに表示する

        Args:
            result (int): 解析結果
            failed_rate (float): 失敗率
            timestamp (str): タイムスタンプ
        """
        self.results.append(result)
        self.failed_rates.append(failed_rate)
        self.update_graph(result, failed_rate, timestamp)

    def update_graph(self, result: int, failed_rate: float, timestamp: str) -> None:
        """グラフを更新する

        Args:
            result (int): 解析結果
            failed_rate (float): 失敗率
            timestamp (str): タイムスタンプ
        """
        self.graph_results.append(result)
        self.graph_failed_rates.append(failed_rate)
        self.graph_timestamps.append(timestamp)
        self.graph_label.update_existing_plot(
            self.graph_timestamps, self.graph_failed_rates, self.graph_results
        )

    def display_extract_image(self, image: np.ndarray) -> None:
        """切り出し画像を表示する

        推論時の2値化しきい値を適用した7セグメント領域を表示する
        """
        image = self.fe.draw_separation_lines(image)
        q_image = convert_cv_to_qimage(image)
        self.extracted_label.setPixmap(QPixmap.fromImage(q_image))

    def detect_cancelled(self) -> None:
        """解析中止時の処理

        ワーカーからのシグナルを受け取り、タイムスタンプを推論結果の数に合わせる
        """
        self.term_label.setText("中止しました")
        self.logger.info("Detect cancelled.")
        self.data_store.set(
            "timestamps", self.data_store.get("timestamps")[: len(self.results)]
        )

    def detect_finished(self) -> None:
        """解析完了時の処理

        ワーカーからのシグナルを受け取り、結果を保存し、環境をクリアする
        """
        self.graph_label.clear()
        self.logger.info("Detect finished.")
        self.logger.info(f"Results: {self.results}")
        self.data_store.set("results", self.results)
        self.data_store.set("failed_rates", self.failed_rates)
        self.export()
        self.screen_manager.show_screen("menu")
        self.clear_env()

    def export(self) -> None:
        """解析結果をファイルに出力する

        解析結果をファイルに出力し、保存場所を表示する
        使用したパラメータも出力する
        """
        self.logger.info("Data exporting...")
        export_result(self.data_store.get_all())
        export_settings(self.data_store.get_all())
        self.screen_manager.popup(f"保存場所：{self.data_store.get('out_dir')}")

    def clear_env(self) -> None:
        """環境をクリアする"""
        self.graph_label.clear()
        self.extracted_label.clear()
        self.term_label.setText("")
        self.logger.info("Environment cleared.")
        self.screen_manager.restore_screen_size()
