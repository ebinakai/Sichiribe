from typing import Dict, Any
from threading import Lock


class DataStore:
    """
    アプリケーション全体で共有されるデータを管理するクラス
    シングルトロンパターンで実装されている
    また、スレッドセーフな実装となっている
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
        self.shared_data: Dict = {}
        self._data_lock = Lock()

    def set(self, key: str, value: Any) -> None:
        """指定されたキーに値を設定する

        Args:
            key (str): キー
            value (Any): 値
        """
        with self._data_lock:
            self.shared_data[key] = value

    def set_all(self, data: Dict) -> None:
        """複数のキーに値を設定する

        Args:
            data (Dict): データストアに追加するデータ
        """
        with self._data_lock:
            self.shared_data.update(data)

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
            return self.shared_data.get(key)

    def get_all(self) -> Dict:
        """すべてのキーと値を取得する"""
        with self._data_lock:
            return self.shared_data

    def has(self, key: str) -> bool:
        """指定されたキーが存在するかどうかを判定する

        Args:
            key (str): キー

        Returns:
            bool: キーが存在する場合はTrue、存在しない場合はFalse
        """
        with self._data_lock:
            return key in self.shared_data.keys()

    def clear(self) -> None:
        """すべてのキーと値を削除する"""
        with self._data_lock:
            self.shared_data.clear()
