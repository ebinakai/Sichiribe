import os
import shutil
import logging
import datetime
from typing import Dict, Any, Callable, Union
from pathlib import Path

logger = logging.getLogger("__main__").getChild(__name__)


def clear_directory(directory: Union[str, Path]) -> None:
    """指定されたディレクトリ内の全ファイルとサブディレクトリを削除する

    Args:
        directory (Union[str, Path]): 削除対象のディレクトリのパス
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        logging.debug(f"The specified directory does not exist: {dir_path}")
        return

    # ディレクトリ自体は削除せず、全ファイルとサブディレクトリを削除
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
    """現在時刻を表す文字列を取得する"""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def filter_dict(
    data: Dict[str, Any], predicate: Callable[[str, Any], bool]
) -> Dict[str, Any]:
    """辞書の要素をフィルタリングする

    Args:
        data (Dict[str, Any]): フィルタリング対象の辞書
        predicate (Callable[[str, Any], bool]): フィルタリング条件を表す関数
    """
    return {k: v for k, v in data.items() if predicate(k, v)}


def is_directory_writable(directory_path: Path) -> bool:
    """指定されたディレクトリが存在し、書き込み可能かどうかを判定する

    Args:
        directory_path (Path): チェック対象のディレクトリのパス

    Returns:
        bool: ディレクトリが存在し、書き込み可能な場合はTrue、それ以外はFalse
    """
    if not directory_path.exists():
        logger.error(f"Directory not found: {directory_path}")
        return False

    if not directory_path.is_dir() or not os.access(directory_path, os.W_OK):
        logger.error(f"Directory '{directory_path}' is not writable.")
        return False

    return True
