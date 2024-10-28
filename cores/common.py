import os
import shutil
import logging
import datetime
from typing import Dict, Set, Any, Callable
import json

logger = logging.getLogger("__main__").getChild(__name__)


def validate_output_directory(directory_path: str) -> bool:
    if not os.path.exists(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return False

    if not os.access(directory_path, os.W_OK):
        logger.error(f"Directory '{directory_path}' is not writable.")
        return False
    return True


def clear_directory(directory: str) -> None:
    if not os.path.exists(directory):
        logger.debug(f"The specified directory does not exist: {directory}")
        return

    # ディレクトリ内の全ファイルとサブディレクトリを削除
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f"Failed to delete {file_path}. Reason: {e}")

    logger.debug(f"All contents in the directory '{directory}' have been deleted.")


def get_now_str() -> str:
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def filter_dict(
    data: Dict[str, Any], predicate: Callable[[str, Any], bool]
) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if predicate(k, v)}


def load_config(filepath: str, required_keys: Set[str]) -> Dict[str, Any]:

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r") as file:
        data = json.load(file)
        if not isinstance(data, dict):
            raise TypeError(f"Data in {filepath} is not a dictionary")

        for key in required_keys:
            if key not in data:
                raise KeyError(f"Key '{key}' not found in {filepath}")

    return filter_dict(data, lambda k, _: k in required_keys)
