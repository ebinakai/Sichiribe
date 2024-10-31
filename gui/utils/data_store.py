from typing import Dict, Any
from threading import Lock


# スレッドセーフ実装
class DataStore:
    _instance = None
    _lock = Lock()

    @staticmethod
    def get_instance() -> "DataStore":
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
        with self._data_lock:
            self.shared_data[key] = value

    def set_all(self, data: Dict) -> None:
        with self._data_lock:
            self.shared_data.update(data)

    def get(self, key: str) -> Any:
        with self._data_lock:
            if key not in self.shared_data.keys():
                raise ValueError(f"{key} is not found.")
            return self.shared_data.get(key)

    def get_all(self) -> Dict:
        with self._data_lock:
            return self.shared_data

    def has(self, key: str) -> bool:
        with self._data_lock:
            return key in self.shared_data.keys()

    def clear(self) -> None:
        with self._data_lock:
            self.shared_data.clear()
