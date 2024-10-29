import os
import shutil
import logging
import datetime
from typing import Dict, Set, Any, Callable
import json
from pathlib import Path

logger = logging.getLogger("__main__").getChild(__name__)


def validate_output_directory(directory_path: Path) -> bool:
    if not directory_path.exists():
        logger.error(f"Directory not found: {directory_path}")
        return False

    if not directory_path.is_dir() or not os.access(directory_path, os.W_OK):
        logger.error(f"Directory '{directory_path}' is not writable.")
        return False

    return True


def validate_params(
    params: Dict[str, Any], required_keys: Dict[str, Callable[[Any], bool]]
) -> bool:
    for key, value in required_keys.items():
        param_value = params.get(key)
        if param_value is None:
            logger.error(f"Missing key: {key}")
            return False
        if not value(param_value):
            logger.error(f"Invalid value: {key}={param_value}")
            return False
    return True


def clear_directory(directory: str | Path) -> None:
    dir_path = Path(directory)
    if not dir_path.exists():
        logging.debug(f"The specified directory does not exist: {dir_path}")
        return

    # ディレクトリ内の全ファイルとサブディレクトリを削除
    for path in dir_path.iterdir():
        try:
            if path.is_file() or path.is_symlink():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except Exception as e:
            logging.error(f"Failed to delete {path}. Reason: {e}")

    logging.debug(f"All contents in the directory '{dir_path}' have been deleted.")


def get_now_str() -> str:
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def filter_dict(
    data: Dict[str, Any], predicate: Callable[[str, Any], bool]
) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if predicate(k, v)}


def load_setting(filepath: str | Path, required_keys: Set[str]) -> Dict[str, Any]:

    if not Path(filepath).exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r") as file:
        data = json.load(file)
        if not isinstance(data, dict):
            raise TypeError(f"Data in {filepath} is not a dictionary")

        for key in required_keys:
            if key not in data:
                raise KeyError(f"Key '{key}' not found in {filepath}")

    return filter_dict(data, lambda k, _: k in required_keys)
