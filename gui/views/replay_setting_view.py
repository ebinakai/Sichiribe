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
from cores.common import get_now_str
from cores.settings_manager import SettingsManager
from cores.export_utils import get_supported_formats
import logging
from pathlib import Path


class ReplaySettingWindow(SettingWidget):
    """動画ファイル解析の設定を行うViewクラス

    以下を設定する
    
    - 解析する動画のパス
    - 7セグメント表示器の桁数
    - 動画をサンプリングする頻度
    - 一回のサンプリングで何フレーム取得するか
    - 動画の解析を始めるタイミング
    - 出力形式
    - キャプチャしたフレームを保存するか
    """
    def __init__(self, screen_manager: ScreenManager) -> None:
        self.logger = logging.getLogger("__main__").getChild(__name__)
        self.screen_manager = screen_manager
        self.settings_manager = SettingsManager("replay")

        super().__init__()
        screen_manager.add_screen("replay_setting", self, "動画解析設定")

    def initUI(self):
        """ウィジェットのUIを初期化する
        """
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

        self.batch_frames = QSpinBox()
        self.batch_frames.setValue(30)
        self.batch_frames.setFixedWidth(50)
        self.batch_frames.setMinimum(1)
        form_layout.addRow(
            "一回のサンプリングで何フレーム取得するか：", self.batch_frames
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
        form_layout.addRow("キャプチャしたフレームを保存：", self.save_frame)

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
        self.next_button.setDefault(True)  # 強調表示されるデフォルトボタンに設定
        self.next_button.setAutoDefault(True)
        self.next_button.clicked.connect(self.next)
        footer_layout.addWidget(self.next_button)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(footer_layout)

    def display(self) -> None:
        """ウィジェットを表示時の処理
        
        画面表示時に設定ファイルからパラメータを読み込んでUIに反映する
        """
        super().display()
        has_click_points = (
            self.data_store.has("click_points")
            and len(self.data_store.get("click_points")) == 4
        )
        self.skip_region_select.setEnabled(has_click_points)
        self.skip_region_select.setChecked(has_click_points)

    def select_file(self) -> None:
        """ファイル選択ダイアログを表示して動画ファイルを選択する
        """
        video_path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを選択", "", "動画ファイル (*.mp4)"
        )
        if video_path:
            self.video_path.setText(video_path)

    def back(self) -> None:
        """戻るボタンがクリックされたときの処理
        
        メニュー画面に戻る
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
            self.logger.info(f"Failed to load settings file")
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
        self.screen_manager.get_screen("replay_exe").trigger("startup")

    def next(self) -> None:
        """次へボタンがクリックされたときの処理
        """
        if self.video_path.text() == "":
            self.confirm_txt.setText("動画ファイルを選択してください")
            return
        else:
            self.confirm_txt.setText("")

        self.get_settings_from_ui()
        if not self.skip_region_select.isChecked():
            self.data_store.set("click_points", [])
        self.data_store.set(
            "out_dir",
            str(Path(self.data_store.get("video_path")).parent / get_now_str()),
        )

        if not self.settings_manager.validate(self.data_store.get_all()):
            self.confirm_txt.setText("不正な値が入力されています")
            return

        self.save_settings()
        self.screen_manager.get_screen("replay_exe").trigger("startup")

    def set_ui_from_settings(self) -> None:
        """設定ファイルからパラメータを読み込んでUIに反映する
        """
        self.video_path.setText(self.data_store.get("video_path"))
        self.num_digits.setValue(self.data_store.get("num_digits"))
        self.sampling_sec.setValue(self.data_store.get("sampling_sec"))
        self.batch_frames.setValue(self.data_store.get("batch_frames"))
        self.video_skip_sec.setValue(self.data_store.get("video_skip_sec"))
        self.format.setCurrentText(self.data_store.get("format"))
        self.save_frame.setChecked(self.data_store.get("save_frame"))

    def get_settings_from_ui(self) -> None:
        """UIから設定値を取得してデータストアに保存する
        """
        self.data_store.set("video_path", self.video_path.text())
        self.data_store.set("num_digits", self.num_digits.value())
        self.data_store.set("sampling_sec", self.sampling_sec.value())
        self.data_store.set("batch_frames", self.batch_frames.value())
        self.data_store.set("video_skip_sec", self.video_skip_sec.value())
        self.data_store.set("format", self.format.currentText())
        self.data_store.set("save_frame", self.save_frame.isChecked())
        self.data_store.set("out_dir", self.video_path.text())
