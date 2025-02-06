"""GUIアプリケーション内の各ウィンドウで共有されるデータストア"""

import numpy as np
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Set
from threading import Lock


class DataStore:
    """
    アプリケーション全体で共有されるデータを管理するクラス
    シングルトンパターンで実装されており、スレッドセーフな設計
    """

    _instance = None
    _lock = Lock()

    @staticmethod
    def get_instance() -> "DataStore":
        """インスタンスを取得する

        Returns:
            DataStore: データストアのインスタンス
        """
        with DataStore._lock:
            if DataStore._instance is None:
                DataStore._instance = DataStore()
        return DataStore._instance

    def __init__(self) -> None:
        if DataStore._instance is not None:
            raise Exception("This class is a singleton!")
        self.shared_data: Dict[str, Any] = {}
        self._data_lock = Lock()
        self.temp_files: Set[str] = set()
        self.logger = logging.getLogger("__main__").getChild(__name__)

    def set(self, key: str, value: Any) -> None:
        """指定されたキーに値を設定する

        Args:
            key (str): キー
            value (Any): 値
        """
        if isinstance(value, np.ndarray):
            value = self._set_numpy(value)
        with self._data_lock:
            self.shared_data[key] = value
        self.logger.debug(f"Set {key} to {value}")

    def set_all(self, data: Dict[str, Any]) -> None:
        """複数のキーに値を一括設定する

        Args:
            data (Dict[str, Any]): 設定するデータ
        """
        for key, value in data.items():
            self.set(key, value)

    def get(self, key: str) -> Any:
        """指定されたキーの値を取得する

        Args:
            key (str): キー

        Returns:
            Any: 指定されたキーの値

        Raises:
            ValueError: 指定されたキーが存在しない場合に発生
        """
        with self._data_lock:
            if key not in self.shared_data.keys():
                raise ValueError(f"{key} is not found.")
            value = self.shared_data.get(key)
        if isinstance(value, str) and Path(value).suffix == ".npy":
            return self._get_numpy(value)
        return value

    def get_all(self) -> Dict[str, Any]:
        """すべてのデータを取得する

        Returns:
            Dict[str, Any]: すべてのデータ
        """
        with self._data_lock:
            keys = list(self.shared_data.keys())
        return {key: self.get(key) for key in keys}

    def has(self, key: str) -> bool:
        """指定されたキーが存在するかどうかを判定する

        Args:
            key (str): キー

        Returns:
            bool: キーが存在する場合はTrue、存在しない場合はFalse
        """
        with self._data_lock:
            return key in self.shared_data

    def clear(self) -> None:
        """すべてのキーと値を削除し、一時ファイルもクリーンアップ"""
        with self._data_lock:
            self.shared_data.clear()
            self._cleanup_temp_files()

    def _cleanup_temp_files(self) -> None:
        """保存した一時ファイルを削除"""
        for file_path in self.temp_files:
            path = Path(file_path)
            if path.exists():
                path.unlink()
        self.temp_files.clear()

    def _set_numpy(self, array: np.ndarray) -> str:
        """numpy配列を一時ファイルに保存し、そのパスを返す

        Args:
            array (np.ndarray): numpy配列

        Returns:
            Path: 保存された一時ファイルのパス
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".npy")
        np.save(temp_file.name, array)
        temp_file.close()

        with self._data_lock:
            self.temp_files.add(temp_file.name)

        return temp_file.name

    def _get_numpy(self, file_path: str) -> Optional[np.ndarray]:
        """一時ファイルからnumpy配列を取得する

        Args:
            file_path (Path): 一時ファイルのパス

        Returns:
            Optional[np.ndarray]: numpy配列（存在しない場合はNone）
        """
        if Path(file_path).exists():
            return np.load(file_path, mmap_mode="r")
        return None
