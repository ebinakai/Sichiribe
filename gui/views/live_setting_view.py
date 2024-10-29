"""
リアルタイム解析の設定を行うViewクラス

1. 以下を設定する
    - カメラID
    - 7セグメント表示器の桁数
    - 動画をサンプリングする頻度
    - 一回のサンプリングで何フレーム取得するか
    - 総サンプリング時間
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
from cores.exporter import get_supported_formats, Exporter
from cores.common import (
    get_now_str,
    load_setting,
    validate_output_directory,
    validate_params,
    filter_dict,
)
import logging
from pathlib import Path


class LiveSettingWindow(CustomQWidget):
    def __init__(self, screen_manager: ScreenManager) -> None:
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.ep = Exporter(get_user_data_dir())
        self.screen_manager = screen_manager
        self.data_store = DataStore.get_instance()
        self.required_keys = {
            "device_num": lambda x: isinstance(x, int) and x >= 0,
            "num_digits": lambda x: isinstance(x, int) and x >= 1,
            "sampling_sec": lambda x: isinstance(x, int) and x >= 1,
            "num_frames": lambda x: isinstance(x, int) and x >= 1,
            "total_sampling_sec": lambda x: isinstance(x, int) and x >= 1,
            "format": lambda x: x in get_supported_formats(),
            "save_frame": lambda x: isinstance(x, bool),
            "out_dir": lambda x: validate_output_directory(Path(x).parent),
        }

        super().__init__()
        screen_manager.add_screen("live_setting", self, "ライブ解析設定")

    def initUI(self):
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        footer_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.device_num = QSpinBox()
        self.device_num.setValue(0)
        self.device_num.setFixedWidth(50)
        form_layout.addRow("カメラID：", self.device_num)

        self.num_digits = QSpinBox()
        self.num_digits.setValue(4)
        self.num_digits.setFixedWidth(50)
        self.num_digits.setMinimum(1)
        form_layout.addRow("7セグ表示機の桁数：", self.num_digits)

        self.sampling_sec = QSpinBox()
        self.sampling_sec.setValue(10)
        self.sampling_sec.setFixedWidth(50)
        self.sampling_sec.setMinimum(3)
        self.sampling_sec.valueChanged.connect(self.calc_max_frames)
        form_layout.addRow("動画をサンプリングする頻度(秒)：", self.sampling_sec)

        self.num_frames = QSpinBox()
        self.num_frames.setValue(10)
        self.num_frames.setFixedWidth(50)
        self.num_frames.setMinimum(1)
        self.num_frames.setMaximum(60)
        form_layout.addRow("取得するフレーム数 / サンプリング：", self.num_frames)

        self.total_sampling_min = QSpinBox()
        self.total_sampling_min.setValue(1)
        self.total_sampling_min.setFixedWidth(50)
        self.total_sampling_min.setMinimum(1)
        self.total_sampling_min.setMaximum(600)
        form_layout.addRow("総サンプリング時間(分)：", self.total_sampling_min)

        self.format = QComboBox()
        for fmt in get_supported_formats():
            self.format.addItem(fmt)
        form_layout.addRow("出力フォーマット：", self.format)

        self.save_frame = QCheckBox()
        form_layout.addRow("フレームを保存する：", self.save_frame)

        self.out_dir = QLineEdit()
        self.out_dir.setReadOnly(True)
        self.out_dir_button = QPushButton("フォルダ選択")
        self.out_dir_button.clicked.connect(self.select_folder)
        file_layout = QVBoxLayout()
        file_layout.addWidget(self.out_dir)
        file_layout.addWidget(self.out_dir_button)
        form_layout.addRow("保存場所：", file_layout)

        self.back_button = QPushButton("戻る")
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(
            lambda: self.screen_manager.show_screen("menu")
        )
        footer_layout.addWidget(self.back_button)

        footer_layout.addStretch()  # スペーサー

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
        default_setting_path = Path(get_user_data_dir()) / "setting_live.json"
        try:
            params = load_setting(str(default_setting_path), self.required_keys.keys())
            if validate_params(params, self.required_keys):
                self.data_store.set_all(params)
                self.set_ui_from_params()
        except Exception:
            self.logger.info(f"Failed to load default setting file")

    def select_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "フォルダを選択", "")

        if folder_path:
            self.out_dir.setText(folder_path)

    def calc_max_frames(self) -> None:
        sampling_sec = self.sampling_sec.value()
        self.num_frames.setMaximum(sampling_sec * 5)

    def load_setting(self) -> None:
        self.confirm_txt.setText("")
        folder_path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを選択", "", "設定ファイル(*.json)"
        )

        required_keys = set(self.required_keys.keys())
        required_keys.add("click_points")
        required_keys.add("cap_size")
        try:
            params = load_setting(folder_path, required_keys)
        except Exception:
            self.logger.info(f"Failed to read setting file")
            self.confirm_txt.setText("ファイルが読み込めませんでした")
            return

        self.export_setting()

        out_dir_parent = Path(params["out_dir"]).resolve().parent
        params["out_dir"] = str(out_dir_parent / get_now_str())
        if not validate_params(params, self.required_keys):
            self.logger.info(f"Invalid setting file")
            self.confirm_txt.setText("不正なファイルです")
            return

        self.data_store.set_all(params)
        self.set_ui_from_params()
        if len(params["click_points"]) == 4:
            self.screen_manager.get_screen("live_exe").trigger("startup")
        else:
            self.screen_manager.get_screen("live_feed").trigger("startup")

    def next(self) -> None:
        if self.out_dir.text() == "":
            self.confirm_txt.setText("保存場所を選択してください")
            return
        else:
            self.confirm_txt.setText("")

        self.get_params_from_ui()
        self.export_setting()

        self.data_store.set(
            "out_dir",
            str(Path(self.data_store.get("out_dir")).resolve() / get_now_str()),
        )
        if not validate_params(self.data_store.get_all(), self.required_keys):
            self.confirm_txt.setText("不正な値が入力されています")
            return

        self.screen_manager.get_screen("live_feed").trigger("startup")

    def export_setting(self) -> None:
        setting = self.data_store.get_all()
        setting = filter_dict(setting, lambda k, v: k in self.required_keys.keys())
        self.ep.export(
            setting,
            method="json",
            prefix="setting_live",
            with_timestamp=False,
        )

    def set_ui_from_params(self) -> None:
        self.device_num.setValue(self.data_store.get("device_num"))
        self.num_digits.setValue(self.data_store.get("num_digits"))
        self.sampling_sec.setValue(self.data_store.get("sampling_sec"))
        self.num_frames.setValue(self.data_store.get("num_frames"))
        self.total_sampling_min.setValue(
            self.data_store.get("total_sampling_sec") // 60
        )
        self.format.setCurrentText(self.data_store.get("format"))
        self.save_frame.setChecked(self.data_store.get("save_frame"))
        self.out_dir.setText(self.data_store.get("out_dir"))

    def get_params_from_ui(self):
        self.data_store.set("device_num", self.device_num.value())
        self.data_store.set("num_digits", self.num_digits.value())
        self.data_store.set("sampling_sec", self.sampling_sec.value())
        self.data_store.set("num_frames", self.num_frames.value())
        self.data_store.set("total_sampling_sec", self.total_sampling_min.value() * 60)
        self.data_store.set("format", self.format.currentText())
        self.data_store.set("save_frame", self.save_frame.isChecked())
        self.data_store.set("out_dir", self.out_dir.text())
