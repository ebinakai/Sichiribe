from pathlib import Path
from cores.export_utils import get_supported_formats
from cores.common import filter_dict, is_directory_writable
from typing import Dict, Any, Callable, Union
from platformdirs import user_data_dir
import json
import logging

logger = logging.getLogger("__main__").getChild(__name__)


class SettingsManager:
    def __init__(self, pattern: str) -> None:
        self.required_keys = self._get_required_keys(pattern)
        self.default_path = self._get_default_setting_path(pattern)

    def _get_required_keys(self, pattern: str) -> Dict[str, Callable[[Any], bool]]:
        if pattern == "live":
            return {
                "device_num": lambda x: isinstance(x, int) and x >= 0,
                "num_digits": lambda x: isinstance(x, int) and x >= 1,
                "sampling_sec": lambda x: isinstance(x, int) and x >= 1,
                "num_frames": lambda x: isinstance(x, int) and x >= 1,
                "total_sampling_sec": lambda x: isinstance(x, int) and x >= 1,
                "format": lambda x: x in get_supported_formats(),
                "save_frame": lambda x: isinstance(x, bool),
                "out_dir": lambda x: is_directory_writable(Path(x).parent),
                "click_points": lambda x: isinstance(x, list),
                "cap_size": lambda x: isinstance(x, list) or isinstance(x, tuple),
            }
        elif pattern == "replay":
            return {
                "video_path": lambda x: isinstance(x, str) and Path(x).exists(),
                "num_digits": lambda x: isinstance(x, int) and x >= 1,
                "sampling_sec": lambda x: isinstance(x, int) and x >= 1,
                "num_frames": lambda x: isinstance(x, int) and x >= 1,
                "video_skip_sec": lambda x: isinstance(x, int) and x >= 0,
                "format": lambda x: x in get_supported_formats(),
                "save_frame": lambda x: isinstance(x, bool),
                "out_dir": lambda x: is_directory_writable(Path(x).parent),
                "click_points": lambda x: isinstance(x, list),
            }
        else:
            raise ValueError(f"Invalid pattern: {pattern}")

    def _get_default_setting_path(self, pattern: str) -> Path:
        appname = "Sichiribe"
        appauthor = "EbinaKai"
        user_dir = user_data_dir(appname, appauthor)

        if pattern == "live":
            return Path(user_dir) / "live_settings.json"
        elif pattern == "replay":
            return Path(user_dir) / "replay_settings.json"
        else:
            raise ValueError(f"Invalid pattern: {pattern}")

    def load_default(self) -> Dict[str, Any]:
        return self.load(self.default_path)

    def load(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, "r") as file:
            settings = json.load(file)
            if not isinstance(settings, dict):
                raise TypeError(f"Data in {filepath} is not a dictionary")

            for key in self.required_keys:
                if key not in settings:
                    raise KeyError(f"Key '{key}' not found in {filepath}")

        return self.remove_non_require_keys(settings)

    def validate(self, settings: Dict[str, Any]) -> bool:
        for key, rules in self.required_keys.items():
            value = settings.get(key)
            if value is None:
                logger.error(f"Missing key: {key}")
                return False
            if not rules(value):
                logger.error(f"Invalid value: {key}={value}")
                return False
        return True

    def remove_non_require_keys(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        return filter_dict(settings, lambda k, _: k in self.required_keys)

    def save(self, settings: Dict[str, Any]) -> None:
        if not self.validate(settings):
            raise ValueError("Invalid settings")
        settings = self.remove_non_require_keys(settings)
        with open(self.default_path, "w") as file:
            json.dump(settings, file, indent=4)
