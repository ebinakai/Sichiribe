from typing import Dict, Any
from threading import Lock
import logging


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
        self.logger = logging.getLogger("__main__").getChild(__name__)

    def set(self, key: str, value: Any) -> None:
        with self._data_lock:
            self.shared_data[key] = value
            self.logger.debug(f"{key} is set to {value}")

    def set_all(self, data: Dict) -> None:
        with self._data_lock:
            self.shared_data.update(data)
            self.logger.debug(f"{data} is set.")

    def get(self, key: str) -> Any:
        with self._data_lock:
            value = self.shared_data.get(key)
            if value is None:
                raise ValueError(f"{key} is not found.")
            self.logger.debug(f"{key} is {value}.")
            return value

    def get_all(self) -> Dict:
        with self._data_lock:
            self.logger.debug(f"{self.shared_data} is returned.")
            return self.shared_data

    def has(self, key: str) -> bool:
        with self._data_lock:
            self.logger.debug(f"{key} is checked.")
            return key in self.shared_data

    def clear(self) -> None:
        with self._data_lock:
            self.logger.debug("All data is cleared")
            self.shared_data.clear()
