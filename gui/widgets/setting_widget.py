from gui.widgets.custom_qwidget import CustomQWidget
from cores.settings_manager import SettingsManager
from logging import Logger
from pathlib import Path

class SettingWidget(CustomQWidget):
    def __init__(self) -> None:
        super().__init__()
        self.settings_manager: SettingsManager
        self.logger: Logger

    def display(self):
        try:
            settings = self.settings_manager.load_default()
            if self.settings_manager.validate(settings):
                self.data_store.set_all(settings)
                out_dir = self.data_store.get("out_dir")
                out_dir_parent = Path(out_dir).resolve().parent
                self.data_store.set("out_dir", str(out_dir_parent))
                self.set_ui_from_settings()
        except Exception:
            self.logger.info(f"Failed to load default setting file")

    def save_settings(self) -> None:
        try:
            self.settings_manager.save(self.data_store.get_all())
        except Exception:
            self.logger.info(f"Failed to save settings file")

    def get_settings_from_ui(self) -> None:
        raise NotImplementedError("get_settings_from_ui() is not implemented")

    def set_ui_from_settings(self) -> None:
        raise NotImplementedError("set_ui_from_settings() is not implemented")
