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
from gui.widgets.setting_widget import SettingWidget
from gui.utils.screen_manager import ScreenManager
from cores.export_utils import get_supported_formats
from cores.common import get_now_str
from cores.settings_manager import SettingsManager
import logging
from pathlib import Path


class LiveSettingWindow(SettingWidget):
    """
    リアルタイム解析の設定を行うViewクラス

    以下を設定する
    
    - カメラID
    - 7セグメント表示器の桁数
    - 動画をサンプリングする頻度
    - 一回のサンプリングで何フレーム取得するか
    - 総サンプリング時間
    - 出力形式
    - キャプチャしたフレームを保存するか
    """

    def __init__(self, screen_manager: ScreenManager) -> None:
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.screen_manager = screen_manager
        self.settings_manager = SettingsManager("live")

        super().__init__()
        screen_manager.add_screen("live_setting", self, "ライブ解析設定")

    def initUI(self):
        """UIの初期化
        """
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

        self.batch_frames = QSpinBox()
        self.batch_frames.setValue(10)
        self.batch_frames.setFixedWidth(50)
        self.batch_frames.setMinimum(1)
        self.batch_frames.setMaximum(60)
        form_layout.addRow("取得するフレーム数 / サンプリング：", self.batch_frames)

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
        form_layout.addRow("フレームを保存：", self.save_frame)

        self.out_dir = QLineEdit()
        self.out_dir.setReadOnly(True)
        self.out_dir_button = QPushButton("フォルダ選択")
        self.out_dir_button.clicked.connect(self.select_folder)
        file_layout = QVBoxLayout()
        file_layout.addWidget(self.out_dir)
        file_layout.addWidget(self.out_dir_button)
        form_layout.addRow("保存場所：", file_layout)

        self.skip_region_select = QCheckBox()
        form_layout.addRow("領域選択をスキップ：", self.skip_region_select)

        self.back_button = QPushButton("戻る")
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self.back)
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
        self.next_button.setDefault(True)
        self.next_button.setAutoDefault(True)
        self.next_button.clicked.connect(self.next)
        footer_layout.addWidget(self.next_button)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(footer_layout)

    def display(self) -> None:
        """画面表示時の処理

        画面間共有データを取得し、UIに設定する
        """
        super().display()
        has_click_points = (
            self.data_store.has("click_points")
            and self.data_store.has("cap_size")
            and len(self.data_store.get("click_points")) == 4
            and len(self.data_store.get("cap_size")) == 2
        )
        self.skip_region_select.setEnabled(has_click_points)
        self.skip_region_select.setChecked(has_click_points)

    def select_folder(self) -> None:
        """保存場所を選択するダイアログを表示
        """
        folder_path = QFileDialog.getExistingDirectory(self, "フォルダを選択", "")

        if folder_path:
            self.out_dir.setText(folder_path)

    def calc_max_frames(self) -> None:
        """サンプリング頻度に応じて最大フレーム数を設定
        """
        sampling_sec = self.sampling_sec.value()
        self.batch_frames.setMaximum(sampling_sec * 5)

    def back(self) -> None:
        """戻るボタンがクリックされたときの処理
        """
        self.get_settings_from_ui()
        self.settings_manager.save(self.data_store.get_all())
        self.confirm_txt.setText("")
        self.screen_manager.show_screen("menu")

    def load_setting(self) -> None:
        
        """設定ファイルからパラメータを読み込んで実行する
        
        - 構成ファイルとして、設定ファイル(*.json)を指定する
        - 構成ファイルの click_points に 4 つの座標が含まれている場合、カメラフィードと領域選択画面をスキップして実行する
        """
        self.confirm_txt.setText("")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを選択", "", "設定ファイル(*.json)"
        )

        try:
            settings = self.settings_manager.load(file_path)
        except Exception:
            self.logger.info(f"Failed to read settings file")
            self.confirm_txt.setText("ファイルが読み込めませんでした")
            return

        out_dir_parent = Path(settings["out_dir"]).resolve().parent
        settings["out_dir"] = str(out_dir_parent / get_now_str())
        if not self.settings_manager.validate(settings):
            self.logger.info(f"Invalid settings file")
            self.confirm_txt.setText("不正なファイルです")
            return

        self.data_store.set_all(settings)
        self.save_settings()
        self.next_page()

    def next(self) -> None:
        """次へボタンがクリックされたときの処理
        """
        if self.out_dir.text() == "":
            self.confirm_txt.setText("保存場所を選択してください")
            return
        else:
            self.confirm_txt.setText("")

        self.get_settings_from_ui()
        if not self.skip_region_select.isChecked():
            self.data_store.set("click_points", [])
            self.data_store.set("cap_size", [])

        if not self.settings_manager.validate(self.data_store.get_all()):
            self.confirm_txt.setText("不正な値が入力されています")
            return

        self.save_settings()
        self.next_page()

    def next_page(self) -> None:
        """次の画面に遷移する
        """
        if (
            len(self.data_store.get("click_points")) == 4
            and len(self.data_store.get("cap_size")) == 2
        ):
            self.screen_manager.get_screen("live_exe").trigger("startup")
        else:
            self.screen_manager.get_screen("live_feed").trigger("startup")

    def set_ui_from_settings(self) -> None:
        """設定値をUIに反映する
        """
        self.device_num.setValue(self.data_store.get("device_num"))
        self.num_digits.setValue(self.data_store.get("num_digits"))
        self.sampling_sec.setValue(self.data_store.get("sampling_sec"))
        self.batch_frames.setValue(self.data_store.get("batch_frames"))
        self.total_sampling_min.setValue(
            self.data_store.get("total_sampling_sec") // 60
        )
        self.format.setCurrentText(self.data_store.get("format"))
        self.save_frame.setChecked(self.data_store.get("save_frame"))
        self.out_dir.setText(self.data_store.get("out_dir"))

    def get_settings_from_ui(self):
        """UIから設定値を取得する
        """
        self.data_store.set("device_num", self.device_num.value())
        self.data_store.set("num_digits", self.num_digits.value())
        self.data_store.set("sampling_sec", self.sampling_sec.value())
        self.data_store.set("batch_frames", self.batch_frames.value())
        self.data_store.set("total_sampling_sec", self.total_sampling_min.value() * 60)
        self.data_store.set("format", self.format.currentText())
        self.data_store.set("save_frame", self.save_frame.isChecked())
        self.data_store.set("out_dir", str(Path(self.out_dir.text()) / get_now_str()))
