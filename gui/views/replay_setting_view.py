"""
動画ファイル解析の設定を行うViewクラス

1. 以下を設定する
    - 解析する動画のパス
    - 7セグメント表示器の桁数
    - 動画をサンプリングする頻度
    - 一回のサンプリングで何フレーム取得するか
    - 動画の解析を始めるタイミング
    - 出力形式
    - キャプチャしたフレームを保存するか
2. 実行ボタンを押すと、次の画面に遷移する
3. 構成ファイルから実行ボタンを押すと、設定ファイルからパラメータを読み込んで実行する
    - 構成ファイルとして、設定ファイル(*.json)を指定する
    - 構成ファイルの click_points に 4 つの座標が含まれている場合、カメラフィードと領域選択画面をスキップして実行する
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QFileDialog,
    QLabel,
)
from gui.widgets.custom_qwidget import CustomQWidget
from gui.utils.screen_manager import ScreenManager
from gui.utils.data_store import DataStore
from gui.utils.common import get_user_data_dir
from cores.exporter import Exporter
from cores.common import (
    get_now_str,
    load_setting,
    validate_output_directory,
    validate_params,
)
from cores.exporter import get_supported_formats
import logging
from pathlib import Path


class ReplaySettingWindow(CustomQWidget):
    def __init__(self, screen_manager: ScreenManager) -> None:
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.ep = Exporter(get_user_data_dir())
        self.screen_manager = screen_manager
        self.data_store = DataStore.get_instance()
        self.required_keys = {
            "video_path": lambda x: isinstance(x, str) and Path(x).exists(),
            "num_digits": lambda x: isinstance(x, int) and x >= 1,
            "sampling_sec": lambda x: isinstance(x, int) and x >= 1,
            "num_frames": lambda x: isinstance(x, int) and x >= 1,
            "video_skip_sec": lambda x: isinstance(x, int) and x >= 0,
            "format": lambda x: x in get_supported_formats(),
            "save_frame": lambda x: isinstance(x, bool),
            "out_dir": lambda x: validate_output_directory(Path(x).parent),
        }

        super().__init__()
        screen_manager.add_screen("replay_setting", self, "動画解析設定")

    def initUI(self):
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.video_path = QLineEdit()
        self.video_path.setReadOnly(True)
        self.video_path_button = QPushButton("ファイル選択")
        self.video_path_button.clicked.connect(self.select_file)
        file_layout = QVBoxLayout()
        file_layout.addWidget(self.video_path)
        file_layout.addWidget(self.video_path_button)
        form_layout.addRow("解析する動画のパス：", file_layout)

        self.num_digits = QSpinBox()
        self.num_digits.setValue(4)
        self.num_digits.setFixedWidth(50)
        self.num_digits.setMinimum(1)
        form_layout.addRow("7セグメント表示器の桁数：", self.num_digits)

        self.sampling_sec = QSpinBox()
        self.sampling_sec.setValue(5)
        self.sampling_sec.setFixedWidth(50)
        self.sampling_sec.setMinimum(1)
        form_layout.addRow("動画をサンプリングする頻度 (秒)：", self.sampling_sec)

        self.num_frames = QSpinBox()
        self.num_frames.setValue(30)
        self.num_frames.setFixedWidth(50)
        self.num_frames.setMinimum(1)
        form_layout.addRow(
            "一回のサンプリングで何フレーム取得するか：", self.num_frames
        )

        self.video_skip_sec = QSpinBox()
        self.video_skip_sec.setValue(0)
        self.video_skip_sec.setFixedWidth(50)
        form_layout.addRow("動画の解析を始めるタイミング (秒)：", self.video_skip_sec)

        self.format = QComboBox()
        for fmt in get_supported_formats():
            self.format.addItem(fmt)
        form_layout.addRow("出力フォーマット：", self.format)

        self.save_frame = QCheckBox()
        form_layout.addRow("キャプチャしたフレームを保存する：", self.save_frame)

        self.back_button = QPushButton("戻る")
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(
            lambda: self.screen_manager.show_screen("menu")
        )
        footer_layout.addWidget(self.back_button)

        footer_layout.addStretch()

        self.confirm_txt = QLabel()
        self.confirm_txt.setStyleSheet("color: red")
        footer_layout.addWidget(self.confirm_txt)

        self.load_button = QPushButton("構成ファイルから実行")
        self.load_button.clicked.connect(self.load_setting)
        footer_layout.addWidget(self.load_button)

        self.next_button = QPushButton("実行")
        self.next_button.setFixedWidth(100)
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)
        self.next_button.clicked.connect(self.next)
        footer_layout.addWidget(self.next_button)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(footer_layout)

    def display(self):
        default_setting_path = Path(get_user_data_dir()) / "setting_replay.json"
        try:
            params = load_setting(default_setting_path, self.required_keys.keys())
        except Exception:
            self.logger.info(f"Failed to load default setting file")

        if validate_params(params, self.required_keys):
            self.data_store.set_all(params)
            self.set_ui_from_params()

    def select_file(self) -> None:
        video_path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを選択", "", "動画ファイル (*.mp4 *.avi)"
        )
        if video_path:
            self.video_path.setText(video_path)

    def back(self) -> None:
        self.confirm_txt.setText("")
        self.screen_manager.show_screen("menu")

    def load_setting(self) -> None:
        self.confirm_txt.setText("")
        folder_path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを選択", "", "設定ファイル(*.json)"
        )

        required_keys = set(self.required_keys.keys())
        required_keys.add("click_points")

        try:
            params = load_setting(folder_path, required_keys)
        except Exception:
            self.logger.info(f"Failed to load setting file")
            self.confirm_txt.setText("ファイルが読み込めませんでした")
            return

        out_dir_parent = Path(params["out_dir"]).resolve().parent
        params["out_dir"] = str(out_dir_parent / get_now_str())
        if not validate_params(params, self.required_keys):
            self.logger.info(f"Invalid setting file")
            self.confirm_txt.setText("不正なファイルです")
            return

        self.data_store.set_all(params)
        self.set_ui_from_params()
        self.export_setting()
        self.screen_manager.get_screen("replay_exe").trigger("startup")

    def next(self) -> None:
        if self.video_path.text() == "":
            self.confirm_txt.setText("動画ファイルを選択してください")
            return
        else:
            self.confirm_txt.setText("")

        self.get_params_from_ui()
        self.data_store.set(
            "out_dir",
            str(Path(self.data_store.get("video_path")).parent / get_now_str()),
        )
        if not validate_params(self.data_store.get_all(), self.required_keys):
            self.confirm_txt.setText("不正な値が入力されています")
            return

        self.export_setting()
        self.screen_manager.get_screen("replay_exe").trigger("startup")

    def export_setting(self) -> None:
        self.ep.export(
            self.data_store.get_all(),
            method="json",
            prefix="setting_replay",
            with_timestamp=False,
        )

    def set_ui_from_params(self) -> None:
        self.video_path.setText(self.data_store.get("video_path"))
        self.num_digits.setValue(self.data_store.get("num_digits"))
        self.sampling_sec.setValue(self.data_store.get("sampling_sec"))
        self.num_frames.setValue(self.data_store.get("num_frames"))
        self.video_skip_sec.setValue(self.data_store.get("video_skip_sec"))
        self.format.setCurrentText(self.data_store.get("format"))
        self.save_frame.setChecked(self.data_store.get("save_frame"))

    def get_params_from_ui(self) -> None:
        self.data_store.set("video_path", self.video_path.text())
        self.data_store.set("num_digits", self.num_digits.value())
        self.data_store.set("sampling_sec", self.sampling_sec.value())
        self.data_store.set("num_frames", self.num_frames.value())
        self.data_store.set("video_skip_sec", self.video_skip_sec.value())
        self.data_store.set("format", self.format.currentText())
        self.data_store.set("save_frame", self.save_frame.isChecked())
        self.data_store.set("out_dir", self.video_path.text())
