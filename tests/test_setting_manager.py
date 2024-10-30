from cores.settings_manager import SettingsManager
from pathlib import Path
import json
import os


class TestSettingsManager:
    def setup_class(self):
        self.pattern = "live"
        self.setting_manager = SettingsManager(self.pattern)
        expected_setting = {
            "device_num": 0,
            "num_digits": 4,
            "sampling_sec": 10,
            "num_frames": 10,
            "total_sampling_sec": 1,
            "format": "csv",
            "save_frame": False,
            "out_dir": "tests",  # これは書き込み可能なディレクトリである必要がある
            "click_points": [],
            "cap_size": [0, 0],
            "this_is": "missing",
        }

        setting_path = "tests/setting.json"
        with open(setting_path, "w") as f:
            json.dump(expected_setting, f)

        self.setting_path = setting_path
        self.expected_setting = expected_setting

    def teardown_class(self):
        if Path(self.setting_path).exists():
            os.remove(self.setting_path)

    def test_load_setting(self):
        expected_setting = self.expected_setting.copy()
        expected_setting.pop("this_is")

        output = self.setting_manager.load(self.setting_path)
        assert output == expected_setting

    def test_validate_setting(self):
        assert self.setting_manager.validate(self.expected_setting) is True

    def test_validate_setting_missing_key(self):
        expected_setting = self.expected_setting.copy()
        expected_setting["device_num"] = None
        assert self.setting_manager.validate(expected_setting) is False

    def test_remove_non_require_keys(self):
        output = self.setting_manager.remove_non_require_keys(self.expected_setting)
        expected_setting = self.expected_setting.copy()
        expected_setting.pop("this_is")
        assert output == expected_setting
